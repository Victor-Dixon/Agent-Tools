#!/usr/bin/env python3
"""
Analytics Engine
================

Processes player data to generate insights and metrics.
Provides engagement analysis, retention metrics, and trends.
"""

import logging
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .player_database import PlayerDatabase

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Analytics engine for player data.
    
    Features:
    - Engagement metrics
    - Retention analysis
    - Peak time detection
    - Player segmentation
    - Trend analysis
    """
    
    def __init__(self, database: Optional[PlayerDatabase] = None):
        self.db = database or PlayerDatabase()
    
    def get_engagement_metrics(
        self,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Calculate engagement metrics for the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Engagement metrics
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db.db_path) as conn:
            # Daily Active Users (DAU)
            dau_query = """
                SELECT DATE(start_time) as day, COUNT(DISTINCT player_id) as count
                FROM sessions
                WHERE start_time >= ?
                GROUP BY DATE(start_time)
                ORDER BY day
            """
            dau_data = conn.execute(dau_query, (cutoff,)).fetchall()
            
            # Total unique players in period
            unique_players = conn.execute(
                """SELECT COUNT(DISTINCT player_id) FROM sessions 
                   WHERE start_time >= ?""",
                (cutoff,)
            ).fetchone()[0]
            
            # Total sessions
            total_sessions = conn.execute(
                """SELECT COUNT(*) FROM sessions WHERE start_time >= ?""",
                (cutoff,)
            ).fetchone()[0]
            
            # Total playtime
            total_playtime = conn.execute(
                """SELECT SUM(duration_minutes) FROM sessions 
                   WHERE start_time >= ? AND end_time IS NOT NULL""",
                (cutoff,)
            ).fetchone()[0] or 0
            
            # Average session duration
            avg_session = conn.execute(
                """SELECT AVG(duration_minutes) FROM sessions 
                   WHERE start_time >= ? AND end_time IS NOT NULL""",
                (cutoff,)
            ).fetchone()[0] or 0
            
            # Sessions per player
            sessions_per_player = total_sessions / unique_players if unique_players > 0 else 0
        
        # Calculate DAU average
        dau_values = [row[1] for row in dau_data]
        avg_dau = sum(dau_values) / len(dau_values) if dau_values else 0
        max_dau = max(dau_values) if dau_values else 0
        
        return {
            "period_days": days,
            "unique_players": unique_players,
            "total_sessions": total_sessions,
            "total_playtime_hours": round(total_playtime / 60, 1),
            "avg_session_minutes": round(avg_session, 1),
            "sessions_per_player": round(sessions_per_player, 2),
            "dau": {
                "average": round(avg_dau, 1),
                "max": max_dau,
                "data": [{"date": row[0], "count": row[1]} for row in dau_data[-14:]],
            },
        }
    
    def get_retention_metrics(
        self,
        cohort_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate player retention metrics.
        
        Args:
            cohort_date: Start date for cohort (default: 30 days ago)
            
        Returns:
            Retention metrics
        """
        if cohort_date is None:
            cohort_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        with sqlite3.connect(self.db.db_path) as conn:
            # Get players who started in the cohort period (first session)
            cohort_query = """
                SELECT player_id, MIN(DATE(start_time)) as first_day
                FROM sessions
                GROUP BY player_id
                HAVING first_day >= ?
            """
            
            cohort_players = conn.execute(
                cohort_query, (cohort_date,)
            ).fetchall()
            
            if not cohort_players:
                return {"error": "No players in cohort period"}
            
            cohort_size = len(cohort_players)
            player_ids = [p[0] for p in cohort_players]
            
            # Calculate retention for each day
            retention = {}
            for day_offset in [1, 7, 14, 30]:
                target_date = (
                    datetime.strptime(cohort_date, "%Y-%m-%d") + 
                    timedelta(days=day_offset)
                ).strftime("%Y-%m-%d")
                
                # Count players who returned on or after target day
                placeholders = ",".join("?" * len(player_ids))
                returned = conn.execute(
                    f"""SELECT COUNT(DISTINCT player_id) FROM sessions
                       WHERE player_id IN ({placeholders})
                       AND DATE(start_time) >= ?""",
                    (*player_ids, target_date)
                ).fetchone()[0]
                
                retention[f"day_{day_offset}"] = {
                    "returned": returned,
                    "rate": round((returned / cohort_size) * 100, 1),
                }
        
        return {
            "cohort_date": cohort_date,
            "cohort_size": cohort_size,
            "retention": retention,
        }
    
    def get_peak_hours(
        self,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Analyze peak playing hours.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Peak hour analysis
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db.db_path) as conn:
            # Sessions by hour
            hourly_query = """
                SELECT strftime('%H', start_time) as hour, COUNT(*) as count
                FROM sessions
                WHERE start_time >= ?
                GROUP BY hour
                ORDER BY hour
            """
            hourly_data = conn.execute(hourly_query, (cutoff,)).fetchall()
            
            # Sessions by day of week
            daily_query = """
                SELECT strftime('%w', start_time) as dow, COUNT(*) as count
                FROM sessions
                WHERE start_time >= ?
                GROUP BY dow
                ORDER BY dow
            """
            daily_data = conn.execute(daily_query, (cutoff,)).fetchall()
        
        # Find peaks
        hour_counts = {int(row[0]): row[1] for row in hourly_data}
        peak_hour = max(hour_counts, key=hour_counts.get) if hour_counts else 0
        
        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", 
                     "Thursday", "Friday", "Saturday"]
        day_counts = {int(row[0]): row[1] for row in daily_data}
        peak_day = max(day_counts, key=day_counts.get) if day_counts else 0
        
        return {
            "period_days": days,
            "hourly_distribution": [
                {"hour": h, "sessions": hour_counts.get(h, 0)}
                for h in range(24)
            ],
            "daily_distribution": [
                {"day": day_names[d], "sessions": day_counts.get(d, 0)}
                for d in range(7)
            ],
            "peak_hour": {
                "hour": peak_hour,
                "time": f"{peak_hour:02d}:00",
                "sessions": hour_counts.get(peak_hour, 0),
            },
            "peak_day": {
                "day": day_names[peak_day],
                "sessions": day_counts.get(peak_day, 0),
            },
        }
    
    def get_player_segments(self) -> Dict[str, Any]:
        """
        Segment players by engagement level.
        
        Returns:
            Player segmentation
        """
        with sqlite3.connect(self.db.db_path) as conn:
            # Get all players with playtime
            players = conn.execute(
                """SELECT player_id, username, total_playtime_minutes, 
                          session_count, last_seen
                   FROM players
                   ORDER BY total_playtime_minutes DESC"""
            ).fetchall()
        
        if not players:
            return {"segments": {}, "total_players": 0}
        
        segments = {
            "whales": [],      # Top 10% by playtime
            "regulars": [],    # Next 30%
            "casuals": [],     # Next 40%
            "churned": [],     # Haven't played in 14+ days
            "new": [],         # Played less than 3 sessions
        }
        
        now = datetime.now()
        churn_threshold = now - timedelta(days=14)
        
        for i, player in enumerate(players):
            player_id, username, playtime, sessions, last_seen = player
            
            last_seen_dt = datetime.fromisoformat(last_seen) if last_seen else now
            
            player_data = {
                "player_id": player_id,
                "username": username,
                "playtime_hours": round(playtime / 60, 1),
                "sessions": sessions,
            }
            
            # Segment classification
            if last_seen_dt < churn_threshold:
                segments["churned"].append(player_data)
            elif sessions < 3:
                segments["new"].append(player_data)
            else:
                percentile = i / len(players)
                if percentile < 0.1:
                    segments["whales"].append(player_data)
                elif percentile < 0.4:
                    segments["regulars"].append(player_data)
                else:
                    segments["casuals"].append(player_data)
        
        return {
            "total_players": len(players),
            "segments": {
                name: {
                    "count": len(players_list),
                    "percentage": round((len(players_list) / len(players)) * 100, 1),
                    "top_players": players_list[:5],
                }
                for name, players_list in segments.items()
            },
        }
    
    def get_leaderboard(
        self,
        metric: str = "playtime",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get leaderboard by specified metric.
        
        Args:
            metric: playtime, sessions, streak
            limit: Number of entries
            
        Returns:
            Leaderboard entries
        """
        with sqlite3.connect(self.db.db_path) as conn:
            if metric == "playtime":
                query = """
                    SELECT player_id, username, total_playtime_minutes as value
                    FROM players
                    ORDER BY total_playtime_minutes DESC
                    LIMIT ?
                """
                label = "hours"
                divisor = 60
            elif metric == "sessions":
                query = """
                    SELECT player_id, username, session_count as value
                    FROM players
                    ORDER BY session_count DESC
                    LIMIT ?
                """
                label = "sessions"
                divisor = 1
            else:
                return []
            
            rows = conn.execute(query, (limit,)).fetchall()
        
        return [
            {
                "rank": i + 1,
                "player_id": row[0],
                "username": row[1],
                "value": round(row[2] / divisor, 1) if divisor > 1 else row[2],
                "label": label,
            }
            for i, row in enumerate(rows)
        ]
    
    def get_player_profile(
        self,
        player_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed player profile with analytics.
        
        Args:
            player_id: Player's unique identifier
            
        Returns:
            Comprehensive player profile
        """
        player = self.db.get_player(player_id)
        if not player:
            return None
        
        sessions = self.db.get_player_sessions(player_id, limit=100)
        events = self.db.get_player_events(player_id, limit=50)
        
        # Calculate additional metrics
        if sessions:
            session_durations = [s.duration_minutes for s in sessions if s.duration_minutes > 0]
            avg_session = sum(session_durations) / len(session_durations) if session_durations else 0
            
            # Play pattern
            play_hours = defaultdict(int)
            for session in sessions:
                try:
                    hour = datetime.fromisoformat(session.start_time).hour
                    play_hours[hour] += 1
                except:
                    pass
            
            favorite_hour = max(play_hours, key=play_hours.get) if play_hours else 0
        else:
            avg_session = 0
            favorite_hour = 0
        
        # Rank
        with sqlite3.connect(self.db.db_path) as conn:
            rank = conn.execute(
                """SELECT COUNT(*) + 1 FROM players 
                   WHERE total_playtime_minutes > ?""",
                (player.total_playtime_minutes,)
            ).fetchone()[0]
            
            total_players = conn.execute(
                "SELECT COUNT(*) FROM players"
            ).fetchone()[0]
        
        return {
            "player": player.to_dict(),
            "analytics": {
                "rank": rank,
                "total_players": total_players,
                "percentile": round((1 - rank / total_players) * 100, 1) if total_players > 0 else 0,
                "avg_session_minutes": round(avg_session, 1),
                "favorite_play_hour": f"{favorite_hour:02d}:00",
            },
            "recent_sessions": [s.to_dict() for s in sessions[:10]],
            "recent_events": events[:10],
        }
    
    def get_server_comparison(
        self,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Compare metrics across different servers.
        
        Args:
            days: Period to analyze
            
        Returns:
            Server comparison
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db.db_path) as conn:
            query = """
                SELECT 
                    server_name,
                    COUNT(*) as sessions,
                    COUNT(DISTINCT player_id) as unique_players,
                    SUM(duration_minutes) as total_playtime,
                    AVG(duration_minutes) as avg_session
                FROM sessions
                WHERE start_time >= ? AND end_time IS NOT NULL
                GROUP BY server_name
                ORDER BY sessions DESC
            """
            
            rows = conn.execute(query, (cutoff,)).fetchall()
        
        return {
            "period_days": days,
            "servers": [
                {
                    "server_name": row[0],
                    "sessions": row[1],
                    "unique_players": row[2],
                    "total_playtime_hours": round((row[3] or 0) / 60, 1),
                    "avg_session_minutes": round(row[4] or 0, 1),
                }
                for row in rows
            ],
        }
