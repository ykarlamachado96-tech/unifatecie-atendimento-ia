import { NavLink, Outlet } from "react-router-dom";

import { useAuthStore } from "../auth/store";
import { GraduationCapIcon } from "./icons";

const NAV_BY_ROLE: Record<string, { to: string; label: string }[]> = {
  STUDENT: [{ to: "/aluno", label: "Meus atendimentos" }],
  MONITOR: [{ to: "/monitor/fila", label: "Fila de atendimentos" }],
  ADMIN: [
    { to: "/admin/configuracao", label: "Configuração de IA" },
    { to: "/admin/base-de-conhecimento", label: "Base de Conhecimento" },
    { to: "/admin/simulacao", label: "Simular Atendimento" },
  ],
};

const ROLE_LABEL: Record<string, string> = {
  STUDENT: "Aluno",
  MONITOR: "Atendente",
  ADMIN: "Administrador",
};

export function Layout() {
  const { user, logout } = useAuthStore();
  const items = user ? NAV_BY_ROLE[user.role] ?? [] : [];

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="logo-badge brand">
          <div className="logo-mark">
            <GraduationCapIcon size={18} />
          </div>
          <div className="logo-text">
            <div className="name">UniFatecie</div>
            <div className="subtitle">Atendimento IA</div>
          </div>
        </div>
        {items.map((item) => (
          <NavLink key={item.to} to={item.to}>
            {item.label}
          </NavLink>
        ))}
        <div className="user-info">
          <div>{user?.first_name || user?.username}</div>
          <div>{user ? ROLE_LABEL[user.role] ?? user.role : ""}</div>
          <button className="btn secondary" style={{ marginTop: 8 }} onClick={logout}>
            Sair
          </button>
        </div>
      </aside>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}
