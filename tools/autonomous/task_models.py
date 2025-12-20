"""
Autonomous Task Engine - Data Models
====================================

Shared data models for autonomous task discovery system.

Author: Agent-5 (Business Intelligence & Memory Safety)
Refactored: 2025-10-15 (Lean Excellence V2 Compliance)
Original: tools/autonomous_task_engine.py (781 lines → 3 modules)
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class TaskOpportunity:
    """A discovered task opportunity (autonomous task discovery domain-specific, not to be confused with domain entity Task)."""
    task_id: str
    title: str
    description: str
    file_path: str
    task_type: str  # V2_VIOLATION, TECH_DEBT, FEATURE, BUG, OPTIMIZATION
    severity: str  # CRITICAL, MAJOR, MINOR
    estimated_effort: int  # 1-5 cycles
    estimated_points: int
    roi_score: float  # points / effort
    impact_score: float  # 1-10
    current_lines: Optional[int]
    target_lines: Optional[int]
    reduction_percent: Optional[float]
    blockers: List[str]
    dependencies: List[str]
    coordination_needed: List[str]  # Other agents needed
    skill_match: Dict[str, float]  # agent -> match score (0-1)
    claimed_by: Optional[str]
    claimed_at: Optional[datetime]
    status: str  # AVAILABLE, CLAIMED, IN_PROGRESS, COMPLETED


@dataclass
class AgentProfile:
    """Agent's capabilities and history"""
    agent_id: str
    specializations: List[str]
    past_work_types: Dict[str, int]  # task_type -> count
    files_worked: List[str]
    avg_cycle_time: float
    total_points: int
    success_rate: float
    preferred_complexity: str  # SIMPLE, MODERATE, COMPLEX
    current_workload: int  # 0-5 scale


@dataclass
class TaskRecommendation:
    """Personalized task recommendation for an agent"""
    agent_id: str
    task: TaskOpportunity
    match_score: float  # 0-1 (skill match)
    priority_score: float  # 0-1 (urgency + impact)
    total_score: float  # Combined score
    reasoning: List[str]
    pros: List[str]
    cons: List[str]
    suggested_approach: str
    coordination_plan: Optional[str]

