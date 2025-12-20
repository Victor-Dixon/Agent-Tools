"""
Swarm Proposal System Tools
============================

Tools for democratic proposal creation, review, and voting.

Enables agents to:
- Create proposals for system improvements
- Review and contribute alternative solutions
- Vote on best approaches via debate system
- Access proposal templates

V2 Compliance: <400 lines
Author: Agent-4 (Captain) - Session 2025-10-14
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)

PROPOSALS_DIR = Path("swarm_proposals")
SWARM_AGENTS = [f"Agent-{i}" for i in range(1, 9)]


class CreateProposalTool(IToolAdapter):
    """Create a new swarm proposal."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="proposal.create",
            version="1.0.0",
            category="proposal",
            summary="Create new swarm proposal for democratic review",
            required_params=["topic", "title", "agent_id"],
            optional_params={"content": "", "tags": []},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        errors = []
        if "topic" not in params:
            errors.append("topic is required")
        if "title" not in params:
            errors.append("title is required")
        if "agent_id" not in params:
            errors.append("agent_id is required")
        return len(errors) == 0, errors

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Create proposal."""
        try:
            topic = params["topic"]
            title = params["title"]
            agent_id = params["agent_id"]
            content = params.get("content", "")
            tags = params.get("tags", [])
            
            # Create topic directory
            topic_dir = PROPOSALS_DIR / topic
            topic_dir.mkdir(parents=True, exist_ok=True)
            
            # Create proposal file
            filename = f"{agent_id}_{title.lower().replace(' ', '_')}.md"
            proposal_file = topic_dir / filename
            
            # Generate proposal content
            proposal_content = f"# {title}\n\n"
            proposal_content += f"**Author:** {agent_id}\n"
            proposal_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            proposal_content += f"**Topic:** {topic}\n"
            if tags:
                proposal_content += f"**Tags:** {', '.join(tags)}\n"
            proposal_content += f"\n---\n\n"
            proposal_content += content if content else "## Proposal\n\n[Add your proposal here]\n"
            
            proposal_file.write_text(proposal_content)
            
            # Update topic index
            index_file = topic_dir / "README.md"
            if not index_file.exists():
                index_content = f"# {topic.replace('_', ' ').title()} Proposals\n\n"
                index_content += f"## Proposals\n\n"
            else:
                index_content = index_file.read_text()
            
            index_content += f"- [{title}]({filename}) - {agent_id}\n"
            index_file.write_text(index_content)
            
            return ToolResult(
                success=True,
                output={
                    "file": str(proposal_file),
                    "topic": topic,
                    "title": title,
                    "author": agent_id,
                },
                exit_code=0,
                execution_time=0.0,
            )
        except Exception as e:
            raise ToolExecutionError(f"Proposal creation failed: {e}")


class ListProposalsTool(IToolAdapter):
    """List all proposals by topic."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="proposal.list",
            version="1.0.0",
            category="proposal",
            summary="List all swarm proposals (optionally by topic)",
            required_params=[],
            optional_params={"topic": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return True, []

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """List proposals."""
        try:
            topic = params.get("topic")
            
            if not PROPOSALS_DIR.exists():
                return ToolResult(
                    success=True,
                    output={"topics": [], "total_proposals": 0},
                    exit_code=0,
                    execution_time=0.0,
                )
            
            if topic:
                # List proposals for specific topic
                topic_dir = PROPOSALS_DIR / topic
                if not topic_dir.exists():
                    return ToolResult(
                        success=True,
                        output={"topic": topic, "proposals": []},
                        exit_code=0,
                        execution_time=0.0,
                    )
                
                proposals = [
                    p.name for p in topic_dir.glob("*.md") 
                    if p.name != "README.md" and p.name != "DEBATE.xml"
                ]
                
                return ToolResult(
                    success=True,
                    output={"topic": topic, "proposals": proposals, "count": len(proposals)},
                    exit_code=0,
                    execution_time=0.0,
                )
            else:
                # List all topics and proposals
                topics = {}
                total = 0
                
                for topic_dir in PROPOSALS_DIR.iterdir():
                    if topic_dir.is_dir():
                        proposals = [
                            p.name for p in topic_dir.glob("*.md")
                            if p.name != "README.md" and p.name != "DEBATE.xml"
                        ]
                        topics[topic_dir.name] = proposals
                        total += len(proposals)
                
                return ToolResult(
                    success=True,
                    output={"topics": topics, "total_proposals": total},
                    exit_code=0,
                    execution_time=0.0,
                )
        except Exception as e:
            raise ToolExecutionError(f"Listing proposals failed: {e}")


class ViewProposalTool(IToolAdapter):
    """View a specific proposal."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="proposal.view",
            version="1.0.0",
            category="proposal",
            summary="View a specific swarm proposal",
            required_params=["topic", "filename"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        errors = []
        if "topic" not in params:
            errors.append("topic is required")
        if "filename" not in params:
            errors.append("filename is required")
        return len(errors) == 0, errors

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """View proposal."""
        try:
            topic = params["topic"]
            filename = params["filename"]
            
            proposal_file = PROPOSALS_DIR / topic / filename
            
            if not proposal_file.exists():
                raise ToolExecutionError(f"Proposal not found: {topic}/{filename}")
            
            content = proposal_file.read_text()
            
            return ToolResult(
                success=True,
                output={
                    "topic": topic,
                    "filename": filename,
                    "content": content,
                    "file_path": str(proposal_file),
                },
                exit_code=0,
                execution_time=0.0,
            )
        except Exception as e:
            raise ToolExecutionError(f"Viewing proposal failed: {e}")


class ContributeProposalTool(IToolAdapter):
    """Add alternative solution to existing topic."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="proposal.contribute",
            version="1.0.0",
            category="proposal",
            summary="Contribute alternative solution to existing proposal topic",
            required_params=["topic", "agent_id", "title", "content"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        errors = []
        required = ["topic", "agent_id", "title", "content"]
        for param in required:
            if param not in params:
                errors.append(f"{param} is required")
        return len(errors) == 0, errors

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Contribute to topic."""
        try:
            # Reuse create logic
            create_tool = CreateProposalTool()
            return create_tool.execute(params, context)
        except Exception as e:
            raise ToolExecutionError(f"Contributing proposal failed: {e}")


class StartDebateTool(IToolAdapter):
    """Start debate on proposal topic."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="proposal.debate",
            version="1.0.0",
            category="proposal",
            summary="Start democratic debate on proposal topic",
            required_params=["topic", "question"],
            optional_params={"duration_hours": 24},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        errors = []
        if "topic" not in params:
            errors.append("topic is required")
        if "question" not in params:
            errors.append("question is required")
        return len(errors) == 0, errors

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Start debate."""
        try:
            topic = params["topic"]
            question = params["question"]
            duration = params.get("duration_hours", 24)
            
            # Create DEBATE.xml file
            topic_dir = PROPOSALS_DIR / topic
            topic_dir.mkdir(parents=True, exist_ok=True)
            
            debate_file = topic_dir / "DEBATE.xml"
            
            debate_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<debate>
    <topic>{topic}</topic>
    <question>{question}</question>
    <started>{datetime.now().isoformat()}</started>
    <duration_hours>{duration}</duration_hours>
    <status>active</status>
    <votes>
    </votes>
    <comments>
    </comments>
</debate>
"""
            
            debate_file.write_text(debate_content)
            
            return ToolResult(
                success=True,
                output={
                    "topic": topic,
                    "debate_file": str(debate_file),
                    "question": question,
                    "status": "active",
                },
                exit_code=0,
                execution_time=0.0,
            )
        except Exception as e:
            raise ToolExecutionError(f"Starting debate failed: {e}")


# Export all tools
__all__ = [
    "CreateProposalTool",
    "ListProposalsTool",
    "ViewProposalTool",
    "ContributeProposalTool",
    "StartDebateTool",
]

