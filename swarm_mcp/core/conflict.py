"""
Conflict Detector - Prevent Duplicate Work
===========================================

🐺 WE ARE SWARM - The pack doesn't chase the same prey.

This is IP-level code: Detects when multiple agents are working on
the same task, file, or problem - preventing wasted effort and merge conflicts.

The Problem:
- Agent-1 starts fixing auth.py
- Agent-2 doesn't know, also starts fixing auth.py
- Both spend 30 minutes on the same work
- Merge conflict, wasted time, frustration

The Solution:
- Agents declare intent BEFORE starting work
- System detects overlaps in real-time
- Conflicts resolved before work begins

Author: The Swarm
License: MIT
"""

import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import re


class ConflictSeverity(Enum):
    """How serious is the conflict."""
    BLOCKING = "blocking"      # Same file, same function - stop now
    HIGH = "high"              # Same file, different functions
    MEDIUM = "medium"          # Related files (same module)
    LOW = "low"                # Same general area
    INFO = "info"              # Just FYI, probably fine


@dataclass
class WorkIntent:
    """Declaration of what an agent intends to work on."""
    agent_id: str
    description: str
    files: List[str] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: str = "active"  # active, completed, abandoned


@dataclass
class Conflict:
    """A detected conflict between agents."""
    id: str
    agents: List[str]
    severity: ConflictSeverity
    reason: str
    overlapping_files: List[str] = field(default_factory=list)
    overlapping_functions: List[str] = field(default_factory=list)
    overlapping_keywords: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution: Optional[str] = None


