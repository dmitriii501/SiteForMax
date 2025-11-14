from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from database import get_db

router = APIRouter()

class SubtaskCreate(BaseModel):
    title: str

class SubtaskResponse(BaseModel):
    id: str
    goal_id: str
    title: str
    completed: bool
    created_at: str

class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    expanded: Optional[bool] = None

class GoalResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    expanded: bool
    subtasks: List[SubtaskResponse]
    created_at: str
    updated_at: str

def subtask_row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "goal_id": row["goal_id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"]
    }

@router.get("/", response_model=List[GoalResponse])
async def get_goals():
    """Получить все цели"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals ORDER BY created_at DESC")
        goals_rows = cursor.fetchall()
        
        goals = []
        for goal_row in goals_rows:
            goal_id = goal_row["id"]
            
            # Получаем подзадачи для этой цели
            cursor.execute("SELECT * FROM subtasks WHERE goal_id = ?", (goal_id,))
            subtasks_rows = cursor.fetchall()
            
            goal = {
                "id": goal_id,
                "title": goal_row["title"],
                "description": goal_row["description"],
                "expanded": bool(goal_row["expanded"]),
                "subtasks": [subtask_row_to_dict(row) for row in subtasks_rows],
                "created_at": goal_row["created_at"],
                "updated_at": goal_row["updated_at"]
            }
            goals.append(goal)
        
        return goals

@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(goal_id: str):
    """Получить цель по ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        goal_row = cursor.fetchone()
        if not goal_row:
            raise HTTPException(status_code=404, detail="Цель не найдена")
        
        cursor.execute("SELECT * FROM subtasks WHERE goal_id = ?", (goal_id,))
        subtasks_rows = cursor.fetchall()
        
        return {
            "id": goal_id,
            "title": goal_row["title"],
            "description": goal_row["description"],
            "expanded": bool(goal_row["expanded"]),
            "subtasks": [subtask_row_to_dict(row) for row in subtasks_rows],
            "created_at": goal_row["created_at"],
            "updated_at": goal_row["updated_at"]
        }

@router.post("/", response_model=GoalResponse)
async def create_goal(goal: GoalCreate):
    """Создать новую цель"""
    goal_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO goals (id, title, description, expanded, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (goal_id, goal.title, goal.description, 1, now, now))
        
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        goal_row = cursor.fetchone()
        
        return {
            "id": goal_id,
            "title": goal_row["title"],
            "description": goal_row["description"],
            "expanded": bool(goal_row["expanded"]),
            "subtasks": [],
            "created_at": goal_row["created_at"],
            "updated_at": goal_row["updated_at"]
        }

@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(goal_id: str, goal: GoalUpdate):
    """Обновить цель"""
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Цель не найдена")
        
        updates = []
        values = []
        
        if goal.title is not None:
            updates.append("title = ?")
            values.append(goal.title)
        if goal.description is not None:
            updates.append("description = ?")
            values.append(goal.description)
        if goal.expanded is not None:
            updates.append("expanded = ?")
            values.append(1 if goal.expanded else 0)
        
        updates.append("updated_at = ?")
        values.append(now)
        values.append(goal_id)
        
        cursor.execute(f"""
            UPDATE goals 
            SET {', '.join(updates)}
            WHERE id = ?
        """, values)
        
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        goal_row = cursor.fetchone()
        cursor.execute("SELECT * FROM subtasks WHERE goal_id = ?", (goal_id,))
        subtasks_rows = cursor.fetchall()
        
        return {
            "id": goal_id,
            "title": goal_row["title"],
            "description": goal_row["description"],
            "expanded": bool(goal_row["expanded"]),
            "subtasks": [subtask_row_to_dict(row) for row in subtasks_rows],
            "created_at": goal_row["created_at"],
            "updated_at": goal_row["updated_at"]
        }

@router.delete("/{goal_id}")
async def delete_goal(goal_id: str):
    """Удалить цель"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Цель не найдена")
        return {"message": "Цель удалена"}

@router.post("/{goal_id}/subtasks", response_model=SubtaskResponse)
async def create_subtask(goal_id: str, subtask: SubtaskCreate):
    """Создать подзадачу для цели"""
    subtask_id = f"{goal_id}-{uuid.uuid4()}"
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Проверяем существование цели
        cursor.execute("SELECT id FROM goals WHERE id = ?", (goal_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Цель не найдена")
        
        cursor.execute("""
            INSERT INTO subtasks (id, goal_id, title, completed, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (subtask_id, goal_id, subtask.title, 0, now))
        
        cursor.execute("SELECT * FROM subtasks WHERE id = ?", (subtask_id,))
        row = cursor.fetchone()
        return subtask_row_to_dict(row)

@router.put("/{goal_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(goal_id: str, subtask_id: str, completed: Optional[bool] = None):
    """Обновить подзадачу (переключить выполнение)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM subtasks WHERE id = ? AND goal_id = ?", (subtask_id, goal_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Подзадача не найдена")
        
        new_completed = 1 - row["completed"] if completed is None else (1 if completed else 0)
        cursor.execute("UPDATE subtasks SET completed = ? WHERE id = ?", (new_completed, subtask_id))
        
        cursor.execute("SELECT * FROM subtasks WHERE id = ?", (subtask_id,))
        row = cursor.fetchone()
        return subtask_row_to_dict(row)

@router.delete("/{goal_id}/subtasks/{subtask_id}")
async def delete_subtask(goal_id: str, subtask_id: str):
    """Удалить подзадачу"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subtasks WHERE id = ? AND goal_id = ?", (subtask_id, goal_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Подзадача не найдена")
        return {"message": "Подзадача удалена"}

