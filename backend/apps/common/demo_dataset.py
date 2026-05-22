from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from apps.journal.models import AttendanceStatus, GradeWorkType
from apps.users.models import UserRole


@dataclass(frozen=True)
class DemoUser:
    username: str
    password: str
    role: str
    first_name: str
    last_name: str
    email: str
    phone: str
    is_staff: bool = False
    is_superuser: bool = False


@dataclass(frozen=True)
class DemoGroup:
    name: str
    enrollment_year_offset: int


@dataclass(frozen=True)
class DemoSubject:
    code: str
    name: str
    description: str


@dataclass(frozen=True)
class DemoPeriod:
    name: str
    starts_offset: int
    ends_offset: int
    is_active: bool


@dataclass(frozen=True)
class DemoWorkTemplate:
    title: str
    work_type: str
    date_offset: int
    max_score: Decimal
    weight: Decimal


BASE_USERS = [
    DemoUser(
        username="admin",
        password="admin123",
        role=UserRole.ADMIN,
        first_name="Админ",
        last_name="Системы",
        email="admin@example.local",
        phone="+7 900-000-00-01",
        is_staff=True,
        is_superuser=True,
    ),
    DemoUser(
        username="teacher",
        password="teacher123",
        role=UserRole.TEACHER,
        first_name="Ирина",
        last_name="Петрова",
        email="teacher@example.local",
        phone="+7 900-000-00-02",
    ),
    DemoUser(
        username="student",
        password="student123",
        role=UserRole.STUDENT,
        first_name="Алексей",
        last_name="Иванов",
        email="student@example.local",
        phone="+7 900-000-00-03",
    ),
]

EXTRA_TEACHERS = [
    ("demo_teacher_01", "Марина", "Соколова", "Старший преподаватель"),
    ("demo_teacher_02", "Олег", "Морозов", "Доцент"),
    ("demo_teacher_03", "Наталья", "Федорова", "Преподаватель"),
    ("demo_teacher_04", "Сергей", "Волков", "Преподаватель"),
    ("demo_teacher_05", "Анна", "Кузнецова", "Методист-преподаватель"),
]

GROUPS = [
    DemoGroup("743-2", -1),
    DemoGroup("741-1", -2),
    DemoGroup("742-1", -2),
    DemoGroup("744-1", 0),
    DemoGroup("745-2", 0),
    DemoGroup("746-1", -1),
]

SUBJECTS = [
    DemoSubject("IB-101", "Информационная безопасность", "Защита информации, угрозы, политики безопасности."),
    DemoSubject("DB-201", "Базы данных", "Проектирование схем, SQL, транзакции и индексы."),
    DemoSubject("PY-102", "Программирование на Python", "Основы языка, функции, классы и работа с файлами."),
    DemoSubject("WEB-210", "Web-разработка", "Frontend, backend, HTTP API и клиент-серверные приложения."),
    DemoSubject("NET-120", "Компьютерные сети", "Модели сетей, адресация, маршрутизация и диагностика."),
    DemoSubject("OS-130", "Операционные системы", "Процессы, память, файловые системы и администрирование."),
    DemoSubject("ALG-110", "Алгоритмы и структуры данных", "Сложность алгоритмов, списки, деревья, графы."),
    DemoSubject("TEST-220", "Тестирование ПО", "Тест-дизайн, автоматизация, дефекты и качество."),
    DemoSubject("PM-230", "Управление проектами", "Планирование, риски, задачи и приемка результата."),
    DemoSubject("UI-240", "Проектирование интерфейсов", "UX-паттерны, прототипирование и доступность."),
]

PERIODS = [
    DemoPeriod("Демо период", -30, 3, True),
    DemoPeriod("Прошлый семестр", -150, -40, False),
    DemoPeriod("Летняя практика", 10, 45, True),
]

WORK_TEMPLATES = [
    DemoWorkTemplate("Практическая работа 1", GradeWorkType.CLASSWORK, -24, Decimal("5.00"), Decimal("1.00")),
    DemoWorkTemplate("Домашняя работа 1", GradeWorkType.HOMEWORK, -20, Decimal("5.00"), Decimal("0.80")),
    DemoWorkTemplate("Практическая работа 2", GradeWorkType.CLASSWORK, -16, Decimal("5.00"), Decimal("1.00")),
    DemoWorkTemplate("Тестирование модуля", GradeWorkType.TEST, -12, Decimal("10.00"), Decimal("1.50")),
    DemoWorkTemplate("Индивидуальное задание", GradeWorkType.OTHER, -8, Decimal("10.00"), Decimal("1.20")),
    DemoWorkTemplate("Контрольная работа", GradeWorkType.TEST, -4, Decimal("10.00"), Decimal("2.00")),
]

SESSION_TOPICS = [
    "Вводное занятие и требования курса",
    "Разбор ключевых понятий",
    "Практика по теме модуля",
    "Работа с типовыми ошибками",
    "Групповое практическое задание",
    "Контрольные вопросы",
    "Разбор самостоятельной работы",
    "Итоговое занятие по разделу",
]

STUDENT_FIRST_NAMES = [
    "Алексей",
    "Екатерина",
    "Дмитрий",
    "Полина",
    "Иван",
    "Мария",
    "Никита",
    "Дарья",
    "Артем",
    "Виктория",
    "Кирилл",
    "Алина",
]

STUDENT_LAST_NAMES = [
    "Иванов",
    "Смирнова",
    "Кузнецов",
    "Попова",
    "Соколов",
    "Лебедева",
    "Новиков",
    "Морозова",
    "Волков",
    "Федорова",
    "Павлов",
    "Семенова",
]


def build_extra_teacher_users() -> list[DemoUser]:
    return [
        DemoUser(
            username=username,
            password="teacher123",
            role=UserRole.TEACHER,
            first_name=first_name,
            last_name=last_name,
            email=f"{username}@example.local",
            phone=format_phone(10 + index),
        )
        for index, (username, first_name, last_name, _position) in enumerate(EXTRA_TEACHERS, start=1)
    ]


def build_student_users(groups_count: int, students_per_group: int) -> list[DemoUser]:
    students = [BASE_USERS[2]]
    needed = groups_count * students_per_group
    for index in range(1, needed):
        first_name = STUDENT_FIRST_NAMES[index % len(STUDENT_FIRST_NAMES)]
        last_name = STUDENT_LAST_NAMES[index % len(STUDENT_LAST_NAMES)]
        username = f"demo_student_{index:03d}"
        students.append(
            DemoUser(
                username=username,
                password="student123",
                role=UserRole.STUDENT,
                first_name=first_name,
                last_name=last_name,
                email=f"{username}@example.local",
                phone=format_phone(100 + index),
            )
        )
    return students


def format_phone(number: int) -> str:
    return f"+7 900-{number // 100:03d}-{(number // 10) % 10:02d}-{number % 100:02d}"


def period_dates(period: DemoPeriod, today: date) -> dict:
    return {
        "starts_at": today + timedelta(days=period.starts_offset),
        "ends_at": today + timedelta(days=period.ends_offset),
        "is_active": period.is_active,
    }
