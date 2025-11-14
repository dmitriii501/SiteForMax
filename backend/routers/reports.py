from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta

from database import get_db

router = APIRouter()

class StatsResponse(BaseModel):
    completion_rate: float
    tasks_completed_7days: int
    avg_mood_7days: float
    streak_days: int

class TaskChartData(BaseModel):
    day: str
    completed: int
    total: int

class MoodChartData(BaseModel):
    day: str
    mood: int

class HabitProgressData(BaseModel):
    habit_id: str
    habit_name: str
    progress: float

class EmotionChartData(BaseModel):
    emotion: str
    count: int
    percentage: float

class WeeklyReportData(BaseModel):
    week_start: str
    week_end: str
    todos_completed: int
    todos_total: int
    goals_progress: float
    habits_completed: int
    habits_total: int
    avg_mood: float

def get_last_7_days():
    """Получить последние 7 дней (с понедельника по воскресенье)"""
    today = datetime.now().date()
    day_of_week = today.weekday()  # 0 = понедельник, 6 = воскресенье
    
    # Находим понедельник текущей недели
    monday = today - timedelta(days=day_of_week)
    
    days = []
    for i in range(7):
        day = monday + timedelta(days=i)
        days.append(day.isoformat())
    
    return days

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Получить краткую статистику"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Процент выполнения задач
        cursor.execute("SELECT COUNT(*) as total, SUM(completed) as completed FROM todos")
        row = cursor.fetchone()
        total_tasks = row["total"] or 0
        completed_tasks = row["completed"] or 0
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Выполненные задачи за 7 дней
        last_7_days = get_last_7_days()
        placeholders = ','.join(['?'] * len(last_7_days))
        cursor.execute(f"""
            SELECT COUNT(*) as count 
            FROM todos 
            WHERE completed = 1 AND due_date IN ({placeholders})
        """, last_7_days)
        tasks_7days = cursor.fetchone()["count"] or 0
        
        # Среднее настроение за 7 дней
        cursor.execute(f"""
            SELECT AVG(mood) as avg_mood 
            FROM mood_entries 
            WHERE date IN ({placeholders}) AND mood IS NOT NULL
        """, last_7_days)
        row = cursor.fetchone()
        avg_mood = float(row["avg_mood"]) if row["avg_mood"] else 0.0
        
        # Счетчик дней подряд (упрощенная логика)
        streak_days = 0
        today = datetime.now().date()
        for i in range(30):  # Проверяем последние 30 дней
            check_date = (today - timedelta(days=i)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM todos 
                WHERE completed = 1 AND due_date = ?
            """, (check_date,))
            if cursor.fetchone()["count"] > 0:
                streak_days += 1
            else:
                break
        
        return {
            "completion_rate": round(completion_rate, 1),
            "tasks_completed_7days": tasks_7days,
            "avg_mood_7days": round(avg_mood, 1),
            "streak_days": streak_days
        }

@router.get("/tasks-chart", response_model=List[TaskChartData])
async def get_tasks_chart():
    """Получить данные для графика задач за 7 дней"""
    last_7_days = get_last_7_days()
    day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    
    with get_db() as conn:
        cursor = conn.cursor()
        data = []
        
        for i, date in enumerate(last_7_days):
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(completed) as completed
                FROM todos 
                WHERE due_date = ?
            """, (date,))
            row = cursor.fetchone()
            
            data.append({
                "day": day_names[i],
                "completed": row["completed"] or 0,
                "total": row["total"] or 0
            })
        
        return data

@router.get("/mood-chart", response_model=List[MoodChartData])
async def get_mood_chart():
    """Получить данные для графика настроения за 7 дней"""
    last_7_days = get_last_7_days()
    day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    
    with get_db() as conn:
        cursor = conn.cursor()
        data = []
        
        for i, date in enumerate(last_7_days):
            cursor.execute("SELECT mood FROM mood_entries WHERE date = ?", (date,))
            row = cursor.fetchone()
            
            data.append({
                "day": day_names[i],
                "mood": row["mood"] if row and row["mood"] else 0
            })
        
        return data

