#!/usr/bin/env python3
"""
Session Tracker
===============

Tracks player sessions in real-time.
Handles join/leave events and session lifecycle.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable

from .player_database import PlayerDatabase, Player, Session

logger = logging.getLogger(__name__)


class SessionTracker:
    """
    Real-time player session tracking.
    
    Features:
    - Player join/leave tracking
    - Active session management
    - Event hooks for notifications
    - Session duration tracking
    """
    
    def __init__(
        self,
        database: Optional[PlayerDatabase] = None,
        server_name: str = "default",
    ):
        self.db = database or PlayerDatabase()
        self.server_name = server_name
        
        # Active sessions indexed by player_id
        self._active_sessions: Dict[str, Session] = {}
        
        # Event callbacks
        self._on_join_callbacks: List[Callable] = []
        self._on_leave_callbacks: List[Callable] = []
        self._on_event_callbacks: List[Callable] = []
        
        # Restore active sessions from DB
        self._restore_active_sessions()
    
    def _restore_active_sessions(self) -> None:
        """Restore active sessions from database on startup."""
        active = self.db.get_active_sessions(self.server_name)
        for session in active:
            self._active_sessions[session.player_id] = session
        
        if active:
            logger.info(f"Restored {len(active)} active sessions")
    
    def on_join(self, callback: Callable[[Player, Session], None]) -> None:
        """Register a callback for player join events."""
        self._on_join_callbacks.append(callback)
    
    def on_leave(self, callback: Callable[[Player, Session], None]) -> None:
        """Register a callback for player leave events."""
        self._on_leave_callbacks.append(callback)
    
    def on_event(self, callback: Callable[[str, Dict], None]) -> None:
        """Register a callback for all events."""
        self._on_event_callbacks.append(callback)
    
    def player_join(
        self,
        player_id: str,
        username: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Handle player join event.
        
        Args:
            player_id: Unique player identifier
            username: Player's display name
            metadata: Optional additional data
            
        Returns:
            Join result with session info
        """
        # Check if already in an active session
        if player_id in self._active_sessions:
            existing = self._active_sessions[player_id]
            return {
                "success": False,
                "error": "Player already has active session",
                "session_id": existing.session_id,
            }
        
        # Get or create player record
        player = self.db.get_or_create_player(player_id, username)
        
        # Update username if changed
        if player.username != username:
            player.username = username
            self.db.update_player(player)
        
        # Create session
        session = self.db.create_session(player_id, self.server_name)
        self._active_sessions[player_id] = session
        
        # Log event
        self.db.log_event(
            player_id=player_id,
            event_type="join",
            event_data=metadata or {},
            session_id=session.session_id,
        )
        
        # Trigger callbacks
        for callback in self._on_join_callbacks:
            try:
                callback(player, session)
            except Exception as e:
                logger.error(f"Join callback error: {e}")
        
        for callback in self._on_event_callbacks:
            try:
                callback("join", {
                    "player": player.to_dict(),
                    "session": session.to_dict(),
                })
            except Exception as e:
                logger.error(f"Event callback error: {e}")
        
        logger.info(f"Player joined: {username} ({player_id})")
        
        return {
            "success": True,
            "player": player.to_dict(),
            "session": session.to_dict(),
            "is_new_player": player.session_count == 0,
        }
    
    def player_leave(
        self,
        player_id: str,
        reason: str = "disconnect",
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Handle player leave event.
        
        Args:
            player_id: Player's unique identifier
            reason: Reason for leaving (disconnect, kick, ban, etc.)
            metadata: Optional additional data
            
        Returns:
            Leave result with session summary
        """
        if player_id not in self._active_sessions:
            return {
                "success": False,
                "error": "No active session for player",
            }
        
        session = self._active_sessions[player_id]
        
        # End session
        ended_session = self.db.end_session(session.session_id)
        del self._active_sessions[player_id]
        
        # Get updated player
        player = self.db.get_player(player_id)
        
        # Log event
        self.db.log_event(
            player_id=player_id,
            event_type="leave",
            event_data={
                "reason": reason,
                "duration_minutes": ended_session.duration_minutes if ended_session else 0,
                **(metadata or {}),
            },
            session_id=session.session_id,
        )
        
        # Trigger callbacks
        for callback in self._on_leave_callbacks:
            try:
                callback(player, ended_session)
            except Exception as e:
                logger.error(f"Leave callback error: {e}")
        
        for callback in self._on_event_callbacks:
            try:
                callback("leave", {
                    "player": player.to_dict() if player else {},
                    "session": ended_session.to_dict() if ended_session else {},
                    "reason": reason,
                })
            except Exception as e:
                logger.error(f"Event callback error: {e}")
        
        logger.info(
            f"Player left: {player.username if player else player_id} "
            f"(session: {ended_session.duration_minutes if ended_session else 0}m)"
        )
        
        return {
            "success": True,
            "player": player.to_dict() if player else None,
            "session": ended_session.to_dict() if ended_session else None,
            "reason": reason,
        }
    
    def log_player_event(
        self,
        player_id: str,
        event_type: str,
        event_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Log a custom player event.
        
        Args:
            player_id: Player's unique identifier
            event_type: Type of event (death, achievement, etc.)
            event_data: Event-specific data
            
        Returns:
            Log result
        """
        session_id = None
        if player_id in self._active_sessions:
            session_id = self._active_sessions[player_id].session_id
        
        self.db.log_event(
            player_id=player_id,
            event_type=event_type,
            event_data=event_data or {},
            session_id=session_id,
        )
        
        # Trigger event callbacks
        for callback in self._on_event_callbacks:
            try:
                callback(event_type, {
                    "player_id": player_id,
                    "session_id": session_id,
                    "data": event_data,
                })
            except Exception as e:
                logger.error(f"Event callback error: {e}")
        
        return {
            "success": True,
            "event_type": event_type,
            "player_id": player_id,
            "session_id": session_id,
        }
    
    def get_active_players(self) -> List[Dict[str, Any]]:
        """Get list of currently active players."""
        result = []
        
        for player_id, session in self._active_sessions.items():
            player = self.db.get_player(player_id)
            if player:
                # Calculate current session duration
                start = datetime.fromisoformat(session.start_time)
                duration = int((datetime.now() - start).total_seconds() / 60)
                
                result.append({
                    "player": player.to_dict(),
                    "session": session.to_dict(),
                    "current_session_minutes": duration,
                })
        
        return result
    
    def get_player_count(self) -> int:
        """Get current player count."""
        return len(self._active_sessions)
    
    def is_player_online(self, player_id: str) -> bool:
        """Check if a player is currently online."""
        return player_id in self._active_sessions
    
    def get_session_info(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get current session info for a player."""
        if player_id not in self._active_sessions:
            return None
        
        session = self._active_sessions[player_id]
        start = datetime.fromisoformat(session.start_time)
        duration = int((datetime.now() - start).total_seconds() / 60)
        
        return {
            "session": session.to_dict(),
            "current_duration_minutes": duration,
        }
    
    def end_all_sessions(self, reason: str = "server_shutdown") -> int:
        """End all active sessions (e.g., on server shutdown)."""
        count = 0
        
        for player_id in list(self._active_sessions.keys()):
            result = self.player_leave(player_id, reason=reason)
            if result["success"]:
                count += 1
        
        logger.info(f"Ended {count} sessions due to: {reason}")
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current tracking statistics."""
        db_stats = self.db.get_stats()
        
        return {
            "server_name": self.server_name,
            "active_players": len(self._active_sessions),
            **db_stats,
        }
