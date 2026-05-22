import { FormEvent, useMemo, useState } from "react";
import { AxiosError } from "axios";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BookOpenCheck,
  BriefcaseBusiness,
  CalendarDays,
  Mail,
  Pencil,
  Plus,
  Search,
  Trash2,
  UserRoundCog,
} from "lucide-react";

import type { AttendanceStatus } from "../../api/student";
import {
  createAttendance,
  createClassSession,
  createGrade,
  createGradeWork,
  deleteAttendance,
  deleteClassSession,
  deleteGrade,
  deleteGradeWork,
  fetchTeacherAssignments,
  fetchTeacherAttendance,
  fetchTeacherClassSessions,
  fetchTeacherDashboard,
  fetchTeacherGrades,
  fetchTeacherGradeWorks,
  fetchTeacherStudents,
  updateAttendance,
  updateGrade,
} from "../../api/teacher";
import type {
  AttendancePayload,
  ClassSessionPayload,
  GradePayload,
  GradeWorkPayload,
  TeacherAssignment,
  TeacherAttendance,
  TeacherClassSession,
  TeacherGrade,
  TeacherGradeWork,
  TeacherStudent,
} from "../../api/teacher";
import { StatusBadge } from "../../components/StatusBadge";
import {
  Button,
  DataTable,
  ErrorState,
  LoadingState,
  Modal,
  PageHeader,
  SectionToolbar,
  SelectField,
  TextareaField,
  TextField,
} from "../../components/ui";
import type { DataTableColumn } from "../../components/ui";

type ModalKind = "attendance" | "class-session" | "grade" | "grade-work" | null;
type TeacherTab = "attendance" | "grades" | "overview";

type DeleteTarget = {
  id: number;
  kind: "attendance" | "class-session" | "grade" | "grade-work";
  title: string;
  warning?: string;
};

type GradeWorkForm = {
  assignment: string;
  max_score: string;
  title: string;
  weight: string;
  work_date: string;
  work_type: string;
};

type GradeForm = {
  comment: string;
  student: string;
  value: string;
  work: string;
};

type ClassSessionForm = {
  assignment: string;
  session_date: string;
  topic: string;
};

type AttendanceForm = {
  comment: string;
  session: string;
  status: AttendanceStatus;
  student: string;
};

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

const workTypeOptions = [
  { label: "Работа на занятии", value: "classwork" },
  { label: "Домашняя работа", value: "homework" },
  { label: "Контрольная работа", value: "test" },
  { label: "Экзамен", value: "exam" },
  { label: "Другое", value: "other" },
];

const attendanceStatusOptions = [
  { label: attendanceLabels.present, value: "present" },
  { label: attendanceLabels.absent, value: "absent" },
  { label: attendanceLabels.excused, value: "excused" },
  { label: attendanceLabels.late, value: "late" },
];

const today = new Date().toISOString().slice(0, 10);
const emptyAssignments: TeacherAssignment[] = [];
const emptyStudents: TeacherStudent[] = [];
const emptyGradeWorks: TeacherGradeWork[] = [];
const emptySessions: TeacherClassSession[] = [];

