import { apiClient } from "./client";

export type NotificationType = "session_closing";

export type NotificationRecipient = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  email: string;
  role: "admin" | "student" | "teacher";
  access_expires_at: string | null;
  is_active: boolean;
  last_login: string | null;
  date_joined: string;
};

export type AppNotification = {
  id: number;
  recipient: number;
  recipient_details: NotificationRecipient;
  notification_type: NotificationType;
  title: string;
  message: string;
  period: number | null;
  period_name: string | null;
  is_read: boolean;
  created_at: string;
  read_at: string | null;
};

export async function fetchNotifications(): Promise<AppNotification[]> {
  const response = await apiClient.get<AppNotification[]>("/api/notifications/notifications/");
  return response.data;
}

export async function markNotificationRead(id: number): Promise<AppNotification> {
  const response = await apiClient.post<AppNotification>(`/api/notifications/notifications/${id}/mark-read/`);
  return response.data;
}
