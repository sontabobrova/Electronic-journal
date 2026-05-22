import { FormEvent, useMemo, useState } from "react";
import { AxiosError } from "axios";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { KeyRound, Plus, Search, ShieldCheck, Trash2 } from "lucide-react";

import type { CurrentUser, UserRole } from "../../api/auth";
import {
  createAssignment,
  createGroup,
  createPeriod,
  createStudentProfile,
  createSubject,
  createTeacherProfile,
  createUser,
  deleteAssignment,
  deleteGroup,
  deletePeriod,
  deleteSubject,
  fetchAdminDashboard,
  fetchAssignmentsAdmin,
  fetchAuditLogs,
  fetchGroups,
  fetchPeriods,
  fetchStudentsAdmin,
  fetchSubjects,
  fetchTeachersAdmin,
  fetchUsers,
  resetUserPassword,
  updateAssignment,
  updateGroup,
  updatePeriod,
  updateStudentProfile,
  updateSubject,
  updateTeacherProfile,
  updateUser,
} from "../../api/admin";
import type {
  AcademicGroup,
  AcademicPeriod,
  AuditLog,
  StudentProfileAdmin,
  Subject,
  TeacherProfileAdmin,
  TeachingAssignmentAdmin,
  UserPayload,
} from "../../api/admin";
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

type AdminTab = "audit" | "education" | "users";
type ModalKind = "assignment" | "group" | "period" | "reset-password" | "subject" | "user" | null;
type DeleteTarget =
  | { id: number; kind: "assignment"; label: string }
  | { id: number; kind: "group"; label: string }
  | { id: number; kind: "period"; label: string }
  | { id: number; kind: "subject"; label: string }
  | null;

type UserForm = {
  access_expires_at: string;
  email: string;
  first_name: string;
  is_active: string;
  last_name: string;
  password: string;
  phone: string;
  role: UserRole;
  student_enrollment_date: string;
  student_group: string;
  student_id: string;
  teacher_personnel_number: string;
  teacher_position: string;
  username: string;
};

const roleLabels: Record<UserRole, string> = {
  admin: "Администратор",
  teacher: "Преподаватель",
  student: "Студент",
};

const roleOptions = [
  { label: roleLabels.admin, value: "admin" },
  { label: roleLabels.teacher, value: "teacher" },
  { label: roleLabels.student, value: "student" },
];

const activeOptions = [
  { label: "Активен", value: "true" },
  { label: "Отключен", value: "false" },
];

const today = new Date().toISOString().slice(0, 10);
const emptyUsers: CurrentUser[] = [];
const emptyGroups: AcademicGroup[] = [];
const emptySubjects: Subject[] = [];
const emptyPeriods: AcademicPeriod[] = [];
const emptyStudents: StudentProfileAdmin[] = [];
const emptyTeachers: TeacherProfileAdmin[] = [];
const emptyAssignments: TeachingAssignmentAdmin[] = [];
const emptyAuditLogs: AuditLog[] = [];

