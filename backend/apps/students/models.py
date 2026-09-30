from django.conf import settings
from django.db import models


class Student(models.Model):
    class AcademicStatus(models.TextChoices):
        REGULAR = "REGULAR", "Regular"
        PENDING_ENROLLMENT = "PENDING_ENROLLMENT", "Matrícula pendente"
        LOCKED = "LOCKED", "Trancado"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    ra = models.CharField("RA", max_length=20, unique=True)
    course = models.ForeignKey("academic.Course", on_delete=models.PROTECT, related_name="students")
    current_period = models.PositiveSmallIntegerField(default=1)
    academic_status = models.CharField(
        max_length=25, choices=AcademicStatus.choices, default=AcademicStatus.REGULAR
    )

    def __str__(self):
        return f"{self.ra} - {self.user.get_full_name() or self.user.username}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "ENROLLED", "Matriculado"
        IN_PROGRESS = "IN_PROGRESS", "Em andamento"
        PASSED = "PASSED", "Aprovado"
        FAILED = "FAILED", "Reprovado"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    subject = models.ForeignKey("academic.Subject", on_delete=models.CASCADE, related_name="enrollments")
    period = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ENROLLED)
    grade = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        unique_together = ("student", "subject", "period")

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.status})"


class Activity(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        SUBMITTED = "SUBMITTED", "Entregue"
        LATE = "LATE", "Atrasada"
        GRADED = "GRADED", "Corrigida"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="activities")
    subject = models.ForeignKey("academic.Subject", on_delete=models.CASCADE, related_name="activities")
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f"{self.title} - {self.student} ({self.status})"
