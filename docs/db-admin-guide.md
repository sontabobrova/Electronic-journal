# Руководство по базе данных

## Резервное копирование

Создать дамп PostgreSQL:

```bash
docker compose exec db pg_dump -U journal_user electronic_journal > backup.sql
```

Если имя базы или пользователя изменено в `.env`, используйте актуальные значения `POSTGRES_USER` и `POSTGRES_DB`.

## Восстановление

Остановите backend и фоновые задачи:

```bash
docker compose stop backend celery-worker celery-beat
```

Восстановите дамп:

```bash
docker compose exec -T db psql -U journal_user electronic_journal < backup.sql
```

Запустите сервисы:

```bash
docker compose up -d backend celery-worker celery-beat
```

## Миграции

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py makemigrations --check --dry-run
```

## Рекомендации

- Хранить дампы вне сервера приложения.
- Проверять восстановление на отдельном окружении.
- Ограничить доступ к PostgreSQL сетью Docker и учетными данными из `.env`.
- Для промышленной эксплуатации настроить регулярные резервные копии и мониторинг свободного места.
