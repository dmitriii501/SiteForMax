# Деплой на Render.com

Простая инструкция по деплою приложения на Render.

## 🚀 Быстрый старт

### Вариант 1: Автоматический деплой через render.yaml

1. **Загрузите код на GitHub**
   - Создайте репозиторий на GitHub
   - Загрузите все файлы проекта

2. **Подключите к Render**
   - Зайдите на [render.com](https://render.com)
   - Нажмите **New** → **Blueprint**
   - Подключите ваш GitHub репозиторий
   - Render автоматически обнаружит `render.yaml` и создаст все сервисы

3. **Настройте переменные окружения**
   - После создания сервисов, откройте **API сервис** → **Environment**
   - Добавьте переменную:
     ```
     ALLOWED_ORIGINS=https://your-frontend-name.onrender.com
     ```
   - Замените `your-frontend-name` на имя вашего фронтенд сервиса

4. **Готово!** 🎉
   - API будет доступен по адресу: `https://your-api-name.onrender.com`
   - Фронтенд будет доступен по адресу: `https://your-frontend-name.onrender.com`

### Вариант 2: Ручной деплой

#### Шаг 1: Деплой Backend API

1. Зайдите на [render.com](https://render.com)
2. Нажмите **New** → **Web Service**
3. Подключите ваш GitHub репозиторий
4. Настройки:
   - **Name**: `maxpersonal-effect-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free (или Starter для продакшена)

5. Добавьте переменные окружения:
   - `ALLOWED_ORIGINS` = `https://your-frontend-name.onrender.com` (укажите после создания фронтенда)
   - `DEBUG` = `false`

6. Нажмите **Create Web Service**

#### Шаг 2: Создание PostgreSQL базы данных

1. Нажмите **New** → **PostgreSQL**
2. Настройки:
   - **Name**: `maxpersonal-effect-db`
   - **Database**: `maxpersonal_effect`
   - **User**: `maxpersonal_user`
   - **Plan**: Free

3. После создания, скопируйте **Internal Database URL**

4. Вернитесь к вашему API сервису → **Environment**
5. Добавьте переменную:
   - `DATABASE_URL` = (вставьте скопированный Internal Database URL)

#### Шаг 3: Деплой Frontend

1. Нажмите **New** → **Static Site**
2. Подключите ваш GitHub репозиторий
3. Настройки:
   - **Name**: `maxpersonal-effect-frontend`
   - **Build Command**: (оставьте пустым или `echo "No build needed"`)
   - **Publish Directory**: `.` (корень проекта)

4. После создания, откройте файл `js/api.js` в вашем репозитории
5. Измените `API_BASE_URL` на адрес вашего API:
   ```javascript
   const API_BASE_URL = 'https://your-api-name.onrender.com/api';
   ```
6. Закоммитьте и запушьте изменения
7. Render автоматически пересоберет фронтенд

## 🔧 Настройка CORS

После создания обоих сервисов:

1. Откройте **API сервис** → **Environment**
2. Обновите `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://your-frontend-name.onrender.com
   ```
3. Нажмите **Save Changes**
4. Render автоматически перезапустит сервис

## 📝 Обновление API URL во фронтенде

Если вы используете отдельные домены для API и фронтенда:

1. Откройте `js/api.js`
2. Измените:
   ```javascript
   const API_BASE_URL = 'https://your-api-name.onrender.com/api';
   ```
3. Закоммитьте изменения
4. Render автоматически обновит фронтенд

## ✅ Проверка работы

1. **API Health Check**: `https://your-api-name.onrender.com/health`
2. **API Docs**: `https://your-api-name.onrender.com/docs` (если DEBUG=true)
3. **Frontend**: `https://your-frontend-name.onrender.com`

## 🔄 Обновление приложения

1. Внесите изменения в код
2. Закоммитьте и запушьте в GitHub
3. Render автоматически обнаружит изменения и пересоберет сервисы

## 💡 Полезные советы

### Использование кастомных доменов

1. В настройках сервиса нажмите **Custom Domains**
2. Добавьте ваш домен
3. Настройте DNS записи согласно инструкциям Render

### Мониторинг

- **Logs**: Просмотр логов в реальном времени через панель Render
- **Metrics**: Базовые метрики доступны на бесплатном плане
- **Alerts**: Настройте уведомления о падениях сервисов

### Резервное копирование

- PostgreSQL на Render автоматически делает бэкапы
- Для экспорта данных используйте команду через Shell:
  ```bash
  pg_dump $DATABASE_URL > backup.sql
  ```

## 🐛 Решение проблем

### API не запускается

1. Проверьте логи в панели Render
2. Убедитесь, что все зависимости установлены
3. Проверьте переменные окружения

### Ошибки CORS

1. Убедитесь, что `ALLOWED_ORIGINS` содержит правильный URL фронтенда
2. URL должен быть с протоколом `https://`
3. Не должно быть завершающего слеша

### Проблемы с базой данных

1. Убедитесь, что `DATABASE_URL` правильно настроен
2. Проверьте, что база данных создана и запущена
3. Используйте Internal Database URL для подключения

### Фронтенд не подключается к API

1. Проверьте `API_BASE_URL` в `js/api.js`
2. Убедитесь, что API сервис запущен
3. Проверьте CORS настройки

## 📚 Дополнительная информация

- [Документация Render](https://render.com/docs)
- [FastAPI на Render](https://render.com/docs/deploy-fastapi)
- [PostgreSQL на Render](https://render.com/docs/databases)

## 🎉 Готово!

Ваше приложение теперь работает на Render! 

**Преимущества Render:**
- ✅ Автоматический деплой из GitHub
- ✅ Бесплатный план для начала
- ✅ Автоматические SSL сертификаты
- ✅ Простое масштабирование
- ✅ Встроенный мониторинг

