import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { assignTicket, closeTicket, getTicket, sendMessage, transferTicket } from "../../api/endpoints";
import { useAuthStore } from "../../auth/store";
import { ChatWindow } from "../../components/ChatWindow";
import { HandoffContextPanel } from "../../components/HandoffContextPanel";
import { MessageComposer } from "../../components/MessageComposer";
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
    <div className="ticket-chat-page">
      <button className="back-link" onClick={() => navigate("/monitor/fila")}>
        ← Fila de atendimentos
      </button>

      <div className="ticket-chat-header">
        <div>
          <span className="eyebrow">{ticket.student_name} · {ticket.student_ra}</span>
          <h1>
            Atendimento <span className="mono">#{ticket.id}</span>
          </h1>
        </div>
        <StatusBadge status={ticket.status} />
      </div>

      <HandoffContextPanel context={ticket.handoff_context} />

      <div className="card chat-card">
        <ChatWindow messages={ticket.messages} viewerType="MONITOR" />

        {isUnassigned && (
          <button className="btn" onClick={() => assignMutation.mutate()} disabled={assignMutation.isPending}>
            Assumir atendimento
          </button>
        )}

        {isMine && ticket.status !== "CLOSED" && (
          <>
            <MessageComposer
              value={text}
              onChange={setText}
              onSend={() => sendMutation.mutate()}
              sending={sendMutation.isPending}
              placeholder="Responder ao aluno..."
            />
            <div className="chat-actions">
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
