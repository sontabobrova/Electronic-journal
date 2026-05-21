# Развертывание и эксплуатационный запуск

## Требования

- Docker и Docker Compose.
- Свободные порты `8000`, `5432`, `6379`, если значения не переопределены в `.env`.
- Доступ к каталогу проекта и право создавать Docker volumes.

## Первый запуск

1. Создайте файл окружения:

   ```bash
   cp .env.example .env
   ```

2. Запустите сервисы:

   ```bash
   docker compose up --build -d
   ```

3. Проверьте состояние контейнеров:

   ```bash
   docker compose ps
   ```

4. Проверьте backend:

   ```text
   http://localhost:8000/health/
   ```

   Ожидаемый ответ:

   ```json
   {"status":"ok"}
   ```

## Демо-данные для приемки

Команда создает администратора, преподавателя, студента, группу, дисциплину, учебный период, назначение, оценку, посещаемость и напоминание. Команду можно запускать повторно.

```bash
docker compose exec backend python manage.py create_demo_data
```

Учетные записи:

- `admin / admin123`
- `teacher / teacher123`
- `student / student123`

## Сервисы

- `backend` - Django REST API.
- `db` - PostgreSQL.
- `redis` - брокер Celery.
- `celery-worker` - выполнение фоновых задач.
- `celery-beat` - расписание фоновых задач.

## Полезные команды

```bash
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend pytest -q
docker compose down
```

## Переменные окружения

Основные параметры задаются в `.env`:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `REDIS_URL`

Для промышленной среды нужно задать собственный `DJANGO_SECRET_KEY`, отключить `DJANGO_DEBUG` и ограничить `DJANGO_ALLOWED_HOSTS`.
