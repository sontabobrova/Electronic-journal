# Тестирование

## Автоматические тесты

Запуск всего набора тестов в Docker:

```bash
docker compose run --rm backend pytest apps/users/tests apps/education/tests apps/journal/tests apps/reports/tests apps/notifications/tests apps/audit/tests apps/common/tests -q
```

Проверка Django-конфигурации:

```bash
docker compose run --rm backend python manage.py check
```

Проверка миграций:

```bash
docker compose run --rm backend python manage.py makemigrations --check --dry-run
```

## Что покрыто тестами

- Авторизация, роли, ограничения доступа и блокировка входа.
- CRUD пользователей и сброс пароля администратором.
- Учебные справочники: группы, дисциплины, периоды, студенты, преподаватели, назначения.
- Журнал оценок и разграничение доступа преподавателя/студента.
- Журнал посещаемости и разграничение доступа.
- Кабинеты студента и преподавателя.
- Отчеты CSV/XLSX/PDF.
- Напоминания о закрытии периода.
- Аудит действий.
- Команда приемочных демо-данных.

## Ручная приемка

1. Запустить проект по `docs/deployment.md`.
2. Выполнить `create_demo_data`.
3. Авторизоваться под каждой ролью через `POST /api/auth/login/`.
4. Пройти сценарии из `docs/acceptance-test-cases.md`.
5. Проверить, что действия отражаются в `/api/audit/logs/`.
