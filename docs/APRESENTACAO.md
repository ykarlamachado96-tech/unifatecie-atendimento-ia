# Roteiro de Apresentação

## Calendário oficial do prêmio (Regulamento FAIS — ver `docs/regulamento/`)

| Etapa | Período |
|---|---|
| Período de inscrições | 20/07 a **30/09/2026** |
| Período de atualização das iniciativas | **01/10 a 20/10/2026** |
| Avaliação do Comitê (Curadoria Técnica + Comissão Julgadora) | 21/10 a 06/11/2026 |
| Divulgação dos finalistas | 10/11/2026 |
| Cerimônia de reconhecimento | 11/12/2026 |

**30/09 é o fim do cadastro/inscrição, não a entrega final.** Depois disso ainda há 3 semanas (até 20/10)
para atualizar a iniciativa — vídeo, novas evidências, ajustes — antes de a avaliação começar.

**Avaliação = ICE Score**: Impacto, Confiança e Facilidade, nota 1-10 cada, média final — mais avaliação
estratégica da Comissão (alinhamento institucional, potencial de escala, redução de custo/retrabalho/risco).

## Estrutura da demonstração

1. **Problema** — Grande volume de atendimentos repetitivos em todos os setores da Mensageria, cada um
   lido e classificado manualmente por um atendente.
2. **Solução** — Motor de IA que classifica o atendimento pelo setor certo e resolve sozinho os casos onde
   já tem base de conhecimento carregada, escalando para humano com contexto completo quando não pode.
3. **Demo** — Um atendimento real simulado, de ponta a ponta (roteiro abaixo), sobre o módulo de Estágio
   Obrigatório de Pedagogia.
4. **Governança** — Moderação de linguagem (aluno e atendente), auditoria por execução de IA, versionamento
   de prompt.
5. **Ciência** — Golden Dataset, métricas separadas por tipo, testes executados contra o modelo real.
6. **Escalabilidade** — `AcademicConnector` e `AIProvider` plugáveis; cada novo setor é um módulo (base de
   conhecimento + ferramentas), sem reescrever o motor.

## Credenciais de demonstração

Todas sobre uma base simulada (~10.000 alunos de Pedagogia e outros cursos); nenhum dado real.

| Papel | Usuário | Senha | Cenário |
|---|---|---|---|
| Aluno | `FTC900000` | `FTC900000` | Elegível, sem requerimento aberto |
| Aluno | `FTC900001` | `FTC900001` | 1ª etapa (Educação Infantil) em análise |
| Aluno | `FTC900002` | `FTC900002` | Dispensa por atividade profissional deferida (50%, 48h restantes) |
| Aluno | `FTC900003` | `FTC900003` | 3 etapas concluídas, relatório final enviado, aguardando correção |
| Aluno | `FTC900004` | `FTC900004` | Ainda não chegou ao 7º período (fora do período de estágio) |
| Aluno | `FTC900005` | `FTC900005` | Score reduzido por reincidência em linguagem |
| Atendente | `yanka.machado` | `demo123` | Fila de atendimentos |
| Administrador | `admin.master` | `demo123` | Django Admin em `/admin/` |

Os demais ~10.000 alunos logam com usuário = senha = RA (`FTC100000` a `FTC109999`); só os alunos de
Pedagogia no 7º período ou além têm dados de estágio populados.

## Roteiro passo a passo

### Parte A — Auto-resolução pela IA

1. Login com RA `FTC900002`.
2. "+ Novo atendimento" → escolher na triagem "Dispensa por atividade profissional ou convalidação".
3. Enviar: *"Quantas horas de estágio eu ainda preciso cumprir?"*
4. Mostrar a resposta aparecendo sozinha, citando exatamente o percentual (50%) e as horas restantes (48h)
   do protocolo individual do aluno — nunca um cálculo genérico.
5. Repetir com RA `FTC900001`: *"Já posso abrir a solicitação da segunda etapa?"* — mostra a regra de um
   requerimento por vez sendo aplicada corretamente.
6. Encerrar o atendimento como aluno e avaliar com estrelas.

### Parte B — Fora de escopo + handoff

1. Login com RA `FTC900000`.
2. Novo atendimento: *"Quantas horas eu preciso cumprir no Estágio de Ambientação?"*
3. A IA deve reconhecer que é um programa diferente do Estágio Obrigatório, sem regras carregadas, e
   encaminhar para humano com setor identificado — nunca reutilizar as regras do Estágio Obrigatório.
4. Logout. Login como `yanka.machado` / `demo123`.
5. Abrir a fila de atendimentos, abrir o ticket, mostrar o **resumo produzido pela IA** (setor, assunto,
   resumo, motivo do encaminhamento).
6. Assumir e responder o atendimento.

### Parte C — Caso humano por exceção de política

1. Qualquer aluno: *"Fiz o estágio numa escola sem o Termo de Compromisso formalizado porque a diretora
   disse que dava pra regularizar depois, e agora não sei o que fazer."*
2. Mostrar que a IA não inventa uma solução — encaminha diretamente, com o contexto já estruturado.

### Parte D — Moderação de linguagem

1. Com qualquer aluno, enviar uma mensagem com linguagem inadequada — mostrar a mensagem mascarada na tela
   e o aviso de moderação.
2. No mesmo atendimento assumido pelo atendente, mostrar que a mesma validação vale para ele também.

### Parte E — Avaliação e regra das 24h

1. Encerrar um atendimento e mostrar a tela de avaliação (estrelas + comentário).
2. Explicar a regra das 24h: se o aluno não avaliar, o Celery Beat aplica nota automática depois de 24h.

### Parte F — Escalabilidade (fala, não precisa de tela nova)

1. Explicar a camada de conectores (`AcademicConnector`) e a abstração de IA (`AIProvider`): o mesmo motor
   já roda com Claude, foi testado com Gemini e com Ollama local, sem mudar uma linha do harness.
2. Explicar que um novo setor da Mensageria é um módulo: base de conhecimento + ferramentas de consulta,
   reaproveitando classificação, moderação e auditoria que já existem.

## Métricas e metodologia (ter os números em mãos)

```bash
docker compose exec backend python manage.py run_golden_dataset
```

Imprime Tool Selection Accuracy, Handoff Accuracy e Moderation Accuracy sobre os cenários do módulo de
Estágio Obrigatório — leve esses números prontos para a fala da seção "Ciência".
