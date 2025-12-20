#!/usr/bin/env python3
"""
File Locking Optimizer - Agent-3
=================================

Analyzes file locking metrics and provides optimization recommendations.

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tools.file_locking_monitor import FileLockingMonitor


class FileLockingOptimizer:
    """Analyze and optimize file locking retry logic."""

    def __init__(self, monitor: Optional[FileLockingMonitor] = None):
        """Initialize optimizer."""
        self.monitor = monitor or FileLockingMonitor()

    def analyze_current_config(self) -> Dict[str, Any]:
        """Analyze current retry configuration."""
        return {
            "max_retries": 8,
            "base_delay": 0.15,
            "max_delay_cap": 2.0,
            "exponential_backoff": True,
        }

    def get_optimization_recommendations(
        self, hours: int = 24
    ) -> Dict[str, Any]:
        """Get optimization recommendations based on metrics."""
        summary = self.monitor.get_summary(hours)
        current_config = self.analyze_current_config()

        recommendations = {
            "current_config": current_config,
            "metrics": summary,
            "recommendations": [],
            "optimized_config": current_config.copy(),
        }

        # Analyze retry failures
        if summary["retry_failure_count"] > 0:
            recommendations["recommendations"].append({
                "priority": "HIGH",
                "issue": "Retry failures detected",
                "current": f"max_retries={current_config['max_retries']}",
                "recommendation": f"Increase max_retries to {current_config['max_retries'] + 2}",
                "reason": f"{summary['retry_failure_count']} retry failures in last {hours} hours",
            })
            recommendations["optimized_config"]["max_retries"] = (
                current_config["max_retries"] + 2
            )

        # Analyze max attempts needed
        if summary["max_attempts_needed"] >= 7:
            recommendations["recommendations"].append({
                "priority": "MEDIUM",
                "issue": "Max retries approaching limit",
                "current": f"max_retries={current_config['max_retries']}",
                "recommendation": f"Increase max_retries to {current_config['max_retries'] + 1}",
                "reason": f"Max attempts needed: {summary['max_attempts_needed']}",
            })
            if recommendations["optimized_config"]["max_retries"] == current_config["max_retries"]:
                recommendations["optimized_config"]["max_retries"] = (
                    current_config["max_retries"] + 1
                )

        # Analyze retry delays
        if summary["avg_retry_delay_seconds"] > 1.5:
            recommendations["recommendations"].append({
                "priority": "MEDIUM",
                "issue": "Average retry delay high",
                "current": f"base_delay={current_config['base_delay']}s",
                "recommendation": f"Consider reducing base_delay to {current_config['base_delay'] * 0.8:.3f}s",
                "reason": f"Average delay: {summary['avg_retry_delay_seconds']:.3f}s",
            })

        # Analyze error distribution
        if summary["winerror_32_count"] > summary["winerror_5_count"] * 2:
            recommendations["recommendations"].append({
                "priority": "LOW",
                "issue": "High concurrency scenario (WinError 32 dominant)",
                "current": "Current config",
                "recommendation": "Consider implementing file locking mechanism (msvcrt/fcntl)",
                "reason": f"WinError 32: {summary['winerror_32_count']}, WinError 5: {summary['winerror_5_count']}",
            })

        # Success rate analysis
        if summary["success_rate"] < 0.95:
            recommendations["recommendations"].append({
                "priority": "HIGH",
                "issue": "Low success rate",
                "current": f"Success rate: {summary['success_rate'] * 100:.1f}%",
                "recommendation": "Review retry parameters and consider file locking mechanism",
                "reason": f"Success rate below 95%: {summary['success_rate'] * 100:.1f}%",
            })

        return recommendations

    def generate_optimization_report(self, hours: int = 24) -> str:
        """Generate optimization report."""
        recommendations = self.get_optimization_recommendations(hours)

        report = []
        report.append("=" * 70)
        report.append("🔧 File Locking Optimization Report")
        report.append("=" * 70)
        report.append("")

        # Current Configuration
        report.append("⚙️ Current Configuration:")
        report.append("-" * 70)
        config = recommendations["current_config"]
        report.append(f"Max Retries: {config['max_retries']}")
        report.append(f"Base Delay: {config['base_delay']}s")
        report.append(f"Max Delay Cap: {config['max_delay_cap']}s")
        report.append(f"Exponential Backoff: {config['exponential_backoff']}")
        report.append("")

        # Metrics Summary
        report.append("📊 Metrics Summary:")
        report.append("-" * 70)
        metrics = recommendations["metrics"]
        report.append(f"Total Errors: {metrics['total_errors']}")
        report.append(f"Retry Successes: {metrics['retry_success_count']}")
        report.append(f"Retry Failures: {metrics['retry_failure_count']}")
        report.append(f"Success Rate: {metrics['success_rate'] * 100:.1f}%")
        report.append(f"Max Attempts Needed: {metrics['max_attempts_needed']}")
        report.append("")

        # Recommendations
        report.append("💡 Optimization Recommendations:")
        report.append("-" * 70)

        if not recommendations["recommendations"]:
            report.append("✅ No optimizations needed - current configuration is optimal")
        else:
            for rec in recommendations["recommendations"]:
                priority_emoji = {
                    "HIGH": "🔴",
                    "MEDIUM": "🟡",
                    "LOW": "🟢",
                }.get(rec["priority"], "⚪")

                report.append(f"{priority_emoji} {rec['priority']}: {rec['issue']}")
                report.append(f"   Current: {rec['current']}")
                report.append(f"   Recommendation: {rec['recommendation']}")
                report.append(f"   Reason: {rec['reason']}")
                report.append("")

        # Optimized Configuration
        if recommendations["optimized_config"] != recommendations["current_config"]:
            report.append("🚀 Optimized Configuration:")
            report.append("-" * 70)
            opt_config = recommendations["optimized_config"]
            report.append(f"Max Retries: {opt_config['max_retries']}")
            report.append(f"Base Delay: {opt_config['base_delay']}s")
            report.append(f"Max Delay Cap: {opt_config['max_delay_cap']}s")
            report.append("")

        return "\n".join(report)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="File Locking Optimizer")
    parser.add_argument(
        "--hours", type=int, default=24, help="Hours to analyze (default: 24)"
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save report to file",
    )

    args = parser.parse_args()

    optimizer = FileLockingOptimizer()
    report = optimizer.generate_optimization_report(args.hours)
    print(report)

    if args.save_report:
        from datetime import datetime

        report_file = Path(
            f"agent_workspaces/Agent-3/file_locking_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report)
        print(f"\n✅ Report saved: {report_file}")

    return 0


if __name__ == "__main__":
    exit(main())

