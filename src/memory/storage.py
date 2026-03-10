"""SQLite storage for research history."""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import aiosqlite

from src.utils.config import config


class Storage:
    """SQLite-based storage for research history."""

    def __init__(self, db_path: str = "research_history.db"):
        self.db_path = db_path
        self._initialized = False

    async def initialize(self):
        """Initialize the database schema."""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS research_history (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    clarified_query TEXT,
                    final_answer TEXT,
                    sources TEXT,
                    cost REAL,
                    duration_seconds REAL,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

        self._initialized = True

    async def save_research(
        self,
        research_id: str,
        query: str,
        clarified_query: str,
        final_answer: str,
        sources: List[Dict[str, str]],
        cost: float,
        duration_seconds: float,
        status: str
    ) -> str:
        """Save a research result to the database."""
        await self.initialize()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO research_history 
                (id, query, clarified_query, final_answer, sources, cost, duration_seconds, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    research_id,
                    query,
                    clarified_query,
                    final_answer,
                    str(sources),  # Store as string
                    cost,
                    duration_seconds,
                    status
                )
            )
            await db.commit()

        return research_id

    async def get_research(self, research_id: str) -> Optional[Dict[str, Any]]:
        """Get a research result by ID."""
        await self.initialize()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM research_history WHERE id = ?",
                (research_id,)
            ) as cursor:
                row = await cursor.fetchone()

        if row:
            return dict(row)
        return None

    async def get_research_history(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get research history with pagination."""
        await self.initialize()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT id, query, final_answer, cost, duration_seconds, status, created_at
                FROM research_history
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            ) as cursor:
                rows = await cursor.fetchall()

        return [dict(row) for row in rows]

    async def delete_research(self, research_id: str) -> bool:
        """Delete a research result."""
        await self.initialize()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM research_history WHERE id = ?",
                (research_id,)
            )
            await db.commit()

        return cursor.rowcount > 0


# Singleton instance
storage = Storage()
