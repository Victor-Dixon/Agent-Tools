"""
Agent DNA - Learn Agent Strengths Over Time
============================================

🐺 WE ARE SWARM - Every wolf has unique strengths.

This is IP-level code: Builds a profile of each agent's capabilities
by analyzing their work history. Enables intelligent task matching.

What It Tracks:
- Task completion rates by category
- Average time to complete by task type
- Quality scores (based on reviews, reverts, etc.)
- Preferred file types and modules
- Peak productivity times
- Collaboration patterns

Why It Matters:
- Auto-assign auth bugs to agent who's best at auth
- Route frontend work to CSS specialists
- Know who to pair for complex tasks
- Predict completion times accurately

Author: The Swarm
License: MIT
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
import statistics


@dataclass
class TaskRecord:
    """Record of a completed task."""
    task_id: str
    agent_id: str
    category: str
    description: str
    files_touched: List[str]
    started_at: datetime
    completed_at: datetime
    success: bool
    quality_score: float = 1.0  # 0-1
    reverted: bool = False
    review_score: Optional[float] = None
    collaborators: List[str] = field(default_factory=list)


@dataclass
class AgentProfile:
    """An agent's learned capability profile."""
    agent_id: str
    total_tasks: int = 0
    success_rate: float = 0.0
    category_scores: Dict[str, float] = field(default_factory=dict)
    category_counts: Dict[str, int] = field(default_factory=dict)
    avg_completion_times: Dict[str, float] = field(default_factory=dict)
    file_expertise: Dict[str, float] = field(default_factory=dict)
    module_expertise: Dict[str, float] = field(default_factory=dict)
    collaboration_affinity: Dict[str, float] = field(default_factory=dict)
    peak_hours: List[int] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class AgentDNA:
    """
    Learns and tracks agent capabilities over time.
    
    This is core IP: ML-free capability learning through work analysis.
    
    Example:
        dna = AgentDNA()
        
        # Record completed tasks
        dna.record_task(
            agent_id="agent-1",
            category="debugging",
            description="Fixed auth token expiry bug",
            files=["src/auth.py", "src/tokens.py"],
            duration_minutes=45,
            success=True,
            quality_score=0.9
        )
        
        # Get agent strengths
        profile = dna.get_profile("agent-1")
        print(profile.strengths)  # ["debugging", "auth", "python"]
        
        # Find best agent for a task
        best = dna.find_best_agent(
            category="debugging",
            files=["src/auth.py"]
        )
        print(best)  # "agent-1" (because they've done auth work before)
    """
    
    def __init__(self, storage_dir: str = "./swarm_dna"):
        """Initialize Agent DNA tracker."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir = self.storage_dir / "tasks"
        self.profiles_dir = self.storage_dir / "profiles"
        self.tasks_dir.mkdir(exist_ok=True)
        self.profiles_dir.mkdir(exist_ok=True)
        
        self.profiles: Dict[str, AgentProfile] = {}
        self.task_history: List[TaskRecord] = []
        self._load_data()
    
    def _load_data(self):
        """Load profiles and task history."""
        # Load profiles
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                data = json.loads(profile_file.read_text())
                self.profiles[data["agent_id"]] = AgentProfile(
                    agent_id=data["agent_id"],
                    total_tasks=data.get("total_tasks", 0),
                    success_rate=data.get("success_rate", 0.0),
                    category_scores=data.get("category_scores", {}),
                    category_counts=data.get("category_counts", {}),
                    avg_completion_times=data.get("avg_completion_times", {}),
                    file_expertise=data.get("file_expertise", {}),
                    module_expertise=data.get("module_expertise", {}),
                    collaboration_affinity=data.get("collaboration_affinity", {}),
                    peak_hours=data.get("peak_hours", []),
                    strengths=data.get("strengths", []),
                    weaknesses=data.get("weaknesses", [])
                )
            except Exception:
                pass
    
    def _save_profile(self, profile: AgentProfile):
        """Save a profile to disk."""
        data = {
            "agent_id": profile.agent_id,
            "total_tasks": profile.total_tasks,
            "success_rate": profile.success_rate,
            "category_scores": profile.category_scores,
            "category_counts": profile.category_counts,
            "avg_completion_times": profile.avg_completion_times,
            "file_expertise": profile.file_expertise,
            "module_expertise": profile.module_expertise,
            "collaboration_affinity": profile.collaboration_affinity,
            "peak_hours": profile.peak_hours,
            "strengths": profile.strengths,
            "weaknesses": profile.weaknesses,
            "last_updated": datetime.now().isoformat()
        }
        
        profile_file = self.profiles_dir / f"{profile.agent_id}.json"
        profile_file.write_text(json.dumps(data, indent=2))
    
    def _extract_module(self, file_path: str) -> str:
        """Extract module from file path."""
        path = file_path.replace("\\", "/").lower()
        parts = path.split("/")
        # Get the most meaningful part (not src, not __init__)
        for part in reversed(parts):
            if part and part not in ("src", "__init__.py", "tests", "test"):
                if part.endswith(".py"):
                    return part[:-3]
                return part
        return "unknown"
    
    def record_task(
        self,
        agent_id: str,
        category: str,
        description: str,
        files: List[str],
        duration_minutes: float,
        success: bool,
        quality_score: float = 1.0,
        reverted: bool = False,
        review_score: Optional[float] = None,
        collaborators: Optional[List[str]] = None
    ) -> TaskRecord:
        """
        Record a completed task for learning.
        
        Args:
            agent_id: Who did the work
            category: Task category (debugging, feature, refactor, etc.)
            description: What was done
            files: Files touched
            duration_minutes: How long it took
            success: Did it work?
            quality_score: 0-1 quality rating
            reverted: Was it rolled back?
            review_score: Code review score if applicable
            collaborators: Other agents who helped
            
        Returns:
            The recorded task
        """
        now = datetime.now()
        started_at = now - timedelta(minutes=duration_minutes)
        
        record = TaskRecord(
            task_id=f"task_{now.strftime('%Y%m%d%H%M%S')}_{agent_id}",
            agent_id=agent_id,
            category=category.lower(),
            description=description,
            files_touched=files,
            started_at=started_at,
            completed_at=now,
            success=success,
            quality_score=quality_score,
            reverted=reverted,
            review_score=review_score,
            collaborators=collaborators or []
        )
        
        self.task_history.append(record)
        
        # Save task
        task_file = self.tasks_dir / f"{record.task_id}.json"
        task_file.write_text(json.dumps({
            "task_id": record.task_id,
            "agent_id": record.agent_id,
            "category": record.category,
            "description": record.description,
            "files_touched": record.files_touched,
            "started_at": record.started_at.isoformat(),
            "completed_at": record.completed_at.isoformat(),
            "success": record.success,
            "quality_score": record.quality_score,
            "reverted": record.reverted,
            "review_score": record.review_score,
            "collaborators": record.collaborators
        }, indent=2))
        
        # Update profile
        self._update_profile(record)
        
        return record
    
    def _update_profile(self, record: TaskRecord):
        """Update agent profile based on new task record."""
        agent_id = record.agent_id
        
        # Get or create profile
        if agent_id not in self.profiles:
            self.profiles[agent_id] = AgentProfile(agent_id=agent_id)
        
        profile = self.profiles[agent_id]
        
        # Update basic stats
        profile.total_tasks += 1
        
        # Update success rate (rolling average)
        old_successes = profile.success_rate * (profile.total_tasks - 1)
        new_successes = old_successes + (1 if record.success else 0)
        profile.success_rate = new_successes / profile.total_tasks
        
        # Update category scores
        category = record.category
        if category not in profile.category_counts:
            profile.category_counts[category] = 0
            profile.category_scores[category] = 0.0
        
        profile.category_counts[category] += 1
        
        # Category score is weighted by success and quality
        task_score = record.quality_score if record.success else 0.3
        if record.reverted:
            task_score *= 0.5
        
        old_score = profile.category_scores[category]
        count = profile.category_counts[category]
        profile.category_scores[category] = (
            (old_score * (count - 1) + task_score) / count
        )
        
        # Update completion times
        duration = (record.completed_at - record.started_at).total_seconds() / 60
        if category not in profile.avg_completion_times:
            profile.avg_completion_times[category] = duration
        else:
            old_time = profile.avg_completion_times[category]
            profile.avg_completion_times[category] = (old_time + duration) / 2
        
        # Update file expertise
        for file in record.files_touched:
            normalized = file.replace("\\", "/").lower()
            if normalized not in profile.file_expertise:
                profile.file_expertise[normalized] = 0.0
            profile.file_expertise[normalized] += task_score
        
        # Update module expertise
        for file in record.files_touched:
            module = self._extract_module(file)
            if module not in profile.module_expertise:
                profile.module_expertise[module] = 0.0
            profile.module_expertise[module] += task_score
        
        # Update collaboration affinity
        for collaborator in record.collaborators:
            if collaborator not in profile.collaboration_affinity:
                profile.collaboration_affinity[collaborator] = 0.0
            profile.collaboration_affinity[collaborator] += 1
        
        # Update peak hours
        hour = record.completed_at.hour
        profile.peak_hours.append(hour)
        # Keep last 50 hours
        profile.peak_hours = profile.peak_hours[-50:]
        
        # Recalculate strengths and weaknesses
        self._calculate_strengths(profile)
        
        profile.last_updated = datetime.now()
        self._save_profile(profile)
    
    def _calculate_strengths(self, profile: AgentProfile):
        """Calculate agent's strengths and weaknesses."""
        # Sort categories by score
        if not profile.category_scores:
            return
        
        sorted_categories = sorted(
            profile.category_scores.items(),
            key=lambda x: (x[1], profile.category_counts.get(x[0], 0)),
            reverse=True
        )
        
        # Top 3 are strengths (if score > 0.6)
        profile.strengths = [
            cat for cat, score in sorted_categories[:3]
            if score > 0.6 and profile.category_counts.get(cat, 0) >= 2
        ]
        
        # Bottom with score < 0.5 and count > 1 are weaknesses
        profile.weaknesses = [
            cat for cat, score in sorted_categories
            if score < 0.5 and profile.category_counts.get(cat, 0) >= 2
        ][:3]
        
        # Add module expertise to strengths
        if profile.module_expertise:
            top_modules = sorted(
                profile.module_expertise.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            for module, score in top_modules:
                if score > 2 and module not in profile.strengths:
                    profile.strengths.append(module)
    
    def get_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get an agent's capability profile."""
        return self.profiles.get(agent_id)
    
    def find_best_agent(
        self,
        category: Optional[str] = None,
        files: Optional[List[str]] = None,
        modules: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None
    ) -> Optional[Tuple[str, float]]:
        """
        Find the best agent for a task.
        
        Args:
            category: Task category
            files: Files that will be touched
            modules: Modules involved
            exclude: Agents to exclude
            
        Returns:
            Tuple of (agent_id, confidence_score) or None
        """
        exclude = set(exclude or [])
        candidates = []
        
        for agent_id, profile in self.profiles.items():
            if agent_id in exclude:
                continue
            
            score = 0.0
            factors = 0
            
            # Category match
            if category and category.lower() in profile.category_scores:
                cat_score = profile.category_scores[category.lower()]
                cat_count = profile.category_counts.get(category.lower(), 0)
                # Weight by experience
                experience_factor = min(cat_count / 10, 1.0)
                score += cat_score * experience_factor * 2
                factors += 2
            
            # File expertise match
            if files:
                for file in files:
                    normalized = file.replace("\\", "/").lower()
                    if normalized in profile.file_expertise:
                        score += min(profile.file_expertise[normalized] / 5, 1.0)
                        factors += 1
            
            # Module expertise match
            if modules:
                for module in modules:
                    if module.lower() in profile.module_expertise:
                        score += min(profile.module_expertise[module.lower()] / 5, 1.0)
                        factors += 1
            elif files:
                # Extract modules from files
                for file in files:
                    module = self._extract_module(file)
                    if module in profile.module_expertise:
                        score += min(profile.module_expertise[module] / 5, 1.0)
                        factors += 1
            
            # Base score from success rate
            score += profile.success_rate * 0.5
            factors += 0.5
            
            if factors > 0:
                normalized_score = score / factors
                candidates.append((agent_id, normalized_score))
        
        if not candidates:
            return None
        
        # Sort by score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0]
    
    def get_task_estimate(
        self,
        agent_id: str,
        category: str
    ) -> Optional[float]:
        """Estimate how long a task will take for an agent."""
        profile = self.profiles.get(agent_id)
        if not profile:
            return None
        
        return profile.avg_completion_times.get(category.lower())
    
    def get_leaderboard(
        self,
        category: Optional[str] = None
    ) -> List[Tuple[str, float, int]]:
        """
        Get leaderboard of agents.
        
        Returns:
            List of (agent_id, score, task_count)
        """
        leaderboard = []
        
        for agent_id, profile in self.profiles.items():
            if category:
                score = profile.category_scores.get(category.lower(), 0)
                count = profile.category_counts.get(category.lower(), 0)
            else:
                score = profile.success_rate
                count = profile.total_tasks
            
            if count > 0:
                leaderboard.append((agent_id, score, count))
        
        leaderboard.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return leaderboard
    
    def suggest_pairing(
        self,
        agent_id: str,
        category: str
    ) -> Optional[str]:
        """Suggest a good collaborator for an agent on a task type."""
        profile = self.profiles.get(agent_id)
        if not profile:
            return None
        
        # Find agents they've collaborated with successfully
        if profile.collaboration_affinity:
            best_collab = max(
                profile.collaboration_affinity.items(),
                key=lambda x: x[1]
            )
            return best_collab[0]
        
        # Otherwise find someone strong in this category
        result = self.find_best_agent(
            category=category,
            exclude=[agent_id]
        )
        return result[0] if result else None
