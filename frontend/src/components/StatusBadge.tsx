import type { TicketStatus } from "../api/types";

const LABELS: Record<TicketStatus, string> = {
  OPEN: "Aberto",
  AI_PROCESSING: "IA processando",
  AI_WAITING_USER: "Aguardando você",
  WAITING_HUMAN: "Aguardando monitor",
  HUMAN_ASSIGNED: "Monitor designado",
  HUMAN_PROCESSING: "Em atendimento",
  RESOLVED: "Resolvido",
  CLOSED: "Encerrado",
};

const CLASS_BY_STATUS: Record<TicketStatus, string> = {
  OPEN: "open",
  AI_PROCESSING: "open",
  AI_WAITING_USER: "open",
  WAITING_HUMAN: "waiting",
  HUMAN_ASSIGNED: "human",
  HUMAN_PROCESSING: "human",
  RESOLVED: "closed",
  CLOSED: "closed",
};

export function StatusBadge({ status }: { status: TicketStatus }) {
  return <span className={`badge ${CLASS_BY_STATUS[status]}`}>{LABELS[status]}</span>;
}
