"""
Конфигурация бота для Max
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "f9LHodD0cOJG8_jxMdYQq9URP1b9wuy2hAJsqicXd7ya7lqAX52Jb-6BY4nf0I6feJ6EovqJMf1FrsCOJTCf")

# URL мини-приложения
APP_URL = os.getenv("APP_URL", "https://maxpersonal-effect-frontend.onrender.com")

# URL API бэкенда
API_URL = os.getenv("API_URL", "https://maxpersonal-effect-api.onrender.com/api")

# Название бота
BOT_NAME = os.getenv("BOT_NAME", "t628_hakaton_bot")

# Ник бота
BOT_NICKNAME = os.getenv("BOT_NICKNAME", "Хакатон 628")

