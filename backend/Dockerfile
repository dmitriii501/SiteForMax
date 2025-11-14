# Dockerfile для FastAPI бэкенда
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директории для базы данных
RUN mkdir -p /app/data

# Переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./data/max_personal_effect.db

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]

