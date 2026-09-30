from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Papel", {"fields": ("role", "behavior_score")}),)
    list_display = ("username", "email", "first_name", "last_name", "role", "behavior_score", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
