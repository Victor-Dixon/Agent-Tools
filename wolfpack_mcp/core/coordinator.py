"""
Pack Coordinator - Central orchestration for wolf pack AI systems.

🐺 The Alpha coordinates the pack. Every wolf knows their role.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class WolfStatus:
    """Status of a wolf in the pack."""
    wolf_id: str
    role: str = "scout"  # alpha, beta, scout, omega
    status: str = "ready"  # ready, hunting, resting, stuck
    current_hunt: Optional[str] = None
    last_howl: datetime = field(default_factory=datetime.now)
    kills: int = 0  # completed tasks
    territory: List[str] = field(default_factory=list)  # specialties


@dataclass 
class Prey:
    """A work target identified by the pack."""
    prey_id: str
    prey_type: str
    description: str
    location: Optional[str] = None
    difficulty: int = 3  # 1=easy prey, 5=dangerous
    reward: int = 100
    required_skills: List[str] = field(default_factory=list)


class PackCoordinator:
    """
    🐺 Central coordinator for the wolf pack.
    
    The Alpha doesn't micromanage - they coordinate, communicate, and 
    ensure every wolf is hunting effectively.
    
    Example:
        pack = PackCoordinator(
            wolves=["alpha", "beta", "scout-1", "scout-2"],
            den="./wolf_den"
        )
        
        # Check pack status
        pack.roll_call()
        
        # Find ready wolves
        ready = pack.get_ready_wolves()
        
        # Assign hunt
        pack.assign_hunt(wolf="scout-1", prey="Fix bug in auth.py")
        
        # Howl to all
        pack.broadcast("Pack meeting at sunset")
    """
    
    def __init__(
        self,
        wolves: List[str],
        den: str = "./wolf_den",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the pack.
        
        Args:
            wolves: List of wolf IDs
            den: Path to pack den (workspace)
            config: Optional configuration
        """
        self.wolves = wolves
        self.den = Path(den)
        self.config = config or {}
        self._pack_status: Dict[str, WolfStatus] = {}
        self._prey_queue: List[Prey] = []
        
        # Initialize pack
        for wolf_id in wolves:
            role = "alpha" if wolf_id == wolves[0] else "scout"
            self._pack_status[wolf_id] = WolfStatus(wolf_id=wolf_id, role=role)
    
    def get_status(self, wolf_id: str) -> WolfStatus:
        """Get status of a specific wolf."""
        if wolf_id not in self._pack_status:
            raise ValueError(f"Unknown wolf: {wolf_id}")
        
        # Try to load from den
        status_file = self.den / wolf_id / "status.json"
        if status_file.exists():
            try:
                data = json.loads(status_file.read_text())
                status = self._pack_status[wolf_id]
                status.status = data.get("status", "ready")
                status.current_hunt = data.get("current_hunt")
                status.kills = data.get("kills", 0)
            except Exception:
                pass
        
        return self._pack_status[wolf_id]
    
    def roll_call(self) -> Dict[str, WolfStatus]:
        """Roll call - get status of entire pack."""
        return {wolf_id: self.get_status(wolf_id) for wolf_id in self.wolves}
    
    def get_ready_wolves(self) -> List[str]:
        """Get wolves ready for the hunt."""
        ready = []
        for wolf_id in self.wolves:
            status = self.get_status(wolf_id)
            if status.status == "ready":
                ready.append(wolf_id)
        return ready
    
    def assign_hunt(self, wolf_id: str, prey: str, difficulty: int = 3) -> bool:
        """
        Assign a hunt to a wolf.
        
        Args:
            wolf_id: Target wolf
            prey: Hunt description
            difficulty: 1=easy, 5=dangerous
            
        Returns:
            True if assignment succeeded
        """
        if wolf_id not in self.wolves:
            raise ValueError(f"Unknown wolf: {wolf_id}")
        
        # Create hunt order in wolf's territory
        territory = self.den / wolf_id / "hunts"
        territory.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hunt_file = territory / f"hunt_{timestamp}.json"
        
        hunt_data = {
            "prey": prey,
            "difficulty": difficulty,
            "assigned_at": datetime.now().isoformat(),
            "status": "assigned"
        }
        
        hunt_file.write_text(json.dumps(hunt_data, indent=2))
        
        # Update wolf status
        status = self._pack_status[wolf_id]
        status.current_hunt = prey
        status.status = "hunting"
        
        return True
    
    def broadcast(self, howl: str, urgency: int = 3) -> Dict[str, bool]:
        """
        🐺 Howl to the entire pack.
        
        Args:
            howl: Message content
            urgency: 1=emergency, 5=casual
            
        Returns:
            Dict of wolf_id -> success
        """
        results = {}
        for wolf_id in self.wolves:
            try:
                self.assign_hunt(wolf_id, howl, urgency)
                results[wolf_id] = True
            except Exception:
                results[wolf_id] = False
        return results
    
    def scout_territory(self, path: str = ".") -> List[Prey]:
        """
        Scout territory for prey (scan codebase for work).
        
        Args:
            path: Territory to scout
            
        Returns:
            List of discovered prey
        """
        prey_list = []
        territory = Path(path)
        
        # Hunt for TODOs and FIXMEs
        for py_file in territory.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split("\n"), 1):
                    if "TODO" in line or "FIXME" in line:
                        prey_list.append(Prey(
                            prey_id=f"prey_{py_file.stem}_{i}",
                            prey_type="todo",
                            description=line.strip(),
                            location=str(py_file),
                            difficulty=3,
                            reward=50
                        ))
            except Exception:
                pass
        
        self._prey_queue = prey_list
        return prey_list
    
    def get_best_prey(self, wolf_id: str) -> Optional[Prey]:
        """
        Get best prey for a wolf based on their skills.
        
        Args:
            wolf_id: Wolf to find prey for
            
        Returns:
            Best matching prey or None
        """
        if not self._prey_queue:
            self.scout_territory()
        
        available = [p for p in self._prey_queue if p.difficulty <= 3]
        if available:
            available.sort(key=lambda p: p.difficulty)
            return available[0]
        
        return None
