#!/usr/bin/env python3
"""
Repository Consolidation Continuation Tool
==========================================

Continues GitHub repo consolidation analysis by:
1. Identifying additional overlaps not yet found
2. Analyzing unanalyzed repos for consolidation opportunities
3. Refining existing consolidation groups
4. Ensuring no duplicate work

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
Builds on: Agent-8, Agent-5, Agent-6, Agent-7 consolidation work
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from difflib import SequenceMatcher

def load_existing_consolidation_plan() -> Dict[str, Any]:
    """Load existing consolidation plan from Agent-8."""
    plan_path = Path('agent_workspaces/Agent-8/REPO_CONSOLIDATION_PLAN.json')
    if plan_path.exists():
        return json.loads(plan_path.read_text(encoding='utf-8'))
    return {}

def load_master_repo_list() -> List[Dict[str, Any]]:
    """Load master repository list."""
    master_list_path = Path('data/github_75_repos_master_list.json')
    if master_list_path.exists():
        data = json.loads(master_list_path.read_text(encoding='utf-8'))
        return data.get('repos', [])
    return []

def load_repo_analyses() -> Dict[str, Dict[str, Any]]:
    """Load all repository analysis devlogs."""
    analyses = {}
    devlogs_path = Path('swarm_brain/devlogs/repository_analysis')
    
    if devlogs_path.exists():
        for devlog_file in devlogs_path.glob('*.md'):
            try:
                content = devlog_file.read_text(encoding='utf-8')
                # Extract repo name from filename or content
                repo_name = None
                
                # Try to extract from filename
                filename = devlog_file.stem
                if 'repo' in filename.lower():
                    parts = re.split(r'[_\-\s]', filename)
                    for part in parts:
                        if part and part not in ['repo', 'analysis', 'github', 'agent']:
                            repo_name = part
                            break
                
                # Try to extract from content
                if not repo_name:
                    for line in content.split('\n')[:30]:
                        if 'repo' in line.lower() and ('#' in line or ':' in line):
                            match = re.search(r'repo[#:\s]+(\d+)[\s:]+([^\s]+)', line, re.IGNORECASE)
                            if match:
                                repo_name = match.group(2).strip()
                                break
                
                if repo_name:
                    analyses[repo_name.lower()] = {
                        'name': repo_name,
                        'filename': devlog_file.name,
                        'content': content[:1000],
                        'analyzed': True
                    }
            except Exception as e:
                continue
    
    return analyses

def find_additional_overlaps(repos: List[Dict[str, Any]], existing_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find additional overlaps not in existing consolidation plan."""
    additional_groups = []
    
    # Get existing consolidation targets
    existing_targets = set()
    existing_merge_from = set()
    
    if 'consolidation_groups' in existing_plan:
        for group in existing_plan.get('consolidation_groups', []):
            if 'target' in group:
                existing_targets.add(group['target'].lower())
            if 'merge_from' in group:
                for repo in group['merge_from']:
                    existing_merge_from.add(repo.lower())
    
    # Group repos by normalized name
    repo_by_normalized = defaultdict(list)
    for repo in repos:
        if repo.get('analyzed'):
            name = repo.get('name', '').lower()
            normalized = re.sub(r'[^a-z0-9]', '', name)
            repo_by_normalized[normalized].append(repo)
    
    # Find case variations not in plan
    for normalized, repo_list in repo_by_normalized.items():
        if len(repo_list) > 1:
            # Check if already in consolidation plan
            repo_names = [r.get('name', '').lower() for r in repo_list]
            if not any(name in existing_targets or name in existing_merge_from for name in repo_names):
                # New case variation found
                primary = max(repo_list, key=lambda r: r.get('num', 0))
                secondary = [r for r in repo_list if r.get('name') != primary.get('name')]
                
                if secondary:
                    additional_groups.append({
                        'type': 'case_variation',
                        'priority': 'HIGH',
                        'target': primary.get('name'),
                        'merge_from': [r.get('name') for r in secondary],
                        'repos': repo_list,
                        'reduction': len(secondary),
                        'reason': 'Case variation not in existing plan'
                    })
    
    # Find similar purpose repos
    purpose_keywords = {
        'trading': ['trade', 'trading', 'stock', 'option', 'market'],
        'ai_assistant': ['ai', 'assistant', 'dream', 'agent'],
        'streaming': ['stream', 'youtube', 'video', 'tuber'],
        'ml': ['ml', 'machine', 'learning', 'model', 'train'],
        'agent': ['agent', 'multi-agent', 'intelligent'],
        'web': ['website', 'web', 'site'],
        'bible': ['bible', 'scripture'],
    }
    
    purpose_groups = defaultdict(list)
    for repo in repos:
        if repo.get('analyzed'):
            name = repo.get('name', '').lower()
            for purpose, keywords in purpose_keywords.items():
                if any(kw in name for kw in keywords):
                    purpose_groups[purpose].append(repo)
                    break
    
    # Check for new purpose-based groups
    for purpose, purpose_repos in purpose_groups.items():
        if len(purpose_repos) >= 2:
            # Check if already in plan
            repo_names = [r.get('name', '').lower() for r in purpose_repos]
            if not all(name in existing_targets or name in existing_merge_from for name in repo_names):
                # New purpose group found
                primary = max(purpose_repos, key=lambda r: (
                    r.get('goldmine', False),
                    r.get('num', 0)
                ))
                secondary = [r for r in purpose_repos if r.get('name') != primary.get('name')]
                
                if secondary:
                    additional_groups.append({
                        'type': 'similar_purpose',
                        'priority': 'MEDIUM',
                        'target': primary.get('name'),
                        'merge_from': [r.get('name') for r in secondary],
                        'repos': purpose_repos,
                        'reduction': len(secondary),
                        'purpose_category': purpose,
                        'reason': f'Similar purpose: {purpose}'
                    })
    
    return additional_groups

