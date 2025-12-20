#!/usr/bin/env python3
"""
Analyze Merge Plan Failures
============================

Analyzes why merge plans failed during consolidation.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

def main():
    # Read archived merge plans
    archive_file = Path("docs/archive/consolidation/merge_plans_full_2025-11-30.json")
    if not archive_file.exists():
        print("❌ Archive file not found")
        return 1
    
    data = json.loads(archive_file.read_text(encoding='utf-8'))
    
    # Analyze failures
    failed_plans = {k: v for k, v in data.items() if v['status'] == 'failed'}
    successful_plans = {k: v for k, v in data.items() if v['status'] == 'merged'}
    
    print("=" * 70)
    print("🔍 MERGE PLAN FAILURE ANALYSIS")
    print("=" * 70)
    print()
    
    print(f"📊 Overview:")
    print(f"   Total plans: {len(data)}")
    print(f"   Successful: {len(successful_plans)}")
    print(f"   Failed: {len(failed_plans)}")
    print()
    
    # Analyze error messages
    error_messages = []
    error_details = defaultdict(list)
    
    for plan_id, plan in failed_plans.items():
        error = plan.get('metadata', {}).get('error', 'Unknown error')
        error_messages.append(error)
        error_details[error].append({
            'plan_id': plan_id,
            'source_repo': plan.get('source_repo'),
            'target_repo': plan.get('target_repo'),
            'description': plan.get('description'),
            'failed_at': plan.get('metadata', {}).get('failed_at')
        })
    
    error_counts = Counter(error_messages)
    
    print("🚨 Error Breakdown:")
    for error, count in error_counts.most_common():
        print(f"   {error}: {count} ({count/len(failed_plans)*100:.1f}%)")
    print()
    
    # Detailed analysis by error type
    print("=" * 70)
    print("📋 DETAILED ERROR ANALYSIS")
    print("=" * 70)
    print()
    
    for error_type, plans in error_details.items():
        print(f"## {error_type} ({len(plans)} occurrences)")
        print()
        
        # Group by repo pairs
        repo_pairs = defaultdict(list)
        for plan in plans:
            pair = f"{plan['source_repo']} → {plan['target_repo']}"
            repo_pairs[pair].append(plan)
        
        print(f"   Affected repo pairs: {len(repo_pairs)}")
        print()
        
        # Show unique repo pairs
        for pair, pair_plans in list(repo_pairs.items())[:10]:  # Show first 10
            print(f"   - {pair}")
            print(f"     Attempts: {len(pair_plans)}")
            if len(pair_plans) > 1:
                print(f"     (Multiple attempts detected)")
        if len(repo_pairs) > 10:
            print(f"   ... and {len(repo_pairs) - 10} more pairs")
        print()
    
    # Analyze patterns
    print("=" * 70)
    print("🔍 PATTERN ANALYSIS")
    print("=" * 70)
    print()
    
    # Check for duplicate attempts
    repo_pair_attempts = defaultdict(int)
    for plan in failed_plans.values():
        pair = f"{plan.get('source_repo')} → {plan.get('target_repo')}"
        repo_pair_attempts[pair] += 1
    
    multiple_attempts = {pair: count for pair, count in repo_pair_attempts.items() if count > 1}
    
    if multiple_attempts:
        print(f"⚠️  Multiple attempts detected for {len(multiple_attempts)} repo pairs:")
        for pair, count in sorted(multiple_attempts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {pair}: {count} attempts")
        print()
    
    # Check for case variations (common consolidation pattern)
    case_variations = []
    for plan in failed_plans.values():
        source = plan.get('source_repo', '').lower()
        target = plan.get('target_repo', '').lower()
        if source == target and plan.get('source_repo') != plan.get('target_repo'):
            case_variations.append(plan)
    
    if case_variations:
        print(f"📝 Case variation merges (likely consolidation): {len(case_variations)}")
        for plan in case_variations[:5]:
            print(f"   {plan.get('source_repo')} → {plan.get('target_repo')}")
        print()
    
    # Successful merge analysis
    print("=" * 70)
    print("✅ SUCCESSFUL MERGE ANALYSIS")
    print("=" * 70)
    print()
    
    for plan_id, plan in successful_plans.items():
        print(f"Plan ID: {plan_id}")
        print(f"   Source: {plan.get('source_repo')}")
        print(f"   Target: {plan.get('target_repo')}")
        print(f"   Description: {plan.get('description')}")
        print(f"   Created: {plan.get('created_at')}")
        if plan.get('diff_file'):
            print(f"   Diff file: {plan.get('diff_file')}")
        print()
    
    # Recommendations
    print("=" * 70)
    print("💡 RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    if "Source repo not available" in error_counts:
        count = error_counts["Source repo not available"]
        print(f"1. 'Source repo not available' ({count} failures):")
        print("   - Repositories may have been deleted or renamed")
        print("   - Repositories may have already been merged")
        print("   - Check if repos exist in GitHub")
        print("   - Verify repository names are correct")
        print()
    
    if "Target repo not available" in error_counts:
        count = error_counts["Target repo not available"]
        print(f"2. 'Target repo not available' ({count} failures):")
        print("   - Target repositories may not exist")
        print("   - Check repository permissions")
        print("   - Verify target repo names are correct")
        print()
    
    if multiple_attempts:
        print(f"3. Multiple attempts detected ({len(multiple_attempts)} pairs):")
        print("   - Some repo pairs were attempted multiple times")
        print("   - Consider implementing retry logic with backoff")
        print("   - Add duplicate attempt detection")
        print()
    
    # Save detailed report
    report = {
        "summary": {
            "total_plans": len(data),
            "successful": len(successful_plans),
            "failed": len(failed_plans),
            "failure_rate": f"{len(failed_plans)/len(data)*100:.1f}%"
        },
        "error_breakdown": dict(error_counts),
        "error_details": {
            error: [
                {
                    'source_repo': p['source_repo'],
                    'target_repo': p['target_repo'],
                    'description': p['description']
                }
                for p in plans
            ]
            for error, plans in error_details.items()
        },
        "patterns": {
            "multiple_attempts": dict(multiple_attempts),
            "case_variations": len(case_variations)
        },
        "successful_merges": {
            plan_id: {
                'source_repo': plan['source_repo'],
                'target_repo': plan['target_repo'],
                'description': plan['description']
            }
            for plan_id, plan in successful_plans.items()
        }
    }
    
    report_file = Path("docs/archive/consolidation/merge_failure_analysis.json")
    report_file.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"📄 Detailed report saved to: {report_file}")
    print()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())


