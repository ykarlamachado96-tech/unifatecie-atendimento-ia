from django.contrib import admin

from .models import Activity, Enrollment, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("ra", "user", "course", "current_period", "academic_status")
    list_filter = ("course", "academic_status", "current_period")
    search_fields = ("ra", "user__username", "user__first_name", "user__last_name")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "period", "status", "grade")
    list_filter = ("status", "period")
    search_fields = ("student__ra", "subject__code")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "subject", "due_date", "status")
    list_filter = ("status",)
    search_fields = ("title", "student__ra")
