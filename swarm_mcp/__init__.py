"""
Swarm MCP Toolbelt - Multi-Agent AI Coordination Framework
===========================================================

🐺 WE ARE SWARM - A pack of wolves, not bees.

A Model Context Protocol (MCP) toolbelt for coordinating a swarm of AI agents.
Like wolves hunting together - communicating, sharing knowledge, and 
coordinating attacks without human intervention.

"Alone we are strong. Together we are unstoppable."

Core Features:
    - PackCoordinator: Central orchestration for the swarm
    - MessageQueue: Agent-to-agent async messaging
    - PackMemory: Collective knowledge sharing

IP-Level Features:
    - ConsensusEngine: Multi-agent voting and decision making
    - ConflictDetector: Prevent duplicate work across agents
    - AgentDNA: Learn agent strengths over time
    - WorkProofSystem: Cryptographic proof of work completion
    - PatternMiner: Learn from successful coordination patterns

Quick Start:
    from swarm_mcp import PackCoordinator, ConsensusEngine, AgentDNA
    
    # Coordinate agents
    pack = PackCoordinator(wolves=["agent-1", "agent-2", "agent-3"])
    pack.assign_hunt("agent-1", "Fix the auth bug")
    
    # Make collective decisions
    consensus = ConsensusEngine()
    proposal = consensus.propose("agent-1", "Use PostgreSQL", "Need ACID...")
    consensus.vote(proposal.id, "agent-2", VoteType.APPROVE, "Agree")
    
    # Learn agent strengths
    dna = AgentDNA()
    best = dna.find_best_agent(category="debugging", files=["auth.py"])

License: MIT
"""

__version__ = "0.1.0"
__author__ = "The Swarm"

# Core modules
from .core.coordinator import PackCoordinator
from .core.messaging import MessageQueue, howl, broadcast
from .core.memory import PackMemory

# IP-level modules
from .core.consensus import ConsensusEngine, Proposal, Vote, VoteType, ConsensusRule
from .core.conflict import ConflictDetector, WorkIntent, Conflict, ConflictSeverity
from .core.agent_dna import AgentDNA, AgentProfile, TaskRecord
from .core.work_proof import WorkProofSystem, WorkCommitment, WorkProof
from .core.pattern_miner import PatternMiner, Pattern, Suggestion, CoordinationEvent

__all__ = [
    # Core
    "PackCoordinator",
    "MessageQueue", 
    "howl",
    "broadcast",
    "PackMemory",
    # Consensus
    "ConsensusEngine",
    "Proposal",
    "Vote",
    "VoteType",
    "ConsensusRule",
    # Conflict Detection
    "ConflictDetector",
    "WorkIntent",
    "Conflict",
    "ConflictSeverity",
    # Agent DNA
    "AgentDNA",
    "AgentProfile",
    "TaskRecord",
    # Work Proof
    "WorkProofSystem",
    "WorkCommitment",
    "WorkProof",
    # Pattern Mining
    "PatternMiner",
    "Pattern",
    "Suggestion",
    "CoordinationEvent",
]
