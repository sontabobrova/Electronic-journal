# Документация проекта

Актуализировано: 23.05.2026.

Этот каталог содержит эксплуатационную и приемочную документацию по проекту `Электронный журнал`.

## Документы

- [deployment.md](deployment.md) - запуск проекта, Docker Compose, переменные окружения, production-заметки.
- [testing.md](testing.md) - автоматические тесты, frontend-проверки, smoke-test и ручная приемка.
- [acceptance-test-cases.md](acceptance-test-cases.md) - приемочные сценарии по ролям и разделам.
- [admin-guide.md](admin-guide.md) - руководство администратора по пользователям, учебному процессу, отчетам и аудиту.
- [user-guide.md](user-guide.md) - руководство студента и преподавателя.
- [db-admin-guide.md](db-admin-guide.md) - PostgreSQL, резервное копирование, восстановление и миграции.

## Быстрые ссылки

- Главный README проекта: [../README.md](../README.md)
- Frontend: `http://localhost:3000/`
- Backend healthcheck: `http://localhost:8000/health/`
- Django admin: `http://localhost:8000/admin/`

## Demo-стенд

Минимальный набор:

```bash
docker compose exec backend python manage.py create_demo_data
```

Большой воспроизводимый набор для демонстрации:

```bash
docker compose exec backend python manage.py create_demo_data --reset --full
```

