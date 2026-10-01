interface Props {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  sending: boolean;
  placeholder?: string;
}

export function MessageComposer({ value, onChange, onSend, sending, placeholder }: Props) {
  function handleSend() {
    if (value.trim() && !sending) onSend();
  }

  return (
    <div className="chat-input">
      <textarea
        rows={1}
        placeholder={placeholder ?? "Digite sua mensagem..."}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
      />
      <button className="btn" onClick={handleSend} disabled={!value.trim() || sending}>
        Enviar
      </button>
    </div>
  );
}
