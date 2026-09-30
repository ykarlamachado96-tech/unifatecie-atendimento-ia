import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { assignTicket, closeTicket, getTicket, sendMessage, transferTicket } from "../../api/endpoints";
import { useAuthStore } from "../../auth/store";
import { ChatWindow } from "../../components/ChatWindow";
import { HandoffContextPanel } from "../../components/HandoffContextPanel";
import { StatusBadge } from "../../components/StatusBadge";

export function MonitorTicketDetailPage() {
  const { ticketId } = useParams();
  const id = Number(ticketId);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [text, setText] = useState("");
  const user = useAuthStore((s) => s.user);

  const { data: ticket } = useQuery({
    queryKey: ["ticket", id],
    queryFn: () => getTicket(id),
    refetchInterval: 3000,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["ticket", id] });

  const assignMutation = useMutation({ mutationFn: () => assignTicket(id), onSuccess: invalidate });
  const sendMutation = useMutation({
    mutationFn: () => sendMessage(id, text),
    onSuccess: () => {
      setText("");
      invalidate();
    },
  });
  const transferMutation = useMutation({
    mutationFn: () => transferTicket(id),
    onSuccess: () => navigate("/monitor/fila"),
  });
  const closeMutation = useMutation({
    mutationFn: () => closeTicket(id),
    onSuccess: () => navigate("/monitor/fila"),
  });

  if (!ticket) return <p>Carregando...</p>;

  const isMine = ticket.assigned_monitor === user?.id;
  const isUnassigned = ticket.status === "WAITING_HUMAN" && !ticket.assigned_monitor;

  return (
    <div>
      <button className="btn secondary" onClick={() => navigate("/monitor/fila")} style={{ marginBottom: 16 }}>
        ← Voltar à fila
      </button>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h1>
          Atendimento <span className="mono">#{ticket.id}</span> · {ticket.student_name}{" "}
          <span className="mono" style={{ fontSize: "0.7em", color: "var(--text-muted)" }}>
            {ticket.student_ra}
          </span>
        </h1>
        <StatusBadge status={ticket.status} />
      </div>

      <HandoffContextPanel context={ticket.handoff_context} />

      <div className="card">
        <ChatWindow messages={ticket.messages} viewerType="MONITOR" />

        {isUnassigned && (
          <button className="btn" onClick={() => assignMutation.mutate()} disabled={assignMutation.isPending}>
            Assumir atendimento
          </button>
        )}

        {isMine && ticket.status !== "CLOSED" && (
          <>
            <div className="chat-input">
              <input
                placeholder="Responder ao aluno..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && text.trim() && sendMutation.mutate()}
              />
              <button className="btn" onClick={() => sendMutation.mutate()} disabled={!text.trim() || sendMutation.isPending}>
                Enviar
              </button>
            </div>
            <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
              <button className="btn secondary" onClick={() => transferMutation.mutate()}>
                Transferir para a fila
              </button>
              <button className="btn" onClick={() => closeMutation.mutate()}>
                Encerrar atendimento
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
