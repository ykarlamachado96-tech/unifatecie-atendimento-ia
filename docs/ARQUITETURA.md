# Arquitetura — MVP FATECE

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Django 5 + Django REST Framework |
| Banco de dados | PostgreSQL 16 com extensão `pgvector` |
| Fila / agendamento | Celery + Redis + `django-celery-beat` |
| IA | Google Gemini (`google-genai`) via `GeminiProvider`; Ollama via `LocalProvider` para testes |
| Frontend | React 18 + TypeScript + Vite + React Query + Zustand |
| Infra local | Docker Compose (db, redis, backend, celery-worker, celery-beat, frontend, ollama) |

## Estrutura de apps (backend)

```
backend/apps/
├── accounts/       # User customizado com papel (STUDENT/MONITOR/MANAGEMENT/ADMIN) e score comportamental
├── students/       # Student, Enrollment, Activity + seed_demo (10k alunos)
├── academic/       # Course, Subject
├── finance/        # FinancialRecord (boletos)
├── internship/     # InternshipStatus, InternshipDocument
├── support/        # Ticket, Message — o coração do fluxo de atendimento
├── moderation/     # Occurrence, MessageValidator, decaimento de score
├── evaluations/    # Evaluation, regra das 24h (Celery Beat)
├── ai/             # Harness, providers (Gemini/Local), tools, RAG, Golden Dataset
├── integrations/   # AcademicConnector / MockFateceConnector
├── audit/          # (reservado — auditoria hoje vive em management/services.py)
└── management/     # Dashboard e auditoria (label Django: management_panel)
```

## Camada de conectores

```
AcademicConnector (interface abstrata)
    └── MockFateceConnector  ← implementação atual, sobre os modelos Django locais
    └── RealFateceConnector  ← futuro, quando houver acesso à base real da FATECE
```

Nenhuma ferramenta de IA acessa modelos Django diretamente — todas passam por `get_connector()`. Trocar a fonte de dados real no futuro não exige reescrever tools, harness ou frontend.

## Provider de IA

```
AIProvider (interface abstrata: decide, compose_answer, embed, score_conversation)
    └── GeminiProvider  ← produção (google-genai, com retry para 429/503)
    └── LocalProvider   ← Ollama, usado em desenvolvimento para não consumir cota de API
```

Selecionado via `AI_PROVIDER` no `.env` (`gemini` ou `local`), lido por `apps/ai/providers/get_provider()`.

## Fluxo do orquestrador (`apps/ai/harness.py`)

```
Mensagem recebida (aluno ou monitor)
        ↓
Moderação (apps/moderation/service.py) — sempre, para qualquer remetente
        ↓
Ticket já com humano? → só persiste a mensagem, IA não participa
        ↓ (não)
Remetente é aluno? → não, retorna
        ↓ (sim)
IA classifica intenção (IntentDecision, validado por Pydantic)
        ↓
Ferramenta solicitada? → executa via TOOL_REGISTRY (apps/ai/tools/)
        ↓
confidence < 0.6 OU requires_human? → handoff (WAITING_HUMAN + contexto para o monitor)
        ↓ (não)
IA compõe resposta final com o dado real da ferramenta
        ↓
Ticket → AI_WAITING_USER
```

Qualquer falha do provider de IA (erro de rede, JSON inválido, cota excedida) é capturada como `ProviderError` e vira handoff automático para humano — o sistema nunca quebra por causa da IA.

## Saída estruturada da IA

```json
{"intent": "...", "confidence": 0.0, "requires_tool": true, "tool": "...",
 "tool_args": {}, "requires_human": false, "reason": null}
```

Validada com Pydantic (`apps/ai/schemas.py`) antes de qualquer execução de ferramenta.

## Ferramentas por domínio (`apps/ai/tools/`)

- **Acadêmico**: `get_student_profile`, `get_student_course`, `get_student_enrollments`, `get_student_subjects`, `get_subject_details`, `get_student_activities`, `get_activity_status`.
- **Financeiro**: `get_student_financial_status`, `get_open_invoices`, `get_invoice_details`.
- **Estágio**: `get_student_internship_status`, `get_internship_requirements`, `get_internship_documents`.
- **Atendimento**: `create_support_ticket`, `transfer_to_human`, `get_ticket_status`, `close_ticket`.
- **Conhecimento**: `search_knowledge_base` (RAG).

## RAG

`KnowledgeDocument` / `KnowledgeChunk` (com `VectorField` do `pgvector`). Busca por similaridade de embedding quando disponível; cai para busca textual (`icontains`) quando o provider não consegue gerar embeddings — nunca quebra a experiência do aluno. Nunca contém dados individuais de alunos (regra: `DADOS DO ALUNO ≠ RAG`).

## Modelos centrais

```
Ticket{id, student, status, intent, handoff_context, assigned_monitor, resolved_by, closed_at}
Message{id, ticket, sender, sender_type, original_content, displayed_content, moderation_status}
AIExecution{id, ticket, message, provider, model, prompt_version, intent, confidence, tool, input, output, latency_ms, error}
Occurrence{id, user, role, ticket, message, category, severity, original_message, sanitized_message, validator_version}
Evaluation{id, ticket, student, monitor, stars, comment, status, deadline_at, submitted_at}
```

## Segurança (documento, seção 33)

- Senhas com hash (Django `PBKDF2` por padrão).
- Autenticação por token (`rest_framework.authtoken`).
- RBAC: aluno só vê seus próprios tickets; monitor vê a fila + seus atendimentos; gerência tem acesso de leitura a indicadores e auditoria; administrador usa o Django Admin.
- Secrets fora do código, via `.env` (nunca commitado).
- A IA nunca recebe senha nem PII além do necessário para responder a pergunta feita.

## Como rodar localmente

```bash
docker compose up -d db redis ollama
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py seed_demo --students 10000
docker compose run --rm backend python manage.py seed_knowledge_base
docker compose up -d backend celery-worker celery-beat frontend
```

Backend: `http://localhost:8000` · Frontend: `http://localhost:5173` · Admin: `http://localhost:8000/admin/`
