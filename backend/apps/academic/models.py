from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    total_periods = models.PositiveSmallIntegerField(default=6)
    internship_eligible_period = models.PositiveSmallIntegerField(default=5)

    def __str__(self):
        return self.name


class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    period = models.PositiveSmallIntegerField()
    workload = models.PositiveSmallIntegerField(default=60)

    def __str__(self):
        return f"{self.code} - {self.name}"