@router.get("/habits-progress", response_model=List[HabitProgressData])
async def get_habits_progress():
    """Получить прогресс по привычкам"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Получаем все привычки
        cursor.execute("SELECT id, name FROM habits")
        habits = cursor.fetchall()
        
        progress_data = []
        
        for habit in habits:
            habit_id = habit["id"]
            habit_name = habit["name"]
            
            # Подсчитываем выполненные дни за последние 7 дней
            last_7_days = get_last_7_days()
            placeholders = ','.join(['?'] * len(last_7_days))
            
            cursor.execute(f"""
                SELECT COUNT(*) as completed
                FROM habit_completions
                WHERE habit_id = ? AND date IN ({placeholders}) AND completed = 1
            """, [habit_id] + last_7_days)
            
            completed = cursor.fetchone()["completed"] or 0
            progress = (completed / 7 * 100) if 7 > 0 else 0
            
            progress_data.append({
                "habit_id": habit_id,
                "habit_name": habit_name,
                "progress": round(progress, 1)
            })
        
        return progress_data

@router.get("/emotions-chart", response_model=List[EmotionChartData])
async def get_emotions_chart():
    """Получить статистику по эмоциям за 7 дней"""
    last_7_days = get_last_7_days()
    placeholders = ','.join(['?'] * len(last_7_days))
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Получаем все эмоции за последние 7 дней
        cursor.execute(f"""
            SELECT emotion, COUNT(*) as count
            FROM emotions
            WHERE mood_date IN ({placeholders})
            GROUP BY emotion
            ORDER BY count DESC
            LIMIT 5
        """, last_7_days)
        
        emotion_rows = cursor.fetchall()
        
        # Подсчитываем общее количество записей с эмоциями
        cursor.execute(f"""
            SELECT COUNT(DISTINCT mood_date) as total
            FROM emotions
            WHERE mood_date IN ({placeholders})
        """, last_7_days)
        total_entries = cursor.fetchone()["total"] or 1
        
        data = []
        for row in emotion_rows:
            percentage = (row["count"] / total_entries * 100) if total_entries > 0 else 0
            data.append({
                "emotion": row["emotion"],
                "count": row["count"],
                "percentage": round(percentage, 1)
            })
        
        return data

@router.get("/weekly-report", response_model=WeeklyReportData)
async def get_weekly_report():
    """Получить еженедельный отчет"""
    last_7_days = get_last_7_days()
    week_start = last_7_days[0]
    week_end = last_7_days[-1]
    placeholders = ','.join(['?'] * len(last_7_days))
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Задачи
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(completed) as completed
            FROM todos
            WHERE due_date IN ({placeholders})
        """, last_7_days)
        task_row = cursor.fetchone()
        todos_total = task_row["total"] or 0
        todos_completed = task_row["completed"] or 0
        
        # Цели (средний прогресс)
        cursor.execute("""
            SELECT 
                g.id,
                COUNT(s.id) as total_subtasks,
                SUM(s.completed) as completed_subtasks
            FROM goals g
            LEFT JOIN subtasks s ON g.id = s.goal_id
            GROUP BY g.id
        """)
        goal_rows = cursor.fetchall()
        
        goals_progress = 0.0
        if goal_rows:
            total_progress = 0
            goals_with_subtasks = 0
            for row in goal_rows:
                total = row["total_subtasks"] or 0
                completed = row["completed_subtasks"] or 0
                if total > 0:
                    total_progress += (completed / total * 100)
                    goals_with_subtasks += 1
            goals_progress = total_progress / goals_with_subtasks if goals_with_subtasks > 0 else 0
        
        # Привычки
        cursor.execute("SELECT COUNT(*) as total FROM habits")
        habits_total = cursor.fetchone()["total"] or 0
        
        cursor.execute(f"""
            SELECT COUNT(DISTINCT habit_id) as completed
            FROM habit_completions
            WHERE date IN ({placeholders}) AND completed = 1
        """, last_7_days)
        habits_completed = cursor.fetchone()["completed"] or 0
        
        # Среднее настроение
        cursor.execute(f"""
            SELECT AVG(mood) as avg_mood
            FROM mood_entries
            WHERE date IN ({placeholders}) AND mood IS NOT NULL
        """, last_7_days)
        row = cursor.fetchone()
        avg_mood = float(row["avg_mood"]) if row["avg_mood"] else 0.0
        
        return {
            "week_start": week_start,
            "week_end": week_end,
            "todos_completed": todos_completed,
            "todos_total": todos_total,
            "goals_progress": round(goals_progress, 1),
            "habits_completed": habits_completed,
            "habits_total": habits_total,
            "avg_mood": round(avg_mood, 1)
        }

