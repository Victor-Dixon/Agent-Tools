#!/usr/bin/env python3
"""
V2 Compliance Dashboard Sync Tool
=================================

Automatically syncs V2 compliance dashboard with comprehensive audit results.
Prevents discrepancy between reported and actual violation counts.

Usage:
    python tools/v2_compliance_dashboard_sync.py [--verify] [--update]
    python tools/v2_compliance_dashboard_sync.py --verify  # Check for discrepancies
    python tools/v2_compliance_dashboard_sync.py --update  # Update dashboard

Author: Agent-4 (Captain)
V2 Compliant: <300 lines
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

MAX_FILE_LINES = 300
DASHBOARD_PATH = Path("docs/v2_compliance/V2_COMPLIANCE_DASHBOARD.md")


def find_all_violations() -> List[Dict]:
    """Find all files exceeding 300-line limit."""
    violations = []
    
    src_path = Path('src')
    if not src_path.exists():
        return violations
    
    for py_file in src_path.rglob('*.py'):
        if '__pycache__' in str(py_file) or 'test_' in py_file.name:
            continue
        
        try:
            lines = py_file.read_text(encoding='utf-8').splitlines()
            line_count = len(lines)
            
            if line_count > MAX_FILE_LINES:
                violations.append({
                    'file': str(py_file),
                    'lines': line_count,
                    'excess': line_count - MAX_FILE_LINES
                })
        except Exception:
            continue
    
    violations.sort(key=lambda x: x['lines'], reverse=True)
    return violations


def categorize_violations(violations: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize violations by severity."""
    categories = {
        'critical': [],  # >1000 lines
        'major': [],     # 500-1000 lines
        'moderate': [],  # 400-500 lines
        'minor': []      # 300-400 lines
    }
    
    for v in violations:
        if v['lines'] > 1000:
            categories['critical'].append(v)
        elif v['lines'] > 500:
            categories['major'].append(v)
        elif v['lines'] > 400:
            categories['moderate'].append(v)
        else:
            categories['minor'].append(v)
    
    return categories


def read_dashboard() -> str:
    """Read current dashboard content."""
    if not DASHBOARD_PATH.exists():
        return ""
    return DASHBOARD_PATH.read_text(encoding='utf-8')


def extract_dashboard_counts(content: str) -> Tuple[int, float]:
    """Extract violation count and compliance rate from dashboard."""
    # Look for violation count pattern
    violation_match = re.search(r'Violations.*?:\s*(\d+)', content, re.IGNORECASE)
    compliance_match = re.search(r'Compliance.*?:\s*([\d.]+)%', content, re.IGNORECASE)
    
    violations = int(violation_match.group(1)) if violation_match else 0
    compliance = float(compliance_match.group(1)) if compliance_match else 0.0
    
    return violations, compliance


def verify_dashboard() -> Tuple[bool, Dict]:
    """Verify dashboard accuracy against actual violations."""
    actual_violations = find_all_violations()
    actual_count = len(actual_violations)
    actual_compliance = (889 - actual_count) / 889 * 100  # Assuming 889 total files
    
    dashboard_content = read_dashboard()
    dashboard_count, dashboard_compliance = extract_dashboard_counts(dashboard_content)
    
    is_accurate = (actual_count == dashboard_count) and (
        abs(actual_compliance - dashboard_compliance) < 0.1
    )
    
    return is_accurate, {
        'actual_violations': actual_count,
        'actual_compliance': actual_compliance,
        'dashboard_violations': dashboard_count,
        'dashboard_compliance': dashboard_compliance,
        'discrepancy': actual_count != dashboard_count
    }


def update_dashboard_summary(violations: List[Dict], categories: Dict) -> str:
    """Generate dashboard summary section."""
    total_files = 889  # From dashboard
    compliant_files = total_files - len(violations)
    compliance_rate = (compliant_files / total_files) * 100
    
    summary = f"""## 🎯 V2 COMPLIANCE OVERVIEW

**Standard**: Files MUST be ≤300 lines (with approved exceptions)

### Current Status:
- **Total Files**: {total_files} files
- **Violations Remaining**: {len(violations)} violations
- **Compliant Files**: {compliant_files} compliant
- **Compliance Rate**: {compliance_rate:.1f}% ✅

### Violation Breakdown:
- **Critical (>1000 lines)**: {len(categories['critical'])} files
- **Major (500-1000 lines)**: {len(categories['major'])} files
- **Moderate (400-500 lines)**: {len(categories['moderate'])} files
- **Minor (300-400 lines)**: {len(categories['minor'])} files

### Top 10 Violations:
"""
    
    for i, v in enumerate(violations[:10], 1):
        rel_path = v['file'].replace('src\\', 'src/').replace('\\', '/')
        summary += f"{i}. `{rel_path}` - **{v['lines']} lines** (+{v['excess']})\n"
    
    return summary


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sync V2 compliance dashboard with audit results"
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify dashboard accuracy without updating'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update dashboard with current violation counts'
    )
    
    args = parser.parse_args()
    
    if not args.verify and not args.update:
        print("❌ Error: Must specify --verify or --update")
        print("Usage: python tools/v2_compliance_dashboard_sync.py [--verify] [--update]")
        sys.exit(1)
    
    violations = find_all_violations()
    categories = categorize_violations(violations)
    
    if args.verify:
        is_accurate, info = verify_dashboard()
        
        print("\n" + "="*60)
        print("V2 COMPLIANCE DASHBOARD VERIFICATION")
        print("="*60)
        print(f"\nActual Violations: {info['actual_violations']}")
        print(f"Actual Compliance: {info['actual_compliance']:.1f}%")
        print(f"\nDashboard Violations: {info['dashboard_violations']}")
        print(f"Dashboard Compliance: {info['dashboard_compliance']:.1f}%")
        
        if is_accurate:
            print("\n✅ Dashboard is ACCURATE")
        else:
            print("\n❌ Dashboard is INACCURATE - Update required!")
            if info['discrepancy']:
                print(f"   Violation count mismatch: {info['dashboard_violations']} vs {info['actual_violations']}")
        
        print("="*60 + "\n")
        sys.exit(0 if is_accurate else 1)
    
    if args.update:
        print("⚠️ Dashboard auto-update not yet implemented")
        print("Please update dashboard manually using the summary below:\n")
        print(update_dashboard_summary(violations, categories))
        sys.exit(0)


if __name__ == '__main__':
    main()


