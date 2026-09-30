# Plano Futuro — Pós-MVP

## Fase 2 (documento, seção 46)

- Melhorar o RAG (chunking mais inteligente, mais documentos institucionais reais, reranking).
- Aumentar o Golden Dataset além dos 8 cenários iniciais, cobrindo mais variações e casos de borda.
- Integrações reais com os sistemas acadêmico/financeiro da FATECE (implementar `RealFateceConnector`).
- SSO institucional.
- Monitoramento e analytics de produção (latência, taxa de erro do provider de IA, custo por atendimento).
- Regras configuráveis (hoje o threshold de confiança e os pesos de decaimento de score estão em constantes no código; mover para configuração editável pela gerência/administrador).
- Editor de prompts com versionamento visual (hoje é um arquivo Python com uma constante de versão).
- Editor de fluxos para permitir novos tipos de atendimento sem alterar código.
- Answer Correctness automatizado (hoje depende de avaliação humana).

## Fase 3 — Plataforma multi-tenant (seção 47)

```
Tenant
  ↓
Configuração
  ↓
Prompt
  ↓
Knowledge Base
  ↓
Tools
  ↓
Integrações
```

A arquitetura atual já isola os pontos que vão precisar variar por tenant:

- `AcademicConnector` → cada tenant pode ter seu próprio connector (ERP, planilha, API própria).
- `AIProvider` → cada tenant pode escolher Gemini, OpenAI, ou um modelo local, sem tocar no harness.
- `TOOL_REGISTRY` → pode ser filtrado/estendido por tenant sem alterar o orquestrador.
- Moderação e score comportamental já são genéricos (não têm nada específico de "faculdade" no código, só nos textos de exemplo).

Pacotes possíveis mencionados no documento: Educação, Clínicas, Odontologia, Pet Shop, Atendimento empresarial — todos reaproveitariam o mesmo harness, moderação, auditoria e avaliação; só mudariam o connector, o prompt e as tools.
