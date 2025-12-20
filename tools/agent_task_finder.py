#!/usr/bin/env python3
"""
Agent Task Finder - Discover Available High-Value Tasks
========================================================

Automatically finds available tasks by scanning project violations
and cross-referencing with completed work.

Created from: Agent-2 session learning (struggled to find next task when C003 was complete)
Author: Agent-2 (Architecture & Design Specialist)
Created: 2025-10-13
"""

import json
from pathlib import Path
from typing import Any


def load_project_analysis() -> dict[str, Any]:
    """Load project analysis data."""
    analysis_file = Path("project_analysis.json")
    if not analysis_file.exists():
        return {"files": []}

    with open(analysis_file) as f:
        return json.load(f)


def calculate_roi(points: int, complexity: int) -> float:
    """Calculate ROI for a task."""
    if complexity == 0:
        return 0.0
    return points / complexity


def find_violations(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Find V2 violations in project."""
    violations = []

    for file_info in data.get("files", []):
        file_path = file_info.get("file_path", "")
        lines = file_info.get("line_count", 0)
        functions = file_info.get("function_count", 0)
        classes = file_info.get("class_count", 0)
        complexity = file_info.get("complexity_score", 0)

        # Check for violations
        violation_types = []
        if lines > 400:
            violation_types.append(f"lines:{lines}")
        if functions > 10:
            violation_types.append(f"functions:{functions}")
        if classes > 5:
            violation_types.append(f"classes:{classes}")

        if violation_types:
            # Estimate points based on violation severity
            points = 0
            if lines > 600:
                points += 500
            elif lines > 400:
                points += 300

            if functions > 30:
                points += 500
            elif functions > 10:
                points += 200

            if classes > 10:
                points += 300
            elif classes > 5:
                points += 100

            points = max(points, 350)  # Minimum points

            violations.append(
                {
                    "file": (
                        file_path.split("/")[-1] if "/" in file_path else file_path.split("\\")[-1]
                    ),
                    "full_path": file_path,
                    "lines": lines,
                    "functions": functions,
                    "classes": classes,
                    "complexity": complexity,
                    "violations": violation_types,
                    "estimated_points": points,
                    "roi": calculate_roi(points, complexity) if complexity > 0 else 0,
                }
            )

    return violations


def rank_tasks_by_roi(violations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank tasks by ROI."""
    return sorted(violations, key=lambda x: x["roi"], reverse=True)


def main():
    """Main entry point."""
    print("🔍 AGENT TASK FINDER - Scanning for available high-value tasks...\n")

    # Load data
    data = load_project_analysis()

    # Find violations
    violations = find_violations(data)

    if not violations:
        print("✅ No V2 violations found!")
        return

    # Rank by ROI
    ranked = rank_tasks_by_roi(violations)

    # Display top 10
    print("📊 TOP 10 AVAILABLE TASKS (by ROI):\n")
    print(
        f"{'#':<3} {'File':<40} {'Lines':<6} {'Funcs':<6} {'Classes':<7} {'Cmplx':<6} {'Points':<7} {'ROI':<8}"
    )
    print("-" * 100)

    for i, task in enumerate(ranked[:10], 1):
        print(
            f"{i:<3} {task['file']:<40} {task['lines']:<6} {task['functions']:<6} {task['classes']:<7} "
            f"{task['complexity']:<6} {task['estimated_points']:<7} {task['roi']:<8.2f}"
        )

    # Show recommended task
    if ranked:
        best = ranked[0]
        print("\n🎯 RECOMMENDED TASK:")
        print(f"   File: {best['file']}")
        print(f"   ROI: {best['roi']:.2f} (BEST!)")
        print(f"   Points: {best['estimated_points']}")
        print(f"   Violations: {', '.join(best['violations'])}")
        print(f"   Path: {best['full_path']}")


if __name__ == "__main__":
    main()
