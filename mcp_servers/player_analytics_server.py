#!/usr/bin/env python3
"""
MCP Server for Player Analytics
=================================

Exposes player analytics operations via Model Context Protocol.

Tools:
- Session tracking (join/leave)
- Player profiles and search
- Engagement metrics
- Leaderboards
- Reports
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "player_analytics"))

try:
    from core.player_database import PlayerDatabase
    from core.session_tracker import SessionTracker
    from core.analytics_engine import AnalyticsEngine
    from core.report_generator import ReportGenerator
    HAS_ANALYTICS = True
except ImportError as e:
    HAS_ANALYTICS = False
    import_error = str(e)


# Global instances
_db: Optional[PlayerDatabase] = None
_tracker: Optional[SessionTracker] = None
_analytics: Optional[AnalyticsEngine] = None
_reports: Optional[ReportGenerator] = None


def _get_db() -> PlayerDatabase:
    global _db
    if _db is None:
        _db = PlayerDatabase()
    return _db


def _get_tracker(server_name: str = "default") -> SessionTracker:
    global _tracker
    if _tracker is None or _tracker.server_name != server_name:
        _tracker = SessionTracker(_get_db(), server_name)
    return _tracker


def _get_analytics() -> AnalyticsEngine:
    global _analytics
    if _analytics is None:
        _analytics = AnalyticsEngine(_get_db())
    return _analytics


def _get_reports() -> ReportGenerator:
    global _reports
    if _reports is None:
        _reports = ReportGenerator(_get_analytics())
    return _reports


# ============ Session Tracking ============

def player_join(
    player_id: str,
    username: str,
    server_name: str = "default",
    metadata: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Track player joining the server."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": f"Analytics not available: {import_error}"}
    
    try:
        tracker = _get_tracker(server_name)
        result = tracker.player_join(player_id, username, metadata)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def player_leave(
    player_id: str,
    server_name: str = "default",
    reason: str = "disconnect",
) -> Dict[str, Any]:
    """Track player leaving the server."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        tracker = _get_tracker(server_name)
        result = tracker.player_leave(player_id, reason)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def log_event(
    player_id: str,
    event_type: str,
    server_name: str = "default",
    event_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Log a custom player event."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        tracker = _get_tracker(server_name)
        result = tracker.log_player_event(player_id, event_type, event_data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_active_players(server_name: str = "default") -> Dict[str, Any]:
    """Get list of currently active players."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        tracker = _get_tracker(server_name)
        players = tracker.get_active_players()
        return {
            "success": True,
            "count": len(players),
            "players": players,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ Player Data ============

def get_player(player_id: str) -> Dict[str, Any]:
    """Get player profile."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        analytics = _get_analytics()
        profile = analytics.get_player_profile(player_id)
        if profile:
            return {"success": True, "profile": profile}
        return {"success": False, "error": "Player not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_players(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search for players by username."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        db = _get_db()
        players = db.search_players(query, limit)
        return {
            "success": True,
            "count": len(players),
            "players": [p.to_dict() for p in players],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_player_sessions(player_id: str, limit: int = 20) -> Dict[str, Any]:
    """Get session history for a player."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        db = _get_db()
        sessions = db.get_player_sessions(player_id, limit)
        return {
            "success": True,
            "count": len(sessions),
            "sessions": [s.to_dict() for s in sessions],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_player_events(
    player_id: str,
    event_type: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Get events for a player."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        db = _get_db()
        events = db.get_player_events(player_id, event_type, limit)
        return {
            "success": True,
            "count": len(events),
            "events": events,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ Analytics ============

def get_engagement_metrics(days: int = 30) -> Dict[str, Any]:
    """Get player engagement metrics."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        analytics = _get_analytics()
        metrics = analytics.get_engagement_metrics(days)
        return {"success": True, "metrics": metrics}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_retention_metrics(cohort_date: Optional[str] = None) -> Dict[str, Any]:
    """Get player retention metrics."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        analytics = _get_analytics()
        metrics = analytics.get_retention_metrics(cohort_date)
        return {"success": True, "metrics": metrics}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_peak_hours(days: int = 7) -> Dict[str, Any]:
    """Get peak playing hours analysis."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        analytics = _get_analytics()
        data = analytics.get_peak_hours(days)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_player_segments() -> Dict[str, Any]:
    """Get player segmentation analysis."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        analytics = _get_analytics()
        segments = analytics.get_player_segments()
        return {"success": True, "segments": segments}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_leaderboard(
    metric: str = "playtime",
    limit: int = 10,
) -> Dict[str, Any]:
    """Get player leaderboard."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        analytics = _get_analytics()
        leaderboard = analytics.get_leaderboard(metric, limit)
        return {
            "success": True,
            "metric": metric,
            "leaderboard": leaderboard,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_server_comparison(days: int = 7) -> Dict[str, Any]:
    """Compare analytics across servers."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        analytics = _get_analytics()
        comparison = analytics.get_server_comparison(days)
        return {"success": True, "comparison": comparison}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ Reports ============

def generate_daily_report(date: Optional[str] = None) -> Dict[str, Any]:
    """Generate daily analytics report."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        reports = _get_reports()
        report = reports.generate_daily_report(date)
        return {"success": True, "report": report}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_weekly_report(week_start: Optional[str] = None) -> Dict[str, Any]:
    """Generate weekly analytics report."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        reports = _get_reports()
        report = reports.generate_weekly_report(week_start)
        return {"success": True, "report": report}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_reports(report_type: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """List available reports."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        reports = _get_reports()
        report_list = reports.list_reports(report_type, limit)
        return {"success": True, "reports": report_list}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_stats() -> Dict[str, Any]:
    """Get overall analytics statistics."""
    if not HAS_ANALYTICS:
        return {"success": False, "error": "Analytics not available"}
    
    try:
        db = _get_db()
        stats = db.get_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}


# MCP Server Protocol
def main():
    """MCP server main loop."""
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            # Session Tracking
                            "player_join": {
                                "description": "Track player joining the server",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "player_id": {"type": "string"},
                                        "username": {"type": "string"},
                                        "server_name": {"type": "string", "default": "default"},
                                        "metadata": {"type": "object"},
                                    },
                                    "required": ["player_id", "username"],
                                },
                            },
                            "player_leave": {
                                "description": "Track player leaving the server",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "player_id": {"type": "string"},
                                        "server_name": {"type": "string", "default": "default"},
                                        "reason": {"type": "string", "default": "disconnect"},
                                    },
                                    "required": ["player_id"],
                                },
                            },
                            "log_event": {
                                "description": "Log a custom player event (death, achievement, etc.)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "player_id": {"type": "string"},
                                        "event_type": {"type": "string"},
                                        "server_name": {"type": "string"},
                                        "event_data": {"type": "object"},
                                    },
                                    "required": ["player_id", "event_type"],
                                },
                            },
                            "get_active_players": {
                                "description": "Get currently active players on the server",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "server_name": {"type": "string", "default": "default"},
                                    },
                                },
                            },
                            
                            # Player Data
                            "get_player": {
                                "description": "Get detailed player profile with analytics",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "player_id": {"type": "string"},
                                    },
                                    "required": ["player_id"],
                                },
                            },
                            "search_players": {
                                "description": "Search for players by username",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string"},
                                        "limit": {"type": "integer", "default": 20},
                                    },
                                    "required": ["query"],
                                },
                            },
                            "get_player_sessions": {
                                "description": "Get session history for a player",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "player_id": {"type": "string"},
                                        "limit": {"type": "integer", "default": 20},
                                    },
                                    "required": ["player_id"],
                                },
                            },
                            "get_player_events": {
                                "description": "Get events for a player",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "player_id": {"type": "string"},
                                        "event_type": {"type": "string"},
                                        "limit": {"type": "integer", "default": 50},
                                    },
                                    "required": ["player_id"],
                                },
                            },
                            
                            # Analytics
                            "get_engagement_metrics": {
                                "description": "Get player engagement metrics (DAU, sessions, playtime)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "days": {"type": "integer", "default": 30},
                                    },
                                },
                            },
                            "get_retention_metrics": {
                                "description": "Get player retention analysis",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "cohort_date": {"type": "string"},
                                    },
                                },
                            },
                            "get_peak_hours": {
                                "description": "Get peak playing hours analysis",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "days": {"type": "integer", "default": 7},
                                    },
                                },
                            },
                            "get_player_segments": {
                                "description": "Get player segmentation (whales, regulars, casuals, churned)",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            "get_leaderboard": {
                                "description": "Get player leaderboard",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "metric": {"type": "string", "enum": ["playtime", "sessions"]},
                                        "limit": {"type": "integer", "default": 10},
                                    },
                                },
                            },
                            "get_server_comparison": {
                                "description": "Compare analytics across different servers",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "days": {"type": "integer", "default": 7},
                                    },
                                },
                            },
                            
                            # Reports
                            "generate_daily_report": {
                                "description": "Generate daily analytics report",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "date": {"type": "string"},
                                    },
                                },
                            },
                            "generate_weekly_report": {
                                "description": "Generate weekly analytics report",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "week_start": {"type": "string"},
                                    },
                                },
                            },
                            "list_reports": {
                                "description": "List available analytics reports",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "report_type": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                                        "limit": {"type": "integer", "default": 20},
                                    },
                                },
                            },
                            "get_stats": {
                                "description": "Get overall analytics database statistics",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                        }
                    },
                    "serverInfo": {"name": "player-analytics", "version": "1.0.0"},
                },
            }
        )
    )

    # Handle tool calls
    tool_map = {
        "player_join": player_join,
        "player_leave": player_leave,
        "log_event": log_event,
        "get_active_players": get_active_players,
        "get_player": get_player,
        "search_players": search_players,
        "get_player_sessions": get_player_sessions,
        "get_player_events": get_player_events,
        "get_engagement_metrics": get_engagement_metrics,
        "get_retention_metrics": get_retention_metrics,
        "get_peak_hours": get_peak_hours,
        "get_player_segments": get_player_segments,
        "get_leaderboard": get_leaderboard,
        "get_server_comparison": get_server_comparison,
        "generate_daily_report": generate_daily_report,
        "generate_weekly_report": generate_weekly_report,
        "list_reports": list_reports,
        "get_stats": get_stats,
    }

    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name in tool_map:
                    result = tool_map[tool_name](**arguments)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
                        }
                    )
                )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if 'request' in dir() else None,
                        "error": {"code": -32603, "message": str(e)},
                    }
                )
            )


if __name__ == "__main__":
    main()
