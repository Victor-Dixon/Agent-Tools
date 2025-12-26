#!/usr/bin/env python3
"""
Status Poster
=============

Automatically posts and updates server status in Discord.
Supports persistent status messages that update in-place.
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .embed_builder import EmbedBuilder, DiscordEmbed
from .webhook_manager import WebhookManager

logger = logging.getLogger(__name__)


@dataclass
class StatusMessage:
    """Tracks a status message for editing."""
    webhook_name: str
    message_id: str
    server_name: str
    created_at: str
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "webhook_name": self.webhook_name,
            "message_id": self.message_id,
            "server_name": self.server_name,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
        }


class StatusPoster:
    """
    Posts and updates server status in Discord channels.
    
    Features:
    - Create persistent status messages
    - Update status in-place (edit existing message)
    - Support multiple servers
    - Auto-refresh on schedule
    """
    
    def __init__(
        self,
        webhook_manager: WebhookManager,
        state_path: Optional[Path] = None,
    ):
        self.webhook_manager = webhook_manager
        self.state_path = state_path or Path.home() / ".discord_integration" / "status_state.json"
        
        self._status_messages: Dict[str, StatusMessage] = {}  # server_name -> message
        self._load_state()
    
    def _load_state(self) -> None:
        """Load persistent status message state."""
        if self.state_path.exists():
            try:
                with open(self.state_path) as f:
                    data = json.load(f)
                for msg_data in data.get("status_messages", []):
                    msg = StatusMessage(
                        webhook_name=msg_data["webhook_name"],
                        message_id=msg_data["message_id"],
                        server_name=msg_data["server_name"],
                        created_at=msg_data["created_at"],
                        last_updated=msg_data["last_updated"],
                    )
                    self._status_messages[msg.server_name] = msg
            except Exception as e:
                logger.warning(f"Failed to load status state: {e}")
    
    def _save_state(self) -> None:
        """Save status message state."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "status_messages": [msg.to_dict() for msg in self._status_messages.values()]
        }
        with open(self.state_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def _get_webhook_url(self, webhook_name: str) -> Optional[str]:
        """Get the full webhook URL from manager."""
        # Access private attribute - in production, add a method to WebhookManager
        if webhook_name in self.webhook_manager._webhooks:
            return self.webhook_manager._webhooks[webhook_name].url
        return None
    
    def create_status_message(
        self,
        webhook_name: str,
        server_name: str,
        game: str,
        status: str = "Starting",
        player_count: int = 0,
        max_players: int = 0,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a new status message that can be updated.
        
        Args:
            webhook_name: Webhook to use
            server_name: Server identifier
            game: Game name
            status: Current status
            player_count: Current players
            max_players: Max players
            
        Returns:
            Result with message ID
        """
        webhook_url = self._get_webhook_url(webhook_name)
        if not webhook_url:
            return {"success": False, "error": "Webhook not found"}
        
        # Build embed
        embed = EmbedBuilder.server_status(
            server_name=server_name,
            game=game,
            status=status,
            player_count=player_count,
            max_players=max_players,
            **kwargs,
        )
        
        # Send with wait=true to get message ID
        try:
            response = requests.post(
                f"{webhook_url}?wait=true",
                json={
                    "embeds": [embed.to_dict()],
                    "username": "Server Status",
                },
                timeout=10,
            )
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get("id")
                
                # Store for future updates
                self._status_messages[server_name] = StatusMessage(
                    webhook_name=webhook_name,
                    message_id=message_id,
                    server_name=server_name,
                    created_at=datetime.now().isoformat(),
                    last_updated=datetime.now().isoformat(),
                )
                self._save_state()
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "server_name": server_name,
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_status(
        self,
        server_name: str,
        game: str,
        status: str,
        player_count: int,
        max_players: int,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Update an existing status message.
        
        Args:
            server_name: Server to update
            game: Game name
            status: Current status
            player_count: Current players
            max_players: Max players
            
        Returns:
            Update result
        """
        if server_name not in self._status_messages:
            return {"success": False, "error": "Status message not found for server"}
        
        msg = self._status_messages[server_name]
        webhook_url = self._get_webhook_url(msg.webhook_name)
        
        if not webhook_url:
            return {"success": False, "error": "Webhook not found"}
        
        # Build updated embed
        embed = EmbedBuilder.server_status(
            server_name=server_name,
            game=game,
            status=status,
            player_count=player_count,
            max_players=max_players,
            **kwargs,
        )
        
        # Edit the message
        try:
            edit_url = f"{webhook_url}/messages/{msg.message_id}"
            
            response = requests.patch(
                edit_url,
                json={"embeds": [embed.to_dict()]},
                timeout=10,
            )
            
            if response.status_code in [200, 204]:
                msg.last_updated = datetime.now().isoformat()
                self._save_state()
                
                return {"success": True, "message_id": msg.message_id}
            else:
                # Message might have been deleted, recreate
                logger.warning(f"Failed to edit message, will recreate: {response.status_code}")
                return self.create_status_message(
                    webhook_name=msg.webhook_name,
                    server_name=server_name,
                    game=game,
                    status=status,
                    player_count=player_count,
                    max_players=max_players,
                    **kwargs,
                )
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_status_message(self, server_name: str) -> bool:
        """Delete a status message."""
        if server_name not in self._status_messages:
            return False
        
        msg = self._status_messages[server_name]
        webhook_url = self._get_webhook_url(msg.webhook_name)
        
        if webhook_url:
            try:
                delete_url = f"{webhook_url}/messages/{msg.message_id}"
                requests.delete(delete_url, timeout=10)
            except Exception:
                pass  # Message might already be deleted
        
        del self._status_messages[server_name]
        self._save_state()
        return True
    
    def list_status_messages(self) -> List[Dict[str, Any]]:
        """List all tracked status messages."""
        return [msg.to_dict() for msg in self._status_messages.values()]
    
    def post_or_update(
        self,
        webhook_name: str,
        server_name: str,
        game: str,
        status: str,
        player_count: int,
        max_players: int,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Post new status or update existing.
        
        Convenience method that handles both cases.
        """
        if server_name in self._status_messages:
            return self.update_status(
                server_name=server_name,
                game=game,
                status=status,
                player_count=player_count,
                max_players=max_players,
                **kwargs,
            )
        else:
            return self.create_status_message(
                webhook_name=webhook_name,
                server_name=server_name,
                game=game,
                status=status,
                player_count=player_count,
                max_players=max_players,
                **kwargs,
            )


class StatusScheduler:
    """
    Schedules automatic status updates.
    
    Features:
    - Periodic status refresh
    - Multiple server support
    - Callback-based metrics collection
    """
    
    def __init__(
        self,
        status_poster: StatusPoster,
        default_interval: int = 60,  # seconds
    ):
        self.status_poster = status_poster
        self.default_interval = default_interval
        
        self._servers: Dict[str, Dict[str, Any]] = {}  # server_name -> config
        self._running = False
    
    def add_server(
        self,
        server_name: str,
        webhook_name: str,
        game: str,
        metrics_callback: callable,
        interval: Optional[int] = None,
    ) -> None:
        """
        Add a server for automatic status updates.
        
        Args:
            server_name: Server identifier
            webhook_name: Webhook to post to
            game: Game name
            metrics_callback: Function that returns dict with status, player_count, max_players
            interval: Update interval in seconds
        """
        self._servers[server_name] = {
            "webhook_name": webhook_name,
            "game": game,
            "metrics_callback": metrics_callback,
            "interval": interval or self.default_interval,
            "last_update": 0,
        }
    
    def remove_server(self, server_name: str) -> bool:
        """Remove a server from scheduling."""
        if server_name in self._servers:
            del self._servers[server_name]
            return True
        return False
    
    def update_all(self) -> Dict[str, Any]:
        """Update all servers immediately."""
        results = {}
        
        for server_name, config in self._servers.items():
            try:
                # Get metrics
                metrics = config["metrics_callback"]()
                
                # Update status
                result = self.status_poster.post_or_update(
                    webhook_name=config["webhook_name"],
                    server_name=server_name,
                    game=config["game"],
                    status=metrics.get("status", "Unknown"),
                    player_count=metrics.get("player_count", 0),
                    max_players=metrics.get("max_players", 0),
                    **{k: v for k, v in metrics.items() 
                       if k not in ["status", "player_count", "max_players"]},
                )
                
                results[server_name] = result
                config["last_update"] = time.time()
                
            except Exception as e:
                results[server_name] = {"success": False, "error": str(e)}
        
        return results
    
    def run_once(self) -> Dict[str, Any]:
        """Run a single update cycle (only servers due for update)."""
        results = {}
        now = time.time()
        
        for server_name, config in self._servers.items():
            if now - config["last_update"] >= config["interval"]:
                try:
                    metrics = config["metrics_callback"]()
                    
                    result = self.status_poster.post_or_update(
                        webhook_name=config["webhook_name"],
                        server_name=server_name,
                        game=config["game"],
                        status=metrics.get("status", "Unknown"),
                        player_count=metrics.get("player_count", 0),
                        max_players=metrics.get("max_players", 0),
                    )
                    
                    results[server_name] = result
                    config["last_update"] = now
                    
                except Exception as e:
                    results[server_name] = {"success": False, "error": str(e)}
        
        return results
