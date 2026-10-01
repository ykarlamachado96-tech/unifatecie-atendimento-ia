import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { createSandboxTicket, listSandboxTickets, resetSandbox } from "../../api/endpoints";
import { StatusBadge } from "../../components/StatusBadge";

export function SandboxPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: tickets, isLoading } = useQuery({ queryKey: ["sandbox-tickets"], queryFn: listSandboxTickets });

  const createMutation = useMutation({
    mutationFn: createSandboxTicket,
    onSuccess: (ticket) => {
      queryClient.invalidateQueries({ queryKey: ["sandbox-tickets"] });
      navigate(`/admin/simulacao/${ticket.id}`);
    },
  });

  const resetMutation = useMutation({
    mutationFn: resetSandbox,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sandbox-tickets"] }),
  });

  return (
    <div>
      <span className="eyebrow">Administrador</span>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h1>Simular Atendimento</h1>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn secondary" onClick={() => resetMutation.mutate()} disabled={resetMutation.isPending}>
            Limpar simulação
          </button>
          <button className="btn" onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
            + Nova simulação
          </button>
        </div>
      </div>

      <p style={{ color: "var(--text-muted)", marginTop: -8, marginBottom: 20 }}>
        Roda o mesmo motor que o aluno usa de verdade (moderação, classificação, ferramentas, handoff),
        mas num aluno isolado — nunca toca nos 10.000 alunos de demonstração.
      </p>

      <div className="card">
        {isLoading && <p>Carregando...</p>}
        {!isLoading && (!tickets || tickets.length === 0) && (
          <p className="empty">Nenhuma simulação ainda. Clique em "+ Nova simulação" para começar.</p>
        )}
        {tickets && tickets.length > 0 && (
          <ul className="ticket-list">
            {tickets.map((t) => (
              <li key={t.id} onClick={() => navigate(`/admin/simulacao/${t.id}`)} style={{ cursor: "pointer" }}>
                <div>
                  <strong>Simulação <span className="mono">#{t.id}</span></strong>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
                    <span className="mono" style={{ fontSize: 11 }}>{new Date(t.created_at).toLocaleString("pt-BR")}</span>
                    {t.intent && ` · ${t.intent}`}
                  </div>
                </div>
                <StatusBadge status={t.status} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
