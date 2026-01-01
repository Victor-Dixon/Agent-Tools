#!/usr/bin/env python3
"""
MCP Server for Discord Integration
====================================

Exposes Discord integration operations via Model Context Protocol.

Tools:
- Webhook management
- Status posting
- Role synchronization
- Event notifications
- Embed creation
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "discord_integration"))

try:
    from core.webhook_manager import WebhookManager
    from core.status_poster import StatusPoster
    from core.role_sync import RoleSync
    from core.embed_builder import EmbedBuilder
    HAS_DISCORD = True
except ImportError as e:
    HAS_DISCORD = False
    import_error = str(e)


# Global instances (would be configured per-session in production)
_webhook_manager: Optional[WebhookManager] = None
_status_poster: Optional[StatusPoster] = None
_role_sync: Optional[RoleSync] = None


def _get_webhook_manager() -> WebhookManager:
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager


def _get_status_poster() -> StatusPoster:
    global _status_poster
    if _status_poster is None:
        _status_poster = StatusPoster(_get_webhook_manager())
    return _status_poster


def _get_role_sync() -> RoleSync:
    global _role_sync
    if _role_sync is None:
        _role_sync = RoleSync()
    return _role_sync


# ============ Webhook Management ============

def add_webhook(
    name: str,
    url: str,
    channel_type: str = "general",
    rate_limit: int = 30,
) -> Dict[str, Any]:
    """Add a Discord webhook."""
    if not HAS_DISCORD:
        return {"success": False, "error": f"Discord integration not available: {import_error}"}
    
    try:
        manager = _get_webhook_manager()
        success = manager.add_webhook(name, url, channel_type, rate_limit)
        return {"success": success, "webhook": name}
    except Exception as e:
        return {"success": False, "error": str(e)}


def remove_webhook(name: str) -> Dict[str, Any]:
    """Remove a Discord webhook."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        manager = _get_webhook_manager()
        success = manager.remove_webhook(name)
        return {"success": success, "webhook": name}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_webhooks() -> Dict[str, Any]:
    """List configured webhooks."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        manager = _get_webhook_manager()
        webhooks = manager.list_webhooks()
        stats = manager.get_stats()
        return {"success": True, "webhooks": webhooks, "stats": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_webhook(webhook_name: str) -> Dict[str, Any]:
    """Test a webhook by sending a test message."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        manager = _get_webhook_manager()
        result = manager.test_webhook(webhook_name)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ Sending Messages ============

