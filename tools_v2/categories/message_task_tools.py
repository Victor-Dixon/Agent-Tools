#!/usr/bin/env python3
"""
Message-Task Integration Tools
===============================

Tools for autonomous message-to-task loop.

Author: Agent-7 - Repository Cloning Specialist
Created: 2025-10-13
"""

import logging
from typing import Any

from ..adapters.base_adapter import IToolAdapter

logger = logging.getLogger(__name__)


class MessageIngestTool(IToolAdapter):
    """Ingest message and create task."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute message ingestion."""
        try:
            from src.message_task.messaging_integration import process_message_for_task

            message_id = params.get("message_id", f"msg-{params.get('content', '')[:8]}")
            content = params.get("content")
            author = params.get("author", "Agent")
            channel = params.get("channel", "cli")

            if not content:
                return {"success": False, "error": "Content required"}

            task_id = process_message_for_task(message_id, content, author, channel)

            if task_id:
                return {
                    "success": True,
                    "task_id": task_id,
                    "message": f"Task created: {task_id}",
                }
            else:
                return {"success": False, "error": "Failed to create task"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class TaskParserTool(IToolAdapter):
    """Parse message to extract task info."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute task parsing."""
        try:
            from src.message_task.parsers.ai_parser import AIParser
            from src.message_task.parsers.fallback_regex import FallbackRegexParser
            from src.message_task.parsers.structured_parser import StructuredParser

            content = params.get("content")
            if not content:
                return {"success": False, "error": "Content required"}

            # Try parsers
            for parser_name, parser in [
                ("structured", StructuredParser),
                ("ai", AIParser),
                ("fallback", FallbackRegexParser),
            ]:
                result = parser.parse(content)
                if result:
                    return {
                        "success": True,
                        "parser_used": parser_name,
                        "title": result.title,
                        "description": result.description,
                        "priority": result.priority,
                        "assignee": result.assignee,
                    }

            return {"success": False, "error": "No parser succeeded"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class TaskFingerprintTool(IToolAdapter):
    """Generate task fingerprint for deduplication."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute fingerprint generation."""
        try:
            from src.message_task.dedupe import task_fingerprint

            task_dict = {
                "title": params.get("title", ""),
                "description": params.get("description", ""),
                "priority": params.get("priority", "P3"),
                "assignee": params.get("assignee"),
            }

            fingerprint = task_fingerprint(task_dict)

            return {"success": True, "fingerprint": fingerprint, "length": len(fingerprint)}

        except Exception as e:
            return {"success": False, "error": str(e)}
