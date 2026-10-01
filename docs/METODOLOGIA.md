# Metodologia e Métricas

## Desenvolvimento orientado a testes

```
Regra real (diretriz do setor) → prompt/ferramenta → Golden Dataset → teste manual via API/browser
```

Toda regra de negócio do módulo de Estágio Obrigatório foi extraída do documento oficial de diretrizes do
setor, nunca de suposição — mudanças de comportamento só acontecem quando um caso real de conversa expõe
um problema (prompt ambíguo, regra confundida, dado inventado).

## Versionamento de prompts

`apps/ai/prompts.py` define `PROMPT_VERSION`, registrado em todo `AIExecution`. Qualquer mudança relevante
no prompt sobe a versão (`internship_pedagogia_v1` → `v2` → `v3`, por exemplo) para permitir comparar
comportamento entre versões — nunca se edita o prompt em produção sem esse histórico.

## Golden Dataset

`apps/ai/golden_dataset.py` contém os cenários de demonstração do módulo de Estágio Obrigatório, cada um
com o resultado esperado (ferramenta correta, se deve ou não encaminhar para humano, se a moderação deve
sinalizar a mensagem). Rodar com:

```bash
docker compose exec backend python manage.py run_golden_dataset
```

O comando cria tickets reais, roda o harness de ponta a ponta contra o provider de IA configurado e
reporta três métricas separadas — nunca um "acerto geral":

- **Tool Selection Accuracy** — a IA escolheu a ferramenta certa (ou corretamente decidiu não usar
  nenhuma, por ser pergunta de regra geral)?
- **Handoff Accuracy** — a decisão de encaminhar (ou não) para humano bateu com o esperado, incluindo
  reconhecer corretamente um assunto fora do escopo do módulo (ex.: um programa diferente do Estágio
  Obrigatório)?
- **Moderation Accuracy** — a moderação identificou corretamente linguagem inadequada de aluno e
  atendente?

## Resultado mais recente

Executado com o provider Claude (`claude-opus-5`) em produção:

| Métrica | Resultado |
|---|---|
| Tool Selection Accuracy | 100% (7/7) |
| Handoff Accuracy | 100% (7/7) |
| Moderation Accuracy | 100% (2/2) |

Os casos cobrem: regra geral vs. situação individual do aluno, sequência obrigatória de etapas, dispensa
com percentual/horas vindos do protocolo individual (nunca recalculado), os dois prazos de 7 dias úteis
distintos (análise do Termo vs. correção do Relatório Final), um programa fora de escopo (Estágio de
Ambientação), um caso de exceção que exige humano, e moderação de linguagem de aluno e atendente.

## Estratégia de custo de IA

- A IA nunca recebe o histórico completo sem necessidade nem listas grandes de registros — só o resultado
  da ferramenta relevante.
- Dúvidas de regra geral (ex. "quantas horas tem a etapa de Gestão Escolar?") são resolvidas via RAG sobre
  a base de conhecimento, não por memória do modelo.
- Dados individuais do aluno (status de etapa, dispensa deferida, relatório final) sempre vêm de uma
  consulta real ao `AcademicConnector` — a IA nunca estima ou calcula esses números.

## Próximo passo natural

Ampliar o Golden Dataset conforme novos setores da Mensageria ganharem base de conhecimento própria, e
automatizar também uma métrica de "Answer Correctness" (hoje avaliada por leitura manual da resposta
gerada em cada caso).
