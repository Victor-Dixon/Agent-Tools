#!/usr/bin/env python3
"""
Swarm Brain & Notes Tools
==========================

Tools for agent notes and swarm knowledge management.

Author: Agent-7 - Repository Cloning Specialist
Created: 2025-10-13
"""

import logging
from typing import Any

from ..adapters.base_adapter import IToolAdapter

logger = logging.getLogger(__name__)


class TakeNoteTool(IToolAdapter):
    """Take personal note."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute note taking."""
        try:
            from src.swarm_brain import NoteType, SwarmMemory

            agent_id = params.get("agent_id")
            content = params.get("content")
            note_type = params.get("note_type", "important")

            if not agent_id or not content:
                return {"success": False, "error": "agent_id and content required"}

            memory = SwarmMemory(agent_id)

            # Map string to enum
            type_map = {
                "learning": NoteType.LEARNING,
                "important": NoteType.IMPORTANT,
                "todo": NoteType.TODO,
                "decision": NoteType.DECISION,
                "work_log": NoteType.WORK_LOG,
            }

            note_type_enum = type_map.get(note_type, NoteType.IMPORTANT)
            memory.take_note(content, note_type_enum)

            return {"success": True, "message": f"Note added: {note_type}"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class ShareLearningTool(IToolAdapter):
    """Share learning with swarm brain."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute learning sharing."""
        try:
            from src.swarm_brain import SwarmMemory

            agent_id = params.get("agent_id")
            title = params.get("title")
            content = params.get("content")
            tags = params.get("tags", [])

            if not agent_id or not title or not content:
                return {"success": False, "error": "agent_id, title, content required"}

            memory = SwarmMemory(agent_id)
            entry_id = memory.share_learning(title, content, tags)

            return {
                "success": True,
                "entry_id": entry_id,
                "message": f"Learning shared: {entry_id}",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class SearchKnowledgeTool(IToolAdapter):
    """Search swarm knowledge base."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute knowledge search."""
        try:
            from src.swarm_brain import SwarmMemory

            agent_id = params.get("agent_id", "Agent-1")
            query = params.get("query")

            if not query:
                return {"success": False, "error": "query required"}

            memory = SwarmMemory(agent_id)
            results = memory.search_swarm_knowledge(query)

            return {
                "success": True,
                "results": [
                    {"title": r.title, "author": r.author, "tags": r.tags} for r in results
                ],
                "count": len(results),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class LogSessionTool(IToolAdapter):
    """Log work session to agent notes."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute session logging."""
        try:
            from src.swarm_brain import SwarmMemory

            agent_id = params.get("agent_id")
            summary = params.get("summary")

            if not agent_id or not summary:
                return {"success": False, "error": "agent_id and summary required"}

            memory = SwarmMemory(agent_id)
            memory.log_session(summary)

            return {"success": True, "message": "Session logged"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class GetAgentNotesTool(IToolAdapter):
    """Get agent's personal notes."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute note retrieval."""
        try:
            from src.swarm_brain import NoteType, SwarmMemory

            agent_id = params.get("agent_id")
            note_type = params.get("note_type")

            if not agent_id:
                return {"success": False, "error": "agent_id required"}

            memory = SwarmMemory(agent_id)

            if note_type:
                type_map = {
                    "learning": NoteType.LEARNING,
                    "important": NoteType.IMPORTANT,
                    "todo": NoteType.TODO,
                }
                notes = memory.get_my_notes(type_map.get(note_type))
            else:
                notes = memory.get_my_notes()

            return {"success": True, "notes": notes, "count": len(notes)}

        except Exception as e:
            return {"success": False, "error": str(e)}
