# Roteiro de Apresentação — MVP FATECE

## Calendário oficial do prêmio (Regulamento FAIS, seção 07.8 — ver `docs/regulamento/`)

| Etapa | Período |
|---|---|
| Período de inscrições | 20/07 a **30/09/2026** |
| Período de atualização das iniciativas | **01/10 a 20/10/2026** |
| Avaliação do Comitê (Curadoria Técnica + Comissão Julgadora) | 21/10 a 06/11/2026 |
| Divulgação dos finalistas | 10/11/2026 |
| Cerimônia de reconhecimento | 11/12/2026 |

**30/09 é o fim do cadastro/inscrição, não a entrega final.** Depois disso ainda há 3 semanas (até 20/10) para atualizar a iniciativa — incluir vídeo, novas evidências, ajustes — antes de a avaliação começar. Não é preciso ter o vídeo gravado nem tudo perfeito até dia 30.

**Requisitos mínimos para cadastrar até 30/09** (seção 06.3 do regulamento): título, descrição clara, problema/oportunidade que resolve, público beneficiado, benefícios esperados, ferramentas de IA usadas, estágio atual da solução (aceita "Ideia estruturada" ou "Protótipo" — não precisa ser "Solução em uso"), e evidências **quando disponíveis** (não obrigatório para o cadastro inicial). Isto é, dá para inscrever com o que já está pronto e continuar evoluindo depois.

**Avaliação = ICE Score** (seção 08.3): Impacto, Confiança e Facilidade, nota 1-10 cada, média final — mais uma avaliação estratégica da Comissão (alinhamento institucional, potencial de escala, redução de custo/retrabalho/risco). Vale estruturar a descrição da inscrição e o pitch em torno desses 3 eixos.

---

## Estrutura da demonstração (documento, seção 44)

1. **Problema** — Grande volume de atendimentos acadêmicos repetitivos (dúvidas de disciplina, boleto, estágio) sobrecarregando a equipe.
2. **Solução** — IA que triagem, consulta sistemas reais, resolve casos simples sozinha, escala casos complexos para um humano com contexto completo, e nunca inventa dados.
3. **Demo** — Um atendimento real simulado, de ponta a ponta (roteiro abaixo).
4. **Governança** — Auditoria completa, moderação de linguagem, score comportamental, avaliação do atendimento, indicadores gerenciais.
5. **Ciência** — Golden Dataset, métricas separadas por tipo, versionamento de prompts, testes automatizados.
6. **Escalabilidade** — `MockFateceConnector` → `RealFateceConnector` sem reescrever a aplicação; `GeminiProvider` substituível por outro provider de IA (a própria demo pode mostrar o `LocalProvider`/Ollama rodando).

---

## Checklist até 30/09 — cadastro na plataforma do FAIS

- [ ] Preencher os campos mínimos (seção 06.3): título, descrição, problema, público beneficiado, benefícios, ferramentas de IA (Gemini/Claude/Ollama via `AIProvider`), estágio da solução.
- [ ] Anexar o que já existir (screenshots do sistema rodando, este repositório) — vídeo e evidências extras podem entrar depois, até 20/10.

## Antes de gravar o vídeo (até 20/10) — checklist

- [ ] Trocar `AI_PROVIDER=local` → `AI_PROVIDER=gemini` ou `claude` no `.env` (a demonstração fica muito mais forte com a IA real resolvendo sozinha).
- [ ] Confirmar cota suficiente do provider escolhido para a gravação (Gemini free tier é só 20 req/dia; Claude via API key paga por uso).
- [ ] Resetar a base: `docker compose run --rm backend python manage.py seed_demo --students 10000` seguido de `python manage.py seed_knowledge_base`.
- [ ] Confirmar que todos os serviços estão de pé: `docker compose ps` (db, redis, backend, celery-worker, celery-beat, frontend; ollama é opcional, só para testes locais).
- [ ] Abrir `http://localhost:5173` e confirmar que a tela de login carrega.
- [ ] Fazer um teste seco (sem gravar) do roteiro completo uma vez, para garantir que a IA responde dentro do tempo esperado.

## Credenciais de demonstração

**Alunos: usuário e senha são o próprio RA** (igual ao portal real — matrícula como login). As personas fixas abaixo têm RA previsível para facilitar o roteiro; os demais ~10.000 alunos gerados também logam com usuário = senha = RA (`FTC100000` até `FTC109999`), cada um com um arquétipo acadêmico sorteado (ver seção "Cenários de aluno" abaixo).

| Papel | RA / Usuário | Senha | Cenário |
|---|---|---|---|
| Aluno | `FTC900000` | `FTC900000` | Baseline, sem pendências |
| Aluno | `FTC900001` | `FTC900001` | Matrícula pendente / sem disciplina vigente |
| Aluno | `FTC900002` | `FTC900002` | Boleto vencido (cenário 1) |
| Aluno | `FTC900003` | `FTC900003` | Atividade atrasada (cenário 2) |
| Aluno | `FTC900004` | `FTC900004` | Fora do período de estágio + linguagem inadequada (cenário 3) |
| Aluno | `FTC900005` | `FTC900005` | Score comportamental já reduzido (reincidência) |
| Monitor | `yanka.machado` | `demo123` | Fila de atendimentos |
| Gerência | `pedro.guarnieri` | `demo123` | Dashboard e auditoria |
| Administrador | `admin.master` | `demo123` | Django Admin em `/admin/` |

### Cenários de aluno na base de 10.000 (arquétipos)

