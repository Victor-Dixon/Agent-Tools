"""
Wolfpack MCP Toolbelt - Multi-Agent AI Coordination Framework
==============================================================

A Model Context Protocol (MCP) toolbelt for coordinating a pack of AI agents.
Enables autonomous agent-to-agent communication, task management, and pack intelligence.

🐺 "Alone we are strong. Together we are unstoppable."

Quick Start:
    from wolfpack_mcp import PackCoordinator
    
    pack = PackCoordinator(wolves=["alpha", "beta", "scout"])
    pack.howl("alpha", "Hunt begins at dawn")
    pack.broadcast("All wolves: converge on target")

MCP Servers:
    - pack-messaging: Wolf-to-wolf communication
    - den-manager: Task queue and territory management  
    - pack-memory: Collective hunting knowledge
    - alpha-control: Pack coordination and rankings

License: MIT
"""

__version__ = "0.1.0"
__author__ = "Wolfpack Team"

from .core.coordinator import PackCoordinator
from .core.messaging import MessageQueue, howl, broadcast
from .core.memory import PackMemory

__all__ = [
    "PackCoordinator",
    "MessageQueue", 
    "howl",
    "broadcast",
    "PackMemory",
]
