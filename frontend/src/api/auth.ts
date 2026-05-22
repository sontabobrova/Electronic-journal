import { apiClient } from "./client";

export type UserRole = "student" | "teacher" | "admin";

export type CurrentUser = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  email: string;
  role: UserRole;
  access_expires_at: string | null;
  is_active: boolean;
  last_login: string | null;
  date_joined: string;
  permissions: {
    is_student: boolean;
    is_teacher: boolean;
    is_admin: boolean;
    has_active_access: boolean;
    is_locked: boolean;
  };
};

export type LoginPayload = {
  username: string;
  password: string;
};

export type LoginResponse = {
  token: string;
  user: CurrentUser;
};

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>("/api/auth/login/", payload);
  return response.data;
}

export async function logout(): Promise<void> {
  await apiClient.post("/api/auth/logout/");
}

export async function fetchCurrentUser(): Promise<CurrentUser> {
  const response = await apiClient.get<CurrentUser>("/api/auth/me/");
  return response.data;
}
