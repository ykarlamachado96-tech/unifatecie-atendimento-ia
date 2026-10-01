import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { closeTicket, getEvaluation, getTicket, sendMessage, submitEvaluation } from "../../api/endpoints";
import { ChatWindow } from "../../components/ChatWindow";
import { EvaluationModal } from "../../components/EvaluationModal";
import { MessageComposer } from "../../components/MessageComposer";
import { StatusBadge } from "../../components/StatusBadge";

const HUMAN_STATES = ["WAITING_HUMAN", "HUMAN_ASSIGNED", "HUMAN_PROCESSING"];

export function TicketChatPage() {
  const { ticketId } = useParams();
  const id = Number(ticketId);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [text, setText] = useState("");
  const [showEvaluation, setShowEvaluation] = useState(false);

  const { data: ticket } = useQuery({
    queryKey: ["ticket", id],
    queryFn: () => getTicket(id),
    refetchInterval: 2000,
  });

  const { data: evaluation } = useQuery({
    queryKey: ["evaluation", id],
    queryFn: () => getEvaluation(id),
    enabled: ticket?.status === "CLOSED",
  });

  const sendMutation = useMutation({
    mutationFn: () => sendMessage(id, text),
    onSuccess: () => {
      setText("");
      queryClient.invalidateQueries({ queryKey: ["ticket", id] });
    },
  });

  const closeMutation = useMutation({
    mutationFn: () => closeTicket(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ticket", id] });
      setShowEvaluation(true);
    },
  });

  const evaluateMutation = useMutation({
    mutationFn: ({ stars, comment }: { stars: number; comment: string }) => submitEvaluation(id, stars, comment),
    onSuccess: () => {
      setShowEvaluation(false);
      queryClient.invalidateQueries({ queryKey: ["evaluation", id] });
    },
  });

  if (!ticket) return <p>Carregando...</p>;

  const canClose = ticket.status === "AI_WAITING_USER" || ticket.status === "RESOLVED";
  const isClosed = ticket.status === "CLOSED";
  const isHuman = HUMAN_STATES.includes(ticket.status);

  return (
    <div className="ticket-chat-page">
      <button className="back-link" onClick={() => navigate("/aluno")}>
        ← Meus atendimentos
      </button>

      <div className="ticket-chat-header">
        <div>
          <span className="eyebrow">Estágio Obrigatório</span>
          <h1>
            Atendimento <span className="mono">#{ticket.id}</span>
          </h1>
        </div>
        <StatusBadge status={ticket.status} />
      </div>

      {isHuman && (
        <div className="status-banner">
          Seu atendimento foi encaminhado para um atendente humano do setor de estágio. Você pode continuar
          escrevendo aqui — alguém vai te responder em breve.
        </div>
      )}

      <div className="card chat-card">
        <ChatWindow messages={ticket.messages} viewerType="STUDENT" />

        {!isClosed && (
          <MessageComposer
            value={text}
            onChange={setText}
            onSend={() => sendMutation.mutate()}
            sending={sendMutation.isPending}
            placeholder="Digite sua dúvida sobre o estágio..."
          />
        )}

        {(canClose || (isClosed && evaluation)) && (
          <div className="chat-actions">
            {canClose && (
              <button className="btn secondary" onClick={() => closeMutation.mutate()}>
                Encerrar atendimento
              </button>
            )}
            {isClosed && evaluation && evaluation.status === "PENDING" && (
              <button className="btn" onClick={() => setShowEvaluation(true)}>
                Avaliar atendimento
              </button>
            )}
            {isClosed && evaluation && evaluation.status !== "PENDING" && (
              <p className="chat-evaluated-note">
                Você avaliou este atendimento com {evaluation.stars} estrela(s).
              </p>
            )}
          </div>
        )}
      </div>

      {showEvaluation && (
        <EvaluationModal
          submitting={evaluateMutation.isPending}
          onClose={() => setShowEvaluation(false)}
          onSubmit={(stars, comment) => evaluateMutation.mutate({ stars, comment })}
        />
      )}
    </div>
  );
}
