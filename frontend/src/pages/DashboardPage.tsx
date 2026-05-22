import { Bell, BookOpenCheck, ClipboardList, GraduationCap, LayoutDashboard, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

import { useAuth } from "../auth/authContext";
import { StatusBadge } from "../components/StatusBadge";
import { PageHeader } from "../components/ui";

type DashboardLink = {
  description: string;
  icon: typeof LayoutDashboard;
  label: string;
  roles?: Array<"admin" | "student" | "teacher">;
  to: string;
};

const roleLabels = {
  admin: "Администратор",
  student: "Студент",
  teacher: "Преподаватель",
};

const dashboardLinks: DashboardLink[] = [
  {
    description: "Оценки, посещаемость и личная учебная сводка.",
    icon: GraduationCap,
    label: "Кабинет студента",
    roles: ["student"],
    to: "/student",
  },
  {
    description: "Группы, работы журнала, оценки и посещаемость.",
    icon: BookOpenCheck,
    label: "Кабинет преподавателя",
    roles: ["teacher"],
    to: "/teacher",
  },
  {
    description: "Пользователи, справочники, назначения и аудит.",
    icon: ShieldCheck,
    label: "Администрирование",
    roles: ["admin"],
    to: "/admin",
  },
  {
    description: "Выгрузки по успеваемости и посещаемости.",
    icon: ClipboardList,
    label: "Отчеты",
    roles: ["admin", "teacher"],
    to: "/reports",
  },
  {
    description: "Рабочие напоминания и системные сообщения.",
    icon: Bell,
    label: "Уведомления",
    roles: ["admin", "teacher"],
    to: "/notifications",
  },
];

export function DashboardPage() {
  const { user } = useAuth();
  const visibleLinks = dashboardLinks.filter((item) => !item.roles || (user && item.roles.includes(user.role)));
  const displayName = user?.full_name || user?.username || "Пользователь";

  return (
    <section className="content-stack">
      <PageHeader
        badge={<StatusBadge tone="success">Рабочая область</StatusBadge>}
        description="Выберите раздел, с которого хотите начать работу."
        icon={<LayoutDashboard aria-hidden="true" size={34} />}
        title={`Добро пожаловать, ${displayName}`}
      />

      <div className="metric-grid">
        <article className="metric">
          <span>Пользователь</span>
          <strong>{displayName}</strong>
        </article>
        <article className="metric">
          <span>Роль</span>
          <strong>{user ? roleLabels[user.role] : "-"}</strong>
        </article>
        <article className="metric">
          <span>Доступ</span>
          <strong>{user?.permissions.has_active_access ? "Активен" : "Ограничен"}</strong>
        </article>
      </div>

      <section className="panel">
        <div className="section-toolbar">
          <h2>Доступные разделы</h2>
        </div>

        <div className="quick-link-grid">
          {visibleLinks.map((item) => {
            const Icon = item.icon;

            return (
              <Link className="quick-link" key={item.to} to={item.to}>
                <span className="quick-link__icon">
                  <Icon aria-hidden="true" size={21} />
                </span>
                <span>
                  <strong>{item.label}</strong>
                  <small>{item.description}</small>
                </span>
              </Link>
            );
          })}
        </div>
      </section>
    </section>
  );
}
