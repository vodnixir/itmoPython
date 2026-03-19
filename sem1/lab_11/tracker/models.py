"""Модели пользователей и задач для трекера."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Менеджер пользователей с удобными методами создания."""

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> CustomUser:
        """
        Создает и сохраняет пользователя с переданными учетными данными.

        :param email: уникальная почта пользователя
        :param password: пароль пользователя
        :param extra_fields: дополнительные поля модели
        :return: созданный пользователь
        """
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields: Any,
    ) -> CustomUser:
        """
        Создает суперпользователя с правами администратора.

        :param email: почта суперпользователя
        :param password: пароль суперпользователя
        :param extra_fields: дополнительные атрибуты
        :return: созданный суперпользователь
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с авторизацией по почте."""

    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    def __str__(self) -> str:
        """Возвращает удобное представление пользователя."""
        return self.full_name or self.email


class Task(models.Model):
    """Модель задачи, принадлежащей пользователю."""

    PRIORITY_CHOICES = [
        ("low", "Низкий"),
        ("medium", "Средний"),
        ("high", "Высокий"),
    ]

    STATUS_CHOICES = [
        ("todo", "К выполнению"),
        ("in_progress", "В работе"),
        ("done", "Готово"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="todo",
    )
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        """Возвращает название задачи с текущим статусом."""
        return f"{self.title} ({self.get_status_display()})"
