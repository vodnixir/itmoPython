"""Маршруты приложения tracker."""

from django.urls import path

from .views import (
    UserLoginView,
    account_delete,
    dashboard,
    logout_view,
    register,
    task_create,
    task_delete,
    task_edit,
    task_update_status,
    tasks_list,
    users_list,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register, name="register"),
    path("tasks/", tasks_list, name="tasks_list"),
    path("tasks/new/", task_create, name="task_create"),
    path("tasks/<int:pk>/edit/", task_edit, name="task_edit"),
    path("tasks/<int:pk>/delete/", task_delete, name="task_delete"),
    path(
        "tasks/<int:pk>/status/",
        task_update_status,
        name="task_update_status",
    ),
    path("users/", users_list, name="users_list"),
    path("account/delete/", account_delete, name="account_delete"),
]
