#!/usr/bin/env python3
"""
Analyze Test Patterns - Agent-8
================================

Analyzes test files to identify duplicate patterns and consolidation opportunities.

<!-- SSOT Domain: qa -->

Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def load_test_analysis() -> Dict:
    """Load test analysis JSON file."""
    analysis_path = Path("test_analysis.json")
    if not analysis_path.exists():
        return {}
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_test_patterns(analysis: Dict) -> Dict:
    """Analyze test files for duplicate patterns."""
    patterns = {
        "setup_methods": defaultdict(list),
        "teardown_methods": defaultdict(list),
        "test_functions": defaultdict(list),
        "test_classes": defaultdict(list),
        "fixtures": defaultdict(list),
        "complexity_distribution": defaultdict(int),
    }
    
    for file_path, file_data in analysis.items():
        if 'test' not in file_path.lower() and 'conftest' not in file_path.lower():
            continue
        
        complexity = file_data.get("complexity", 0)
        patterns["complexity_distribution"][complexity] += 1
        
        # Analyze classes
        for class_name, class_data in file_data.get("classes", {}).items():
            methods = class_data.get("methods", [])
            
            # Setup/teardown patterns
            setup_methods = [m for m in methods if 'setup' in m.lower() or 'set_up' in m.lower()]
            teardown_methods = [m for m in methods if 'teardown' in m.lower() or 'tear_down' in m.lower()]
            
            for method in setup_methods:
                patterns["setup_methods"][method].append(file_path)
            for method in teardown_methods:
                patterns["teardown_methods"][method].append(file_path)
            
            # Test class patterns
            if 'test' in class_name.lower():
                patterns["test_classes"][class_name].append(file_path)
        
        # Analyze functions
        functions = file_data.get("functions", [])
        test_functions = [f for f in functions if f.startswith('test_') or 'test' in f.lower()]
        
        for func in test_functions:
            patterns["test_functions"][func].append(file_path)
    
    return patterns


def identify_duplicate_patterns(patterns: Dict) -> Dict:
    """Identify duplicate patterns for consolidation."""
    duplicates = {
        "setup_duplicates": [],
        "teardown_duplicates": [],
        "test_function_duplicates": [],
        "test_class_duplicates": [],
    }
    
    # Setup methods used in multiple files
    for method, files in patterns["setup_methods"].items():
        if len(files) > 1:
            duplicates["setup_duplicates"].append({
                "method": method,
                "files": files,
                "count": len(files)
            })
    
    # Teardown methods used in multiple files
    for method, files in patterns["teardown_methods"].items():
        if len(files) > 1:
            duplicates["teardown_duplicates"].append({
                "method": method,
                "files": files,
                "count": len(files)
            })
    
    # Test functions with similar names
    for func, files in patterns["test_functions"].items():
        if len(files) > 1:
            duplicates["test_function_duplicates"].append({
                "function": func,
                "files": files,
                "count": len(files)
            })
    
    # Test classes with similar names
    for class_name, files in patterns["test_classes"].items():
        if len(files) > 1:
            duplicates["test_class_duplicates"].append({
                "class": class_name,
                "files": files,
                "count": len(files)
            })
    
    return duplicates


def generate_consolidation_report(patterns: Dict, duplicates: Dict) -> str:
    """Generate consolidation opportunity report."""
    report = []
    report.append("# Test Pattern Analysis - Consolidation Opportunities\n")
    report.append(f"**Date**: 2025-12-04\n")
    report.append(f"**Agent**: Agent-8 (Testing & Quality Assurance Specialist)\n\n")
    
    report.append("## 📊 Pattern Analysis Summary\n\n")
    report.append(f"- **Setup Methods**: {len(patterns['setup_methods'])} unique methods\n")
    report.append(f"- **Teardown Methods**: {len(patterns['teardown_methods'])} unique methods\n")
    report.append(f"- **Test Functions**: {len(patterns['test_functions'])} unique functions\n")
    report.append(f"- **Test Classes**: {len(patterns['test_classes'])} unique classes\n\n")
    
    report.append("## 🔍 Duplicate Patterns Identified\n\n")
    
    # Setup duplicates
    if duplicates["setup_duplicates"]:
        report.append("### Setup Method Duplicates\n\n")
        for dup in sorted(duplicates["setup_duplicates"], key=lambda x: x["count"], reverse=True)[:10]:
            report.append(f"- **{dup['method']}**: Used in {dup['count']} files\n")
            for file in dup["files"][:3]:
                report.append(f"  - {file}\n")
            if len(dup["files"]) > 3:
                report.append(f"  - ... and {len(dup['files']) - 3} more\n")
        report.append("\n")
    
    # Teardown duplicates
    if duplicates["teardown_duplicates"]:
        report.append("### Teardown Method Duplicates\n\n")
        for dup in sorted(duplicates["teardown_duplicates"], key=lambda x: x["count"], reverse=True)[:10]:
            report.append(f"- **{dup['method']}**: Used in {dup['count']} files\n")
        report.append("\n")
    
    # Test function duplicates
    if duplicates["test_function_duplicates"]:
        report.append("### Test Function Duplicates\n\n")
        for dup in sorted(duplicates["test_function_duplicates"], key=lambda x: x["count"], reverse=True)[:10]:
            report.append(f"- **{dup['function']}**: Used in {dup['count']} files\n")
        report.append("\n")
    
    # Complexity distribution
    report.append("## 📈 Complexity Distribution\n\n")
    for complexity in sorted(patterns["complexity_distribution"].keys()):
        count = patterns["complexity_distribution"][complexity]
        report.append(f"- **Complexity {complexity}**: {count} files\n")
    report.append("\n")
    
    # Consolidation recommendations
    report.append("## 💡 Consolidation Recommendations\n\n")
    report.append("### HIGH Priority:\n")
    report.append("1. Create unified test base class with common setup/teardown\n")
    report.append("2. Consolidate duplicate setup methods\n")
    report.append("3. Create test fixture utilities\n\n")
    
    report.append("### MEDIUM Priority:\n")
    report.append("1. Organize test files by domain\n")
    report.append("2. Standardize test naming conventions\n")
    report.append("3. Create test utility modules\n\n")
    
    return "".join(report)


def main():
    """Main function."""
    print("🔍 Analyzing test patterns for consolidation opportunities...\n")
    
    # Load analysis
    analysis = load_test_analysis()
    if not analysis:
        print("❌ test_analysis.json not found")
        return
    
    print(f"✅ Loaded {len(analysis)} files from test_analysis.json\n")
    
    # Analyze patterns
    print("📊 Analyzing test patterns...")
    patterns = analyze_test_patterns(analysis)
    
    # Identify duplicates
    print("🔍 Identifying duplicate patterns...")
    duplicates = identify_duplicate_patterns(patterns)
    
    # Generate report
    print("📝 Generating consolidation report...")
    report = generate_consolidation_report(patterns, duplicates)
    
    # Save report
    report_path = Path("agent_workspaces/Agent-8/TEST_PATTERN_ANALYSIS_REPORT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    
    print(f"\n✅ Report saved to: {report_path}")
    
    # Print summary
    print("\n📊 Summary:")
    print(f"   Setup duplicates: {len(duplicates['setup_duplicates'])}")
    print(f"   Teardown duplicates: {len(duplicates['teardown_duplicates'])}")
    print(f"   Test function duplicates: {len(duplicates['test_function_duplicates'])}")
    print(f"   Test class duplicates: {len(duplicates['test_class_duplicates'])}")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

