#!/usr/bin/env python3
"""
Batch 1 Business Value Analysis
================================
Analyzes duplicate groups from Batch 1 re-analysis to determine business value
for consolidation prioritization.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-18
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def calculate_business_value(group: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate business value metrics for a duplicate group."""
    ssot = group.get('ssot', '')
    duplicates = group.get('duplicates', [])
    count = group.get('count', 0)
    risk = group.get('risk', 'UNKNOWN')

    # Business value factors
    metrics = {
        'file_elimination_count': len(duplicates),
        'total_files': count,
        'risk_level': risk,
        'location_value': 0,
        'domain_value': 0,
        'maintenance_value': 0,
        'business_value_score': 0
    }

    # Location value: Higher for production code (src/), lower for temp/workspace
    if 'src\\' in ssot or 'src/' in ssot:
        metrics['location_value'] = 50
    elif 'tools\\' in ssot or 'tools/' in ssot:
        metrics['location_value'] = 30
    elif 'temp_repos\\' in ssot or 'temp_repos/' in ssot:
        metrics['location_value'] = 10
    elif 'agent_workspaces\\' in ssot or 'agent_workspaces/' in ssot:
        metrics['location_value'] = 5
    else:
        metrics['location_value'] = 20

    # Domain value: Core systems, analytics, web are higher value
    ssot_lower = ssot.lower()
    if any(x in ssot_lower for x in ['core', 'analytics', 'web', 'api', 'service']):
        metrics['domain_value'] = 30
    elif any(x in ssot_lower for x in ['test', 'demo', 'example']):
        metrics['domain_value'] = 5
    else:
        metrics['domain_value'] = 15

    # Maintenance value: More duplicates = higher maintenance burden
    # Each duplicate file increases maintenance cost
    metrics['maintenance_value'] = len(duplicates) * 10

    # Risk multiplier (lower risk = safer to consolidate = higher value)
    risk_multipliers = {
        'LOW': 1.0,
        'MEDIUM': 0.7,
        'HIGH': 0.4,
        'CRITICAL': 0.2
    }
    risk_mult = risk_multipliers.get(risk, 0.5)

    # Business value score calculation
    base_score = (
        metrics['file_elimination_count'] * 15 +  # Files eliminated
        metrics['location_value'] +                # Location importance
        metrics['domain_value'] +                  # Domain importance
        # Maintenance burden reduction
        metrics['maintenance_value']
    )
    metrics['business_value_score'] = int(base_score * risk_mult)

    return metrics


