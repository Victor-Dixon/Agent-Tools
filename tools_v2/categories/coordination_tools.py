"""
Coordination Tools - Agent Toolbelt Category
===========================================

Tools for expert coordination (Pattern #5) and swarm collaboration.

Based on Agent-1 + Agent-2 coordination success.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import json
from pathlib import Path

from ..adapters.base_adapter import IToolAdapter, ToolResult


class FindDomainExpertAdapter(IToolAdapter):
    """Find which agent has expertise in a given domain."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="coord.find-expert",
            version="1.0.0",
            category="coordination",
            summary="Find domain expert agent for Pattern #5 coordination",
            required_params=["domain"],
            optional_params={},
        )

    def get_help(self) -> str:
        return """
Find Domain Expert
==================
Identifies which agent has expertise in a specific domain.

Parameters:
  domain: Domain to find expert for (architecture, integration, v2-compliance, etc.)
  
Returns: Agent ID and specialization info
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        if "domain" not in params:
            return False, ["domain"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        domain = params["domain"].lower()

        # Agent specializations (from AGENTS.md)
        experts = {
            "architecture": {"agent": "Agent-2", "title": "Architecture & Design Specialist"},
            "integration": {"agent": "Agent-1", "title": "Integration & Core Systems Specialist"},
            "v2-compliance": {"agent": "Agent-1", "title": "V2 Compliance Specialist"},
            "code-cleanup": {"agent": "Agent-3", "title": "Code Cleanup Specialist"},
            "coordination": {"agent": "Agent-4", "title": "Captain - Swarm Coordinator"},
            "database": {"agent": "Agent-5", "title": "Database Specialist"},
            "testing": {"agent": "Agent-6", "title": "Quality Gates Specialist"},
            "web": {"agent": "Agent-7", "title": "Web Development Specialist"},
            "devops": {"agent": "Agent-8", "title": "DevOps Specialist"},
        }

        expert = experts.get(
            domain,
            {
                "agent": "Captain",
                "title": "Swarm Coordinator",
                "note": f"No specific expert for {domain}, consult Captain",
            },
        )

        return ToolResult(success=True, output=expert, exit_code=0)


class RequestExpertReviewAdapter(IToolAdapter):
    """Request expert review using Pattern #5 coordination."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="coord.request-review",
            version="1.0.0",
            category="coordination",
            summary="Request expert review (Pattern #5)",
            required_params=["domain", "topic", "agent"],
            optional_params={},
        )

    def get_help(self) -> str:
        return """
Request Expert Review
====================
Sends a review request to domain expert (implements Pattern #5).

Parameters:
  domain: Domain expertise needed
  topic: What needs review
  agent: Your agent ID
  
Returns: Success status and expert agent ID
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        required = ["domain", "topic", "agent"]
        missing = [p for p in required if p not in params]
        if missing:
            return False, missing
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        domain = params["domain"]
        topic = params["topic"]
        requester = params["agent"]

        try:
            # Find expert
            expert_finder = FindDomainExpertAdapter()
            expert_result = expert_finder.execute({"domain": domain}, context)

            if not expert_result.success:
                return expert_result

            expert_agent = expert_result.output["agent"]

            # Create review request message
            message = f"""[A2A] {requester} → {expert_agent}: Expert Review Request

**Domain:** {domain}
**Topic:** {topic}

**Pattern #5 Coordination:**
I've discovered {topic} and would like your expert review before proceeding.

Please validate:
1. Is the approach sound?
2. Any architectural concerns?
3. Any suggestions for improvement?

Standing by for your guidance!

