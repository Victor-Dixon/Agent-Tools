#!/usr/bin/env python3
"""
Update Master Consolidation Plan with Comprehensive Analysis
===========================================================

Merges Agent-5's comprehensive analysis findings into Agent-8's master consolidation plan.

Author: Agent-5
Date: 2025-01-27
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_comprehensive_analysis() -> Dict[str, Any]:
    """Load Agent-5's comprehensive analysis data."""
    path = Path('agent_workspaces/Agent-5/comprehensive_repo_analysis_data.json')
    if not path.exists():
        return {}
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_master_plan() -> Dict[str, Any]:
    """Load Agent-8's master consolidation plan."""
    path = Path('agent_workspaces/Agent-8/REPO_CONSOLIDATION_PLAN.json')
    if not path.exists():
        return {}
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_plan_with_comprehensive_findings(master_plan: Dict[str, Any], 
                                            comprehensive_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Update master plan with comprehensive analysis findings."""
    
    # Add comprehensive analysis metadata
    master_plan['comprehensive_analysis'] = {
        'analyzer': 'Agent-5',
        'analysis_date': comprehensive_analysis.get('analysis_date', '2025-01-27'),
        'total_repos_analyzed': comprehensive_analysis.get('total_repos_analyzed', 0),
        'similarity_matrix_size': comprehensive_analysis.get('similarity_matrix_size', 0),
        'missing_repos': comprehensive_analysis.get('missing_repos', []),
    }
    
    # Add new consolidation groups from comprehensive analysis
    if 'consolidation_groups' in comprehensive_analysis:
        groups = comprehensive_analysis['consolidation_groups']
        
        # High similarity groups (ready to execute)
        if 'high_similarity' in groups:
            if 'new_consolidation_groups' not in master_plan['consolidation_plan']:
                master_plan['consolidation_plan']['new_consolidation_groups'] = []
            
            for group in groups['high_similarity']:
                master_plan['consolidation_plan']['new_consolidation_groups'].append({
                    'category': 'high_similarity_duplicates',
                    'target_repo': group.get('target_repo'),
                    'target_name': group.get('target_name'),
                    'merge_from': group.get('merge_from', []),
                    'merge_from_names': group.get('merge_from_names', []),
                    'similarity_score': group.get('similarity_score', 0),
                    'priority': 'HIGH',
                    'source': 'Agent-5 Comprehensive Analysis'
                })
        
        # Medium similarity groups (review needed)
        if 'medium_similarity' in groups:
            if 'medium_priority_groups' not in master_plan['consolidation_plan']:
                master_plan['consolidation_plan']['medium_priority_groups'] = []
            
            # Filter out duplicates already in high priority
            existing_targets = {g.get('target_repo') for g in master_plan['consolidation_plan'].get('high_priority', [])}
            
            for group in groups['medium_similarity']:
                if group.get('target_repo') not in existing_targets:
                    master_plan['consolidation_plan']['medium_priority_groups'].append({
                        'category': 'medium_similarity',
                        'target_repo': group.get('target_repo'),
                        'target_name': group.get('target_name'),
                        'merge_from': group.get('merge_from', []),
                        'merge_from_names': group.get('merge_from_names', []),
                        'similarity_score': group.get('similarity_score', 0),
                        'priority': 'MEDIUM',
                        'source': 'Agent-5 Comprehensive Analysis'
                    })
    
    # Add top similar pairs for reference
    if 'top_similar_pairs' in comprehensive_analysis:
        master_plan['similarity_reference'] = {
            'top_pairs': comprehensive_analysis['top_similar_pairs'][:50],  # Top 50 pairs
            'total_pairs': comprehensive_analysis.get('similarity_matrix_size', 0),
            'source': 'Agent-5 Comprehensive Analysis'
        }
    
    # Add all repos data for reference
    if 'all_repos' in comprehensive_analysis:
        if 'comprehensive_repo_data' not in master_plan:
            master_plan['comprehensive_repo_data'] = {}
        master_plan['comprehensive_repo_data'].update(comprehensive_analysis['all_repos'])
    
    # Update summary with comprehensive findings
    if 'summary' not in master_plan['consolidation_plan']:
        master_plan['consolidation_plan']['summary'] = {}
    
    summary = master_plan['consolidation_plan']['summary']
    summary['comprehensive_analysis_included'] = True
    summary['comprehensive_analysis_date'] = comprehensive_analysis.get('analysis_date', '2025-01-27')
    summary['comprehensive_analyzer'] = 'Agent-5'
    summary['similarity_pairs_found'] = comprehensive_analysis.get('similarity_matrix_size', 0)
    
    # Update last updated info
    master_plan['last_updated'] = '2025-01-27'
    master_plan['updated_by'] = 'Agent-8 + Agent-5 (Comprehensive Analysis Integration)'
    master_plan['update_notes'] = 'Integrated Agent-5 comprehensive analysis findings including similarity matrix, additional consolidation groups, and all 75 repos data.'
    
    return master_plan


def main():
    """Main update function."""
    print("=" * 70)
    print("📦 UPDATING MASTER CONSOLIDATION PLAN")
    print("=" * 70)
    print()
    
    # Load data
    print("📂 Loading data...")
    comprehensive_analysis = load_comprehensive_analysis()
    master_plan = load_master_plan()
    
    if not master_plan:
        print("❌ ERROR: Master consolidation plan not found!")
        return
    
    if not comprehensive_analysis:
        print("⚠️  WARNING: Comprehensive analysis not found, proceeding with master plan only")
    
    print(f"✅ Loaded master plan: {len(master_plan.get('groups', {}))} groups")
    print(f"✅ Loaded comprehensive analysis: {comprehensive_analysis.get('total_repos_analyzed', 0)} repos")
    
    # Update plan
    print("\n🔄 Updating master plan with comprehensive findings...")
    updated_plan = update_plan_with_comprehensive_findings(master_plan, comprehensive_analysis)
    
    # Save updated plan
    output_path = Path('agent_workspaces/Agent-8/REPO_CONSOLIDATION_PLAN.json')
    backup_path = Path('agent_workspaces/Agent-8/REPO_CONSOLIDATION_PLAN.json.backup')
    
    # Create backup
    if output_path.exists():
        import shutil
        shutil.copy(output_path, backup_path)
        print(f"💾 Created backup: {backup_path}")
    
    # Save updated plan
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(updated_plan, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated master plan saved to: {output_path}")
    
    # Print summary
    print("\n📊 Update Summary:")
    print(f"   New consolidation groups added: {len(updated_plan['consolidation_plan'].get('new_consolidation_groups', []))}")
    print(f"   Similarity pairs: {comprehensive_analysis.get('similarity_matrix_size', 0)}")
    print(f"   Repos in comprehensive data: {len(comprehensive_analysis.get('all_repos', {}))}")
    
    print("\n✅ Master consolidation plan updated successfully!")


if __name__ == '__main__':
    main()


