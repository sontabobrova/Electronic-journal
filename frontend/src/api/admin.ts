import type { CurrentUser, UserRole } from "./auth";
import { apiClient } from "./client";

export type AdminDashboard = {
  users: {
    total: number;
    active: number;
    inactive: number;
    locked: number;
    expired_access: number;
    by_role: Record<UserRole, number>;
    profiles: {
      students: number;
      teachers: number;
    };
  };
  education: EducationSummary;
  journal: {
    grade_works: number;
    grades: number;
    class_sessions: number;
    attendance_records: number;
    attendance_by_status: Record<string, number>;
  };
  recent_users: CurrentUser[];
};

export type EducationSummary = {
  groups: { total: number; active: number };
  subjects: { total: number; active: number };
  periods: { total: number; active: number };
  teaching_assignments: number;
};

export type UserPayload = {
  access_expires_at: string | null;
  email: string;
  first_name: string;
  is_active: boolean;
  last_name: string;
  password?: string;
  phone: string;
  role: UserRole;
  username: string;
};

export type StudentProfilePayload = {
  enrollment_date: string | null;
  group: number;
  student_id: number;
  user: number;
};

export type TeacherProfilePayload = {
  personnel_number?: string;
  position: string;
  user: number;
};

export type AcademicGroup = {
  id: number;
  name: string;
  enrollment_year: number;
  is_active: boolean;
};

export type Subject = {
  id: number;
  name: string;
  code: string;
  description: string;
  is_active: boolean;
};

export type AcademicPeriod = {
  id: number;
  name: string;
  starts_at: string;
  ends_at: string;
  is_active: boolean;
};

export type TeacherProfileAdmin = {
  id: number;
  user: number;
  user_details: CurrentUser;
  personnel_number: string;
  position: string;
};

export type StudentProfileAdmin = {
  id: number;
  user: number;
  user_details: CurrentUser;
  student_id: number;
  group: number;
  group_name: string;
  enrollment_date: string | null;
};

export type TeachingAssignmentAdmin = {
  id: number;
  teacher: number;
  teacher_name: string;
  subject: number;
  subject_name: string;
  group: number;
  group_name: string;
  period: number;
  period_name: string;
};

