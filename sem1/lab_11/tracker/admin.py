"""Настройки административной панели Django."""

from django.contrib import admin

from .models import CustomUser, Task


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Отображение и поиск пользователей в админке."""

    list_display = ("email", "full_name", "is_staff", "is_active")
    search_fields = ("email", "full_name")
    ordering = ("email",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Управление задачами в административной панели."""

    list_display = ("title", "owner", "priority", "status", "updated_at")
    list_filter = ("priority", "status")
    search_fields = ("title", "description", "owner__email")
