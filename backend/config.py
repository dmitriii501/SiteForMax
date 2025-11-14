"""
Конфигурация приложения
"""
import os
from pathlib import Path

# Базовый путь к приложению
BASE_DIR = Path(__file__).parent.resolve()

# Загрузка переменных окружения
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv не обязателен

# Настройки базы данных
DB_DIR = os.getenv("DB_DIR", str(BASE_DIR))
DATABASE_URL = os.path.join(DB_DIR, "max_personal_effect.db")

# CORS настройки
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
if ALLOWED_ORIGINS != "*":
    ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS.split(",")]

# Режим отладки
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Секретный ключ (для будущего использования)
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")

# Настройки сервера
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