{requester}"""

            # Would actually send message here via messaging system
            # For now, return the formatted message

            return ToolResult(
                success=True,
                output={
                    "expert": expert_agent,
                    "message": message,
                    "pattern": "Pattern #5 - Expert Coordination",
                },
                exit_code=0,
            )
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class CheckCoordinationPatternsAdapter(IToolAdapter):
    """Check swarm brain for coordination patterns."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="coord.check-patterns",
            version="1.0.0",
            category="coordination",
            summary="Check swarm brain for coordination patterns",
            required_params=[],
            optional_params={},
        )

    def get_help(self) -> str:
        return """
Check Coordination Patterns
===========================
Reads swarm brain to find coordination patterns.

Parameters:
  None
  
Returns: List of coordination patterns
        """

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        try:
            brain_path = Path("runtime/swarm_brain.json")

            if not brain_path.exists():
                return ToolResult(
                    success=False, output=None, exit_code=1, error_message="Swarm brain not found"
                )

            with open(brain_path) as f:
                brain = json.load(f)

            patterns = brain.get("patterns", [])

            # Find coordination-related patterns
            coord_patterns = [
                p
                for p in patterns
                if any(
                    tag in p.get("tags", [])
                    for tag in ["coordination", "expert", "pattern", "collaboration"]
                )
            ]

            return ToolResult(
                success=True,
                output={
                    "patterns": coord_patterns,
                    "count": len(coord_patterns),
                    "total_patterns": len(patterns),
                },
                exit_code=0,
            )
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class SwarmOrchestratorAdapter(IToolAdapter):
    """Autonomous swarm orchestrator - 'The Gas Station'."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="coord.swarm_orchestrate",
            version="1.0.0",
            category="coordination",
            summary="Run autonomous swarm orchestration cycle (gas delivery)",
            required_params=[],
            optional_params={"cycles": 1, "interval": 300},
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Run orchestration cycle."""
        try:
            import subprocess
            import sys
            from pathlib import Path

            cycles = params.get("cycles", 1)
            interval = params.get("interval", 300)

            project_root = Path.cwd()

            cmd = [
                sys.executable,
                str(project_root / "tools" / "swarm_orchestrator.py"),
                "--cycles",
                str(cycles),
                "--interval",
                str(interval),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            return ToolResult(
                success=result.returncode == 0,
                output={
                    "cycles_run": cycles,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class SwarmStatusBroadcasterAdapter(IToolAdapter):
    """Broadcast status messages to multiple agents."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="coord.broadcast_status",
            version="1.0.0",
            category="coordination",
            summary="Broadcast status message to multiple agents",
            required_params=["message"],
            optional_params={
                "priority": "regular",
                "exclude_agents": [],
                "include_only": None,
                "use_pyautogui": False,
            },
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        if "message" not in params:
            return False, ["message"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Broadcast status message."""
        try:
            import subprocess
            import sys
            from pathlib import Path

            message = params["message"]
            priority = params.get("priority", "regular")
            exclude_agents = params.get("exclude_agents", [])
            include_only = params.get("include_only")
            use_pyautogui = params.get("use_pyautogui", False)

            project_root = Path.cwd()
            broadcaster_path = project_root / "tools" / "swarm_status_broadcaster.py"

            # Use Python to import and execute
            import sys

            sys.path.insert(0, str(project_root / "tools"))

            from swarm_status_broadcaster import SwarmStatusBroadcaster

            broadcaster = SwarmStatusBroadcaster()

            results = broadcaster.broadcast(
                message=message,
                priority=priority,
                exclude_agents=exclude_agents if exclude_agents else None,
                include_only=include_only,
                use_pyautogui=use_pyautogui,
            )

            success_count = sum(1 for v in results.values() if v)
            total_count = len(results)

            return ToolResult(
                success=success_count > 0,
                output={
                    "results": results,
                    "success_count": success_count,
                    "total_count": total_count,
                    "success_rate": success_count / total_count if total_count > 0 else 0,
                },
                exit_code=0 if success_count == total_count else 1,
            )
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class MissionControlAdapter(IToolAdapter):
    """Autonomous mission generator for swarm agents."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="coord.generate_mission",
            version="1.0.0",
            category="coordination",
            summary="Generate autonomous mission for agent",
            required_params=["agent_id"],
            optional_params={"force": False},
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        if "agent_id" not in params:
            return False, ["agent_id"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Generate mission for agent."""
        try:
            import subprocess
            import sys
            from pathlib import Path

            agent_id = params["agent_id"]
            force = params.get("force", False)

            project_root = Path.cwd()
            mission_control_path = project_root / "tools" / "mission_control.py"

            cmd = [sys.executable, str(mission_control_path), "--agent", agent_id]

            if force:
                cmd.append("--force")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            return ToolResult(
                success=result.returncode == 0,
                output={
                    "agent_id": agent_id,
                    "mission_generated": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class CoordinateValidatorAdapter(IToolAdapter):
    """Validate agent coordinates before PyAutoGUI operations."""

    def get_spec(self):
        from ..adapters.base_adapter import ToolSpec

        return ToolSpec(
            name="coord.validate_coordinates",
            version="1.0.0",
            category="coordination",
            summary="Validate agent coordinates for PyAutoGUI operations",
            required_params=[],
            optional_params={"agent_id": None},
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Validate coordinates."""
        try:
            import subprocess
            import sys
            from pathlib import Path

            agent_id = params.get("agent_id")

            project_root = Path.cwd()
            validator_path = project_root / "tools" / "captain_coordinate_validator.py"

            cmd = [sys.executable, str(validator_path)]

            if agent_id:
                cmd.extend(["--agent", agent_id])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            return ToolResult(
                success=result.returncode == 0,
                output={
                    "coordinates_valid": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


# Registration dictionary
COORDINATION_TOOLS = {
    "coord.find-expert": FindDomainExpertAdapter,
    "coord.request-review": RequestExpertReviewAdapter,
    "coord.check-patterns": CheckCoordinationPatternsAdapter,
    "coord.swarm_orchestrate": SwarmOrchestratorAdapter,
    "coord.broadcast_status": SwarmStatusBroadcasterAdapter,
    "coord.generate_mission": MissionControlAdapter,
    "coord.validate_coordinates": CoordinateValidatorAdapter,
}