def identify_unanalyzed_consolidation_opportunities(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify consolidation opportunities for unanalyzed repos."""
    opportunities = []
    
    # Get unanalyzed repos
    unanalyzed = [r for r in repos if not r.get('analyzed', False)]
    analyzed = [r for r in repos if r.get('analyzed', False)]
    
    # Check if unanalyzed repos match names of analyzed repos
    analyzed_names = {r.get('name', '').lower(): r for r in analyzed}
    
    for unanalyzed_repo in unanalyzed:
        name = unanalyzed_repo.get('name', '').lower()
        if name and name != 'unknown':
            # Check for exact match
            if name in analyzed_names:
                opportunities.append({
                    'type': 'unanalyzed_duplicate',
                    'priority': 'HIGH',
                    'target': analyzed_names[name].get('name'),
                    'merge_from': [unanalyzed_repo.get('name')],
                    'repos': [unanalyzed_repo, analyzed_names[name]],
                    'reduction': 1,
                    'reason': f'Unanalyzed repo {unanalyzed_repo.get("name")} matches analyzed repo'
                })
    
    return opportunities

def refine_existing_groups(existing_plan: Dict[str, Any], repos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Refine existing consolidation groups with new information."""
    refined_plan = existing_plan.copy()
    
    # Add Thea to Dream Projects group (Agent-6's finding)
    if 'consolidation_groups' in refined_plan:
        for group in refined_plan.get('consolidation_groups', []):
            if group.get('target', '').lower() == 'dreamvault':
                # Check if Thea is already in merge_from
                merge_from = group.get('merge_from', [])
                if 'Thea' not in merge_from and 'thea' not in [m.lower() for m in merge_from]:
                    # Find Thea in repos
                    thea_repo = next((r for r in repos if r.get('name', '').lower() == 'thea'), None)
                    if thea_repo:
                        merge_from.append('Thea')
                        group['merge_from'] = merge_from
                        group['reduction'] = len(merge_from)
                        group['notes'] = group.get('notes', '') + ' | Thea added per Agent-6 findings'
    
    return refined_plan

def generate_continuation_report(
    existing_plan: Dict[str, Any],
    additional_groups: List[Dict[str, Any]],
    opportunities: List[Dict[str, Any]],
    repos: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate continuation analysis report."""
    
    # Calculate totals
    existing_reduction = sum(g.get('reduction', 0) for g in existing_plan.get('consolidation_groups', []))
    additional_reduction = sum(g.get('reduction', 0) for g in additional_groups)
    opportunities_reduction = sum(g.get('reduction', 0) for g in opportunities)
    
    total_reduction = existing_reduction + additional_reduction + opportunities_reduction
    
    report = {
        'analysis_date': '2025-01-27',
        'analyzer': 'Agent-2',
        'builds_on': ['Agent-8', 'Agent-5', 'Agent-6', 'Agent-7'],
        'total_repos': len(repos),
        'analyzed_repos': len([r for r in repos if r.get('analyzed')]),
        'unanalyzed_repos': len([r for r in repos if not r.get('analyzed')]),
        'existing_consolidation_groups': len(existing_plan.get('consolidation_groups', [])),
        'existing_reduction': existing_reduction,
        'additional_groups_found': len(additional_groups),
        'additional_reduction': additional_reduction,
        'unanalyzed_opportunities': len(opportunities),
        'opportunities_reduction': opportunities_reduction,
        'total_potential_reduction': total_reduction,
        'target_repo_count': len(repos) - total_reduction,
        'additional_groups': additional_groups,
        'unanalyzed_opportunities': opportunities,
        'refinements': {
            'thea_added_to_dream_projects': True,
            'case_variations_identified': len([g for g in additional_groups if g.get('type') == 'case_variation']),
            'purpose_groups_identified': len([g for g in additional_groups if g.get('type') == 'similar_purpose'])
        }
    }
    
    return report

def main():
    """Main continuation analysis."""
    print("🔍 Repository Consolidation Continuation - Agent-2")
    print("=" * 70)
    print("Building on Agent-8, Agent-5, Agent-6, and Agent-7's work...")
    print()
    
    # Load existing work
    existing_plan = load_existing_consolidation_plan()
    repos = load_master_repo_list()
    analyses = load_repo_analyses()
    
    print(f"📊 Loaded {len(repos)} repos from master list")
    print(f"📊 Found {len(analyses)} analyzed repos")
    print(f"📊 Existing plan has {len(existing_plan.get('consolidation_groups', []))} groups")
    print()
    
    # Find additional overlaps
    print("🔍 Searching for additional overlaps...")
    additional_groups = find_additional_overlaps(repos, existing_plan)
    print(f"   Found {len(additional_groups)} additional consolidation groups")
    
    # Identify unanalyzed opportunities
    print("🔍 Identifying unanalyzed consolidation opportunities...")
    opportunities = identify_unanalyzed_consolidation_opportunities(repos)
    print(f"   Found {len(opportunities)} unanalyzed opportunities")
    
    # Refine existing plan
    print("🔍 Refining existing consolidation plan...")
    refined_plan = refine_existing_groups(existing_plan, repos)
    
    # Generate report
    report = generate_continuation_report(
        existing_plan,
        additional_groups,
        opportunities,
        repos
    )
    
    # Save report
    output_path = Path('agent_workspaces/Agent-2/repo_consolidation_continuation.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2))
    
    print()
    print("✅ Continuation analysis complete!")
    print(f"   Existing reduction: {report['existing_reduction']} repos")
    print(f"   Additional reduction: {report['additional_reduction']} repos")
    print(f"   Opportunities reduction: {report['opportunities_reduction']} repos")
    print(f"   Total potential reduction: {report['total_potential_reduction']} repos")
    print(f"   Target repo count: {report['target_repo_count']} repos")
    print()
    print(f"📄 Full report saved to: {output_path}")
    
    # Print summary
    if additional_groups:
        print()
        print("📋 Additional Consolidation Groups Found:")
        print("-" * 70)
        for i, group in enumerate(additional_groups[:10], 1):
            print(f"\n{i}. {group['type']} - {group['priority']} Priority")
            print(f"   Target: {group['target']}")
            print(f"   Merge from: {', '.join(group['merge_from'][:3])}")
            print(f"   Reduction: {group['reduction']} repos")
            print(f"   Reason: {group.get('reason', 'N/A')}")
    
    if opportunities:
        print()
        print("📋 Unanalyzed Consolidation Opportunities:")
        print("-" * 70)
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"\n{i}. {opp['type']} - {opp['priority']} Priority")
            print(f"   Target: {opp['target']}")
            print(f"   Merge from: {', '.join(opp['merge_from'])}")
            print(f"   Reduction: {opp['reduction']} repos")
    
    return report

if __name__ == '__main__':
    main()


