import {
  Bell,
  BookOpenCheck,
  ClipboardList,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  ShieldCheck,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { NavLink, Outlet } from "react-router-dom";

import { fetchNotifications } from "../api/notifications";
import type { UserRole } from "../api/auth";
import { useAuth } from "../auth/authContext";

const navItems: Array<{
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
  roles?: UserRole[];
}> = [
  { to: "/", label: "Обзор", icon: LayoutDashboard },
  { to: "/student", label: "Студент", icon: GraduationCap, roles: ["student"] },
  { to: "/teacher", label: "Преподаватель", icon: BookOpenCheck, roles: ["teacher"] },
  { to: "/admin", label: "Администратор", icon: ShieldCheck, roles: ["admin"] },
  { to: "/reports", label: "Отчеты", icon: ClipboardList, roles: ["admin", "teacher"] },
  { to: "/notifications", label: "Уведомления", icon: Bell, roles: ["admin", "teacher"] },
];

const roleLabels: Record<UserRole, string> = {
  admin: "Администратор",
  teacher: "Преподаватель",
  student: "Студент",
};

export function AppLayout() {
  const { user, logout } = useAuth();
  const notificationsQuery = useQuery({
    queryKey: ["notifications"],
    queryFn: fetchNotifications,
    enabled: Boolean(user && user.role !== "student"),
  });
  const visibleNavItems = navItems.filter((item) => !item.roles || (user && item.roles.includes(user.role)));
  const displayName = user?.full_name || user?.username || "Пользователь";
  const unreadCount = (notificationsQuery.data ?? []).filter((notification) => !notification.is_read && notification.recipient_details.id === user?.id).length;

  return (
    <div className="app-frame">
      <header className="app-header">
        <div className="user-card" aria-label="Текущий пользователь">
          <div className="user-card__text">
            <strong>{displayName}</strong>
            <span>{user ? roleLabels[user.role] : "Загрузка"}</span>
          </div>
        </div>

        <nav className="top-nav" aria-label="Основная навигация">
          {visibleNavItems.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink key={item.to} to={item.to} end={item.to === "/"} className="top-nav__link">
                <Icon aria-hidden="true" size={17} />
                <span>{item.label}</span>
                {item.to === "/notifications" && unreadCount ? <span className="top-nav__badge">{unreadCount}</span> : null}
              </NavLink>
            );
          })}
        </nav>

        <button className="icon-button" type="button" onClick={() => void logout()} aria-label="Выйти">
          <LogOut aria-hidden="true" size={19} />
        </button>
      </header>

      <main className="workspace">
        <Outlet />
      </main>
    </div>
  );
}
