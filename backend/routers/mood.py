from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db

router = APIRouter()

class MoodEntryCreate(BaseModel):
    mood: Optional[int] = None
    emotions: List[str] = []

class MoodEntryUpdate(BaseModel):
    mood: Optional[int] = None
    emotions: Optional[List[str]] = None

class MoodEntryResponse(BaseModel):
    date: str
    mood: Optional[int]
    emotions: List[str]
    created_at: str
    updated_at: str

@router.get("/", response_model=List[MoodEntryResponse])
async def get_mood_entries(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Получить все записи настроения"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM mood_entries"
        params = []
        
        if start_date or end_date:
            conditions = []
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY date DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        entries = []
        for row in rows:
            # Получаем эмоции для этой записи
            cursor.execute("SELECT emotion FROM emotions WHERE mood_date = ?", (row["date"],))
            emotion_rows = cursor.fetchall()
            emotions = [e["emotion"] for e in emotion_rows]
            
            entries.append({
                "date": row["date"],
                "mood": row["mood"],
                "emotions": emotions,
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })
        
        return entries

@router.get("/{date}", response_model=MoodEntryResponse)
async def get_mood_entry(date: str):
    """Получить запись настроения по дате"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mood_entries WHERE date = ?", (date,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        
        cursor.execute("SELECT emotion FROM emotions WHERE mood_date = ?", (date,))
        emotion_rows = cursor.fetchall()
        emotions = [e["emotion"] for e in emotion_rows]
        
        return {
            "date": row["date"],
            "mood": row["mood"],
            "emotions": emotions,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }

@router.post("/{date}", response_model=MoodEntryResponse)
async def create_or_update_mood_entry(date: str, entry: MoodEntryCreate):
    """Создать или обновить запись настроения"""
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем существующую запись
        cursor.execute("SELECT * FROM mood_entries WHERE date = ?", (date,))
        row = cursor.fetchone()
        
        if row:
            # Обновляем
            cursor.execute("""
                UPDATE mood_entries 
                SET mood = ?, updated_at = ?
                WHERE date = ?
            """, (entry.mood, now, date))
            
            # Удаляем старые эмоции
            cursor.execute("DELETE FROM emotions WHERE mood_date = ?", (date,))
        else:
            # Создаем новую запись
            cursor.execute("""
                INSERT INTO mood_entries (date, mood, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (date, entry.mood, now, now))
        
        # Добавляем эмоции
        for emotion in entry.emotions:
            cursor.execute("""
                INSERT INTO emotions (mood_date, emotion)
                VALUES (?, ?)
            """, (date, emotion))
        
        cursor.execute("SELECT * FROM mood_entries WHERE date = ?", (date,))
        row = cursor.fetchone()
        cursor.execute("SELECT emotion FROM emotions WHERE mood_date = ?", (date,))
        emotion_rows = cursor.fetchall()
        emotions = [e["emotion"] for e in emotion_rows]
        
        return {
            "date": row["date"],
            "mood": row["mood"],
            "emotions": emotions,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }

@router.put("/{date}", response_model=MoodEntryResponse)
async def update_mood_entry(date: str, entry: MoodEntryUpdate):
    """Обновить запись настроения"""
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM mood_entries WHERE date = ?", (date,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        
        # Обновляем настроение, если передано
        if entry.mood is not None:
            cursor.execute("""
                UPDATE mood_entries 
                SET mood = ?, updated_at = ?
                WHERE date = ?
            """, (entry.mood, now, date))
        
        # Обновляем эмоции, если переданы
        if entry.emotions is not None:
            cursor.execute("DELETE FROM emotions WHERE mood_date = ?", (date,))
            for emotion in entry.emotions:
                cursor.execute("""
                    INSERT INTO emotions (mood_date, emotion)
                    VALUES (?, ?)
                """, (date, emotion))
        
        cursor.execute("SELECT * FROM mood_entries WHERE date = ?", (date,))
        row = cursor.fetchone()
        cursor.execute("SELECT emotion FROM emotions WHERE mood_date = ?", (date,))
        emotion_rows = cursor.fetchall()
        emotions = [e["emotion"] for e in emotion_rows]
        
        return {
            "date": row["date"],
            "mood": row["mood"],
            "emotions": emotions,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }

@router.delete("/{date}")
async def delete_mood_entry(date: str):
    """Удалить запись настроения"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mood_entries WHERE date = ?", (date,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        return {"message": "Запись удалена"}

