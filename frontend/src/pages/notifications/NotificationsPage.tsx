import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCheck, Clock, MailOpen, Search } from "lucide-react";

import { fetchNotifications, markNotificationRead } from "../../api/notifications";
import type { AppNotification } from "../../api/notifications";
import { useAuth } from "../../auth/authContext";
import { StatusBadge } from "../../components/StatusBadge";
import { Button, EmptyState, ErrorState, LoadingState, PageHeader, SectionToolbar, TextField } from "../../components/ui";

type NotificationFilter = "all" | "read" | "unread";

const emptyNotifications: AppNotification[] = [];
const notificationTypeLabels: Record<string, string> = {
  session_closing: "Закрытие успеваемости",
};

export function NotificationsPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [activeFilter, setActiveFilter] = useState<NotificationFilter>("all");
  const [search, setSearch] = useState("");

  const notificationsQuery = useQuery({ queryKey: ["notifications"], queryFn: fetchNotifications });
  const notifications = notificationsQuery.data ?? emptyNotifications;
  const ownUnreadNotifications = notifications.filter((notification) => isOwnNotification(notification, user?.id) && !notification.is_read);
  const readNotifications = notifications.filter((notification) => notification.is_read);

  const markReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: async () => {
      await Promise.all(ownUnreadNotifications.map((notification) => markNotificationRead(notification.id)));
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const normalizedSearch = search.trim().toLowerCase();
  const visibleNotifications = useMemo(
    () =>
      notifications.filter((notification) => {
        const matchesFilter =
          activeFilter === "all" ||
          (activeFilter === "unread" && !notification.is_read) ||
          (activeFilter === "read" && notification.is_read);
        const matchesSearch = `${notification.title} ${notification.message} ${notification.period_name ?? ""} ${notificationTypeLabels[notification.notification_type]}`
          .toLowerCase()
          .includes(normalizedSearch);
        return matchesFilter && matchesSearch;
      }),
    [activeFilter, normalizedSearch, notifications],
  );

  if (notificationsQuery.isLoading) {
    return <LoadingState text="Загружаем уведомления" />;
  }

  if (notificationsQuery.isError) {
    return <ErrorState text="Не удалось загрузить уведомления." />;
  }

  return (
    <section className="content-stack">
      <PageHeader
        actions={
          <Button
            disabled={!ownUnreadNotifications.length || markAllReadMutation.isPending}
            icon={<CheckCheck aria-hidden="true" size={16} />}
            onClick={() => markAllReadMutation.mutate()}
            variant="secondary"
          >
            Все прочитано
          </Button>
        }
        badge={<StatusBadge tone={ownUnreadNotifications.length ? "warning" : "success"}>{ownUnreadNotifications.length ? "Есть новые" : "Все прочитано"}</StatusBadge>}
        description="Системные напоминания и рабочие события электронного журнала."
        icon={<Bell aria-hidden="true" size={34} />}
        title="Уведомления"
      />

      <div className="attendance-summary">
        <SummaryCard label="Всего" value={notifications.length.toString()} />
        <SummaryCard label="Мои новые" value={ownUnreadNotifications.length.toString()} />
        <SummaryCard label="Прочитано" value={readNotifications.length.toString()} />
        <SummaryCard label="Напоминания" value={notifications.filter((item) => item.notification_type === "session_closing").length.toString()} />
      </div>

      <section className="panel">
        <SectionToolbar title="Лента">
          <div className="segmented-control" role="tablist">
            <button className={activeFilter === "all" ? "is-active" : ""} onClick={() => setActiveFilter("all")} type="button">
              Все
            </button>
            <button className={activeFilter === "unread" ? "is-active" : ""} onClick={() => setActiveFilter("unread")} type="button">
              Непрочитанные
            </button>
            <button className={activeFilter === "read" ? "is-active" : ""} onClick={() => setActiveFilter("read")} type="button">
              Прочитанные
            </button>
          </div>
          <TextField icon={<Search aria-hidden="true" size={16} />} label="Поиск" onChange={(event) => setSearch(event.target.value)} placeholder="Заголовок, текст или период" value={search} />
        </SectionToolbar>

        {visibleNotifications.length ? (
          <div className="notification-list">
            {visibleNotifications.map((notification) => (
              <article className={`notification-item ${notification.is_read ? "" : "is-unread"}`} key={notification.id}>
                <div className="notification-item__icon">
                  {notification.is_read ? <MailOpen aria-hidden="true" size={20} /> : <Bell aria-hidden="true" size={20} />}
                </div>
                <div className="notification-item__content">
                  <div className="notification-item__header">
                    <div>
                      <strong>{notification.title}</strong>
                      <span>{notificationTypeLabels[notification.notification_type] ?? notification.notification_type}</span>
                      {user?.role === "admin" ? <span>Получатель: {notification.recipient_details.full_name || notification.recipient_details.username}</span> : null}
                    </div>
                    <StatusBadge tone={notification.is_read ? "neutral" : "warning"}>{notification.is_read ? "Прочитано" : "Новое"}</StatusBadge>
                  </div>
                  <p>{notification.message}</p>
                  <div className="notification-meta">
                    <span><Clock aria-hidden="true" size={14} /> {formatDateTime(notification.created_at)}</span>
                    {notification.period_name ? <span>{notification.period_name}</span> : null}
                    {notification.read_at ? <span>Прочитано: {formatDateTime(notification.read_at)}</span> : null}
                    {!isOwnNotification(notification, user?.id) ? <span>Чужое уведомление</span> : null}
                  </div>
                </div>
                <div className="notification-item__actions">
                  <Button
                    disabled={notification.is_read || markReadMutation.isPending || !isOwnNotification(notification, user?.id)}
                    icon={<CheckCheck aria-hidden="true" size={14} />}
                    onClick={() => markReadMutation.mutate(notification.id)}
                    size="sm"
                    variant={notification.is_read ? "ghost" : "primary"}
                  >
                    Прочитано
                  </Button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState text="Уведомлений по выбранному фильтру нет." title="Лента пуста" />
        )}
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

function isOwnNotification(notification: AppNotification, userId?: number) {
  return Boolean(userId && notification.recipient_details.id === userId);
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
