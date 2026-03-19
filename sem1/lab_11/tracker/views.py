"""Веб-представления трекера задач."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .controllers import task_controller, user_controller
from .forms import LoginForm, RegistrationForm, TaskForm, TaskStatusForm
from .models import CustomUser, Task


class UserLoginView(LoginView):
    """Страница входа с использованием кастомной формы."""

    template_name = "tracker/login.html"
    redirect_authenticated_user = True
    authentication_form = LoginForm


def register(request: HttpRequest) -> HttpResponse:
    """Регистрирует нового пользователя и авторизует его."""
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = user_controller.register_user_from_form(form)
            login(request, user)
            messages.success(request, "Аккаунт создан, добро пожаловать!")
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "tracker/register.html", {"form": form})


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Отображает панель с задачами пользователя."""
    tasks = task_controller.list_for_owner(request.user)
    return render(
        request,
        "tracker/dashboard.html",
        {"tasks": tasks, "status_choices": Task.STATUS_CHOICES},
    )


@login_required
def task_create(request: HttpRequest) -> HttpResponse:
    """Создает новую задачу для текущего пользователя."""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task_controller.create_from_form(request.user, form)
            messages.success(request, "Задача создана.")
            return redirect("dashboard")
    else:
        form = TaskForm()
    return render(
        request,
        "tracker/task_form.html",
        {"form": form, "title": "Новая задача"},
    )


@login_required
def task_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Редактирует задачу пользователя по идентификатору."""
    task = task_controller.get_for_owner(request.user, pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task_controller.update_from_form(form)
            messages.info(request, "Задача обновлена.")
            return redirect("dashboard")
    else:
        form = TaskForm(instance=task)
    return render(
        request,
        "tracker/task_form.html",
        {"form": form, "title": "Редактирование"},
    )


@login_required
def task_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Удаляет задачу после подтверждения пользователя."""
    task = task_controller.get_for_owner(request.user, pk)
    if request.method == "POST":
        task_controller.delete_task(task)
        messages.warning(request, "Задача удалена.")
        return redirect("dashboard")
    return render(
        request,
        "tracker/task_confirm_delete.html",
        {"task": task},
    )


@login_required
def task_update_status(request: HttpRequest, pk: int) -> HttpResponse:
    """Обновляет статус задачи по идентификатору."""
    task = task_controller.get_for_owner(request.user, pk)
    if request.method == "POST":
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            task_controller.update_status(form)
            messages.success(request, "Статус изменён.")
            return redirect("dashboard")
        return HttpResponseForbidden("Некорректный статус")
    return redirect("dashboard")


@login_required
def users_list(request: HttpRequest) -> HttpResponse:
    """Отображает всех пользователей и количество их задач."""
    users = CustomUser.objects.all().prefetch_related("tasks")
    return render(request, "tracker/users_list.html", {"users": users})


@login_required
def tasks_list(request: HttpRequest) -> HttpResponse:
    """Показывает все задачи в системе."""
    tasks = task_controller.list_all()
    return render(request, "tracker/tasks_list.html", {"tasks": tasks})


@login_required
def account_delete(request: HttpRequest) -> HttpResponse:
    """Удаляет учетную запись текущего пользователя."""
    if request.method == "POST":
        user_controller.delete_account(request)
        messages.warning(request, "Аккаунт удалён.")
        return redirect("register")
    return render(request, "tracker/account_confirm_delete.html")


@require_http_methods(["GET", "POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    """Выходит из аккаунта и перенаправляет на форму входа."""
    user_controller.perform_logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("login")