def send_message(
    webhook_name: str,
    content: str = "",
    title: str = "",
    description: str = "",
    color: str = "primary",
    fields: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Send a message to a Discord webhook."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        manager = _get_webhook_manager()
        
        embed = None
        if title:
            embed = EmbedBuilder.custom(
                title=title,
                description=description,
                color=color,
                fields=fields,
            )
        
        result = manager.send(
            webhook_name=webhook_name,
            content=content,
            embed=embed,
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_server_status(
    webhook_name: str,
    server_name: str,
    game: str,
    status: str,
    player_count: int,
    max_players: int,
    ip: str = "",
    port: int = 0,
    mods_count: int = 0,
    uptime: str = "",
) -> Dict[str, Any]:
    """Send a server status embed."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        manager = _get_webhook_manager()
        
        embed = EmbedBuilder.server_status(
            server_name=server_name,
            game=game,
            status=status,
            player_count=player_count,
            max_players=max_players,
            ip=ip,
            port=port,
            mods_count=mods_count,
            uptime=uptime,
        )
        
        result = manager.send(webhook_name=webhook_name, embed=embed)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_alert(
    alert_type: str,
    severity: str,
    message: str,
    server_name: str = "",
    recommendations: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Send an alert to alert-type webhooks."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        manager = _get_webhook_manager()
        result = manager.send_alert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            server_name=server_name,
            recommendations=recommendations,
        )
        return {"success": True, "results": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_player_notification(
    event_type: str,
    player_name: str,
    server_name: str,
    player_count: int,
    max_players: int,
    session_time: str = "",
) -> Dict[str, Any]:
    """Send player join/leave notification."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        manager = _get_webhook_manager()
        
        if event_type == "join":
            embed = EmbedBuilder.player_join(
                player_name=player_name,
                server_name=server_name,
                player_count=player_count,
                max_players=max_players,
            )
        else:
            embed = EmbedBuilder.player_leave(
                player_name=player_name,
                server_name=server_name,
                player_count=player_count,
                max_players=max_players,
                session_time=session_time,
            )
        
        result = manager.send_to_channel_type("events", embed=embed)
        return {"success": True, "results": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_leaderboard(
    webhook_name: str,
    title: str,
    entries: List[Dict[str, Any]],
    stat_name: str = "Score",
) -> Dict[str, Any]:
    """Send a leaderboard embed."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        manager = _get_webhook_manager()
        
        embed = EmbedBuilder.leaderboard(
            title=title,
            entries=entries,
            stat_name=stat_name,
        )
        
        result = manager.send(webhook_name=webhook_name, embed=embed)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ Status Messages ============

def create_status_message(
    webhook_name: str,
    server_name: str,
    game: str,
    status: str = "Starting",
    player_count: int = 0,
    max_players: int = 0,
) -> Dict[str, Any]:
    """Create an editable status message."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        poster = _get_status_poster()
        result = poster.create_status_message(
            webhook_name=webhook_name,
            server_name=server_name,
            game=game,
            status=status,
            player_count=player_count,
            max_players=max_players,
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_status_message(
    server_name: str,
    game: str,
    status: str,
    player_count: int,
    max_players: int,
) -> Dict[str, Any]:
    """Update an existing status message."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        poster = _get_status_poster()
        result = poster.update_status(
            server_name=server_name,
            game=game,
            status=status,
            player_count=player_count,
            max_players=max_players,
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_status_messages() -> Dict[str, Any]:
    """List tracked status messages."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        poster = _get_status_poster()
        messages = poster.list_status_messages()
        return {"success": True, "messages": messages}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ Role Sync ============

def add_role_mapping(
    game_role: str,
    discord_role_id: str,
    discord_role_name: str,
    priority: int = 0,
) -> Dict[str, Any]:
    """Add a game role to Discord role mapping."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        sync = _get_role_sync()
        success = sync.add_role_mapping(
            game_role=game_role,
            discord_role_id=discord_role_id,
            discord_role_name=discord_role_name,
            priority=priority,
        )
        return {"success": success, "mapping": game_role}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_role_mappings() -> Dict[str, Any]:
    """List role mappings."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        sync = _get_role_sync()
        mappings = sync.list_role_mappings()
        stats = sync.get_stats()
        return {"success": True, "mappings": mappings, "stats": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}


def link_account(
    discord_id: str,
    discord_username: str,
    game_id: str,
    game_username: str,
    verified: bool = False,
) -> Dict[str, Any]:
    """Link a game account to Discord."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        sync = _get_role_sync()
        result = sync.link_account(
            discord_id=discord_id,
            discord_username=discord_username,
            game_id=game_id,
            game_username=game_username,
            verified=verified,
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_linked_account(discord_id: str) -> Dict[str, Any]:
    """Get linked account info."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        sync = _get_role_sync()
        account = sync.get_linked_account(discord_id)
        if account:
            return {"success": True, "account": account}
        return {"success": False, "error": "Account not linked"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_player_roles(
    discord_id: str,
    game_roles: List[str],
) -> Dict[str, Any]:
    """Update a player's game roles and sync to Discord."""
    if not HAS_DISCORD:
        return {"success": False, "error": "Discord integration not available"}
    
    try:
        sync = _get_role_sync()
        result = sync.update_game_roles(discord_id, game_roles)
        return result
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
                            # Webhook Management
                            "add_webhook": {
                                "description": "Add a Discord webhook for notifications",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "Webhook name"},
                                        "url": {"type": "string", "description": "Discord webhook URL"},
                                        "channel_type": {"type": "string", "enum": ["status", "alerts", "events", "general"]},
                                        "rate_limit": {"type": "integer", "default": 30},
                                    },
                                    "required": ["name", "url"],
                                },
                            },
                            "list_webhooks": {
                                "description": "List configured Discord webhooks",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            "test_webhook": {
                                "description": "Test a webhook by sending a test message",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "webhook_name": {"type": "string"},
                                    },
                                    "required": ["webhook_name"],
                                },
                            },
                            
                            # Sending Messages
                            "send_message": {
                                "description": "Send a message to a Discord webhook",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "webhook_name": {"type": "string"},
                                        "content": {"type": "string"},
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "color": {"type": "string", "enum": ["success", "warning", "error", "info", "primary"]},
                                        "fields": {"type": "array"},
                                    },
                                    "required": ["webhook_name"],
                                },
                            },
                            "send_server_status": {
                                "description": "Send a server status embed to Discord",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "webhook_name": {"type": "string"},
                                        "server_name": {"type": "string"},
                                        "game": {"type": "string"},
                                        "status": {"type": "string"},
                                        "player_count": {"type": "integer"},
                                        "max_players": {"type": "integer"},
                                        "ip": {"type": "string"},
                                        "port": {"type": "integer"},
                                        "mods_count": {"type": "integer"},
                                        "uptime": {"type": "string"},
                                    },
                                    "required": ["webhook_name", "server_name", "game", "status", "player_count", "max_players"],
                                },
                            },
                            "send_alert": {
                                "description": "Send an alert notification to Discord",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "alert_type": {"type": "string"},
                                        "severity": {"type": "string", "enum": ["info", "warning", "critical"]},
                                        "message": {"type": "string"},
                                        "server_name": {"type": "string"},
                                        "recommendations": {"type": "array", "items": {"type": "string"}},
                                    },
                                    "required": ["alert_type", "severity", "message"],
                                },
                            },
                            "send_player_notification": {
                                "description": "Send player join/leave notification",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "event_type": {"type": "string", "enum": ["join", "leave"]},
                                        "player_name": {"type": "string"},
                                        "server_name": {"type": "string"},
                                        "player_count": {"type": "integer"},
                                        "max_players": {"type": "integer"},
                                        "session_time": {"type": "string"},
                                    },
                                    "required": ["event_type", "player_name", "server_name", "player_count", "max_players"],
                                },
                            },
                            "send_leaderboard": {
                                "description": "Send a leaderboard embed",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "webhook_name": {"type": "string"},
                                        "title": {"type": "string"},
                                        "entries": {"type": "array", "items": {"type": "object"}},
                                        "stat_name": {"type": "string", "default": "Score"},
                                    },
                                    "required": ["webhook_name", "title", "entries"],
                                },
                            },
                            
                            # Status Messages
                            "create_status_message": {
                                "description": "Create an editable status message in Discord",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "webhook_name": {"type": "string"},
                                        "server_name": {"type": "string"},
                                        "game": {"type": "string"},
                                        "status": {"type": "string"},
                                        "player_count": {"type": "integer"},
                                        "max_players": {"type": "integer"},
                                    },
                                    "required": ["webhook_name", "server_name", "game"],
                                },
                            },
                            "update_status_message": {
                                "description": "Update an existing status message",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "server_name": {"type": "string"},
                                        "game": {"type": "string"},
                                        "status": {"type": "string"},
                                        "player_count": {"type": "integer"},
                                        "max_players": {"type": "integer"},
                                    },
                                    "required": ["server_name", "game", "status", "player_count", "max_players"],
                                },
                            },
                            "list_status_messages": {
                                "description": "List tracked status messages",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            
                            # Role Sync
                            "add_role_mapping": {
                                "description": "Add a game role to Discord role mapping",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_role": {"type": "string"},
                                        "discord_role_id": {"type": "string"},
                                        "discord_role_name": {"type": "string"},
                                        "priority": {"type": "integer", "default": 0},
                                    },
                                    "required": ["game_role", "discord_role_id", "discord_role_name"],
                                },
                            },
                            "list_role_mappings": {
                                "description": "List game to Discord role mappings",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            "link_account": {
                                "description": "Link a game account to a Discord account",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "discord_id": {"type": "string"},
                                        "discord_username": {"type": "string"},
                                        "game_id": {"type": "string"},
                                        "game_username": {"type": "string"},
                                        "verified": {"type": "boolean", "default": False},
                                    },
                                    "required": ["discord_id", "discord_username", "game_id", "game_username"],
                                },
                            },
                            "get_linked_account": {
                                "description": "Get linked account info for a Discord user",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "discord_id": {"type": "string"},
                                    },
                                    "required": ["discord_id"],
                                },
                            },
                            "update_player_roles": {
                                "description": "Update player's game roles and sync to Discord",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "discord_id": {"type": "string"},
                                        "game_roles": {"type": "array", "items": {"type": "string"}},
                                    },
                                    "required": ["discord_id", "game_roles"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "discord-integration", "version": "1.0.0"},
                },
            }
        )
    )

    # Handle tool calls
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                # Route to appropriate function
                tool_map = {
                    "add_webhook": add_webhook,
                    "remove_webhook": remove_webhook,
                    "list_webhooks": list_webhooks,
                    "test_webhook": test_webhook,
                    "send_message": send_message,
                    "send_server_status": send_server_status,
                    "send_alert": send_alert,
                    "send_player_notification": send_player_notification,
                    "send_leaderboard": send_leaderboard,
                    "create_status_message": create_status_message,
                    "update_status_message": update_status_message,
                    "list_status_messages": list_status_messages,
                    "add_role_mapping": add_role_mapping,
                    "list_role_mappings": list_role_mappings,
                    "link_account": link_account,
                    "get_linked_account": get_linked_account,
                    "update_player_roles": update_player_roles,
                }

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
