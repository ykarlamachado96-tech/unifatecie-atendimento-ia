from apps.integrations.connectors import get_connector


def get_student_profile(student, **kwargs):
    return get_connector().get_student_profile(student.id)


def get_student_course(student, **kwargs):
    return get_connector().get_student_course(student.id)


def get_student_enrollments(student, **kwargs):
    return get_connector().get_student_enrollments(student.id)


def get_student_subjects(student, **kwargs):
    return get_connector().get_student_subjects(student.id)


def get_subject_details(student, subject_code=None, **kwargs):
    if not subject_code:
        return {"error": "subject_code é obrigatório"}
    return get_connector().get_subject_details(subject_code)


def get_student_activities(student, **kwargs):
    return get_connector().get_student_activities(student.id)


def get_activity_status(student, subject_code=None, **kwargs):
    return get_connector().get_activity_status(student.id, subject_code)
