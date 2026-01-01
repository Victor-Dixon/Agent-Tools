#!/usr/bin/env python3
"""
Performance Analyzer
====================

Analyzes server performance metrics to detect issues
and provide optimization recommendations.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .metrics_collector import ServerMetrics

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Severity levels for detected issues."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class IssueType(Enum):
    """Types of performance issues."""
    HIGH_CPU = "high_cpu"
    HIGH_MEMORY = "high_memory"
    LOW_TICK_RATE = "low_tick_rate"
    MEMORY_LEAK = "memory_leak"
    DISK_SPACE = "disk_space"
    HIGH_LATENCY = "high_latency"
    PLAYER_SPIKE = "player_spike"
    CRASH_RISK = "crash_risk"


@dataclass
class PerformanceIssue:
    """Represents a detected performance issue."""
    type: IssueType
    severity: IssueSeverity
    message: str
    current_value: float
    threshold: float
    timestamp: str
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "message": self.message,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp,
            "recommendations": self.recommendations,
        }


@dataclass
class PerformanceReport:
    """Comprehensive performance analysis report."""
    timestamp: str
    overall_score: int  # 0-100
    status: str  # healthy, degraded, critical
    issues: List[PerformanceIssue]
    metrics_summary: Dict[str, float]
    recommendations: List[str]
    trends: Dict[str, str]  # metric -> trend (improving, stable, declining)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "overall_score": self.overall_score,
            "status": self.status,
            "issues": [i.to_dict() for i in self.issues],
            "metrics_summary": self.metrics_summary,
            "recommendations": self.recommendations,
            "trends": self.trends,
        }


class PerformanceAnalyzer:
    """
    Analyzes server performance and provides insights.
    
    Features:
    - Issue detection with thresholds
    - Trend analysis
    - Optimization recommendations
    - Crash risk prediction
    """
    
    # Default thresholds
    THRESHOLDS = {
        "cpu_warning": 70,
        "cpu_critical": 90,
        "memory_warning": 70,
        "memory_critical": 90,
        "tick_rate_warning": 80,  # % of target
        "tick_rate_critical": 50,
        "disk_warning": 80,
        "disk_critical": 95,
    }
    
    def __init__(
        self,
        thresholds: Optional[Dict[str, float]] = None,
    ):
        self.thresholds = {**self.THRESHOLDS, **(thresholds or {})}
        self._baseline: Optional[Dict[str, float]] = None
    
    def analyze(
        self,
        current: ServerMetrics,
        history: Optional[List[ServerMetrics]] = None,
    ) -> PerformanceReport:
        """
        Analyze current metrics and history to generate a report.
        
        Args:
            current: Current metrics snapshot
            history: Historical metrics for trend analysis
            
        Returns:
            Comprehensive PerformanceReport
        """
        issues = []
        recommendations = []
        trends = {}
        
        # Detect issues
        issues.extend(self._check_cpu(current))
        issues.extend(self._check_memory(current, history))
        issues.extend(self._check_tick_rate(current))
        issues.extend(self._check_disk(current))
        
        # Analyze trends if history available
        if history and len(history) >= 5:
            trends = self._analyze_trends(history)
            
            # Add trend-based recommendations
            if trends.get("memory") == "increasing":
                recommendations.append(
                    "Memory usage is trending upward. Consider scheduling a restart "
                    "or investigating potential memory leaks."
                )
            
            if trends.get("tick_rate") == "decreasing":
                recommendations.append(
                    "Tick rate is declining over time. Check for accumulating entities, "
                    "growing world size, or mod performance issues."
                )
        
        # Calculate overall score
        score = self._calculate_score(current, issues)
        
        # Determine status
        if any(i.severity == IssueSeverity.CRITICAL for i in issues):
            status = "critical"
        elif any(i.severity == IssueSeverity.WARNING for i in issues):
            status = "degraded"
        else:
            status = "healthy"
        
        # Compile top recommendations
        for issue in issues:
            recommendations.extend(issue.recommendations[:2])
        
        return PerformanceReport(
            timestamp=current.timestamp,
            overall_score=score,
            status=status,
            issues=issues,
            metrics_summary={
                "cpu_percent": current.cpu_percent,
                "memory_percent": current.memory_percent,
                "tick_rate_percent": current.tick_rate_percent,
                "disk_percent": current.disk_percent,
                "player_count": current.player_count,
            },
            recommendations=list(set(recommendations))[:5],  # Top 5 unique
            trends=trends,
        )
    
    def _check_cpu(self, metrics: ServerMetrics) -> List[PerformanceIssue]:
        """Check for CPU issues."""
        issues = []
        
        if metrics.cpu_percent >= self.thresholds["cpu_critical"]:
            issues.append(PerformanceIssue(
                type=IssueType.HIGH_CPU,
                severity=IssueSeverity.CRITICAL,
                message=f"CPU usage critically high at {metrics.cpu_percent:.1f}%",
                current_value=metrics.cpu_percent,
                threshold=self.thresholds["cpu_critical"],
                timestamp=metrics.timestamp,
                recommendations=[
                    "Reduce max player count or mod load",
                    "Check for runaway processes or infinite loops",
                    "Consider upgrading server CPU",
                ],
            ))
        elif metrics.cpu_percent >= self.thresholds["cpu_warning"]:
            issues.append(PerformanceIssue(
                type=IssueType.HIGH_CPU,
                severity=IssueSeverity.WARNING,
                message=f"CPU usage elevated at {metrics.cpu_percent:.1f}%",
                current_value=metrics.cpu_percent,
                threshold=self.thresholds["cpu_warning"],
                timestamp=metrics.timestamp,
                recommendations=[
                    "Monitor for further increases",
                    "Review recently added mods for performance impact",
                ],
            ))
        
        return issues
    
    def _check_memory(
        self,
        metrics: ServerMetrics,
        history: Optional[List[ServerMetrics]] = None,
    ) -> List[PerformanceIssue]:
        """Check for memory issues including potential leaks."""
        issues = []
        
        if metrics.memory_percent >= self.thresholds["memory_critical"]:
            issues.append(PerformanceIssue(
                type=IssueType.HIGH_MEMORY,
                severity=IssueSeverity.CRITICAL,
                message=f"Memory usage critically high at {metrics.memory_percent:.1f}%",
                current_value=metrics.memory_percent,
                threshold=self.thresholds["memory_critical"],
                timestamp=metrics.timestamp,
                recommendations=[
                    "Schedule immediate server restart",
                    "Reduce world size or player limit",
                    "Check for memory-intensive mods",
                ],
            ))
        elif metrics.memory_percent >= self.thresholds["memory_warning"]:
            issues.append(PerformanceIssue(
                type=IssueType.HIGH_MEMORY,
                severity=IssueSeverity.WARNING,
                message=f"Memory usage elevated at {metrics.memory_percent:.1f}%",
                current_value=metrics.memory_percent,
                threshold=self.thresholds["memory_warning"],
                timestamp=metrics.timestamp,
                recommendations=[
                    "Consider scheduling a restart during off-peak hours",
                    "Review memory usage trends",
                ],
            ))
        
        # Check for memory leak pattern
        if history and len(history) >= 10:
            memory_values = [m.memory_percent for m in history[-10:]]
            if all(memory_values[i] <= memory_values[i+1] for i in range(len(memory_values)-1)):
                # Consistently increasing memory
                increase_rate = memory_values[-1] - memory_values[0]
                if increase_rate > 5:  # More than 5% increase
                    issues.append(PerformanceIssue(
                        type=IssueType.MEMORY_LEAK,
                        severity=IssueSeverity.WARNING,
                        message=f"Potential memory leak detected: +{increase_rate:.1f}% over monitoring period",
                        current_value=increase_rate,
                        threshold=5.0,
                        timestamp=metrics.timestamp,
                        recommendations=[
                            "Schedule regular restarts to mitigate",
                            "Identify the leaking mod or plugin",
                            "Check for known memory leak issues in installed mods",
                        ],
                    ))
        
        return issues
    
    def _check_tick_rate(self, metrics: ServerMetrics) -> List[PerformanceIssue]:
        """Check for tick rate issues."""
        issues = []
        tick_percent = metrics.tick_rate_percent
        
        if tick_percent <= self.thresholds["tick_rate_critical"]:
            issues.append(PerformanceIssue(
                type=IssueType.LOW_TICK_RATE,
                severity=IssueSeverity.CRITICAL,
                message=f"Tick rate critically low at {metrics.tick_rate:.1f} ({tick_percent:.0f}% of target)",
                current_value=tick_percent,
                threshold=self.thresholds["tick_rate_critical"],
                timestamp=metrics.timestamp,
                recommendations=[
                    "Reduce entity count or world complexity",
                    "Disable performance-heavy mods",
                    "Consider a world reset or cleanup",
                    "Check for lag-inducing builds or machines",
                ],
            ))
        elif tick_percent <= self.thresholds["tick_rate_warning"]:
            issues.append(PerformanceIssue(
                type=IssueType.LOW_TICK_RATE,
                severity=IssueSeverity.WARNING,
                message=f"Tick rate below optimal at {metrics.tick_rate:.1f} ({tick_percent:.0f}% of target)",
                current_value=tick_percent,
                threshold=self.thresholds["tick_rate_warning"],
                timestamp=metrics.timestamp,
                recommendations=[
                    "Monitor entity counts",
                    "Review mod performance settings",
                ],
            ))
        
        return issues
    
    def _check_disk(self, metrics: ServerMetrics) -> List[PerformanceIssue]:
        """Check for disk space issues."""
        issues = []
        
        if metrics.disk_percent >= self.thresholds["disk_critical"]:
            issues.append(PerformanceIssue(
                type=IssueType.DISK_SPACE,
                severity=IssueSeverity.CRITICAL,
                message=f"Disk space critically low at {metrics.disk_percent:.1f}% used",
                current_value=metrics.disk_percent,
                threshold=self.thresholds["disk_critical"],
                timestamp=metrics.timestamp,
                recommendations=[
                    "Clean up old backups and logs immediately",
                    "Remove unused mods or worlds",
                    "Expand disk capacity",
                ],
            ))
        elif metrics.disk_percent >= self.thresholds["disk_warning"]:
            issues.append(PerformanceIssue(
                type=IssueType.DISK_SPACE,
                severity=IssueSeverity.WARNING,
                message=f"Disk space getting low at {metrics.disk_percent:.1f}% used",
                current_value=metrics.disk_percent,
                threshold=self.thresholds["disk_warning"],
                timestamp=metrics.timestamp,
                recommendations=[
                    "Schedule log rotation and cleanup",
                    "Review backup retention policy",
                ],
            ))
        
        return issues
    
    def _analyze_trends(
        self,
        history: List[ServerMetrics],
    ) -> Dict[str, str]:
        """Analyze metric trends over time."""
        trends = {}
        
        if len(history) < 5:
            return trends
        
        # Split into first and second half
        mid = len(history) // 2
        first_half = history[:mid]
        second_half = history[mid:]
        
        # CPU trend
        cpu_first = sum(m.cpu_percent for m in first_half) / len(first_half)
        cpu_second = sum(m.cpu_percent for m in second_half) / len(second_half)
        trends["cpu"] = self._get_trend(cpu_first, cpu_second)
        
        # Memory trend
        mem_first = sum(m.memory_percent for m in first_half) / len(first_half)
        mem_second = sum(m.memory_percent for m in second_half) / len(second_half)
        trends["memory"] = self._get_trend(mem_first, mem_second)
        
        # Tick rate trend (inverted - higher is better)
        tick_first = sum(m.tick_rate for m in first_half) / len(first_half)
        tick_second = sum(m.tick_rate for m in second_half) / len(second_half)
        trends["tick_rate"] = self._get_trend(tick_second, tick_first)  # Inverted
        
        return trends
    
    def _get_trend(self, old_value: float, new_value: float, threshold: float = 5) -> str:
        """Determine trend direction."""
        diff_percent = ((new_value - old_value) / max(old_value, 1)) * 100
        
        if diff_percent > threshold:
            return "increasing"
        elif diff_percent < -threshold:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_score(
        self,
        metrics: ServerMetrics,
        issues: List[PerformanceIssue],
    ) -> int:
        """Calculate overall performance score (0-100)."""
        score = 100
        
        # Deduct for issues
        for issue in issues:
            if issue.severity == IssueSeverity.CRITICAL:
                score -= 30
            elif issue.severity == IssueSeverity.WARNING:
                score -= 10
        
        # Adjust for metric values
        if metrics.cpu_percent > 50:
            score -= int((metrics.cpu_percent - 50) * 0.3)
        
        if metrics.memory_percent > 50:
            score -= int((metrics.memory_percent - 50) * 0.3)
        
        if metrics.tick_rate_percent < 100:
            score -= int((100 - metrics.tick_rate_percent) * 0.2)
        
        return max(0, min(100, score))
    
    def generate_weekly_report(
        self,
        history: List[ServerMetrics],
    ) -> Dict[str, Any]:
        """Generate a weekly performance summary."""
        if not history:
            return {"error": "No historical data available"}
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in history) / len(history)
        avg_memory = sum(m.memory_percent for m in history) / len(history)
        avg_tick = sum(m.tick_rate for m in history) / len(history)
        avg_players = sum(m.player_count for m in history) / len(history)
        
        # Find peaks
        max_cpu = max(m.cpu_percent for m in history)
        max_memory = max(m.memory_percent for m in history)
        max_players = max(m.player_count for m in history)
        min_tick = min(m.tick_rate for m in history)
        
        # Calculate uptime
        total_samples = len(history)
        healthy_samples = sum(1 for m in history if m.is_healthy)
        uptime_percent = (healthy_samples / total_samples) * 100
        
        return {
            "period": {
                "start": history[0].timestamp,
                "end": history[-1].timestamp,
                "samples": total_samples,
            },
            "averages": {
                "cpu_percent": round(avg_cpu, 1),
                "memory_percent": round(avg_memory, 1),
                "tick_rate": round(avg_tick, 1),
                "player_count": round(avg_players, 1),
            },
            "peaks": {
                "max_cpu_percent": round(max_cpu, 1),
                "max_memory_percent": round(max_memory, 1),
                "max_players": max_players,
                "min_tick_rate": round(min_tick, 1),
            },
            "reliability": {
                "uptime_percent": round(uptime_percent, 2),
                "healthy_samples": healthy_samples,
                "degraded_samples": total_samples - healthy_samples,
            },
        }
