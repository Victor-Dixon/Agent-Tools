"""
Swarm Coordinator - Central orchestration for multi-agent systems.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AgentStatus:
    """Status of an agent in the swarm."""
    agent_id: str
    status: str = "idle"  # idle, working, stuck, offline
    current_task: Optional[str] = None
    last_seen: datetime = field(default_factory=datetime.now)
    points: int = 0
    specialties: List[str] = field(default_factory=list)


@dataclass 
class TaskOpportunity:
    """A work opportunity discovered in the codebase."""
    task_id: str
    task_type: str
    description: str
    file_path: Optional[str] = None
    priority: int = 3  # 1=critical, 5=low
    estimated_points: int = 100
    required_skills: List[str] = field(default_factory=list)


class SwarmCoordinator:
    """
    Central coordinator for multi-agent swarm operations.
    
    Example:
        swarm = SwarmCoordinator(
            agents=["agent-1", "agent-2", "agent-3"],
            workspace="./agent_workspaces"
        )
        
        # Check agent status
        status = swarm.get_all_status()
        
        # Find idle agents
        idle = swarm.get_idle_agents()
        
        # Assign work
        swarm.assign_task(agent="agent-1", task="Fix bug in auth.py")
        
        # Broadcast to all
        swarm.broadcast("Sync meeting in 5 minutes")
    """
    
    def __init__(
        self,
        agents: List[str],
        workspace: str = "./agent_workspaces",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize swarm coordinator.
        
        Args:
            agents: List of agent IDs (e.g., ["agent-1", "agent-2"])
            workspace: Path to agent workspaces directory
            config: Optional configuration overrides
        """
        self.agents = agents
        self.workspace = Path(workspace)
        self.config = config or {}
        self._agent_status: Dict[str, AgentStatus] = {}
        self._task_queue: List[TaskOpportunity] = []
        
        # Initialize agent status
        for agent_id in agents:
            self._agent_status[agent_id] = AgentStatus(agent_id=agent_id)
    
    def get_status(self, agent_id: str) -> AgentStatus:
        """Get status of a specific agent."""
        if agent_id not in self._agent_status:
            raise ValueError(f"Unknown agent: {agent_id}")
        
        # Try to load from workspace
        status_file = self.workspace / agent_id / "status.json"
        if status_file.exists():
            try:
                data = json.loads(status_file.read_text())
                status = self._agent_status[agent_id]
                status.status = data.get("status", "idle")
                status.current_task = data.get("current_task")
                status.points = data.get("points", 0)
            except Exception:
                pass
        
        return self._agent_status[agent_id]
    
    def get_all_status(self) -> Dict[str, AgentStatus]:
        """Get status of all agents."""
        return {agent_id: self.get_status(agent_id) for agent_id in self.agents}
    
    def get_idle_agents(self) -> List[str]:
        """Get list of idle agents ready for work."""
        idle = []
        for agent_id in self.agents:
            status = self.get_status(agent_id)
            if status.status == "idle":
                idle.append(agent_id)
        return idle
    
    def assign_task(self, agent_id: str, task: str, priority: int = 3) -> bool:
        """
        Assign a task to an agent.
        
        Args:
            agent_id: Target agent
            task: Task description
            priority: 1=critical, 5=low
            
        Returns:
            True if assignment succeeded
        """
        if agent_id not in self.agents:
            raise ValueError(f"Unknown agent: {agent_id}")
        
        # Create inbox message
        inbox_dir = self.workspace / agent_id / "inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_file = inbox_dir / f"task_{timestamp}.json"
        
        task_data = {
            "task": task,
            "priority": priority,
            "assigned_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        task_file.write_text(json.dumps(task_data, indent=2))
        
        # Update agent status
        status = self._agent_status[agent_id]
        status.current_task = task
        status.status = "assigned"
        
        return True
    
    def broadcast(self, message: str, priority: int = 3) -> Dict[str, bool]:
        """
        Broadcast message to all agents.
        
        Args:
            message: Message content
            priority: 1=urgent, 5=low
            
        Returns:
            Dict of agent_id -> success
        """
        results = {}
        for agent_id in self.agents:
            try:
                self.assign_task(agent_id, message, priority)
                results[agent_id] = True
            except Exception:
                results[agent_id] = False
        return results
    
    def discover_tasks(self, scan_path: str = ".") -> List[TaskOpportunity]:
        """
        Scan codebase for work opportunities.
        
        Args:
            scan_path: Path to scan
            
        Returns:
            List of discovered task opportunities
        """
        tasks = []
        scan_dir = Path(scan_path)
        
        # Scan for TODOs
        for py_file in scan_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split("\n"), 1):
                    if "TODO" in line or "FIXME" in line:
                        tasks.append(TaskOpportunity(
                            task_id=f"todo_{py_file.stem}_{i}",
                            task_type="todo",
                            description=line.strip(),
                            file_path=str(py_file),
                            priority=3,
                            estimated_points=50
                        ))
            except Exception:
                pass
        
        self._task_queue = tasks
        return tasks
    
    def get_optimal_assignment(self, agent_id: str) -> Optional[TaskOpportunity]:
        """
        Get optimal task for an agent based on skills and availability.
        
        Args:
            agent_id: Agent to find task for
            
        Returns:
            Best matching task or None
        """
        if not self._task_queue:
            self.discover_tasks()
        
        available = [t for t in self._task_queue if t.priority <= 3]
        if available:
            # Sort by priority (lower = more urgent)
            available.sort(key=lambda t: t.priority)
            return available[0]
        
        return None
