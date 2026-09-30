import type { AcademicSummary } from "../api/types";

const ACTIVITY_BADGE: Record<string, string> = { PENDING: "warn", LATE: "danger" };
const INVOICE_BADGE: Record<string, string> = {
  PENDING: "warn",
  OVERDUE: "danger",
  PROCESSING: "neutral",
  PAID: "ok",
};
const INTERNSHIP_OVERALL_LABEL: Record<string, string> = {
  NOT_ELIGIBLE: "Ainda não elegível",
  NOT_STARTED: "Elegível, sem requerimento aberto",
  AWAITING_ANALYSIS: "Requerimento em análise",
  IN_PROGRESS: "Em andamento",
  AWAITING_FINAL_REPORT_REVIEW: "Aguardando correção do Relatório Final",
  PENDING_CORRECTION: "Relatório Final devolvido para correção",
  DEPENDENCY: "Regime de Dependência",
  COMPLETED: "Concluído",
};
const STAGE_STATUS_BADGE: Record<string, string> = {
  NOT_REQUESTED: "neutral",
  IN_ANALYSIS: "warn",
  FORMALIZED: "ok",
  REJECTED: "danger",
  COMPLETED: "ok",
};
const STAGE_STATUS_LABEL: Record<string, string> = {
  NOT_REQUESTED: "Não solicitado",
  IN_ANALYSIS: "Em análise",
  FORMALIZED: "Formalizado",
  REJECTED: "Indeferido",
  COMPLETED: "Concluído",
};
const ACADEMIC_STATUS_LABEL: Record<string, string> = {
  REGULAR: "Regular",
  PENDING_ENROLLMENT: "Matrícula pendente",
  LOCKED: "Trancado",
};

function money(v: number) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function date(v: string) {
  return new Date(v + "T00:00:00").toLocaleDateString("pt-BR");
}

export function AcademicSummaryCard({ summary }: { summary: AcademicSummary }) {
  return (
    <div className="summary-card">
      <div className="summary-header">
        <h2>{summary.course}</h2>
        <span className="meta">
          {summary.current_period}º período · RA {summary.ra} ·{" "}
          {ACADEMIC_STATUS_LABEL[summary.academic_status] ?? summary.academic_status}
        </span>
      </div>

      <div className="summary-grid">
        <div className="summary-section">
          <h3>Disciplinas em andamento</h3>
          {summary.current_subjects.length === 0 ? (
            <p className="empty">Nenhuma disciplina vigente no momento.</p>
          ) : (
            <ul className="summary-list">
              {summary.current_subjects.map((s) => (
                <li key={s.subject_code}>
                  <span className="label">{s.subject_name}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="summary-section">
          <h3>Atividades</h3>
          {summary.pending_activities.length === 0 ? (
            <p className="empty">Nenhuma atividade pendente ou atrasada.</p>
          ) : (
            <ul className="summary-list">
              {summary.pending_activities.map((a, i) => (
                <li key={i}>
                  <span className="label">
                    {a.title}
                    <br />
                    <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
                      prazo {date(a.due_date)}
                    </span>
                  </span>
                  <span className={`badge ${ACTIVITY_BADGE[a.status] ?? "neutral"}`}>
                    {a.status === "LATE" ? "Atrasada" : "Pendente"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="summary-section">
          <h3>Financeiro</h3>
          {summary.open_invoices.length === 0 ? (
            <p className="empty">Nenhum boleto em aberto.</p>
          ) : (
            <ul className="summary-list">
              {summary.open_invoices.map((inv) => (
                <li key={inv.invoice_id}>
                  <span className="label">
                    {money(inv.amount)}
                    <br />
                    <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
                      vencimento {date(inv.due_date)}
                    </span>
                  </span>
                  <span className={`badge ${INVOICE_BADGE[inv.status] ?? "neutral"}`}>
                    {inv.status === "OVERDUE" ? "Vencido" : inv.status === "PROCESSING" ? "Em processamento" : "Aberto"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="summary-section">
          <h3>Estágio Obrigatório — Pedagogia</h3>
          <ul className="summary-list">
            <li>
              <span className="label">Situação geral</span>
              <span className="badge neutral">
                {INTERNSHIP_OVERALL_LABEL[summary.internship_status.overall_status] ??
                  summary.internship_status.overall_status}
              </span>
            </li>
            {summary.internship_status.is_eligible &&
              summary.internship_status.stages.map((stage) => (
                <li key={stage.stage}>
                  <span className="label">
                    {stage.stage_label}
                    <br />
                    <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
                      {stage.required_hours}h
                      {stage.host_institution ? ` · ${stage.host_institution}` : ""}
                      {stage.rejection_reason ? ` · motivo: ${stage.rejection_reason}` : ""}
                    </span>
                  </span>
                  <span className={`badge ${STAGE_STATUS_BADGE[stage.status] ?? "neutral"}`}>
                    {STAGE_STATUS_LABEL[stage.status] ?? stage.status}
                  </span>
                </li>
              ))}
            {summary.internship_status.active_waiver && (
              <li>
                <span className="label">
                  Dispensa/convalidação deferida
                  <br />
                  <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
                    protocolo {summary.internship_status.active_waiver.protocol_number}
                    {summary.internship_status.active_waiver.remaining_hours != null
                      ? ` · restam ${summary.internship_status.active_waiver.remaining_hours}h presenciais`
                      : ""}
                  </span>
                </span>
                <span className="badge ok">
                  {summary.internship_status.active_waiver.approved_percentage}%
                </span>
              </li>
            )}
            {summary.internship_status.final_report.status !== "NOT_SUBMITTED" && (
              <li>
                <span className="label">Relatório Final</span>
                <span className="badge neutral">
                  {summary.internship_status.final_report.status === "SUBMITTED"
                    ? "Enviado, aguardando correção"
                    : summary.internship_status.final_report.status === "RETURNED_FOR_CORRECTION"
                      ? "Devolvido para correção"
                      : summary.internship_status.final_report.status === "APPROVED"
                        ? "Aprovado"
                        : "Regime de Dependência"}
                </span>
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
