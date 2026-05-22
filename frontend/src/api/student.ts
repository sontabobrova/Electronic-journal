import { apiClient } from "./client";

export type StudentProfile = {
  id: number;
  student_id: number;
  full_name: string;
  username: string;
  email: string;
  group: number;
  group_name: string;
  enrollment_date: string | null;
};

export type StudentDashboard = {
  profile: StudentProfile;
  grades: {
    total: number;
    average: string | null;
  };
  attendance: {
    total: number;
    by_status: Record<AttendanceStatus, number>;
  };
};

export type StudentGrade = {
  id: number;
  value: string;
  comment: string;
  work_title: string;
  work_type: string;
  work_date: string;
  max_score: string;
  subject_name: string;
  period_name: string;
  teacher_name: string;
  updated_at: string;
};

export type AttendanceStatus = "present" | "absent" | "excused" | "late";

export type StudentAttendance = {
  id: number;
  status: AttendanceStatus;
  comment: string;
  session_topic: string;
  session_date: string;
  subject_name: string;
  period_name: string;
  teacher_name: string;
  updated_at: string;
};

export async function fetchStudentDashboard(): Promise<StudentDashboard> {
  const response = await apiClient.get<StudentDashboard>("/api/journal/student/dashboard/");
  return response.data;
}

export async function fetchStudentGrades(): Promise<StudentGrade[]> {
  const response = await apiClient.get<StudentGrade[]>("/api/journal/student/grades/");
  return response.data;
}

export async function fetchStudentAttendance(): Promise<StudentAttendance[]> {
  const response = await apiClient.get<StudentAttendance[]>("/api/journal/student/attendance/");
  return response.data;
}
