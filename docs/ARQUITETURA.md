# Arquitetura

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Django 5 + Django REST Framework |
| Banco de dados | PostgreSQL 16 com extensão `pgvector` |
| Fila / agendamento | Celery + Redis + `django-celery-beat` |
| IA | Claude (Anthropic API) via `ClaudeProvider` — ativo hoje; `GeminiProvider` e `LocalProvider` (Ollama) disponíveis sem trocar nada no resto do sistema |
| Frontend (demonstração) | React 18 + TypeScript + Vite + React Query + Zustand |
| Infra local | Docker Compose (db, redis, backend, celery-worker, celery-beat, frontend, ollama) |

## Papéis

Só existem dois papéis voltados ao produto: **Aluno** e **Atendente** (`MONITOR` no código, por histórico).
Há também um `ADMIN` técnico, usado só para acessar o Django Admin — não aparece na SPA.

## Estrutura de apps (backend)

```
backend/apps/
├── accounts/       # User customizado com papel (STUDENT/MONITOR/ADMIN)
├── students/       # Student, Enrollment, Activity + seed_demo (10k alunos)
├── academic/       # Course, Subject
├── finance/        # FinancialRecord (boletos) — dado simulado, hoje sem ferramenta de IA ativa
├── internship/     # Domínio do Estágio Obrigatório: etapas, requerimentos, dispensas, relatório final
├── support/        # Ticket, Message — o coração do fluxo de atendimento
├── moderation/     # Occurrence, MessageValidator, decaimento de score comportamental
├── evaluations/    # Evaluation, regra das 24h (Celery Beat)
├── ai/             # Harness, providers, tools, prompts, RAG, Golden Dataset
└── integrations/   # AcademicConnector / MockFateceConnector
```

## Camada de conectores

```
AcademicConnector (interface abstrata)
    └── MockFateceConnector  ← implementação atual, sobre os modelos Django locais
    └── (futuro) um connector real, quando houver acesso ao sistema acadêmico da UniFatecie
```

Nenhuma ferramenta de IA acessa modelos Django diretamente — todas passam por `get_connector()`. Trocar a
fonte de dados real no futuro não exige reescrever tools, harness ou frontend.

## Provider de IA

```
AIProvider (interface abstrata: decide, compose_answer, embed, score_conversation)
    └── ClaudeProvider  ← ativo hoje (Anthropic API)
    └── GeminiProvider  ← alternativa testada
    └── LocalProvider   ← Ollama, usado para desenvolver sem consumir cota de API paga
```

Selecionado via `AI_PROVIDER` no `.env` (`claude`, `gemini` ou `local`).

## Fluxo do orquestrador (`apps/ai/harness.py`)

```
Mensagem recebida (aluno ou atendente)
        ↓
Moderação (apps/moderation/service.py) — sempre, para qualquer remetente
        ↓
Ticket já com humano? → só persiste a mensagem, IA não participa
        ↓ (não)
Remetente é aluno? → não, retorna
        ↓ (sim)
Router classifica intenção e setor (IntentDecision, validado por Pydantic)
        ↓
Ferramenta solicitada? → executa via TOOL_REGISTRY (apps/ai/tools/)
        ↓
confidence baixa OU requires_human OU setor fora de escopo? → handoff (WAITING_HUMAN + setor/assunto/resumo)
        ↓ (não)
Responder compõe a resposta final em linguagem natural, com o dado real da ferramenta
        ↓
Ticket → AI_WAITING_USER
```

Qualquer falha do provider de IA (erro de rede, JSON inválido, cota excedida) é capturada como
`ProviderError` e vira handoff automático para humano — o sistema nunca quebra por causa da IA.

## Saída estruturada do Router

```json
{"intent": "...", "confidence": 0.0, "requires_tool": true, "tool": "...",
 "tool_args": {}, "requires_human": false, "reason": null,
 "setor": null, "assunto": null, "resumo": null}
```

Validada com Pydantic (`apps/ai/schemas.py`) antes de qualquer execução de ferramenta. O `setor` identifica
para onde o atendimento deve ir quando o assunto não é do módulo de Estágio Obrigatório.

## Ferramentas ativas (`apps/ai/tools/__init__.py`)

- **Estágio Obrigatório**: `get_student_internship_status`, `get_internship_requirements`,
  `get_internship_documents`.
- **Atendimento**: `create_support_ticket`, `transfer_to_human`, `get_ticket_status`, `close_ticket`.
- **Conhecimento**: `search_knowledge_base` (RAG).

As ferramentas de `academic.py`/`financial.py` continuam existindo (usadas pelo resumo acadêmico do
aluno), mas não são oferecidas à IA — qualquer dúvida fora do módulo de Estágio é classificada e
encaminhada ao setor correto, nunca resolvida com dado genérico.

## RAG

`KnowledgeDocument` / `KnowledgeChunk` (com `VectorField` do `pgvector`). Busca por similaridade de
embedding quando o provider suporta; cai para busca textual (`icontains`) quando não suporta (caso do
Claude) — nunca quebra a experiência do aluno. Nunca contém dados individuais de alunos.

```bash
docker compose exec backend python manage.py ingest_knowledge_base
```

## Modelos centrais

```
Ticket{id, student, status, intent, handoff_context, assigned_monitor, resolved_by, closed_at}
Message{id, ticket, sender, sender_type, original_content, displayed_content, moderation_status}
AIExecution{id, ticket, message, provider, model, prompt_version, intent, confidence, tool, input, output, latency_ms, error}
Occurrence{id, user, role, ticket, message, category, severity, original_message, sanitized_message, validator_version}
Evaluation{id, ticket, student, monitor, stars, comment, status, deadline_at, submitted_at}
InternshipRequirement{id, student, stage, status, host_institution, protocol_date, decision_date, planned_start_date, rejection_reason}
InternshipWaiver{id, student, kind, status, protocol_number, approved_percentage, remaining_hours}
InternshipFinalReport{id, student, status, submitted_at, discipline_term_ends_at, feedback}
```

## Segurança

- Senhas com hash (Django `PBKDF2` por padrão).
- Autenticação por token (`rest_framework.authtoken`).
- RBAC: aluno só vê seus próprios tickets; atendente vê a fila e seus atendimentos.
- Secrets fora do código, via `.env` (nunca commitado — ver `.gitignore`).
- A IA nunca recebe senha nem PII além do necessário para responder a pergunta feita.

## Como rodar localmente

```bash
cp .env.example .env   # edite com sua chave de IA
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_demo --students 10000
docker compose exec backend python manage.py ingest_knowledge_base
```

Backend: `http://localhost:8000` · Frontend: `http://localhost:5173` · Admin: `http://localhost:8000/admin/`
