import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { createKnowledgeSource, listKnowledgeSources, processKnowledgeSource } from "../../api/endpoints";

const CATEGORY_OPTIONS = [
  { value: "REGULATION", label: "Regulamento" },
  { value: "FAQ", label: "FAQ" },
  { value: "PROCEDURE", label: "Procedimento" },
  { value: "INTERNSHIP_RULES", label: "Regras de estágio" },
  { value: "FINANCIAL_GUIDANCE", label: "Orientação financeira" },
];

const STATUS_BADGE: Record<string, string> = { PENDING: "neutral", PROCESSED: "ok", ERROR: "danger" };
const STATUS_LABEL: Record<string, string> = {
  PENDING: "Aguardando processamento",
  PROCESSED: "Processado",
  ERROR: "Erro no processamento",
};

export function KnowledgeSourcesPage() {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState(CATEGORY_OPTIONS[0].value);
  const [rawText, setRawText] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const { data: sources, isLoading } = useQuery({
    queryKey: ["knowledge-sources"],
    queryFn: listKnowledgeSources,
  });

  const createMutation = useMutation({
    mutationFn: () => createKnowledgeSource({ title, category, file, raw_text: rawText }),
    onSuccess: () => {
      setTitle("");
      setRawText("");
      setFile(null);
      queryClient.invalidateQueries({ queryKey: ["knowledge-sources"] });
    },
  });

  const processMutation = useMutation({
    mutationFn: (id: number) => processKnowledgeSource(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["knowledge-sources"] }),
  });

  return (
    <div>
      <span className="eyebrow">Administrador</span>
      <h1>Base de Conhecimento</h1>

      <div className="card">
        <h2 style={{ marginTop: 0 }}>Nova fonte</h2>
        <div className="field">
          <label>Título</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ex.: Diretrizes de Estágio — Pedagogia" />
        </div>
        <div className="field">
          <label>Categoria</label>
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            {CATEGORY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Arquivo (opcional)</label>
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        </div>
        <div className="field">
          <label>Ou cole o texto aqui</label>
          <textarea rows={4} value={rawText} onChange={(e) => setRawText(e.target.value)} placeholder="## Seção\n\nConteúdo..." />
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button
            className="btn"
            onClick={() => createMutation.mutate()}
            disabled={!title.trim() || (!file && !rawText.trim()) || createMutation.isPending}
          >
            Cadastrar
          </button>
        </div>
      </div>

      <div className="card">
        <h2 style={{ marginTop: 0 }}>Fontes cadastradas</h2>
        {isLoading && <p>Carregando...</p>}
        {!isLoading && (!sources || sources.length === 0) && <p className="empty">Nenhuma fonte cadastrada ainda.</p>}
        {sources && sources.length > 0 && (
          <ul className="ticket-list">
            {sources.map((source) => (
              <li key={source.id}>
                <div>
                  <strong>{source.title}</strong>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
                    {CATEGORY_OPTIONS.find((o) => o.value === source.category)?.label ?? source.category}
                    {source.document_title && ` · ${source.document_title}`}
                    {source.error_message && ` · ${source.error_message}`}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span className={`badge ${STATUS_BADGE[source.status] ?? "neutral"}`}>
                    {STATUS_LABEL[source.status] ?? source.status}
                  </span>
                  <button
                    className="btn secondary"
                    onClick={() => processMutation.mutate(source.id)}
                    disabled={processMutation.isPending}
                  >
                    Processar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
