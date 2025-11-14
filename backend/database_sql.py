"""
SQL схемы для создания таблиц
"""
def get_sql_schema():
    """Возвращает список SQL команд для создания таблиц"""
    return [
        # Таблица для задач (todos)
        """
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER DEFAULT 0,
            due_date TEXT,
            reminder TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Таблица для целей (goals)
        """
        CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            expanded INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Таблица для подзадач целей (subtasks)
        """
        CREATE TABLE IF NOT EXISTS subtasks (
            id TEXT PRIMARY KEY,
            goal_id TEXT NOT NULL,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
        )
        """,
        
        # Таблица для привычек (habits)
        """
        CREATE TABLE IF NOT EXISTS habits (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Таблица для отметок выполнения привычек (habit_completions)
        """
        CREATE TABLE IF NOT EXISTS habit_completions (
            id SERIAL PRIMARY KEY,
            habit_id TEXT NOT NULL,
            date TEXT NOT NULL,
            completed INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
            UNIQUE(habit_id, date)
        )
        """,
        
        # Таблица для данных о воде (water_data)
        """
        CREATE TABLE IF NOT EXISTS water_data (
            date TEXT PRIMARY KEY,
            amount INTEGER DEFAULT 0,
            goal INTEGER DEFAULT 2000,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Таблица для записей настроения (mood_entries)
        """
        CREATE TABLE IF NOT EXISTS mood_entries (
            date TEXT PRIMARY KEY,
            mood INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Таблица для эмоций (emotions)
        """
        CREATE TABLE IF NOT EXISTS emotions (
            id SERIAL PRIMARY KEY,
            mood_date TEXT NOT NULL,
            emotion TEXT NOT NULL,
            FOREIGN KEY (mood_date) REFERENCES mood_entries(date) ON DELETE CASCADE
        )
        """
    ]

