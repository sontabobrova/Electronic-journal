# Нагрузочное тестирование

Актуализировано: 10.06.2026.

Нагрузочное тестирование реализовано через Locust. Web-интерфейс Locust дает таблицы и графики, которые можно вставить скриншотом в отчет.

## Что проверяется

Сценарий нагружает REST API под тремя ролями:

- администратор;
- преподаватель;
- студент.

Проверяются основные пользовательские потоки:

- вход через `/api/auth/login/`;
- кабинет администратора;
- учебные справочники;
- кабинет преподавателя;
- работы журнала, оценки, занятия, посещаемость;
- кабинет студента;
- уведомления;
- список отчетов.

По умолчанию сценарий работает в read-only режиме. Он не создает новые отчеты и не засоряет базу. Генерацию отчетов можно включить отдельно.

## Подготовка стенда

1. Запустить проект:

   ```bash
   docker compose up -d
   ```

2. Создать большой demo-набор:

   ```bash
   docker compose exec backend python manage.py create_demo_data --reset --full
   ```

## Запуск Locust UI

```bash
docker compose --profile loadtest up loadtest
```

Открыть Locust:

```text
http://localhost:8089/
```

Если стенд запущен на сервере или виртуальной машине:

```text
http://<адрес-сервера>:8089/
```

Рекомендуемые параметры для демонстрационного скриншота:

| Поле | Значение |
| --- | --- |
| Number of users | `50` |
| Spawn rate | `5` |
| Host | `http://backend:8000` |

После запуска дождитесь 3-5 минут стабильной работы и сделайте скриншот вкладок:

- `Statistics`;
- `Charts`;
- при наличии ошибок: `Failures`.

## Headless-прогон с HTML-отчетом

```bash
docker compose run --rm loadtest -f /mnt/locust/locustfile.py --host http://backend:8000 --headless -u 50 -r 5 -t 3m --html /mnt/locust/reports/loadtest-report.html --csv /mnt/locust/reports/loadtest
```

Файлы появятся в:

```text
load_tests/reports/
```

Папка `load_tests/reports/` не коммитит результаты, кроме `.gitkeep`.

## Генерация отчетов во время нагрузки

По умолчанию:

```env
LOADTEST_ENABLE_WRITES=false
```

Чтобы включить POST-запросы генерации отчетов:

```bash
LOADTEST_ENABLE_WRITES=true docker compose --profile loadtest up loadtest
```

Этот режим создает файлы в `backend/media/reports/`. Для обычного скриншота производительности read-only режима достаточно.

## Ограничения интерпретации

По умолчанию backend в Docker Compose запускается через Django `runserver`. Это подходит для демонстрации и поиска грубых проблем, но не является production WSGI/ASGI-сервером. Для итоговых производственных цифр нужно запускать backend через production-сервер, например Gunicorn, и тестировать на окружении, близком к релизному.
