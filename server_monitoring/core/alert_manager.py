#!/usr/bin/env python3
"""
Alert Manager
=============

Manages alerts and notifications for server performance issues.
Supports Discord, email, and webhook notifications.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

import requests

from .performance_analyzer import PerformanceIssue, IssueSeverity

logger = logging.getLogger(__name__)


class AlertChannel(Enum):
    """Available notification channels."""
    DISCORD = "discord"
    WEBHOOK = "webhook"
    EMAIL = "email"
    LOG = "log"


@dataclass
class AlertConfig:
    """Configuration for an alert channel."""
    channel: AlertChannel
    enabled: bool = True
    url: str = ""
    min_severity: IssueSeverity = IssueSeverity.WARNING
    cooldown_minutes: int = 15  # Don't repeat same alert within this time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel": self.channel.value,
            "enabled": self.enabled,
            "url": self.url,
            "min_severity": self.min_severity.value,
            "cooldown_minutes": self.cooldown_minutes,
        }


@dataclass
class Alert:
    """Represents a sent alert."""
    id: str
    issue_type: str
    severity: str
    message: str
    sent_at: str
    channels: List[str]
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "message": self.message,
            "sent_at": self.sent_at,
            "channels": self.channels,
            "acknowledged": self.acknowledged,
        }


class AlertManager:
    """
    Manages performance alerts and notifications.
    
    Features:
    - Multi-channel notifications (Discord, webhook, email)
    - Alert cooldowns to prevent spam
    - Alert history and acknowledgment
    - Custom alert rules
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        alert_history_path: Optional[Path] = None,
    ):
        self.config_path = config_path or Path.home() / ".server_monitoring" / "alerts.json"
        self.history_path = alert_history_path or Path.home() / ".server_monitoring" / "alert_history.json"
        
        self._channels: List[AlertConfig] = []
        self._history: List[Alert] = []
        self._last_alerts: Dict[str, datetime] = {}  # issue_type -> last alert time
        self._custom_handlers: List[Callable[[PerformanceIssue], None]] = []
        
        self._load_config()
        self._load_history()
    
    def _load_config(self) -> None:
        """Load alert configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                for ch_data in data.get("channels", []):
                    self._channels.append(AlertConfig(
                        channel=AlertChannel(ch_data["channel"]),
                        enabled=ch_data.get("enabled", True),
                        url=ch_data.get("url", ""),
                        min_severity=IssueSeverity(ch_data.get("min_severity", "warning")),
                        cooldown_minutes=ch_data.get("cooldown_minutes", 15),
                    ))
            except Exception as e:
                logger.warning(f"Failed to load alert config: {e}")
        
        # Add default Discord from environment
        discord_webhook = os.getenv("DISCORD_WEBHOOK")
        if discord_webhook and not any(c.channel == AlertChannel.DISCORD for c in self._channels):
            self._channels.append(AlertConfig(
                channel=AlertChannel.DISCORD,
                url=discord_webhook,
            ))
    
    def _save_config(self) -> None:
        """Save alert configuration."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"channels": [c.to_dict() for c in self._channels]}
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def _load_history(self) -> None:
        """Load alert history."""
        if self.history_path.exists():
            try:
                with open(self.history_path) as f:
                    data = json.load(f)
                # Only load last 24 hours
                cutoff = datetime.now() - timedelta(hours=24)
                for alert_data in data.get("alerts", []):
                    alert_time = datetime.fromisoformat(alert_data["sent_at"])
                    if alert_time > cutoff:
                        self._history.append(Alert(**alert_data))
            except Exception as e:
                logger.warning(f"Failed to load alert history: {e}")
    
    def _save_history(self) -> None:
        """Save alert history."""
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"alerts": [a.to_dict() for a in self._history[-100:]]}  # Keep last 100
        with open(self.history_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def add_channel(self, config: AlertConfig) -> None:
        """Add an alert channel."""
        self._channels.append(config)
        self._save_config()
    
    def remove_channel(self, channel: AlertChannel) -> None:
        """Remove an alert channel."""
        self._channels = [c for c in self._channels if c.channel != channel]
        self._save_config()
    
    def add_custom_handler(self, handler: Callable[[PerformanceIssue], None]) -> None:
        """Add a custom alert handler function."""
        self._custom_handlers.append(handler)
    
    def should_alert(self, issue: PerformanceIssue) -> bool:
        """Check if an alert should be sent (respecting cooldown)."""
        issue_key = f"{issue.type.value}:{issue.severity.value}"
        
        if issue_key in self._last_alerts:
            last_time = self._last_alerts[issue_key]
            # Use minimum cooldown from all channels
            min_cooldown = min(
                (c.cooldown_minutes for c in self._channels if c.enabled),
                default=15
            )
            if datetime.now() - last_time < timedelta(minutes=min_cooldown):
                return False
        
        return True
    
    def process_issues(self, issues: List[PerformanceIssue]) -> List[Alert]:
        """Process issues and send alerts as needed."""
        sent_alerts = []
        
        for issue in issues:
            if self.should_alert(issue):
                alert = self._send_alert(issue)
                if alert:
                    sent_alerts.append(alert)
        
        return sent_alerts
    
    def _send_alert(self, issue: PerformanceIssue) -> Optional[Alert]:
        """Send alert to all configured channels."""
        channels_sent = []
        
        for config in self._channels:
            if not config.enabled:
                continue
            
            # Check severity threshold
            severity_order = [IssueSeverity.INFO, IssueSeverity.WARNING, IssueSeverity.CRITICAL]
            if severity_order.index(issue.severity) < severity_order.index(config.min_severity):
                continue
            
            success = False
            
            if config.channel == AlertChannel.DISCORD:
                success = self._send_discord(config.url, issue)
            elif config.channel == AlertChannel.WEBHOOK:
                success = self._send_webhook(config.url, issue)
            elif config.channel == AlertChannel.LOG:
                success = self._send_log(issue)
            
            if success:
                channels_sent.append(config.channel.value)
        
        # Run custom handlers
        for handler in self._custom_handlers:
            try:
                handler(issue)
            except Exception as e:
                logger.error(f"Custom handler failed: {e}")
        
        if channels_sent:
            # Record alert
            alert_id = f"{issue.type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            alert = Alert(
                id=alert_id,
                issue_type=issue.type.value,
                severity=issue.severity.value,
                message=issue.message,
                sent_at=datetime.now().isoformat(),
                channels=channels_sent,
            )
            
            self._history.append(alert)
            self._last_alerts[f"{issue.type.value}:{issue.severity.value}"] = datetime.now()
            self._save_history()
            
            return alert
        
        return None
    
    def _send_discord(self, webhook_url: str, issue: PerformanceIssue) -> bool:
        """Send alert to Discord webhook."""
        try:
            # Color based on severity
            colors = {
                IssueSeverity.INFO: 0x3498db,     # Blue
                IssueSeverity.WARNING: 0xf39c12,  # Orange
                IssueSeverity.CRITICAL: 0xe74c3c, # Red
            }
            
            # Emoji based on severity
            emojis = {
                IssueSeverity.INFO: "ℹ️",
                IssueSeverity.WARNING: "⚠️",
                IssueSeverity.CRITICAL: "🚨",
            }
            
            embed = {
                "title": f"{emojis[issue.severity]} Server Alert: {issue.type.value.replace('_', ' ').title()}",
                "description": issue.message,
                "color": colors[issue.severity],
                "timestamp": issue.timestamp,
                "fields": [
                    {
                        "name": "Current Value",
                        "value": f"`{issue.current_value:.1f}`",
                        "inline": True,
                    },
                    {
                        "name": "Threshold",
                        "value": f"`{issue.threshold:.1f}`",
                        "inline": True,
                    },
                ],
            }
            
            if issue.recommendations:
                embed["fields"].append({
                    "name": "Recommendations",
                    "value": "\n".join(f"• {r}" for r in issue.recommendations[:3]),
                    "inline": False,
                })
            
            payload = {"embeds": [embed]}
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Discord alert failed: {e}")
            return False
    
    def _send_webhook(self, webhook_url: str, issue: PerformanceIssue) -> bool:
        """Send alert to generic webhook."""
        try:
            payload = {
                "type": issue.type.value,
                "severity": issue.severity.value,
                "message": issue.message,
                "current_value": issue.current_value,
                "threshold": issue.threshold,
                "timestamp": issue.timestamp,
                "recommendations": issue.recommendations,
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code in [200, 201, 202, 204]
            
        except Exception as e:
            logger.error(f"Webhook alert failed: {e}")
            return False
    
    def _send_log(self, issue: PerformanceIssue) -> bool:
        """Log alert to file/stdout."""
        log_method = {
            IssueSeverity.INFO: logger.info,
            IssueSeverity.WARNING: logger.warning,
            IssueSeverity.CRITICAL: logger.critical,
        }
        
        log_method[issue.severity](
            f"ALERT [{issue.type.value}] {issue.message} "
            f"(value: {issue.current_value}, threshold: {issue.threshold})"
        )
        return True
    
    def get_active_alerts(self) -> List[Alert]:
        """Get unacknowledged alerts."""
        return [a for a in self._history if not a.acknowledged]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self._history:
            if alert.id == alert_id:
                alert.acknowledged = True
                self._save_history()
                return True
        return False
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of recent alerts."""
        now = datetime.now()
        last_hour = [
            a for a in self._history
            if datetime.fromisoformat(a.sent_at) > now - timedelta(hours=1)
        ]
        last_24h = [
            a for a in self._history
            if datetime.fromisoformat(a.sent_at) > now - timedelta(hours=24)
        ]
        
        return {
            "last_hour": {
                "total": len(last_hour),
                "critical": sum(1 for a in last_hour if a.severity == "critical"),
                "warning": sum(1 for a in last_hour if a.severity == "warning"),
            },
            "last_24h": {
                "total": len(last_24h),
                "critical": sum(1 for a in last_24h if a.severity == "critical"),
                "warning": sum(1 for a in last_24h if a.severity == "warning"),
            },
            "unacknowledged": len(self.get_active_alerts()),
        }
