"""
Core Swarm Coordination Modules
================================

🐺 WE ARE SWARM - The pack hunts together.

Core Modules:
- PackCoordinator: Central orchestration
- MessageQueue: Agent-to-agent messaging
- PackMemory: Collective knowledge

IP-Level Modules:
- ConsensusEngine: Multi-agent voting & decisions
- ConflictDetector: Prevent duplicate work
- AgentDNA: Learn agent strengths over time
- WorkProofSystem: Verifiable task completion
- PatternMiner: Learn from successful coordination
"""

from .coordinator import PackCoordinator
from .messaging import MessageQueue, howl, broadcast
from .memory import PackMemory
from .consensus import ConsensusEngine, Proposal, Vote, VoteType, ConsensusRule
from .conflict import ConflictDetector, WorkIntent, Conflict, ConflictSeverity
from .agent_dna import AgentDNA, AgentProfile, TaskRecord
from .work_proof import WorkProofSystem, WorkCommitment, WorkProof
from .pattern_miner import PatternMiner, Pattern, Suggestion, CoordinationEvent

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
