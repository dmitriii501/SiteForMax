"""
Работа с базой данных (поддержка SQLite и PostgreSQL)
"""
import os
from contextlib import contextmanager
from typing import Generator

# Определяем тип базы данных по DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./max_personal_effect.db")

if DATABASE_URL.startswith("postgres"):
    # PostgreSQL для Render
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        @contextmanager
        def get_db() -> Generator:
            """Контекстный менеджер для работы с PostgreSQL"""
            parsed = urlparse(DATABASE_URL)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password
            )
            conn.set_session(autocommit=False)
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
                
    except ImportError:
        # Если psycopg2 не установлен, используем SQLite
        DATABASE_URL = "sqlite:///./max_personal_effect.db"
        import sqlite3
        from config import DATABASE_URL as SQLITE_DB
        
        @contextmanager
        def get_db() -> Generator:
            conn = sqlite3.connect(SQLITE_DB)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
else:
    # SQLite для локальной разработки
    import sqlite3
    from config import DATABASE_URL as SQLITE_DB
    
    @contextmanager
    def get_db() -> Generator:
        """Контекстный менеджер для работы с SQLite"""
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

def init_db():
    """Инициализация базы данных и создание таблиц"""
    from database_sql import get_sql_schema
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Получаем SQL схему
        schema = get_sql_schema()
        
        for statement in schema:
            # Адаптируем SQL для разных БД
            if DATABASE_URL.startswith("postgres"):
                # PostgreSQL - заменяем AUTOINCREMENT на SERIAL
                sql = statement.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            else:
                # SQLite - заменяем SERIAL на AUTOINCREMENT
                sql = statement.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
            
            cursor.execute(sql)
        
        conn.commit()