export function TeacherCabinetPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TeacherTab>("overview");
  const [search, setSearch] = useState("");
  const [group, setGroup] = useState("");
  const [attendanceStatus, setAttendanceStatus] = useState("");
  const [modalKind, setModalKind] = useState<ModalKind>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null);
  const [editingGrade, setEditingGrade] = useState<TeacherGrade | null>(null);
  const [editingAttendance, setEditingAttendance] = useState<TeacherAttendance | null>(null);
  const [gradeWorkForm, setGradeWorkForm] = useState<GradeWorkForm>(emptyGradeWorkForm());
  const [gradeForm, setGradeForm] = useState<GradeForm>(emptyGradeForm());
  const [classSessionForm, setClassSessionForm] = useState<ClassSessionForm>(emptyClassSessionForm());
  const [attendanceForm, setAttendanceForm] = useState<AttendanceForm>(emptyAttendanceForm());

  const dashboardQuery = useQuery({ queryKey: ["teacher", "dashboard"], queryFn: fetchTeacherDashboard });
  const assignmentsQuery = useQuery({ queryKey: ["teacher", "assignments"], queryFn: fetchTeacherAssignments });
  const studentsQuery = useQuery({ queryKey: ["teacher", "students"], queryFn: fetchTeacherStudents });
  const gradeWorksQuery = useQuery({ queryKey: ["teacher", "gradeWorks"], queryFn: fetchTeacherGradeWorks });
  const gradesQuery = useQuery({ queryKey: ["teacher", "grades"], queryFn: fetchTeacherGrades });
  const sessionsQuery = useQuery({ queryKey: ["teacher", "sessions"], queryFn: fetchTeacherClassSessions });
  const attendanceQuery = useQuery({ queryKey: ["teacher", "attendance"], queryFn: fetchTeacherAttendance });

  const assignments = assignmentsQuery.data ?? emptyAssignments;
  const students = studentsQuery.data ?? emptyStudents;
  const gradeWorks = gradeWorksQuery.data ?? emptyGradeWorks;
  const sessions = sessionsQuery.data ?? emptySessions;

  const invalidateTeacherQueries = async () => {
    await queryClient.invalidateQueries({ queryKey: ["teacher"] });
  };

  const createGradeWorkMutation = useMutation({
    mutationFn: (payload: GradeWorkPayload) => createGradeWork(payload),
    onSuccess: async () => {
      closeModal();
      await invalidateTeacherQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const createClassSessionMutation = useMutation({
    mutationFn: (payload: ClassSessionPayload) => createClassSession(payload),
    onSuccess: async () => {
      closeModal();
      await invalidateTeacherQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const saveGradeMutation = useMutation({
    mutationFn: (payload: GradePayload) =>
      editingGrade
        ? updateGrade(editingGrade.id, { comment: payload.comment, value: payload.value })
        : createGrade(payload),
    onSuccess: async () => {
      closeModal();
      await invalidateTeacherQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const saveAttendanceMutation = useMutation({
    mutationFn: (payload: AttendancePayload) =>
      editingAttendance
        ? updateAttendance(editingAttendance.id, { comment: payload.comment, status: payload.status })
        : createAttendance(payload),
    onSuccess: async () => {
      closeModal();
      await invalidateTeacherQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const deleteMutation = useMutation({
    mutationFn: async (target: DeleteTarget) => {
      if (target.kind === "grade-work") {
        await deleteGradeWork(target.id);
      }
      if (target.kind === "grade") {
        await deleteGrade(target.id);
      }
      if (target.kind === "class-session") {
        await deleteClassSession(target.id);
      }
      if (target.kind === "attendance") {
        await deleteAttendance(target.id);
      }
    },
    onSuccess: async () => {
      setDeleteTarget(null);
      await invalidateTeacherQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const groupOptions = useMemo(
    () => uniqueOptions([...assignments.map((item) => item.group_name), ...students.map((item) => item.group_name)]),
    [assignments, students],
  );

  const assignmentOptions = useMemo(
    () =>
      assignments.map((assignment) => ({
        label: `${assignment.subject_name} - ${assignment.group_name} (${assignment.period_name})`,
        value: assignment.id.toString(),
      })),
    [assignments],
  );

  const gradeWorkOptions = useMemo(
    () =>
      gradeWorks.map((work) => ({
        label: `${work.title} - ${work.group_name}`,
        value: work.id.toString(),
      })),
    [gradeWorks],
  );

  const sessionOptions = useMemo(
    () =>
      sessions.map((session) => ({
        label: `${session.topic} - ${session.group_name}, ${formatDate(session.session_date)}`,
        value: session.id.toString(),
      })),
    [sessions],
  );

  const selectedGradeWork = gradeWorks.find((work) => work.id.toString() === gradeForm.work);
  const selectedSession = sessions.find((session) => session.id.toString() === attendanceForm.session);
  const gradeStudentOptions = studentOptionsByGroup(students, selectedGradeWork?.group_name);
  const attendanceStudentOptions = studentOptionsByGroup(students, selectedSession?.group_name);

  const filteredAssignments = useMemo(
    () => filterRows(assignments, search, group, (row) => `${row.subject_name} ${row.subject_code} ${row.group_name} ${row.period_name}`, (row) => row.group_name),
    [assignments, group, search],
  );
  const filteredStudents = useMemo(
    () => filterRows(students, search, group, (row) => `${row.full_name} ${row.username} ${row.student_id} ${row.group_name}`, (row) => row.group_name),
    [group, search, students],
  );
  const filteredGradeWorks = useMemo(
    () => filterRows(gradeWorks, search, group, (row) => `${row.title} ${row.subject_name} ${row.group_name} ${row.period_name}`, (row) => row.group_name),
    [gradeWorks, group, search],
  );
  const filteredGrades = useMemo(
    () => filterRows(gradesQuery.data ?? [], search, group, (row) => `${row.student_name} ${row.work_title} ${row.subject_name} ${row.group_name}`, (row) => row.group_name),
    [gradesQuery.data, group, search],
  );
  const filteredSessions = useMemo(
    () => filterRows(sessions, search, group, (row) => `${row.topic} ${row.subject_name} ${row.group_name} ${row.period_name}`, (row) => row.group_name),
    [group, search, sessions],
  );
  const filteredAttendance = useMemo(() => {
    return filterRows(
      attendanceQuery.data ?? [],
      search,
      group,
      (row) => `${row.student_name} ${row.session_topic} ${row.subject_name} ${row.group_name}`,
      (row) => row.group_name,
    ).filter((row) => !attendanceStatus || row.status === attendanceStatus);
  }, [attendanceQuery.data, attendanceStatus, group, search]);

  const gradeColumns: Array<DataTableColumn<TeacherGrade>> = [
    ...baseGradeColumns,
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => (
        <div className="table-actions">
          <Button icon={<Pencil aria-hidden="true" size={14} />} onClick={() => openEditGrade(row)} size="sm" variant="ghost">
            Изменить
          </Button>
          <Button icon={<Trash2 aria-hidden="true" size={14} />} onClick={() => confirmDeleteGrade(row)} size="sm" variant="danger">
            Удалить
          </Button>
        </div>
      ),
      width: "230px",
    },
  ];

  const attendanceColumns: Array<DataTableColumn<TeacherAttendance>> = [
    ...baseAttendanceColumns,
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => (
        <div className="table-actions">
          <Button icon={<Pencil aria-hidden="true" size={14} />} onClick={() => openEditAttendance(row)} size="sm" variant="ghost">
            Изменить
          </Button>
          <Button icon={<Trash2 aria-hidden="true" size={14} />} onClick={() => confirmDeleteAttendance(row)} size="sm" variant="danger">
            Удалить
          </Button>
        </div>
      ),
      width: "230px",
    },
  ];

  const gradeWorkColumnsWithActions: Array<DataTableColumn<TeacherGradeWork>> = [
    ...gradeWorkColumns,
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => (
        <Button icon={<Trash2 aria-hidden="true" size={14} />} onClick={() => confirmDeleteGradeWork(row)} size="sm" variant="danger">
          Удалить
        </Button>
      ),
      width: "130px",
    },
  ];

  const sessionColumnsWithActions: Array<DataTableColumn<TeacherClassSession>> = [
    ...sessionColumns,
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => (
        <Button icon={<Trash2 aria-hidden="true" size={14} />} onClick={() => confirmDeleteSession(row)} size="sm" variant="danger">
          Удалить
        </Button>
      ),
      width: "130px",
    },
  ];

  if (dashboardQuery.isLoading) {
    return <LoadingState text="Загружаем кабинет преподавателя" />;
  }

  if (dashboardQuery.isError || !dashboardQuery.data) {
    return <ErrorState text="Проверьте, что у пользователя создан профиль преподавателя и есть назначение." />;
  }

  const dashboard = dashboardQuery.data;
  const profile = dashboard.profile;
  const isSaving =
    createClassSessionMutation.isPending ||
    createGradeWorkMutation.isPending ||
    saveAttendanceMutation.isPending ||
    saveGradeMutation.isPending;
  const toolbarActions =
    activeTab === "grades" ? (
      <>
        <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openGradeWorkModal} size="sm" variant="primary">
          Работа
        </Button>
        <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openCreateGradeModal} size="sm" variant="secondary">
          Оценка
        </Button>
      </>
    ) : activeTab === "attendance" ? (
      <>
        <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openClassSessionModal} size="sm" variant="primary">
          Занятие
        </Button>
        <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openCreateAttendanceModal} size="sm" variant="secondary">
          Посещаемость
        </Button>
      </>
    ) : null;

  function openGradeWorkModal() {
    const firstAssignment = assignments[0];
    setGradeWorkForm({ ...emptyGradeWorkForm(), assignment: firstAssignment?.id.toString() ?? "" });
    openModal("grade-work");
  }

  function openClassSessionModal() {
    const firstAssignment = assignments[0];
    setClassSessionForm({ ...emptyClassSessionForm(), assignment: firstAssignment?.id.toString() ?? "" });
    openModal("class-session");
  }

  function openCreateGradeModal() {
    const firstWork = gradeWorks[0];
    const firstStudent = studentOptionsByGroup(students, firstWork?.group_name)[0];
    setEditingGrade(null);
    setGradeForm({ ...emptyGradeForm(), student: firstStudent?.value ?? "", work: firstWork?.id.toString() ?? "" });
    openModal("grade");
  }

  function openEditGrade(grade: TeacherGrade) {
    setEditingGrade(grade);
    setGradeForm({
      comment: grade.comment,
      student: grade.student.toString(),
      value: grade.value,
      work: grade.work.toString(),
    });
    openModal("grade");
  }

  function openCreateAttendanceModal() {
    const firstSession = sessions[0];
    const firstStudent = studentOptionsByGroup(students, firstSession?.group_name)[0];
    setEditingAttendance(null);
    setAttendanceForm({
      ...emptyAttendanceForm(),
      session: firstSession?.id.toString() ?? "",
      student: firstStudent?.value ?? "",
    });
    openModal("attendance");
  }

  function openEditAttendance(record: TeacherAttendance) {
    setEditingAttendance(record);
    setAttendanceForm({
      comment: record.comment,
      session: record.session.toString(),
      status: record.status,
      student: record.student.toString(),
    });
    openModal("attendance");
  }

  function openModal(kind: ModalKind) {
    setFormError(null);
    setModalKind(kind);
  }

  function closeModal() {
    setFormError(null);
    setModalKind(null);
    setEditingGrade(null);
    setEditingAttendance(null);
  }

  function handleGradeWorkSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createGradeWorkMutation.mutate({
      assignment: Number(gradeWorkForm.assignment),
      max_score: gradeWorkForm.max_score,
      title: gradeWorkForm.title,
      weight: gradeWorkForm.weight,
      work_date: gradeWorkForm.work_date,
      work_type: gradeWorkForm.work_type,
    });
  }

  function handleClassSessionSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createClassSessionMutation.mutate({
      assignment: Number(classSessionForm.assignment),
      session_date: classSessionForm.session_date,
      topic: classSessionForm.topic,
    });
  }

  function handleGradeSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    saveGradeMutation.mutate({
      comment: gradeForm.comment,
      student: Number(gradeForm.student),
      value: gradeForm.value,
      work: Number(gradeForm.work),
    });
  }

  function handleAttendanceSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    saveAttendanceMutation.mutate({
      comment: attendanceForm.comment,
      session: Number(attendanceForm.session),
      status: attendanceForm.status,
      student: Number(attendanceForm.student),
    });
  }

  function handleGradeWorkChange(workId: string) {
    const nextWork = gradeWorks.find((work) => work.id.toString() === workId);
    const nextStudent = studentOptionsByGroup(students, nextWork?.group_name)[0];
    setGradeForm((current) => ({ ...current, student: nextStudent?.value ?? "", work: workId }));
  }

  function handleSessionChange(sessionId: string) {
    const nextSession = sessions.find((session) => session.id.toString() === sessionId);
    const nextStudent = studentOptionsByGroup(students, nextSession?.group_name)[0];
    setAttendanceForm((current) => ({ ...current, session: sessionId, student: nextStudent?.value ?? "" }));
  }

  function confirmDeleteGradeWork(work: TeacherGradeWork) {
    setFormError(null);
    setDeleteTarget({
      id: work.id,
      kind: "grade-work",
      title: work.title,
      warning: "Связанные оценки по этой работе тоже будут удалены.",
    });
  }

  function confirmDeleteGrade(grade: TeacherGrade) {
    setFormError(null);
    setDeleteTarget({
      id: grade.id,
      kind: "grade",
      title: `${grade.student_name} - ${grade.work_title}`,
    });
  }

  function confirmDeleteSession(session: TeacherClassSession) {
    setFormError(null);
    setDeleteTarget({
      id: session.id,
      kind: "class-session",
      title: session.topic,
      warning: "Связанные отметки посещаемости по этому занятию тоже будут удалены.",
    });
  }

  function confirmDeleteAttendance(record: TeacherAttendance) {
    setFormError(null);
    setDeleteTarget({
      id: record.id,
      kind: "attendance",
      title: `${record.student_name} - ${record.session_topic}`,
    });
  }

  return (
    <section className="content-stack">
      <PageHeader
        badge={<StatusBadge tone="success">Кабинет преподавателя</StatusBadge>}
        description="Назначения, студенты, журнал оценок и посещаемость по вашим группам."
        icon={<BookOpenCheck aria-hidden="true" size={34} />}
        title={profile.full_name || profile.username}
      />

      <div className="student-profile-grid">
        <article className="profile-panel">
          <div className="profile-panel__icon">
            <UserRoundCog aria-hidden="true" size={24} />
          </div>
          <div>
            <h2>Профиль</h2>
            <dl className="details-list">
              <div>
                <dt>Должность</dt>
                <dd>{profile.position || "-"}</dd>
              </div>
              <div>
                <dt>Табельный номер</dt>
                <dd>{profile.personnel_number}</dd>
              </div>
              <div>
                <dt>Назначений</dt>
                <dd>{dashboard.assignments_total}</dd>
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

        <SummaryCard label="Групп" value={dashboard.groups_total.toString()} />
        <SummaryCard label="Студентов" value={dashboard.students_total.toString()} />
        <SummaryCard label="Оценок" value={dashboard.grades_total.toString()} />
      </div>

      <div className="attendance-summary">
        <SummaryCard label="Работ" value={dashboard.grade_works_total.toString()} />
        <SummaryCard label="Занятий" value={dashboard.class_sessions_total.toString()} />
        <SummaryCard label="Посещаемость" value={dashboard.attendance_total.toString()} />
        <SummaryCard label="Отсутствий" value={(dashboard.attendance_by_status.absent ?? 0).toString()} />
      </div>

      <section className="panel">
        <SectionToolbar actions={toolbarActions} title="Рабочая область">
          <div className="segmented-control" role="tablist">
            <button className={activeTab === "overview" ? "is-active" : ""} onClick={() => setActiveTab("overview")} type="button">
              Обзор
            </button>
            <button className={activeTab === "grades" ? "is-active" : ""} onClick={() => setActiveTab("grades")} type="button">
              Оценки
            </button>
            <button className={activeTab === "attendance" ? "is-active" : ""} onClick={() => setActiveTab("attendance")} type="button">
              Посещаемость
            </button>
          </div>
          <TextField
            icon={<Search aria-hidden="true" size={16} />}
            label="Поиск"
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Группа, студент, дисциплина, тема"
            value={search}
          />
          <SelectField
            icon={<BriefcaseBusiness aria-hidden="true" size={16} />}
            label="Группа"
            onChange={(event) => setGroup(event.target.value)}
            options={[{ label: "Все группы", value: "" }, ...groupOptions]}
            value={group}
          />
        </SectionToolbar>
      </section>

      {activeTab === "overview" ? (
        <>
          <section className="panel">
            <SectionToolbar title="Мои группы и дисциплины" />
            <DataTable columns={assignmentColumns} data={filteredAssignments} emptyText="Групп и дисциплин по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={assignmentsQuery.isLoading} />
          </section>

          <section className="panel">
            <SectionToolbar title="Студенты групп" />
            <DataTable columns={studentColumns} data={filteredStudents} emptyText="Студентов по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={studentsQuery.isLoading} />
          </section>
        </>
      ) : null}

      {activeTab === "grades" ? (
        <>
          <section className="panel">
            <SectionToolbar
              actions={
                <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openGradeWorkModal} size="sm" variant="primary">
                  Добавить работу
                </Button>
              }
              title="Работы журнала"
            />
            <DataTable columns={gradeWorkColumnsWithActions} data={filteredGradeWorks} emptyText="Работ по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={gradeWorksQuery.isLoading} />
          </section>

          <section className="panel">
            <SectionToolbar
              actions={
                <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openCreateGradeModal} size="sm" variant="primary">
                  Выставить оценку
                </Button>
              }
              title="Оценки"
            />
            <DataTable columns={gradeColumns} data={filteredGrades} emptyText="Оценок по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={gradesQuery.isLoading} />
          </section>
        </>
      ) : null}

      {activeTab === "attendance" ? (
        <>
          <section className="panel">
            <SectionToolbar
              actions={
                <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openClassSessionModal} size="sm" variant="primary">
                  Добавить занятие
                </Button>
              }
              title="Занятия"
            />
            <DataTable columns={sessionColumnsWithActions} data={filteredSessions} emptyText="Занятий по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={sessionsQuery.isLoading} />
          </section>

          <section className="panel">
            <SectionToolbar
              actions={
                <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openCreateAttendanceModal} size="sm" variant="primary">
                  Отметить посещаемость
                </Button>
              }
              title="Посещаемость"
            >
              <SelectField
                icon={<CalendarDays aria-hidden="true" size={16} />}
                label="Статус"
                onChange={(event) => setAttendanceStatus(event.target.value)}
                options={[{ label: "Все статусы", value: "" }, ...attendanceStatusOptions]}
                value={attendanceStatus}
              />
            </SectionToolbar>
            <DataTable columns={attendanceColumns} data={filteredAttendance} emptyText="Посещаемости по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={attendanceQuery.isLoading} />
          </section>
        </>
      ) : null}

      <Modal
        footer={<ModalFooter formId="grade-work-form" isSaving={isSaving} onCancel={closeModal} />}
        isOpen={modalKind === "grade-work"}
        onClose={closeModal}
        title="Новая работа журнала"
      >
        <form className="form-grid" id="grade-work-form" onSubmit={handleGradeWorkSubmit}>
          <SelectField label="Назначение" onChange={(event) => setGradeWorkForm((current) => ({ ...current, assignment: event.target.value }))} options={assignmentOptions} required value={gradeWorkForm.assignment} />
          <TextField label="Название работы" onChange={(event) => setGradeWorkForm((current) => ({ ...current, title: event.target.value }))} placeholder="Например, Контрольная работа 1" required value={gradeWorkForm.title} />
          <SelectField label="Тип работы" onChange={(event) => setGradeWorkForm((current) => ({ ...current, work_type: event.target.value }))} options={workTypeOptions} required value={gradeWorkForm.work_type} />
          <TextField label="Дата работы" onChange={(event) => setGradeWorkForm((current) => ({ ...current, work_date: event.target.value }))} required type="date" value={gradeWorkForm.work_date} />
          <div className="form-grid form-grid--two">
            <TextField label="Максимальный балл" min="1" onChange={(event) => setGradeWorkForm((current) => ({ ...current, max_score: event.target.value }))} required step="0.01" type="number" value={gradeWorkForm.max_score} />
            <TextField label="Вес" min="0.01" onChange={(event) => setGradeWorkForm((current) => ({ ...current, weight: event.target.value }))} required step="0.01" type="number" value={gradeWorkForm.weight} />
          </div>
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal
        footer={<ModalFooter formId="class-session-form" isSaving={isSaving} onCancel={closeModal} />}
        isOpen={modalKind === "class-session"}
        onClose={closeModal}
        title="Новое занятие"
      >
        <form className="form-grid" id="class-session-form" onSubmit={handleClassSessionSubmit}>
          <SelectField label="Назначение" onChange={(event) => setClassSessionForm((current) => ({ ...current, assignment: event.target.value }))} options={assignmentOptions} required value={classSessionForm.assignment} />
          <TextField label="Дата занятия" onChange={(event) => setClassSessionForm((current) => ({ ...current, session_date: event.target.value }))} required type="date" value={classSessionForm.session_date} />
          <TextField label="Тема занятия" onChange={(event) => setClassSessionForm((current) => ({ ...current, topic: event.target.value }))} placeholder="Например, Практическое занятие" required value={classSessionForm.topic} />
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal
        footer={<ModalFooter formId="grade-form" isSaving={isSaving} onCancel={closeModal} />}
        isOpen={modalKind === "grade"}
        onClose={closeModal}
        title={editingGrade ? "Изменить оценку" : "Выставить оценку"}
      >
        <form className="form-grid" id="grade-form" onSubmit={handleGradeSubmit}>
          <SelectField disabled={Boolean(editingGrade)} label="Работа" onChange={(event) => handleGradeWorkChange(event.target.value)} options={gradeWorkOptions} required value={gradeForm.work} />
          <SelectField disabled={Boolean(editingGrade)} label="Студент" onChange={(event) => setGradeForm((current) => ({ ...current, student: event.target.value }))} options={gradeStudentOptions} required value={gradeForm.student} />
          <TextField label="Оценка" min="0" onChange={(event) => setGradeForm((current) => ({ ...current, value: event.target.value }))} required step="0.01" type="number" value={gradeForm.value} />
          <TextareaField label="Комментарий" onChange={(event) => setGradeForm((current) => ({ ...current, comment: event.target.value }))} value={gradeForm.comment} />
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal
        footer={<ModalFooter formId="attendance-form" isSaving={isSaving} onCancel={closeModal} />}
        isOpen={modalKind === "attendance"}
        onClose={closeModal}
        title={editingAttendance ? "Изменить посещаемость" : "Отметить посещаемость"}
      >
        <form className="form-grid" id="attendance-form" onSubmit={handleAttendanceSubmit}>
          <SelectField disabled={Boolean(editingAttendance)} label="Занятие" onChange={(event) => handleSessionChange(event.target.value)} options={sessionOptions} required value={attendanceForm.session} />
          <SelectField disabled={Boolean(editingAttendance)} label="Студент" onChange={(event) => setAttendanceForm((current) => ({ ...current, student: event.target.value }))} options={attendanceStudentOptions} required value={attendanceForm.student} />
          <SelectField label="Статус" onChange={(event) => setAttendanceForm((current) => ({ ...current, status: event.target.value as AttendanceStatus }))} options={attendanceStatusOptions} required value={attendanceForm.status} />
          <TextareaField label="Комментарий" onChange={(event) => setAttendanceForm((current) => ({ ...current, comment: event.target.value }))} value={attendanceForm.comment} />
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal
        footer={
          <>
            <Button disabled={deleteMutation.isPending} onClick={() => setDeleteTarget(null)} variant="ghost">
              Отмена
            </Button>
            <Button
              disabled={deleteMutation.isPending || !deleteTarget}
              icon={<Trash2 aria-hidden="true" size={16} />}
              onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget)}
              variant="danger"
            >
              {deleteMutation.isPending ? "Удаляем" : "Удалить"}
            </Button>
          </>
        }
        isOpen={Boolean(deleteTarget)}
        onClose={() => setDeleteTarget(null)}
        title="Подтвердите удаление"
      >
        <div className="confirm-delete">
          <p>
            Вы действительно хотите удалить <strong>{deleteTarget?.title}</strong>?
          </p>
          {deleteTarget?.warning ? <p className="confirm-delete__warning">{deleteTarget.warning}</p> : null}
          <FormError text={formError} />
        </div>
      </Modal>
    </section>
  );
}

