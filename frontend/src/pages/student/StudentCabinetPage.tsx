import { useMemo, useState } from "react";
import { CalendarDays, GraduationCap, Mail, Search, UserRound } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { fetchStudentAttendance, fetchStudentDashboard, fetchStudentGrades } from "../../api/student";
import type { AttendanceStatus, StudentAttendance, StudentGrade } from "../../api/student";
import { StatusBadge } from "../../components/StatusBadge";
import { DataTable, ErrorState, LoadingState, PageHeader, SectionToolbar, SelectField, TextField } from "../../components/ui";
import type { DataTableColumn } from "../../components/ui";

const attendanceLabels: Record<AttendanceStatus, string> = {
  present: "Присутствовал",
  absent: "Отсутствовал",
  excused: "Уважительная причина",
  late: "Опоздал",
};

const attendanceTone: Record<AttendanceStatus, "success" | "warning" | "neutral"> = {
  present: "success",
  absent: "warning",
  excused: "neutral",
  late: "warning",
};

const gradeColumns: Array<DataTableColumn<StudentGrade>> = [
  {
    key: "work_date",
    header: "Дата",
    render: (row) => formatDate(row.work_date),
    width: "130px",
  },
  {
    key: "subject",
    header: "Дисциплина",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.subject_name}</strong>
        <span>{row.work_title}</span>
      </div>
    ),
  },
  {
    key: "teacher",
    header: "Преподаватель",
    render: (row) => row.teacher_name || "-",
  },
  {
    key: "period",
    header: "Период",
    render: (row) => row.period_name,
  },
  {
    key: "value",
    header: "Оценка",
    align: "right",
    render: (row) => (
      <span className="score-chip">
        {formatDecimal(row.value)} / {formatDecimal(row.max_score)}
      </span>
    ),
    width: "140px",
  },
];

const attendanceColumns: Array<DataTableColumn<StudentAttendance>> = [
  {
    key: "session_date",
    header: "Дата",
    render: (row) => formatDate(row.session_date),
    width: "130px",
  },
  {
    key: "subject",
    header: "Занятие",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.subject_name}</strong>
        <span>{row.session_topic}</span>
      </div>
    ),
  },
  {
    key: "teacher",
    header: "Преподаватель",
    render: (row) => row.teacher_name || "-",
  },
  {
    key: "period",
    header: "Период",
    render: (row) => row.period_name,
  },
  {
    key: "status",
    header: "Статус",
    render: (row) => <StatusBadge tone={attendanceTone[row.status]}>{attendanceLabels[row.status]}</StatusBadge>,
    width: "190px",
  },
];

