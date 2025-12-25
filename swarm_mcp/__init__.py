"""
Swarm MCP Toolbelt - Multi-Agent AI Coordination Framework
===========================================================

A Model Context Protocol (MCP) toolbelt for coordinating multiple AI agents.
Enables autonomous agent-to-agent communication, task management, and swarm intelligence.

Quick Start:
    from swarm_mcp import SwarmCoordinator
    
    swarm = SwarmCoordinator(agents=["agent-1", "agent-2"])
    swarm.send_message("agent-1", "Start task X")
    swarm.broadcast("All agents: sync up")

MCP Servers:
    - swarm-messaging: Agent-to-agent communication
    - task-manager: Task queue and inbox management  
    - swarm-brain: Collective memory and knowledge sharing
    - mission-control: Agent coordination and leaderboard
    - git-operations: Work verification
    - code-quality: Compliance and refactoring
    - observability: Metrics and health checks
    - testing: Coverage and mutation testing

License: MIT
"""

__version__ = "0.1.0"
__author__ = "Swarm Team"

from .core.coordinator import SwarmCoordinator
from .core.messaging import MessageQueue, send_message, broadcast
from .core.brain import SwarmBrain

__all__ = [
    "SwarmCoordinator",
    "MessageQueue", 
    "send_message",
    "broadcast",
    "SwarmBrain",
]
