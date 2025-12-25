"""
Consensus Engine - Multi-Agent Decision Making
===============================================

🐺 WE ARE SWARM - When the pack must decide together.

This is IP-level code: A distributed consensus algorithm for AI agents.
Agents vote, discuss, and reach agreement without human intervention.

Use Cases:
- Code review approval (2 of 3 agents must approve)
- Architecture decisions (majority vote)
- Priority ranking (weighted voting by expertise)
- Conflict resolution (structured debate → vote)

Author: The Swarm
License: MIT
"""

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from collections import defaultdict


class VoteType(Enum):
    """Types of votes."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    DEFER = "defer"


class ConsensusRule(Enum):
    """Rules for reaching consensus."""
    UNANIMOUS = "unanimous"      # All must agree
    MAJORITY = "majority"        # >50% must agree
    SUPERMAJORITY = "super"      # >66% must agree
    QUORUM = "quorum"            # N specific agents must vote
    WEIGHTED = "weighted"        # Votes weighted by expertise


@dataclass
class Vote:
    """A vote cast by an agent."""
    agent_id: str
    vote: VoteType
    reasoning: str
    confidence: float = 1.0  # 0-1, how confident in this vote
    timestamp: datetime = field(default_factory=datetime.now)
    weight: float = 1.0  # For weighted voting


@dataclass
class Proposal:
    """A proposal for the swarm to vote on."""
    id: str
    title: str
    description: str
    proposer: str
    category: str  # architecture, code-review, priority, etc.
    options: List[str] = field(default_factory=lambda: ["approve", "reject"])
    votes: Dict[str, Vote] = field(default_factory=dict)
    rule: ConsensusRule = ConsensusRule.MAJORITY
    quorum_agents: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    status: str = "open"  # open, passed, rejected, expired
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    outcome: Optional[str] = None


class ConsensusEngine:
    """
    Distributed consensus for AI agent swarms.
    
    This is the core IP: enabling multiple AI agents to make
    collective decisions without human intervention.
    
    Example:
        engine = ConsensusEngine()
        
        # Create a proposal
        proposal = engine.propose(
            proposer="agent-1",
            title="Use PostgreSQL for user data",
            description="We need ACID transactions for payments...",
            category="architecture",
            rule=ConsensusRule.SUPERMAJORITY
        )
        
        # Agents vote
        engine.vote(proposal.id, "agent-2", VoteType.APPROVE, 
                   "Agree - ACID is critical for money")
        engine.vote(proposal.id, "agent-3", VoteType.APPROVE,
                   "Good choice, familiar with Postgres")
        engine.vote(proposal.id, "agent-4", VoteType.REJECT,
                   "Prefer MongoDB for flexibility")
        
        # Check result
        result = engine.resolve(proposal.id)
        print(result)  # {"passed": True, "votes": {"approve": 3, "reject": 1}}
    """
    
    def __init__(self, storage_dir: str = "./swarm_consensus"):
        """Initialize consensus engine."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.proposals: Dict[str, Proposal] = {}
        self._load_proposals()
    
    def _generate_id(self, title: str) -> str:
        """Generate unique proposal ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_input = f"{title}{timestamp}".encode()
        short_hash = hashlib.sha256(hash_input).hexdigest()[:8]
        return f"prop_{short_hash}"
    
    def _load_proposals(self):
        """Load proposals from storage."""
        for prop_file in self.storage_dir.glob("*.json"):
            try:
                data = json.loads(prop_file.read_text())
                votes = {}
                for agent_id, vote_data in data.get("votes", {}).items():
                    votes[agent_id] = Vote(
                        agent_id=vote_data["agent_id"],
                        vote=VoteType(vote_data["vote"]),
                        reasoning=vote_data["reasoning"],
                        confidence=vote_data.get("confidence", 1.0),
                        weight=vote_data.get("weight", 1.0)
                    )
                
                proposal = Proposal(
                    id=data["id"],
                    title=data["title"],
                    description=data["description"],
                    proposer=data["proposer"],
                    category=data["category"],
                    options=data.get("options", ["approve", "reject"]),
                    votes=votes,
                    rule=ConsensusRule(data.get("rule", "majority")),
                    status=data.get("status", "open"),
                    outcome=data.get("outcome")
                )
                self.proposals[proposal.id] = proposal
            except Exception:
                pass
    
    def _save_proposal(self, proposal: Proposal):
        """Save proposal to storage."""
        votes_data = {}
        for agent_id, vote in proposal.votes.items():
            votes_data[agent_id] = {
                "agent_id": vote.agent_id,
                "vote": vote.vote.value,
                "reasoning": vote.reasoning,
                "confidence": vote.confidence,
                "weight": vote.weight,
                "timestamp": vote.timestamp.isoformat()
            }
        
        data = {
            "id": proposal.id,
            "title": proposal.title,
            "description": proposal.description,
            "proposer": proposal.proposer,
            "category": proposal.category,
            "options": proposal.options,
            "votes": votes_data,
            "rule": proposal.rule.value,
            "status": proposal.status,
            "outcome": proposal.outcome,
            "created_at": proposal.created_at.isoformat()
        }
        
        prop_file = self.storage_dir / f"{proposal.id}.json"
        prop_file.write_text(json.dumps(data, indent=2))
    
    def propose(
        self,
        proposer: str,
        title: str,
        description: str,
        category: str = "general",
        rule: ConsensusRule = ConsensusRule.MAJORITY,
        options: Optional[List[str]] = None,
        quorum_agents: Optional[List[str]] = None,
        deadline_hours: Optional[int] = None
    ) -> Proposal:
        """
        Create a new proposal for the swarm to vote on.
        
        Args:
            proposer: Agent creating the proposal
            title: Short title
            description: Full description of what's being decided
            category: Type of decision (architecture, code-review, etc.)
            rule: How to determine consensus
            options: Custom options (default: approve/reject)
            quorum_agents: Required voters for QUORUM rule
            deadline_hours: Auto-expire after N hours
            
        Returns:
            The created proposal
        """
        proposal = Proposal(
            id=self._generate_id(title),
            title=title,
            description=description,
            proposer=proposer,
            category=category,
            options=options or ["approve", "reject"],
            rule=rule,
            quorum_agents=quorum_agents or [],
            deadline=datetime.now() + timedelta(hours=deadline_hours) if deadline_hours else None
        )
        
        self.proposals[proposal.id] = proposal
        self._save_proposal(proposal)
        
        return proposal
    
    def vote(
        self,
        proposal_id: str,
        agent_id: str,
        vote: VoteType,
        reasoning: str,
        confidence: float = 1.0,
        weight: float = 1.0
    ) -> bool:
        """
        Cast a vote on a proposal.
        
        Args:
            proposal_id: Proposal to vote on
            agent_id: Agent casting the vote
            vote: The vote (approve, reject, abstain, defer)
            reasoning: Why this vote
            confidence: How confident (0-1)
            weight: Vote weight for weighted voting
            
        Returns:
            True if vote was recorded
        """
        if proposal_id not in self.proposals:
            raise ValueError(f"Unknown proposal: {proposal_id}")
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != "open":
            raise ValueError(f"Proposal is {proposal.status}, cannot vote")
        
        if proposal.deadline and datetime.now() > proposal.deadline:
            proposal.status = "expired"
            self._save_proposal(proposal)
            raise ValueError("Proposal has expired")
        
        proposal.votes[agent_id] = Vote(
            agent_id=agent_id,
            vote=vote,
            reasoning=reasoning,
            confidence=confidence,
            weight=weight
        )
        
        self._save_proposal(proposal)
        return True
    
    def get_tally(self, proposal_id: str) -> Dict[str, Any]:
        """
        Get current vote tally for a proposal.
        
        Returns:
            Vote counts and percentages
        """
        if proposal_id not in self.proposals:
            raise ValueError(f"Unknown proposal: {proposal_id}")
        
        proposal = self.proposals[proposal_id]
        
        tally = defaultdict(lambda: {"count": 0, "weight": 0.0, "agents": []})
        total_votes = len(proposal.votes)
        total_weight = sum(v.weight for v in proposal.votes.values())
        
        for agent_id, vote in proposal.votes.items():
            vote_type = vote.vote.value
            tally[vote_type]["count"] += 1
            tally[vote_type]["weight"] += vote.weight
            tally[vote_type]["agents"].append(agent_id)
        
        result = {
            "proposal_id": proposal_id,
            "title": proposal.title,
            "status": proposal.status,
            "rule": proposal.rule.value,
            "total_votes": total_votes,
            "total_weight": total_weight,
            "tally": dict(tally),
            "votes": {
                agent_id: {
                    "vote": v.vote.value,
                    "reasoning": v.reasoning,
                    "confidence": v.confidence
                }
                for agent_id, v in proposal.votes.items()
            }
        }
        
        return result
    
    def resolve(self, proposal_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Resolve a proposal - determine if consensus was reached.
        
        Args:
            proposal_id: Proposal to resolve
            force: Force resolution even if quorum not met
            
        Returns:
            Resolution result with outcome
        """
        if proposal_id not in self.proposals:
            raise ValueError(f"Unknown proposal: {proposal_id}")
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != "open" and not force:
            return {
                "proposal_id": proposal_id,
                "status": proposal.status,
                "outcome": proposal.outcome,
                "already_resolved": True
            }
        
        tally = self.get_tally(proposal_id)
        votes = proposal.votes
        
        approve_count = tally["tally"].get("approve", {}).get("count", 0)
        reject_count = tally["tally"].get("reject", {}).get("count", 0)
        total_votes = len(votes)
        
        approve_weight = tally["tally"].get("approve", {}).get("weight", 0)
        total_weight = tally["total_weight"]
        
        passed = False
        reason = ""
        
        if proposal.rule == ConsensusRule.UNANIMOUS:
            passed = reject_count == 0 and approve_count > 0
            reason = "All voters approved" if passed else "Not unanimous"
            
        elif proposal.rule == ConsensusRule.MAJORITY:
            if total_votes > 0:
                passed = approve_count > total_votes / 2
                reason = f"{approve_count}/{total_votes} approved (>50% required)"
            else:
                reason = "No votes cast"
                
        elif proposal.rule == ConsensusRule.SUPERMAJORITY:
            if total_votes > 0:
                passed = approve_count >= total_votes * 2 / 3
                reason = f"{approve_count}/{total_votes} approved (>66% required)"
            else:
                reason = "No votes cast"
                
        elif proposal.rule == ConsensusRule.QUORUM:
            required = set(proposal.quorum_agents)
            voted = set(votes.keys())
            if required.issubset(voted):
                passed = approve_count > reject_count
                reason = f"Quorum met, {approve_count} approve vs {reject_count} reject"
            else:
                missing = required - voted
                reason = f"Quorum not met, missing: {missing}"
                
        elif proposal.rule == ConsensusRule.WEIGHTED:
            if total_weight > 0:
                passed = approve_weight > total_weight / 2
                reason = f"Weighted: {approve_weight:.1f}/{total_weight:.1f} approved"
            else:
                reason = "No weighted votes"
        
        proposal.status = "passed" if passed else "rejected"
        proposal.outcome = reason
        proposal.resolved_at = datetime.now()
        self._save_proposal(proposal)
        
        return {
            "proposal_id": proposal_id,
            "title": proposal.title,
            "passed": passed,
            "reason": reason,
            "tally": tally["tally"],
            "status": proposal.status
        }
    
    def get_open_proposals(self, category: Optional[str] = None) -> List[Proposal]:
        """Get all open proposals, optionally filtered by category."""
        proposals = [p for p in self.proposals.values() if p.status == "open"]
        if category:
            proposals = [p for p in proposals if p.category == category]
        return sorted(proposals, key=lambda p: p.created_at, reverse=True)
    
    def get_agent_pending_votes(self, agent_id: str) -> List[Proposal]:
        """Get proposals where an agent hasn't voted yet."""
        pending = []
        for proposal in self.proposals.values():
            if proposal.status == "open" and agent_id not in proposal.votes:
                pending.append(proposal)
        return pending
