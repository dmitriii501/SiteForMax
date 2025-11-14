"""
Бот для Max мессенджера - интеграция с MaxPersonalEffect
"""
import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any
from config import BOT_TOKEN, APP_URL, API_URL

class MaxBot:
    """Класс для работы с Max Bot API"""
    
    def __init__(self, token: str):
        self.token = token
        self.session: Optional[aiohttp.ClientSession] = None
        self.api_url = f"https://api.max.ma/api/v1/bots/{token}"
    
    async def get_session(self):
        """Получить или создать HTTP сессию"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def send_message(self, chat_id: str, text: str, reply_markup: Optional[Dict] = None):
        """Отправить сообщение"""
        session = await self.get_session()
        data = {
            "chat_id": chat_id,
            "text": text
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        async with session.post(f"{self.api_url}/sendMessage", json=data) as response:
            return await response.json()
    
    async def answer_callback_query(self, callback_query_id: str, text: str = ""):
        """Ответить на callback query"""
        session = await self.get_session()
        data = {
            "callback_query_id": callback_query_id,
            "text": text
        }
        async with session.post(f"{self.api_url}/answerCallbackQuery", json=data) as response:
            return await response.json()
    
    async def edit_message_text(self, chat_id: str, message_id: int, text: str, reply_markup: Optional[Dict] = None):
        """Редактировать сообщение"""
        session = await self.get_session()
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        async with session.post(f"{self.api_url}/editMessageText", json=data) as response:
            return await response.json()
    
    async def get_updates(self, offset: int = 0, timeout: int = 30):
        """Получить обновления (polling)"""
        session = await self.get_session()
        params = {
            "offset": offset,
            "timeout": timeout
        }
        async with session.get(f"{self.api_url}/getUpdates", params=params) as response:
            return await response.json()
    
    async def close(self):
        """Закрыть сессию"""
        if self.session and not self.session.closed:
            await self.session.close()

# Создание экземпляра бота
bot = MaxBot(BOT_TOKEN)

async def handle_message(message: Dict[str, Any]):
    """Обработка входящего сообщения"""
    text = message.get("text", "")
    chat_id = str(message.get("chat", {}).get("id", ""))
    message_id = message.get("message_id", 0)
    
    if text.startswith("/start"):
        await start_command(chat_id)
    elif text.startswith("/help"):
        await help_command(chat_id)
    elif text.startswith("/app"):
        await app_command(chat_id)
    elif text.startswith("/todos"):
        await todos_menu(chat_id)
    elif text.startswith("/report"):
        await weekly_report(chat_id)

async def handle_callback(callback: Dict[str, Any]):
    """Обработка callback query"""
    data = callback.get("data", "")
    chat_id = str(callback.get("message", {}).get("chat", {}).get("id", ""))
    callback_id = callback.get("id", "")
    message_id = callback.get("message", {}).get("message_id", 0)
    
    if data == "view_todos":
        await todos_menu(chat_id)
    elif data == "nearest_task":
        await nearest_task(chat_id, callback_id)
    elif data == "todos_today":
        await todos_today(chat_id, callback_id)
    elif data == "todos_week":
        await todos_week(chat_id, callback_id)
    elif data == "weekly_report":
        await weekly_report(chat_id, callback_id)
    elif data == "back_to_menu":
        await start_command(chat_id)

async def start_command(chat_id: str):
    """Обработка команды /start"""
    welcome_text = """Приветствую! Я — ваш персональный помощник MaxPersonalEffect для повышения продуктивности, формирования привычек и эмоционального благополучия.

Чтобы получить доступ ко всем инструментам, перейдите в наше мини-приложение. Выберите нужную функцию ниже."""
    
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Зайти в мини-приложение",
                    "url": APP_URL
                }
            ],
            [
                {
                    "text": "Посмотреть список дел",
                    "callback_data": "view_todos"
                }
            ],
            [
                {
                    "text": "Отчетность за неделю",
                    "callback_data": "weekly_report"
                }
            ]
        ]
    }
    
    await bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=keyboard)

async def help_command(chat_id: str):
    """Справка по командам бота"""
    help_text = """🤖 Команды бота MaxPersonalEffect:

