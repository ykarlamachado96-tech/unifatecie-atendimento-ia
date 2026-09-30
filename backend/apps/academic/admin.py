from django.contrib import admin

from .models import Course, Subject


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "total_periods", "internship_eligible_period")
    search_fields = ("name", "code")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "course", "period", "workload")
    list_filter = ("course", "period")
    search_fields = ("name", "code")
