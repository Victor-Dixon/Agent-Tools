#!/usr/bin/env python3
"""
Find Easy Documentation Deletions
==================================

Identifies redundant, duplicate, or easily deletable documentation files.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-12
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# Patterns for identifying redundant files
REDUNDANT_PATTERNS = {
    "summary": ["SUMMARY", "SUMMARY_", "_SUMMARY"],
    "report": ["REPORT", "REPORT_", "_REPORT"],
    "checkpoint": ["CHECKPOINT", "CHECKPOINT_", "_CHECKPOINT"],
    "status": ["STATUS", "STATUS_", "_STATUS"],
    "progress": ["PROGRESS", "PROGRESS_", "_PROGRESS"],
}

# Files that are clearly redundant (can be deleted)
EASY_DELETIONS = {
    "docs/agent-8": [
        # Multiple summary files - keep only DAILY_SUMMARY
        "AGENT8_QA_VALIDATION_SUMMARY_2025-12-12.md",  # Redundant with DAILY_SUMMARY
        "AGENT8_PROGRESS_REPORT_2025-12-12.md",  # Redundant with DAILY_SUMMARY
        "SESSION_SUMMARY_2025-12-12.md",  # Redundant with DAILY_SUMMARY
        
        # Multiple checkpoint files - keep only VALIDATION_CHECKPOINTS_SUMMARY
        "V2_VALIDATION_RUN_2025-12-12_15-13.md",  # Consolidated in CHECKPOINTS_SUMMARY
        "V2_VALIDATION_RUN_2025-12-12_17-44.md",  # Consolidated in CHECKPOINTS_SUMMARY
        "V2_VALIDATION_RUN_2025-12-12_19-23.md",  # Consolidated in CHECKPOINTS_SUMMARY
        
        # Redundant status/certificate files
        "QA_VALIDATION_PREPARATION_CERTIFICATE.md",  # Redundant with STATUS_REPORT
        "VALIDATION_SCRIPT_VERIFICATION.md",  # Small, can merge into README
        
        # Redundant reference files - keep only QUICK_REFERENCE
        "VALIDATION_WORKFLOW_DIAGRAM.md",  # Can merge into EXECUTION_GUIDE
    ]
}

# Files to keep (important)
KEEP_FILES = {
    "docs/agent-8": [
        "README.md",  # Navigation guide
        "QA_VALIDATION_CHECKLIST_2025-12-12.md",  # Core checklist
        "V2_COMPLIANCE_VALIDATION_2025-12-12.md",  # Baseline data
        "REFACTORING_READINESS_ASSESSMENT_2025-12-12.md",  # Refactoring strategies
        "COORDINATION_STATUS_REPORT_2025-12-12.md",  # Coordination info
        "DAILY_SUMMARY_2025-12-12.md",  # Main summary (keep one)
        "VALIDATION_CHECKPOINTS_SUMMARY.md",  # Consolidated checkpoints
        "QA_VALIDATION_QUICK_REFERENCE.md",  # Quick reference (keep one)
        "VALIDATION_EXECUTION_GUIDE.md",  # Execution guide
        "ARTIFACT_INDEX_2025-12-12.md",  # Artifact catalog
        "VALIDATION_STATUS_REPORT_2025-12-12.md",  # Current status
        "VALIDATION_METRICS_DASHBOARD.md",  # Metrics tracking
        "CODE_COMMENT_MISMATCH_QA_VALIDATION_2025-12-12.md",  # QA validation
    ]
}


def analyze_documentation(base_path: Path) -> Dict[str, List[Dict]]:
    """Analyze documentation files and identify easy deletions."""
    results = {
        "easy_deletions": [],
        "potential_consolidations": [],
        "keep": [],
        "unknown": [],
    }
    
    for dir_path, files_to_delete in EASY_DELETIONS.items():
        full_dir = base_path / dir_path
        if not full_dir.exists():
            continue
            
        for file_name in files_to_delete:
            file_path = full_dir / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                results["easy_deletions"].append({
                    "path": str(file_path.relative_to(base_path)),
                    "size": size,
                    "reason": "Redundant/duplicate content",
                })
    
    # Check for files not in keep list
    for dir_path, keep_files in KEEP_FILES.items():
        full_dir = base_path / dir_path
        if not full_dir.exists():
            continue
            
        for md_file in full_dir.glob("*.md"):
            file_name = md_file.name
            if file_name not in keep_files and file_name not in [f.split("/")[-1] for f in EASY_DELETIONS.get(dir_path, [])]:
                size = md_file.stat().st_size
                results["unknown"].append({
                    "path": str(md_file.relative_to(base_path)),
                    "size": size,
                })
    
    return results


def main():
    """Main entry point."""
    base_path = Path.cwd()
    results = analyze_documentation(base_path)
    
    print("=" * 60)
    print("EASY DOCUMENTATION DELETIONS ANALYSIS")
    print("=" * 60)
    print()
    
    # Easy deletions
    if results["easy_deletions"]:
        total_size = sum(f["size"] for f in results["easy_deletions"])
        print(f"✅ EASY DELETIONS ({len(results['easy_deletions'])} files, {total_size:,} bytes):")
        print()
        for item in results["easy_deletions"]:
            print(f"  - {item['path']}")
            print(f"    Size: {item['size']:,} bytes")
            print(f"    Reason: {item['reason']}")
            print()
    else:
        print("✅ No easy deletions identified")
        print()
    
    # Unknown files
    if results["unknown"]:
        print(f"⚠️  UNKNOWN FILES ({len(results['unknown'])} files):")
        print("   (Not in keep list, not marked for deletion - review manually)")
        print()
        for item in results["unknown"]:
            print(f"  - {item['path']} ({item['size']:,} bytes)")
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Easy Deletions: {len(results['easy_deletions'])} files")
    print(f"Total Size to Delete: {sum(f['size'] for f in results['easy_deletions']):,} bytes")
    print(f"Unknown Files: {len(results['unknown'])} files")
    print()
    
    # Generate deletion commands
    if results["easy_deletions"]:
        print("=" * 60)
        print("DELETION COMMANDS")
        print("=" * 60)
        print()
        for item in results["easy_deletions"]:
            print(f"git rm {item['path']}")
        print()


if __name__ == "__main__":
    main()