function ModalFooter({ formId, isSaving, onCancel }: { formId: string; isSaving: boolean; onCancel: () => void }) {
  return (
    <>
      <Button disabled={isSaving} onClick={onCancel} variant="ghost">
        Отмена
      </Button>
      <Button disabled={isSaving} form={formId} type="submit" variant="primary">
        {isSaving ? "Сохраняем" : "Сохранить"}
      </Button>
    </>
  );
}

function FormError({ text }: { text: string | null }) {
  return text ? <div className="form-error">{text}</div> : null;
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="summary-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

const assignmentColumns: Array<DataTableColumn<TeacherAssignment>> = [
  {
    key: "subject",
    header: "Дисциплина",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.subject_name}</strong>
        <span>{row.subject_code}</span>
      </div>
    ),
  },
  { key: "group", header: "Группа", render: (row) => row.group_name, width: "130px" },
  { key: "period", header: "Период", render: (row) => row.period_name },
];

const studentColumns: Array<DataTableColumn<TeacherStudent>> = [
  {
    key: "name",
    header: "Студент",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.full_name || row.username}</strong>
        <span>ID {row.student_id}</span>
      </div>
    ),
  },
  { key: "group", header: "Группа", render: (row) => row.group_name, width: "130px" },
  { key: "enrollment", header: "Дата зачисления", render: (row) => (row.enrollment_date ? formatDate(row.enrollment_date) : "-"), width: "170px" },
];

