# Тестирование

Актуализировано: 22.05.2026.

## Автоматические проверки

### Backend

Полный набор backend-тестов:

```bash
docker compose exec backend pytest apps/users/tests apps/education/tests apps/journal/tests apps/reports/tests apps/notifications/tests apps/audit/tests apps/common/tests -q
```

Проверка Django-конфигурации:

```bash
docker compose exec backend python manage.py check
```

Проверка миграций:

```bash
docker compose exec backend python manage.py makemigrations --check --dry-run
```

### Frontend

Линт:

```bash
docker compose exec frontend npm run lint
```

Production-сборка:

```bash
docker compose exec frontend npm run build
```

Если frontend запускается локально без Docker:

```bash
cd frontend
npm run lint
npm run build
```

## Что покрыто backend-тестами

- Авторизация и получение текущего пользователя.
- Блокировка после трех неудачных попыток входа.
- CRUD пользователей администратором.
- Сброс пароля.
- Автосоздание профиля преподавателя при создании или смене роли пользователя.
- Учебные справочники.
- Профили студентов и преподавателей.
- Назначения преподавателей.
- Журнал оценок.
- Журнал посещаемости.
- Кабинет студента.
- Кабинет преподавателя.
- Отчеты `csv`, `xlsx`, `pdf`.
- Уведомления и напоминания о закрытии периода.
- Персональная отметка уведомлений прочитанными.
- Аудит действий.
- Команда `create_demo_data`.

## Ручная приемка

1. Запустить проект по [deployment.md](deployment.md).
2. Выполнить:

   ```bash
   docker compose exec backend python manage.py create_demo_data
   ```

3. Открыть `http://localhost:3000/`.
4. Проверить вход под ролями:
   - `admin / admin123`;
   - `teacher / teacher123`;
   - `student / student123`.
5. Пройти сценарии из [acceptance-test-cases.md](acceptance-test-cases.md).
6. Проверить, что действия администратора и преподавателя появляются в журнале аудита.
7. Проверить формирование отчетов и скачивание файлов.
8. Проверить, что преподаватель не видит чужие назначения, а студент не видит чужие оценки и посещаемость.

## Минимальный smoke-test после изменений

```bash
docker compose exec backend pytest apps/users/tests/test_auth.py apps/education/tests/test_education_api.py -q
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
```

Дополнительно открыть в браузере:

- `/admin` - форма пользователя и учебный процесс;
- `/teacher` - работы, оценки, занятия и посещаемость;
- `/student` - личные оценки и посещаемость;
- `/reports` - генерация отчета;
- `/notifications` - уведомления администратора или преподавателя.
