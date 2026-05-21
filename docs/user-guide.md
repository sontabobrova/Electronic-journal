# Руководство пользователя

## Студент

Студент работает только со своими данными.

Доступные разделы:

- `/api/journal/student/dashboard/` - личная сводка, средний балл и посещаемость.
- `/api/journal/student/grades/` - оценки.
- `/api/journal/student/attendance/` - посещаемость.
- `/api/notifications/notifications/` - личные уведомления.

Студент не может изменять оценки, занятия и посещаемость.

## Преподаватель

Преподаватель работает с группами и дисциплинами, назначенными администратором.

Доступные разделы:

- `/api/journal/teacher/dashboard/` - сводка преподавателя.
- `/api/journal/teacher/assignments/` - назначения.
- `/api/journal/teacher/students/` - студенты назначенных групп.
- `/api/journal/teacher/grade-works/` - работы в журнале оценок.
- `/api/journal/teacher/grades/` - оценки.
- `/api/journal/teacher/class-sessions/` - занятия.
- `/api/journal/teacher/attendance/` - посещаемость.
- `/api/notifications/notifications/` - уведомления.

Преподаватель видит и меняет только данные по своим назначениям.

## Вход и выход

```text
POST /api/auth/login/
POST /api/auth/logout/
GET /api/auth/me/
```

После входа используйте полученный токен в заголовке:

```text
Authorization: Token <token>
```
