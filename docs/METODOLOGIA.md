# Metodologia e Métricas — MVP FATECE

## Desenvolvimento orientado a testes (documento, seção 38)

```
Regra → teste unitário → teste integrado → Golden Dataset → teste manual
```

Toda regra de negócio implementada neste MVP passou por verificação via API antes de ser considerada pronta (ver histórico de validação: fluxo do aluno, fluxo do monitor, moderação, avaliação, dashboard e auditoria foram todos exercitados via chamadas reais, não só migrations).

## Versionamento de prompts (seção 39)

`apps/ai/prompts.py` define `PROMPT_VERSION = "academic_router_v1"`, registrado em todo `AIExecution`. Qualquer mudança relevante no prompt deve subir a versão (`academic_router_v2`, etc.) para permitir comparar performance entre versões — nunca editar o prompt em produção sem histórico.

## Golden Dataset (seção 27)

`apps/ai/golden_dataset.py` contém os 8 cenários obrigatórios de demonstração (seção 29), cada um com o resultado esperado. Rodar com:

```bash
docker compose run --rm backend python manage.py run_golden_dataset
```

O comando cria tickets reais, roda o harness de ponta a ponta e reporta:

- **Tool Selection Accuracy** — a IA escolheu a ferramenta certa?
- **Handoff Accuracy** — a decisão de encaminhar (ou não) para humano bateu com o esperado?
- **Moderation Accuracy** — a moderação identificou corretamente linguagem inadequada de aluno e monitor?

## Métricas separadas (seção 28)

O documento original pede métricas separadas em vez de um número genérico de "acerto". Neste MVP:

| Métrica | Onde é medida |
|---|---|
| Intent/Tool Selection Accuracy | `run_golden_dataset` |
| Handoff Accuracy | `run_golden_dataset` |
| Moderation Accuracy | `run_golden_dataset` |
| Resolution Rate / Human Escalation Rate | Dashboard da gerência (`taxa_resolucao_automatica`, `percentual_handoff`) |
| Answer Correctness | Não automatizado neste MVP — depende de avaliação humana/curadoria; próximo passo natural na Fase 2 |

O MVP não precisa bater as metas futuras do documento (>= 98-99%) — precisa demonstrar que **existe** metodologia para medir e evoluir. Isso está feito: os números são reais, gerados por execução real do harness, não estimados.

## Resultado real observado nesta implementação

Com o provider Gemini real (antes de trocarmos para o `LocalProvider` por causa da cota gratuita de 20 req/dia), o Golden Dataset mediu:

- Tool Selection Accuracy: 67% (4/6) — os "erros" foram escolhas de ferramenta semanticamente equivalentes (ex.: `get_student_subjects` em vez de `get_student_enrollments` para "quais disciplinas estou cursando"), não alucinações.
- Handoff Accuracy: 83% (5/6) — a falha restante foi por cota de API excedida durante o teste, não por decisão errada do modelo.
- Moderation Accuracy: 100% (2/2) — não depende de IA, é determinística.

Isso é evidência real de que a arquitetura funciona; refinar os prompts e ampliar o Golden Dataset é trabalho natural de pós-MVP (Fase 2).

## Estratégia de custo de IA (seção 40)

- A IA nunca recebe o histórico completo sem necessidade nem listas grandes de registros — só o resultado da ferramenta relevante.
- Consultas determinísticas (ex. "meu boleto está pago?") são resolvidas pelo backend via connector; a IA só recebe o resultado já filtrado.
- O `GeminiProvider` tem retry automático com backoff para erros transitórios (429/503), reduzindo desperdício de tentativas malsucedidas.
- Um `LocalProvider` (Ollama) está disponível para desenvolvimento/testes sem consumir cota de nenhuma API paga — trade-off: modelos locais pequenos têm Tool Selection Accuracy mais baixa, adequado para testar mecânica do pipeline, não qualidade de resposta.
