from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.common.demo_dataset import (
    BASE_USERS,
    EXTRA_TEACHERS,
    GROUPS,
    PERIODS,
    SESSION_TOPICS,
    SUBJECTS,
    WORK_TEMPLATES,
    build_extra_teacher_users,
    build_student_users,
    period_dates,
)
from apps.education.models import (
    AcademicGroup,
    AcademicPeriod,
    StudentProfile,
    Subject,
    TeacherProfile,
    TeachingAssignment,
)
from apps.journal.models import AttendanceRecord, AttendanceStatus, ClassSession, Grade, GradeWork
from apps.notifications.models import Notification
from apps.notifications.tasks import send_session_closing_reminders
from apps.reports.models import ReportRequest
from apps.users.models import User, UserRole


class Command(BaseCommand):
    help = "Create reproducible demo data. Default mode is a small acceptance dataset."

    def add_arguments(self, parser):
        parser.add_argument("--small", action="store_true", help="Create a minimal acceptance dataset. This is the default mode.")
        parser.add_argument("--full", action="store_true", help="Create a rich demonstration dataset.")
        parser.add_argument("--reset", action="store_true", help="Delete only generated demo data before creating it again.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["small"] and options["full"]:
            raise CommandError("Use either --small or --full, not both.")

        mode = "full" if options["full"] else "small"
        today = timezone.localdate()

        if options["reset"]:
            self._reset_demo_data(mode)

        if mode == "full":
            stats = self._create_full_dataset(today)
        else:
            stats = self._create_small_dataset(today)

        created_reminders = send_session_closing_reminders()

        self.stdout.write(self.style.SUCCESS(f"Demo data is ready in {mode} mode."))
        self.stdout.write("Credentials:")
        self.stdout.write("  admin / admin123")
        self.stdout.write("  teacher / teacher123")
        self.stdout.write("  student / student123")
        if mode == "full":
            self.stdout.write("  demo_teacher_01..demo_teacher_05 / teacher123")
            self.stdout.write("  demo_student_001..demo_student_059 / student123")
        self.stdout.write(f"Created reminders: {created_reminders}")
        self.stdout.write(
            "Dataset: "
            f"{stats['users']} users, "
            f"{stats['groups']} groups, "
            f"{stats['subjects']} subjects, "
            f"{stats['periods']} periods, "
            f"{stats['assignments']} assignments, "
            f"{stats['works']} grade works, "
            f"{stats['grades']} grades, "
            f"{stats['sessions']} sessions, "
            f"{stats['attendance']} attendance records."
        )

    def _create_small_dataset(self, today):
        admin = self._upsert_user(BASE_USERS[0])
        teacher = self._upsert_user(BASE_USERS[1])
        student = self._upsert_user(BASE_USERS[2])

        group = self._upsert_group(GROUPS[0], today)
        subject = self._upsert_subject(SUBJECTS[0])
        period = self._upsert_period(PERIODS[0], today)
        teacher_profile = self._upsert_teacher_profile(teacher, "DEMO-T-001", "Преподаватель")
        student_profile = self._upsert_student_profile(student, 100001, group, today)
        assignment = self._upsert_assignment(teacher_profile, subject, group, period)

        work_template = WORK_TEMPLATES[0]
        grade_work = self._upsert_grade_work(assignment, work_template, today, teacher)
        self._upsert_grade(grade_work, student_profile, Decimal("5.00"), teacher)

        session = self._upsert_class_session(assignment, today, SESSION_TOPICS[0], teacher)
        self._upsert_attendance(session, student_profile, AttendanceStatus.PRESENT, teacher)

        return {
            "users": 3,
            "groups": 1,
            "subjects": 1,
            "periods": 1,
            "assignments": 1,
            "works": 1,
            "grades": 1,
            "sessions": 1,
            "attendance": 1,
        }

    def _create_full_dataset(self, today):
        users = {demo_user.username: self._upsert_user(demo_user) for demo_user in BASE_USERS + build_extra_teacher_users()}
        groups = [self._upsert_group(group, today) for group in GROUPS]
        subjects = [self._upsert_subject(subject) for subject in SUBJECTS]
        periods = [self._upsert_period(period, today) for period in PERIODS]

        teacher_profiles = [
            self._upsert_teacher_profile(users["teacher"], "DEMO-T-001", "Преподаватель"),
        ]
        for index, (username, _first_name, _last_name, position) in enumerate(EXTRA_TEACHERS, start=2):
            teacher_profiles.append(self._upsert_teacher_profile(users[username], f"DEMO-T-{index:03d}", position))

        students_per_group = 10
        student_users = build_student_users(groups_count=len(groups), students_per_group=students_per_group)
        student_profiles_by_group = {group.id: [] for group in groups}
        for index, demo_user in enumerate(student_users):
            user = users.get(demo_user.username) or self._upsert_user(demo_user)
            group = groups[index // students_per_group]
            student_id = 100001 + index
            profile = self._upsert_student_profile(user, student_id, group, today)
            student_profiles_by_group[group.id].append(profile)
            users[demo_user.username] = user

        assignments = []
        current_period = periods[0]
        past_period = periods[1]
        for group_index, group in enumerate(groups):
            for offset in range(5):
                subject = subjects[(group_index + offset) % len(subjects)]
                teacher_profile = teacher_profiles[(group_index + offset) % len(teacher_profiles)]
                assignments.append(self._upsert_assignment(teacher_profile, subject, group, current_period))
            for offset in range(2):
                subject = subjects[(group_index + offset + 5) % len(subjects)]
                teacher_profile = teacher_profiles[(group_index + offset + 1) % len(teacher_profiles)]
                assignments.append(self._upsert_assignment(teacher_profile, subject, group, past_period))

        works_count = grades_count = sessions_count = attendance_count = 0
        for assignment_index, assignment in enumerate(assignments):
            students = student_profiles_by_group[assignment.group_id]
            teacher_user = assignment.teacher.user

            for work_index, template in enumerate(WORK_TEMPLATES):
                grade_work = self._upsert_grade_work(assignment, template, today, teacher_user)
                works_count += 1
                for student_index, student in enumerate(students):
                    value = self._grade_value(assignment_index, work_index, student_index, template.max_score)
                    self._upsert_grade(grade_work, student, value, teacher_user)
                    grades_count += 1

            for topic_index, topic in enumerate(SESSION_TOPICS):
                session_date = today.replace() + timezone.timedelta(days=-28 + topic_index * 4)
                session = self._upsert_class_session(assignment, session_date, topic, teacher_user)
                sessions_count += 1
                for student_index, student in enumerate(students):
                    status = self._attendance_status(assignment_index, topic_index, student_index)
                    self._upsert_attendance(session, student, status, teacher_user)
                    attendance_count += 1

        return {
            "users": len(users),
            "groups": len(groups),
            "subjects": len(subjects),
            "periods": len(periods),
            "assignments": len(assignments),
            "works": works_count,
            "grades": grades_count,
            "sessions": sessions_count,
            "attendance": attendance_count,
        }

    def _reset_demo_data(self, mode: str) -> None:
        demo_usernames = self._demo_usernames(mode)
        demo_group_names = self._demo_group_names(mode)
        demo_subject_codes = self._demo_subject_codes(mode)
        demo_period_names = self._demo_period_names(mode)
        demo_student_ids = self._demo_student_ids(mode)

        assignment_filter = (
            Q(teacher__user__username__in=demo_usernames)
            | Q(subject__code__in=demo_subject_codes)
            | Q(group__name__in=demo_group_names)
            | Q(period__name__in=demo_period_names)
        )
        demo_assignments = TeachingAssignment.objects.filter(assignment_filter)
        demo_student_profiles = StudentProfile.objects.filter(Q(user__username__in=demo_usernames) | Q(student_id__in=demo_student_ids))
        demo_sessions = ClassSession.objects.filter(assignment__in=demo_assignments)
        demo_works = GradeWork.objects.filter(assignment__in=demo_assignments)

        AttendanceRecord.objects.filter(Q(session__in=demo_sessions) | Q(student__in=demo_student_profiles)).delete()
        Grade.objects.filter(Q(work__in=demo_works) | Q(student__in=demo_student_profiles)).delete()
        demo_sessions.delete()
        demo_works.delete()
        Notification.objects.filter(Q(recipient__username__in=demo_usernames) | Q(period__name__in=demo_period_names)).delete()
        self._delete_demo_reports(demo_usernames)
        AuditLog.objects.filter(actor__username__in=demo_usernames).delete()
        demo_assignments.delete()
        demo_student_profiles.delete()
        TeacherProfile.objects.filter(user__username__in=demo_usernames).delete()
        self._safe_delete(Subject.objects.filter(code__in=demo_subject_codes), "subjects")
        self._safe_delete(AcademicPeriod.objects.filter(name__in=demo_period_names), "periods")
        self._safe_delete(AcademicGroup.objects.filter(name__in=demo_group_names), "groups")
        User.objects.filter(username__in=demo_usernames).delete()

    def _delete_demo_reports(self, demo_usernames: set[str]) -> None:
        for report in ReportRequest.objects.filter(requested_by__username__in=demo_usernames):
            if report.file:
                report.file.delete(save=False)
            report.delete()

    def _safe_delete(self, queryset, label: str) -> None:
        try:
            queryset.delete()
        except ProtectedError:
            self.stdout.write(self.style.WARNING(f"Skipped deleting some demo {label}: they are referenced by non-demo data."))

    def _demo_usernames(self, mode: str) -> set[str]:
        usernames = {user.username for user in BASE_USERS}
        if mode == "full":
            usernames.update(username for username, *_rest in EXTRA_TEACHERS)
            usernames.update(user.username for user in build_student_users(len(GROUPS), 10))
        return usernames

    def _demo_group_names(self, mode: str) -> set[str]:
        groups = GROUPS if mode == "full" else GROUPS[:1]
        return {group.name for group in groups}

    def _demo_subject_codes(self, mode: str) -> set[str]:
        subjects = SUBJECTS if mode == "full" else SUBJECTS[:1]
        return {subject.code for subject in subjects}

    def _demo_period_names(self, mode: str) -> set[str]:
        periods = PERIODS if mode == "full" else PERIODS[:1]
        return {period.name for period in periods}

    def _demo_student_ids(self, mode: str) -> set[int]:
        count = len(GROUPS) * 10 if mode == "full" else 1
        return {100001 + index for index in range(count)}

    def _upsert_user(self, demo_user) -> User:
        user, _ = User.objects.update_or_create(
            username=demo_user.username,
            defaults={
                "role": demo_user.role,
                "first_name": demo_user.first_name,
                "last_name": demo_user.last_name,
                "email": demo_user.email,
                "phone": demo_user.phone,
                "is_active": True,
                "is_staff": demo_user.is_staff,
                "is_superuser": demo_user.is_superuser,
                "access_expires_at": None,
                "failed_login_attempts": 0,
                "locked_until": None,
            },
        )
        user.set_password(demo_user.password)
        user.save(update_fields=["password"])
        return user

    def _upsert_group(self, demo_group, today):
        return AcademicGroup.objects.update_or_create(
            name=demo_group.name,
            defaults={"enrollment_year": today.year + demo_group.enrollment_year_offset, "is_active": True},
        )[0]

    def _upsert_subject(self, demo_subject):
        return Subject.objects.update_or_create(
            code=demo_subject.code,
            defaults={"name": demo_subject.name, "description": demo_subject.description, "is_active": True},
        )[0]

    def _upsert_period(self, demo_period, today):
        return AcademicPeriod.objects.update_or_create(
            name=demo_period.name,
            defaults=period_dates(demo_period, today),
        )[0]

    def _upsert_teacher_profile(self, user: User, personnel_number: str, position: str):
        return TeacherProfile.objects.update_or_create(
            user=user,
            defaults={"personnel_number": personnel_number, "position": position},
        )[0]

    def _upsert_student_profile(self, user: User, student_id: int, group: AcademicGroup, today):
        return StudentProfile.objects.update_or_create(
            user=user,
            defaults={"student_id": student_id, "group": group, "enrollment_date": today - timezone.timedelta(days=365)},
        )[0]

    def _upsert_assignment(self, teacher, subject, group, period):
        return TeachingAssignment.objects.get_or_create(
            teacher=teacher,
            subject=subject,
            group=group,
            period=period,
        )[0]

    def _upsert_grade_work(self, assignment, template, today, teacher: User):
        return GradeWork.objects.update_or_create(
            assignment=assignment,
            title=template.title,
            work_date=today + timezone.timedelta(days=template.date_offset),
            defaults={
                "work_type": template.work_type,
                "max_score": template.max_score,
                "weight": template.weight,
                "created_by": teacher,
            },
        )[0]

    def _upsert_grade(self, grade_work, student, value: Decimal, teacher: User) -> None:
        Grade.objects.update_or_create(
            work=grade_work,
            student=student,
            defaults={
                "value": value,
                "comment": "Демонстрационная оценка.",
                "created_by": teacher,
                "updated_by": teacher,
            },
        )

    def _upsert_class_session(self, assignment, session_date, topic: str, teacher: User):
        return ClassSession.objects.update_or_create(
            assignment=assignment,
            session_date=session_date,
            topic=topic,
            defaults={"created_by": teacher},
        )[0]

    def _upsert_attendance(self, session, student, status: str, teacher: User) -> None:
        AttendanceRecord.objects.update_or_create(
            session=session,
            student=student,
            defaults={
                "status": status,
                "comment": self._attendance_comment(status),
                "created_by": teacher,
                "updated_by": teacher,
            },
        )

    def _grade_value(self, assignment_index: int, work_index: int, student_index: int, max_score: Decimal) -> Decimal:
        raw = int(max_score) - ((assignment_index + work_index + student_index) % 4)
        if student_index % 11 == 0:
            raw = max(2, raw - 1)
        return Decimal(max(1, raw)).quantize(Decimal("0.01"))

    def _attendance_status(self, assignment_index: int, topic_index: int, student_index: int) -> str:
        marker = (assignment_index + topic_index + student_index) % 12
        if marker == 0:
            return AttendanceStatus.ABSENT
        if marker == 1:
            return AttendanceStatus.LATE
        if marker == 2:
            return AttendanceStatus.EXCUSED
        return AttendanceStatus.PRESENT

    def _attendance_comment(self, status: str) -> str:
        comments = {
            AttendanceStatus.PRESENT: "Присутствовал.",
            AttendanceStatus.ABSENT: "Отсутствовал.",
            AttendanceStatus.EXCUSED: "Уважительная причина.",
            AttendanceStatus.LATE: "Опоздал к началу занятия.",
        }
        return comments[status]
