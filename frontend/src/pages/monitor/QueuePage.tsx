import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { getQueue } from "../../api/endpoints";
import { StatusBadge } from "../../components/StatusBadge";

export function QueuePage() {
  const navigate = useNavigate();
  const { data: tickets, isLoading } = useQuery({
    queryKey: ["queue"],
    queryFn: getQueue,
    refetchInterval: 4000,
  });

  return (
    <div>
      <span className="eyebrow">Atendente</span>
      <h1>Fila de atendimentos</h1>

      <div className="card" style={{ marginTop: 16 }}>
        {isLoading && <p>Carregando...</p>}
        {!isLoading && (!tickets || tickets.length === 0) && (
          <p className="empty">Nenhum atendimento aguardando atendente no momento.</p>
        )}
        {!isLoading && tickets && tickets.length > 0 && (
          <ul className="ticket-list">
            {tickets.map((t) => (
              <li key={t.id} onClick={() => navigate(`/monitor/atendimento/${t.id}`)} style={{ cursor: "pointer" }}>
                <div>
                  <strong><span className="mono">#{t.id}</span> · {t.student_name}</strong>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                    <span className="mono">{t.student_ra}</span> · {t.intent || "intenção não identificada"}
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
