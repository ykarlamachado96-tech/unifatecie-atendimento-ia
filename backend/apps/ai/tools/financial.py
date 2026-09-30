from apps.integrations.connectors import get_connector


def get_student_financial_status(student, **kwargs):
    return get_connector().get_student_financial_status(student.id)


def get_open_invoices(student, **kwargs):
    return get_connector().get_open_invoices(student.id)


def get_invoice_details(student, invoice_id=None, **kwargs):
    if not invoice_id:
        return {"error": "invoice_id é obrigatório"}
    return get_connector().get_invoice_details(student.id, invoice_id)
