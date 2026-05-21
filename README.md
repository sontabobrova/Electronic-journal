# Электронный журнал

Автоматизированная информационная система для учета успеваемости, посещаемости, отчетов, уведомлений и аудита действий пользователей.

## Стек

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Docker Compose
- OpenPyXL
- ReportLab

## Быстрый старт

1. Создайте файл окружения:

   ```bash
   cp .env.example .env
   ```

2. Запустите сервисы:

   ```bash
   docker compose up --build -d
   ```

3. Проверьте backend:

   ```text
   http://localhost:8000/health/
   ```

4. Заполните стенд демо-данными:

   ```bash
   docker compose exec backend python manage.py create_demo_data
   ```

## Демо-учетные записи

- `admin / admin123`
- `teacher / teacher123`
- `student / student123`

## Основные возможности

- Пользователи, роли, авторизация и временная блокировка после неудачных входов.
- Учебные справочники: группы, дисциплины, периоды, студенты, преподаватели, назначения.
- Журнал оценок.
- Журнал посещаемости.
- Кабинет студента.
- Кабинет преподавателя.
- Кабинет администратора.
- Отчеты по успеваемости и посещаемости в `csv`, `xlsx`, `pdf`.
- Напоминания преподавателям о закрытии учебного периода.
- Журнал аудита и `X-Request-ID` для трассировки запросов.

## Документация

- `docs/deployment.md` - развертывание и эксплуатационный запуск.
- `docs/testing.md` - автоматические и ручные проверки.
- `docs/acceptance-test-cases.md` - приемочные сценарии.
- `docs/admin-guide.md` - руководство администратора.
- `docs/user-guide.md` - руководство студента и преподавателя.
- `docs/db-admin-guide.md` - резервное копирование, восстановление и миграции БД.

## Тесты

```bash
docker compose run --rm backend pytest apps/users/tests apps/education/tests apps/journal/tests apps/reports/tests apps/notifications/tests apps/audit/tests apps/common/tests -q
```

## Структура

```text
backend/
  apps/
    audit/
    common/
    education/
    journal/
    notifications/
    reports/
    users/
  config/
    settings/
docker-compose.yml
docs/
```
