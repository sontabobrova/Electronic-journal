# Электронный журнал

Автоматизированная информационная система для ведения учебного журнала: пользователи и роли, учебные справочники, оценки, посещаемость, кабинеты студента и преподавателя, администрирование, отчеты, уведомления и аудит действий.

Проект реализован как web-приложение с Python backend и React frontend. Backend отдает REST API, frontend работает с ним через токен авторизации. Сервисы поднимаются через Docker Compose.


## Содержание

- [Быстрый старт](#быстрый-старт)
- [Демо-доступ](#демо-доступ)
- [Функционал](#функционал)
- [Роли и права доступа](#роли-и-права-доступа)
- [Как работает система](#как-работает-система)
- [Технологический стек](#технологический-стек)
- [Структура проекта](#структура-проекта)
- [Основные API-маршруты](#основные-api-маршруты)
- [Frontend-маршруты](#frontend-маршруты)
- [Команды разработки](#команды-разработки)
- [Переменные окружения](#переменные-окружения)
- [Документация](#документация)

## Быстрый старт

Требования:

- Docker;
- Docker Compose;
- свободные порты `3000`, `8000`, `5432`, `6379`.

Запуск:

```bash
cp .env.example .env
docker compose up --build -d
```

Для демонстрации с доступом с других машин можно взять отдельный файл:

```bash
cp .env.demo .env
docker compose up --build -d
```

Для релизной среды используйте шаблон:

```bash
cp .env.release .env
```

Перед запуском релиза обязательно замените домены, `DJANGO_SECRET_KEY` и пароль PostgreSQL.

Проверка backend:

```text
http://localhost:8000/health/
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

Открыть интерфейс:

```text
http://localhost:3000/
```

Если проект запущен на сервере или виртуальной машине, открывайте frontend по адресу этого сервера:

```text
http://<адрес-сервера>:3000/
```

В `.env.demo` для этого используется автоматическое определение host:

```env
DJANGO_ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=True
VITE_API_BASE_URL=auto
```

Frontend сам построит адрес API как `http://<адрес-сервера>:8000`. После изменения `.env` пересоздайте контейнеры:

```bash
docker compose up -d --force-recreate backend frontend
```

Заполнить демо-данные:

```bash
docker compose exec backend python manage.py create_demo_data
```

Команда демо-данных идемпотентна: ее можно запускать повторно, основные записи не должны дублироваться.

Для расширенного демонстрационного стенда:

```bash
docker compose exec backend python manage.py create_demo_data --reset --full
```

Эта команда воспроизводимо создает большой набор данных для показа системы: пользователей, группы, дисциплины, периоды, назначения, работы журнала, оценки, занятия, посещаемость и уведомления. Очистка `--reset` удаляет только данные, созданные demo-командой.

## Демо-доступ

После выполнения `create_demo_data` доступны учетные записи:

| Роль | Логин | Пароль |
| --- | --- | --- |
| Администратор | `admin` | `admin123` |
| Преподаватель | `teacher` | `teacher123` |
| Студент | `student` | `student123` |

В режиме `--full` дополнительно создаются:

- `demo_teacher_01` ... `demo_teacher_05` с паролем `teacher123`;
- `demo_student_001` ... `demo_student_059` с паролем `student123`.

## Функционал

### Авторизация и пользователи

- Вход по логину и паролю.
- Token-based авторизация через DRF token.
- Восстановление текущей сессии frontend после перезагрузки страницы.
- Выход из системы с удалением токена.
- Роли: `admin`, `teacher`, `student`.
- Блокировка пользователя после трех неудачных попыток входа.
- Срок действия доступа через поле `access_expires_at`.
- Административный CRUD пользователей.
- Сброс пароля администратором.
- При создании/редактировании пользователя в кабинете администратора показываются дополнительные поля профиля:
  - для студента: номер студента, группа, дата зачисления;
  - для преподавателя: табельный номер, должность.
- Для преподавателей профиль создается автоматически при назначении роли `teacher`, чтобы пользователь сразу был доступен в назначениях.

### Учебные сущности

- Учебные группы.
- Дисциплины.
- Учебные периоды.
- Профили студентов.
- Профили преподавателей.
- Назначения преподавателей на дисциплину, группу и учебный период.
- Создание, редактирование и удаление учебных справочников через кабинет администратора.

### Журнал оценок

- Работы журнала: работа на занятии, домашняя работа, контрольная работа, экзамен, другое.
- Максимальный балл и вес работы.
- Выставление, редактирование и удаление оценок.
- Контроль, что оценка не превышает максимальный балл работы.
- Контроль, что студент относится к группе назначения.
- Преподаватель работает только со своими назначениями.

### Журнал посещаемости

- Занятия по назначению преподавателя.
- Тема и дата занятия.
- Отметки посещаемости:
  - присутствовал;
  - отсутствовал;
  - уважительная причина;
  - опоздал.
- Создание, редактирование и удаление занятий и записей посещаемости.
- Контроль, что студент относится к группе занятия.

### Кабинет студента

- Личная сводка.
- Средний балл.
- Список оценок.
- Сводка посещаемости.
- Список посещений.
- Доступ только к собственным данным.

### Кабинет преподавателя

- Профиль преподавателя.
- Сводка по назначениям.
- Студенты назначенных групп.
- Работы журнала.
- Оценки.
- Занятия.
- Посещаемость.
- Создание, редактирование и удаление записей журнала в рамках своих назначений.

### Кабинет администратора

- Сводки по пользователям, учебным сущностям и журналу.
- Управление пользователями и профилями.
- Управление группами, дисциплинами, периодами и назначениями.
- Просмотр журнала аудита.
- Разделение рабочей области на вкладки: пользователи, учебный процесс, аудит.

### Отчеты и экспорт

- Формирование отчетов по успеваемости.
- Формирование отчетов по посещаемости.
- Форматы экспорта:
  - `csv`;
  - `xlsx`;
  - `pdf`.
- Фильтры по группе, дисциплине, периоду и студенту.
- Администратор может формировать отчеты по всем данным.
- Преподаватель формирует отчеты только по своим назначениям.
- Сформированные файлы сохраняются в `MEDIA_ROOT` и доступны по `download_url`.

### Уведомления

- Уведомления привязаны к конкретному пользователю-получателю.
- Отметка о прочтении хранится у конкретного уведомления конкретного пользователя.
- Преподаватели получают напоминание за 3 дня до окончания активного учебного периода.
- Уведомления генерируются фоновой задачей Celery Beat.
- В интерфейсе уведомления доступны администратору и преподавателю.

### Логирование, аудит и безопасность

- Аудит входов, неудачных входов, выходов, изменений пользователей, оценок, посещаемости и отчетов.
- `X-Request-ID` в ответах для трассировки запросов.
- Хранение IP-адреса и user-agent в аудите.
- Ролевые permissions на backend.
- Защита от доступа к чужим данным для студентов и преподавателей.
- CORS-настройки для frontend.

## Роли и права доступа

| Раздел | Администратор | Преподаватель | Студент |
| --- | --- | --- | --- |
| Пользователи | полный доступ | нет | нет |
| Учебные справочники | полный доступ | чтение нужных данных | чтение своих данных |
| Назначения | полный доступ | только свои | нет |
| Оценки | полный доступ | свои назначения | только свои оценки |
| Посещаемость | полный доступ | свои занятия | только свои посещения |
| Отчеты | все данные | свои назначения | нет |
| Уведомления | свои уведомления и обзор | свои уведомления | скрыто в интерфейсе |
| Аудит | просмотр | нет | нет |

## Как работает система

1. Пользователь входит через `/api/auth/login/`.
2. Backend возвращает `token` и данные пользователя.
3. Frontend сохраняет токен в `localStorage` и добавляет заголовок `Authorization: Token <token>` ко всем API-запросам.
4. Навигация frontend строится по роли пользователя.
5. Backend проверяет права доступа на каждом API:
   - администратор управляет системой;
   - преподаватель ограничен своими назначениями;
   - студент ограничен личным профилем.
6. Учебный журнал строится вокруг `TeachingAssignment`: преподаватель + дисциплина + группа + период.
7. Работы, оценки, занятия и посещаемость привязаны к назначению.
8. Отчеты собираются из журналов и сохраняются как файлы.
9. Celery Beat ежедневно запускает задачу напоминаний о закрытии периода.
10. Middleware аудита добавляет request id и сохраняет контекст действий.

## Технологический стек

### Backend

- Python 3.12.
- Django 5.
- Django REST Framework.
- DRF Token Authentication.
- PostgreSQL 16.
- Redis.
- Celery и Celery Beat.
- django-cors-headers.
- OpenPyXL для XLSX.
- ReportLab для PDF.
- Pytest и pytest-django.

### Frontend

- React 18.
- TypeScript.
- Vite.
- React Router.
- TanStack Query.
- Axios.
- Lucide React.
- ESLint.

### Инфраструктура

- Docker Compose.
- Сервисы: `frontend`, `backend`, `db`, `redis`, `celery-worker`, `celery-beat`.
- Volumes: `postgres_data`, `redis_data`, `frontend_node_modules`.

## Структура проекта

```text
.
├── backend/
│   ├── apps/
│   │   ├── audit/          # аудит действий и request id
│   │   ├── common/         # общие команды, демо-данные
│   │   ├── education/      # группы, дисциплины, периоды, профили, назначения
│   │   ├── journal/        # оценки, работы, занятия, посещаемость, кабинеты
│   │   ├── notifications/  # уведомления и фоновые напоминания
│   │   ├── reports/        # отчеты и экспорт файлов
│   │   └── users/          # пользователи, роли, авторизация, админ-сводки
│   ├── config/
│   │   ├── settings/       # local, production, test настройки
│   │   ├── urls.py         # корневая маршрутизация API
│   │   └── celery.py       # Celery app
│   ├── requirements/
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── api/            # axios-клиенты API
│   │   ├── auth/           # контекст авторизации и protected routes
│   │   ├── components/     # общие UI-компоненты
│   │   ├── layouts/        # общий layout приложения
│   │   └── pages/          # страницы кабинетов, отчетов, уведомлений
│   ├── package.json
│   └── vite.config.ts
├── docs/                   # проектная документация
├── docker-compose.yml
├── .env.example
└── README.md
```

## Основные API-маршруты

### Служебные

- `GET /health/` - healthcheck.
- `/admin/` - Django admin.

### Авторизация и пользователи

- `POST /api/auth/login/` - вход.
- `POST /api/auth/logout/` - выход.
- `GET /api/auth/me/` - текущий пользователь.
- `/api/users/` - CRUD пользователей.
- `POST /api/users/{id}/reset-password/` - сброс пароля.
- `GET /api/admin-cabinet/dashboard/` - сводка администратора.
- `GET /api/admin-cabinet/users-summary/` - сводка пользователей.
- `GET /api/admin-cabinet/education-summary/` - сводка учебных сущностей.
- `GET /api/admin-cabinet/journal-summary/` - сводка журнала.

### Учебный процесс

- `/api/education/groups/` - группы.
- `/api/education/subjects/` - дисциплины.
- `/api/education/periods/` - учебные периоды.
- `/api/education/students/` - профили студентов.
- `/api/education/teachers/` - профили преподавателей.
- `/api/education/teaching-assignments/` - назначения преподавателей.

### Журнал

- `/api/journal/grade-works/` - работы журнала.
- `/api/journal/grades/` - оценки.
- `/api/journal/class-sessions/` - занятия.
- `/api/journal/attendance-records/` - посещаемость.
- `GET /api/journal/student/dashboard/` - кабинет студента, сводка.
- `GET /api/journal/student/grades/` - оценки студента.
- `GET /api/journal/student/attendance/` - посещаемость студента.
- `GET /api/journal/teacher/dashboard/` - кабинет преподавателя, сводка.
- `GET /api/journal/teacher/assignments/` - назначения преподавателя.
- `GET /api/journal/teacher/students/` - студенты групп преподавателя.
- `GET /api/journal/teacher/grade-works/` - работы преподавателя.
- `GET /api/journal/teacher/grades/` - оценки преподавателя.
- `GET /api/journal/teacher/class-sessions/` - занятия преподавателя.
- `GET /api/journal/teacher/attendance/` - посещаемость преподавателя.

### Отчеты, уведомления и аудит

- `/api/reports/requests/` - заявки на отчеты.
- `POST /api/reports/requests/generate/` - сформировать отчет.
- `/api/notifications/notifications/` - уведомления пользователя.
- `POST /api/notifications/notifications/{id}/mark-read/` - отметить уведомление прочитанным.
- `/api/audit/logs/` - журнал аудита.

## Frontend-маршруты

- `/login` - вход.
- `/` - обзор и быстрые переходы по доступным разделам.
- `/student` - кабинет студента.
- `/teacher` - кабинет преподавателя.
- `/admin` - кабинет администратора.
- `/reports` - отчеты.
- `/notifications` - уведомления.

## Команды разработки

### Docker

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f celery-worker
docker compose down
```

### Backend

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py create_demo_data
docker compose exec backend python manage.py create_demo_data --reset --full
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py check
docker compose exec backend pytest -q
```

Полный целевой набор тестов:

```bash
docker compose exec backend pytest apps/users/tests apps/education/tests apps/journal/tests apps/reports/tests apps/notifications/tests apps/audit/tests apps/common/tests -q
```

### Frontend

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
```

Локально без Docker:

```bash
cd frontend
npm install
npm run dev
```

## Переменные окружения

Основной файл окружения создается из `.env.example`.

В проекте есть три шаблона окружения:

- `.env.example` - локальный запуск на той же машине.
- `.env.demo` - демонстрационный запуск с доступом с других машин без привязки к конкретному IP.
- `.env.release` - релизный шаблон с production-настройками, доменом сервера и placeholder-секретами.

| Переменная | Назначение |
| --- | --- |
| `DJANGO_ENV` | режим настроек Django: `local`, `production`, `test` |
| `DJANGO_SECRET_KEY` | секретный ключ Django |
| `DJANGO_DEBUG` | debug-режим |
| `DJANGO_ALLOWED_HOSTS` | разрешенные хосты |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | доверенные origins для CSRF |
| `POSTGRES_DB` | имя базы данных |
| `POSTGRES_USER` | пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | пароль PostgreSQL |
| `POSTGRES_HOST` | host PostgreSQL |
| `POSTGRES_PORT` | порт PostgreSQL |
| `REDIS_URL` | URL Redis для Celery |
| `CORS_ALLOWED_ORIGINS` | разрешенные frontend origins |
| `VITE_API_BASE_URL` | базовый URL backend для frontend |

Для production нужно заменить `DJANGO_SECRET_KEY`, установить `DJANGO_DEBUG=False`, ограничить `DJANGO_ALLOWED_HOSTS` и `CORS_ALLOWED_ORIGINS`, а также настроить постоянное хранение media-файлов и резервное копирование PostgreSQL.

## Документация

Актуальные документы находятся в папке `docs/`:

- [docs/README.md](docs/README.md) - индекс документации.
- [docs/deployment.md](docs/deployment.md) - развертывание, эксплуатационный запуск и сервисы.
- [docs/testing.md](docs/testing.md) - автоматические проверки, ручная приемка и тестовые зоны.
- [docs/acceptance-test-cases.md](docs/acceptance-test-cases.md) - приемочные сценарии по ролям.
- [docs/admin-guide.md](docs/admin-guide.md) - руководство администратора.
- [docs/user-guide.md](docs/user-guide.md) - руководство студента и преподавателя.
- [docs/db-admin-guide.md](docs/db-admin-guide.md) - резервное копирование, восстановление и миграции БД.

## Текущее состояние

Проект готов к локальной приемке через Docker Compose. Основные backend-тесты и frontend-сборка должны проходить командами из раздела [Команды разработки](#команды-разработки).
