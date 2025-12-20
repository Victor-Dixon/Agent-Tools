#!/usr/bin/env python3
"""
Analyze Project Scan Results - Consolidation Opportunities
==========================================================

Analyzes project_analysis.json, test_analysis.json, and chatgpt_project_context.json
to identify consolidation opportunities and technical debt.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent

def load_analysis_files():
    """Load all analysis files."""
    project_analysis = {}
    test_analysis = {}
    chatgpt_context = {}
    
    try:
        with open(PROJECT_ROOT / "project_analysis.json", 'r', encoding='utf-8') as f:
            project_analysis = json.load(f)
    except Exception as e:
        print(f"⚠️  Error loading project_analysis.json: {e}")
    
    try:
        with open(PROJECT_ROOT / "test_analysis.json", 'r', encoding='utf-8') as f:
            test_analysis = json.load(f)
    except Exception as e:
        print(f"⚠️  Error loading test_analysis.json: {e}")
    
    try:
        with open(PROJECT_ROOT / "chatgpt_project_context.json", 'r', encoding='utf-8') as f:
            chatgpt_context = json.load(f)
    except Exception as e:
        print(f"⚠️  Error loading chatgpt_project_context.json: {e}")
    
    return project_analysis, test_analysis, chatgpt_context

def find_duplicate_patterns(project_analysis: Dict) -> Dict:
    """Find duplicate function/class patterns."""
    function_names = defaultdict(list)
    class_names = defaultdict(list)
    
    for file_path, file_data in project_analysis.items():
        if isinstance(file_data, dict):
            for func in file_data.get("functions", []):
                function_names[func].append(file_path)
            for cls_name, cls_data in file_data.get("classes", {}).items():
                class_names[cls_name].append(file_path)
    
    # Find duplicates (appearing in 2+ files)
    duplicate_functions = {name: files for name, files in function_names.items() if len(files) > 1}
    duplicate_classes = {name: files for name, files in class_names.items() if len(files) > 1}
    
    return {
        "duplicate_functions": duplicate_functions,
        "duplicate_classes": duplicate_classes,
        "total_duplicate_functions": len(duplicate_functions),
        "total_duplicate_classes": len(duplicate_classes)
    }

def find_high_complexity_files(project_analysis: Dict, threshold: int = 20) -> List[Tuple[str, int]]:
    """Find files with high complexity."""
    high_complexity = []
    
    for file_path, file_data in project_analysis.items():
        if isinstance(file_data, dict):
            complexity = file_data.get("complexity", 0)
            if complexity >= threshold:
                high_complexity.append((file_path, complexity))
    
    return sorted(high_complexity, key=lambda x: x[1], reverse=True)

def find_low_complexity_files(project_analysis: Dict, threshold: int = 2) -> List[Tuple[str, int]]:
    """Find files with very low complexity (potential consolidation candidates)."""
    low_complexity = []
    
    for file_path, file_data in project_analysis.items():
        if isinstance(file_data, dict):
            complexity = file_data.get("complexity", 0)
            functions = len(file_data.get("functions", []))
            classes = len(file_data.get("classes", {}))
            if complexity <= threshold and (functions > 0 or classes > 0):
                low_complexity.append((file_path, complexity, functions, classes))
    
    return sorted(low_complexity, key=lambda x: x[1])

def find_similar_file_names(project_analysis: Dict) -> Dict[str, List[str]]:
    """Find files with similar names (potential duplicates)."""
    file_basenames = defaultdict(list)
    
    for file_path in project_analysis.keys():
        if isinstance(file_path, str):
            basename = Path(file_path).stem
            file_basenames[basename].append(file_path)
    
    # Find basenames that appear multiple times
    duplicates = {name: files for name, files in file_basenames.items() if len(files) > 1}
    
    return duplicates

def analyze_test_coverage(test_analysis: Dict, project_analysis: Dict) -> Dict:
    """Analyze test coverage."""
    test_files = set(test_analysis.keys())
    project_files = set(project_analysis.keys())
    
    # Find files without tests
    files_without_tests = []
    for file_path in project_files:
        if file_path.endswith('.py') and not any(
            test_file for test_file in test_files 
            if file_path.replace('src/', '').replace('tools/', '') in test_file
        ):
            files_without_tests.append(file_path)
    
    return {
        "total_test_files": len(test_files),
        "total_project_files": len(project_files),
        "files_without_tests": len(files_without_tests),
        "coverage_estimate": (len(project_files) - len(files_without_tests)) / len(project_files) * 100 if project_files else 0
    }

def generate_consolidation_report():
    """Generate comprehensive consolidation report."""
    print("🔍 Analyzing project scan results...")
    print()
    
    project_analysis, test_analysis, chatgpt_context = load_analysis_files()
    
    if not project_analysis:
        print("❌ No project analysis data found")
        return
    
    print(f"📊 Project Analysis Summary:")
    print(f"   Total files analyzed: {len(project_analysis)}")
    print()
    
    # Find duplicates
    print("🔍 Finding duplicate patterns...")
    duplicates = find_duplicate_patterns(project_analysis)
    print(f"   Duplicate functions: {duplicates['total_duplicate_functions']}")
    print(f"   Duplicate classes: {duplicates['total_duplicate_classes']}")
    print()
    
    # Find high complexity files
    print("🔍 Finding high complexity files...")
    high_complexity = find_high_complexity_files(project_analysis, threshold=20)
    print(f"   Files with complexity >= 20: {len(high_complexity)}")
    if high_complexity:
        print("   Top 10 most complex files:")
        for file_path, complexity in high_complexity[:10]:
            print(f"      {complexity:3d} - {file_path}")
    print()
    
    # Find low complexity files (consolidation candidates)
    print("🔍 Finding consolidation candidates...")
    low_complexity = find_low_complexity_files(project_analysis, threshold=2)
    print(f"   Low complexity files (potential consolidation): {len(low_complexity)}")
    if low_complexity:
        print("   Top 20 consolidation candidates:")
        for file_path, complexity, funcs, classes in low_complexity[:20]:
            print(f"      {complexity:2d} ({funcs} funcs, {classes} classes) - {file_path}")
    print()
    
    # Find similar file names
    print("🔍 Finding similar file names...")
    similar_names = find_similar_file_names(project_analysis)
    print(f"   Files with duplicate basenames: {len(similar_names)}")
    if similar_names:
        print("   Top 20 similar name groups:")
        for name, files in list(similar_names.items())[:20]:
            if len(files) > 1:
                print(f"      {name}: {len(files)} files")
                for f in files[:3]:
                    print(f"         - {f}")
    print()
    
    # Test coverage
    if test_analysis:
        print("🔍 Analyzing test coverage...")
        coverage = analyze_test_coverage(test_analysis, project_analysis)
        print(f"   Test files: {coverage['total_test_files']}")
        print(f"   Project files: {coverage['total_project_files']}")
        print(f"   Files without tests: {coverage['files_without_tests']}")
        print(f"   Estimated coverage: {coverage['coverage_estimate']:.1f}%")
        print()
    
    # Loop closure scan (incomplete loops)
    loop_scan = scan_loop_closure_trackers()
    if loop_scan["incomplete_loops"]:
        print("🔍 Loop closure scan: Incomplete loops detected")
        for loop in loop_scan["incomplete_loops"]:
            print(f"   • Loop {loop['loop_id']}: {loop['name']} ({loop['status']}) [{loop['source']}]")
        print()
    else:
        print("✅ Loop closure scan: No incomplete loops found")
        print()

    # Generate report
    report = {
        "summary": {
            "total_files": len(project_analysis),
            "duplicate_functions": duplicates['total_duplicate_functions'],
            "duplicate_classes": duplicates['total_duplicate_classes'],
            "high_complexity_files": len(high_complexity),
            "low_complexity_files": len(low_complexity),
            "similar_file_names": len(similar_names),
            "incomplete_loops": len(loop_scan["incomplete_loops"])
        },
        "duplicates": {
            "top_duplicate_functions": dict(list(duplicates['duplicate_functions'].items())[:20]),
            "top_duplicate_classes": dict(list(duplicates['duplicate_classes'].items())[:20])
        },
        "high_complexity": high_complexity[:20],
        "consolidation_candidates": low_complexity[:50],
        "similar_names": dict(list(similar_names.items())[:30]),
        "test_coverage": coverage if test_analysis else None,
        "loop_closure": loop_scan
    }
    
    # Save report
    report_file = PROJECT_ROOT / "docs" / "archive" / "consolidation" / "project_scan_analysis_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report saved to: {report_file}")
    print()
    print("📋 Key Findings:")
    print(f"   • {duplicates['total_duplicate_functions']} duplicate function names found")
    print(f"   • {duplicates['total_duplicate_classes']} duplicate class names found")
    print(f"   • {len(high_complexity)} files need complexity reduction")
    print(f"   • {len(low_complexity)} files are consolidation candidates")
    print(f"   • {len(similar_names)} file name groups may indicate duplicates")
    print(f"   • {len(loop_scan['incomplete_loops'])} incomplete loops detected")


def scan_loop_closure_trackers() -> Dict[str, object]:
    """Scan loop closure tracker files and return incomplete loops."""
    tracker_files = list(
        Path(".").glob("agent_workspaces/**/LOOP_CLOSURE_*TRACKER*.md")
    ) + list(
        Path("agent_workspaces").glob("**/LOOP_CLOSURE_UPDATE_*.md")
    ) + list(
        Path("docs/organization").glob("CAPTAIN_LOOP_CLOSURE_ASSIGNMENTS_*.md")
    )

    incomplete_loops: List[Dict[str, str]] = []

    for file_path in tracker_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue

        for loop in parse_loops(content):
            normalized_status = normalize_status(loop["status"])
            if not is_complete_status(normalized_status):
                incomplete_loops.append(
                    {
                        "loop_id": loop["loop_id"],
                        "name": loop["name"],
                        "status": normalized_status,
                        "source": str(file_path),
                    }
                )

    return {
        "files_scanned": [str(p) for p in tracker_files],
        "incomplete_loops": incomplete_loops,
    }


def parse_loops(content: str) -> List[Dict[str, str]]:
    """Parse loop sections from tracker markdown."""
    loops: List[Dict[str, str]] = []
    sections = re.split(r"(?=### \*\*Loop\s*\d+)", content)
    for section in sections:
        loop_match = re.match(
            r"### \*\*Loop\s*(\d+):\s*(.*?)\*\*.*?\n", section, re.DOTALL
        )
        if not loop_match:
            continue
        loop_id = loop_match.group(1)
        name = loop_match.group(2).strip()
        status_match = re.search(r"Status\*\*:\s*[^\n]*\*\*(.*?)\*\*", section)
        status = status_match.group(1).strip() if status_match else "UNKNOWN"
        loops.append({"loop_id": loop_id, "name": name, "status": status})
    return loops


def normalize_status(status: str) -> str:
    """Normalize status text by stripping emojis and uppercasing."""
    cleaned = re.sub(r"[^\w\s]", " ", status).upper()
    return " ".join(cleaned.split())


def is_complete_status(status: str) -> bool:
    """Return True if status indicates completion."""
    return any(
        keyword in status
        for keyword in [
            "COMPLETE",
            "DONE",
            "CLOSED",
            "VERIFIED COMPLETE",
            "FINALIZED",
        ]
    )

if __name__ == "__main__":
    generate_consolidation_report()

