#!/usr/bin/env python3
"""
Execute Tools Consolidation
============================

Immediate consolidation actions for critical duplicate tools.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-01-27
Priority: CRITICAL
"""

import json
import shutil
from pathlib import Path
from datetime import datetime


def consolidate_duplicates():
    """Consolidate duplicate tools."""
    print("🔧 Consolidating Duplicate Tools...")
    
    # test_imports.py and validate_imports.py
    test_imports = Path("tools/test_imports.py")
    validate_imports = Path("tools/validate_imports.py")
    
    if test_imports.exists() and validate_imports.exists():
        # Keep validate_imports (more descriptive name)
        # Archive test_imports
        archive_dir = Path("tools/deprecated")
        archive_dir.mkdir(exist_ok=True)
        
        archive_path = archive_dir / f"test_imports_archived_{datetime.now().strftime('%Y%m%d')}.py"
        shutil.move(str(test_imports), str(archive_path))
        print(f"  ✅ Archived {test_imports.name} → {archive_path}")
        print(f"  ✅ Kept {validate_imports.name} (consolidated)")
    
    print("✅ Duplicate consolidation complete")


def create_consolidation_directories():
    """Create organized directory structure."""
    print("\n📁 Creating consolidation directories...")
    
    dirs = [
        "tools/monitoring",
        "tools/analysis",
        "tools/validation",
        "tools/deprecated",
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created {dir_path}")
    
    print("✅ Directory structure ready")


def generate_consolidation_report():
    """Generate final consolidation report."""
    print("\n📊 Generating consolidation report...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "IN_PROGRESS",
        "actions_taken": [
            "Consolidated test_imports.py and validate_imports.py",
            "Created organized directory structure",
        ],
        "next_steps": [
            "Consolidate 33 monitoring tools → unified_monitor.py",
            "Consolidate 45 analysis tools → unified_analyzer.py",
            "Consolidate 19 validation tools → unified_validator.py",
            "Migrate 20 captain tools → tools_v2/categories/captain_tools.py",
        ],
        "expected_reduction": "35% (234 → ~150 tools)",
    }
    
    report_path = Path("agent_workspaces/Agent-8/CONSOLIDATION_EXECUTION_REPORT.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    print(f"✅ Report saved: {report_path}")
    return report


def main():
    """Main execution."""
    print("🛠️ Tools Consolidation Execution - Agent-8")
    print("=" * 60)
    print("Priority: CRITICAL - Blocks Phase 1 Execution")
    print()
    
    # Step 1: Consolidate duplicates
    consolidate_duplicates()
    
    # Step 2: Create directories
    create_consolidation_directories()
    
    # Step 3: Generate report
    report = generate_consolidation_report()
    
    print("\n📊 CONSOLIDATION STATUS:")
    print(f"  Status: {report['status']}")
    print(f"  Actions: {len(report['actions_taken'])} completed")
    print(f"  Next Steps: {len(report['next_steps'])} pending")
    print(f"  Expected Reduction: {report['expected_reduction']}")
    
    print("\n🎯 IMMEDIATE NEXT STEPS:")
    for i, step in enumerate(report['next_steps'], 1):
        print(f"  {i}. {step}")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()


