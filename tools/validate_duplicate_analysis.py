#!/usr/bin/env python3
"""
Validate Duplicate Analysis Results
===================================

Validates that duplicate groups from technical debt analysis contain only
existing, non-empty files. Used to verify tool fixes are working correctly.

Author: Agent-1 (Integration & Core Systems)
Date: 2025-12-18
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

project_root = Path(__file__).resolve().parent.parent
tech_debt_path = project_root / "docs" / "technical_debt" / "TECHNICAL_DEBT_ANALYSIS.json"


def validate_duplicate_groups(groups: List[Dict]) -> Dict[str, Any]:
    """Validate duplicate groups."""
    results = {
        "total_groups": len(groups),
        "valid_groups": 0,
        "invalid_groups": 0,
        "issues": []
    }
    
    for i, group in enumerate(groups):
        ssot_path = group.get('ssot', '')
        duplicates = group.get('duplicates', [])
        
        group_issues = []
        
        # Check SSOT file
        ssot_file = project_root / ssot_path
        if not ssot_file.exists():
            group_issues.append(f"SSOT file does not exist: {ssot_path}")
        else:
            try:
                if ssot_file.stat().st_size == 0:
                    group_issues.append(f"SSOT file is empty: {ssot_path}")
            except Exception as e:
                group_issues.append(f"SSOT file error: {ssot_path} - {e}")
        
        # Check duplicate files
        invalid_duplicates = []
        for dup_path in duplicates:
            dup_file = project_root / dup_path
            if not dup_file.exists():
                invalid_duplicates.append(dup_path)
            else:
                try:
                    if dup_file.stat().st_size == 0:
                        invalid_duplicates.append(f"{dup_path} (empty)")
                except Exception as e:
                    invalid_duplicates.append(f"{dup_path} (error: {e})")
        
        if invalid_duplicates:
            group_issues.append(f"Invalid duplicates: {', '.join(invalid_duplicates)}")
        
        if group_issues:
            results["invalid_groups"] += 1
            results["issues"].append({
                "group_index": i,
                "ssot": ssot_path,
                "duplicate_count": len(duplicates),
                "issues": group_issues
            })
        else:
            results["valid_groups"] += 1
    
    return results


def main():
    """Main execution."""
    print("🔍 Validating Duplicate Analysis Results")
    print("=" * 60)
    print()
    
    if not tech_debt_path.exists():
        print(f"❌ Analysis file not found: {tech_debt_path}")
        print("   Run: python tools/technical_debt_analyzer.py")
        sys.exit(1)
    
    # Load data
    print(f"📂 Loading: {tech_debt_path}")
    with open(tech_debt_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    duplicate_groups = data.get('consolidation_recommendations', [])
    print(f"📊 Found {len(duplicate_groups)} duplicate groups")
    print()
    
    # Validate
    print("🔍 Validating groups...")
    validation_results = validate_duplicate_groups(duplicate_groups)
    
    # Report
    print()
    print("=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)
    print(f"Total Groups: {validation_results['total_groups']}")
    print(f"✅ Valid Groups: {validation_results['valid_groups']}")
    print(f"❌ Invalid Groups: {validation_results['invalid_groups']}")
    
    if validation_results['invalid_groups'] > 0:
        print()
        print("⚠️  INVALID GROUPS FOUND:")
        for issue in validation_results['issues'][:10]:  # Show first 10
            print(f"\n  Group {issue['group_index']}: {issue['ssot']}")
            print(f"    Duplicates: {issue['duplicate_count']}")
            for problem in issue['issues']:
                print(f"    - {problem}")
        
        if len(validation_results['issues']) > 10:
            print(f"\n  ... and {len(validation_results['issues']) - 10} more invalid groups")
        
        print()
        print("❌ VALIDATION FAILED")
        print("   Tool fixes may not be working correctly")
        return 1
    else:
        print()
        print("✅ VALIDATION PASSED")
        print("   All duplicate groups contain only existing, non-empty files")
        return 0


if __name__ == "__main__":
    sys.exit(main())

