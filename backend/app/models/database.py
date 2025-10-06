"""
SQLite database setup for interaction logging.
Uses aiosqlite for async database operations.
"""

import aiosqlite
import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path


class Database:
    """Manages SQLite database for interaction logging"""
    
    def __init__(self, db_path: str = "data/interactions.db"):
        self.db_path = db_path
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Create interactions table if it doesn't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_query TEXT NOT NULL,
                    retrieved_faq_ids TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    response_time_ms INTEGER NOT NULL,
                    relevance_scores TEXT NOT NULL,
                    error_occurred BOOLEAN DEFAULT FALSE
                )
            """)
            await db.commit()
    
    async def log_interaction(
        self,
        user_query: str,
        retrieved_faq_ids: List[str],
        ai_response: str,
        response_time_ms: int,
        relevance_scores: List[float],
        error_occurred: bool = False
    ) -> int:
        """
        Insert a new interaction log entry.
        Returns the ID of the inserted row.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO interactions (
                    user_query, retrieved_faq_ids, ai_response, 
                    response_time_ms, relevance_scores, error_occurred
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_query,
                json.dumps(retrieved_faq_ids),
                ai_response,
                response_time_ms,
                json.dumps(relevance_scores),
                error_occurred
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def get_logs(self, limit: int = 100) -> List[dict]:
        """
        Retrieve recent interaction logs.
        Returns list of log entries ordered by most recent first.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM interactions 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_stats(self) -> dict:
        """Get statistics about logged interactions"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END) as total_errors
                FROM interactions
            """) as cursor:
                row = await cursor.fetchone()
                return {
                    "total_queries": row[0] or 0,
                    "avg_response_time_ms": round(row[1] or 0, 2),
                    "total_errors": row[2] or 0
                }
