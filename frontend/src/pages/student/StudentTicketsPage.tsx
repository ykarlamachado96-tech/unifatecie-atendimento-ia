import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createTicket, getMyAcademicSummary, listTickets, sendMessage } from "../../api/endpoints";
import { AcademicSummaryCard } from "../../components/AcademicSummaryCard";
import { StatusBadge } from "../../components/StatusBadge";
import { TriageModal } from "../../components/TriageModal";

export function StudentTicketsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showTriage, setShowTriage] = useState(false);
  const { data: tickets, isLoading } = useQuery({ queryKey: ["tickets"], queryFn: listTickets });
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ["academic-summary"],
    queryFn: getMyAcademicSummary,
  });

  const startMutation = useMutation({
    mutationFn: async (message: string) => {
      const ticket = await createTicket();
      await sendMessage(ticket.id, message);
      return ticket;
    },
    onSuccess: (ticket) => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
      setShowTriage(false);
      navigate(`/aluno/atendimento/${ticket.id}`);
    },
  });

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h1>Meus atendimentos</h1>
        <button className="btn" onClick={() => setShowTriage(true)}>
          + Novo atendimento
        </button>
      </div>

      {!summaryLoading && summary && <AcademicSummaryCard summary={summary} />}

      <div className="card">
        <h2 style={{ marginTop: 0 }}>Histórico de atendimentos</h2>
        {isLoading && <p>Carregando...</p>}
        {!isLoading && (!tickets || tickets.length === 0) && <p>Nenhum atendimento ainda.</p>}
        <ul className="ticket-list">
          {tickets?.map((t) => (
            <li key={t.id} onClick={() => navigate(`/aluno/atendimento/${t.id}`)} style={{ cursor: "pointer" }}>
              <div>
                <strong>Atendimento <span className="mono">#{t.id}</span></strong>
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
                  <span className="mono" style={{ fontSize: 11 }}>{new Date(t.created_at).toLocaleString("pt-BR")}</span>
                  {t.intent && ` · ${t.intent}`}
                </div>
              </div>
              <StatusBadge status={t.status} />
            </li>
          ))}
        </ul>
      </div>

      {showTriage && (
        <TriageModal
          submitting={startMutation.isPending}
          onClose={() => setShowTriage(false)}
          onStart={(message) => startMutation.mutate(message)}
        />
      )}
    </div>
  );
}