Cada aluno gerado em massa recebe um arquétipo coerente (não dimensões sorteadas isoladamente), com histórico completo de matrícula período a período — matérias de períodos já encerrados aparecem com nota final (aprovado/reprovado), matérias do período vigente aparecem em andamento, sem nota, ao estilo Moodle:

| Arquétipo | % da base | O que representa |
|---|---:|---|
| `veterano_ok` | 38% | Progressão normal, matérias fechadas aprovadas, vigentes em andamento |
| `com_dependencia` | 20% | Reprovou uma matéria em período anterior e está refazendo (dependência) junto das vigentes |
| `calouro` | 10% | Primeiro período, sem histórico |
| `matricula_pendente` | 8% | Sem nenhuma disciplina vigente no momento (matrícula pendente) |
| `inadimplente_cronico` | 7% | Maioria dos boletos dos últimos 6 meses vencidos ou em processamento |
| `quase_formando` | 7% | Último período do curso, histórico quase todo aprovado, estágio avançado/concluído |
| `trancamento` | 5% | Tem histórico, mas nenhuma disciplina vigente agora (trancado) |
| `padrão` | 5% | Caso médio, sem característica dominante |

Para achar um aluno de um arquétipo específico para testar, use o Django Admin (`/admin/students/student/`) e filtre por período/situação, ou rode uma consulta rápida via `manage.py shell`.

---

## Roteiro passo a passo (cobre o critério de MVP pronto, seção 43, e os 8 cenários da seção 29)

### Parte A — Auto-resolução pela IA (cenários 1, 2 e 5)

1. Login com RA `FTC900002` (senha igual).
2. Clicar em **"+ Novo atendimento"**.
3. Enviar: *"Meu boleto deste mês está vencido, o que eu faço?"*
4. Mostrar a resposta da IA aparecendo sozinha (sem intervenção humana) — narrar que por trás disso a IA classificou a intenção, chamou a ferramenta `get_student_financial_status`/`get_open_invoices` e respondeu só com o dado real.
5. Repetir rapidamente com o RA `FTC900003`: *"Tenho alguma atividade atrasada?"*
6. (Opcional, cenário 5) Com qualquer aluno: *"Pode revisar se esse texto está formal: 'venho por meio deste solicitar...'"* — mostra a IA ajudando sem precisar de dado do aluno.
7. Encerrar um desses atendimentos como aluno (botão "Encerrar atendimento") e avaliar com estrelas.

### Parte B — Moderação + handoff combinados (cenário 3, cobre a maior parte dos 16 passos)

1. Login com RA `FTC900004`.
2. Novo atendimento. Enviar: *"Preciso fazer estágio obrigatório agora?"*
3. A IA deve identificar que o aluno não está no período elegível e, ao perceber que é uma exceção de política, encaminhar para humano (`requires_human`).
4. Enviar uma segunda mensagem com linguagem inadequada, ex.: *"Isso é um saco, esse sistema é muito burro!"* — mostrar a mensagem sendo mascarada na tela (`***`) e o aviso de moderação.
5. Logout. Login como `yanka.machado` / `demo123`.
6. Abrir a **Fila de atendimentos** — mostrar o ticket do aluno `FTC900004` com o **resumo produzido pela IA** (intenção, motivo do encaminhamento, sugestão de próximo passo).
7. Clicar em **"Assumir atendimento"**.
8. Responder ao aluno.
9. Clicar em **"Encerrar atendimento"**.

### Parte C — Caso humano puro (cenário 6)

1. Qualquer aluno: *"Minha situação é muito específica e não se encaixa em nenhuma regra que vocês têm, preciso falar com uma pessoa."*
2. Mostrar que a IA não inventa uma resposta — encaminha diretamente.

### Parte D — Linguagem do monitor (cenário 8)

1. No mesmo atendimento assumido, o monitor pode digitar algo inadequado propositalmente (ex. em ambiente de teste) para mostrar que a moderação também vale para ele — a mensagem também é mascarada e gera ocorrência.

### Parte E — Avaliação e regra das 24h

1. Encerrar um atendimento e mostrar a tela de avaliação (estrelas + comentário).
2. Explicar a regra das 24h: se o aluno não avaliar, o Celery Beat aplica nota automática 5 depois de 24h (pode mostrar o código/task rodando, já que gravar 24h reais não é viável).

### Parte F — Governança (gerência)

1. Login como `pedro.guarnieri` / `demo123`.
2. Mostrar o **Dashboard**: atendimentos abertos/em andamento/encerrados, taxa de resolução automática, tempo médio, notas, ocorrências de moderação, score médio, atendimentos por monitor/curso/período.
3. Ir em **Auditoria**, buscar pelo ID do atendimento do cenário 3 (ou pelo RA `FTC900...`), e mostrar a reconstrução completa: mensagem original vs. exibida, execução de IA (provider/modelo/intent/confidence/tool/latência), ocorrência de moderação, avaliação.

### Parte G — Escalabilidade (fala, não precisa de tela nova)

1. Explicar a camada de conectores (`AcademicConnector` → `MockFateceConnector` hoje, `RealFateceConnector` no futuro sem reescrever a aplicação).
2. Explicar a abstração de IA (`AIProvider`): mostrar que o mesmo sistema já roda com `GeminiProvider` e também com um `LocalProvider` via Ollama, usado durante o desenvolvimento para não depender de cota de API.

---

## Métricas e metodologia (ter os números em mãos)

Rodar antes da apresentação:

```bash
docker compose run --rm backend python manage.py run_golden_dataset
```

Isso imprime Tool Selection Accuracy, Handoff Accuracy e Moderation Accuracy sobre os 8 cenários — leve esses números prontos para a fala da seção "Ciência".
