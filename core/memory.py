import sqlite3
import logging
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryManager:
    _instance = None
    DB_PATH = "localmolt.db"

    def __init__(self):
        self._init_db()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MemoryManager()
        return cls._instance

    def _init_db(self):
        """Initialize the SQLite database schema."""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Facts Table: Validated knowledge about user/world
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facts (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP
                )
            ''')

            # Interactions Table: Chat history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP,
                    session_id TEXT
                )
            ''')
            
            # Projects Table: Long-running task contexts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    status TEXT,
                    context_data TEXT,
                    updated_at TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"MemoryManager initialized at {self.DB_PATH}")
        except Exception as e:
            logger.critical(f"Failed to init Memory DB: {e}")

    def remember(self, key: str, value: Any):
        """Store a fact."""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            timestamp = datetime.now().isoformat()
            
            # Serialize if not string
            if not isinstance(value, str):
                val_str = json.dumps(value)
            else:
                val_str = value

            conn.execute('''
                INSERT INTO facts (key, value, updated_at) 
                VALUES (?, ?, ?) 
                ON CONFLICT(key) DO UPDATE SET 
                    value=excluded.value, 
                    updated_at=excluded.updated_at
            ''', (key, val_str, timestamp))
            
            conn.commit()
            conn.close()
            logger.info(f"Remembered: {key} = {val_str}")
        except Exception as e:
            logger.error(f"Failed to remember {key}: {e}")

    def recall(self, key: str) -> Optional[Any]:
        """Retrieve a fact."""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM facts WHERE key = ?', (key,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                val = row[0]
                # Try to auto-deserialize JSON
                try:
                    return json.loads(val)
                except:
                    return val
            return None
        except Exception as e:
            logger.error(f"Failed to recall {key}: {e}")
            return None

    def log_interaction(self, role: str, content: str, session_id: str = "default"):
        """Log a chat message."""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            timestamp = datetime.now().isoformat()
            conn.execute('''
                INSERT INTO interactions (role, content, timestamp, session_id)
                VALUES (?, ?, ?, ?)
            ''', (role, content, timestamp, session_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")

    def get_recent_history(self, limit: int = 10, session_id: str = "default") -> List[Dict]:
        """Get recent chat history."""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content, timestamp FROM interactions 
                WHERE session_id = ? 
                ORDER BY id DESC LIMIT ?
            ''', (session_id, limit))
            rows = cursor.fetchall()
            conn.close()
            
            history = [{"role": row["role"], "content": row["content"], "timestamp": row["timestamp"]} for row in rows]
            return history[::-1] # Reverse to chrono order
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
