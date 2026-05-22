# Развертывание и эксплуатационный запуск

Актуализировано: 23.05.2026.

Документ описывает локальный запуск проекта через Docker Compose и базовые действия для эксплуатации стенда.

## Требования

- Docker.
- Docker Compose.
- Свободные порты:
  - `3000` - frontend;
  - `8000` - backend;
  - `5432` - PostgreSQL;
  - `6379` - Redis.
- Доступ на чтение и запись к каталогу проекта.

## Состав Docker Compose

| Сервис | Назначение |
| --- | --- |
| `frontend` | React/Vite клиентская часть |
| `backend` | Django REST API |
| `db` | PostgreSQL 16 |
| `redis` | Redis для Celery |
| `celery-worker` | выполнение фоновых задач |
| `celery-beat` | запуск задач по расписанию |

Volumes:

- `postgres_data` - данные PostgreSQL;
- `redis_data` - данные Redis;
- `frontend_node_modules` - зависимости frontend внутри контейнера.

## Первый запуск

1. Создать `.env`:

   ```bash
   cp .env.example .env
   ```

2. Собрать и запустить сервисы:

   ```bash
   docker compose up --build -d
   ```

3. Проверить контейнеры:

   ```bash
   docker compose ps
   ```

4. Проверить backend:

   ```text
   http://localhost:8000/health/
   ```

   Ожидаемый ответ:

   ```json
   {"status":"ok"}
   ```

5. Открыть frontend:

   ```text
   http://localhost:3000/
   ```

## Миграции

При старте `backend` выполняет:

```bash
python manage.py migrate
```

Ручной запуск:

```bash
docker compose exec backend python manage.py migrate
```

Проверка, что миграции не забыты:

```bash
docker compose exec backend python manage.py makemigrations --check --dry-run
```

## Демо-данные

Создание приемочного набора данных:

```bash
docker compose exec backend python manage.py create_demo_data
```

Создание большого демонстрационного набора с предварительной очисткой старых demo-записей:

```bash
docker compose exec backend python manage.py create_demo_data --reset --full
```

Команда создает:

- администратора;
- преподавателя;
- студента;
- группу;
- дисциплину;
- учебный период;
- назначение преподавателя;
- работу журнала;
- оценку;
- занятие;
- запись посещаемости;
- напоминание преподавателю.

В режиме `--full` создается расширенный стенд:

- 67 demo-пользователей;
- 6 групп;
- 10 дисциплин;
- 3 учебных периода;
- 42 назначения преподавателей;
- 252 работы журнала;
- 2520 оценок;
- 336 занятий;
- 3360 записей посещаемости;
- персональные уведомления преподавателей.

Команда идемпотентна: повторный запуск не должен создавать дубликаты. Флаг `--reset` удаляет только известные demo-записи, созданные этой командой, и не очищает всю базу.

Учетные записи:

| Роль | Логин | Пароль |
| --- | --- | --- |
| Администратор | `admin` | `admin123` |
| Преподаватель | `teacher` | `teacher123` |
| Студент | `student` | `student123` |

Дополнительные учетные записи в режиме `--full`:

- `demo_teacher_01` ... `demo_teacher_05` / `teacher123`;
- `demo_student_001` ... `demo_student_059` / `student123`.

## Основные адреса

- Frontend: `http://localhost:3000/`
- Backend healthcheck: `http://localhost:8000/health/`
- Django admin: `http://localhost:8000/admin/`
- API root: `http://localhost:8000/api/`

## Полезные команды

Логи:

```bash
docker compose logs -f frontend
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose logs -f celery-beat
```

Перезапуск отдельных сервисов:

```bash
docker compose restart frontend
docker compose restart backend
docker compose restart celery-worker celery-beat
```

Пересоздание demo-стенда:

```bash
docker compose exec backend python manage.py create_demo_data --reset --full
```

Остановка:

```bash
docker compose down
```

Остановка с удалением volumes:

```bash
docker compose down -v
```

Использовать осторожно: эта команда удалит данные PostgreSQL и Redis.

## Переменные окружения

Основные переменные в `.env`:

| Переменная | Назначение |
| --- | --- |
| `DJANGO_ENV` | режим настроек |
| `DJANGO_SECRET_KEY` | секретный ключ |
| `DJANGO_DEBUG` | debug-режим |
| `DJANGO_ALLOWED_HOSTS` | разрешенные хосты |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | доверенные origins для CSRF |
| `POSTGRES_DB` | база PostgreSQL |
| `POSTGRES_USER` | пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | пароль PostgreSQL |
| `POSTGRES_HOST` | host PostgreSQL |
| `POSTGRES_PORT` | порт PostgreSQL |
| `REDIS_URL` | Redis URL |
| `CORS_ALLOWED_ORIGINS` | разрешенные origins frontend |
| `VITE_API_BASE_URL` | URL backend для frontend |

## Production-заметки

Перед промышленной эксплуатацией нужно:

- заменить `DJANGO_SECRET_KEY`;
- установить `DJANGO_DEBUG=False`;
- ограничить `DJANGO_ALLOWED_HOSTS`;
- ограничить `CORS_ALLOWED_ORIGINS`;
- настроить HTTPS на внешнем reverse proxy;
- настроить хранение и отдачу `MEDIA_ROOT`;
- настроить регулярные резервные копии PostgreSQL;
- настроить мониторинг контейнеров, диска и фоновых задач;
- заменить dev-команду `runserver` на production WSGI/ASGI запуск, например Gunicorn.