const gradeWorkColumns: Array<DataTableColumn<TeacherGradeWork>> = [
  { key: "date", header: "Дата", render: (row) => formatDate(row.work_date), width: "130px" },
  {
    key: "work",
    header: "Работа",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.title}</strong>
        <span>{row.subject_name}</span>
      </div>
    ),
  },
  { key: "group", header: "Группа", render: (row) => row.group_name, width: "130px" },
  { key: "period", header: "Период", render: (row) => row.period_name },
  { key: "score", header: "Макс.", align: "right", render: (row) => formatDecimal(row.max_score), width: "90px" },
];

const baseGradeColumns: Array<DataTableColumn<TeacherGrade>> = [
  {
    key: "student",
    header: "Студент",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.student_name}</strong>
        <span>ID {row.student_id_number}</span>
      </div>
    ),
  },
  {
    key: "work",
    header: "Работа",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.work_title}</strong>
        <span>{formatDate(row.work_date)}</span>
      </div>
    ),
  },
  { key: "subject", header: "Дисциплина", render: (row) => row.subject_name },
  { key: "group", header: "Группа", render: (row) => row.group_name, width: "130px" },
  { key: "value", header: "Оценка", align: "right", render: (row) => <span className="score-chip">{formatDecimal(row.value)}</span>, width: "100px" },
];

