#!/usr/bin/env python3
"""
Message Analytics Tools - BI Analysis for Message System
========================================================

Autonomous BI tools for analyzing message patterns, communication flows,
and system insights from message history.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-01-27
JET FUEL: Autonomous creation
"""

from typing import Any, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# Fix Counter usage in dict conversion
def _counter_to_dict(counter_obj):
    """Convert Counter to dict, handling both Counter and dict types."""
    if isinstance(counter_obj, Counter):
        return dict(counter_obj)
    return counter_obj if isinstance(counter_obj, dict) else {}

try:
    from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
    from src.repositories.message_repository import MessageRepository
    from src.core.analytics.engines.metrics_engine import MetricsEngine
    from src.core.analytics.framework.pattern_analysis_engine import PatternAnalysisEngine
except ImportError:
    IToolAdapter = object
    ToolResult = None
    ToolSpec = None
    MessageRepository = None
    MetricsEngine = None
    PatternAnalysisEngine = None


class MessagePatternAnalyzerTool(IToolAdapter):
    """Analyze communication patterns from message history."""
    
    def __init__(self):
        """Initialize message pattern analyzer."""
        self.repo = MessageRepository() if MessageRepository else None
        self.pattern_engine = PatternAnalysisEngine() if PatternAnalysisEngine else None
    
    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="bi.message.patterns",
            version="1.0.0",
            category="business_intelligence",
            summary="Analyze communication patterns from message history",
            required_params=[],
            optional_params={"limit": 1000},
        )
    
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])
    
    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Analyze message patterns."""
        if not self.repo:
            return ToolResult(success=False, output=None, error_message="MessageRepository not available", exit_code=1)
        
        limit = params.get("limit", 1000)
        history = self.repo.get_message_history(limit=limit)
        
        # Analyze patterns
        patterns = {
            "total_messages": len(history),
            "by_sender": Counter(),
            "by_recipient": Counter(),
            "by_type": Counter(),
            "by_priority": Counter(),
            "communication_pairs": Counter(),
            "hourly_distribution": defaultdict(int),
            "daily_distribution": defaultdict(int),
        }
        
        for msg in history:
            sender = msg.get("from") or msg.get("sender", "UNKNOWN")
            recipient = msg.get("to") or msg.get("recipient", "UNKNOWN")
            msg_type = msg.get("message_type") or msg.get("type", "unknown")
            priority = msg.get("priority", "normal")
            timestamp = msg.get("timestamp", "")
            
            patterns["by_sender"][sender] += 1
            patterns["by_recipient"][recipient] += 1
            patterns["by_type"][msg_type] += 1
            patterns["by_priority"][priority] += 1
            patterns["communication_pairs"][f"{sender}→{recipient}"] += 1
            
            # Time analysis
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                patterns["hourly_distribution"][dt.hour] += 1
                patterns["daily_distribution"][dt.strftime("%Y-%m-%d")] += 1
            except (ValueError, AttributeError):
                pass
        
        # Convert Counters to dicts
        result = {
            "total_messages": patterns["total_messages"],
            "by_sender": dict(patterns["by_sender"].most_common(10)),
            "by_recipient": dict(patterns["by_recipient"].most_common(10)),
            "by_type": dict(patterns["by_type"]),
            "by_priority": dict(patterns["by_priority"]),
            "top_communication_pairs": dict(patterns["communication_pairs"].most_common(10)),
            "hourly_distribution": dict(patterns["hourly_distribution"]),
            "daily_distribution": dict(patterns["daily_distribution"]),
        }
        
        return ToolResult(success=True, output=result)
    
    def get_help(self) -> str:
        """Get tool help text."""
        return """
Message Pattern Analyzer - Analyze communication patterns

Args:
    limit: Maximum messages to analyze (default: 1000)

Returns:
    Dictionary with pattern analysis:
    - total_messages: Total count
    - by_sender: Top senders
    - by_recipient: Top recipients
    - by_type: Message type distribution
    - by_priority: Priority distribution
    - top_communication_pairs: Most active pairs
    - hourly_distribution: Messages by hour
    - daily_distribution: Messages by day
