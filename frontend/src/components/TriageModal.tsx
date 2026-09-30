import { useState } from "react";

interface TriageLeaf {
  label: string;
  message: string;
}

interface TriageCategory {
  label: string;
  children: TriageLeaf[];
}

// Árvore de assuntos do atendimento. "Estágios" é o único ramo com regras reais
// hoje (Estágio Obrigatório de Pedagogia) — os demais ramos existem para que o
// aluno consiga descrever o assunto certo mesmo quando o caso será encaminhado
// para outro setor (diretrizes, seção 3 — escopo do setor de Estágio).
const TRIAGE_TREE: TriageCategory[] = [
  {
    label: "Estágios",
    children: [
      {
        label: "Estágio Obrigatório — etapas e Termo de Compromisso",
        message: "Tenho uma dúvida sobre as etapas do Estágio Obrigatório ou sobre o Termo de Compromisso.",
      },
      {
        label: "Estágio Obrigatório — carga horária e documentos",
        message: "Tenho uma dúvida sobre carga horária, relatórios, planos de aula ou outros documentos do Estágio Obrigatório.",
      },
      {
        label: "Estágio Obrigatório — dispensa ou convalidação de horas",
        message: "Tenho uma dúvida sobre dispensa por atividade profissional ou convalidação de horas do Estágio Obrigatório.",
      },
      {
        label: "Estágio Obrigatório — Relatório Final e prazos",
        message: "Tenho uma dúvida sobre o Relatório Final do Estágio Obrigatório e seus prazos.",
      },
      {
        label: "Estágio de Ambientação",
        message: "Tenho uma dúvida sobre o Estágio de Ambientação.",
      },
    ],
  },
  {
    label: "Outros assuntos acadêmicos",
    children: [
      { label: "TCC", message: "Tenho uma dúvida sobre o TCC." },
      { label: "Atividades complementares", message: "Tenho uma dúvida sobre atividades complementares." },
      { label: "Notas ou dependência de disciplinas", message: "Tenho uma dúvida sobre notas ou dependência de uma disciplina." },
      { label: "Colação de grau, certificado ou diploma", message: "Tenho uma dúvida sobre colação de grau, certificado ou diploma." },
      { label: "Matrícula e documentos gerais", message: "Tenho uma dúvida sobre matrícula ou documentos gerais." },
    ],
  },
  {
    label: "Financeiro",
    children: [
      { label: "Boletos e mensalidade", message: "Tenho uma dúvida sobre boletos ou mensalidade." },
      { label: "Situação financeira geral", message: "Tenho uma dúvida sobre minha situação financeira." },
    ],
  },
];

interface Props {
  onStart: (message: string) => void;
  onClose: () => void;
  submitting: boolean;
}

export function TriageModal({ onStart, onClose, submitting }: Props) {
  const [text, setText] = useState("");
  const [expanded, setExpanded] = useState<string | null>(TRIAGE_TREE[0].label);

  return (
    <div className="modal-overlay">
      <div className="modal-box triage-box">
        <span className="eyebrow">Novo atendimento</span>
        <h2>Sobre o que você precisa de ajuda?</h2>
        <p className="triage-hint">
          Escolha um assunto para começar mais rápido, ou descreva com suas próprias palavras.
        </p>

        <div className="triage-tree">
          {TRIAGE_TREE.map((category) => {
            const isOpen = expanded === category.label;
            return (
              <div key={category.label} className={`triage-category ${isOpen ? "open" : ""}`}>
                <button
                  type="button"
                  className="triage-category-header"
                  onClick={() => setExpanded(isOpen ? null : category.label)}
                >
                  <span className="chevron">▸</span>
                  {category.label}
                </button>
                {isOpen && (
                  <div className="triage-subtopics">
                    {category.children.map((leaf) => (
                      <button
                        key={leaf.label}
                        type="button"
                        className={`triage-chip ${text === leaf.message ? "selected" : ""}`}
                        onClick={() => setText(leaf.message)}
                      >
                        {leaf.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="field">
          <label>Sua dúvida</label>
          <textarea
            rows={3}
            placeholder="Ex.: já posso abrir a solicitação da segunda etapa do meu estágio?"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>

        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button className="btn secondary" onClick={onClose} disabled={submitting}>
            Cancelar
          </button>
          <button
            className="btn"
            onClick={() => text.trim() && onStart(text.trim())}
            disabled={submitting || !text.trim()}
          >
            {submitting ? "Iniciando..." : "Iniciar atendimento"}
          </button>
        </div>
      </div>
    </div>
  );
}
