import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../api/endpoints";
import { useAuthStore } from "../auth/store";
import { GraduationCapIcon } from "../components/icons";

const HOME_BY_ROLE: Record<string, string> = {
  STUDENT: "/aluno",
  MONITOR: "/monitor/fila",
};

function PersonIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20c0-4 3.5-6 8-6s8 2 8 6" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </svg>
  );
}

function EyeIcon({ off }: { off: boolean }) {
  return off ? (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 3l18 18" />
      <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
      <path d="M9.9 4.24A9.1 9.1 0 0 1 12 4c5 0 9 4 10 8-.3 1.1-.9 2.2-1.6 3.2M6.1 6.1C3.9 7.6 2.3 9.7 2 12c1 4 5 8 10 8 1 0 2-.2 2.9-.5" />
    </svg>
  ) : (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M2 12s4-8 10-8 10 8 10 8-4 8-10 8-10-8-10-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function ArrowRightIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

export function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const authLogin = useAuthStore((s) => s.login);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { token, user } = await login(username, password);
      authLogin(token, user);
      navigate(HOME_BY_ROLE[user.role] ?? "/");
    } catch {
      setError("Usuário ou senha inválidos.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-letterhead">
        <div className="logo-mark logo-mark-lg">
          <GraduationCapIcon size={28} />
        </div>
        <div className="name">UniFatecie</div>
        <div className="subtitle">CENTRO UNIVERSITÁRIO</div>
        <p className="welcome">Bem-vindo à Mensageria</p>
      </div>

      <div className="login-body">
      <form className="login-box" onSubmit={handleSubmit}>
        <p className="lead">Informe suas credenciais para acessar o portal:</p>

        <div className="field">
          <label>Usuário</label>
          <div className="input-with-icon">
            <PersonIcon />
            <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus placeholder="RA (aluno) ou usuário (equipe)" />
          </div>
        </div>

        <div className="field">
          <label>Senha</label>
          <div className="input-with-icon">
            <LockIcon />
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ paddingRight: 36 }}
            />
            <span
              onClick={() => setShowPassword((v) => !v)}
              style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", cursor: "pointer", color: "var(--text-muted)" }}
            >
              <EyeIcon off={showPassword} />
            </span>
          </div>
        </div>

        {error && <p className="error-text">{error}</p>}

        <button className="btn" type="submit" disabled={loading} style={{ width: "100%", justifyContent: "center", marginTop: 8 }}>
          {loading ? "Entrando..." : "Fazer login"}
          {!loading && <ArrowRightIcon />}
        </button>
      </form>
      </div>
    </div>
  );
}
