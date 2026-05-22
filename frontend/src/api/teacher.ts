import type { AttendanceStatus } from "./student";
import { apiClient } from "./client";

export type TeacherProfile = {
  id: number;
  full_name: string;
  username: string;
  email: string;
  personnel_number: string;
  position: string;
};

export type TeacherDashboard = {
  profile: TeacherProfile;
  assignments_total: number;
  groups_total: number;
  students_total: number;
  grade_works_total: number;
  grades_total: number;
  class_sessions_total: number;
  attendance_total: number;
  attendance_by_status: Record<AttendanceStatus, number>;
};

export type TeacherAssignment = {
  id: number;
  subject: number;
  subject_name: string;
  subject_code: string;
  group: number;
  group_name: string;
  period: number;
  period_name: string;
};

export type TeacherStudent = {
  id: number;
  student_id: number;
  full_name: string;
  username: string;
  group: number;
  group_name: string;
  enrollment_date: string | null;
};

export type TeacherGradeWork = {
  id: number;
  assignment_id: number;
  subject_name: string;
  group_name: string;
  period_name: string;
  title: string;
  work_type: string;
  work_date: string;
  max_score: string;
  weight: string;
  updated_at: string;
};

export type TeacherGrade = {
  id: number;
  student: number;
  student_id_number: number;
  student_name: string;
  work: number;
  work_title: string;
  work_date: string;
  subject_name: string;
  group_name: string;
  value: string;
  comment: string;
  updated_at: string;
};

export type TeacherClassSession = {
  id: number;
  assignment_id: number;
  subject_name: string;
  group_name: string;
  period_name: string;
  session_date: string;
  topic: string;
  updated_at: string;
};

export type TeacherAttendance = {
  id: number;
  student: number;
  student_id_number: number;
  student_name: string;
  session: number;
  session_topic: string;
  session_date: string;
  subject_name: string;
  group_name: string;
  status: AttendanceStatus;
  comment: string;
  updated_at: string;
};

export type GradeWorkPayload = {
  assignment: number;
  title: string;
  work_type: string;
  work_date: string;
  max_score: string;
  weight: string;
};

export type GradePayload = {
  work: number;
  student: number;
  value: string;
  comment: string;
};

export type ClassSessionPayload = {
  assignment: number;
  session_date: string;
  topic: string;
};

export type AttendancePayload = {
  session: number;
  student: number;
  status: AttendanceStatus;
  comment: string;
};

export async function fetchTeacherDashboard(): Promise<TeacherDashboard> {
  const response = await apiClient.get<TeacherDashboard>("/api/journal/teacher/dashboard/");
  return response.data;
}

export async function fetchTeacherAssignments(): Promise<TeacherAssignment[]> {
  const response = await apiClient.get<TeacherAssignment[]>("/api/journal/teacher/assignments/");
  return response.data;
}

export async function fetchTeacherStudents(): Promise<TeacherStudent[]> {
  const response = await apiClient.get<TeacherStudent[]>("/api/journal/teacher/students/");
  return response.data;
}

export async function fetchTeacherGradeWorks(): Promise<TeacherGradeWork[]> {
  const response = await apiClient.get<TeacherGradeWork[]>("/api/journal/teacher/grade-works/");
  return response.data;
}

export async function fetchTeacherGrades(): Promise<TeacherGrade[]> {
  const response = await apiClient.get<TeacherGrade[]>("/api/journal/teacher/grades/");
  return response.data;
}

export async function fetchTeacherClassSessions(): Promise<TeacherClassSession[]> {
  const response = await apiClient.get<TeacherClassSession[]>("/api/journal/teacher/class-sessions/");
  return response.data;
}

export async function fetchTeacherAttendance(): Promise<TeacherAttendance[]> {
  const response = await apiClient.get<TeacherAttendance[]>("/api/journal/teacher/attendance/");
  return response.data;
}

export async function createGradeWork(payload: GradeWorkPayload): Promise<TeacherGradeWork> {
  const response = await apiClient.post<TeacherGradeWork>("/api/journal/grade-works/", payload);
  return response.data;
}

export async function createGrade(payload: GradePayload): Promise<TeacherGrade> {
  const response = await apiClient.post<TeacherGrade>("/api/journal/grades/", payload);
  return response.data;
}

export async function updateGrade(id: number, payload: Pick<GradePayload, "comment" | "value">): Promise<TeacherGrade> {
  const response = await apiClient.patch<TeacherGrade>(`/api/journal/grades/${id}/`, payload);
  return response.data;
}

export async function createClassSession(payload: ClassSessionPayload): Promise<TeacherClassSession> {
  const response = await apiClient.post<TeacherClassSession>("/api/journal/class-sessions/", payload);
  return response.data;
}

export async function createAttendance(payload: AttendancePayload): Promise<TeacherAttendance> {
  const response = await apiClient.post<TeacherAttendance>("/api/journal/attendance-records/", payload);
  return response.data;
}

export async function updateAttendance(id: number, payload: Pick<AttendancePayload, "comment" | "status">): Promise<TeacherAttendance> {
  const response = await apiClient.patch<TeacherAttendance>(`/api/journal/attendance-records/${id}/`, payload);
  return response.data;
}

export async function deleteGradeWork(id: number): Promise<void> {
  await apiClient.delete(`/api/journal/grade-works/${id}/`);
}

export async function deleteGrade(id: number): Promise<void> {
  await apiClient.delete(`/api/journal/grades/${id}/`);
}

export async function deleteClassSession(id: number): Promise<void> {
  await apiClient.delete(`/api/journal/class-sessions/${id}/`);
}

export async function deleteAttendance(id: number): Promise<void> {
  await apiClient.delete(`/api/journal/attendance-records/${id}/`);
}
