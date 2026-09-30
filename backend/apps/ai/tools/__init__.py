from . import internship, knowledge, support

# O produto foi reduzido ao escopo único de Estágio Supervisionado Obrigatório de
# Pedagogia (diretrizes internas do setor). As ferramentas de academic.py e
# financial.py continuam existindo (usadas pelo AcademicSummaryCard do aluno),
# mas não são mais oferecidas à IA: qualquer dúvida fora do estágio deve ser
# identificada pelo router e encaminhada ao setor correto, nunca resolvida aqui.
TOOL_REGISTRY = {
    "get_student_internship_status": internship.get_student_internship_status,
    "get_internship_requirements": internship.get_internship_requirements,
    "get_internship_documents": internship.get_internship_documents,
    "create_support_ticket": support.create_support_ticket,
    "transfer_to_human": support.transfer_to_human,
    "get_ticket_status": support.get_ticket_status,
    "close_ticket": support.close_ticket,
    "search_knowledge_base": knowledge.search_knowledge_base,
}

__all__ = ["TOOL_REGISTRY"]
