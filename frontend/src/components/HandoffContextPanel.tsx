import type { HandoffContext } from "../api/types";

export function HandoffContextPanel({ context }: { context: HandoffContext | null }) {
  if (!context) return null;

  return (
    <div className="handoff-panel">
      <h3>Resumo produzido pela IA</h3>
      <p>
        <strong>Setor:</strong> {context.setor || "não identificado"}
      </p>
      <p>
        <strong>Assunto:</strong> {context.assunto || "não identificado"}
      </p>
      <p>
        <strong>Resumo do problema:</strong> {context.resumo || context.summary || "—"}
      </p>
      <p>
        <strong>Intenção identificada:</strong> {context.intent || "não identificada"}
      </p>
      <p>
        <strong>Ferramentas utilizadas:</strong>{" "}
        {context.tools_used.length ? context.tools_used.join(", ") : "nenhuma"}
      </p>
      <p>
        <strong>Motivo do encaminhamento:</strong> {context.reason}
      </p>
      <p>
        <strong>Sugestão de próximo passo:</strong> {context.suggested_next_step}
      </p>
    </div>
  );
}
