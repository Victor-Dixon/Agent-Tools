"""
Swarm Brain - Collective memory and knowledge sharing.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Learning:
    """A learned insight shared by an agent."""
    id: str
    agent_id: str
    category: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    upvotes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """A recorded decision with context and outcome."""
    id: str
    agent_id: str
    decision: str
    context: str
    outcome: Optional[str] = None
    success: Optional[bool] = None
    timestamp: datetime = field(default_factory=datetime.now)
    learnings: List[str] = field(default_factory=list)


class SwarmBrain:
    """
    Collective memory for the swarm - enables knowledge sharing across agents.
    
    Example:
        brain = SwarmBrain(brain_dir="./swarm_brain")
        
        # Share a learning
        brain.share_learning(
            agent_id="agent-1",
            category="debugging",
            title="Circular import fix pattern",
            content="When you see ImportError, check for circular imports..."
        )
        
        # Search knowledge
        results = brain.search("circular import")
        
        # Record a decision
        brain.record_decision(
            agent_id="agent-2",
            decision="Used async/await instead of threads",
            context="High concurrency API handler",
            outcome="50% latency reduction",
            success=True
        )
    """
    
    def __init__(self, brain_dir: str = "./swarm_brain"):
        """
        Initialize swarm brain.
        
        Args:
            brain_dir: Directory to store brain data
        """
        self.brain_dir = Path(brain_dir)
        self.brain_dir.mkdir(parents=True, exist_ok=True)
        
        self.learnings_dir = self.brain_dir / "learnings"
        self.decisions_dir = self.brain_dir / "decisions"
        self.notes_dir = self.brain_dir / "notes"
        
        self.learnings_dir.mkdir(exist_ok=True)
        self.decisions_dir.mkdir(exist_ok=True)
        self.notes_dir.mkdir(exist_ok=True)
        
        self._learning_counter = 0
        self._decision_counter = 0
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        if prefix == "learning":
            self._learning_counter += 1
            counter = self._learning_counter
        else:
            self._decision_counter += 1
            counter = self._decision_counter
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}_{timestamp}_{counter}"
    
    def share_learning(
        self,
        agent_id: str,
        category: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Learning:
        """
        Share a learning with the swarm.
        
        Args:
            agent_id: Agent sharing the learning
            category: Category (e.g., "debugging", "architecture", "tooling")
            title: Short title
            content: Full learning content
            tags: Optional tags for searching
            metadata: Additional metadata
            
        Returns:
            The created learning
        """
        learning = Learning(
            id=self._generate_id("learning"),
            agent_id=agent_id,
            category=category,
            title=title,
            content=content,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Save by category
        category_dir = self.learnings_dir / category
        category_dir.mkdir(exist_ok=True)
        
        learning_file = category_dir / f"{learning.id}.json"
        learning_data = {
            "id": learning.id,
            "agent_id": learning.agent_id,
            "category": learning.category,
            "title": learning.title,
            "content": learning.content,
            "tags": learning.tags,
            "timestamp": learning.timestamp.isoformat(),
            "upvotes": learning.upvotes,
            "metadata": learning.metadata
        }
        learning_file.write_text(json.dumps(learning_data, indent=2))
        
        return learning
    
    def record_decision(
        self,
        agent_id: str,
        decision: str,
        context: str,
        outcome: Optional[str] = None,
        success: Optional[bool] = None,
        learnings: Optional[List[str]] = None
    ) -> Decision:
        """
        Record a decision for future reference.
        
        Args:
            agent_id: Agent making the decision
            decision: What was decided
            context: Why this decision was made
            outcome: What happened (can be updated later)
            success: Whether it worked out
            learnings: Key learnings from this decision
            
        Returns:
            The recorded decision
        """
        dec = Decision(
            id=self._generate_id("decision"),
            agent_id=agent_id,
            decision=decision,
            context=context,
            outcome=outcome,
            success=success,
            learnings=learnings or []
        )
        
        # Save by agent
        agent_dir = self.decisions_dir / agent_id
        agent_dir.mkdir(exist_ok=True)
        
        dec_file = agent_dir / f"{dec.id}.json"
        dec_data = {
            "id": dec.id,
            "agent_id": dec.agent_id,
            "decision": dec.decision,
            "context": dec.context,
            "outcome": dec.outcome,
            "success": dec.success,
            "timestamp": dec.timestamp.isoformat(),
            "learnings": dec.learnings
        }
        dec_file.write_text(json.dumps(dec_data, indent=2))
        
        return dec
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Learning]:
        """
        Search learnings in the swarm brain.
        
        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum results
            
        Returns:
            Matching learnings
        """
        results = []
        query_lower = query.lower()
        
        # Search through learnings
        search_dirs = [self.learnings_dir / category] if category else [
            d for d in self.learnings_dir.iterdir() if d.is_dir()
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            for learning_file in search_dir.glob("*.json"):
                if len(results) >= limit:
                    break
                
                try:
                    data = json.loads(learning_file.read_text())
                    
                    # Simple text matching
                    searchable = (
                        data.get("title", "").lower() +
                        data.get("content", "").lower() +
                        " ".join(data.get("tags", []))
                    )
                    
                    if query_lower in searchable:
                        learning = Learning(
                            id=data["id"],
                            agent_id=data["agent_id"],
                            category=data["category"],
                            title=data["title"],
                            content=data["content"],
                            tags=data.get("tags", []),
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            upvotes=data.get("upvotes", 0),
                            metadata=data.get("metadata", {})
                        )
                        results.append(learning)
                except Exception:
                    pass
        
        return results
    
    def get_agent_notes(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all notes for an agent."""
        notes_file = self.notes_dir / f"{agent_id}.json"
        if not notes_file.exists():
            return []
        
        try:
            return json.loads(notes_file.read_text())
        except Exception:
            return []
    
    def add_note(self, agent_id: str, content: str, note_type: str = "general") -> Dict[str, Any]:
        """Add a note for an agent."""
        notes = self.get_agent_notes(agent_id)
        
        note = {
            "id": f"note_{len(notes) + 1}",
            "content": content,
            "type": note_type,
            "timestamp": datetime.now().isoformat()
        }
        notes.append(note)
        
        notes_file = self.notes_dir / f"{agent_id}.json"
        notes_file.write_text(json.dumps(notes, indent=2))
        
        return note
    
    def get_stats(self) -> Dict[str, Any]:
        """Get brain statistics."""
        learning_count = sum(
            len(list(d.glob("*.json")))
            for d in self.learnings_dir.iterdir()
            if d.is_dir()
        )
        
        decision_count = sum(
            len(list(d.glob("*.json")))
            for d in self.decisions_dir.iterdir()
            if d.is_dir()
        )
        
        return {
            "total_learnings": learning_count,
            "total_decisions": decision_count,
            "categories": [d.name for d in self.learnings_dir.iterdir() if d.is_dir()],
            "agents_with_decisions": [d.name for d in self.decisions_dir.iterdir() if d.is_dir()]
        }
