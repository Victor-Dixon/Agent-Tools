#!/usr/bin/env python3
"""
Prioritize Duplicate Groups for SSOT Consolidation
===================================================

Analyzes duplicate groups from technical debt analysis and prioritizes them
for SSOT consolidation based on impact, risk, and consolidation value.

Task: Technical Debt Duplicate Resolution Coordination (Agent-4 ↔ Agent-8)
Author: Agent-8 (SSOT & System Integration Specialist)
V2 Compliant: <300 lines

FIXED: 2025-12-18 by Agent-3
- Added file existence validation for SSOT and duplicate files
- Added empty file filtering
- Added validation before prioritization to prevent processing invalid groups
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

project_root = Path(__file__).resolve().parent.parent
tech_debt_path = project_root / "docs" / "technical_debt" / "TECHNICAL_DEBT_ANALYSIS.json"


def load_tech_debt_data() -> Dict:
    """Load technical debt analysis data."""
    if not tech_debt_path.exists():
        print(f"❌ Technical debt analysis not found: {tech_debt_path}")
        sys.exit(1)
    
    with open(tech_debt_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_duplicate_groups(groups: List[Dict]) -> List[Dict]:
    """Validate duplicate groups by checking file existence."""
    validated_groups = []
    invalid_count = 0
    
    for group in groups:
        ssot_path = group.get('ssot', '')
        duplicates = group.get('duplicates', [])
        
        # Check SSOT file exists and is not empty
        ssot_file = project_root / ssot_path
        if not ssot_file.exists():
            invalid_count += 1
            continue
        try:
            if ssot_file.stat().st_size == 0:
                invalid_count += 1
                continue  # Skip empty SSOT files
        except Exception:
            invalid_count += 1
            continue
        
        # Check duplicate files exist
        valid_duplicates = []
        for dup_path in duplicates:
            dup_file = project_root / dup_path
            if dup_file.exists():
                try:
                    if dup_file.stat().st_size > 0:  # Only include non-empty files
                        valid_duplicates.append(dup_path)
                except Exception:
                    pass  # Skip files that can't be checked
        
        # Only include groups with valid SSOT and at least one valid duplicate
        if valid_duplicates:
            validated_group = group.copy()
            validated_group['duplicates'] = valid_duplicates
            validated_group['count'] = len(valid_duplicates) + 1  # SSOT + duplicates
            validated_groups.append(validated_group)
        else:
            invalid_count += 1
    
    if invalid_count > 0:
        print(f"⚠️  Filtered out {invalid_count} invalid groups (non-existent or empty files)")
    
    return validated_groups


def score_duplicate_group(group: Dict, all_groups: List[Dict]) -> Dict[str, Any]:
    """Score a duplicate group for prioritization."""
    score = 0
    factors = {}
    
    # Factor 1: Count (more duplicates = higher priority)
    count = group.get('count', 2)
    count_score = count * 10
    score += count_score
    factors['count_score'] = count_score
    
    # Factor 2: Risk level (LOW=1, MEDIUM=3, HIGH=5, CRITICAL=10)
    risk = group.get('risk', 'LOW').upper()
    risk_multipliers = {'LOW': 1, 'MEDIUM': 3, 'HIGH': 5, 'CRITICAL': 10}
    risk_mult = risk_multipliers.get(risk, 1)
    score *= risk_mult
    factors['risk_multiplier'] = risk_mult
    factors['risk'] = risk
    
    # Factor 3: SSOT location quality (src/ > tools/ > temp_repos/)
    ssot_path = group.get('ssot', '')
    if ssot_path.startswith('src/'):
        location_bonus = 50
    elif ssot_path.startswith('tools/'):
        location_bonus = 30
    elif 'temp_repos' in ssot_path:
        location_bonus = 10
    else:
        location_bonus = 20
    score += location_bonus
    factors['location_bonus'] = location_bonus
    factors['ssot_location'] = 'src/' if ssot_path.startswith('src/') else 'other'
    
    # Factor 4: Cross-domain impact (files in different domains = higher priority)
    all_files = [ssot_path] + group.get('duplicates', [])
    domains = set()
    for file_path in all_files:
        if file_path.startswith('src/'):
            parts = file_path.split('/')
            if len(parts) > 1:
                domains.add(parts[1])  # src/<domain>/
    
    cross_domain_bonus = len(domains) * 25 if len(domains) > 1 else 0
    score += cross_domain_bonus
    factors['cross_domain_bonus'] = cross_domain_bonus
    factors['domains'] = list(domains) if domains else []
    
    # Factor 5: Action type (DELETE vs MERGE)
    action = group.get('action', 'DELETE')
    if action == 'DELETE':
        action_bonus = 20  # Deletion is cleaner
    else:
        action_bonus = 10
    score += action_bonus
    factors['action_bonus'] = action_bonus
    factors['action'] = action
    
    return {
        'group': group,
        'score': score,
        'factors': factors,
        'priority': determine_priority(score)
    }


def determine_priority(score: int) -> str:
    """Determine priority level from score."""
    if score >= 500:
        return 'CRITICAL'
    elif score >= 200:
        return 'HIGH'
    elif score >= 100:
        return 'MEDIUM'
    else:
        return 'LOW'


def prioritize_groups(duplicate_groups: List[Dict]) -> List[Dict]:
    """Prioritize duplicate groups by consolidation value."""
    scored_groups = [score_duplicate_group(group, duplicate_groups) for group in duplicate_groups]
    
    # Sort by score (descending)
    scored_groups.sort(key=lambda x: x['score'], reverse=True)
    
    return scored_groups


def generate_batch_list(prioritized_groups: List[Dict], batch_size: int = 15) -> List[List[Dict]]:
    """Generate batches from prioritized groups."""
    batches = []
    
    # Group by priority
    by_priority = defaultdict(list)
    for scored in prioritized_groups:
        priority = scored['priority']
        by_priority[priority].append(scored)
    
    # Create batches: CRITICAL first, then HIGH, then MEDIUM
    current_batch = []
    
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if priority not in by_priority:
            continue
        
        for scored in by_priority[priority]:
            current_batch.append(scored)
            if len(current_batch) >= batch_size:
                batches.append(current_batch)
                current_batch = []
    
    # Add remaining
    if current_batch:
        batches.append(current_batch)
    
    return batches


def main():
    """Main execution."""
    print("🔧 Prioritizing Duplicate Groups for SSOT Consolidation")
    print(f"   Source: {tech_debt_path}")
    print()
    
    # Load data
    data = load_tech_debt_data()
    duplicate_groups = data.get('consolidation_recommendations', [])
    
    print(f"📊 Analysis:")
    print(f"   Total duplicate groups loaded: {len(duplicate_groups)}")
    
    # Validate file existence
    print()
    print("🔍 Validating file existence...")
    duplicate_groups = validate_duplicate_groups(duplicate_groups)
    print(f"   Valid duplicate groups: {len(duplicate_groups)}")
    
    # Prioritize
    print()
    print("🔍 Prioritizing groups...")
    prioritized = prioritize_groups(duplicate_groups)
    
    # Generate batches
    batches = generate_batch_list(prioritized, batch_size=15)
    
    # Summary by priority
    by_priority = defaultdict(int)
    for scored in prioritized:
        by_priority[scored['priority']] += 1
    
    print()
    print("📊 Priority Distribution:")
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = by_priority.get(priority, 0)
        if count > 0:
            print(f"   {priority}: {count} groups")
    
    # Top 15 high-value groups
    print()
    print("🎯 Top 15 High-Value Duplicate Groups:")
    print("=" * 80)
    for i, scored in enumerate(prioritized[:15], 1):
        group = scored['group']
        ssot = group.get('ssot', 'N/A')
        count = group.get('count', 0)
        risk = group.get('risk', 'LOW')
        score = scored['score']
        priority = scored['priority']
        
        print(f"\n{i}. Priority: {priority} | Score: {score} | Risk: {risk} | Count: {count}")
        print(f"   SSOT: {ssot}")
        print(f"   Duplicates: {len(group.get('duplicates', []))} files")
        if scored['factors'].get('domains'):
            print(f"   Domains: {', '.join(scored['factors']['domains'])}")
    
    # Create batch report
    output_path = project_root / "docs" / "technical_debt" / "DUPLICATE_GROUPS_PRIORITY_BATCHES.json"
    output_data = {
        "analysis_date": data.get('summary', {}).get('analysis_date', ''),
        "total_groups": len(duplicate_groups),
        "batches": [],
        "top_15": []
    }
    
    for batch_num, batch in enumerate(batches, 1):
        batch_data = {
            "batch_number": batch_num,
            "priority": batch[0]['priority'] if batch else 'LOW',
            "size": len(batch),
            "groups": []
        }
        
        for scored in batch:
            group_data = {
                "ssot": scored['group'].get('ssot'),
                "duplicates": scored['group'].get('duplicates', []),
                "count": scored['group'].get('count'),
                "risk": scored['group'].get('risk'),
                "action": scored['group'].get('action'),
                "score": scored['score'],
                "priority": scored['priority'],
                "factors": scored['factors']
            }
            batch_data['groups'].append(group_data)
        
        output_data['batches'].append(batch_data)
    
    # Add top 15
    for scored in prioritized[:15]:
        output_data['top_15'].append({
            "ssot": scored['group'].get('ssot'),
            "score": scored['score'],
            "priority": scored['priority'],
            "risk": scored['group'].get('risk'),
            "count": scored['group'].get('count')
        })
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print()
    print("=" * 80)
    print("✅ PRIORITIZATION COMPLETE")
    print(f"   Output: {output_path}")
    print(f"   Batches created: {len(batches)}")
    print(f"   Top 15 groups identified for immediate consolidation")
    print()
    print("🎯 Next Steps:")
    print("   1. Review prioritized batches with Agent-4")
    print("   2. Assign batches to agents for execution")
    print("   3. Begin consolidation with Batch 1 (highest priority)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

