import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { getSandboxTicket, sendSandboxMessage } from "../../api/endpoints";
import { ChatWindow } from "../../components/ChatWindow";
import { MessageComposer } from "../../components/MessageComposer";
import { StatusBadge } from "../../components/StatusBadge";

export function SandboxChatPage() {
  const { ticketId } = useParams();
  const id = Number(ticketId);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [text, setText] = useState("");

  const { data: ticket } = useQuery({
    queryKey: ["sandbox-ticket", id],
    queryFn: () => getSandboxTicket(id),
    refetchInterval: 2000,
  });

  const sendMutation = useMutation({
    mutationFn: () => sendSandboxMessage(id, text),
    onSuccess: () => {
      setText("");
      queryClient.invalidateQueries({ queryKey: ["sandbox-ticket", id] });
    },
  });

  if (!ticket) return <p>Carregando...</p>;

  return (
    <div className="ticket-chat-page">
      <button className="back-link" onClick={() => navigate("/admin/simulacao")}>
        ← Simulações
      </button>

      <div className="ticket-chat-header">
        <div>
          <span className="eyebrow">Simulação (isolada dos dados de demonstração)</span>
          <h1>
            Simulação <span className="mono">#{ticket.id}</span>
          </h1>
        </div>
        <StatusBadge status={ticket.status} />
      </div>

      <div className="card chat-card">
        <ChatWindow messages={ticket.messages} viewerType="STUDENT" />
        <MessageComposer
          value={text}
          onChange={setText}
          onSend={() => sendMutation.mutate()}
          sending={sendMutation.isPending}
          placeholder="Digite a pergunta de teste..."
        />
      </div>
    </div>
  );
}
