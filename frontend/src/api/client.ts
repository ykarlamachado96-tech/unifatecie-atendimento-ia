import axios from "axios";

import { useAuthStore } from "../auth/store";

// Acesso local usa localhost direto; acesso via túnel público usa a URL pública do backend
// (o endereço muda a cada reinício do túnel — ver VITE_PUBLIC_API_URL no .env).
const isLocal = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const API_URL = isLocal
  ? import.meta.env.VITE_API_URL || "http://localhost:8000"
  : import.meta.env.VITE_PUBLIC_API_URL || import.meta.env.VITE_API_URL;

export const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  },
);
