"""
Конфигурация Gunicorn для ISPmanager
"""
import multiprocessing
import os

# Количество воркеров (обычно 2 * CPU cores + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# Адрес и порт (ISPmanager обычно настраивает это автоматически)
bind = "0.0.0.0:8000"

# Тип воркера (uvicorn для FastAPI)
worker_class = "uvicorn.workers.UvicornWorker"

# Таймауты
timeout = 120
keepalive = 5

# Логирование
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"

# Перезагрузка при изменении кода (отключить в продакшене)
reload = False

# Имя приложения
wsgi_app = "main:app"

