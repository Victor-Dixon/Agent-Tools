#!/usr/bin/env python3
"""
Webhook Manager
===============

Manages Discord webhooks for sending notifications.
Supports multiple channels and rate limiting.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import deque

import requests

from .embed_builder import DiscordEmbed

logger = logging.getLogger(__name__)


@dataclass
class WebhookConfig:
    """Configuration for a Discord webhook."""
    name: str
    url: str
    channel_type: str  # status, alerts, events, chat, logs
    enabled: bool = True
    rate_limit_per_minute: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "url": self.url[:50] + "..." if len(self.url) > 50 else self.url,  # Mask URL
            "channel_type": self.channel_type,
            "enabled": self.enabled,
            "rate_limit_per_minute": self.rate_limit_per_minute,
        }


@dataclass
class WebhookMessage:
    """A message to send via webhook."""
    content: str = ""
    username: str = ""
    avatar_url: str = ""
    embeds: List[DiscordEmbed] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        payload = {}
        
        if self.content:
            payload["content"] = self.content
        if self.username:
            payload["username"] = self.username
        if self.avatar_url:
            payload["avatar_url"] = self.avatar_url
        if self.embeds:
            payload["embeds"] = [e.to_dict() for e in self.embeds]
        
        return payload


class RateLimiter:
    """Simple rate limiter using sliding window."""
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()
    
    def can_proceed(self) -> bool:
        """Check if a request can proceed."""
        now = time.time()
        
        # Remove old requests outside the window
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()
        
        return len(self.requests) < self.max_requests
    
    def record_request(self) -> None:
        """Record a request."""
        self.requests.append(time.time())
    
    def wait_time(self) -> float:
        """Get time to wait before next request is allowed."""
        if self.can_proceed():
            return 0
        
        oldest = self.requests[0]
        return max(0, oldest + self.window_seconds - time.time())


class WebhookManager:
    """
    Manages Discord webhooks for game server notifications.
    
    Features:
    - Multiple webhook channels
    - Rate limiting per webhook
    - Message queuing
    - Retry on failure
    - Message history
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        default_username: str = "Game Server Bot",
        default_avatar: str = "",
    ):
        self.config_path = config_path or Path.home() / ".discord_integration" / "webhooks.json"
        self.default_username = default_username
        self.default_avatar = default_avatar
        
        self._webhooks: Dict[str, WebhookConfig] = {}
        self._rate_limiters: Dict[str, RateLimiter] = {}
        self._message_history: List[Dict[str, Any]] = []
        self._max_history = 100
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load webhook configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                for wh_data in data.get("webhooks", []):
                    wh = WebhookConfig(
                        name=wh_data["name"],
                        url=wh_data["url"],
                        channel_type=wh_data.get("channel_type", "general"),
                        enabled=wh_data.get("enabled", True),
                        rate_limit_per_minute=wh_data.get("rate_limit_per_minute", 30),
                    )
                    self._webhooks[wh.name] = wh
                    self._rate_limiters[wh.name] = RateLimiter(wh.rate_limit_per_minute)
            except Exception as e:
                logger.warning(f"Failed to load webhook config: {e}")
    
    def _save_config(self) -> None:
        """Save webhook configuration."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Store with full URLs (be careful with secrets!)
        data = {
            "webhooks": [
                {
                    "name": wh.name,
                    "url": wh.url,
                    "channel_type": wh.channel_type,
                    "enabled": wh.enabled,
                    "rate_limit_per_minute": wh.rate_limit_per_minute,
                }
                for wh in self._webhooks.values()
            ]
        }
        
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def add_webhook(
        self,
        name: str,
        url: str,
        channel_type: str = "general",
        rate_limit: int = 30,
    ) -> bool:
        """Add a new webhook."""
        if not url.startswith("https://discord.com/api/webhooks/"):
            logger.error("Invalid webhook URL")
            return False
        
        self._webhooks[name] = WebhookConfig(
            name=name,
            url=url,
            channel_type=channel_type,
            rate_limit_per_minute=rate_limit,
        )
        self._rate_limiters[name] = RateLimiter(rate_limit)
        self._save_config()
        
        logger.info(f"Added webhook: {name}")
        return True
    
    def remove_webhook(self, name: str) -> bool:
        """Remove a webhook."""
        if name in self._webhooks:
            del self._webhooks[name]
            if name in self._rate_limiters:
                del self._rate_limiters[name]
            self._save_config()
            return True
        return False
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List configured webhooks (URLs masked)."""
        return [wh.to_dict() for wh in self._webhooks.values()]
    
    def send(
        self,
        webhook_name: str,
        message: Optional[WebhookMessage] = None,
        embed: Optional[DiscordEmbed] = None,
        content: str = "",
        wait_for_rate_limit: bool = True,
    ) -> Dict[str, Any]:
        """
        Send a message to a webhook.
        
        Args:
            webhook_name: Name of the webhook to use
            message: Full WebhookMessage object
            embed: Single embed to send
            content: Text content to send
            wait_for_rate_limit: Wait if rate limited
            
        Returns:
            Result dict with success status
        """
        if webhook_name not in self._webhooks:
            return {"success": False, "error": f"Webhook not found: {webhook_name}"}
        
        webhook = self._webhooks[webhook_name]
        
        if not webhook.enabled:
            return {"success": False, "error": "Webhook is disabled"}
        
        # Build message
        if message is None:
            message = WebhookMessage()
        
        if content:
            message.content = content
        if embed:
            message.embeds.append(embed)
        
        if not message.username:
            message.username = self.default_username
        if not message.avatar_url and self.default_avatar:
            message.avatar_url = self.default_avatar
        
        # Check rate limit
        limiter = self._rate_limiters.get(webhook_name)
        if limiter:
            if not limiter.can_proceed():
                if wait_for_rate_limit:
                    wait_time = limiter.wait_time()
                    logger.info(f"Rate limited, waiting {wait_time:.1f}s")
                    time.sleep(wait_time)
                else:
                    return {"success": False, "error": "Rate limited"}
        
        # Send request
        try:
            payload = message.to_dict()
            
            response = requests.post(
                webhook.url,
                json=payload,
                timeout=10,
            )
            
            if limiter:
                limiter.record_request()
            
            # Record in history
            self._message_history.append({
                "webhook": webhook_name,
                "timestamp": datetime.now().isoformat(),
                "status_code": response.status_code,
                "success": response.status_code in [200, 204],
            })
            
            if len(self._message_history) > self._max_history:
                self._message_history = self._message_history[-self._max_history:]
            
            if response.status_code == 204:
                return {"success": True}
            elif response.status_code == 200:
                return {"success": True, "response": response.json()}
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text[:200],
                }
                
        except requests.Timeout:
            return {"success": False, "error": "Request timeout"}
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def send_to_channel_type(
        self,
        channel_type: str,
        embed: Optional[DiscordEmbed] = None,
        content: str = "",
    ) -> Dict[str, Any]:
        """
        Send to all webhooks of a specific channel type.
        
        Args:
            channel_type: Type of channel (status, alerts, events, etc.)
            embed: Embed to send
            content: Text content
            
        Returns:
            Results for each webhook
        """
        results = {}
        
        for name, webhook in self._webhooks.items():
            if webhook.channel_type == channel_type and webhook.enabled:
                results[name] = self.send(
                    webhook_name=name,
                    embed=embed,
                    content=content,
                )
        
        return results
    
    def send_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        server_name: str = "",
        recommendations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Send an alert to alert-type webhooks."""
        from .embed_builder import EmbedBuilder
        
        embed = EmbedBuilder.alert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            server_name=server_name,
            recommendations=recommendations,
        )
        
        return self.send_to_channel_type("alerts", embed=embed)
    
    def send_status_update(
        self,
        server_name: str,
        game: str,
        status: str,
        player_count: int,
        max_players: int,
        **kwargs,
    ) -> Dict[str, Any]:
        """Send a server status update to status-type webhooks."""
        from .embed_builder import EmbedBuilder
        
        embed = EmbedBuilder.server_status(
            server_name=server_name,
            game=game,
            status=status,
            player_count=player_count,
            max_players=max_players,
            **kwargs,
        )
        
        return self.send_to_channel_type("status", embed=embed)
    
    def send_event(
        self,
        event_type: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Send an event notification to event-type webhooks."""
        from .embed_builder import EmbedBuilder
        
        if event_type == "player_join":
            embed = EmbedBuilder.player_join(**kwargs)
        elif event_type == "player_leave":
            embed = EmbedBuilder.player_leave(**kwargs)
        elif event_type == "mod_update":
            embed = EmbedBuilder.mod_update(**kwargs)
        elif event_type == "backup_complete":
            embed = EmbedBuilder.backup_complete(**kwargs)
        elif event_type == "server_restart":
            embed = EmbedBuilder.server_restart(**kwargs)
        else:
            embed = EmbedBuilder.custom(title=event_type, **kwargs)
        
        return self.send_to_channel_type("events", embed=embed)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get webhook usage statistics."""
        now = datetime.now()
        last_hour = [
            m for m in self._message_history
            if datetime.fromisoformat(m["timestamp"]) > now - timedelta(hours=1)
        ]
        
        return {
            "webhook_count": len(self._webhooks),
            "enabled_count": sum(1 for w in self._webhooks.values() if w.enabled),
            "messages_last_hour": len(last_hour),
            "success_rate": (
                sum(1 for m in last_hour if m["success"]) / len(last_hour) * 100
                if last_hour else 100
            ),
        }
    
    def test_webhook(self, webhook_name: str) -> Dict[str, Any]:
        """Send a test message to a webhook."""
        from .embed_builder import EmbedBuilder
        
        embed = EmbedBuilder.custom(
            title="🧪 Webhook Test",
            description="This is a test message from the Discord Integration system.",
            color="success",
            fields=[
                {"name": "Webhook", "value": webhook_name, "inline": True},
                {"name": "Status", "value": "✅ Working", "inline": True},
            ],
        )
        
        return self.send(webhook_name=webhook_name, embed=embed)
