# Plano Futuro

## Curto prazo — acoplamento com a plataforma real

A Mensageria da UniFatecie já existe e já tem seu próprio frontend, fluxo de tickets e organização por
Tema/Setor. Este repositório não deve virar uma segunda aplicação em produção — o objetivo é acoplar o
motor (classificação, resolução por módulo, moderação, auditoria) a essa plataforma já existente.

Passos concretos:

- Definir com a equipe responsável pela Mensageria o formato de acoplamento (API própria exposta pelo
  motor, webhook disparado pela plataforma real, ou biblioteca interna).
- Validar o comportamento do motor com casos reais de atendimento (não só a base simulada) antes de
  qualquer uso em produção.
- Mapear os Temas/Setores reais da Mensageria para o formato de "módulo" usado aqui (base de conhecimento
  + ferramentas de consulta, quando existirem dados estruturados).

## Novos módulos

Cada novo setor segue o mesmo padrão do módulo de Estágio Obrigatório:

1. Diretrizes do setor documentadas e carregadas via `ingest_knowledge_base`.
2. Se o setor tiver dados individuais consultáveis (ex.: situação financeira, status de matrícula), expor
   ferramentas específicas em `apps/ai/tools/` e registrá-las no `TOOL_REGISTRY`.
3. Ajustar o prompt do Router para reconhecer o novo setor e saber quando resolver sozinho vs. encaminhar.
4. Escrever os casos correspondentes no Golden Dataset antes de considerar o módulo pronto.

Candidatos óbvios, pela frequência observada na Mensageria real: Financeiro (boletos, mensalidade), TCC
(correção, orientador, prazos), Secretaria (documentos, matrícula).

## Melhorias de plataforma

- RAG com chunking mais inteligente e reranking conforme a base de conhecimento crescer.
- Monitoramento de produção: latência, taxa de erro do provider de IA, custo por atendimento resolvido
  automaticamente vs. encaminhado.
- Mover constantes hoje fixas no código (limiar de confiança, pesos de moderação) para configuração
  editável sem deploy.
- "Answer Correctness" automatizado, hoje dependente de leitura manual do Golden Dataset.

## O que a arquitetura já deixa pronto para isso

- `AcademicConnector` isola toda fonte de dado — trocar por um connector real não exige tocar na IA.
- `AIProvider` isola o modelo de IA — já validado com Claude, Gemini e Ollama sem mudar o harness.
- `TOOL_REGISTRY` pode crescer por módulo sem alterar o orquestrador.
- Moderação, auditoria e avaliação já são genéricas — não têm nada específico de "estágio" no código, só
  nos prompts e nas ferramentas daquele módulo.
