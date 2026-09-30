from apps.integrations.connectors import get_connector


def get_student_internship_status(student, **kwargs):
    return get_connector().get_student_internship_status(student.id)


def get_internship_requirements(student, **kwargs):
    return get_connector().get_internship_requirements(student.id)


def get_internship_documents(student, **kwargs):
    return get_connector().get_internship_documents(student.id)
