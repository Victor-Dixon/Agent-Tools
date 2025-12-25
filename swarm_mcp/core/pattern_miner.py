"""
Pattern Miner - Learn from Successful Coordination
===================================================

🐺 WE ARE SWARM - We learn from every hunt.

This is IP-level code: Extracts patterns from successful multi-agent
coordination and suggests them for similar future situations.

What It Learns:
- Task sequences that work well together
- Agent pairings that produce quality work
- Time-of-day patterns for productivity
- File change patterns that indicate good architecture
- Communication patterns that resolve blockers

Why It Matters:
- "Last time we had an auth bug, agent-1 and agent-3 paired and fixed it in 30min"
- "Database tasks done after infrastructure tasks have 90% success rate"
- "Agent-2 is most productive between 2-4pm"

Author: The Swarm
License: MIT
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from collections import defaultdict
import re


@dataclass
class CoordinationEvent:
    """A recorded coordination event."""
    id: str
    event_type: str  # task_complete, collaboration, conflict_resolved, etc.
    agents: List[str]
    context: Dict[str, Any]
    outcome: str  # success, failure, partial
    timestamp: datetime = field(default_factory=datetime.now)
    duration_minutes: float = 0
    quality_score: float = 1.0
    tags: List[str] = field(default_factory=list)


@dataclass
class Pattern:
    """A discovered coordination pattern."""
    id: str
    name: str
    description: str
    pattern_type: str  # sequence, pairing, timing, workflow
    conditions: Dict[str, Any]
    actions: List[str]
    success_rate: float
    occurrence_count: int
    avg_quality: float
    example_events: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class Suggestion:
    """A pattern-based suggestion for current situation."""
    pattern_id: str
    pattern_name: str
    confidence: float  # 0-1
    reasoning: str
    suggested_actions: List[str]
    expected_outcome: str
    similar_past_events: List[str]


class PatternMiner:
    """
    Learns coordination patterns from swarm history.
    
    This is core IP: Emergent learning without ML models.
    
    Example:
        miner = PatternMiner()
        
        # Record events as they happen
        miner.record_event(
            event_type="task_complete",
            agents=["agent-1", "agent-3"],
            context={"category": "debugging", "file": "auth.py"},
            outcome="success",
            duration_minutes=45,
            quality_score=0.95
        )
        
        # Over time, patterns emerge...
        
        # Get suggestions for a new situation
        suggestions = miner.suggest(
            context={"category": "debugging", "file": "auth.py"}
        )
        # Returns: "Pattern: Agent pairing for auth"
        # "agent-1 and agent-3 have 95% success rate on auth bugs"
    """
    
    def __init__(self, storage_dir: str = "./swarm_patterns"):
        """Initialize pattern miner."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.events_dir = self.storage_dir / "events"
        self.patterns_dir = self.storage_dir / "patterns"
        self.events_dir.mkdir(exist_ok=True)
        self.patterns_dir.mkdir(exist_ok=True)
        
        self.events: List[CoordinationEvent] = []
        self.patterns: Dict[str, Pattern] = {}
        
        self._load_data()
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}_{timestamp[:16]}"
    
    def _load_data(self):
        """Load events and patterns."""
        # Load events
        for event_file in sorted(self.events_dir.glob("*.json")):
            try:
                data = json.loads(event_file.read_text())
                self.events.append(CoordinationEvent(
                    id=data["id"],
                    event_type=data["event_type"],
                    agents=data["agents"],
                    context=data["context"],
                    outcome=data["outcome"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    duration_minutes=data.get("duration_minutes", 0),
                    quality_score=data.get("quality_score", 1.0),
                    tags=data.get("tags", [])
                ))
            except Exception:
                pass
        
        # Load patterns
        for pattern_file in self.patterns_dir.glob("*.json"):
            try:
                data = json.loads(pattern_file.read_text())
                self.patterns[data["id"]] = Pattern(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    pattern_type=data["pattern_type"],
                    conditions=data["conditions"],
                    actions=data["actions"],
                    success_rate=data["success_rate"],
                    occurrence_count=data["occurrence_count"],
                    avg_quality=data.get("avg_quality", 0.8),
                    example_events=data.get("example_events", []),
                    discovered_at=datetime.fromisoformat(data["discovered_at"]),
                    last_seen=datetime.fromisoformat(data.get("last_seen", data["discovered_at"]))
                )
            except Exception:
                pass
    
    def _save_event(self, event: CoordinationEvent):
        """Save event to disk."""
        event_file = self.events_dir / f"{event.id}.json"
        event_file.write_text(json.dumps({
            "id": event.id,
            "event_type": event.event_type,
            "agents": event.agents,
            "context": event.context,
            "outcome": event.outcome,
            "timestamp": event.timestamp.isoformat(),
            "duration_minutes": event.duration_minutes,
            "quality_score": event.quality_score,
            "tags": event.tags
        }, indent=2))
    
    def _save_pattern(self, pattern: Pattern):
        """Save pattern to disk."""
        pattern_file = self.patterns_dir / f"{pattern.id}.json"
        pattern_file.write_text(json.dumps({
            "id": pattern.id,
            "name": pattern.name,
            "description": pattern.description,
            "pattern_type": pattern.pattern_type,
            "conditions": pattern.conditions,
            "actions": pattern.actions,
            "success_rate": pattern.success_rate,
            "occurrence_count": pattern.occurrence_count,
            "avg_quality": pattern.avg_quality,
            "example_events": pattern.example_events,
            "discovered_at": pattern.discovered_at.isoformat(),
            "last_seen": pattern.last_seen.isoformat()
        }, indent=2))
    
    def record_event(
        self,
        event_type: str,
        agents: List[str],
        context: Dict[str, Any],
        outcome: str,
        duration_minutes: float = 0,
        quality_score: float = 1.0,
        tags: Optional[List[str]] = None
    ) -> CoordinationEvent:
        """
        Record a coordination event.
        
        Args:
            event_type: Type (task_complete, collaboration, conflict, etc.)
            agents: Agents involved
            context: Context (category, files, etc.)
            outcome: success/failure/partial
            duration_minutes: How long it took
            quality_score: Quality of outcome (0-1)
            tags: Additional tags
            
        Returns:
            The recorded event
        """
        event = CoordinationEvent(
            id=self._generate_id("event"),
            event_type=event_type,
            agents=sorted(agents),
            context=context,
            outcome=outcome,
            duration_minutes=duration_minutes,
            quality_score=quality_score,
            tags=tags or []
        )
        
        self.events.append(event)
        self._save_event(event)
        
        # Trigger pattern mining
        self._mine_patterns()
        
        return event
    
    def _mine_patterns(self):
        """Mine patterns from event history."""
        if len(self.events) < 5:
            return  # Need minimum data
        
        # Mine different pattern types
        self._mine_pairing_patterns()
        self._mine_sequence_patterns()
        self._mine_timing_patterns()
        self._mine_context_patterns()
    
    def _mine_pairing_patterns(self):
        """Find successful agent pairing patterns."""
        # Group events by agent pairs
        pair_outcomes: Dict[Tuple[str, ...], List[CoordinationEvent]] = defaultdict(list)
        
        for event in self.events:
            if len(event.agents) >= 2 and event.outcome == "success":
                pair = tuple(sorted(event.agents))
                pair_outcomes[pair].append(event)
        
        # Find pairs with high success rates
        for pair, events in pair_outcomes.items():
            if len(events) < 3:
                continue
            
            # Calculate metrics
            success_count = sum(1 for e in events if e.outcome == "success")
            success_rate = success_count / len(events)
            avg_quality = sum(e.quality_score for e in events) / len(events)
            
            if success_rate >= 0.8 and avg_quality >= 0.7:
                # Extract common context
                categories = [e.context.get("category") for e in events if "category" in e.context]
                common_category = max(set(categories), key=categories.count) if categories else None
                
                pattern_id = f"pairing_{'-'.join(pair)}"
                
                if pattern_id in self.patterns:
                    # Update existing
                    pattern = self.patterns[pattern_id]
                    pattern.occurrence_count = len(events)
                    pattern.success_rate = success_rate
                    pattern.avg_quality = avg_quality
                    pattern.last_seen = datetime.now()
                    pattern.example_events = [e.id for e in events[-5:]]
                else:
                    # Create new
                    self.patterns[pattern_id] = Pattern(
                        id=pattern_id,
                        name=f"Successful pairing: {' + '.join(pair)}",
                        description=f"Agents {' and '.join(pair)} work well together",
                        pattern_type="pairing",
                        conditions={"agents": list(pair), "category": common_category},
                        actions=[f"Pair {pair[0]} with {pair[1]}"],
                        success_rate=success_rate,
                        occurrence_count=len(events),
                        avg_quality=avg_quality,
                        example_events=[e.id for e in events[-5:]]
                    )
                
                self._save_pattern(self.patterns[pattern_id])
    
    def _mine_sequence_patterns(self):
        """Find successful task sequence patterns."""
        # Look at tasks completed within 2 hours of each other
        window = timedelta(hours=2)
        sequences: Dict[Tuple[str, str], List[Tuple[CoordinationEvent, CoordinationEvent]]] = defaultdict(list)
        
        sorted_events = sorted(self.events, key=lambda e: e.timestamp)
        
        for i, event1 in enumerate(sorted_events):
            if event1.outcome != "success":
                continue
            
            cat1 = event1.context.get("category", "unknown")
            
            for event2 in sorted_events[i+1:]:
                if event2.timestamp - event1.timestamp > window:
                    break
                
                if event2.outcome != "success":
                    continue
                
                cat2 = event2.context.get("category", "unknown")
                sequences[(cat1, cat2)].append((event1, event2))
        
        # Find frequent sequences
        for (cat1, cat2), event_pairs in sequences.items():
            if len(event_pairs) < 3:
                continue
            
            # Calculate combined quality
            avg_quality = sum(
                (e1.quality_score + e2.quality_score) / 2
                for e1, e2 in event_pairs
            ) / len(event_pairs)
            
            if avg_quality >= 0.7:
                pattern_id = f"sequence_{cat1}_{cat2}"
                
                if pattern_id not in self.patterns:
                    self.patterns[pattern_id] = Pattern(
                        id=pattern_id,
                        name=f"Sequence: {cat1} → {cat2}",
                        description=f"Doing {cat1} before {cat2} leads to better outcomes",
                        pattern_type="sequence",
                        conditions={"first_category": cat1, "second_category": cat2},
                        actions=[f"Do {cat1} task first", f"Then do {cat2} task"],
                        success_rate=1.0,  # All were successful
                        occurrence_count=len(event_pairs),
                        avg_quality=avg_quality,
                        example_events=[e[0].id for e in event_pairs[-3:]]
                    )
                    self._save_pattern(self.patterns[pattern_id])
    
    def _mine_timing_patterns(self):
        """Find time-of-day productivity patterns."""
        # Group by hour of day
        hourly_quality: Dict[int, List[float]] = defaultdict(list)
        
        for event in self.events:
            if event.outcome == "success":
                hour = event.timestamp.hour
                hourly_quality[hour].append(event.quality_score)
        
        # Find peak hours
        peak_hours = []
        for hour, qualities in hourly_quality.items():
            if len(qualities) >= 3:
                avg = sum(qualities) / len(qualities)
                if avg >= 0.85:
                    peak_hours.append((hour, avg, len(qualities)))
        
        if peak_hours:
            peak_hours.sort(key=lambda x: x[1], reverse=True)
            best_hours = [h[0] for h in peak_hours[:3]]
            
            pattern_id = "timing_peak_hours"
            if pattern_id not in self.patterns:
                self.patterns[pattern_id] = Pattern(
                    id=pattern_id,
                    name="Peak productivity hours",
                    description=f"Best work happens at hours: {best_hours}",
                    pattern_type="timing",
                    conditions={"peak_hours": best_hours},
                    actions=[f"Schedule complex tasks for hours {best_hours}"],
                    success_rate=peak_hours[0][1],
                    occurrence_count=sum(h[2] for h in peak_hours),
                    avg_quality=sum(h[1] for h in peak_hours) / len(peak_hours)
                )
                self._save_pattern(self.patterns[pattern_id])
    
    def _mine_context_patterns(self):
        """Find patterns based on context (files, categories)."""
        # Group by category
        category_outcomes: Dict[str, List[CoordinationEvent]] = defaultdict(list)
        
        for event in self.events:
            category = event.context.get("category")
            if category:
                category_outcomes[category].append(event)
        
        # Find categories with consistent success
        for category, events in category_outcomes.items():
            if len(events) < 5:
                continue
            
            success_events = [e for e in events if e.outcome == "success"]
            success_rate = len(success_events) / len(events)
            
            if success_rate >= 0.8:
                # Find common agents for this category
                agent_counts: Dict[str, int] = defaultdict(int)
                for event in success_events:
                    for agent in event.agents:
                        agent_counts[agent] += 1
                
                best_agents = sorted(
                    agent_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                
                pattern_id = f"context_{category}"
                if pattern_id not in self.patterns:
                    self.patterns[pattern_id] = Pattern(
                        id=pattern_id,
                        name=f"Experts for {category}",
                        description=f"Best agents for {category}: {[a[0] for a in best_agents]}",
                        pattern_type="context",
                        conditions={"category": category},
                        actions=[f"Assign {category} tasks to {best_agents[0][0]}"],
                        success_rate=success_rate,
                        occurrence_count=len(events),
                        avg_quality=sum(e.quality_score for e in success_events) / len(success_events),
                        example_events=[e.id for e in events[-5:]]
                    )
                    self._save_pattern(self.patterns[pattern_id])
    
    def suggest(
        self,
        context: Dict[str, Any],
        agents: Optional[List[str]] = None
    ) -> List[Suggestion]:
        """
        Get suggestions based on patterns.
        
        Args:
            context: Current context (category, files, etc.)
            agents: Available agents
            
        Returns:
            List of pattern-based suggestions
        """
        suggestions = []
        
        category = context.get("category", "").lower()
        files = context.get("files", [])
        
        for pattern in self.patterns.values():
            confidence = 0.0
            reasoning = ""
            
            if pattern.pattern_type == "context":
                if pattern.conditions.get("category") == category:
                    confidence = pattern.success_rate * 0.9
                    reasoning = f"Pattern '{pattern.name}' matches category"
            
            elif pattern.pattern_type == "pairing":
                pattern_agents = set(pattern.conditions.get("agents", []))
                if agents and pattern_agents.issubset(set(agents)):
                    confidence = pattern.success_rate * 0.85
                    reasoning = f"Available agents match successful pairing"
            
            elif pattern.pattern_type == "timing":
                current_hour = datetime.now().hour
                peak_hours = pattern.conditions.get("peak_hours", [])
                if current_hour in peak_hours:
                    confidence = 0.7
                    reasoning = "Current time is a peak productivity hour"
            
            if confidence >= 0.5:
                suggestions.append(Suggestion(
                    pattern_id=pattern.id,
                    pattern_name=pattern.name,
                    confidence=confidence,
                    reasoning=reasoning,
                    suggested_actions=pattern.actions,
                    expected_outcome=f"{pattern.success_rate*100:.0f}% success rate based on {pattern.occurrence_count} past events",
                    similar_past_events=pattern.example_events
                ))
        
        # Sort by confidence
        suggestions.sort(key=lambda s: s.confidence, reverse=True)
        return suggestions[:5]  # Top 5 suggestions
    
    def get_patterns(self, pattern_type: Optional[str] = None) -> List[Pattern]:
        """Get all discovered patterns."""
        patterns = list(self.patterns.values())
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        return sorted(patterns, key=lambda p: p.success_rate, reverse=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pattern mining statistics."""
        return {
            "total_events": len(self.events),
            "total_patterns": len(self.patterns),
            "patterns_by_type": {
                ptype: len([p for p in self.patterns.values() if p.pattern_type == ptype])
                for ptype in ["pairing", "sequence", "timing", "context"]
            },
            "top_patterns": [
                {"name": p.name, "success_rate": p.success_rate, "occurrences": p.occurrence_count}
                for p in sorted(self.patterns.values(), key=lambda x: x.success_rate, reverse=True)[:5]
            ]
        }
