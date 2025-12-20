#!/usr/bin/env python3
"""
Auto-Validate Cycle V2 - Post-Cycle Validation Hook
====================================================

Automatically runs cycle v2 validator after agent completes cycle
and attaches score to status.json report.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-07
V2 Compliant: Yes
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def auto_validate_cycle_v2(agent_id: str, attach_to_status: bool = True) -> Optional[Dict[str, Any]]:
    """
    Auto-validate agent's cycle v2 and optionally attach to status.json.
    
    Args:
        agent_id: Agent ID (e.g., Agent-7)
        attach_to_status: Whether to attach validation report to status.json
        
    Returns:
        Validation report dictionary or None if validation failed
    """
    try:
        from tools.agent_cycle_v2_report_validator import CycleV2Validator
        
        status_path = project_root / "agent_workspaces" / agent_id / "status.json"
        
        if not status_path.exists():
            logger.warning(f"Status file not found: {status_path}")
            return None
        
        # Run validator
        validator = CycleV2Validator()
        report = validator.validate_status_json(status_path)
        
        # Attach to status.json if requested
        if attach_to_status:
            try:
                with open(status_path, "r", encoding="utf-8") as f:
                    status = json.load(f)
                
                # Add validation report to cycle_v2 section
                if "cycle_v2" not in status:
                    status["cycle_v2"] = {}
                
                status["cycle_v2"]["validation_report"] = {
                    "score": report["score"],
                    "max_score": report["max_score"],
                    "score_percent": report["score_percent"],
                    "grade": report["grade"],
                    "errors_count": report["errors_count"],
                    "warnings_count": report["warnings_count"],
                    "errors": report["errors"],
                    "warnings": report["warnings"],
                    "validated_at": json.dumps({"timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()})
                }
                
                with open(status_path, "w", encoding="utf-8") as f:
                    json.dump(status, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Validation report attached to {agent_id} status.json")
                logger.info(f"   Score: {report['score_percent']:.1f}% ({report['grade']})")
                
            except Exception as e:
                logger.error(f"Failed to attach validation report: {e}")
        
        return report
        
    except Exception as e:
        logger.error(f"Auto-validation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-validate Cycle V2 and attach score to status.json"
    )
    parser.add_argument(
        "--agent",
        type=str,
        required=True,
        help="Agent ID (e.g., Agent-7)"
    )
    parser.add_argument(
        "--no-attach",
        action="store_true",
        help="Don't attach validation report to status.json"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON report file"
    )
    
    args = parser.parse_args()
    
    # Run validation
    report = auto_validate_cycle_v2(
        args.agent,
        attach_to_status=not args.no_attach
    )
    
    if report:
        print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CYCLE V2 AUTO-VALIDATION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent: {args.agent}
Score: {report['score']:.2f} / {report['max_score']:.2f} ({report['score_percent']:.2f}%)
Grade: {report['grade']}

Errors: {report['errors_count']}
Warnings: {report['warnings_count']}
""")
        
        if report['errors']:
            print("❌ ERRORS:")
            for error in report['errors']:
                print(f"  • {error}")
        
        if report['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in report['warnings']:
                print(f"  • {warning}")
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {args.output}")
        
        sys.exit(0 if report['errors_count'] == 0 else 1)
    else:
        print("❌ Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()


