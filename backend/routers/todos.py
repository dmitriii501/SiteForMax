from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from database import get_db

router = APIRouter()

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    reminder: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[str] = None
    reminder: Optional[str] = None

class TodoResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    completed: bool
    due_date: Optional[str]
    reminder: Optional[str]
    created_at: str
    updated_at: str

def row_to_dict(row) -> dict:
    """Преобразует строку БД в словарь"""
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
        "due_date": row["due_date"],
        "reminder": row["reminder"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }

@router.get("/", response_model=List[TodoResponse])
async def get_todos():
    """Получить все задачи"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos ORDER BY completed ASC, created_at DESC")
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: str):
    """Получить задачу по ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return row_to_dict(row)

@router.post("/", response_model=TodoResponse)
async def create_todo(todo: TodoCreate):
    """Создать новую задачу"""
    todo_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO todos (id, title, description, completed, due_date, reminder, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (todo_id, todo.title, todo.description, 0, todo.due_date, todo.reminder, now, now))
        
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        return row_to_dict(row)

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, todo: TodoUpdate):
    """Обновить задачу"""
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Получаем текущие данные
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        # Обновляем только переданные поля
        updates = []
        values = []
        
        if todo.title is not None:
            updates.append("title = ?")
            values.append(todo.title)
        if todo.description is not None:
            updates.append("description = ?")
            values.append(todo.description)
        if todo.completed is not None:
            updates.append("completed = ?")
            values.append(1 if todo.completed else 0)
        if todo.due_date is not None:
            updates.append("due_date = ?")
            values.append(todo.due_date)
        if todo.reminder is not None:
            updates.append("reminder = ?")
            values.append(todo.reminder)
        
        updates.append("updated_at = ?")
        values.append(now)
        values.append(todo_id)
        
        cursor.execute(f"""
            UPDATE todos 
            SET {', '.join(updates)}
            WHERE id = ?
        """, values)
        
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        return row_to_dict(row)

@router.delete("/{todo_id}")
async def delete_todo(todo_id: str):
    """Удалить задачу"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return {"message": "Задача удалена"}