const sessionColumns: Array<DataTableColumn<TeacherClassSession>> = [
  { key: "date", header: "Дата", render: (row) => formatDate(row.session_date), width: "130px" },
  {
    key: "topic",
    header: "Занятие",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.topic}</strong>
        <span>{row.subject_name}</span>
      </div>
    ),
  },
  { key: "group", header: "Группа", render: (row) => row.group_name, width: "130px" },
  { key: "period", header: "Период", render: (row) => row.period_name },
];

const baseAttendanceColumns: Array<DataTableColumn<TeacherAttendance>> = [
  {
    key: "student",
    header: "Студент",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.student_name}</strong>
        <span>ID {row.student_id_number}</span>
      </div>
    ),
  },
  {
    key: "session",
    header: "Занятие",
    render: (row) => (
      <div className="table-main-cell">
        <strong>{row.session_topic}</strong>
        <span>
          {row.subject_name}, {formatDate(row.session_date)}
        </span>
      </div>
    ),
  },
  { key: "group", header: "Группа", render: (row) => row.group_name, width: "130px" },
  { key: "status", header: "Статус", render: (row) => <StatusBadge tone={attendanceTone[row.status]}>{attendanceLabels[row.status]}</StatusBadge>, width: "190px" },
];

function emptyGradeWorkForm(): GradeWorkForm {
  return { assignment: "", max_score: "5.00", title: "", weight: "1.00", work_date: today, work_type: "classwork" };
}

