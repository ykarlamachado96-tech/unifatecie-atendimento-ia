"""Golden Dataset (diretrizes internas, metodologia de testes) — cenários de
demonstração do setor de Estágio Supervisionado Obrigatório de Pedagogia.

Usa as personas fixas do seed_demo (login = RA):
FTC900000 sem requerimento · FTC900001 em análise · FTC900002 com dispensa ·
FTC900003 relatório enviado · FTC900005 reincidente em linguagem.
"""

GOLDEN_CASES = [
    {
        "id": "CASO_001_TRES_ETAPAS",
        "type": "ai_intent",
        "student_username": "FTC900000",
        "question": "Posso fazer só a etapa de Educação Infantil e pular as outras duas do estágio?",
        "expected_tool": "search_knowledge_base",
        "expected_requires_human": False,
    },
    {
        "id": "CASO_002_UM_REQUERIMENTO_POR_VEZ",
        "type": "ai_intent",
        "student_username": "FTC900001",
        "question": "Já posso abrir a solicitação da segunda etapa do meu estágio?",
        "expected_tool": "get_student_internship_status",
        "expected_requires_human": False,
    },
    {
        "id": "CASO_003_CNPJ_NAO_APARECE",
        "type": "ai_intent",
        "student_username": "FTC900000",
        "question": "O CNPJ da escola onde vou estagiar não aparece no sistema, o que eu faço?",
        "expected_tool": "search_knowledge_base",
        "expected_requires_human": False,
    },
    {
        "id": "CASO_004_DISPENSA_PARCIAL",
        "type": "ai_intent",
        "student_username": "FTC900002",
        "question": "Tenho dispensa por atividade profissional. Quantas horas de estágio ainda preciso cumprir?",
        "expected_tool": "get_student_internship_status",
        "expected_requires_human": False,
    },
    {
        "id": "CASO_005_PRAZO_RELATORIO_FINAL",
        "type": "ai_intent",
        "student_username": "FTC900003",
        "question": "Enviei meu relatório final há mais de uma semana, quando ele fica pronto?",
        "expected_tool": "get_student_internship_status",
        "expected_requires_human": False,
    },
    {
        "id": "CASO_006B_ESTAGIO_AMBIENTACAO_FORA_DE_ESCOPO",
        "type": "ai_intent",
        "student_username": "FTC900000",
        "question": "Quantas horas eu preciso cumprir no Estágio de Ambientação?",
        "expected_tool": None,
        "expected_requires_human": True,
    },
    {
        "id": "CASO_006_CASO_HUMANO",
        "type": "ai_intent",
        "student_username": "FTC900000",
        "question": (
            "Fiz o estágio numa escola sem o Termo de Compromisso formalizado porque a diretora disse "
            "que dava para regularizar depois, e agora não sei o que fazer."
        ),
        "expected_tool": None,
        "expected_requires_human": True,
    },
    {
        "id": "CASO_007_LINGUAGEM_ALUNO",
        "type": "moderation",
        "student_username": "FTC900000",
        "sender_role": "STUDENT",
        "message": "Isso é uma porra, vocês são uns idiotas!",
        "expected_flagged": True,
    },
    {
        "id": "CASO_008_LINGUAGEM_MONITOR",
        "type": "moderation",
        "student_username": "FTC900000",
        "sender_role": "MONITOR",
        "message": "Para de me encher o saco com isso, seu burro.",
        "expected_flagged": True,
    },
]