class ConflictDetector:
    """
    Detects and prevents duplicate work across agents.
    
    This is core IP: Real-time conflict detection for AI swarms.
    
    Example:
        detector = ConflictDetector()
        
        # Agent-1 declares intent
        detector.declare_intent(
            agent_id="agent-1",
            description="Fixing authentication bug",
            files=["src/auth.py", "src/login.py"],
            keywords=["auth", "login", "token"]
        )
        
        # Agent-2 tries to work on same area
        conflicts = detector.check_conflicts(
            agent_id="agent-2",
            files=["src/auth.py"],
            keywords=["authentication"]
        )
        
        if conflicts:
            print(f"⚠️ Conflict with {conflicts[0].agents}")
            # Agent-2 should pick different work
    """
    
    def __init__(
        self,
        storage_dir: str = "./swarm_conflicts",
        intent_ttl_hours: int = 4
    ):
        """
        Initialize conflict detector.
        
        Args:
            storage_dir: Where to store intent declarations
            intent_ttl_hours: How long intents are valid (default 4 hours)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.intent_ttl = timedelta(hours=intent_ttl_hours)
        self.intents: Dict[str, WorkIntent] = {}
        self.conflicts: Dict[str, Conflict] = {}
        self._load_intents()
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"conflict_{hashlib.sha256(timestamp.encode()).hexdigest()[:8]}"
    
    def _load_intents(self):
        """Load active intents from storage."""
        intents_file = self.storage_dir / "active_intents.json"
        if intents_file.exists():
            try:
                data = json.loads(intents_file.read_text())
                for agent_id, intent_data in data.items():
                    started_at = datetime.fromisoformat(intent_data["started_at"])
                    expires_at = started_at + self.intent_ttl
                    
                    # Skip expired intents
                    if datetime.now() > expires_at:
                        continue
                    
                    self.intents[agent_id] = WorkIntent(
                        agent_id=agent_id,
                        description=intent_data["description"],
                        files=intent_data.get("files", []),
                        modules=intent_data.get("modules", []),
                        functions=intent_data.get("functions", []),
                        keywords=intent_data.get("keywords", []),
                        started_at=started_at,
                        expires_at=expires_at,
                        status=intent_data.get("status", "active")
                    )
            except Exception:
                pass
    
    def _save_intents(self):
        """Save intents to storage."""
        data = {}
        for agent_id, intent in self.intents.items():
            if intent.status == "active":
                data[agent_id] = {
                    "description": intent.description,
                    "files": intent.files,
                    "modules": intent.modules,
                    "functions": intent.functions,
                    "keywords": intent.keywords,
                    "started_at": intent.started_at.isoformat(),
                    "status": intent.status
                }
        
        intents_file = self.storage_dir / "active_intents.json"
        intents_file.write_text(json.dumps(data, indent=2))
    
    def _normalize_path(self, path: str) -> str:
        """Normalize file path for comparison."""
        return path.replace("\\", "/").lower().strip("/")
    
    def _extract_module(self, file_path: str) -> str:
        """Extract module name from file path."""
        normalized = self._normalize_path(file_path)
        # Remove extension
        if normalized.endswith(".py"):
            normalized = normalized[:-3]
        # Get parent directory as module
        parts = normalized.split("/")
        if len(parts) > 1:
            return parts[-2]  # Parent directory
        return parts[0]
    
    def _calculate_similarity(
        self,
        set1: Set[str],
        set2: Set[str]
    ) -> Tuple[float, Set[str]]:
        """Calculate Jaccard similarity and overlap."""
        if not set1 or not set2:
            return 0.0, set()
        
        intersection = set1 & set2
        union = set1 | set2
        
        similarity = len(intersection) / len(union) if union else 0.0
        return similarity, intersection
    
    def declare_intent(
        self,
        agent_id: str,
        description: str,
        files: Optional[List[str]] = None,
        modules: Optional[List[str]] = None,
        functions: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        ttl_hours: Optional[int] = None
    ) -> Tuple[WorkIntent, List[Conflict]]:
        """
        Declare intent to work on something.
        
        Returns the intent AND any conflicts detected.
        
        Args:
            agent_id: Agent declaring intent
            description: What they plan to do
            files: Files they'll touch
            modules: Modules they'll work in
            functions: Functions they'll modify
            keywords: Keywords describing the work
            ttl_hours: Override default TTL
            
        Returns:
            Tuple of (intent, list of conflicts)
        """
        # First check for conflicts
        conflicts = self.check_conflicts(
            agent_id=agent_id,
            files=files,
            modules=modules,
            functions=functions,
            keywords=keywords
        )
        
        # Create intent
        ttl = timedelta(hours=ttl_hours) if ttl_hours else self.intent_ttl
        intent = WorkIntent(
            agent_id=agent_id,
            description=description,
            files=[self._normalize_path(f) for f in (files or [])],
            modules=modules or [],
            functions=functions or [],
            keywords=[k.lower() for k in (keywords or [])],
            expires_at=datetime.now() + ttl
        )
        
        # Extract modules from files if not provided
        if files and not modules:
            intent.modules = list(set(
                self._extract_module(f) for f in files
            ))
        
        self.intents[agent_id] = intent
        self._save_intents()
        
        return intent, conflicts
    
    def check_conflicts(
        self,
        agent_id: str,
        files: Optional[List[str]] = None,
        modules: Optional[List[str]] = None,
        functions: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> List[Conflict]:
        """
        Check if proposed work conflicts with active intents.
        
        Args:
            agent_id: Agent checking for conflicts
            files: Files they want to touch
            modules: Modules they want to work in
            functions: Functions they want to modify
            keywords: Keywords describing their work
            
        Returns:
            List of conflicts (empty if none)
        """
        conflicts = []
        
        # Normalize inputs
        my_files = set(self._normalize_path(f) for f in (files or []))
        my_modules = set(m.lower() for m in (modules or []))
        my_functions = set(f.lower() for f in (functions or []))
        my_keywords = set(k.lower() for k in (keywords or []))
        
        # Extract modules from files
        if my_files and not my_modules:
            my_modules = set(self._extract_module(f) for f in my_files)
        
        # Check against all active intents
        now = datetime.now()
        for other_agent, intent in self.intents.items():
            # Skip self
            if other_agent == agent_id:
                continue
            
            # Skip expired/inactive
            if intent.status != "active":
                continue
            if intent.expires_at and now > intent.expires_at:
                continue
            
            other_files = set(intent.files)
            other_modules = set(m.lower() for m in intent.modules)
            other_functions = set(f.lower() for f in intent.functions)
            other_keywords = set(k.lower() for k in intent.keywords)
            
            # Check file overlap (BLOCKING)
            file_sim, file_overlap = self._calculate_similarity(my_files, other_files)
            if file_overlap:
                # Check function overlap (even more specific)
                func_sim, func_overlap = self._calculate_similarity(
                    my_functions, other_functions
                )
                
                if func_overlap:
                    severity = ConflictSeverity.BLOCKING
                    reason = f"Same file AND function: {func_overlap}"
                else:
                    severity = ConflictSeverity.HIGH
                    reason = f"Same file(s): {file_overlap}"
                
                conflicts.append(Conflict(
                    id=self._generate_id(),
                    agents=[agent_id, other_agent],
                    severity=severity,
                    reason=reason,
                    overlapping_files=list(file_overlap),
                    overlapping_functions=list(func_overlap) if func_overlap else []
                ))
                continue
            
            # Check module overlap (MEDIUM)
            mod_sim, mod_overlap = self._calculate_similarity(my_modules, other_modules)
            if mod_overlap and mod_sim > 0.3:
                conflicts.append(Conflict(
                    id=self._generate_id(),
                    agents=[agent_id, other_agent],
                    severity=ConflictSeverity.MEDIUM,
                    reason=f"Same module(s): {mod_overlap}",
                    overlapping_files=[]
                ))
                continue
            
            # Check keyword overlap (LOW/INFO)
            kw_sim, kw_overlap = self._calculate_similarity(my_keywords, other_keywords)
            if kw_overlap and kw_sim > 0.5:
                conflicts.append(Conflict(
                    id=self._generate_id(),
                    agents=[agent_id, other_agent],
                    severity=ConflictSeverity.LOW if kw_sim > 0.7 else ConflictSeverity.INFO,
                    reason=f"Similar keywords: {kw_overlap}",
                    overlapping_keywords=list(kw_overlap)
                ))
        
        # Save conflicts
        for conflict in conflicts:
            self.conflicts[conflict.id] = conflict
        
        return conflicts
    
    def complete_work(self, agent_id: str) -> bool:
        """Mark an agent's work as complete, freeing up the area."""
        if agent_id in self.intents:
            self.intents[agent_id].status = "completed"
            self._save_intents()
            return True
        return False
    
    def abandon_work(self, agent_id: str) -> bool:
        """Mark work as abandoned (agent got stuck, reassigned, etc.)."""
        if agent_id in self.intents:
            self.intents[agent_id].status = "abandoned"
            self._save_intents()
            return True
        return False
    
    def get_active_intents(self) -> List[WorkIntent]:
        """Get all currently active work intents."""
        now = datetime.now()
        return [
            intent for intent in self.intents.values()
            if intent.status == "active" and
            (not intent.expires_at or now < intent.expires_at)
        ]
    
    def get_agent_intent(self, agent_id: str) -> Optional[WorkIntent]:
        """Get a specific agent's current intent."""
        intent = self.intents.get(agent_id)
        if intent and intent.status == "active":
            return intent
        return None
    
    def get_blocked_files(self) -> Dict[str, str]:
        """Get all files currently being worked on and by whom."""
        blocked = {}
        for intent in self.get_active_intents():
            for file in intent.files:
                blocked[file] = intent.agent_id
        return blocked
