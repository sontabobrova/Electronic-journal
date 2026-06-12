# Нагрузочное тестирование

Нагрузочные сценарии реализованы через Locust.

## Подготовка данных

Перед запуском нужен большой demo-набор:

```bash
docker compose exec backend python manage.py create_demo_data --reset --full
```

## Запуск web-интерфейса Locust

```bash
docker compose --profile loadtest up loadtest
```

Открыть:

```text
http://localhost:8089/
```

Если проект запущен на сервере или виртуальной машине:

```text
http://<адрес-сервера>:8089/
```

В форме Locust можно указать:

- Number of users: `50`
- Spawn rate: `5`
- Host: `http://backend:8000`

Для скриншота в отчет используйте вкладки `Statistics` и `Charts`.

## Headless-прогон с HTML-отчетом

```bash
docker compose run --rm loadtest -f /mnt/locust/locustfile.py --host http://backend:8000 --headless -u 50 -r 5 -t 3m --html /mnt/locust/reports/loadtest-report.html --csv /mnt/locust/reports/loadtest
```

Результаты появятся в:

```text
load_tests/reports/
```

## Профиль нагрузки

Сценарии используют три роли:

- `AdminApiUser` - админские сводки, пользователи, справочники, аудит, отчеты.
- `TeacherApiUser` - кабинет преподавателя, журнал оценок, занятия, посещаемость, уведомления.
- `StudentApiUser` - кабинет студента, оценки, посещаемость.

По умолчанию сценарий не создает новые отчеты и работает в read-only режиме. Чтобы включить генерацию отчетов:

```bash
LOADTEST_ENABLE_WRITES=true docker compose --profile loadtest up loadtest
```

Генерация отчетов создает файлы в `backend/media/reports/`, поэтому для демонстрационного скриншота обычно достаточно read-only режима.
