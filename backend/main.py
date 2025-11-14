from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import ALLOWED_ORIGINS, DEBUG
from database import init_db
from routers import todos, goals, habits, mood, reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (если нужно)

app = FastAPI(
    title="MaxPersonalEffect API", 
    version="1.0.0", 
    lifespan=lifespan,
    docs_url="/docs" if DEBUG else None,  # Отключаем docs в продакшене
    redoc_url="/redoc" if DEBUG else None
)

# CORS middleware для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if isinstance(ALLOWED_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(todos.router, prefix="/api/todos", tags=["todos"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(habits.router, prefix="/api/habits", tags=["habits"])
app.include_router(mood.router, prefix="/api/mood", tags=["mood"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "MaxPersonalEffect API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

