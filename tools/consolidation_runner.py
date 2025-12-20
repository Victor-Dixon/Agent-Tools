#!/usr/bin/env python3
"""
Consolidation Runner - Unified Consolidation Tool
=================================================

Single unified tool that consolidates functionality from:
- consolidation_orchestrator.py (orchestration)
- consolidation_execution_script.py (execution)
- consolidation_coordination_tool.py (coordination)
- consolidation_roadmap_plan.py (planning)

V2 Compliance: Centralized consolidation management
Author: V2 SWARM
License: MIT
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ConsolidationPlan:
    """Plan for consolidation operations."""
    plan_id: str
    description: str
    files_to_consolidate: List[str]
    target_file: str
    backup_required: bool = True
    risk_level: str = "MEDIUM"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ConsolidationRunner:
    """Unified consolidation runner."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize consolidation runner."""
        self.project_root = project_root or Path.cwd()
        self.src_path = self.project_root / "src"
        self.backup_path = self.project_root / "backups" / "consolidation"
        self.plans_path = self.project_root / "consolidation_plans"
        self.plans_path.mkdir(exist_ok=True)

    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze current project structure."""
        print("📊 Analyzing project structure...")

        py_files = list(self.src_path.rglob("*.py"))
        total_files = len(py_files)

        # Count by directory
        dir_counts = {}
        for py_file in py_files:
            rel_path = py_file.relative_to(self.src_path)
            top_dir = str(rel_path.parts[0]) if rel_path.parts else "root"
            dir_counts[top_dir] = dir_counts.get(top_dir, 0) + 1

        return {
            "total_python_files": total_files,
            "directory_breakdown": dir_counts,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def create_plan(
        self,
        plan_id: str,
        description: str,
        files: List[str],
        target: str
    ) -> ConsolidationPlan:
        """Create a consolidation plan."""
        plan = ConsolidationPlan(
            plan_id=plan_id,
            description=description,
            files_to_consolidate=files,
            target_file=target
        )

        # Save plan
        plan_file = self.plans_path / f"{plan_id}.json"
        with open(plan_file, 'w') as f:
            json.dump(plan.__dict__, f, indent=2)

        print(f"✅ Created plan: {plan_id}")
        return plan

    def execute_plan(self, plan_id: str, dry_run: bool = False) -> bool:
        """Execute a consolidation plan."""
        plan_file = self.plans_path / f"{plan_id}.json"
        if not plan_file.exists():
            print(f"❌ Plan not found: {plan_id}")
            return False

        with open(plan_file) as f:
            plan_data = json.load(f)

        print(f"🚀 Executing plan: {plan_id}")
        print(f"📋 Mode: {'DRY RUN' if dry_run else 'LIVE'}")

        if dry_run:
            print("\n📝 Would perform:")
            print(f"  - Backup {len(plan_data['files_to_consolidate'])} files")
            print(f"  - Consolidate into: {plan_data['target_file']}")
            return True

        # Create backup
        if plan_data['backup_required']:
            self._create_backup(plan_data['files_to_consolidate'])

        # Consolidate files
        self._consolidate_files(
            plan_data['files_to_consolidate'],
            plan_data['target_file']
        )

        print("✅ Plan executed successfully")
        return True

    def list_plans(self) -> List[str]:
        """List all available consolidation plans."""
        plans = [p.stem for p in self.plans_path.glob("*.json")]
        print(f"📋 Found {len(plans)} consolidation plans:")
        for plan in plans:
            print(f"  - {plan}")
        return plans

    def _create_backup(self, files: List[str]) -> None:
        """Create backup of files."""
        print("💾 Creating backup...")
        self.backup_path.mkdir(parents=True, exist_ok=True)

        for file_path in files:
            src_file = Path(file_path)
            if src_file.exists():
                backup_file = self.backup_path / src_file.name
                shutil.copy2(src_file, backup_file)

        print(f"✅ Backed up {len(files)} files to {self.backup_path}")

    def _consolidate_files(self, files: List[str], target: str) -> None:
        """Consolidate multiple files into one."""
        print(f"🔧 Consolidating {len(files)} files...")

        consolidated_content = [
            '"""',
            'Consolidated Module - Auto-generated',
            '====================================',
            '',
            f'Generated: {datetime.now().isoformat()}',
            f'Source files: {len(files)}',
            '"""',
            '',
            'from typing import Any, Dict, List, Optional',
            'import logging',
            '',
            'logger = logging.getLogger(__name__)',
            ''
        ]

        # Read and combine files
        for file_path in files:
            src_file = Path(file_path)
            if src_file.exists():
                try:
                    content = src_file.read_text(encoding='utf-8')
                    consolidated_content.append(f"\n# From: {src_file.name}\n")
                    # Skip docstrings and imports (basic)
                    lines = content.split('\n')
                    in_docstring = False
                    for line in lines:
                        if '"""' in line or "'''" in line:
                            in_docstring = not in_docstring
                            continue
                        if not in_docstring and not line.strip().startswith(('import ', 'from ')):
                            consolidated_content.append(line)
                except Exception as e:
                    print(f"⚠️ Warning: Could not process {file_path}: {e}")

        # Write consolidated file
        target_path = Path(target)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text('\n'.join(consolidated_content), encoding='utf-8')
        print(f"✅ Created consolidated file: {target}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Unified Consolidation Tool")
    parser.add_argument('--analyze', action='store_true', help='Analyze project structure')
    parser.add_argument('--create-plan', metavar='PLAN_ID', help='Create consolidation plan')
    parser.add_argument('--execute', metavar='PLAN_ID', help='Execute consolidation plan')
    parser.add_argument('--list-plans', action='store_true', help='List all plans')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--files', nargs='+', help='Files to consolidate')
    parser.add_argument('--target', help='Target consolidated file')
    parser.add_argument('--description', help='Plan description')

    args = parser.parse_args()

    runner = ConsolidationRunner()

    if args.analyze:
        stats = runner.analyze_structure()
        print(json.dumps(stats, indent=2))

    elif args.create_plan:
        if not args.files or not args.target:
            print("❌ Error: --files and --target required for plan creation")
            return 1
        runner.create_plan(
            plan_id=args.create_plan,
            description=args.description or "Consolidation plan",
            files=args.files,
            target=args.target
        )

    elif args.execute:
        runner.execute_plan(args.execute, dry_run=args.dry_run)

    elif args.list_plans:
        runner.list_plans()

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    exit(main())

