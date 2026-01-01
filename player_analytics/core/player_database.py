#!/usr/bin/env python3
"""
Player Database
===============

Stores and manages player data for analytics.
Uses SQLite for local storage with optional external DB support.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Player:
    """Represents a player record."""
    player_id: str
    username: str
    first_seen: str
    last_seen: str
    total_playtime_minutes: int = 0
    session_count: int = 0
    discord_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "username": self.username,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "total_playtime_minutes": self.total_playtime_minutes,
            "total_playtime_human": self._format_playtime(self.total_playtime_minutes),
            "session_count": self.session_count,
            "avg_session_minutes": (
                self.total_playtime_minutes / self.session_count 
                if self.session_count > 0 else 0
            ),
            "discord_id": self.discord_id,
            "tags": self.tags,
            "custom_data": self.custom_data,
        }
    
    @staticmethod
    def _format_playtime(minutes: int) -> str:
        if minutes < 60:
            return f"{minutes}m"
        elif minutes < 1440:
            return f"{minutes // 60}h {minutes % 60}m"
        else:
            days = minutes // 1440
            hours = (minutes % 1440) // 60
            return f"{days}d {hours}h"


@dataclass
class Session:
    """Represents a play session."""
    session_id: str
    player_id: str
    server_name: str
    start_time: str
    end_time: Optional[str] = None
    duration_minutes: int = 0
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def is_active(self) -> bool:
        return self.end_time is None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "player_id": self.player_id,
            "server_name": self.server_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_minutes": self.duration_minutes,
            "is_active": self.is_active,
            "events": self.events,
        }


class PlayerDatabase:
    """
    SQLite-based player database for analytics.
    
    Features:
    - Player profile management
    - Session history
    - Event logging
    - Efficient querying
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / ".player_analytics" / "players.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    total_playtime_minutes INTEGER DEFAULT 0,
                    session_count INTEGER DEFAULT 0,
                    discord_id TEXT,
                    tags TEXT DEFAULT '[]',
                    custom_data TEXT DEFAULT '{}'
                );
                
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    player_id TEXT NOT NULL,
                    server_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_minutes INTEGER DEFAULT 0,
                    events TEXT DEFAULT '[]',
                    FOREIGN KEY (player_id) REFERENCES players(player_id)
                );
                
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT NOT NULL,
                    session_id TEXT,
                    event_type TEXT NOT NULL,
                    event_data TEXT DEFAULT '{}',
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (player_id) REFERENCES players(player_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_sessions_player ON sessions(player_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_server ON sessions(server_name);
                CREATE INDEX IF NOT EXISTS idx_sessions_time ON sessions(start_time);
                CREATE INDEX IF NOT EXISTS idx_events_player ON events(player_id);
                CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
                CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp);
            """)
    
    def get_or_create_player(
        self,
        player_id: str,
        username: str,
    ) -> Player:
        """Get existing player or create new one."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM players WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return Player(
                    player_id=row["player_id"],
                    username=row["username"],
                    first_seen=row["first_seen"],
                    last_seen=row["last_seen"],
                    total_playtime_minutes=row["total_playtime_minutes"],
                    session_count=row["session_count"],
                    discord_id=row["discord_id"],
                    tags=json.loads(row["tags"]),
                    custom_data=json.loads(row["custom_data"]),
                )
            else:
                # Create new player
                now = datetime.now().isoformat()
                conn.execute(
                    """INSERT INTO players 
                       (player_id, username, first_seen, last_seen) 
                       VALUES (?, ?, ?, ?)""",
                    (player_id, username, now, now)
                )
                return Player(
                    player_id=player_id,
                    username=username,
                    first_seen=now,
                    last_seen=now,
                )
    
    def update_player(self, player: Player) -> None:
        """Update player record."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE players SET
                   username = ?,
                   last_seen = ?,
                   total_playtime_minutes = ?,
                   session_count = ?,
                   discord_id = ?,
                   tags = ?,
                   custom_data = ?
                   WHERE player_id = ?""",
                (
                    player.username,
                    player.last_seen,
                    player.total_playtime_minutes,
                    player.session_count,
                    player.discord_id,
                    json.dumps(player.tags),
                    json.dumps(player.custom_data),
                    player.player_id,
                )
            )
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM players WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return Player(
                    player_id=row["player_id"],
                    username=row["username"],
                    first_seen=row["first_seen"],
                    last_seen=row["last_seen"],
                    total_playtime_minutes=row["total_playtime_minutes"],
                    session_count=row["session_count"],
                    discord_id=row["discord_id"],
                    tags=json.loads(row["tags"]),
                    custom_data=json.loads(row["custom_data"]),
                )
            return None
    
    def search_players(
        self,
        query: str,
        limit: int = 50,
    ) -> List[Player]:
        """Search players by username."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM players 
                   WHERE username LIKE ? 
                   ORDER BY total_playtime_minutes DESC
                   LIMIT ?""",
                (f"%{query}%", limit)
            )
            
            return [
                Player(
                    player_id=row["player_id"],
                    username=row["username"],
                    first_seen=row["first_seen"],
                    last_seen=row["last_seen"],
                    total_playtime_minutes=row["total_playtime_minutes"],
                    session_count=row["session_count"],
                    discord_id=row["discord_id"],
                    tags=json.loads(row["tags"]),
                    custom_data=json.loads(row["custom_data"]),
                )
                for row in cursor.fetchall()
            ]
    
    def create_session(
        self,
        player_id: str,
        server_name: str,
    ) -> Session:
        """Create a new session."""
        session_id = f"{player_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        start_time = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO sessions 
                   (session_id, player_id, server_name, start_time)
                   VALUES (?, ?, ?, ?)""",
                (session_id, player_id, server_name, start_time)
            )
        
        return Session(
            session_id=session_id,
            player_id=player_id,
            server_name=server_name,
            start_time=start_time,
        )
    
    def end_session(
        self,
        session_id: str,
    ) -> Optional[Session]:
        """End a session and calculate duration."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get session
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            start_time = datetime.fromisoformat(row["start_time"])
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds() / 60)
            
            # Update session
            conn.execute(
                """UPDATE sessions SET
                   end_time = ?,
                   duration_minutes = ?
                   WHERE session_id = ?""",
                (end_time.isoformat(), duration, session_id)
            )
            
            # Update player stats
            conn.execute(
                """UPDATE players SET
                   last_seen = ?,
                   total_playtime_minutes = total_playtime_minutes + ?,
                   session_count = session_count + 1
                   WHERE player_id = ?""",
                (end_time.isoformat(), duration, row["player_id"])
            )
            
            return Session(
                session_id=session_id,
                player_id=row["player_id"],
                server_name=row["server_name"],
                start_time=row["start_time"],
                end_time=end_time.isoformat(),
                duration_minutes=duration,
            )
    
    def get_active_sessions(self, server_name: Optional[str] = None) -> List[Session]:
        """Get all active (ongoing) sessions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if server_name:
                cursor = conn.execute(
                    """SELECT * FROM sessions 
                       WHERE end_time IS NULL AND server_name = ?""",
                    (server_name,)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM sessions WHERE end_time IS NULL"
                )
            
            return [
                Session(
                    session_id=row["session_id"],
                    player_id=row["player_id"],
                    server_name=row["server_name"],
                    start_time=row["start_time"],
                )
                for row in cursor.fetchall()
            ]
    
    def get_player_sessions(
        self,
        player_id: str,
        limit: int = 50,
    ) -> List[Session]:
        """Get session history for a player."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM sessions 
                   WHERE player_id = ?
                   ORDER BY start_time DESC
                   LIMIT ?""",
                (player_id, limit)
            )
            
            return [
                Session(
                    session_id=row["session_id"],
                    player_id=row["player_id"],
                    server_name=row["server_name"],
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    duration_minutes=row["duration_minutes"],
                )
                for row in cursor.fetchall()
            ]
    
    def log_event(
        self,
        player_id: str,
        event_type: str,
        event_data: Optional[Dict] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Log a player event."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO events 
                   (player_id, session_id, event_type, event_data, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    player_id,
                    session_id,
                    event_type,
                    json.dumps(event_data or {}),
                    datetime.now().isoformat(),
                )
            )
    
    def get_player_events(
        self,
        player_id: str,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get events for a player."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if event_type:
                cursor = conn.execute(
                    """SELECT * FROM events 
                       WHERE player_id = ? AND event_type = ?
                       ORDER BY timestamp DESC
                       LIMIT ?""",
                    (player_id, event_type, limit)
                )
            else:
                cursor = conn.execute(
                    """SELECT * FROM events 
                       WHERE player_id = ?
                       ORDER BY timestamp DESC
                       LIMIT ?""",
                    (player_id, limit)
                )
            
            return [
                {
                    "event_id": row["event_id"],
                    "player_id": row["player_id"],
                    "session_id": row["session_id"],
                    "event_type": row["event_type"],
                    "event_data": json.loads(row["event_data"]),
                    "timestamp": row["timestamp"],
                }
                for row in cursor.fetchall()
            ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            player_count = conn.execute(
                "SELECT COUNT(*) FROM players"
            ).fetchone()[0]
            
            session_count = conn.execute(
                "SELECT COUNT(*) FROM sessions"
            ).fetchone()[0]
            
            event_count = conn.execute(
                "SELECT COUNT(*) FROM events"
            ).fetchone()[0]
            
            total_playtime = conn.execute(
                "SELECT SUM(total_playtime_minutes) FROM players"
            ).fetchone()[0] or 0
            
            return {
                "total_players": player_count,
                "total_sessions": session_count,
                "total_events": event_count,
                "total_playtime_hours": total_playtime / 60,
            }
