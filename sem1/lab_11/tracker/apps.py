"""Конфигурация приложения Tracker."""

from django.apps import AppConfig


class TrackerConfig(AppConfig):
    """Регистрация приложения в проекте Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tracker"
