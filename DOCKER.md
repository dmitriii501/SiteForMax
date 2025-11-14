# Docker инструкция

Инструкция по запуску приложения через Docker.

## 🐳 Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)

Запускает все сервисы одной командой:

```bash
docker-compose up -d
```

Приложение будет доступно:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### Вариант 2: Отдельные контейнеры

#### Запуск бэкенда

```bash
cd backend
docker build -t maxpersonal-effect-api .
docker run -d -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./data/max_personal_effect.db \
  -e ALLOWED_ORIGINS=http://localhost:3000 \
  -v $(pwd)/data:/app/data \
  --name maxpersonal-effect-api \
  maxpersonal-effect-api
```

#### Запуск фронтенда

```bash
docker build -f Dockerfile.frontend -t maxpersonal-effect-frontend .
docker run -d -p 3000:80 \
  --name maxpersonal-effect-frontend \
  maxpersonal-effect-frontend
```

## 📋 Команды Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes (удалит данные БД!)
docker-compose down -v

# Пересборка образов
docker-compose build --no-cache

# Перезапуск конкретного сервиса
docker-compose restart backend
docker-compose restart frontend

# Просмотр статуса
docker-compose ps
```

## 🔧 Настройка переменных окружения

Отредактируйте `docker-compose.yml` для изменения настроек:

```yaml
environment:
  - DATABASE_URL=postgresql://user:password@db:5432/dbname
  - ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
  - DEBUG=false
```

Или создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql://maxpersonal_user:maxpersonal_password@db:5432/maxpersonal_effect
ALLOWED_ORIGINS=http://localhost:3000
DEBUG=false
POSTGRES_PASSWORD=maxpersonal_password
```

И обновите `docker-compose.yml`:

```yaml
environment:
  - DATABASE_URL=${DATABASE_URL}
  - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
```

## 🗄️ База данных

### PostgreSQL (по умолчанию в docker-compose)

Данные сохраняются в Docker volume `postgres_data`.

**Подключение к БД:**
```bash
docker-compose exec db psql -U maxpersonal_user -d maxpersonal_effect
```

**Резервное копирование:**
```bash
docker-compose exec db pg_dump -U maxpersonal_user maxpersonal_effect > backup.sql
```

**Восстановление:**
```bash
docker-compose exec -T db psql -U maxpersonal_user maxpersonal_effect < backup.sql
```

### SQLite (для разработки)

Если хотите использовать SQLite вместо PostgreSQL, измените `docker-compose.yml`:

```yaml
backend:
  environment:
    - DATABASE_URL=sqlite:///./data/max_personal_effect.db
  volumes:
    - ./backend/data:/app/data
```

И уберите сервис `db` из `docker-compose.yml`.

## 🌐 Настройка API URL

Если фронтенд и бэкенд в разных контейнерах, обновите `js/api.js`:

```javascript
// Для Docker Compose (все на одном хосте)
const API_BASE_URL = '/api';

// Или для отдельных контейнеров
const API_BASE_URL = 'http://localhost:8000/api';
```

Nginx в контейнере фронтенда автоматически проксирует `/api` запросы на бэкенд.

## 🚀 Деплой Docker образа

### Сборка образов для продакшена

```bash
# Бэкенд
docker build -t your-registry/maxpersonal-effect-api:latest ./backend

# Фронтенд
docker build -f Dockerfile.frontend -t your-registry/maxpersonal-effect-frontend:latest .
```

### Загрузка в Docker Hub

```bash
# Логин
docker login

# Тегирование
docker tag maxpersonal-effect-api:latest your-username/maxpersonal-effect-api:latest
docker tag maxpersonal-effect-frontend:latest your-username/maxpersonal-effect-frontend:latest

# Загрузка
docker push your-username/maxpersonal-effect-api:latest
docker push your-username/maxpersonal-effect-frontend:latest
```

### Запуск на сервере

```bash
# Скачать образы
docker pull your-username/maxpersonal-effect-api:latest
docker pull your-username/maxpersonal-effect-frontend:latest

# Запустить через docker-compose
docker-compose up -d
```

## 🔍 Отладка

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Вход в контейнер

```bash
# Бэкенд
docker-compose exec backend bash

# База данных
docker-compose exec db psql -U maxpersonal_user -d maxpersonal_effect
```

### Проверка работы

```bash
# Health check API
curl http://localhost:8000/health

# Проверка фронтенда
curl http://localhost:3000
```

## 🛠️ Разработка с Docker

### Hot reload для бэкенда

Для разработки можно монтировать код:

```yaml
backend:
  volumes:
    - ./backend:/app
    - ./backend/data:/app/data
  command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Hot reload для фронтенда

Используйте локальный сервер для разработки фронтенда, а Docker только для бэкенда.

## 📝 Структура Docker файлов

```
.
├── docker-compose.yml      # Оркестрация всех сервисов
├── Dockerfile.frontend      # Образ для фронтенда (Nginx)
├── nginx.conf              # Конфигурация Nginx
├── .dockerignore           # Игнорируемые файлы
└── backend/
    ├── Dockerfile          # Образ для бэкенда (FastAPI)
    └── .dockerignore       # Игнорируемые файлы бэкенда
```

## ⚠️ Важные замечания

1. **Пароли**: В продакшене используйте сильные пароли и переменные окружения
2. **Volumes**: Данные БД сохраняются в Docker volumes
3. **Порты**: Убедитесь, что порты 3000, 8000, 5432 свободны
4. **CORS**: Настройте `ALLOWED_ORIGINS` для вашего домена
5. **SSL**: Для продакшена используйте reverse proxy (Traefik, Nginx) с SSL

## 🆘 Решение проблем

### Порт уже занят

Измените порты в `docker-compose.yml`:
```yaml
ports:
  - "3001:80"  # Вместо 3000
  - "8001:8000"  # Вместо 8000
```

### Ошибки подключения к БД

Проверьте, что сервис `db` запущен:
```bash
docker-compose ps
docker-compose logs db
```

### Фронтенд не подключается к API

Проверьте `nginx.conf` и убедитесь, что проксирование настроено правильно.

### Очистка

```bash
# Удалить все контейнеры и volumes
docker-compose down -v

# Удалить образы
docker rmi maxpersonal-effect-api maxpersonal-effect-frontend

# Полная очистка (осторожно!)
docker system prune -a --volumes
```

