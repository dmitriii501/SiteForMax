from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import random

from database import get_db

router = APIRouter()

# Цвета для привычек
COLORS = ["#8b5cf6", "#ec4899", "#10b981", "#f59e0b", "#3b82f6", "#ef4444", "#06b6d4", "#a855f7"]

class HabitCreate(BaseModel):
    name: str

class HabitResponse(BaseModel):
    id: str
    name: str
    color: Optional[str]
    created_at: str
    updated_at: str

class HabitCompletionResponse(BaseModel):
    habit_id: str
    date: str
    completed: bool

class WaterDataResponse(BaseModel):
    date: str
    amount: int
    goal: int
    updated_at: str

class WaterDataUpdate(BaseModel):
    amount: Optional[int] = None
    goal: Optional[int] = None

def habit_row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "color": row["color"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }

@router.get("/", response_model=List[HabitResponse])
async def get_habits():
    """Получить все привычки"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM habits ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [habit_row_to_dict(row) for row in rows]

@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(habit_id: str):
    """Получить привычку по ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Привычка не найдена")
        return habit_row_to_dict(row)

@router.post("/", response_model=HabitResponse)
async def create_habit(habit: HabitCreate):
    """Создать новую привычку"""
    habit_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    color = random.choice(COLORS)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO habits (id, name, color, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (habit_id, habit.name, color, now, now))
        
        cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        row = cursor.fetchone()
        return habit_row_to_dict(row)

@router.delete("/{habit_id}")
async def delete_habit(habit_id: str):
    """Удалить привычку"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Привычка не найдена")
        return {"message": "Привычка удалена"}

@router.get("/{habit_id}/completions", response_model=List[HabitCompletionResponse])
async def get_habit_completions(habit_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Получить отметки выполнения привычки"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM habit_completions WHERE habit_id = ?"
        params = [habit_id]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [
            {
                "habit_id": row["habit_id"],
                "date": row["date"],
                "completed": bool(row["completed"])
            }
            for row in rows
        ]

@router.post("/{habit_id}/completions/{date}")
async def toggle_habit_completion(habit_id: str, date: str):
    """Переключить отметку выполнения привычки на дату"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем существование привычки
        cursor.execute("SELECT id FROM habits WHERE id = ?", (habit_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Привычка не найдена")
        
        # Проверяем существующую запись
        cursor.execute("SELECT * FROM habit_completions WHERE habit_id = ? AND date = ?", (habit_id, date))
        row = cursor.fetchone()
        
        if row:
            # Переключаем
            new_completed = 1 - row["completed"]
            cursor.execute("""
                UPDATE habit_completions 
                SET completed = ? 
                WHERE habit_id = ? AND date = ?
            """, (new_completed, habit_id, date))
        else:
            # Создаем новую запись
            cursor.execute("""
                INSERT INTO habit_completions (habit_id, date, completed)
                VALUES (?, ?, ?)
            """, (habit_id, date, 1))
        
        return {"message": "Отметка обновлена"}

@router.delete("/{habit_id}/completions/{date}")
async def delete_habit_completion(habit_id: str, date: str):
    """Удалить отметку выполнения привычки"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habit_completions WHERE habit_id = ? AND date = ?", (habit_id, date))
        return {"message": "Отметка удалена"}

# Водный трекер
@router.get("/water/{date}", response_model=WaterDataResponse)
async def get_water_data(date: str):
    """Получить данные о воде на дату"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM water_data WHERE date = ?", (date,))
        row = cursor.fetchone()
        
        if not row:
            # Создаем запись по умолчанию
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO water_data (date, amount, goal, updated_at)
                VALUES (?, ?, ?, ?)
            """, (date, 0, 2000, now))
            return {
                "date": date,
                "amount": 0,
                "goal": 2000,
                "updated_at": now
            }
        
        return {
            "date": row["date"],
            "amount": row["amount"],
            "goal": row["goal"],
            "updated_at": row["updated_at"]
        }

@router.put("/water/{date}", response_model=WaterDataResponse)
async def update_water_data(date: str, data: WaterDataUpdate):
    """Обновить данные о воде"""
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем существующую запись
        cursor.execute("SELECT * FROM water_data WHERE date = ?", (date,))
        row = cursor.fetchone()
        
        if row:
            # Обновляем
            updates = []
            values = []
            
            if data.amount is not None:
                updates.append("amount = ?")
                values.append(data.amount)
            if data.goal is not None:
                updates.append("goal = ?")
                values.append(data.goal)
            
            updates.append("updated_at = ?")
            values.append(now)
            values.append(date)
            
            cursor.execute(f"""
                UPDATE water_data 
                SET {', '.join(updates)}
                WHERE date = ?
            """, values)
        else:
            # Создаем новую запись
            amount = data.amount if data.amount is not None else 0
            goal = data.goal if data.goal is not None else 2000
            cursor.execute("""
                INSERT INTO water_data (date, amount, goal, updated_at)
                VALUES (?, ?, ?, ?)
            """, (date, amount, goal, now))
        
        cursor.execute("SELECT * FROM water_data WHERE date = ?", (date,))
        row = cursor.fetchone()
        return {
            "date": row["date"],
            "amount": row["amount"],
            "goal": row["goal"],
            "updated_at": row["updated_at"]
        }

@router.post("/water/{date}/add")
async def add_water(date: str, amount: int = 100):
    """Добавить воду (по умолчанию 100мл)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM water_data WHERE date = ?", (date,))
        row = cursor.fetchone()
        
        if row:
            new_amount = min(row["amount"] + amount, row["goal"])
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE water_data 
                SET amount = ?, updated_at = ?
                WHERE date = ?
            """, (new_amount, now, date))
        else:
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO water_data (date, amount, goal, updated_at)
                VALUES (?, ?, ?, ?)
            """, (date, min(amount, 2000), 2000, now))
        
        return {"message": "Вода добавлена"}

