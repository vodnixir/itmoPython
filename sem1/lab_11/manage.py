"""Утилита командной строки Django для административных задач."""
import os
import sys


def main() -> None:
    """Запускает стандартный CLI Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tasktracker.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Install it and try again."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
