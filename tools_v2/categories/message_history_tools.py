"""
Message History Tools - Agent Toolbelt V2
=========================================

Tools for viewing, searching, filtering, and analyzing message history.

Author: Agent-4 (Captain)
Date: 2025-01-27
V2 Compliance: <300 lines per tool
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..adapters.base_adapter import IToolAdapter, ToolResult
from ..core.tool_spec import ToolSpec

logger = logging.getLogger(__name__)


class MessageHistoryViewerTool(IToolAdapter):
    """View and search message history."""

    def get_name(self) -> str:
        return "message_history.view"

    def get_description(self) -> str:
        return "View message history with search, filter, and analysis capabilities"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="message_history.view",
            version="1.0.0",
            category="messaging",
            summary="View message history",
            required_params=[],
            optional_params={
                "sender": None,
                "recipient": None,
                "limit": 50,
                "search": None,
                "date_from": None,
                "date_to": None,
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """View message history with filters."""
        try:
            from src.repositories.message_repository import MessageRepository

            repo = MessageRepository()
            limit = params.get("limit", 50)
            sender = params.get("sender")
            recipient = params.get("recipient")
            search = params.get("search")
            date_from = params.get("date_from")
            date_to = params.get("date_to")

            # Get messages
            if sender:
                messages = repo.get_messages_by_sender(sender)
            elif recipient:
                messages = repo.get_messages_by_recipient(recipient)
            else:
                messages = repo.get_message_history(limit=limit)

            # Apply filters
            if search:
                messages = [
                    m
                    for m in messages
                    if search.lower() in str(m.get("content", "")).lower()
                ]

            if date_from:
                messages = [
                    m
                    for m in messages
                    if m.get("timestamp", "") >= date_from
                ]

            if date_to:
                messages = [
                    m
                    for m in messages
                    if m.get("timestamp", "") <= date_to
                ]

            # Format output
            output = {
                "total": len(messages),
                "messages": messages[:limit],
                "filters": {
                    "sender": sender,
                    "recipient": recipient,
                    "search": search,
                    "date_from": date_from,
                    "date_to": date_to,
                },
            }

            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"Message history view failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )


class MessageHistoryAnalyzerTool(IToolAdapter):
    """Analyze message history for patterns."""

    def get_name(self) -> str:
        return "message_history.analyze"

    def get_description(self) -> str:
        return "Analyze message history for patterns, statistics, and insights"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="message_history.analyze",
            version="1.0.0",
            category="messaging",
            summary="Analyze message patterns",
            required_params=[],
            optional_params={"days": 7, "group_by": "sender"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Analyze message history."""
        try:
            from src.repositories.message_repository import MessageRepository

            repo = MessageRepository()
            days = params.get("days", 7)
            group_by = params.get("group_by", "sender")

            # Get recent messages
            cutoff_date = (
                datetime.now().timestamp() - (days * 24 * 60 * 60)
            ).isoformat()
            messages = repo.get_message_history()

            # Filter by date
            recent_messages = [
                m
                for m in messages
                if m.get("timestamp", "") >= cutoff_date
            ]

            # Analyze
            stats = {
                "total_messages": len(recent_messages),
                "by_sender": {},
                "by_recipient": {},
                "by_type": {},
                "by_priority": {},
                "time_distribution": {},
            }

            for msg in recent_messages:
                # By sender
                sender = msg.get("sender", "unknown")
                stats["by_sender"][sender] = stats["by_sender"].get(sender, 0) + 1

                # By recipient
                recipient = msg.get("recipient", "unknown")
                stats["by_recipient"][recipient] = (
                    stats["by_recipient"].get(recipient, 0) + 1
                )

                # By type
                msg_type = msg.get("message_type", "unknown")
                stats["by_type"][msg_type] = stats["by_type"].get(msg_type, 0) + 1

                # By priority
                priority = msg.get("priority", "regular")
                stats["by_priority"][priority] = (
                    stats["by_priority"].get(priority, 0) + 1
                )

                # Time distribution (hour of day)
                try:
                    timestamp = msg.get("timestamp", "")
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        hour = dt.hour
                        stats["time_distribution"][hour] = (
                            stats["time_distribution"].get(hour, 0) + 1
                        )
                except Exception:
                    pass

            return ToolResult(success=True, output=stats)

        except Exception as e:
            logger.error(f"Message history analysis failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )


class MessageCompressionTool(IToolAdapter):
    """Compress message history based on age."""

    def get_name(self) -> str:
        return "message_history.compress"

    def get_description(self) -> str:
        return "Compress message history based on age (Level 1: 0-7 days, Level 2: 7-30 days, Level 3: 30+ days)"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="message_history.compress",
            version="1.0.0",
            category="messaging",
            summary="Compress message history",
            required_params=[],
            optional_params={"dry_run": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Compress message history."""
        try:
            from src.repositories.message_repository import MessageRepository

            repo = MessageRepository()
            dry_run = params.get("dry_run", False)

            messages = repo.get_message_history()
            current_time = datetime.now()

            compressed = []
            aggregated = []
            kept_full = []

            for msg in messages:
                try:
                    timestamp = msg.get("timestamp", "")
                    if not timestamp:
                        continue

                    msg_time = datetime.fromisoformat(
                        timestamp.replace("Z", "+00:00")
                    )
                    age_days = (current_time - msg_time.replace(tzinfo=None)).days

                    if age_days <= 7:
                        # Level 1: Keep full
                        kept_full.append(msg)
                    elif age_days <= 30:
                        # Level 2: Compress
                        compressed_msg = {
                            "sender": msg.get("sender"),
                            "recipient": msg.get("recipient"),
                            "timestamp": timestamp,
                            "queue_id": msg.get("queue_id"),
                            "message_type": msg.get("message_type"),
                            "priority": msg.get("priority"),
                            "content_preview": str(msg.get("content", ""))[:200],
                            "content_length": len(str(msg.get("content", ""))),
                        }
                        compressed.append(compressed_msg)
                    else:
                        # Level 3: Aggregate (will be aggregated separately)
                        aggregated.append(msg)
                except Exception as e:
                    logger.warning(f"Failed to process message: {e}")
                    continue

            if not dry_run:
                # TODO: Implement actual compression save
                pass

            output = {
                "total_messages": len(messages),
                "kept_full": len(kept_full),
                "compressed": len(compressed),
                "aggregated": len(aggregated),
                "compression_ratio": f"{(len(compressed) + len(aggregated)) / len(messages) * 100:.1f}%",
                "dry_run": dry_run,
            }

            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"Message compression failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )

