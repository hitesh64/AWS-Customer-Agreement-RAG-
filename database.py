import sqlite3
import logging
import os
from config import DB_PATH

logger = logging.getLogger(__name__)

def get_db_connection():
    # Yeh line automatically folder bana degi agar wo nahi hoga
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                answer_found BOOLEAN NOT NULL,
                response_time REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def log_query(question: str, answer: str, answer_found: bool, response_time: float):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO query_logs (question, answer, answer_found, response_time)
            VALUES (?, ?, ?, ?)
        ''', (question, answer, answer_found, response_time))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error logging query to database: {e}")