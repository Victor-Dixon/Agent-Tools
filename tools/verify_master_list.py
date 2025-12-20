#!/usr/bin/env python3
"""
Verify Master List Accuracy - Repo Analysis Improvement Tool
============================================================

Verifies accuracy of github_75_repos_master_list.json and identifies discrepancies.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-01-27
"""

import json
from pathlib import Path
from typing import Any


def load_master_list() -> dict[str, Any]:
    """Load the master list of repos."""
    master_list_path = Path("data/github_75_repos_master_list.json")
    if not master_list_path.exists():
        raise FileNotFoundError(f"Master list not found: {master_list_path}")
    
    with open(master_list_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_master_list() -> dict[str, Any]:
    """Analyze master list for accuracy issues."""
    data = load_master_list()
    repos = data.get("repos", [])
    
    analysis = {
        "total_repos": len(repos),
        "analyzed_repos": 0,
        "unknown_repos": [],
        "missing_names": [],
        "duplicate_names": {},
        "discrepancies": [],
    }
    
    # Track names for duplicates
    name_counts = {}
    
    for repo in repos:
        repo_num = repo.get("num")
        repo_name = repo.get("name", "").strip()
        analyzed = repo.get("analyzed", False)
        
        if analyzed:
            analysis["analyzed_repos"] += 1
        
        # Check for Unknown repos
        if not repo_name or repo_name.lower() == "unknown":
            analysis["unknown_repos"].append({
                "num": repo_num,
                "name": repo_name or "MISSING",
                "analyzed": analyzed,
            })
        
        # Check for missing names
        if not repo_name:
            analysis["missing_names"].append(repo_num)
        
        # Track name counts for duplicates
        if repo_name and repo_name.lower() != "unknown":
            name_lower = repo_name.lower()
            if name_lower not in name_counts:
                name_counts[name_lower] = []
            name_counts[name_lower].append(repo_num)
    
    # Find duplicates
    for name, nums in name_counts.items():
        if len(nums) > 1:
            analysis["duplicate_names"][name] = nums
    
    # Check for specific discrepancies mentioned in plan
    repo_10 = next((r for r in repos if r.get("num") == 10), None)
    if repo_10:
        repo_10_name = repo_10.get("name", "").lower()
        if repo_10_name == "thea" and repo_10.get("analyzed", False):
            analysis["discrepancies"].append({
                "repo_num": 10,
                "issue": "Repo #10 marked as 'Thea' in master list but may be marked Unknown elsewhere",
                "master_list_name": repo_10.get("name"),
            })
    
    return analysis


def print_analysis_report(analysis: dict[str, Any]) -> None:
    """Print analysis report."""
    print("=" * 80)
    print("MASTER LIST VERIFICATION REPORT")
    print("=" * 80)
    print()
    
    print(f"Total Repos: {analysis['total_repos']}")
    print(f"Analyzed Repos: {analysis['analyzed_repos']} ({analysis['analyzed_repos']/analysis['total_repos']*100:.1f}%)")
    print()
    
    print(f"Unknown Repos: {len(analysis['unknown_repos'])}")
    if analysis['unknown_repos']:
        print("  Repos needing identification:")
        for repo in analysis['unknown_repos']:
            print(f"    - Repo #{repo['num']}: {repo['name']} (analyzed: {repo['analyzed']})")
    print()
    
    if analysis['missing_names']:
        print(f"Missing Names: {len(analysis['missing_names'])}")
        print(f"  Repo numbers: {', '.join(map(str, analysis['missing_names']))}")
        print()
    
    if analysis['duplicate_names']:
        print(f"Duplicate Names Found: {len(analysis['duplicate_names'])}")
        for name, nums in analysis['duplicate_names'].items():
            print(f"  '{name}': Repos {', '.join(map(str, nums))}")
        print()
    
    if analysis['discrepancies']:
        print(f"Discrepancies Found: {len(analysis['discrepancies'])}")
        for disc in analysis['discrepancies']:
            print(f"  Repo #{disc['repo_num']}: {disc['issue']}")
            print(f"    Master list name: {disc['master_list_name']}")
        print()
    
    print("=" * 80)


def main():
    """Main execution."""
    try:
        analysis = analyze_master_list()
        print_analysis_report(analysis)
        
        # Save analysis to file
        output_path = Path("agent_workspaces/Agent-8/master_list_verification.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Analysis saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


