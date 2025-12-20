#!/usr/bin/env python3
"""
Unified Cleanup Tools - Consolidated Cleanup Operations
========================================================

<!-- SSOT Domain: infrastructure -->

Consolidates all cleanup and archive capabilities into a single unified tool.
Replaces 15+ individual cleanup/archive tools with modular cleanup system.

Cleanup Categories:
- archive: Archive operations
- delete: Delete operations
- cleanup: Cleanup operations
- disk: Disk space management

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-06
V2 Compliant: Yes (<400 lines)
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedCleanup:
    """Unified cleanup system consolidating all cleanup capabilities."""
    
    def __init__(self):
        """Initialize unified cleanup."""
        self.project_root = project_root
        
    def handle_archive(self, action: str = "tools", **kwargs) -> Dict[str, Any]:
        """Handle archive operations."""
        try:
            if action == "tools":
                from tools.archive_consolidated_tools import archive_tools
                result = archive_tools()
                return {
                    "category": "archive",
                    "action": "tools",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "communication":
                from tools.archive_communication_validation_tools import archive_communication
                result = archive_communication()
                return {
                    "category": "archive",
                    "action": "communication",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "deprecated":
                from tools.archive_deprecated_tools import archive_deprecated
                result = archive_deprecated()
                return {
                    "category": "archive",
                    "action": "deprecated",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "candidates":
                from tools.archive_consolidation_candidates import archive_candidates
                result = archive_candidates()
                return {
                    "category": "archive",
                    "action": "candidates",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "remaining":
                from tools.archive_remaining_candidates import archive_remaining
                result = archive_remaining()
                return {
                    "category": "archive",
                    "action": "remaining",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "merge-plans":
                from tools.archive_merge_plans import archive_plans
                result = archive_plans()
                return {
                    "category": "archive",
                    "action": "merge-plans",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "source-repos":
                from tools.archive_source_repos import archive_repos
                result = archive_repos()
                return {
                    "category": "archive",
                    "action": "source-repos",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "archive",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["tools", "communication", "deprecated", "candidates", "remaining", "merge-plans", "source-repos"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Archive operation failed: {e}")
            return {
                "category": "archive",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def handle_delete(self, action: str = "deprecated", **kwargs) -> Dict[str, Any]:
        """Handle delete operations."""
        try:
            if action == "deprecated":
                from tools.delete_deprecated_tools import delete_tools
                result = delete_tools()
                return {
                    "category": "delete",
                    "action": "deprecated",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "outdated-docs":
                from tools.delete_outdated_docs import delete_docs
                result = delete_docs()
                return {
                    "category": "delete",
                    "action": "outdated-docs",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "delete",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["deprecated", "outdated-docs"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Delete operation failed: {e}")
            return {
                "category": "delete",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def handle_cleanup(self, action: str = "obsolete-docs", **kwargs) -> Dict[str, Any]:
        """Handle cleanup operations."""
        try:
            if action == "obsolete-docs":
                from tools.cleanup_obsolete_docs import cleanup_docs
                result = cleanup_docs()
                return {
                    "category": "cleanup",
                    "action": "obsolete-docs",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "merge-dirs":
                from tools.cleanup_old_merge_directories import cleanup_dirs
                result = cleanup_dirs()
                return {
                    "category": "cleanup",
                    "action": "merge-dirs",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "venv":
                from tools.cleanup_superpowered_venv import cleanup_venv
                result = cleanup_venv()
                return {
                    "category": "cleanup",
                    "action": "venv",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "cleanup",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["obsolete-docs", "merge-dirs", "venv"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Cleanup operation failed: {e}")
            return {
                "category": "cleanup",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def handle_disk(self, action: str = "cleanup", **kwargs) -> Dict[str, Any]:
        """Handle disk space management operations."""
        try:
            if action == "cleanup":
                from tools.disk_space_cleanup import cleanup_disk
                result = cleanup_disk()
                return {
                    "category": "disk",
                    "action": "cleanup",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "optimize":
                from tools.disk_space_optimization import optimize_disk
                result = optimize_disk()
                return {
                    "category": "disk",
                    "action": "optimize",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "comprehensive":
                from tools.comprehensive_disk_cleanup import comprehensive_cleanup
                result = comprehensive_cleanup()
                return {
                    "category": "disk",
                    "action": "comprehensive",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "disk",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["cleanup", "optimize", "comprehensive"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Disk operation failed: {e}")
            return {
                "category": "disk",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for unified cleanup."""
    parser = argparse.ArgumentParser(
        description="Unified Cleanup Tools - Consolidated Cleanup Operations",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--category",
        choices=["archive", "delete", "cleanup", "disk", "all"],
        default="all",
        help="Category of cleanup operations"
    )
    
    parser.add_argument(
        "--action",
        type=str,
        help="Specific action to perform (varies by category)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    cleanup = UnifiedCleanup()
    results = []
    
    categories = ["archive", "delete", "cleanup", "disk"] if args.category == "all" else [args.category]
    
    for category in categories:
        action = args.action or {
            "archive": "tools",
            "delete": "deprecated",
            "cleanup": "obsolete-docs",
            "disk": "cleanup"
        }.get(category, "tools")
        
        if category == "archive":
            result = cleanup.handle_archive(action=action)
        elif category == "delete":
            result = cleanup.handle_delete(action=action)
        elif category == "cleanup":
            result = cleanup.handle_cleanup(action=action)
        elif category == "disk":
            result = cleanup.handle_disk(action=action)
        else:
            result = {
                "category": category,
                "error": "Unknown category",
                "timestamp": datetime.now().isoformat()
            }
        
        results.append(result)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            if "error" in result:
                print(f"❌ {result['category']}: {result['error']}")
            else:
                print(f"✅ {result['category']}: {result.get('action', 'completed')}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

