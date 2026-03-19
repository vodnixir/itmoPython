"""Бизнес-логика для выборки и изменения задач."""

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from tracker.forms import TaskForm, TaskStatusForm
from tracker.models import CustomUser, Task


def list_for_owner(user: CustomUser) -> QuerySet[Task]:
    """Возвращает задачи, принадлежащие указанному пользователю."""
    return Task.objects.filter(owner=user)


def list_all() -> QuerySet[Task]:
    """Возвращает все задачи с подгруженным владельцем."""
    return Task.objects.select_related("owner")


def get_for_owner(user: CustomUser, pk: int) -> Task:
    """Получает задачу по id, принадлежащую конкретному пользователю."""
    return get_object_or_404(Task, pk=pk, owner=user)


def create_from_form(user: CustomUser, form: TaskForm) -> Task:
    """Создает задачу из формы и привязывает к владельцу."""
    task = form.save(commit=False)
    task.owner = user
    task.save()
    return task


def update_from_form(form: TaskForm) -> Task:
    """Обновляет задачу на основе данных формы."""
    return form.save()


def delete_task(task: Task) -> None:
    """Удаляет задачу."""
    task.delete()


def update_status(form: TaskStatusForm) -> Task:
    """Обновляет статус задачи из отдельной формы."""
    return form.save()
