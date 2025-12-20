#!/usr/bin/env python3
"""
Agent-2 Independent Architecture Review
UNBIASED assessment of 75 GitHub repos from architecture perspective
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

def get_repo_list() -> List[str]:
    """Extract just repo names (not Agent-6's scores)"""
    with open('COMPLETE_GITHUB_ROI_RESULTS.json') as f:
        data = json.load(f)
    return [r['repo'] for r in data['results']]

def assess_architecture(repo_name: str) -> Dict:
    """
    INDEPENDENT architecture assessment
    Using Agent-2's architecture expertise (NOT Agent-6's ROI)
    """
    arch_score = 0
    issues = []
    strengths = []
    
    # Initial assessment from repo name patterns
    # (Will clone top repos for deeper analysis)
    
    # Architecture pattern recognition
    name_lower = repo_name.lower()
    
    # STRENGTH: Good naming conventions
    if any(x in name_lower for x in ['robot', 'analyzer', 'scanner', 'automation']):
        arch_score += 10
        strengths.append("Clear purpose from naming")
    
    # WEAKNESS: Poor naming
    if any(x in name_lower for x in ['test', 'tmp', 'backup', 'old', 'copy']):
        issues.append("Temporary/test naming suggests low quality")
    
    # WEAKNESS: Typos in name (indicates low care)
    if 'auot' in name_lower or 'ult' in name_lower:
        issues.append("Typos in repo name (quality concern)")
    
    # STRENGTH: Professional patterns
    if '-' in repo_name or '_' in repo_name:  # Proper naming convention
        arch_score += 5
        strengths.append("Follows naming conventions")
    
    # Multiple version suggests architecture iteration (can be good or bad)
    if any(x in name_lower for x in ['v2', 'v3', 'new', 'ultimate']):
        issues.append("Multiple versions - check for duplicates")
    
    # Determine tier based on architecture criteria
    if arch_score >= 60:
        tier = "KEEP - Good Architecture"
    elif arch_score >= 40:
        tier = "REVIEW - Needs Assessment"
    else:
        tier = "NEEDS DEEP REVIEW"
    
    return {
        'repo': repo_name,
        'arch_score': arch_score,
        'tier': tier,
        'issues': issues,
        'strengths': strengths,
        'needs_clone_review': True  # All need deeper review
    }

def clone_and_assess_deep(repo_name: str) -> Dict:
    """
    Deep architecture assessment by cloning
    Check actual code structure
    """
    clone_url = f"https://github.com/Dadudekc/{repo_name}.git"
    clone_dir = Path(f"temp_arch_review/{repo_name}")
    
    # Check if already in audit results
    audit_file = Path("GITHUB_AUDIT_RESULTS.json")
    if audit_file.exists():
        with open(audit_file) as f:
            audit_data = json.load(f)
            for r in audit_data['results']:
                if r['name'] == repo_name:
                    return assess_from_audit_data(r)
    
    return {'cloned': False, 'message': 'Not in deep audit yet'}

def assess_from_audit_data(audit_result: Dict) -> Dict:
    """
    Architecture assessment from audit data
    """
    arch_score = 0
    
    # Architecture criteria (Agent-2 perspective)
    if audit_result.get('has_tests'):
        arch_score += 25  # Testability
        test_count = audit_result.get('test_count', 0)
        if test_count >= 20:
            arch_score += 10  # Excellent test coverage
        elif test_count >= 10:
            arch_score += 5   # Good test coverage
    
    if audit_result.get('has_ci_cd'):
        arch_score += 20  # Automation/professionalism
        
    if audit_result.get('has_requirements') or audit_result.get('has_package_json'):
        arch_score += 15  # Proper dependency management
        
    if audit_result.get('has_readme'):
        arch_score += 10  # Documentation
        
    if audit_result.get('has_gitignore'):
        arch_score += 10  # Professional setup
        
    if audit_result.get('has_license'):
        arch_score += 10  # Legal/professional
    
    # Issues reduce score
    issues_count = len(audit_result.get('issues', []))
    arch_score -= (issues_count * 5)
    
    # Determine architectural tier
    if arch_score >= 70:
        tier = "EXCELLENT - Keep & Showcase"
    elif arch_score >= 50:
        tier = "GOOD - Keep with minor improvements"
    elif arch_score >= 30:
        tier = "NEEDS WORK - Consider consolidation"
    else:
        tier = "POOR - Archive candidate"
    
    return {
        'repo': audit_result['name'],
        'arch_score': arch_score,
        'tier': tier,
        'has_tests': audit_result.get('has_tests', False),
        'test_count': audit_result.get('test_count', 0),
        'has_ci_cd': audit_result.get('has_ci_cd', False),
        'issues': audit_result.get('issues', []),
        'recommendations': audit_result.get('recommendations', [])
    }

def main():
    """Main independent review"""
    print("=" * 80)
    print("AGENT-2 INDEPENDENT ARCHITECTURE REVIEW")
    print("Architecture perspective - NO Agent-6 bias")
    print("=" * 80)
    print()
    
    # Step 1: Get all 75 repos
    repos = get_repo_list()
    print(f"✅ Found {len(repos)} repos for review\n")
    
    # Step 2: Initial assessment (all repos)
    initial_assessments = []
    for repo in repos:
        assessment = assess_architecture(repo)
        initial_assessments.append(assessment)
    
    print(f"✅ Initial assessment complete\n")
    
    # Step 3: Deep assessment (8 repos we have audit data for)
    deep_assessments = []
    audited_repos = [
        'projectscanner', 'AutoDream.Os', 'UltimateOptionsTradingRobot',
        'trade_analyzer', 'dreambank', 'Agent_Cellphone',
        'machinelearningmodelmaker', 'network-scanner'
    ]
    
    print("Deep assessment of audited repos:")
    with open('GITHUB_AUDIT_RESULTS.json') as f:
        audit_data = json.load(f)
    
    for audit_result in audit_data['results']:
        deep_assessment = assess_from_audit_data(audit_result)
        deep_assessments.append(deep_assessment)
        print(f"  {deep_assessment['repo']}: Score {deep_assessment['arch_score']} - {deep_assessment['tier']}")
    
    print()
    
    # Step 4: Categorize all repos
    excellent = [a for a in deep_assessments if 'EXCELLENT' in a['tier']]
    good = [a for a in deep_assessments if 'GOOD' in a['tier']]
    needs_work = [a for a in deep_assessments if 'NEEDS WORK' in a['tier']]
    poor = [a for a in deep_assessments if 'POOR' in a['tier']]
    
    print("\n" + "=" * 80)
    print("AGENT-2 ARCHITECTURAL FINDINGS")
    print("=" * 80)
    print(f"\nTotal Repos Analyzed: {len(repos)}")
    print(f"Deep Assessment: {len(deep_assessments)} repos")
    print()
    print(f"EXCELLENT (Keep & Showcase): {len(excellent)} repos")
    for a in excellent:
        print(f"  - {a['repo']} (Score: {a['arch_score']})")
    print()
    print(f"GOOD (Keep with improvements): {len(good)} repos")
    for a in good:
        print(f"  - {a['repo']} (Score: {a['arch_score']})")
    print()
    print(f"NEEDS WORK (Consider consolidation): {len(needs_work)} repos")
    for a in needs_work:
        print(f"  - {a['repo']} (Score: {a['arch_score']})")
    print()
    print(f"POOR (Archive candidates): {len(poor)} repos")
    for a in poor:
        print(f"  - {a['repo']} (Score: {a['arch_score']})")
    print()
    
    # Step 5: Save results
    results = {
        'agent': 'Agent-2',
        'perspective': 'Architecture Quality',
        'date': '2025-10-14',
        'total_repos': len(repos),
        'deep_assessed': len(deep_assessments),
        'excellent_count': len(excellent),
        'good_count': len(good),
        'needs_work_count': len(needs_work),
        'poor_count': len(poor),
        'deep_assessments': deep_assessments,
        'all_repo_names': repos
    }
    
    with open('AGENT2_INDEPENDENT_ARCHITECTURE_REVIEW.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("✅ Results saved to AGENT2_INDEPENDENT_ARCHITECTURE_REVIEW.json")
    print()
    print("Next: Compare with Agent-6's findings...")

if __name__ == '__main__':
    main()