export function AdminCabinetPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<AdminTab>("users");
  const [search, setSearch] = useState("");
  const [modalKind, setModalKind] = useState<ModalKind>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [editingUser, setEditingUser] = useState<CurrentUser | null>(null);
  const [editingGroup, setEditingGroup] = useState<AcademicGroup | null>(null);
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null);
  const [editingPeriod, setEditingPeriod] = useState<AcademicPeriod | null>(null);
  const [editingAssignment, setEditingAssignment] = useState<TeachingAssignmentAdmin | null>(null);
  const [resetUser, setResetUser] = useState<CurrentUser | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget>(null);
  const [newPassword, setNewPassword] = useState("");
  const [userForm, setUserForm] = useState<UserForm>(emptyUserForm());
  const [groupForm, setGroupForm] = useState({ enrollment_year: new Date().getFullYear().toString(), is_active: "true", name: "" });
  const [subjectForm, setSubjectForm] = useState({ code: "", description: "", is_active: "true", name: "" });
  const [periodForm, setPeriodForm] = useState({ ends_at: today, is_active: "true", name: "", starts_at: today });
  const [assignmentForm, setAssignmentForm] = useState({ group: "", period: "", subject: "", teacher: "" });

  const dashboardQuery = useQuery({ queryKey: ["admin", "dashboard"], queryFn: fetchAdminDashboard });
  const usersQuery = useQuery({ queryKey: ["admin", "users"], queryFn: fetchUsers });
  const groupsQuery = useQuery({ queryKey: ["admin", "groups"], queryFn: fetchGroups });
  const subjectsQuery = useQuery({ queryKey: ["admin", "subjects"], queryFn: fetchSubjects });
  const periodsQuery = useQuery({ queryKey: ["admin", "periods"], queryFn: fetchPeriods });
  const studentsQuery = useQuery({ queryKey: ["admin", "students"], queryFn: fetchStudentsAdmin });
  const teachersQuery = useQuery({ queryKey: ["admin", "teachers"], queryFn: fetchTeachersAdmin });
  const assignmentsQuery = useQuery({ queryKey: ["admin", "assignments"], queryFn: fetchAssignmentsAdmin });
  const auditQuery = useQuery({ queryKey: ["admin", "audit"], queryFn: fetchAuditLogs });

  const invalidateAdminQueries = async () => {
    await queryClient.invalidateQueries({ queryKey: ["admin"] });
  };

  const saveUserMutation = useMutation({
    mutationFn: async (payload: UserPayload) => {
      const savedUser = editingUser ? await updateUser(editingUser.id, stripEmptyPassword(payload)) : await createUser(payload);
      await syncRoleProfile(savedUser.id, payload.role);
      return savedUser;
    },
    onSuccess: async () => {
      closeModal();
      await invalidateAdminQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const resetPasswordMutation = useMutation({
    mutationFn: () => resetUserPassword(resetUser!.id, newPassword),
    onSuccess: async () => {
      closeModal();
      await invalidateAdminQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const createGroupMutation = useMutation({
    mutationFn: () => {
      const payload = {
        enrollment_year: Number(groupForm.enrollment_year),
        is_active: groupForm.is_active === "true",
        name: groupForm.name,
      };
      return editingGroup ? updateGroup(editingGroup.id, payload) : createGroup(payload);
    },
    onSuccess: async () => {
      closeModal();
      await invalidateAdminQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const createSubjectMutation = useMutation({
    mutationFn: () => {
      const payload = {
        code: subjectForm.code,
        description: subjectForm.description,
        is_active: subjectForm.is_active === "true",
        name: subjectForm.name,
      };
      return editingSubject ? updateSubject(editingSubject.id, payload) : createSubject(payload);
    },
    onSuccess: async () => {
      closeModal();
      await invalidateAdminQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const createPeriodMutation = useMutation({
    mutationFn: () => {
      const payload = {
        ends_at: periodForm.ends_at,
        is_active: periodForm.is_active === "true",
        name: periodForm.name,
        starts_at: periodForm.starts_at,
      };
      return editingPeriod ? updatePeriod(editingPeriod.id, payload) : createPeriod(payload);
    },
    onSuccess: async () => {
      closeModal();
      await invalidateAdminQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const createAssignmentMutation = useMutation({
    mutationFn: () => {
      const payload = {
        group: Number(assignmentForm.group),
        period: Number(assignmentForm.period),
        subject: Number(assignmentForm.subject),
        teacher: Number(assignmentForm.teacher),
      };
      return editingAssignment ? updateAssignment(editingAssignment.id, payload) : createAssignment(payload);
    },
    onSuccess: async () => {
      closeModal();
      await invalidateAdminQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!deleteTarget) return;
      if (deleteTarget.kind === "assignment") await deleteAssignment(deleteTarget.id);
      if (deleteTarget.kind === "group") await deleteGroup(deleteTarget.id);
      if (deleteTarget.kind === "period") await deletePeriod(deleteTarget.id);
      if (deleteTarget.kind === "subject") await deleteSubject(deleteTarget.id);
    },
    onSuccess: async () => {
      closeModal();
      await invalidateAdminQueries();
    },
    onError: (error) => setFormError(getApiErrorMessage(error)),
  });

  const users = usersQuery.data ?? emptyUsers;
  const groups = groupsQuery.data ?? emptyGroups;
  const subjects = subjectsQuery.data ?? emptySubjects;
  const periods = periodsQuery.data ?? emptyPeriods;
  const students = studentsQuery.data ?? emptyStudents;
  const teachers = teachersQuery.data ?? emptyTeachers;
  const assignments = assignmentsQuery.data ?? emptyAssignments;
  const auditLogs = auditQuery.data ?? emptyAuditLogs;

  const normalizedSearch = search.trim().toLowerCase();
  const filteredUsers = useMemo(
    () =>
      users.filter((user) =>
        `${user.username} ${user.full_name} ${user.email} ${user.role}`.toLowerCase().includes(normalizedSearch),
      ),
    [normalizedSearch, users],
  );
  const filteredGroups = useMemo(() => groups.filter((item) => `${item.name} ${item.enrollment_year}`.toLowerCase().includes(normalizedSearch)), [groups, normalizedSearch]);
  const filteredSubjects = useMemo(() => subjects.filter((item) => `${item.name} ${item.code}`.toLowerCase().includes(normalizedSearch)), [normalizedSearch, subjects]);
  const filteredPeriods = useMemo(() => periods.filter((item) => item.name.toLowerCase().includes(normalizedSearch)), [normalizedSearch, periods]);
  const filteredAssignments = useMemo(
    () =>
      assignments.filter((item) =>
        `${item.teacher_name} ${item.subject_name} ${item.group_name} ${item.period_name}`.toLowerCase().includes(normalizedSearch),
      ),
    [assignments, normalizedSearch],
  );
  const filteredAudit = useMemo(
    () =>
      auditLogs.filter((item) =>
        `${item.action} ${item.object_type} ${item.object_repr} ${item.actor_details?.username ?? ""}`.toLowerCase().includes(normalizedSearch),
      ),
    [auditLogs, normalizedSearch],
  );

  const teacherOptions = teachers.map((teacher) => ({ label: teacher.user_details.full_name || teacher.user_details.username, value: teacher.id.toString() }));
  const groupOptions = groups.map((group) => ({ label: group.name, value: group.id.toString() }));
  const subjectOptions = subjects.map((subject) => ({ label: `${subject.name} (${subject.code})`, value: subject.id.toString() }));
  const periodOptions = periods.map((period) => ({ label: period.name, value: period.id.toString() }));

  const userColumns: Array<DataTableColumn<CurrentUser>> = [
    {
      key: "user",
      header: "Пользователь",
      render: (row) => (
        <div className="table-main-cell">
          <strong>{row.full_name || row.username}</strong>
          <span>{row.username}</span>
        </div>
      ),
    },
    { key: "role", header: "Роль", render: (row) => roleLabels[row.role], width: "160px" },
    { key: "email", header: "Email", render: (row) => row.email || "-", width: "220px" },
    { key: "status", header: "Статус", render: (row) => <StatusBadge tone={row.is_active ? "success" : "warning"}>{row.is_active ? "Активен" : "Отключен"}</StatusBadge>, width: "140px" },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => (
        <div className="table-actions">
          <Button onClick={() => openEditUser(row)} size="sm" variant="ghost">Изменить</Button>
          <Button icon={<KeyRound aria-hidden="true" size={14} />} onClick={() => openResetPassword(row)} size="sm" variant="secondary">Пароль</Button>
        </div>
      ),
      width: "220px",
    },
  ];

  const groupColumns: Array<DataTableColumn<AcademicGroup>> = [
    { key: "name", header: "Группа", render: (row) => row.name },
    { key: "year", header: "Год набора", render: (row) => row.enrollment_year.toString(), width: "150px" },
    { key: "active", header: "Статус", render: (row) => <StatusBadge tone={row.is_active ? "success" : "warning"}>{row.is_active ? "Активна" : "Отключена"}</StatusBadge>, width: "150px" },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => <EducationActions onDelete={() => openDeleteTarget({ id: row.id, kind: "group", label: row.name })} onEdit={() => openEditGroup(row)} />,
      width: "190px",
    },
  ];

  const subjectColumns: Array<DataTableColumn<Subject>> = [
    { key: "name", header: "Дисциплина", render: (row) => <div className="table-main-cell"><strong>{row.name}</strong><span>{row.description || "-"}</span></div> },
    { key: "code", header: "Код", render: (row) => row.code, width: "140px" },
    { key: "active", header: "Статус", render: (row) => <StatusBadge tone={row.is_active ? "success" : "warning"}>{row.is_active ? "Активна" : "Отключена"}</StatusBadge>, width: "150px" },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => <EducationActions onDelete={() => openDeleteTarget({ id: row.id, kind: "subject", label: row.name })} onEdit={() => openEditSubject(row)} />,
      width: "190px",
    },
  ];

  const periodColumns: Array<DataTableColumn<AcademicPeriod>> = [
    { key: "name", header: "Период", render: (row) => row.name },
    { key: "dates", header: "Даты", render: (row) => `${formatDate(row.starts_at)} - ${formatDate(row.ends_at)}` },
    { key: "active", header: "Статус", render: (row) => <StatusBadge tone={row.is_active ? "success" : "warning"}>{row.is_active ? "Активен" : "Отключен"}</StatusBadge>, width: "150px" },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => <EducationActions onDelete={() => openDeleteTarget({ id: row.id, kind: "period", label: row.name })} onEdit={() => openEditPeriod(row)} />,
      width: "190px",
    },
  ];

  const assignmentColumns: Array<DataTableColumn<TeachingAssignmentAdmin>> = [
    { key: "teacher", header: "Преподаватель", render: (row) => row.teacher_name || "-" },
    { key: "subject", header: "Дисциплина", render: (row) => row.subject_name },
    { key: "group", header: "Группа", render: (row) => row.group_name, width: "130px" },
    { key: "period", header: "Период", render: (row) => row.period_name },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => (
        <EducationActions
          onDelete={() => openDeleteTarget({ id: row.id, kind: "assignment", label: `${row.teacher_name} - ${row.subject_name} - ${row.group_name}` })}
          onEdit={() => openEditAssignment(row)}
        />
      ),
      width: "190px",
    },
  ];

  if (dashboardQuery.isLoading) {
    return <LoadingState text="Загружаем кабинет администратора" />;
  }

  if (dashboardQuery.isError || !dashboardQuery.data) {
    return <ErrorState text="Не удалось загрузить административные сводки." />;
  }

  const dashboard = dashboardQuery.data;
  const isSaving =
    createAssignmentMutation.isPending ||
    createGroupMutation.isPending ||
    createPeriodMutation.isPending ||
    createSubjectMutation.isPending ||
    deleteMutation.isPending ||
    resetPasswordMutation.isPending ||
    saveUserMutation.isPending;

  function openCreateUser() {
    setEditingUser(null);
    setUserForm({ ...emptyUserForm(), student_group: groupOptions[0]?.value ?? "" });
    openModal("user");
  }

  function openEditUser(user: CurrentUser) {
    const studentProfile = students.find((profile) => profile.user === user.id);
    const teacherProfile = teachers.find((profile) => profile.user === user.id);
    setEditingUser(user);
    setUserForm({
      access_expires_at: user.access_expires_at ? user.access_expires_at.slice(0, 16) : "",
      email: user.email,
      first_name: user.first_name,
      is_active: user.is_active ? "true" : "false",
      last_name: user.last_name,
      password: "",
      phone: user.phone,
      role: user.role,
      student_enrollment_date: studentProfile?.enrollment_date ?? "",
      student_group: studentProfile?.group.toString() ?? groupOptions[0]?.value ?? "",
      student_id: studentProfile?.student_id.toString() ?? "",
      teacher_personnel_number: teacherProfile?.personnel_number ?? "",
      teacher_position: teacherProfile?.position ?? "",
      username: user.username,
    });
    openModal("user");
  }

  function openResetPassword(user: CurrentUser) {
    setResetUser(user);
    setNewPassword("");
    openModal("reset-password");
  }

  function openCreateGroup() {
    setEditingGroup(null);
    setGroupForm({ enrollment_year: new Date().getFullYear().toString(), is_active: "true", name: "" });
    openModal("group");
  }

  function openEditGroup(group: AcademicGroup) {
    setEditingGroup(group);
    setGroupForm({ enrollment_year: group.enrollment_year.toString(), is_active: group.is_active ? "true" : "false", name: group.name });
    openModal("group");
  }

  function openCreateSubject() {
    setEditingSubject(null);
    setSubjectForm({ code: "", description: "", is_active: "true", name: "" });
    openModal("subject");
  }

  function openEditSubject(subject: Subject) {
    setEditingSubject(subject);
    setSubjectForm({
      code: subject.code,
      description: subject.description,
      is_active: subject.is_active ? "true" : "false",
      name: subject.name,
    });
    openModal("subject");
  }

  function openCreatePeriod() {
    setEditingPeriod(null);
    setPeriodForm({ ends_at: today, is_active: "true", name: "", starts_at: today });
    openModal("period");
  }

  function openEditPeriod(period: AcademicPeriod) {
    setEditingPeriod(period);
    setPeriodForm({
      ends_at: period.ends_at,
      is_active: period.is_active ? "true" : "false",
      name: period.name,
      starts_at: period.starts_at,
    });
    openModal("period");
  }

  function openCreateAssignment() {
    setEditingAssignment(null);
    setAssignmentForm({
      group: groupOptions[0]?.value ?? "",
      period: periodOptions[0]?.value ?? "",
      subject: subjectOptions[0]?.value ?? "",
      teacher: teacherOptions[0]?.value ?? "",
    });
    openModal("assignment");
  }

  function openEditAssignment(assignment: TeachingAssignmentAdmin) {
    setEditingAssignment(assignment);
    setAssignmentForm({
      group: assignment.group.toString(),
      period: assignment.period.toString(),
      subject: assignment.subject.toString(),
      teacher: assignment.teacher.toString(),
    });
    openModal("assignment");
  }

  function openDeleteTarget(target: NonNullable<DeleteTarget>) {
    setFormError(null);
    setDeleteTarget(target);
  }

  function openModal(kind: ModalKind) {
    setFormError(null);
    setModalKind(kind);
  }

  function closeModal() {
    setFormError(null);
    setModalKind(null);
    setEditingUser(null);
    setEditingGroup(null);
    setEditingSubject(null);
    setEditingPeriod(null);
    setEditingAssignment(null);
    setResetUser(null);
    setDeleteTarget(null);
  }

  function handleUserSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (userForm.role === "student" && (!userForm.student_id || !userForm.student_group)) {
      setFormError("Заполните номер студента и группу.");
      return;
    }

    saveUserMutation.mutate({
      access_expires_at: userForm.access_expires_at ? new Date(userForm.access_expires_at).toISOString() : null,
      email: userForm.email,
      first_name: userForm.first_name,
      is_active: userForm.is_active === "true",
      last_name: userForm.last_name,
      password: userForm.password || undefined,
      phone: userForm.phone,
      role: userForm.role,
      username: userForm.username,
    });
  }

  async function syncRoleProfile(userId: number, role: UserRole) {
    if (role === "student") {
      const payload = {
        enrollment_date: userForm.student_enrollment_date || null,
        group: Number(userForm.student_group),
        student_id: Number(userForm.student_id),
        user: userId,
      };
      const existingProfile = students.find((profile) => profile.user === userId);

      if (existingProfile) {
        await updateStudentProfile(existingProfile.id, payload);
      } else {
        await createStudentProfile(payload);
      }
    }

    if (role === "teacher") {
      const freshTeachers = await fetchTeachersAdmin();
      const existingProfile = freshTeachers.find((profile) => profile.user === userId);
      const personnelNumber = userForm.teacher_personnel_number.trim();
      const payload = {
        position: userForm.teacher_position,
        user: userId,
        ...(personnelNumber ? { personnel_number: personnelNumber } : {}),
      };

      if (existingProfile) {
        await updateTeacherProfile(existingProfile.id, payload);
      } else {
        await createTeacherProfile({
          personnel_number: personnelNumber || buildDefaultPersonnelNumber(userId),
          position: userForm.teacher_position,
          user: userId,
        });
      }
    }
  }

  return (
    <section className="content-stack">
      <PageHeader
        badge={<StatusBadge tone="success">Кабинет администратора</StatusBadge>}
        description="Управление пользователями, учебными справочниками, назначениями и аудитом."
        icon={<ShieldCheck aria-hidden="true" size={34} />}
        title="Администрирование системы"
      />

      <div className="metric-grid">
        <SummaryCard label="Пользователей" value={dashboard.users.total.toString()} />
        <SummaryCard label="Групп" value={dashboard.education.groups.total.toString()} />
        <SummaryCard label="Оценок" value={dashboard.journal.grades.toString()} />
      </div>

      <div className="attendance-summary">
        <SummaryCard label="Студентов" value={dashboard.users.by_role.student.toString()} />
        <SummaryCard label="Преподавателей" value={dashboard.users.by_role.teacher.toString()} />
        <SummaryCard label="Дисциплин" value={dashboard.education.subjects.total.toString()} />
        <SummaryCard label="Назначений" value={dashboard.education.teaching_assignments.toString()} />
      </div>

      <section className="panel">
        <SectionToolbar
          actions={
            activeTab === "users" ? (
              <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openCreateUser} size="sm" variant="primary">Пользователь</Button>
            ) : activeTab === "education" ? (
              <>
                <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openCreateGroup} size="sm" variant="primary">Группа</Button>
                <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openCreateSubject} size="sm" variant="primary">Дисциплина</Button>
                <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openCreatePeriod} size="sm" variant="primary">Период</Button>
                <Button icon={<Plus aria-hidden="true" size={16} />} onClick={openCreateAssignment} size="sm" variant="secondary">Назначение</Button>
              </>
            ) : null
          }
          title="Рабочая область"
        >
          <div className="segmented-control" role="tablist">
            <button className={activeTab === "users" ? "is-active" : ""} onClick={() => setActiveTab("users")} type="button">Пользователи</button>
            <button className={activeTab === "education" ? "is-active" : ""} onClick={() => setActiveTab("education")} type="button">Учебный процесс</button>
            <button className={activeTab === "audit" ? "is-active" : ""} onClick={() => setActiveTab("audit")} type="button">Аудит</button>
          </div>
          <TextField icon={<Search aria-hidden="true" size={16} />} label="Поиск" onChange={(event) => setSearch(event.target.value)} placeholder="Поиск по текущей вкладке" value={search} />
        </SectionToolbar>
      </section>

      {activeTab === "users" ? (
        <section className="panel">
          <SectionToolbar title="Пользователи" />
          <DataTable columns={userColumns} data={filteredUsers} emptyText="Пользователей по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={usersQuery.isLoading} />
        </section>
      ) : null}

      {activeTab === "education" ? (
        <>
          <section className="panel">
            <SectionToolbar title="Группы" />
            <DataTable columns={groupColumns} data={filteredGroups} emptyText="Групп по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={groupsQuery.isLoading} />
          </section>
          <section className="panel">
            <SectionToolbar title="Дисциплины" />
            <DataTable columns={subjectColumns} data={filteredSubjects} emptyText="Дисциплин по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={subjectsQuery.isLoading} />
          </section>
          <section className="panel">
            <SectionToolbar title="Учебные периоды" />
            <DataTable columns={periodColumns} data={filteredPeriods} emptyText="Периодов по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={periodsQuery.isLoading} />
          </section>
          <section className="panel">
            <SectionToolbar title="Назначения преподавателей" />
            <DataTable columns={assignmentColumns} data={filteredAssignments} emptyText="Назначений по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={assignmentsQuery.isLoading} />
          </section>
        </>
      ) : null}

      {activeTab === "audit" ? (
        <section className="panel">
          <SectionToolbar title="Журнал аудита" />
          <DataTable columns={auditColumns} data={filteredAudit} emptyText="Записей аудита по выбранным фильтрам нет." getRowKey={(row) => row.id} isLoading={auditQuery.isLoading} />
        </section>
      ) : null}

      <Modal footer={<ModalFooter formId="user-form" isSaving={isSaving} onCancel={closeModal} />} isOpen={modalKind === "user"} onClose={closeModal} title={editingUser ? "Изменить пользователя" : "Новый пользователь"}>
        <form className="form-grid" id="user-form" onSubmit={handleUserSubmit}>
          <div className="form-grid form-grid--two">
            <TextField label="Логин" onChange={(event) => setUserForm((current) => ({ ...current, username: event.target.value }))} required value={userForm.username} />
            <SelectField label="Роль" onChange={(event) => setUserForm((current) => ({ ...current, role: event.target.value as UserRole }))} options={roleOptions} required value={userForm.role} />
          </div>
          <div className="form-grid form-grid--two">
            <TextField label="Имя" onChange={(event) => setUserForm((current) => ({ ...current, first_name: event.target.value }))} value={userForm.first_name} />
            <TextField label="Фамилия" onChange={(event) => setUserForm((current) => ({ ...current, last_name: event.target.value }))} value={userForm.last_name} />
          </div>
          <TextField label="Пароль" minLength={6} onChange={(event) => setUserForm((current) => ({ ...current, password: event.target.value }))} required={!editingUser} type="password" value={userForm.password} />
          <div className="form-grid form-grid--two">
            <TextField label="Телефон" onChange={(event) => setUserForm((current) => ({ ...current, phone: event.target.value }))} placeholder="+7 900-000-00-00" value={userForm.phone} />
            <TextField label="Email" onChange={(event) => setUserForm((current) => ({ ...current, email: event.target.value }))} type="email" value={userForm.email} />
          </div>
          <div className="form-grid form-grid--two">
            <SelectField label="Статус" onChange={(event) => setUserForm((current) => ({ ...current, is_active: event.target.value }))} options={activeOptions} value={userForm.is_active} />
            <TextField label="Доступ до" onChange={(event) => setUserForm((current) => ({ ...current, access_expires_at: event.target.value }))} type="datetime-local" value={userForm.access_expires_at} />
          </div>
          {userForm.role === "student" ? (
            <div className="role-profile-fields">
              <h3>Профиль студента</h3>
              <div className="form-grid form-grid--two">
                <TextField label="Номер студента" min="1" onChange={(event) => setUserForm((current) => ({ ...current, student_id: event.target.value }))} required type="number" value={userForm.student_id} />
                <SelectField label="Группа" onChange={(event) => setUserForm((current) => ({ ...current, student_group: event.target.value }))} options={groupOptions} required value={userForm.student_group} />
              </div>
              <TextField label="Дата зачисления" onChange={(event) => setUserForm((current) => ({ ...current, student_enrollment_date: event.target.value }))} type="date" value={userForm.student_enrollment_date} />
            </div>
          ) : null}
          {userForm.role === "teacher" ? (
            <div className="role-profile-fields">
              <h3>Профиль преподавателя</h3>
              <div className="form-grid form-grid--two">
                <TextField
                  hint="Если оставить пустым, номер будет назначен автоматически."
                  label="Табельный номер"
                  onChange={(event) => setUserForm((current) => ({ ...current, teacher_personnel_number: event.target.value }))}
                  value={userForm.teacher_personnel_number}
                />
                <TextField label="Должность" onChange={(event) => setUserForm((current) => ({ ...current, teacher_position: event.target.value }))} value={userForm.teacher_position} />
              </div>
            </div>
          ) : null}
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal footer={<ModalFooter formId="reset-password-form" isSaving={isSaving} onCancel={closeModal} />} isOpen={modalKind === "reset-password"} onClose={closeModal} title="Сброс пароля">
        <form className="form-grid" id="reset-password-form" onSubmit={(event) => { event.preventDefault(); resetPasswordMutation.mutate(); }}>
          <p className="muted-text">Новый пароль для пользователя {resetUser?.username}</p>
          <TextField label="Новый пароль" minLength={6} onChange={(event) => setNewPassword(event.target.value)} required type="password" value={newPassword} />
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal footer={<ModalFooter formId="group-form" isSaving={isSaving} onCancel={closeModal} />} isOpen={modalKind === "group"} onClose={closeModal} title={editingGroup ? "Изменить группу" : "Новая группа"}>
        <form className="form-grid" id="group-form" onSubmit={(event) => { event.preventDefault(); createGroupMutation.mutate(); }}>
          <TextField label="Название" onChange={(event) => setGroupForm((current) => ({ ...current, name: event.target.value }))} required value={groupForm.name} />
          <TextField label="Год набора" onChange={(event) => setGroupForm((current) => ({ ...current, enrollment_year: event.target.value }))} required type="number" value={groupForm.enrollment_year} />
          <SelectField label="Статус" onChange={(event) => setGroupForm((current) => ({ ...current, is_active: event.target.value }))} options={activeOptions} value={groupForm.is_active} />
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal footer={<ModalFooter formId="subject-form" isSaving={isSaving} onCancel={closeModal} />} isOpen={modalKind === "subject"} onClose={closeModal} title={editingSubject ? "Изменить дисциплину" : "Новая дисциплина"}>
        <form className="form-grid" id="subject-form" onSubmit={(event) => { event.preventDefault(); createSubjectMutation.mutate(); }}>
          <TextField label="Название" onChange={(event) => setSubjectForm((current) => ({ ...current, name: event.target.value }))} required value={subjectForm.name} />
          <TextField label="Код" onChange={(event) => setSubjectForm((current) => ({ ...current, code: event.target.value }))} required value={subjectForm.code} />
          <TextareaField label="Описание" onChange={(event) => setSubjectForm((current) => ({ ...current, description: event.target.value }))} value={subjectForm.description} />
          <SelectField label="Статус" onChange={(event) => setSubjectForm((current) => ({ ...current, is_active: event.target.value }))} options={activeOptions} value={subjectForm.is_active} />
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal footer={<ModalFooter formId="period-form" isSaving={isSaving} onCancel={closeModal} />} isOpen={modalKind === "period"} onClose={closeModal} title={editingPeriod ? "Изменить учебный период" : "Новый учебный период"}>
        <form className="form-grid" id="period-form" onSubmit={(event) => { event.preventDefault(); createPeriodMutation.mutate(); }}>
          <TextField label="Название" onChange={(event) => setPeriodForm((current) => ({ ...current, name: event.target.value }))} required value={periodForm.name} />
          <div className="form-grid form-grid--two">
            <TextField label="Дата начала" onChange={(event) => setPeriodForm((current) => ({ ...current, starts_at: event.target.value }))} required type="date" value={periodForm.starts_at} />
            <TextField label="Дата окончания" onChange={(event) => setPeriodForm((current) => ({ ...current, ends_at: event.target.value }))} required type="date" value={periodForm.ends_at} />
          </div>
          <SelectField label="Статус" onChange={(event) => setPeriodForm((current) => ({ ...current, is_active: event.target.value }))} options={activeOptions} value={periodForm.is_active} />
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal footer={<ModalFooter formId="assignment-form" isSaving={isSaving} onCancel={closeModal} />} isOpen={modalKind === "assignment"} onClose={closeModal} title={editingAssignment ? "Изменить назначение" : "Новое назначение"}>
        <form className="form-grid" id="assignment-form" onSubmit={(event) => { event.preventDefault(); createAssignmentMutation.mutate(); }}>
          <SelectField label="Преподаватель" onChange={(event) => setAssignmentForm((current) => ({ ...current, teacher: event.target.value }))} options={teacherOptions} required value={assignmentForm.teacher} />
          <SelectField label="Дисциплина" onChange={(event) => setAssignmentForm((current) => ({ ...current, subject: event.target.value }))} options={subjectOptions} required value={assignmentForm.subject} />
          <SelectField label="Группа" onChange={(event) => setAssignmentForm((current) => ({ ...current, group: event.target.value }))} options={groupOptions} required value={assignmentForm.group} />
          <SelectField label="Период" onChange={(event) => setAssignmentForm((current) => ({ ...current, period: event.target.value }))} options={periodOptions} required value={assignmentForm.period} />
          <FormError text={formError} />
        </form>
      </Modal>

      <Modal
        footer={
          <>
            <Button disabled={isSaving} onClick={closeModal} variant="ghost">Отмена</Button>
            <Button disabled={isSaving} icon={<Trash2 aria-hidden="true" size={16} />} onClick={() => deleteMutation.mutate()} variant="danger">
              {isSaving ? "Удаляем" : "Удалить"}
            </Button>
          </>
        }
        isOpen={deleteTarget !== null}
        onClose={closeModal}
        title="Удалить запись"
      >
        <div className="confirm-delete">
          <p>Удалить запись «{deleteTarget?.label}»?</p>
          <div className="confirm-delete__warning">Если запись уже используется в журнале или профилях, сервер может запретить удаление. В этом случае лучше отключить ее через статус.</div>
          <FormError text={formError} />
        </div>
      </Modal>
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

function ModalFooter({ formId, isSaving, onCancel }: { formId: string; isSaving: boolean; onCancel: () => void }) {
  return (
    <>
      <Button disabled={isSaving} onClick={onCancel} variant="ghost">Отмена</Button>
      <Button disabled={isSaving} form={formId} type="submit" variant="primary">{isSaving ? "Сохраняем" : "Сохранить"}</Button>
    </>
  );
}

function EducationActions({ onDelete, onEdit }: { onDelete: () => void; onEdit: () => void }) {
  return (
    <div className="table-actions">
      <Button onClick={onEdit} size="sm" variant="ghost">Изменить</Button>
      <Button icon={<Trash2 aria-hidden="true" size={14} />} onClick={onDelete} size="sm" variant="danger">Удалить</Button>
    </div>
  );
}

function FormError({ text }: { text: string | null }) {
  return text ? <div className="form-error">{text}</div> : null;
}

function emptyUserForm(): UserForm {
  return {
    access_expires_at: "",
    email: "",
    first_name: "",
    is_active: "true",
    last_name: "",
    password: "",
    phone: "",
    role: "student",
    student_enrollment_date: "",
    student_group: "",
    student_id: "",
    teacher_personnel_number: "",
    teacher_position: "",
    username: "",
  };
}

function buildDefaultPersonnelNumber(userId: number): string {
  return `T-${userId.toString().padStart(6, "0")}`;
}

function stripEmptyPassword(payload: UserPayload): Partial<UserPayload> {
  if (payload.password) {
    return payload;
  }
  const payloadWithoutPassword: Partial<UserPayload> = { ...payload };
  delete payloadWithoutPassword.password;
  return payloadWithoutPassword;
}

const auditColumns: Array<DataTableColumn<AuditLog>> = [
  { key: "date", header: "Дата", render: (row) => formatDateTime(row.created_at), width: "180px" },
  { key: "actor", header: "Пользователь", render: (row) => row.actor_details?.username ?? "-", width: "160px" },
  { key: "action", header: "Действие", render: (row) => row.action, width: "190px" },
  { key: "object", header: "Объект", render: (row) => <div className="table-main-cell"><strong>{row.object_type || "-"}</strong><span>{row.object_repr || row.object_id || "-"}</span></div> },
  { key: "request", header: "Request ID", render: (row) => row.request_id || "-", width: "220px" },
];

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU").format(new Date(value));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(new Date(value));
}

function getApiErrorMessage(error: unknown): string {
  if (error instanceof AxiosError && error.response?.data) {
    return flattenError(error.response.data);
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Не удалось сохранить данные. Проверьте поля формы.";
}

function flattenError(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(flattenError).join(" ");
  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => `${key}: ${flattenError(item)}`)
      .join(" ");
  }
  return "Ошибка сохранения.";
}
