import { api } from "./client";
import type {
  AcademicSummary,
  Evaluation,
  Message,
  Ticket,
  TicketDetail,
} from "./types";

export async function login(username: string, password: string) {
  const { data } = await api.post("/api/auth/login/", { username, password });
  return data as { token: string; user: any };
}

export async function getMyAcademicSummary() {
  const { data } = await api.get<AcademicSummary>("/api/students/me/summary/");
  return data;
}

export async function listTickets() {
  const { data } = await api.get<Ticket[]>("/api/support/tickets/");
  return data;
}

export async function createTicket() {
  const { data } = await api.post<Ticket>("/api/support/tickets/");
  return data;
}

export async function getTicket(ticketId: number) {
  const { data } = await api.get<TicketDetail>(`/api/support/tickets/${ticketId}/`);
  return data;
}

export async function listMessages(ticketId: number, since?: string) {
  const { data } = await api.get<Message[]>(`/api/support/tickets/${ticketId}/messages/`, {
    params: since ? { since } : undefined,
  });
  return data;
}

export async function sendMessage(ticketId: number, content: string) {
  const { data } = await api.post<Message>(`/api/support/tickets/${ticketId}/messages/`, { content });
  return data;
}

export async function getQueue() {
  const { data } = await api.get<Ticket[]>("/api/support/tickets/queue/");
  return data;
}

export async function assignTicket(ticketId: number) {
  const { data } = await api.post<TicketDetail>(`/api/support/tickets/${ticketId}/assign/`);
  return data;
}

export async function transferTicket(ticketId: number) {
  const { data } = await api.post<Ticket>(`/api/support/tickets/${ticketId}/transfer/`);
  return data;
}

export async function closeTicket(ticketId: number) {
  const { data } = await api.post<Ticket>(`/api/support/tickets/${ticketId}/close/`);
  return data;
}

export async function getEvaluation(ticketId: number) {
  const { data } = await api.get<Evaluation>(`/api/evaluations/${ticketId}/`);
  return data;
}

export async function submitEvaluation(ticketId: number, stars: number, comment: string) {
  const { data } = await api.post<Evaluation>(`/api/evaluations/${ticketId}/`, { stars, comment });
  return data;
}
