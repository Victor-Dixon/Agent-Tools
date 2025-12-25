"""
Pack Memory - Collective hunting knowledge.

🐺 The pack remembers. Every hunt teaches us something.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class HuntingLore:
    """Knowledge learned from the hunt."""
    id: str
    wolf_id: str
    category: str
    title: str
    wisdom: str
    tags: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    respect: int = 0  # upvotes from pack
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HuntRecord:
    """Record of a hunt decision and outcome."""
    id: str
    wolf_id: str
    decision: str
    context: str
    outcome: Optional[str] = None
    success: Optional[bool] = None
    timestamp: datetime = field(default_factory=datetime.now)
    lessons: List[str] = field(default_factory=list)


class PackMemory:
    """
    🐺 Collective memory of the pack - wisdom passed down through generations.
    
    Example:
        memory = PackMemory(den="./pack_memory")
        
        # Share hunting wisdom
        memory.share_lore(
            wolf_id="scout-1",
            category="debugging",
            title="Tracking circular imports",
            wisdom="When ImportError strikes, check for circular dependencies..."
        )
        
        # Search pack knowledge
        lore = memory.recall("circular import")
        
        # Record hunt decisions
        memory.record_hunt(
            wolf_id="beta",
            decision="Used async over threads",
            context="High concurrency API",
            outcome="50% faster",
            success=True
        )
    """
    
    def __init__(self, den: str = "./pack_memory"):
        """
        Initialize pack memory.
        
        Args:
            den: Directory for pack memory
        """
        self.den = Path(den)
        self.den.mkdir(parents=True, exist_ok=True)
        
        self.lore_den = self.den / "lore"
        self.hunt_records = self.den / "hunts"
        self.wolf_notes = self.den / "notes"
        
        self.lore_den.mkdir(exist_ok=True)
        self.hunt_records.mkdir(exist_ok=True)
        self.wolf_notes.mkdir(exist_ok=True)
        
        self._lore_counter = 0
        self._hunt_counter = 0
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        if prefix == "lore":
            self._lore_counter += 1
            counter = self._lore_counter
        else:
            self._hunt_counter += 1
            counter = self._hunt_counter
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}_{timestamp}_{counter}"
    
    def share_lore(
        self,
        wolf_id: str,
        category: str,
        title: str,
        wisdom: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> HuntingLore:
        """
        🐺 Share hunting wisdom with the pack.
        
        Args:
            wolf_id: Wolf sharing the wisdom
            category: Category (tracking, hunting, territory, etc.)
            title: Short title
            wisdom: The knowledge to share
            tags: Search tags
            metadata: Extra data
            
        Returns:
            The created lore
        """
        lore = HuntingLore(
            id=self._generate_id("lore"),
            wolf_id=wolf_id,
            category=category,
            title=title,
            wisdom=wisdom,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Save by category
        category_den = self.lore_den / category
        category_den.mkdir(exist_ok=True)
        
        lore_file = category_den / f"{lore.id}.json"
        lore_data = {
            "id": lore.id,
            "wolf_id": lore.wolf_id,
            "category": lore.category,
            "title": lore.title,
            "wisdom": lore.wisdom,
            "tags": lore.tags,
            "timestamp": lore.timestamp.isoformat(),
            "respect": lore.respect,
            "metadata": lore.metadata
        }
        lore_file.write_text(json.dumps(lore_data, indent=2))
        
        return lore
    
    def record_hunt(
        self,
        wolf_id: str,
        decision: str,
        context: str,
        outcome: Optional[str] = None,
        success: Optional[bool] = None,
        lessons: Optional[List[str]] = None
    ) -> HuntRecord:
        """
        🐺 Record a hunt for future reference.
        
        Args:
            wolf_id: Wolf who led the hunt
            decision: What was decided
            context: Why this approach
            outcome: What happened
            success: Did it work
            lessons: Key takeaways
            
        Returns:
            The hunt record
        """
        record = HuntRecord(
            id=self._generate_id("hunt"),
            wolf_id=wolf_id,
            decision=decision,
            context=context,
            outcome=outcome,
            success=success,
            lessons=lessons or []
        )
        
        # Save by wolf
        wolf_records = self.hunt_records / wolf_id
        wolf_records.mkdir(exist_ok=True)
        
        record_file = wolf_records / f"{record.id}.json"
        record_data = {
            "id": record.id,
            "wolf_id": record.wolf_id,
            "decision": record.decision,
            "context": record.context,
            "outcome": record.outcome,
            "success": record.success,
            "timestamp": record.timestamp.isoformat(),
            "lessons": record.lessons
        }
        record_file.write_text(json.dumps(record_data, indent=2))
        
        return record
    
    def recall(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[HuntingLore]:
        """
        🐺 Recall wisdom from pack memory.
        
        Args:
            query: What to search for
            category: Optional category filter
            limit: Max results
            
        Returns:
            Matching lore
        """
        results = []
        query_lower = query.lower()
        
        search_dens = [self.lore_den / category] if category else [
            d for d in self.lore_den.iterdir() if d.is_dir()
        ]
        
        for search_den in search_dens:
            if not search_den.exists():
                continue
            
            for lore_file in search_den.glob("*.json"):
                if len(results) >= limit:
                    break
                
                try:
                    data = json.loads(lore_file.read_text())
                    
                    searchable = (
                        data.get("title", "").lower() +
                        data.get("wisdom", "").lower() +
                        " ".join(data.get("tags", []))
                    )
                    
                    if query_lower in searchable:
                        lore = HuntingLore(
                            id=data["id"],
                            wolf_id=data["wolf_id"],
                            category=data["category"],
                            title=data["title"],
                            wisdom=data["wisdom"],
                            tags=data.get("tags", []),
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            respect=data.get("respect", 0),
                            metadata=data.get("metadata", {})
                        )
                        results.append(lore)
                except Exception:
                    pass
        
        return results
    
    def get_wolf_notes(self, wolf_id: str) -> List[Dict[str, Any]]:
        """Get personal notes for a wolf."""
        notes_file = self.wolf_notes / f"{wolf_id}.json"
        if not notes_file.exists():
            return []
        
        try:
            return json.loads(notes_file.read_text())
        except Exception:
            return []
    
    def add_note(self, wolf_id: str, content: str, note_type: str = "general") -> Dict[str, Any]:
        """Add a personal note for a wolf."""
        notes = self.get_wolf_notes(wolf_id)
        
        note = {
            "id": f"note_{len(notes) + 1}",
            "content": content,
            "type": note_type,
            "timestamp": datetime.now().isoformat()
        }
        notes.append(note)
        
        notes_file = self.wolf_notes / f"{wolf_id}.json"
        notes_file.write_text(json.dumps(notes, indent=2))
        
        return note
    
    def pack_stats(self) -> Dict[str, Any]:
        """Get pack memory statistics."""
        lore_count = sum(
            len(list(d.glob("*.json")))
            for d in self.lore_den.iterdir()
            if d.is_dir()
        )
        
        hunt_count = sum(
            len(list(d.glob("*.json")))
            for d in self.hunt_records.iterdir()
            if d.is_dir()
        )
        
        return {
            "total_lore": lore_count,
            "total_hunts": hunt_count,
            "categories": [d.name for d in self.lore_den.iterdir() if d.is_dir()],
            "active_wolves": [d.name for d in self.hunt_records.iterdir() if d.is_dir()]
        }
