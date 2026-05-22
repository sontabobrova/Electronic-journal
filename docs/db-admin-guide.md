# Руководство по базе данных

Актуализировано: 23.05.2026.

Проект использует PostgreSQL 16. В Docker Compose база запускается сервисом `db`, данные хранятся в volume `postgres_data`.

## Подключение

Значения по умолчанию из `.env.example`:

| Параметр | Значение |
| --- | --- |
| База | `electronic_journal` |
| Пользователь | `journal_user` |
| Пароль | `journal_password` |
| Host внутри Docker | `db` |
| Внешний порт | `5432` |

Интерактивная консоль:

```bash
docker compose exec db psql -U journal_user -d electronic_journal
```

Если значения изменены в `.env`, используйте актуальные `POSTGRES_USER` и `POSTGRES_DB`.

## Резервное копирование

Создать дамп:

```bash
docker compose exec db pg_dump -U journal_user electronic_journal > backup.sql
```

Для сжатого дампа:

```bash
docker compose exec db pg_dump -U journal_user -Fc electronic_journal > backup.dump
```

Рекомендации:

- хранить дампы вне сервера приложения;
- хранить несколько последних копий;
- регулярно проверять восстановление на отдельном окружении;
- контролировать свободное место на диске.

## Восстановление из SQL-дампа

Остановить backend и фоновые задачи:

```bash
docker compose stop backend celery-worker celery-beat
```

Восстановить:

```bash
docker compose exec -T db psql -U journal_user -d electronic_journal < backup.sql
```

Запустить сервисы:

```bash
docker compose up -d backend celery-worker celery-beat
```

## Восстановление из custom dump

```bash
docker compose stop backend celery-worker celery-beat
docker compose exec -T db pg_restore -U journal_user -d electronic_journal --clean --if-exists < backup.dump
docker compose up -d backend celery-worker celery-beat
```

## Миграции Django

Применить миграции:

```bash
docker compose exec backend python manage.py migrate
```

Проверить, что миграции не забыты:

```bash
docker compose exec backend python manage.py makemigrations --check --dry-run
```

Показать список миграций:

```bash
docker compose exec backend python manage.py showmigrations
```

## Основные доменные таблицы

- `users_user` - пользователи и роли.
- `education_academicgroup` - учебные группы.
- `education_subject` - дисциплины.
- `education_academicperiod` - учебные периоды.
- `education_studentprofile` - профили студентов.
- `education_teacherprofile` - профили преподавателей.
- `education_teachingassignment` - назначения преподавателей.
- `journal_gradework` - работы журнала.
- `journal_grade` - оценки.
- `journal_classsession` - занятия.
- `journal_attendancerecord` - посещаемость.
- `reports_reportrequest` - заявки на отчеты.
- `notifications_notification` - уведомления.
- `audit_auditlog` - аудит.

## Очистка локального стенда

Полностью удалить контейнеры и volumes:

```bash
docker compose down -v
```

После этого данные PostgreSQL будут удалены. Для восстановления нужно снова поднять сервисы, применить миграции и выполнить `create_demo_data` или восстановить дамп.
