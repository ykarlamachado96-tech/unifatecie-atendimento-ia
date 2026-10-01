import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { listProviders, updateProvider } from "../../api/endpoints";
import type { AIProviderCredential } from "../../api/types";

const PROVIDER_LABEL: Record<string, string> = {
  openai: "ChatGPT (OpenAI)",
  claude: "Claude (Anthropic)",
  gemini: "Gemini (Google)",
  ollama: "Ollama (local)",
};

function ProviderCard({ credential }: { credential: AIProviderCredential }) {
  const queryClient = useQueryClient();
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState(credential.base_url);
  const [modelName, setModelName] = useState(credential.model_name);
  const [temperature, setTemperature] = useState(credential.temperature?.toString() ?? "");
  const [maxTokens, setMaxTokens] = useState(credential.max_tokens?.toString() ?? "");

  const saveMutation = useMutation({
    mutationFn: (payload: Partial<AIProviderCredential> & { api_key?: string }) =>
      updateProvider(credential.id, payload),
    onSuccess: () => {
      setApiKey("");
      queryClient.invalidateQueries({ queryKey: ["providers"] });
    },
  });

  function handleSave() {
    saveMutation.mutate({
      api_key: apiKey || undefined,
      base_url: baseUrl,
      model_name: modelName,
      temperature: temperature ? Number(temperature) : null,
      max_tokens: maxTokens ? Number(maxTokens) : null,
    });
  }

  function toggle(field: "is_active" | "use_for_embeddings") {
    saveMutation.mutate({ [field]: !credential[field] });
  }

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>{PROVIDER_LABEL[credential.provider] ?? credential.provider}</h2>
        <div style={{ display: "flex", gap: 8 }}>
          {credential.is_active && <span className="badge ok">decisão/resposta</span>}
          {credential.use_for_embeddings && <span className="badge neutral">embeddings</span>}
        </div>
      </div>

      <div className="field">
        <label>Chave de API {credential.api_key_display && <span className="mono">({credential.api_key_display})</span>}</label>
        <input
          type="password"
          placeholder="Deixe em branco para manter a chave atual"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
        />
      </div>

      {credential.provider === "ollama" && (
        <div className="field">
          <label>Base URL</label>
          <input value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} placeholder="http://ollama:11434" />
        </div>
      )}

      <div className="field">
        <label>Modelo</label>
        <input value={modelName} onChange={(e) => setModelName(e.target.value)} placeholder="(usa o padrão se vazio)" />
      </div>

      <div style={{ display: "flex", gap: 12 }}>
        <div className="field" style={{ flex: 1 }}>
          <label>Temperature</label>
          <input value={temperature} onChange={(e) => setTemperature(e.target.value)} placeholder="0.0 – 1.0" />
        </div>
        <div className="field" style={{ flex: 1 }}>
          <label>Max tokens</label>
          <input value={maxTokens} onChange={(e) => setMaxTokens(e.target.value)} placeholder="ex.: 1024" />
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", alignItems: "center", marginTop: 8 }}>
        <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
          <input type="checkbox" checked={credential.is_active} onChange={() => toggle("is_active")} />
          Ativo (decisão/resposta)
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
          <input
            type="checkbox"
            checked={credential.use_for_embeddings}
            onChange={() => toggle("use_for_embeddings")}
          />
          Usar para embeddings
        </label>
        <button className="btn" onClick={handleSave} disabled={saveMutation.isPending}>
          Salvar
        </button>
      </div>
    </div>
  );
}

export function ProvidersPage() {
  const { data: providers, isLoading } = useQuery({ queryKey: ["providers"], queryFn: listProviders });

  return (
    <div>
      <span className="eyebrow">Administrador</span>
      <h1>Configuração de IA</h1>
      <p style={{ color: "var(--text-muted)", marginTop: -6, marginBottom: 20 }}>
        Só uma credencial pode estar "Ativa" (decisão/resposta) por vez; o mesmo vale para "Usar para
        embeddings" — marcar uma desmarca a anterior automaticamente.
      </p>

      {isLoading && <p>Carregando...</p>}
      {providers?.map((credential) => (
        <ProviderCard key={credential.id} credential={credential} />
      ))}
    </div>
  );
}