def analyze_batch1() -> Dict[str, Any]:
    """Analyze Batch 1 groups for business value."""
    batches_file = Path(
        'docs/technical_debt/DUPLICATE_GROUPS_PRIORITY_BATCHES.json')

    if not batches_file.exists():
        print(f"❌ File not found: {batches_file}")
        return {}

    with open(batches_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find Batch 1
    batch1 = None
    for batch in data.get('batches', []):
        if batch.get('batch_number') == 1:
            batch1 = batch
            break

    if not batch1:
        print("❌ Batch 1 not found")
        return {}

    groups = batch1.get('groups', [])
    print(f"📊 Analyzing {len(groups)} groups from Batch 1...\n")

    # Analyze each group
    analyzed_groups = []
    for i, group in enumerate(groups, 1):
        metrics = calculate_business_value(group)
        analyzed_groups.append({
            'group_number': i,
            'ssot': group.get('ssot', ''),
            'duplicates': group.get('duplicates', []),
            'original_score': group.get('score', 0),
            'risk': group.get('risk', 'UNKNOWN'),
            'metrics': metrics
        })

    # Sort by business value score (descending)
    analyzed_groups.sort(
        key=lambda x: x['metrics']['business_value_score'], reverse=True)

    # Summary statistics
    total_files_eliminated = sum(
        g['metrics']['file_elimination_count'] for g in analyzed_groups)
    total_groups = len(analyzed_groups)
    avg_business_value = sum(g['metrics']['business_value_score']
                             for g in analyzed_groups) / total_groups if total_groups > 0 else 0

    return {
        'summary': {
            'total_groups': total_groups,
            'total_files_eliminated': total_files_eliminated,
            'average_business_value': round(avg_business_value, 2),
            'highest_value_group': analyzed_groups[0] if analyzed_groups else None
        },
        'groups': analyzed_groups
    }


def generate_report(analysis: Dict[str, Any]) -> str:
    """Generate markdown report from analysis."""
    if not analysis:
        return "❌ No analysis data available"

    summary = analysis['summary']
    groups = analysis['groups']

    report = f"""# Batch 1 Business Value Analysis

**Date**: 2025-12-18  
**Agent**: Agent-5 (Business Intelligence Specialist)  
**Purpose**: Prioritize duplicate consolidation based on business value

---

## 📊 Summary

- **Total Groups**: {summary['total_groups']}
- **Total Files to Eliminate**: {summary['total_files_eliminated']}
- **Average Business Value Score**: {summary['average_business_value']}

---

## 🎯 Top 10 Highest Business Value Groups

These groups provide the highest business value for consolidation prioritization:

"""

    for i, group in enumerate(groups[:10], 1):
        metrics = group['metrics']
        ssot_name = Path(group['ssot']).name

        report += f"""### {i}. {ssot_name}

- **Business Value Score**: {metrics['business_value_score']} (Rank #{i})
- **Files to Eliminate**: {metrics['file_elimination_count']}
- **Total Files**: {metrics['total_files']}
- **Risk Level**: {metrics['risk_level']}
- **Location**: `{group['ssot']}`
- **Location Value**: {metrics['location_value']}/50
- **Domain Value**: {metrics['domain_value']}/30
- **Maintenance Value**: {metrics['maintenance_value']}/100

**Impact**: Eliminating {metrics['file_elimination_count']} duplicate file(s) with {metrics['risk_level']} risk.

"""

    report += "\n---\n\n## 📈 Business Value Metrics Explanation\n\n"
    report += """
**Business Value Score Calculation**:
- **File Elimination Count** (15 points per file): Direct impact on reducing duplicates
- **Location Value** (5-50 points): Higher for production code (src/), lower for temp/workspace
- **Domain Value** (5-30 points): Higher for core/analytics/web, lower for tests/demos
- **Maintenance Value** (10 points per duplicate): Ongoing maintenance burden reduction
- **Risk Multiplier** (0.2-1.0): Lower risk = safer consolidation = higher value

**Prioritization Recommendation**: Consolidate groups with highest business value scores first.

---

"""

    report += "## 📋 All Groups (Sorted by Business Value)\n\n"
    report += "| Rank | Business Value | Files Eliminated | Risk | SSOT File |\n"
    report += "|------|---------------|------------------|------|-----------|\n"

    for i, group in enumerate(groups, 1):
        metrics = group['metrics']
        ssot_name = Path(group['ssot']).name
        report += f"| {i} | {metrics['business_value_score']} | {metrics['file_elimination_count']} | {metrics['risk_level']} | `{ssot_name}` |\n"

    report += "\n---\n\n🐝 **WE. ARE. SWARM. ⚡🔥**\n"

    return report


def main():
    """Main entry point."""
    print("🔍 Batch 1 Business Value Analysis")
    print("=" * 60)
    print()

    analysis = analyze_batch1()

    if not analysis:
        print("❌ Analysis failed")
        return

    # Generate and save report
    report = generate_report(analysis)
    report_path = Path('docs/technical_debt/BATCH1_BUSINESS_VALUE_ANALYSIS.md')
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print("✅ Analysis complete!")
    print(f"📄 Report saved to: {report_path}\n")

    # Print summary
    summary = analysis['summary']
    print("📊 SUMMARY:")
    print(f"   Total Groups: {summary['total_groups']}")
    print(f"   Files to Eliminate: {summary['total_files_eliminated']}")
    print(f"   Average Business Value: {summary['average_business_value']}")

    if summary['highest_value_group']:
        top = summary['highest_value_group']
        print(f"\n🏆 TOP GROUP:")
        print(f"   SSOT: {Path(top['ssot']).name}")
        print(
            f"   Business Value Score: {top['metrics']['business_value_score']}")
        print(
            f"   Files Eliminated: {top['metrics']['file_elimination_count']}")


if __name__ == '__main__':
    main()

