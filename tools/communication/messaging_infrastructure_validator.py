#!/usr/bin/env python3
"""
Unified Messaging Infrastructure Validator
===========================================

Consolidates messaging infrastructure validation tools.
Combines functionality from check_queue_status.py and queue validation tools.

Features:
- Message queue health checks
- Queue persistence validation
- Messaging infrastructure connectivity
- Queue status monitoring

V2 Compliance: ≤300 lines, ≤200 lines/class, ≤30 lines/function
Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Task: Phase 2 Tools Consolidation - Communication Validation
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.core.message_queue_persistence import FileQueuePersistence
    HAS_QUEUE_PERSISTENCE = True
except ImportError:
    HAS_QUEUE_PERSISTENCE = False


class MessagingInfrastructureValidator:
    """Unified messaging infrastructure validation."""

    def __init__(self, queue_file: Optional[Path] = None):
        """Initialize validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        if queue_file is None:
            queue_file = Path("message_queue/queue.json")
        self.queue_file = queue_file
        self.persistence = None
        if HAS_QUEUE_PERSISTENCE:
            try:
                self.persistence = FileQueuePersistence(queue_file)
            except Exception as e:
                self.errors.append(f"Failed to initialize queue persistence: {e}")

    def check_queue_status(self) -> Dict[str, Any]:
        """Check message queue status."""
        if not self.persistence:
            return {
                "valid": False,
                "error": "Queue persistence not available",
                "status_counts": {},
            }

        try:
            entries = self.persistence.load_entries()
            status_counts = {}
            for entry in entries:
                status = getattr(entry, 'status', 'UNKNOWN')
                status_counts[status] = status_counts.get(status, 0) + 1

            pending = status_counts.get('PENDING', 0)
            processing = status_counts.get('PROCESSING', 0)
            failed = status_counts.get('FAILED', 0)

            if failed > 0:
                self.errors.append(f"{failed} messages in FAILED status")
            if processing > 10:
                self.warnings.append(f"{processing} messages processing (may be stuck)")

            return {
                "valid": len(self.errors) == 0,
                "total_messages": len(entries),
                "status_counts": status_counts,
                "pending": pending,
                "processing": processing,
                "delivered": status_counts.get('DELIVERED', 0),
                "failed": failed,
            }
        except Exception as e:
            self.errors.append(f"Error checking queue status: {e}")
            return {
                "valid": False,
                "error": str(e),
                "status_counts": {},
            }

    def validate_queue_file(self) -> bool:
        """Validate queue file exists and is readable."""
        if not self.queue_file.exists():
            self.errors.append(f"Queue file not found: {self.queue_file}")
            return False

        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, (list, dict)):
                self.errors.append("Queue file has invalid format")
                return False
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"Queue file is not valid JSON: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading queue file: {e}")
            return False

    def validate_queue_directory(self) -> bool:
        """Validate queue directory exists."""
        queue_dir = self.queue_file.parent
        if not queue_dir.exists():
            self.warnings.append(f"Queue directory does not exist: {queue_dir}")
            return False
        return True

    def validate_infrastructure_health(self) -> Dict[str, Any]:
        """Validate overall messaging infrastructure health."""
        queue_dir_valid = self.validate_queue_directory()
        queue_file_valid = self.validate_queue_file()
        queue_status = self.check_queue_status()

        return {
            "valid": len(self.errors) == 0 and queue_dir_valid and queue_file_valid,
            "queue_directory": queue_dir_valid,
            "queue_file": queue_file_valid,
            "queue_status": queue_status,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def print_report(self) -> None:
        """Print validation report using SSOT utility."""
        from src.core.utils.validation_utils import print_validation_report
        print_validation_report(
            errors=self.errors,
            warnings=self.warnings,
        )


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified messaging infrastructure validator"
    )
    parser.add_argument(
        "--queue-file", type=Path,
        default=Path("message_queue/queue.json"),
        help="Path to queue file"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Check queue status"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()
    validator = MessagingInfrastructureValidator(args.queue_file)

    if args.status:
        results = validator.validate_infrastructure_health()
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            queue_status = results.get("queue_status", {})
            print("📊 Queue Status:")
            print(f"  Total messages: {queue_status.get('total_messages', 0)}")
            status_counts = queue_status.get("status_counts", {})
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            validator.print_report()
        return 0 if results["valid"] else 1
    else:
        results = validator.validate_infrastructure_health()
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            validator.print_report()
        return 0 if results["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())