"""


class MessageMetricsDashboardTool(IToolAdapter):
    """Generate metrics dashboard from message system."""
    
    def __init__(self):
        """Initialize metrics dashboard."""
        self.repo = MessageRepository() if MessageRepository else None
        self.metrics_engine = MetricsEngine() if MetricsEngine else None
    
    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="bi.message.dashboard",
            version="1.0.0",
            category="business_intelligence",
            summary="Generate comprehensive metrics dashboard from message system",
            required_params=[],
            optional_params={},
        )
    
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])
    
    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Generate metrics dashboard."""
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "message_history": {},
            "queue_metrics": {},
            "activity_metrics": {},
        }
        
        # Message history metrics
        if self.repo:
            history = self.repo.get_message_history(limit=100)
            status_counter = Counter(m.get("status", "unknown") for m in history)
            dashboard["message_history"] = {
                "total_messages": len(history),
                "recent_messages": len([m for m in history if self._is_recent(m.get("timestamp", ""))]),
                "by_status": dict(status_counter),
            }
        
        # Queue metrics from metrics engine
        if self.metrics_engine:
            all_metrics = self.metrics_engine.get_all_metrics()
            queue_metrics = {k: v for k, v in all_metrics.items() if k.startswith("queue.")}
            dashboard["queue_metrics"] = queue_metrics
        
        # Activity metrics
        try:
            from src.core.agent_activity_tracker import get_activity_tracker
            tracker = get_activity_tracker()
            activity = tracker.get_all_agent_activity()
            dashboard["activity_metrics"] = {
                "active_agents": len([a for a in activity.values() if a.state.value != "idle"]),
                "by_state": Counter(a.state.value for a in activity.values()),
            }
        except Exception:
            pass
        
        return ToolResult(success=True, output=dashboard)
    
    def _is_recent(self, timestamp: str, hours: int = 24) -> bool:
        """Check if timestamp is within recent hours."""
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return (datetime.now() - dt.replace(tzinfo=None)) < timedelta(hours=hours)
        except (ValueError, AttributeError):
            return False
    
    def get_help(self) -> str:
        """Get tool help text."""
        return """
Message Metrics Dashboard - Generate comprehensive metrics

Returns:
    Dictionary with dashboard data:
    - message_history: History statistics
    - queue_metrics: Queue performance metrics
    - activity_metrics: Agent activity metrics
"""


class MessageLearningExtractorTool(IToolAdapter):
    """Extract learning opportunities from message history."""
    
    def __init__(self):
        """Initialize learning extractor."""
        self.repo = MessageRepository() if MessageRepository else None
    
    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="bi.message.learnings",
            version="1.0.0",
            category="business_intelligence",
            summary="Extract learning opportunities and insights from message history",
            required_params=[],
            optional_params={"limit": 500},
        )
    
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])
    
    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Extract learning opportunities."""
        if not self.repo:
            return ToolResult(success=False, output=None, error_message="MessageRepository not available", exit_code=1)
        
        limit = params.get("limit", 500)
        history = self.repo.get_message_history(limit=limit)
        
        learnings = {
            "communication_patterns": [],
            "efficiency_insights": [],
            "bottleneck_identifications": [],
            "optimization_opportunities": [],
        }
        
        # Analyze communication patterns
        sender_counts = Counter(m.get("from") or m.get("sender") for m in history)
        recipient_counts = Counter(m.get("to") or m.get("recipient") for m in history)
        
        # Identify top communicators
        top_senders = sender_counts.most_common(5)
        top_recipients = recipient_counts.most_common(5)
        
        learnings["communication_patterns"] = [
            f"Top sender: {sender} ({count} messages)" for sender, count in top_senders
        ]
        learnings["communication_patterns"].extend([
            f"Top recipient: {recipient} ({count} messages)" for recipient, count in top_recipients
        ])
        
        # Identify bottlenecks (high message volume to single recipient)
        if top_recipients:
            max_recipient = top_recipients[0]
            if max_recipient[1] > 50:
                learnings["bottleneck_identifications"].append(
                    f"Potential bottleneck: {max_recipient[0]} receiving {max_recipient[1]} messages"
                )
        
        # Efficiency insights (message types)
        type_counts = Counter(m.get("message_type") or m.get("type") for m in history)
        learnings["efficiency_insights"] = [
            f"Message type distribution: {dict(type_counts)}"
        ]
        
        # Optimization opportunities
        failed_messages = [m for m in history if m.get("status") == "FAILED"]
        if failed_messages:
            learnings["optimization_opportunities"].append(
                f"Failed messages: {len(failed_messages)} ({len(failed_messages)/len(history)*100:.1f}% failure rate)" if history else "No history"
            )
        
        return ToolResult(success=True, output=learnings)
    
    def get_help(self) -> str:
        """Get tool help text."""
        return """
Message Learning Extractor - Extract insights from message history

Args:
    limit: Maximum messages to analyze (default: 500)

Returns:
    Dictionary with learning opportunities:
    - communication_patterns: Top senders/recipients
    - efficiency_insights: Message type analysis
    - bottleneck_identifications: Potential bottlenecks
    - optimization_opportunities: Optimization suggestions
"""

