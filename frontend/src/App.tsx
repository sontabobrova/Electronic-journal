import { createBrowserRouter, RouterProvider } from "react-router-dom";

import { ProtectedRoute } from "./auth/ProtectedRoute";
import { AppLayout } from "./layouts/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { AdminCabinetPage } from "./pages/admin/AdminCabinetPage";
import { NotificationsPage } from "./pages/notifications/NotificationsPage";
import { ReportsPage } from "./pages/reports/ReportsPage";
import { StudentCabinetPage } from "./pages/student/StudentCabinetPage";
import { TeacherCabinetPage } from "./pages/teacher/TeacherCabinetPage";

const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <DashboardPage /> },
      {
        path: "student",
        element: (
          <ProtectedRoute roles={["student"]}>
            <StudentCabinetPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "teacher",
        element: (
          <ProtectedRoute roles={["teacher"]}>
            <TeacherCabinetPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "admin",
        element: (
          <ProtectedRoute roles={["admin"]}>
            <AdminCabinetPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "reports",
        element: (
          <ProtectedRoute roles={["admin", "teacher"]}>
            <ReportsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "notifications",
        element: (
          <ProtectedRoute roles={["admin", "teacher"]}>
            <NotificationsPage />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);

export function App() {
  return <RouterProvider router={router} />;
}
