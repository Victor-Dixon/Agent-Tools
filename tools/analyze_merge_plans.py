#!/usr/bin/env python3
"""
Analyze Merge Plans
===================

Analyzes the merge plans JSON file to provide insights.

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-12-04
"""

import json
from pathlib import Path
from collections import Counter
from datetime import datetime

def analyze_merge_plans():
    """Analyze merge plans and provide summary."""
    plans_file = Path("dream/consolidation_buffer/merge_plans.json")
    
    if not plans_file.exists():
        print(f"❌ File not found: {plans_file}")
        return
    
    # Load data
    with open(plans_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 60)
    print("📊 MERGE PLANS ANALYSIS")
    print("=" * 60)
    print()
    
    # Basic stats
    total = len(data)
    print(f"Total merge plans: {total}")
    print()
    
    # Status breakdown
    statuses = Counter(p['status'] for p in data.values())
    print("Status breakdown:")
    for status, count in statuses.most_common():
        percentage = (count / total) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    print()
    
    # Successful merges
    successful = [p for p in data.values() if p['status'] == 'merged']
    print(f"✅ Successful merges: {len(successful)}")
    if successful:
        print("\nSuccessful merge details:")
        for plan in successful:
            print(f"  - {plan['source_repo']} → {plan['target_repo']}")
            print(f"    Plan ID: {plan['plan_id']}")
            print(f"    Created: {plan['created_at']}")
            if plan.get('diff_file'):
                print(f"    Diff file: {plan['diff_file']}")
    print()
    
    # Failed merges
    failed = [p for p in data.values() if p['status'] == 'failed']
    print(f"❌ Failed merges: {len(failed)}")
    
    # Error breakdown
    errors = Counter(
        p['metadata'].get('error', 'Unknown error') 
        for p in failed
    )
    print("\nError breakdown:")
    for error, count in errors.most_common():
        print(f"  {error}: {count}")
    print()
    
    # Repository analysis
    source_repos = set(p['source_repo'] for p in data.values())
    target_repos = set(p['target_repo'] for p in data.values())
    
    print(f"Unique source repositories: {len(source_repos)}")
    print(f"Unique target repositories: {len(target_repos)}")
    print()
    
    # Most attempted merges
    merge_attempts = Counter(
        f"{p['source_repo']} → {p['target_repo']}"
        for p in data.values()
    )
    print("Most attempted merges:")
    for merge, count in merge_attempts.most_common(10):
        print(f"  {merge}: {count} attempts")
    print()
    
    # Date range
    dates = [datetime.fromisoformat(p['created_at']) for p in data.values()]
    if dates:
        print(f"Date range:")
        print(f"  Earliest: {min(dates)}")
        print(f"  Latest: {max(dates)}")
    print()
    
    print("=" * 60)

if __name__ == "__main__":
    analyze_merge_plans()

