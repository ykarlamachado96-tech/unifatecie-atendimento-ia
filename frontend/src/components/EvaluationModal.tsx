import { useState } from "react";

interface Props {
  onSubmit: (stars: number, comment: string) => void;
  onClose: () => void;
  submitting: boolean;
}

export function EvaluationModal({ onSubmit, onClose, submitting }: Props) {
  const [stars, setStars] = useState(5);
  const [comment, setComment] = useState("");

  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <h2>Avalie o atendimento</h2>
        <div className="stars">
          {[1, 2, 3, 4, 5].map((n) => (
            <span
              key={n}
              className={`star ${n <= stars ? "filled" : ""}`}
              onClick={() => setStars(n)}
            >
              ★
            </span>
          ))}
        </div>
        <div className="field">
          <label>Comentário (opcional)</label>
          <textarea rows={3} value={comment} onChange={(e) => setComment(e.target.value)} />
        </div>
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button className="btn secondary" onClick={onClose} disabled={submitting}>
            Depois
          </button>
          <button className="btn" onClick={() => onSubmit(stars, comment)} disabled={submitting}>
            Enviar avaliação
          </button>
        </div>
      </div>
    </div>
  );
}
