"""
Vector Database Tools
=====================

Tool adapters for vector database operations.

V2 Compliance: <220 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class TaskContextTool(IToolAdapter):
    """Get intelligent task context from vector DB."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="vector.context",
            version="1.0.0",
            category="vector",
            summary="Get intelligent context for a task from vector database",
            required_params=["agent_id", "task"],
            optional_params={"limit": 5},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute task context retrieval."""
        try:
            from src.services.agent_management import TaskContextManager

            agent_id = params["agent_id"]
            task = params["task"]

            context_mgr = TaskContextManager(agent_id=agent_id)
            task_context = context_mgr.get_task_context(task)

            return ToolResult(success=True, output=task_context, exit_code=0)
        except Exception as e:
            logger.error(f"Error getting task context: {e}")
            raise ToolExecutionError(str(e), tool_name="vector.context")


class VectorSearchTool(IToolAdapter):
    """Semantic search across vector database."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="vector.search",
            version="1.0.0",
            category="vector",
            summary="Semantic search across all indexed content",
            required_params=["query"],
            optional_params={"agent_id": None, "limit": 5, "collection": "agent_work"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute semantic search."""
        try:
            from src.services.vector_database import search_vector_database
            from src.services.vector_database.vector_database_models import SearchQuery

            query = SearchQuery(
                query=params["query"],
                collection_name=params.get("collection", "agent_work"),
                limit=params.get("limit", 5),
            )

            results = search_vector_database(query)

            return ToolResult(success=True, output=results, exit_code=0)
        except Exception as e:
            logger.error(f"Error searching vector DB: {e}")
            raise ToolExecutionError(str(e), tool_name="vector.search")


class IndexWorkTool(IToolAdapter):
    """Index completed work to vector database."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="vector.index",
            version="1.0.0",
            category="vector",
            summary="Index agent work to vector database for future retrieval",
            required_params=["agent_id"],
            optional_params={"file": None, "inbox": False, "work_type": "code"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        is_valid, missing = spec.validate_params(params)

        # Additional validation: must have either file or inbox
        if is_valid and not params.get("file") and not params.get("inbox"):
            return (False, ["file or inbox (must specify one)"])

        return (is_valid, missing)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute work indexing."""
        try:
            from src.services.work_indexer import WorkIndexer

            agent_id = params["agent_id"]
            indexer = WorkIndexer(agent_id=agent_id)

            if params.get("inbox"):
                count = indexer.index_inbox_messages()
                return ToolResult(
                    success=True, output={"indexed_count": count, "type": "inbox"}, exit_code=0
                )
            elif params.get("file"):
                success = indexer.index_agent_work(params["file"], params.get("work_type", "code"))
                return ToolResult(
                    success=success,
                    output={"file": params["file"], "indexed": success},
                    exit_code=0 if success else 1,
                )
            else:
                raise ToolExecutionError(
                    "Must specify either --file or --inbox", tool_name="vector.index"
                )

        except Exception as e:
            logger.error(f"Error indexing work: {e}")
            raise ToolExecutionError(str(e), tool_name="vector.index")
