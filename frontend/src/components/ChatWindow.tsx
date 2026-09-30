import { useEffect, useRef } from "react";

import type { Message } from "../api/types";

function senderClass(m: Message) {
  return m.sender_type.toLowerCase();
}

function senderLabel(m: Message, viewerType: "STUDENT" | "MONITOR") {
  switch (m.sender_type) {
    case "STUDENT":
      return viewerType === "STUDENT" ? "Você" : "Aluno";
    case "MONITOR":
      return viewerType === "MONITOR" ? "Você" : "Atendente";
    case "AI":
      return "Assistente virtual";
    default:
      return "Sistema";
  }
}

function avatarGlyph(m: Message) {
  switch (m.sender_type) {
    case "STUDENT":
      return "AL";
    case "MONITOR":
      return "AT";
    case "AI":
      return "IA";
    default:
      return "•";
  }
}

export function ChatWindow({
  messages,
  viewerType = "STUDENT",
}: {
  messages: Message[];
  viewerType?: "STUDENT" | "MONITOR";
}) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <p className="chat-empty">Nenhuma mensagem ainda. Descreva sua dúvida para começar.</p>
      )}
      {messages.map((m) => {
        if (m.sender_type === "SYSTEM") {
          return (
            <div key={m.id} className="chat-system-note">
              {m.displayed_content}
            </div>
          );
        }
        return (
          <div key={m.id} className={`chat-row ${senderClass(m)}`}>
            <span className="chat-avatar">{avatarGlyph(m)}</span>
            <div className={`chat-message ${senderClass(m)}`}>
              <div className="meta">
                {senderLabel(m, viewerType)} · {new Date(m.created_at).toLocaleTimeString("pt-BR")}
                {m.moderation_status !== "CLEAN" &&
                  ` · mensagem ${m.moderation_status === "MASKED" ? "moderada" : "bloqueada"}`}
              </div>
              {m.displayed_content}
            </div>
          </div>
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
