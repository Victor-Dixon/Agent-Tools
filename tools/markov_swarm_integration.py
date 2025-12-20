"""
Markov Task Optimizer - Swarm Integration Adapter
==================================================

Connects the Markov Task Optimizer to the swarm systems:
- CaptainSwarmCoordinator (task assignment)
- Agent status tracking (current state)
- Contract system (task discovery)
- AutonomousTaskEngine (task recommendations)

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-05
Priority: HIGH - Swarm Integration
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

from markov_task_optimizer import (
    MarkovTaskOptimizer,
    OptimizationTask,
    ProjectState,
)
from captain_swarm_coordinator import CaptainSwarmCoordinator

# Optional import - autonomous task engine may not be available
try:
    from autonomous_task_engine import AutonomousTaskEngine
    HAS_AUTONOMOUS_ENGINE = True
except ImportError:
    HAS_AUTONOMOUS_ENGINE = False
    AutonomousTaskEngine = None


class MarkovSwarmIntegration:
    """
    Integration adapter connecting Markov optimizer to swarm systems.
    
    Enables:
    - Reading real agent status from status.json files
    - Converting discovered tasks to OptimizationTask format
    - Using Markov optimizer to select optimal tasks
    - Assigning tasks via CaptainSwarmCoordinator
    - Tracking task dependencies and blockers
    """

    def __init__(self, repo_path: str = "."):
        """Initialize swarm integration."""
        self.repo_path = Path(repo_path)
        self.coordinator = CaptainSwarmCoordinator()
        self.task_engine = (
            AutonomousTaskEngine(str(self.repo_path))
            if HAS_AUTONOMOUS_ENGINE
            else None
        )
        self.optimizer: Optional[MarkovTaskOptimizer] = None
        self.agent_workspaces = self.repo_path / "agent_workspaces"

    def load_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Load current status of all agents from status.json files."""
        statuses = {}
        
        for agent_id in self.coordinator.AGENT_SPECIALIZATIONS.keys():
            status_file = self.agent_workspaces / agent_id / "status.json"
            
            if status_file.exists():
                try:
                    with open(status_file, "r", encoding="utf-8") as f:
                        status = json.load(f)
                    statuses[agent_id] = status
                except Exception as e:
                    print(f"⚠️ Error reading {agent_id} status: {e}")
                    statuses[agent_id] = {"status": "error", "error": str(e)}
            else:
                statuses[agent_id] = {"status": "missing"}
        
        return statuses

    def get_available_agents(self, statuses: Dict[str, Dict[str, Any]]) -> Set[str]:
        """Extract available agents from status data."""
        available = set()
        
        for agent_id, status in statuses.items():
            # Agent is available if:
            # 1. Status is ACTIVE
            # 2. No critical blockers
            # 3. Not in error state
            agent_status = status.get("status", "").upper()
            if agent_status == "ACTIVE":
                # Check for blockers in current_tasks
                current_tasks = status.get("current_tasks", [])
                has_critical_blocker = any(
                    "🚨" in task or "BLOCKER" in task.upper()
                    for task in current_tasks
                )
                
                if not has_critical_blocker:
                    available.add(agent_id)
        
        return available

    def get_active_agents(self, statuses: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Extract currently active agents and their tasks."""
        active = {}
        
        for agent_id, status in statuses.items():
            current_tasks = status.get("current_tasks", [])
            # Find active (non-completed) tasks
            for task in current_tasks:
                if not task.startswith("✅") and not task.startswith("⏳"):
                    # Extract task ID or description
                    active[agent_id] = task
                    break
        
        return active

    def get_completed_tasks(self, statuses: Dict[str, Dict[str, Any]]) -> Set[str]:
        """Extract completed task IDs from all agent statuses."""
        completed = set()
        
        for agent_id, status in statuses.items():
            completed_tasks = status.get("completed_tasks", [])
            for task in completed_tasks:
                # Extract task ID if possible
                if isinstance(task, str):
                    # Try to extract task ID from task description
                    # Format: "✅ Task Name (ID: task-123)"
                    if "ID:" in task:
                        task_id = task.split("ID:")[-1].strip().rstrip(")")
                        completed.add(task_id)
                    else:
                        # Use task description as ID
                        completed.add(task[:50])  # Truncate for uniqueness
        
        return completed

    def get_blocked_tasks(self, statuses: Dict[str, Dict[str, Any]]) -> Set[str]:
        """Extract blocked task IDs from agent statuses."""
        blocked = set()
        
        for agent_id, status in statuses.items():
            current_tasks = status.get("current_tasks", [])
            for task in current_tasks:
                # Check for blocker indicators
                if "🚨" in task or "BLOCKER" in task.upper() or "BLOCKED" in task.upper():
                    # Extract task ID
                    blocked.add(task[:50])
        
        return blocked

    def discover_tasks_from_engine(self) -> List[OptimizationTask]:
        """Discover tasks using AutonomousTaskEngine and convert to OptimizationTask."""
        if not self.task_engine:
            # Fallback: return empty list if engine not available
            return []
        
        # Discover tasks
        opportunities = self.task_engine.discover_tasks()
        
        # Convert to OptimizationTask format
        optimization_tasks = []
        
        for opp in opportunities:
            # Map task type to specialty
            specialty = self._map_task_to_specialty(opp)
            
            # Calculate complexity from task data
            complexity = self._calculate_complexity(opp)
            
            # Extract dependencies/unblocks
            unblocks = opp.dependencies or []
            
            # Extract required files
            requires_files = {opp.file_path} if opp.file_path else set()
            
            # Create OptimizationTask
            opt_task = OptimizationTask(
                id=opp.task_id,
                name=opp.title,
                points=opp.points or 100,  # Default points
                specialty_required=specialty,
                complexity=complexity,
                unblocks=unblocks,
                requires_files=requires_files,
                v2_violations_fixed=1 if opp.severity == "MAJOR" else 0,
                files_consolidated=len(requires_files),
            )
            
            optimization_tasks.append(opt_task)
        
        return optimization_tasks

    def _map_task_to_specialty(self, opportunity) -> str:
        """Map task opportunity to agent specialty."""
        title_lower = opportunity.title.lower()
        file_path = (opportunity.file_path or "").lower()
        
        # Map based on file path and title
        if "src/services" in file_path or "src/core" in file_path:
            return "Agent-1"
        elif "architecture" in title_lower or "design" in title_lower:
            return "Agent-2"
        elif "test" in file_path or "infrastructure" in file_path:
            return "Agent-3"
        elif "analytics" in title_lower or "metrics" in title_lower:
            return "Agent-5"
        elif "coordination" in title_lower or "communication" in title_lower:
            return "Agent-6"
        elif "web" in file_path or "frontend" in title_lower:
            return "Agent-7"
        elif "test" in title_lower or "qa" in title_lower:
            return "Agent-8"
        else:
            return "Agent-1"  # Default

    def _calculate_complexity(self, opportunity) -> int:
        """Calculate task complexity (1-100 scale)."""
        base_complexity = 30
        
        # Adjust based on severity
        if opportunity.severity == "CRITICAL":
            base_complexity += 30
        elif opportunity.severity == "MAJOR":
            base_complexity += 20
        elif opportunity.severity == "MINOR":
            base_complexity -= 10
        
        # Adjust based on affected files
        file_count = len(opportunity.affected_files or [])
        if file_count > 10:
            base_complexity += 20
        elif file_count > 5:
            base_complexity += 10
        
        return min(max(base_complexity, 1), 100)

    def build_project_state(self) -> ProjectState:
        """Build current project state from agent statuses."""
        statuses = self.load_agent_statuses()
        
        return ProjectState(
            completed_tasks=self.get_completed_tasks(statuses),
            active_agents=self.get_active_agents(statuses),
            available_agents=self.get_available_agents(statuses),
            blocked_tasks=self.get_blocked_tasks(statuses),
            available_tasks=set(),  # Will be populated from discovered tasks
            v2_compliance=self._calculate_v2_compliance(statuses),
            points_earned=self._calculate_total_points(statuses),
            locked_files=set(),  # Could be enhanced with file lock tracking
        )

    def _calculate_v2_compliance(self, statuses: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall V2 compliance from agent statuses."""
        # Simplified: assume 0.85 base, adjust based on violations
        base_compliance = 0.85
        
        # Check for V2 violations in status messages
        violation_count = 0
        for status in statuses.values():
            current_tasks = status.get("current_tasks", [])
            for task in current_tasks:
                if "V2" in task.upper() and "VIOLATION" in task.upper():
                    violation_count += 1
        
        # Reduce compliance based on violations
        compliance = base_compliance - (violation_count * 0.01)
        return max(0.0, min(1.0, compliance))

    def _calculate_total_points(self, statuses: Dict[str, Dict[str, Any]]) -> int:
        """Calculate total points earned across all agents."""
        total = 0
        
        for status in statuses.values():
            # Try to extract points from achievements or status
            achievements = status.get("achievements", [])
            # Simplified: assume points based on completed tasks
            completed = status.get("completed_tasks", [])
            total += len(completed) * 50  # Rough estimate
        
        return total

    def get_agent_specialties(self) -> Dict[str, str]:
        """Get agent specialty mapping."""
        specialties = {}
        for agent_id, info in self.coordinator.AGENT_SPECIALIZATIONS.items():
            specialties[agent_id] = info["name"]
        return specialties

    def initialize_optimizer(self) -> MarkovTaskOptimizer:
        """Initialize Markov optimizer with discovered tasks."""
        # Discover tasks
        tasks = self.discover_tasks_from_engine()
        
        # Get agent specialties
        agents = self.get_agent_specialties()
        
        # Create optimizer
        self.optimizer = MarkovTaskOptimizer(tasks, agents)
        
        return self.optimizer

    def get_optimal_next_task(
        self, agent_id: Optional[str] = None
    ) -> Optional[OptimizationTask]:
        """
        Get optimal next task using Markov optimizer.
        
        Args:
            agent_id: Optional agent ID to filter tasks for specific agent
        
        Returns:
            Optimal task or None
        """
        if not self.optimizer:
            self.initialize_optimizer()
        
        # Build current state
        state = self.build_project_state()
        
        # Filter available tasks
        discovered_tasks = self.discover_tasks_from_engine()
        if agent_id:
            # Filter for agent's specialty
            specialty = self.get_agent_specialties().get(agent_id, "")
            available_task_ids = {
                task.id
                for task in discovered_tasks
                if task.specialty_required == agent_id
            }
        else:
            available_task_ids = {task.id for task in discovered_tasks}
        
        state.available_tasks = available_task_ids
        
        # Get optimal task
        best_task, scores = self.optimizer.select_next_task(state, return_scores=True)
        
        return best_task

    def assign_optimal_task_to_agent(
        self, agent_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get optimal task for agent and assign via CaptainSwarmCoordinator.
        
        Returns:
            Assignment result or None
        """
        # Get optimal task
        task = self.get_optimal_next_task(agent_id)
        
        if not task:
            print(f"❌ No optimal task found for {agent_id}")
            return None
        
        # Get explanation
        state = self.build_project_state()
        explanation = self.optimizer.explain_recommendation(task, state)
        
        # Assign via coordinator
        assignment = self.coordinator.assign_task_to_agent(
            agent_id=agent_id,
            task=f"{task.name} (Markov-Optimized)",
            priority="HIGH",
            description=f"""
**Markov-Optimized Task Assignment**

{explanation}

**Task Details:**
- Points: {task.points}
- Complexity: {task.complexity}/100
- V2 Impact: {task.v2_violations_fixed} violations fixed
- Files: {len(task.requires_files)} files affected
- Unblocks: {len(task.unblocks)} tasks

**Optimization Score:** {task.points / max(task.complexity, 1):.2f} ROI
            """.strip(),
        )
        
        return assignment

    def assign_optimal_tasks_to_swarm(self) -> List[Dict[str, Any]]:
        """Assign optimal tasks to all available agents."""
        statuses = self.load_agent_statuses()
        available_agents = self.get_available_agents(statuses)
        
        assignments = []
        
        for agent_id in available_agents:
            assignment = self.assign_optimal_task_to_agent(agent_id)
            if assignment:
                assignments.append(assignment)
        
        return assignments


def main():
    """CLI entry point for Markov swarm integration."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Markov Task Optimizer - Swarm Integration"
    )
    parser.add_argument(
        "--agent",
        help="Get optimal task for specific agent (e.g., Agent-1)",
    )
    parser.add_argument(
        "--assign",
        action="store_true",
        help="Assign optimal task to agent (requires --agent)",
    )
    parser.add_argument(
        "--assign-all",
        action="store_true",
        help="Assign optimal tasks to all available agents",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Show explanation for optimal task",
    )
    
    args = parser.parse_args()
    
    integration = MarkovSwarmIntegration()
    
    if args.assign_all:
        print("🚀 Assigning optimal tasks to all available agents...")
        assignments = integration.assign_optimal_tasks_to_swarm()
        print(f"✅ Assigned {len(assignments)} tasks")
        for assignment in assignments:
            print(f"  - {assignment['agent']}: {assignment['task']}")
    
    elif args.agent:
        if args.assign:
            print(f"🎯 Assigning optimal task to {args.agent}...")
            assignment = integration.assign_optimal_task_to_agent(args.agent)
            if assignment:
                print(f"✅ Task assigned: {assignment['task']}")
            else:
                print("❌ No task assigned")
        else:
            print(f"🔍 Finding optimal task for {args.agent}...")
            task = integration.get_optimal_next_task(args.agent)
            if task:
                print(f"\n✅ Optimal Task: {task.name}")
                print(f"   Points: {task.points}")
                print(f"   Complexity: {task.complexity}/100")
                print(f"   ROI: {task.points / max(task.complexity, 1):.2f}")
                
                if args.explain:
                    state = integration.build_project_state()
                    explanation = integration.optimizer.explain_recommendation(
                        task, state
                    )
                    print(f"\n{explanation}")
            else:
                print("❌ No optimal task found")
    
    else:
        print("🔍 Finding optimal next task for swarm...")
        task = integration.get_optimal_next_task()
        if task:
            print(f"\n✅ Optimal Task: {task.name}")
            print(f"   Points: {task.points}")
            print(f"   Complexity: {task.complexity}/100")
            print(f"   Specialty: {task.specialty_required}")
        else:
            print("❌ No optimal task found")


if __name__ == "__main__":
    main()

