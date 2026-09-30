import { create } from "zustand";

export type Role = "STUDENT" | "MONITOR" | "ADMIN";

export interface AuthUser {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  role: Role;
}

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  login: (token: string, user: AuthUser) => void;
  logout: () => void;
}

function loadInitial(): { token: string | null; user: AuthUser | null } {
  try {
    const token = localStorage.getItem("fatece_token");
    const userRaw = localStorage.getItem("fatece_user");
    return { token, user: userRaw ? JSON.parse(userRaw) : null };
  } catch {
    return { token: null, user: null };
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  ...loadInitial(),
  login: (token, user) => {
    localStorage.setItem("fatece_token", token);
    localStorage.setItem("fatece_user", JSON.stringify(user));
    set({ token, user });
  },
  logout: () => {
    localStorage.removeItem("fatece_token");
    localStorage.removeItem("fatece_user");
    set({ token: null, user: null });
  },
}));
