#!/usr/bin/env python3
"""
Consolidate Duplicate Tools - Agent-3
======================================

Merges duplicate tools identified by consolidation analysis.

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <400 lines
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


# Duplicate groups to consolidate
DUPLICATE_GROUPS = [
    {
        "group": "thea_code_review",
        "keep": "thea_code_review.py",
        "archive": ["test_thea_code_review.py"],
        "reason": "test_thea_code_review is a test wrapper, keep main tool",
    },
    {
        "group": "bump_button",
        "keep": "verify_bump_button.py",
        "archive": ["test_bump_button.py"],
        "reason": "verify_bump_button is more comprehensive, test_bump_button is redundant",
    },
    {
        "group": "repo_consolidation",
        "keep": "enhanced_repo_consolidation_analyzer.py",
        "archive": ["repo_consolidation_enhanced.py"],
        "reason": "enhanced_repo_consolidation_analyzer is more descriptive",
    },
    {
        "group": "compliance",
        "keep": "enforce_agent_compliance.py",
        "archive": ["send_agent3_assignment_direct.py", "setup_compliance_monitoring.py"],
        "reason": "enforce_agent_compliance is most comprehensive",
    },
]


def consolidate_duplicates(dry_run: bool = True) -> Dict[str, Any]:
    """Consolidate duplicate tools."""
    tools_dir = Path(__file__).parent
    archive_dir = tools_dir / "deprecated" / f"consolidated_{datetime.now().strftime('%Y-%m-%d')}"
    archive_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "archived": [],
        "not_found": [],
        "skipped": [],
        "errors": [],
    }

    print("🔧 Consolidating Duplicate Tools...")
    print("=" * 70)

    for group in DUPLICATE_GROUPS:
        print(f"\n📦 Group: {group['group']}")
        print(f"   Keep: {group['keep']}")
        print(f"   Archive: {', '.join(group['archive'])}")
        print(f"   Reason: {group['reason']}")

        # Check if keep file exists
        keep_path = tools_dir / group["keep"]
        if not keep_path.exists():
            print(f"   ⚠️  Keep file not found: {group['keep']}")
            results["not_found"].append(group["keep"])
            continue

        # Archive each duplicate
        for archive_name in group["archive"]:
            archive_path = tools_dir / archive_name

            if not archive_path.exists():
                print(f"   ⚠️  Archive file not found: {archive_name}")
                results["not_found"].append(archive_name)
                continue

            # Check if already archived
            if (archive_dir / archive_name).exists():
                print(f"   ⏭️  Already archived: {archive_name}")
                results["skipped"].append(archive_name)
                continue

            try:
                if not dry_run:
                    shutil.move(str(archive_path), str(archive_dir / archive_name))
                    print(f"   ✅ Archived: {archive_name}")
                else:
                    print(f"   📦 Would archive: {archive_name}")
                results["archived"].append(archive_name)
            except Exception as e:
                print(f"   ❌ Error archiving {archive_name}: {e}")
                results["errors"].append({"file": archive_name, "error": str(e)})

    print(f"\n📊 Summary:")
    print(f"   Archived: {len(results['archived'])}")
    print(f"   Not found: {len(results['not_found'])}")
    print(f"   Skipped: {len(results['skipped'])}")
    print(f"   Errors: {len(results['errors'])}")

    if not dry_run:
        print(f"\n✅ Archive directory: {archive_dir}")

    return results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Consolidate Duplicate Tools")
    parser.add_argument(
        "--execute", action="store_true", help="Actually archive files (default: dry-run)"
    )
    parser.add_argument(
        "--report", action="store_true", help="Save report to file"
    )

    args = parser.parse_args()

    results = consolidate_duplicates(dry_run=not args.execute)

    if args.report:
        from datetime import datetime
        import json

        report_file = Path(
            f"agent_workspaces/Agent-3/tools_consolidation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": not args.execute,
            "results": results,
            "duplicate_groups": DUPLICATE_GROUPS,
        }

        report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\n📄 Report saved: {report_file}")

    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    exit(main())