function emptyGradeForm(): GradeForm {
  return { comment: "", student: "", value: "", work: "" };
}

function emptyClassSessionForm(): ClassSessionForm {
  return { assignment: "", session_date: today, topic: "" };
}

function emptyAttendanceForm(): AttendanceForm {
  return { comment: "", session: "", status: "present", student: "" };
}

function filterRows<T>(rows: T[], search: string, group: string, buildSearchText: (row: T) => string, getGroup: (row: T) => string) {
  const normalizedSearch = search.trim().toLowerCase();
  return rows.filter((row) => {
    const matchesSearch = !normalizedSearch || buildSearchText(row).toLowerCase().includes(normalizedSearch);
    const matchesGroup = !group || getGroup(row) === group;
    return matchesSearch && matchesGroup;
  });
}

function uniqueOptions(values: string[]) {
  return Array.from(new Set(values.filter(Boolean))).map((value) => ({ label: value, value }));
}

function studentOptionsByGroup(students: TeacherStudent[], groupName?: string) {
  return students
    .filter((student) => !groupName || student.group_name === groupName)
    .map((student) => ({
      label: `${student.full_name || student.username} (ID ${student.student_id})`,
      value: student.id.toString(),
    }));
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

function getApiErrorMessage(error: unknown): string {
  if (error instanceof AxiosError && error.response?.data) {
    return flattenError(error.response.data);
  }
  return "Не удалось сохранить данные. Проверьте поля формы.";
}

function flattenError(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map(flattenError).join(" ");
  }
  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => `${key}: ${flattenError(item)}`)
      .join(" ");
  }
  return "Ошибка сохранения.";
}
