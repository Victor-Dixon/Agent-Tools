#!/usr/bin/env python3
"""
Agent Cycle v2 Report Validator
===============================

Machine-gradable validation of agent cycle reports.
Validates status.json against v2 cycle schema and provides scoring.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-07
V2 Compliant: Yes
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CycleV2Validator:
    """Validates agent cycle v2 reports against schema and best practices."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.score: float = 0.0
        self.max_score: float = 100.0
        
    def validate_status_json(self, status_path: Path) -> Dict[str, Any]:
        """
        Validate status.json against v2 cycle schema.
        
        Args:
            status_path: Path to status.json file
            
        Returns:
            Validation report with score and issues
        """
        self.errors = []
        self.warnings = []
        self.score = 0.0
        
        if not status_path.exists():
            self.errors.append(f"Status file not found: {status_path}")
            return self._generate_report()
        
        try:
            with open(status_path, "r", encoding="utf-8") as f:
                status = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return self._generate_report()
        
        # Validate required fields
        self._validate_required_fields(status)
        
        # Validate cycle_v2 if present
        if "cycle_v2" in status:
            self._validate_cycle_v2(status["cycle_v2"])
        else:
            self.warnings.append("cycle_v2 section missing (not using v2 cycle)")
        
        return self._generate_report()
    
    def _validate_required_fields(self, status: Dict[str, Any]) -> None:
        """Validate required top-level fields."""
        required = ["agent_id", "agent_name", "status", "last_updated", 
                    "current_mission", "mission_priority"]
        
        for field in required:
            if field not in status:
                self.errors.append(f"Missing required field: {field}")
            else:
                self.score += 2.0  # 2 points per required field
    
    def _validate_cycle_v2(self, cycle: Dict[str, Any]) -> None:
        """Validate cycle_v2 section."""
        # Required fields
        required = ["cycle_id", "wip_limit", "current_wip", "micro_plan", "dod", "dod_defined"]
        for field in required:
            if field not in cycle:
                self.errors.append(f"Missing required cycle_v2 field: {field}")
            else:
                self.score += 5.0
        
        # WIP limit validation
        if cycle.get("wip_limit") != 1:
            self.errors.append("WIP limit must be 1")
        else:
            self.score += 10.0
        
        if cycle.get("current_wip", 0) > 1:
            self.errors.append(f"Current WIP ({cycle.get('current_wip')}) exceeds limit of 1")
        else:
            self.score += 10.0
        
        # Micro-plan validation
        micro_plan = cycle.get("micro_plan", [])
        if not isinstance(micro_plan, list):
            self.errors.append("micro_plan must be an array")
        elif len(micro_plan) > 3:
            self.warnings.append(f"micro_plan has {len(micro_plan)} items (max 3 recommended)")
        elif len(micro_plan) == 0:
            self.errors.append("micro_plan is empty")
        else:
            self.score += 10.0
        
        # DoD validation
        dod = cycle.get("dod", "")
        if not dod or len(dod.strip()) == 0:
            self.errors.append("DoD is empty")
        else:
            dod_lines = len(dod.strip().split('\n'))
            if dod_lines > 3:
                self.warnings.append(f"DoD has {dod_lines} lines (max 3 recommended)")
            self.score += 10.0
        
        # SSOT boundaries
        if "ssot_boundaries" in cycle:
            if isinstance(cycle["ssot_boundaries"], list) and len(cycle["ssot_boundaries"]) > 0:
                self.score += 5.0
            else:
                self.warnings.append("ssot_boundaries is empty")
        
        # V2 compliance check
        if cycle.get("v2_compliance_checked", False):
            self.score += 5.0
        else:
            self.warnings.append("v2_compliance_checked is false or missing")
        
        # Execution burst validation
        if "execution_burst" in cycle:
            burst = cycle["execution_burst"]
            if burst.get("smallest_viable_change"):
                self.score += 5.0
            if burst.get("scope_expanded", False):
                if not burst.get("subtasks_created"):
                    self.warnings.append("Scope expanded but no subtasks created")
        
        # Mid-cycle checkpoint
        if "mid_cycle_checkpoint" in cycle:
            checkpoint = cycle["mid_cycle_checkpoint"]
            if checkpoint.get("checked", False):
                self.score += 5.0
                if not checkpoint.get("aligned_with_dod", True):
                    self.warnings.append("Mid-cycle checkpoint: not aligned with DoD")
                if not checkpoint.get("within_ssot", True):
                    self.warnings.append("Mid-cycle checkpoint: not within SSOT")
                if not checkpoint.get("within_v2", True):
                    self.warnings.append("Mid-cycle checkpoint: not within V2")
        
        # Validation section
        if "validation" in cycle:
            validation = cycle["validation"]
            if validation.get("tests_run") or validation.get("lint_run") or validation.get("verification_run"):
                self.score += 10.0
            if validation.get("evidence"):
                evidence = validation["evidence"]
                if evidence.get("commands") or evidence.get("output_summary"):
                    self.score += 5.0
        
        # Reporting section
        if "reporting" in cycle:
            reporting = cycle["reporting"]
            required_reporting = ["artifacts_changed", "validation_evidence", 
                                "measurable_result", "next_action"]
            for field in required_reporting:
                if field in reporting and reporting[field]:
                    self.score += 5.0
                else:
                    self.errors.append(f"Missing required reporting field: {field}")
        
        # Documentation
        if "documentation" in cycle:
            doc = cycle["documentation"]
            if doc.get("status_json_updated", False):
                self.score += 5.0
            if doc.get("discord_devlog_posted", False):
                self.score += 5.0
        
        # Success metrics
        if "success_metrics" in cycle:
            metrics = cycle["success_metrics"]
            if metrics.get("output_delivered", False):
                self.score += 10.0
            if metrics.get("validation_evidence_included", False):
                self.score += 5.0
            if metrics.get("zero_drift", True):
                self.score += 5.0
            if metrics.get("wip_respected", True):
                self.score += 5.0
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        score_percent = (self.score / self.max_score) * 100 if self.max_score > 0 else 0
        
        return {
            "score": round(self.score, 2),
            "max_score": self.max_score,
            "score_percent": round(score_percent, 2),
            "errors": self.errors,
            "warnings": self.warnings,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "grade": self._calculate_grade(score_percent)
        }
    
    def _calculate_grade(self, score_percent: float) -> str:
        """Calculate letter grade."""
        if score_percent >= 90:
            return "A"
        elif score_percent >= 80:
            return "B"
        elif score_percent >= 70:
            return "C"
        elif score_percent >= 60:
            return "D"
        else:
            return "F"


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate agent cycle v2 reports"
    )
    parser.add_argument(
        "--agent",
        type=str,
        required=True,
        help="Agent ID (e.g., Agent-7)"
    )
    parser.add_argument(
        "--status-file",
        type=str,
        help="Path to status.json (default: agent_workspaces/{agent}/status.json)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON report file"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "human"],
        default="human",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    # Determine status file path
    if args.status_file:
        status_path = Path(args.status_file)
    else:
        status_path = project_root / "agent_workspaces" / args.agent / "status.json"
    
    # Validate
    validator = CycleV2Validator()
    report = validator.validate_status_json(status_path)
    
    # Output
    if args.format == "json":
        output = json.dumps(report, indent=2)
    else:
        output = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT CYCLE V2 VALIDATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent: {args.agent}
Status File: {status_path}

SCORE: {report['score']:.2f} / {report['max_score']:.2f} ({report['score_percent']:.2f}%)
GRADE: {report['grade']}

Errors: {report['errors_count']}
Warnings: {report['warnings_count']}

"""
        if report['errors']:
            output += "\n❌ ERRORS:\n"
            for error in report['errors']:
                output += f"  • {error}\n"
        
        if report['warnings']:
            output += "\n⚠️  WARNINGS:\n"
            for warning in report['warnings']:
                output += f"  • {warning}\n"
        
        if not report['errors'] and not report['warnings']:
            output += "\n✅ No issues found!\n"
    
    print(output)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            if args.format == "json":
                f.write(json.dumps(report, indent=2))
            else:
                f.write(output)
        logger.info(f"Report saved to {args.output}")
    
    # Exit code based on errors
    sys.exit(1 if report['errors_count'] > 0 else 0)


if __name__ == "__main__":
    main()


