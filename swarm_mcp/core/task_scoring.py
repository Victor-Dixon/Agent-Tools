"""
Task Scoring & Selection Engine
===============================

Prioritizes tasks based on ROI (Return on Investment).

Formula:
    ROI = (User Value * Urgency) / (Effort * Risk * Dependency Factor)

attributes:
    - User Value (1-10): How much the user cares.
    - Urgency (1-10): Time sensitivity.
    - Effort (1-10): Estimated complexity/time.
    - Risk (1-10): Probability of breaking things.
    - Dependencies (count): Number of blocking tasks.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import math

@dataclass
class ScoredTask:
    id: str
    description: str
    value: float = 5.0
    urgency: float = 5.0
    effort: float = 5.0
    risk: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def roi_score(self) -> float:
        """Calculate Return on Investment score."""
        # Avoid division by zero
        effort_factor = max(1.0, self.effort)
        risk_factor = max(1.0, self.risk)
        dep_factor = 1.0 + (len(self.dependencies) * 0.5)
        
        numerator = self.value * self.urgency
        denominator = effort_factor * risk_factor * dep_factor
        
        return numerator / denominator

class TaskScorer:
    """Evaluates and selects the next best task."""

    def __init__(self):
        pass

    def score_tasks(self, tasks: List[ScoredTask]) -> List[ScoredTask]:
        """Return tasks sorted by ROI (descending)."""
        return sorted(tasks, key=lambda t: t.roi_score, reverse=True)

    def select_next_task(self, tasks: List[ScoredTask]) -> Optional[ScoredTask]:
        """Select the single highest impact task."""
        if not tasks:
            return None
        
        scored = self.score_tasks(tasks)
        return scored[0]

    def parse_task_metadata(self, task_description: str) -> Dict[str, float]:
        """
        Extract scoring attributes from task description if present.
        Expected format: "Task description [v=8 u=5 e=3 r=1]"
        """
        import re
        
        # Defaults
        attrs = {
            "value": 5.0,
            "urgency": 5.0,
            "effort": 5.0,
            "risk": 1.0
        }
        
        # Look for [k=v ...] pattern
        match = re.search(r"\[(.*?)\]", task_description)
        if match:
            params = match.group(1).split()
            for p in params:
                if "=" in p:
                    k, v = p.split("=", 1)
                    try:
                        val = float(v)
                        if k in ["v", "val", "value"]: attrs["value"] = val
                        elif k in ["u", "urg", "urgency"]: attrs["urgency"] = val
                        elif k in ["e", "eff", "effort"]: attrs["effort"] = val
                        elif k in ["r", "risk"]: attrs["risk"] = val
                    except ValueError:
                        pass
                        
        return attrs
