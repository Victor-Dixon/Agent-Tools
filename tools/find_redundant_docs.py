#!/usr/bin/env python3
"""
Find Redundant Documentation Files
==================================

Identifies documentation files that are duplicates, redundant, or can be easily deleted.

Checks for:
1. Duplicate files (same content, different names)
2. Multiple validation artifacts for same work
3. Old/outdated documentation
4. Temporary/working files that should be cleaned up
"""

import hashlib
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
from datetime import datetime

# Directories to analyze
DOC_DIRS = [
    "docs",
    "artifacts",
    "devlogs"
]

# Patterns that indicate redundant files
REDUNDANT_PATTERNS = [
    "*_FINAL_*.md",
    "*_FINAL_*.txt",
    "*_COMPLETE_*.md",
    "*_COMPLETE_*.txt",
    "*_VALIDATION_*.md",
    "*_VALIDATION_*.txt",
    "*_SUMMARY_*.md",
    "*_SUMMARY_*.txt",
    "*_DELTA_*.md",
    "*_DELTA_*.txt",
    "*_CERTIFICATE_*.txt",
    "*_RECORD_*.txt",
]

# Files to keep (important documentation)
KEEP_FILES = {
    "docs/README.md",
    "docs/AGENT_OPERATING_CYCLE_WORKFLOW.md",
    "docs/CODE_OF_CONDUCT.md",
    "docs/CONFIGURATION.md",
}


def get_file_hash(file_path: Path) -> str:
    """Get MD5 hash of file content."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def find_duplicates(root_dir: Path) -> Dict[str, List[Path]]:
    """Find duplicate files by content hash."""
    hash_map = defaultdict(list)
    
    for doc_dir in DOC_DIRS:
        dir_path = root_dir / doc_dir
        if not dir_path.exists():
            continue
            
        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.md', '.txt', '.json']:
                if str(file_path.relative_to(root_dir)) in KEEP_FILES:
                    continue
                file_hash = get_file_hash(file_path)
                if file_hash:
                    hash_map[file_hash].append(file_path)
    
    # Return only duplicates (2+ files with same hash)
    return {h: files for h, files in hash_map.items() if len(files) > 1}


def find_redundant_by_pattern(root_dir: Path) -> List[Path]:
    """Find files matching redundant patterns."""
    redundant = []
    
    for doc_dir in DOC_DIRS:
        dir_path = root_dir / doc_dir
        if not dir_path.exists():
            continue
            
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(root_dir))
                if rel_path in KEEP_FILES:
                    continue
                    
                # Check if matches redundant pattern
                for pattern in REDUNDANT_PATTERNS:
                    if file_path.match(pattern):
                        redundant.append(file_path)
                        break
    
    return redundant


def analyze_agent_artifacts(root_dir: Path) -> Dict[str, List[Path]]:
    """Group artifacts by agent and task to find duplicates."""
    artifacts = defaultdict(list)
    
    artifacts_dir = root_dir / "artifacts"
    if not artifacts_dir.exists():
        return {}
    
    for file_path in artifacts_dir.glob("*"):
        if file_path.is_file():
            name = file_path.name
            # Extract agent and date
            if "agent-7" in name.lower() or "agent7" in name.upper():
                artifacts["Agent-7"].append(file_path)
            elif "agent-5" in name.lower() or "agent5" in name.upper():
                artifacts["Agent-5"].append(file_path)
            elif "agent-2" in name.lower() or "agent2" in name.upper():
                artifacts["Agent-2"].append(file_path)
            elif "agent-1" in name.lower() or "agent1" in name.upper():
                artifacts["Agent-1"].append(file_path)
    
    return artifacts


def generate_deletion_report(root_dir: Path) -> str:
    """Generate report of files that can be deleted."""
    duplicates = find_duplicates(root_dir)
    redundant = find_redundant_by_pattern(root_dir)
    agent_artifacts = analyze_agent_artifacts(root_dir)
    
    report = []
    report.append("# Redundant Documentation Analysis")
    report.append(f"\n**Date**: {datetime.now().strftime('%Y-%m-%d')}")
    report.append("\n## Summary\n")
    
    # Duplicates
    total_duplicate_files = sum(len(files) - 1 for files in duplicates.values())
    report.append(f"- **Duplicate files**: {len(duplicates)} groups, {total_duplicate_files} files can be deleted")
    report.append(f"- **Redundant pattern matches**: {len(redundant)} files")
    
    # Agent-7 artifacts (many CI/CD validation files)
    agent7_count = len(agent_artifacts.get("Agent-7", []))
    report.append(f"- **Agent-7 artifacts**: {agent7_count} files (many CI/CD validation duplicates)")
    
    report.append("\n## Recommended Deletions\n")
    
    # Agent-7 CI/CD duplicates
    report.append("### Agent-7 CI/CD Validation Artifacts (Keep 1-2, delete rest)")
    agent7_files = agent_artifacts.get("Agent-7", [])
    ci_cd_files = [f for f in agent7_files if "ci_cd" in f.name.lower() or "CI_CD" in f.name]
    if ci_cd_files:
        report.append(f"\n**Found {len(ci_cd_files)} CI/CD validation files. Recommended to keep:**")
        report.append("- `artifacts/AGENT7_CI_CD_WORK_COMPLETE_2025-12-12.txt` (most comprehensive)")
        report.append("\n**Can delete:**")
        for f in sorted(ci_cd_files):
            if "WORK_COMPLETE" not in f.name:
                report.append(f"- `{f.relative_to(root_dir)}`")
    
    # Duplicates
    if duplicates:
        report.append("\n### Duplicate Files (Keep first, delete rest)")
        for file_hash, files in list(duplicates.items())[:10]:  # Show first 10
            report.append(f"\n**Hash {file_hash[:8]}... ({len(files)} files):**")
            # Keep the shortest path, delete others
            files_sorted = sorted(files, key=lambda p: (len(str(p)), str(p)))
            keep = files_sorted[0]
            report.append(f"- KEEP: `{keep.relative_to(root_dir)}`")
            for f in files_sorted[1:]:
                report.append(f"- DELETE: `{f.relative_to(root_dir)}`")
    
    # Redundant patterns
    if redundant:
        report.append("\n### Files Matching Redundant Patterns")
        report.append(f"\n**{len(redundant)} files match redundant patterns:**")
        for f in sorted(redundant)[:20]:  # Show first 20
            report.append(f"- `{f.relative_to(root_dir)}`")
    
    return "\n".join(report)


if __name__ == "__main__":
    root_dir = Path(__file__).parent.parent
    report = generate_deletion_report(root_dir)
    
    output_file = root_dir / "artifacts" / "REDUNDANT_DOCS_ANALYSIS_2025-12-12.md"
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(report)
    
    print(report)
    print(f"\n\nReport saved to: {output_file}")

