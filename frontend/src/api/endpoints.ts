import { api } from "./client";
import type {
  AcademicSummary,
  AIProviderCredential,
  Evaluation,
  KnowledgeSource,
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

export async function listProviders() {
  const { data } = await api.get<AIProviderCredential[]>("/api/ai/providers/");
  return data;
}

export async function updateProvider(id: number, payload: Partial<AIProviderCredential> & { api_key?: string }) {
  const { data } = await api.patch<AIProviderCredential>(`/api/ai/providers/${id}/`, payload);
  return data;
}

export async function listKnowledgeSources() {
  const { data } = await api.get<KnowledgeSource[]>("/api/ai/knowledge-sources/");
  return data;
}

export async function createKnowledgeSource(payload: {
  title: string;
  category: string;
  file?: File | null;
  raw_text?: string;
}) {
  const form = new FormData();
  form.append("title", payload.title);
  form.append("category", payload.category);
  if (payload.file) form.append("file", payload.file);
  if (payload.raw_text) form.append("raw_text", payload.raw_text);
  const { data } = await api.post<KnowledgeSource>("/api/ai/knowledge-sources/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function processKnowledgeSource(id: number) {
  const { data } = await api.post<KnowledgeSource>(`/api/ai/knowledge-sources/${id}/process/`);
  return data;
}

export async function listSandboxTickets() {
  const { data } = await api.get<Ticket[]>("/api/ai/sandbox/tickets/");
  return data;
}

export async function createSandboxTicket() {
  const { data } = await api.post<Ticket>("/api/ai/sandbox/tickets/");
  return data;
}

export async function getSandboxTicket(ticketId: number) {
  const { data } = await api.get<TicketDetail>(`/api/ai/sandbox/tickets/${ticketId}/`);
  return data;
}

export async function sendSandboxMessage(ticketId: number, content: string) {
  const { data } = await api.post<Message>(`/api/ai/sandbox/tickets/${ticketId}/messages/`, { content });
  return data;
}

export async function resetSandbox() {
  await api.post("/api/ai/sandbox/reset/");
}