export type AuditLog = {
  id: number;
  actor: number | null;
  actor_details: CurrentUser | null;
  action: string;
  object_type: string;
  object_id: string;
  object_repr: string;
  ip_address: string | null;
  user_agent: string;
  request_id: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export async function fetchAdminDashboard(): Promise<AdminDashboard> {
  const response = await apiClient.get<AdminDashboard>("/api/admin-cabinet/dashboard/");
  return response.data;
}

export async function fetchUsers(): Promise<CurrentUser[]> {
  const response = await apiClient.get<CurrentUser[]>("/api/users/");
  return response.data;
}

export async function createUser(payload: UserPayload): Promise<CurrentUser> {
  const response = await apiClient.post<CurrentUser>("/api/users/", payload);
  return response.data;
}

export async function updateUser(id: number, payload: Partial<UserPayload>): Promise<CurrentUser> {
  const response = await apiClient.patch<CurrentUser>(`/api/users/${id}/`, payload);
  return response.data;
}

export async function resetUserPassword(id: number, password: string): Promise<CurrentUser> {
  const response = await apiClient.post<CurrentUser>(`/api/users/${id}/reset-password/`, { password });
  return response.data;
}

export async function fetchGroups(): Promise<AcademicGroup[]> {
  const response = await apiClient.get<AcademicGroup[]>("/api/education/groups/");
  return response.data;
}

export async function createGroup(payload: Omit<AcademicGroup, "id">): Promise<AcademicGroup> {
  const response = await apiClient.post<AcademicGroup>("/api/education/groups/", payload);
  return response.data;
}

export async function updateGroup(id: number, payload: Omit<AcademicGroup, "id">): Promise<AcademicGroup> {
  const response = await apiClient.patch<AcademicGroup>(`/api/education/groups/${id}/`, payload);
  return response.data;
}

export async function deleteGroup(id: number): Promise<void> {
  await apiClient.delete(`/api/education/groups/${id}/`);
}

export async function fetchSubjects(): Promise<Subject[]> {
  const response = await apiClient.get<Subject[]>("/api/education/subjects/");
  return response.data;
}

export async function createSubject(payload: Omit<Subject, "id">): Promise<Subject> {
  const response = await apiClient.post<Subject>("/api/education/subjects/", payload);
  return response.data;
}

export async function updateSubject(id: number, payload: Omit<Subject, "id">): Promise<Subject> {
  const response = await apiClient.patch<Subject>(`/api/education/subjects/${id}/`, payload);
  return response.data;
}

export async function deleteSubject(id: number): Promise<void> {
  await apiClient.delete(`/api/education/subjects/${id}/`);
}

export async function fetchPeriods(): Promise<AcademicPeriod[]> {
  const response = await apiClient.get<AcademicPeriod[]>("/api/education/periods/");
  return response.data;
}

export async function createPeriod(payload: Omit<AcademicPeriod, "id">): Promise<AcademicPeriod> {
  const response = await apiClient.post<AcademicPeriod>("/api/education/periods/", payload);
  return response.data;
}

export async function updatePeriod(id: number, payload: Omit<AcademicPeriod, "id">): Promise<AcademicPeriod> {
  const response = await apiClient.patch<AcademicPeriod>(`/api/education/periods/${id}/`, payload);
  return response.data;
}

export async function deletePeriod(id: number): Promise<void> {
  await apiClient.delete(`/api/education/periods/${id}/`);
}

export async function fetchStudentsAdmin(): Promise<StudentProfileAdmin[]> {
  const response = await apiClient.get<StudentProfileAdmin[]>("/api/education/students/");
  return response.data;
}

export async function createStudentProfile(payload: StudentProfilePayload): Promise<StudentProfileAdmin> {
  const response = await apiClient.post<StudentProfileAdmin>("/api/education/students/", payload);
  return response.data;
}

export async function updateStudentProfile(id: number, payload: Partial<StudentProfilePayload>): Promise<StudentProfileAdmin> {
  const response = await apiClient.patch<StudentProfileAdmin>(`/api/education/students/${id}/`, payload);
  return response.data;
}

export async function fetchTeachersAdmin(): Promise<TeacherProfileAdmin[]> {
  const response = await apiClient.get<TeacherProfileAdmin[]>("/api/education/teachers/");
  return response.data;
}

export async function createTeacherProfile(payload: Required<TeacherProfilePayload>): Promise<TeacherProfileAdmin> {
  const response = await apiClient.post<TeacherProfileAdmin>("/api/education/teachers/", payload);
  return response.data;
}

export async function updateTeacherProfile(id: number, payload: Partial<TeacherProfilePayload>): Promise<TeacherProfileAdmin> {
  const response = await apiClient.patch<TeacherProfileAdmin>(`/api/education/teachers/${id}/`, payload);
  return response.data;
}

export async function fetchAssignmentsAdmin(): Promise<TeachingAssignmentAdmin[]> {
  const response = await apiClient.get<TeachingAssignmentAdmin[]>("/api/education/teaching-assignments/");
  return response.data;
}

export async function createAssignment(payload: Pick<TeachingAssignmentAdmin, "group" | "period" | "subject" | "teacher">): Promise<TeachingAssignmentAdmin> {
  const response = await apiClient.post<TeachingAssignmentAdmin>("/api/education/teaching-assignments/", payload);
  return response.data;
}

export async function updateAssignment(id: number, payload: Pick<TeachingAssignmentAdmin, "group" | "period" | "subject" | "teacher">): Promise<TeachingAssignmentAdmin> {
  const response = await apiClient.patch<TeachingAssignmentAdmin>(`/api/education/teaching-assignments/${id}/`, payload);
  return response.data;
}

export async function deleteAssignment(id: number): Promise<void> {
  await apiClient.delete(`/api/education/teaching-assignments/${id}/`);
}

export async function fetchAuditLogs(): Promise<AuditLog[]> {
  const response = await apiClient.get<AuditLog[]>("/api/audit/logs/");
  return response.data;
}
