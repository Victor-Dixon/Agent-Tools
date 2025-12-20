"""
Debate System Tools
===================

Democratic decision-making system for multi-agent debates and voting.

Based on ACTIVE_DEBATE_COORDINATION.md specification.
Enables swarm intelligence through structured argumentation and consensus building.

V2 Compliance: <400 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class DebateStartTool(IToolAdapter):
    """Start a new multi-agent debate."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="debate.start",
            version="1.0.0",
            category="debate",
            summary="Start a new multi-agent debate with voting options",
            required_params=["topic", "options"],
            optional_params={"deadline": None, "description": ""},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        is_valid, missing = spec.validate_params(params)

        # Validate options is a list
        if is_valid and not isinstance(params.get("options"), list):
            return (False, ["options must be a list"])

        if is_valid and len(params.get("options", [])) < 2:
            return (False, ["options must have at least 2 choices"])

        return (is_valid, missing)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute debate creation."""
        try:
            debate_data = {
                "debate_id": f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "topic": params["topic"],
                "description": params.get("description", ""),
                "options": params["options"],
                "deadline": params.get("deadline"),
                "created": datetime.now().isoformat(),
                "status": "active",
                "votes": {},
                "arguments": [],
            }

            # Save debate
            debates_dir = Path("debates")
            debates_dir.mkdir(exist_ok=True)

            debate_file = debates_dir / f"{debate_data['debate_id']}.json"
            debate_file.write_text(json.dumps(debate_data, indent=2))

            return ToolResult(
                success=True,
                output={
                    "debate_id": debate_data["debate_id"],
                    "topic": debate_data["topic"],
                    "options": debate_data["options"],
                    "status": "Debate created successfully",
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error starting debate: {e}")
            raise ToolExecutionError(str(e), tool_name="debate.start")


class DebateVoteTool(IToolAdapter):
    """Cast vote in active debate."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="debate.vote",
            version="1.0.0",
            category="debate",
            summary="Cast vote in an active debate with optional argument",
            required_params=["debate_id", "agent_id", "option"],
            optional_params={"argument": "", "confidence": 5},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute vote casting."""
        try:
            debate_id = params["debate_id"]
            agent_id = params["agent_id"]
            option = params["option"]

            # Load debate
            debate_file = Path("debates") / f"{debate_id}.json"
            if not debate_file.exists():
                return ToolResult(
                    success=False, output={"error": f"Debate {debate_id} not found"}, exit_code=1
                )

            debate_data = json.loads(debate_file.read_text())

            # Validate option
            if option not in debate_data["options"]:
                return ToolResult(
                    success=False,
                    output={"error": f"Invalid option. Choose from: {debate_data['options']}"},
                    exit_code=1,
                )

            # Record vote
            vote_data = {
                "option": option,
                "timestamp": datetime.now().isoformat(),
                "confidence": params.get("confidence", 5),
                "argument": params.get("argument", ""),
            }

            debate_data["votes"][agent_id] = vote_data

            # Add to arguments if provided
            if vote_data["argument"]:
                debate_data["arguments"].append(
                    {
                        "agent_id": agent_id,
                        "option": option,
                        "argument": vote_data["argument"],
                        "confidence": vote_data["confidence"],
                        "timestamp": vote_data["timestamp"],
                    }
                )

            # Save updated debate
            debate_file.write_text(json.dumps(debate_data, indent=2))

            return ToolResult(
                success=True,
                output={
                    "debate_id": debate_id,
                    "agent_id": agent_id,
                    "vote": option,
                    "total_votes": len(debate_data["votes"]),
                    "status": "Vote recorded successfully",
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error casting vote: {e}")
            raise ToolExecutionError(str(e), tool_name="debate.vote")


class DebateStatusTool(IToolAdapter):
    """Get current debate status and results."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="debate.status",
            version="1.0.0",
            category="debate",
            summary="Get current status, votes, and consensus for a debate",
            required_params=["debate_id"],
            optional_params={"detailed": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute status check."""
        try:
            debate_id = params["debate_id"]
            detailed = params.get("detailed", False)

            # Load debate
            debate_file = Path("debates") / f"{debate_id}.json"
            if not debate_file.exists():
                return ToolResult(
                    success=False, output={"error": f"Debate {debate_id} not found"}, exit_code=1
                )

            debate_data = json.loads(debate_file.read_text())

            # Calculate vote distribution
            vote_counts = {}
            for agent_id, vote in debate_data["votes"].items():
                option = vote["option"]
                vote_counts[option] = vote_counts.get(option, 0) + 1

            # Calculate consensus
            total_votes = len(debate_data["votes"])
            consensus = None
            if total_votes > 0:
                leading_option = max(vote_counts.items(), key=lambda x: x[1])
                consensus_percent = (leading_option[1] / total_votes) * 100
                consensus = {
                    "option": leading_option[0],
                    "votes": leading_option[1],
                    "percent": round(consensus_percent, 1),
                }

            output = {
                "debate_id": debate_id,
                "topic": debate_data["topic"],
                "status": debate_data["status"],
                "total_votes": total_votes,
                "vote_distribution": vote_counts,
                "consensus": consensus,
                "arguments_count": len(debate_data["arguments"]),
            }

            if detailed:
                output["votes"] = debate_data["votes"]
                output["arguments"] = debate_data["arguments"]

            return ToolResult(success=True, output=output, exit_code=0)
        except Exception as e:
            logger.error(f"Error getting debate status: {e}")
            raise ToolExecutionError(str(e), tool_name="debate.status")


class DebateNotifyTool(IToolAdapter):
    """Notify agents to participate in debate."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="debate.notify",
            version="1.0.0",
            category="debate",
            summary="Notify pending agents to participate in debate",
            required_params=["debate_id"],
            optional_params={"urgency": "medium", "agents": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute notification."""
        try:
            debate_id = params["debate_id"]
            urgency = params.get("urgency", "medium")
            target_agents = params.get("agents")

            # Load debate
            debate_file = Path("debates") / f"{debate_id}.json"
            if not debate_file.exists():
                return ToolResult(
                    success=False, output={"error": f"Debate {debate_id} not found"}, exit_code=1
                )

            debate_data = json.loads(debate_file.read_text())

            # Find agents who haven't voted
            all_agents = [f"Agent-{i}" for i in range(1, 9)]  # Agent-1 through Agent-8
            voted_agents = set(debate_data["votes"].keys())
            pending_agents = [a for a in all_agents if a not in voted_agents]

            # Filter to target agents if specified
            if target_agents:
                pending_agents = [a for a in pending_agents if a in target_agents]

            # Create notification message
            urgency_emoji = {"low": "📢", "medium": "⚠️", "high": "🚨", "urgent": "🔥"}
            emoji = urgency_emoji.get(urgency, "📢")

            message = f"""{emoji} DEBATE PARTICIPATION REQUESTED

Debate: {debate_data['topic']}
Status: {debate_data['status']}
Current Votes: {len(debate_data['votes'])}/{len(all_agents)}
Your Vote: Not yet cast

Options:
{chr(10).join(f"  {i+1}. {opt}" for i, opt in enumerate(debate_data['options']))}

Cast your vote:
  python tools/agent_toolbelt.py debate vote --debate-id {debate_id} --agent YOUR_ID --option "choice" --argument "your reasoning"
"""

            # Send notifications (via messaging system)
            notifications_sent = []
            for agent_id in pending_agents:
                # Create inbox message
                inbox_dir = Path(f"agent_workspaces/{agent_id}/inbox")
                inbox_dir.mkdir(parents=True, exist_ok=True)

                msg_file = inbox_dir / f"DEBATE_{debate_id}_{urgency.upper()}.md"
                msg_file.write_text(message)

                notifications_sent.append(agent_id)

            return ToolResult(
                success=True,
                output={
                    "debate_id": debate_id,
                    "urgency": urgency,
                    "notifications_sent": len(notifications_sent),
                    "agents_notified": notifications_sent,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
            raise ToolExecutionError(str(e), tool_name="debate.notify")
