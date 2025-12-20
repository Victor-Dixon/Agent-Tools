#!/usr/bin/env python3
"""
🐝 CAPTAIN WORKSPACE CLEANUP TOOL
==================================

Cleans and organizes Agent-4's workspace by archiving old files
and organizing by date/category.

V2 Compliance: <300 lines, single responsibility
Author: Agent-1 (Captain Support)
"""

import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CaptainWorkspaceCleanup:
    """Cleans and organizes Captain workspace."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the cleanup tool."""
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = project_root
        self.captain_workspace = project_root / "agent_workspaces" / "Agent-4"
        self.archive_dir = self.captain_workspace / "archive"
        self.archive_old = self.archive_dir / "old_files"

    def should_archive(self, file_path: Path, days_old: int = 30) -> bool:
        """Check if file should be archived."""
        if not file_path.is_file():
            return False
        
        # Keep status.json and important config files
        if file_path.name in ["status.json", "HARD_ONBOARDING_MESSAGE.md"]:
            return False
        
        # Keep recent reports
        if file_path.suffix == ".md" and "REPORT" in file_path.name.upper():
            # Check if file is older than threshold
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                age = datetime.now() - mtime
                return age.days > days_old
            except:
                return False
        
        # Archive old markdown files
        if file_path.suffix == ".md":
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                age = datetime.now() - mtime
                return age.days > days_old
            except:
                return False
        
        return False

    def archive_file(self, file_path: Path) -> bool:
        """Archive a file to archive directory."""
        try:
            if not self.archive_old.exists():
                self.archive_old.mkdir(parents=True, exist_ok=True)
            
            # Create date-based subdirectory
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            date_dir = self.archive_old / mtime.strftime("%Y-%m")
            date_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file
            archive_path = date_dir / file_path.name
            if archive_path.exists():
                # Add timestamp if duplicate
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_path = date_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            file_path.rename(archive_path)
            logger.info(f"✅ Archived: {file_path.name} → {archive_path.relative_to(self.captain_workspace)}")
            return True
        except Exception as e:
            logger.error(f"❌ Error archiving {file_path.name}: {e}")
            return False

    def cleanup_workspace(self, days_old: int = 30, dry_run: bool = False) -> dict[str, Any]:
        """Clean up workspace by archiving old files."""
        results = {
            "total_files": 0,
            "archived": 0,
            "kept": 0,
            "errors": [],
        }
        
        if not self.captain_workspace.exists():
            logger.error(f"❌ Captain workspace not found: {self.captain_workspace}")
            return results
        
        # Process files in workspace root (not subdirectories)
        for file_path in self.captain_workspace.iterdir():
            if file_path.is_file():
                results["total_files"] += 1
                
                if self.should_archive(file_path, days_old):
                    if not dry_run:
                        if self.archive_file(file_path):
                            results["archived"] += 1
                        else:
                            results["errors"].append(file_path.name)
                    else:
                        results["archived"] += 1
                        logger.info(f"📦 Would archive: {file_path.name}")
                else:
                    results["kept"] += 1
        
        return results

    def generate_cleanup_report(self, results: dict[str, Any]) -> str:
        """Generate cleanup report."""
        report = f"""# 🧹 CAPTAIN WORKSPACE CLEANUP REPORT

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- **Total Files**: {results['total_files']}
- **Archived**: {results['archived']}
- **Kept**: {results['kept']}
- **Errors**: {len(results['errors'])}

## Archive Location
Files archived to: `agent_workspaces/Agent-4/archive/old_files/`

"""
        if results["errors"]:
            report += "## Errors\n"
            for error in results["errors"]:
                report += f"- {error}\n"
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Captain Workspace Cleanup")
    parser.add_argument("--days", type=int, default=30, help="Archive files older than N days (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be archived without archiving")
    parser.add_argument("--report", action="store_true", help="Generate summary report")
    
    args = parser.parse_args()
    
    cleanup = CaptainWorkspaceCleanup()
    
    logger.info(f"🧹 Starting workspace cleanup (days_old={args.days}, dry_run={args.dry_run})")
    results = cleanup.cleanup_workspace(days_old=args.days, dry_run=args.dry_run)
    
    if args.report:
        report = cleanup.generate_cleanup_report(results)
        print(report)
        
        # Save report
        report_path = cleanup.captain_workspace / "workspace_cleanup_report.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"\n✅ Report saved to: {report_path}")
    else:
        print(f"\n📊 Processed {results['total_files']} files")
        print(f"📦 Archived {results['archived']} files")
        print(f"✅ Kept {results['kept']} files")
        if results['errors']:
            print(f"❌ {len(results['errors'])} errors")


if __name__ == "__main__":
    main()





