# MaxPersonalEffect Backend API

Бэкенд для мини-приложения MaxPersonalEffect на FastAPI.

## Установка

1. Установите зависимости:
```bash
python -m pip install -r requirements.txt
```

**Примечание для Windows:** Если команда `pip` не работает, используйте `python -m pip` вместо `pip`.

## Запуск

```bash
python main.py
```

Или с помощью uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: `http://localhost:8000`

## Документация API

После запуска сервера документация доступна по адресам:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Структура API

### Todos (Список дел)
- `GET /api/todos/` - Получить все задачи
- `GET /api/todos/{todo_id}` - Получить задачу по ID
- `POST /api/todos/` - Создать задачу
- `PUT /api/todos/{todo_id}` - Обновить задачу
- `DELETE /api/todos/{todo_id}` - Удалить задачу

### Goals (Трекер целей)
- `GET /api/goals/` - Получить все цели
- `GET /api/goals/{goal_id}` - Получить цель по ID
- `POST /api/goals/` - Создать цель
- `PUT /api/goals/{goal_id}` - Обновить цель
- `DELETE /api/goals/{goal_id}` - Удалить цель
- `POST /api/goals/{goal_id}/subtasks` - Создать подзадачу
- `PUT /api/goals/{goal_id}/subtasks/{subtask_id}` - Обновить подзадачу
- `DELETE /api/goals/{goal_id}/subtasks/{subtask_id}` - Удалить подзадачу

### Habits (Трекер привычек)
- `GET /api/habits/` - Получить все привычки
- `GET /api/habits/{habit_id}` - Получить привычку по ID
- `POST /api/habits/` - Создать привычку
- `DELETE /api/habits/{habit_id}` - Удалить привычку
- `GET /api/habits/{habit_id}/completions` - Получить отметки выполнения
- `POST /api/habits/{habit_id}/completions/{date}` - Переключить отметку выполнения
- `GET /api/habits/water/{date}` - Получить данные о воде
- `PUT /api/habits/water/{date}` - Обновить данные о воде
- `POST /api/habits/water/{date}/add` - Добавить воду

### Mood (Трекер настроения)
- `GET /api/mood/` - Получить все записи настроения
- `GET /api/mood/{date}` - Получить запись по дате
- `POST /api/mood/{date}` - Создать/обновить запись настроения
- `PUT /api/mood/{date}` - Обновить запись настроения
- `DELETE /api/mood/{date}` - Удалить запись настроения

### Reports (Отчёты и аналитика)
- `GET /api/reports/stats` - Краткая статистика
- `GET /api/reports/tasks-chart` - Данные для графика задач
- `GET /api/reports/mood-chart` - Данные для графика настроения
- `GET /api/reports/habits-progress` - Прогресс по привычкам
- `GET /api/reports/emotions-chart` - Статистика по эмоциям
- `GET /api/reports/weekly-report` - Еженедельный отчет

## База данных

Используется SQLite база данных `max_personal_effect.db`, которая создается автоматически при первом запуске.

## CORS

CORS настроен для работы с фронтендом. В продакшене рекомендуется указать конкретные домены вместо `allow_origins=["*"]`.

