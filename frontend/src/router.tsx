import { Navigate, Route, Routes } from "react-router-dom";

import { useAuthStore } from "./auth/store";
import { Layout } from "./components/Layout";
import { LoginPage } from "./pages/LoginPage";
import { KnowledgeSourcesPage } from "./pages/admin/KnowledgeSourcesPage";
import { ProvidersPage } from "./pages/admin/ProvidersPage";
import { SandboxChatPage } from "./pages/admin/SandboxChatPage";
import { SandboxPage } from "./pages/admin/SandboxPage";
import { QueuePage } from "./pages/monitor/QueuePage";
import { MonitorTicketDetailPage } from "./pages/monitor/TicketDetailPage";
import { StudentTicketsPage } from "./pages/student/StudentTicketsPage";
import { TicketChatPage } from "./pages/student/TicketChatPage";

const SPA_ROLES = ["STUDENT", "MONITOR", "ADMIN"];

function RequireRole({ roles, children }: { roles: string[]; children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  if (!user) return <Navigate to="/login" replace />;
  if (!roles.includes(user.role)) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export function AppRouter() {
  const user = useAuthStore((s) => s.user);
  const canUseSpa = !!user && SPA_ROLES.includes(user.role);

  return (
    <Routes>
      <Route path="/login" element={canUseSpa ? <Navigate to="/" replace /> : <LoginPage />} />

      <Route element={<Layout />}>
        <Route
          path="/aluno"
          element={
            <RequireRole roles={["STUDENT"]}>
              <StudentTicketsPage />
            </RequireRole>
          }
        />
        <Route
          path="/aluno/atendimento/:ticketId"
          element={
            <RequireRole roles={["STUDENT"]}>
              <TicketChatPage />
            </RequireRole>
          }
        />

        <Route
          path="/monitor/fila"
          element={
            <RequireRole roles={["MONITOR"]}>
              <QueuePage />
            </RequireRole>
          }
        />
        <Route
          path="/monitor/atendimento/:ticketId"
          element={
            <RequireRole roles={["MONITOR"]}>
              <MonitorTicketDetailPage />
            </RequireRole>
          }
        />

        <Route
          path="/admin/configuracao"
          element={
            <RequireRole roles={["ADMIN"]}>
              <ProvidersPage />
            </RequireRole>
          }
        />
        <Route
          path="/admin/base-de-conhecimento"
          element={
            <RequireRole roles={["ADMIN"]}>
              <KnowledgeSourcesPage />
            </RequireRole>
          }
        />
        <Route
          path="/admin/simulacao"
          element={
            <RequireRole roles={["ADMIN"]}>
              <SandboxPage />
            </RequireRole>
          }
        />
        <Route
          path="/admin/simulacao/:ticketId"
          element={
            <RequireRole roles={["ADMIN"]}>
              <SandboxChatPage />
            </RequireRole>
          }
        />
      </Route>

      <Route path="/" element={<Navigate to={homeFor(user?.role)} replace />} />
      <Route path="*" element={<Navigate to={homeFor(user?.role)} replace />} />
    </Routes>
  );
}

function homeFor(role?: string) {
  switch (role) {
    case "STUDENT":
      return "/aluno";
    case "MONITOR":
      return "/monitor/fila";
    case "ADMIN":
      return "/admin/configuracao";
    default:
      return "/login";
  }
}
