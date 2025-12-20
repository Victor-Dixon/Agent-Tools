#!/usr/bin/env python3
"""
Functionality Comparison
========================

Compares current functionality signature with baseline.

Author: Agent-1 (Integration & Core Systems Specialist)
V2 Compliant: <300 lines
"""

import json
from pathlib import Path
from typing import Any, Dict, List


class FunctionalityComparison:
    """Compare functionality signatures with baseline."""

    def __init__(self, baseline_file: Path):
        """Initialize comparison with baseline file path."""
        self.baseline_file = baseline_file

    def save_baseline(self, signature: Dict[str, Any]) -> None:
        """Save functionality baseline."""
        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_file, "w", encoding="utf-8") as f:
            json.dump(signature, f, indent=2)

    def load_baseline(self) -> Dict[str, Any] | None:
        """Load functionality baseline."""
        if not self.baseline_file.exists():
            return None

        try:
            with open(self.baseline_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def compare_with_baseline(self, current_signature: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current signature with baseline."""
        baseline = self.load_baseline()
        if not baseline:
            return {
                "risk_assessment": "UNKNOWN",
                "functions_lost": [],
                "functions_added": [],
                "files_changed": [],
                "new_functions": [],
            }

        # Compare functions
        baseline_funcs = {
            (f["name"], f["file"]) for f in baseline.get("functions", [])
        }
        current_funcs = {
            (f["name"], f["file"]) for f in current_signature.get("functions", [])
        }

        functions_lost = list(baseline_funcs - current_funcs)
        functions_added = list(current_funcs - baseline_funcs)

        # Compare classes
        baseline_classes = {
            (c["name"], c["file"]) for c in baseline.get("classes", [])
        }
        current_classes = {
            (c["name"], c["file"]) for c in current_signature.get("classes", [])
        }

        classes_lost = list(baseline_classes - current_classes)
        classes_added = list(current_classes - baseline_classes)

        # Determine risk assessment
        total_lost = len(functions_lost) + len(classes_lost)
        if total_lost > 10:
            risk = "HIGH"
        elif total_lost > 0:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        # Files changed
        baseline_files = set(baseline.get("files", []))
        current_files = set(current_signature.get("files", []))
        files_changed = list(baseline_files.symmetric_difference(current_files))

        return {
            "risk_assessment": risk,
            "functions_lost": [f"{name} ({file})" for name, file in functions_lost],
            "classes_lost": [f"{name} ({file})" for name, file in classes_lost],
            "functions_added": [f"{name} ({file})" for name, file in functions_added],
            "classes_added": [f"{name} ({file})" for name, file in classes_added],
            "files_changed": files_changed,
            "new_functions": [f"{name} ({file})" for name, file in functions_added],
        }

