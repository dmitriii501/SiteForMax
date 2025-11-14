#!/bin/bash
# Скрипт запуска для ISPmanager

# Активация виртуального окружения (если используется)
# source venv/bin/activate

# Запуск через gunicorn
gunicorn -c gunicorn_config.py main:app

# Или через uvicorn напрямую
# uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