export function StudentCabinetPage() {
  const [gradeSearch, setGradeSearch] = useState("");
  const [gradePeriod, setGradePeriod] = useState("");
  const [attendanceSearch, setAttendanceSearch] = useState("");
  const [attendanceStatus, setAttendanceStatus] = useState("");

  const dashboardQuery = useQuery({
    queryKey: ["student", "dashboard"],
    queryFn: fetchStudentDashboard,
  });
  const gradesQuery = useQuery({
    queryKey: ["student", "grades"],
    queryFn: fetchStudentGrades,
  });
  const attendanceQuery = useQuery({
    queryKey: ["student", "attendance"],
    queryFn: fetchStudentAttendance,
  });

  const gradePeriods = useMemo(() => uniqueOptions(gradesQuery.data?.map((grade) => grade.period_name) ?? []), [gradesQuery.data]);
  const filteredGrades = useMemo(() => {
    return (gradesQuery.data ?? []).filter((grade) => {
      const searchTarget = `${grade.subject_name} ${grade.work_title} ${grade.teacher_name}`.toLowerCase();
      const matchesSearch = searchTarget.includes(gradeSearch.trim().toLowerCase());
      const matchesPeriod = !gradePeriod || grade.period_name === gradePeriod;
      return matchesSearch && matchesPeriod;
    });
  }, [gradePeriod, gradeSearch, gradesQuery.data]);

  const filteredAttendance = useMemo(() => {
    return (attendanceQuery.data ?? []).filter((record) => {
      const searchTarget = `${record.subject_name} ${record.session_topic} ${record.teacher_name}`.toLowerCase();
      const matchesSearch = searchTarget.includes(attendanceSearch.trim().toLowerCase());
      const matchesStatus = !attendanceStatus || record.status === attendanceStatus;
      return matchesSearch && matchesStatus;
    });
  }, [attendanceQuery.data, attendanceSearch, attendanceStatus]);

  if (dashboardQuery.isLoading) {
    return <LoadingState text="Загружаем кабинет студента" />;
  }

  if (dashboardQuery.isError || !dashboardQuery.data) {
    return <ErrorState text="Проверьте, что у пользователя создан профиль студента и есть доступ к кабинету." />;
  }

  const { profile, grades, attendance } = dashboardQuery.data;

  return (
    <section className="content-stack">
      <PageHeader
        badge={<StatusBadge tone="success">Кабинет студента</StatusBadge>}
        description="Личная сводка по успеваемости и посещаемости."
        icon={<GraduationCap aria-hidden="true" size={34} />}
        title={profile.full_name || profile.username}
      />

      <div className="student-profile-grid">
        <article className="profile-panel">
          <div className="profile-panel__icon">
            <UserRound aria-hidden="true" size={24} />
          </div>
          <div>
            <h2>Профиль</h2>
            <dl className="details-list">
              <div>
                <dt>Группа</dt>
                <dd>{profile.group_name}</dd>
              </div>
              <div>
                <dt>ID студента</dt>
                <dd>{profile.student_id}</dd>
              </div>
              <div>
                <dt>Дата зачисления</dt>
                <dd>{profile.enrollment_date ? formatDate(profile.enrollment_date) : "-"}</dd>
              </div>
              <div>
                <dt>Email</dt>
                <dd>
                  <Mail aria-hidden="true" size={14} />
                  <span className="detail-text">{profile.email || "-"}</span>
                </dd>
              </div>
            </dl>
          </div>
        </article>

        <SummaryCard label="Средний балл" value={grades.average ? formatDecimal(grades.average) : "-"} />
        <SummaryCard label="Всего оценок" value={grades.total.toString()} />
        <SummaryCard label="Занятий учтено" value={attendance.total.toString()} />
      </div>

      <div className="attendance-summary">
        <SummaryCard label="Присутствовал" value={(attendance.by_status.present ?? 0).toString()} />
        <SummaryCard label="Отсутствовал" value={(attendance.by_status.absent ?? 0).toString()} />
        <SummaryCard label="Уважительная причина" value={(attendance.by_status.excused ?? 0).toString()} />
        <SummaryCard label="Опоздал" value={(attendance.by_status.late ?? 0).toString()} />
      </div>

      <section className="panel">
        <SectionToolbar title="Оценки">
          <TextField
            icon={<Search aria-hidden="true" size={16} />}
            label="Поиск"
            onChange={(event) => setGradeSearch(event.target.value)}
            placeholder="Дисциплина, работа, преподаватель"
            value={gradeSearch}
          />
          <SelectField
            label="Период"
            onChange={(event) => setGradePeriod(event.target.value)}
            options={[{ label: "Все периоды", value: "" }, ...gradePeriods]}
            value={gradePeriod}
          />
        </SectionToolbar>
        <DataTable
          columns={gradeColumns}
          data={filteredGrades}
          emptyText="По выбранным фильтрам оценок нет."
          getRowKey={(row) => row.id}
          isLoading={gradesQuery.isLoading}
        />
      </section>

      <section className="panel">
        <SectionToolbar title="Посещаемость">
          <TextField
            icon={<Search aria-hidden="true" size={16} />}
            label="Поиск"
            onChange={(event) => setAttendanceSearch(event.target.value)}
            placeholder="Дисциплина, тема, преподаватель"
            value={attendanceSearch}
          />
          <SelectField
            icon={<CalendarDays aria-hidden="true" size={16} />}
            label="Статус"
            onChange={(event) => setAttendanceStatus(event.target.value)}
            options={[
              { label: "Все статусы", value: "" },
              { label: attendanceLabels.present, value: "present" },
              { label: attendanceLabels.absent, value: "absent" },
              { label: attendanceLabels.excused, value: "excused" },
              { label: attendanceLabels.late, value: "late" },
            ]}
            value={attendanceStatus}
          />
        </SectionToolbar>
        <DataTable
          columns={attendanceColumns}
          data={filteredAttendance}
          emptyText="По выбранным фильтрам посещаемости нет."
          getRowKey={(row) => row.id}
          isLoading={attendanceQuery.isLoading}
        />
      </section>
    </section>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="summary-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function uniqueOptions(values: string[]) {
  return Array.from(new Set(values.filter(Boolean))).map((value) => ({ label: value, value }));
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU").format(new Date(value));
}

function formatDecimal(value: string) {
  return Number(value).toLocaleString("ru-RU", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  });
}