/start - Начать работу с ботом
/help - Показать эту справку
/app - Открыть мини-приложение
/todos - Посмотреть список дел
/report - Отчетность за неделю

Или используйте кнопки меню для навигации."""
    
    await bot.send_message(chat_id=chat_id, text=help_text)

async def app_command(chat_id: str):
    """Открыть мини-приложение"""
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Открыть мини-приложение",
                    "url": APP_URL
                }
            ]
        ]
    }
    
    await bot.send_message(
        chat_id=chat_id,
        text=f"🔗 Откройте мини-приложение:\n{APP_URL}",
        reply_markup=keyboard
    )

async def todos_menu(chat_id: str):
    """Меню списка дел"""
    text = "Что именно вас интересует?"
    
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Ближайшая задача",
                    "callback_data": "nearest_task"
                }
            ],
            [
                {
                    "text": "На сегодня",
                    "callback_data": "todos_today"
                }
            ],
            [
                {
                    "text": "На неделю",
                    "callback_data": "todos_week"
                }
            ],
            [
                {
                    "text": "Вернуться в меню",
                    "callback_data": "back_to_menu"
                }
            ]
        ]
    }
    
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

async def nearest_task(chat_id: str, callback_id: Optional[str] = None):
    """Получить ближайшую задачу"""
    if callback_id:
        await bot.answer_callback_query(callback_id, "Загрузка...")
    
    try:
        session = await bot.get_session()
        async with session.get(f"{API_URL}/todos/") as response:
            if response.status == 200:
                todos = await response.json()
                
                # Фильтруем невыполненные задачи и сортируем по дате
                active_todos = [t for t in todos if not t.get("completed", False)]
                active_todos.sort(key=lambda x: x.get("due_date", "") or "9999-99-99")
                
                if active_todos:
                    task = active_todos[0]
                    due_date = task.get("due_date", "Не указана")
                    description = task.get("description", "Без описания")
                    
                    text = f"📋 Ближайшая задача:\n\n"
                    text += f"📌 {task['title']}\n"
                    text += f"📝 {description}\n"
                    text += f"📅 Срок: {due_date}"
                else:
                    text = "✅ У вас нет активных задач!"
            else:
                text = "❌ Не удалось загрузить задачи. Попробуйте позже."
    except Exception as e:
        print(f"Error fetching nearest task: {e}")
        text = "❌ Произошла ошибка при загрузке задач."
    
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Зайти в мини-приложение",
                    "url": APP_URL
                }
            ],
            [
                {
                    "text": "Вернуться в меню",
                    "callback_data": "back_to_menu"
                }
            ]
        ]
    }
    
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

async def todos_today(chat_id: str, callback_id: Optional[str] = None):
    """Получить задачи на сегодня"""
    if callback_id:
        await bot.answer_callback_query(callback_id, "Загрузка...")
    
    from datetime import datetime
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        session = await bot.get_session()
        async with session.get(f"{API_URL}/todos/") as response:
            if response.status == 200:
                todos = await response.json()
                today_todos = [t for t in todos if t.get("due_date") == today]
                
                if today_todos:
                    text = f"📋 Задачи на сегодня ({today}):\n\n"
                    for i, task in enumerate(today_todos, 1):
                        status = "✅" if task.get("completed") else "⏳"
                        text += f"{i}. {status} {task['title']}\n"
                else:
                    text = f"✅ На сегодня ({today}) у вас нет задач!"
            else:
                text = "❌ Не удалось загрузить задачи."
    except Exception as e:
        print(f"Error fetching today todos: {e}")
        text = "❌ Произошла ошибка."
    
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Зайти в мини-приложение",
                    "url": APP_URL
                }
            ],
            [
                {
                    "text": "Вернуться в меню",
                    "callback_data": "back_to_menu"
                }
            ]
        ]
    }
    
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

async def todos_week(chat_id: str, callback_id: Optional[str] = None):
    """Получить задачи на неделю"""
    if callback_id:
        await bot.answer_callback_query(callback_id, "Загрузка...")
    
    from datetime import datetime, timedelta
    
    try:
        today = datetime.now()
        week_end = today + timedelta(days=7)
        today_str = today.strftime("%Y-%m-%d")
        week_end_str = week_end.strftime("%Y-%m-%d")
        
        session = await bot.get_session()
        async with session.get(f"{API_URL}/todos/") as response:
            if response.status == 200:
                todos = await response.json()
                week_todos = [
                    t for t in todos 
                    if t.get("due_date") and today_str <= t.get("due_date") <= week_end_str
                ]
                
                if week_todos:
                    text = f"📋 Задачи на неделю ({today_str} - {week_end_str}):\n\n"
                    for i, task in enumerate(week_todos, 1):
                        status = "✅" if task.get("completed") else "⏳"
                        due_date = task.get("due_date", "")
                        text += f"{i}. {status} {task['title']} ({due_date})\n"
                else:
                    text = "✅ На эту неделю у вас нет задач!"
            else:
                text = "❌ Не удалось загрузить задачи."
    except Exception as e:
        print(f"Error fetching week todos: {e}")
        text = "❌ Произошла ошибка."
    
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Зайти в мини-приложение",
                    "url": APP_URL
                }
            ],
            [
                {
                    "text": "Вернуться в меню",
                    "callback_data": "back_to_menu"
                }
            ]
        ]
    }
    
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

async def weekly_report(chat_id: str, callback_id: Optional[str] = None):
    """Получить отчетность за неделю"""
    if callback_id:
        await bot.answer_callback_query(callback_id, "Загрузка отчета...")
    
    try:
        session = await bot.get_session()
        
        # Получаем статистику
        async with session.get(f"{API_URL}/reports/stats") as response:
            if response.status == 200:
                stats = await response.json()
            else:
                stats = {}
        
        # Получаем еженедельный отчет
        async with session.get(f"{API_URL}/reports/weekly-report") as response:
            if response.status == 200:
                weekly = await response.json()
            else:
                weekly = {}
        
        text = "📊 Отчетность за неделю\n\n"
        text += f"📈 Выполнение задач: {stats.get('completion_rate', 0)}%\n"
        text += f"✅ Выполнено задач за 7 дней: {stats.get('tasks_completed_7days', 0)}\n"
        text += f"😊 Среднее настроение: {stats.get('avg_mood_7days', 0)}/5\n"
        text += f"🔥 Дней подряд: {stats.get('streak_days', 0)}\n\n"
        
        if weekly:
            text += f"📅 Период: {weekly.get('week_start', '')} - {weekly.get('week_end', '')}\n"
            text += f"✅ Задач выполнено: {weekly.get('todos_completed', 0)}/{weekly.get('todos_total', 0)}\n"
            text += f"🎯 Прогресс целей: {weekly.get('goals_progress', 0)}%\n"
            text += f"💪 Привычек выполнено: {weekly.get('habits_completed', 0)}/{weekly.get('habits_total', 0)}\n"
            text += f"😊 Среднее настроение: {weekly.get('avg_mood', 0)}/5"
        
    except Exception as e:
        print(f"Error fetching weekly report: {e}")
        text = "❌ Произошла ошибка при загрузке отчета."
    
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Зайти в мини-приложение",
                    "url": APP_URL
                }
            ],
            [
                {
                    "text": "Вернуться в меню",
                    "callback_data": "back_to_menu"
                }
            ]
        ]
    }
    
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

async def polling_loop():
    """Основной цикл polling"""
    offset = 0
    
    print("🤖 Бот MaxPersonalEffect запущен!")
    print(f"📱 Мини-приложение: {APP_URL}")
    print(f"🔗 API: {API_URL}")
    
    while True:
        try:
            updates = await bot.get_updates(offset=offset, timeout=30)
            
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    
                    # Обработка сообщений
                    if "message" in update:
                        await handle_message(update["message"])
                    
                    # Обработка callback queries
                    if "callback_query" in update:
                        await handle_callback(update["callback_query"])
        
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Ошибка в polling loop: {e}")
            await asyncio.sleep(5)

async def main():
    """Главная функция запуска бота"""
    try:
        await polling_loop()
    except KeyboardInterrupt:
        print("\n⏹️ Остановка бота...")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
