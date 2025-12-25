"""
Swarm MCP Toolbelt - Multi-Agent AI Coordination Framework
===========================================================

🐺 WE ARE SWARM - A pack of wolves, not bees.

A Model Context Protocol (MCP) toolbelt for coordinating a swarm of AI agents.
Like wolves hunting together - communicating, sharing knowledge, and 
coordinating attacks without human intervention.

"Alone we are strong. Together we are unstoppable."

Quick Start:
    from swarm_mcp import PackCoordinator
    
    pack = PackCoordinator(wolves=["alpha", "beta", "scout"])
    pack.howl("alpha", "Hunt begins at dawn")
    pack.broadcast("All wolves: converge on target")

MCP Servers:
    - swarm-messaging: Wolf-to-wolf communication (howls)
    - swarm-tasks: Hunt queue and territory management  
    - swarm-memory: Collective pack knowledge
    - swarm-control: Alpha coordination and rankings

License: MIT
"""

__version__ = "0.1.0"
__author__ = "The Swarm"

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
