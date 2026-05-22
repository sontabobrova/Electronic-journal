import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import type { UserRole } from "../api/auth";
import { useAuth } from "./authContext";

type ProtectedRouteProps = {
  children: ReactNode;
  roles?: UserRole[];
};

export function ProtectedRoute({ children, roles }: ProtectedRouteProps) {
  const location = useLocation();
  const { user, token, isLoading } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (isLoading) {
    return <FullScreenState title="Загружаем профиль" text="Проверяем авторизацию и права доступа." />;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (roles && !roles.includes(user.role)) {
    return <FullScreenState title="Нет доступа" text="Этот раздел не доступен для вашей роли." />;
  }

  return children;
}

function FullScreenState({ title, text }: { title: string; text: string }) {
  return (
    <div className="full-screen-state">
      <div className="full-screen-state__panel">
        <h1>{title}</h1>
        <p>{text}</p>
      </div>
    </div>
  );
}
