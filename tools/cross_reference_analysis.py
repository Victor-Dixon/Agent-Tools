#!/usr/bin/env python3
"""
Cross-Reference Analysis Tool - Repo Analysis Improvement
==========================================================

Cross-references multiple analysis sources to identify discrepancies, missing repos,
and improve analysis quality.

Sources:
- Master list (data/github_75_repos_master_list.json)
- Comprehensive analysis (agent_workspaces/Agent-5/comprehensive_repo_analysis_data.json)
- Agent-8 consolidation plan (agent_workspaces/Agent-8/REPO_CONSOLIDATION_PLAN.json)
- Master consolidation tracker (docs/organization/MASTER_CONSOLIDATION_TRACKER.md)
- GitHub book viewer data (if available)

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-01-27
Priority: HIGH
"""

import json
import re
from pathlib import Path
from typing import Any, Optional


def load_master_list() -> dict[str, Any]:
    """Load the master list of repos."""
    master_list_path = Path("data/github_75_repos_master_list.json")
    if not master_list_path.exists():
        raise FileNotFoundError(f"Master list not found: {master_list_path}")
    
    with open(master_list_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_comprehensive_analysis() -> Optional[dict[str, Any]]:
    """Load comprehensive repo analysis data."""
    analysis_path = Path("agent_workspaces/Agent-5/comprehensive_repo_analysis_data.json")
    if not analysis_path.exists():
        return None
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_consolidation_plan() -> Optional[dict[str, Any]]:
    """Load Agent-8's consolidation plan."""
    plan_path = Path("agent_workspaces/Agent-8/REPO_CONSOLIDATION_PLAN.json")
    if not plan_path.exists():
        return None
    
    with open(plan_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_repo_info_from_tracker() -> dict[str, dict[str, Any]]:
    """Extract repo information from master consolidation tracker markdown."""
    tracker_path = Path("docs/organization/MASTER_CONSOLIDATION_TRACKER.md")
    if not tracker_path.exists():
        return {}
    
    repo_info = {}
    
    with open(tracker_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract repo numbers and names from markdown patterns
    # Look for patterns like "Repo #X", "#X: name", etc.
    patterns = [
        r'#(\d+):\s*([^\n]+)',
        r'Repo\s+#(\d+)[:\s]+([^\n]+)',
        r'Repository\s+#(\d+)[:\s]+([^\n]+)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            repo_num = int(match.group(1))
            repo_name = match.group(2).strip()
            if repo_num not in repo_info:
                repo_info[repo_num] = {
                    "num": repo_num,
                    "name": repo_name,
                    "source": "MASTER_CONSOLIDATION_TRACKER",
                }
    
    return repo_info


def cross_reference_analysis() -> dict[str, Any]:
    """Perform cross-reference analysis across all sources."""
    master_list = load_master_list()
    comprehensive = load_comprehensive_analysis()
    consolidation_plan = load_consolidation_plan()
    tracker_info = extract_repo_info_from_tracker()
    
    master_repos = {r.get("num"): r for r in master_list.get("repos", [])}
    
    analysis = {
        "total_sources": 4,
        "sources_available": [],
        "discrepancies": [],
        "missing_in_master": [],
        "missing_in_analysis": [],
        "name_conflicts": [],
        "unknown_repos": [],
        "verification_opportunities": [],
        "cross_reference_summary": {},
    }
    
    # Track which sources are available
    if master_list:
        analysis["sources_available"].append("master_list")
    
    if comprehensive:
        analysis["sources_available"].append("comprehensive_analysis")
        comp_repos = comprehensive.get("repo_data", {})
        comp_missing = comprehensive.get("missing_repos", [])
        
        # Check for repos in comprehensive analysis but not in master list
        for repo_num, repo_data in comp_repos.items():
            repo_num_int = int(repo_num) if isinstance(repo_num, str) and repo_num.isdigit() else None
            if repo_num_int and repo_num_int not in master_repos:
                analysis["missing_in_master"].append({
                    "repo_num": repo_num_int,
                    "name": repo_data.get("name", "Unknown"),
                    "source": "comprehensive_analysis",
                })
    
    if consolidation_plan:
        analysis["sources_available"].append("consolidation_plan")
    
    if tracker_info:
        analysis["sources_available"].append("master_consolidation_tracker")
    
    # Cross-reference master list with other sources
    for repo_num, master_repo in master_repos.items():
        master_name = master_repo.get("name", "").strip()
        master_analyzed = master_repo.get("analyzed", False)
        
        # Check if Unknown or missing
        if not master_name or master_name.lower() == "unknown":
            analysis["unknown_repos"].append({
                "repo_num": repo_num,
                "master_list_status": "Unknown or missing",
                "sources_to_check": [],
            })
        
        # Check against tracker
        if repo_num in tracker_info:
            tracker_name = tracker_info[repo_num].get("name", "").strip()
            if master_name and tracker_name and master_name.lower() != tracker_name.lower():
                analysis["name_conflicts"].append({
                    "repo_num": repo_num,
                    "master_list_name": master_name,
                    "tracker_name": tracker_name,
                    "source": "master_consolidation_tracker",
                })
            elif not master_name or master_name.lower() == "unknown":
                # Tracker has a name but master list doesn't
                analysis["verification_opportunities"].append({
                    "repo_num": repo_num,
                    "suggested_name": tracker_name,
                    "source": "master_consolidation_tracker",
                    "action": "Update master list with tracker name",
                })
        
        # Check for specific discrepancies mentioned in plan
        if repo_num == 10:
            # Repo #10 discrepancy check
            if master_name.lower() == "thea" and not master_analyzed:
                analysis["discrepancies"].append({
                    "repo_num": 10,
                    "issue": "Repo #10 marked as 'Thea' in master list but may be marked Unknown elsewhere",
                    "master_list_name": master_name,
                    "master_list_analyzed": master_analyzed,
                    "recommendation": "Verify if 'Thea' is correct or if it should be Unknown",
                })
        
        if repo_num in [66, 69]:
            # Vision attempts (Victor.os, Dream.os)
            vision_names = {66: "Victor.os", 69: "Dream.os"}
            if not master_name or master_name.lower() == "unknown":
                analysis["verification_opportunities"].append({
                    "repo_num": repo_num,
                    "suggested_name": vision_names.get(repo_num),
                    "source": "improvement_plan",
                    "action": "Verify vision attempt repo exists via GitHub API",
                })
    
    # Identify repos missing from comprehensive analysis
    if comprehensive:
        comp_missing = comprehensive.get("missing_repos", [])
        for repo_num in comp_missing:
            if repo_num in master_repos:
                master_repo = master_repos[repo_num]
                analysis["missing_in_analysis"].append({
                    "repo_num": repo_num,
                    "master_list_name": master_repo.get("name", "Unknown"),
                    "master_list_analyzed": master_repo.get("analyzed", False),
                })
    
    # Create cross-reference summary
    analysis["cross_reference_summary"] = {
        "total_repos_in_master": len(master_repos),
        "unknown_repos_count": len(analysis["unknown_repos"]),
        "name_conflicts_count": len(analysis["name_conflicts"]),
        "verification_opportunities_count": len(analysis["verification_opportunities"]),
        "missing_in_master_count": len(analysis["missing_in_master"]),
        "missing_in_analysis_count": len(analysis["missing_in_analysis"]),
        "discrepancies_count": len(analysis["discrepancies"]),
    }
    
    return analysis


def print_analysis_report(analysis: dict[str, Any]) -> None:
    """Print comprehensive cross-reference analysis report."""
    print("=" * 80)
    print("CROSS-REFERENCE ANALYSIS REPORT")
    print("=" * 80)
    print()
    
    print(f"Sources Available: {len(analysis['sources_available'])}/{analysis['total_sources']}")
    print(f"  - {', '.join(analysis['sources_available'])}")
    print()
    
    summary = analysis["cross_reference_summary"]
    print("CROSS-REFERENCE SUMMARY:")
    print(f"  Total Repos in Master: {summary['total_repos_in_master']}")
    print(f"  Unknown Repos: {summary['unknown_repos_count']}")
    print(f"  Name Conflicts: {summary['name_conflicts_count']}")
    print(f"  Verification Opportunities: {summary['verification_opportunities_count']}")
    print(f"  Missing in Master: {summary['missing_in_master_count']}")
    print(f"  Missing in Analysis: {summary['missing_in_analysis_count']}")
    print(f"  Discrepancies: {summary['discrepancies_count']}")
    print()
    
    if analysis["unknown_repos"]:
        print("UNKNOWN REPOS:")
        for repo in analysis["unknown_repos"]:
            print(f"  Repo #{repo['repo_num']}: {repo['master_list_status']}")
        print()
    
    if analysis["name_conflicts"]:
        print("NAME CONFLICTS:")
        for conflict in analysis["name_conflicts"]:
            print(f"  Repo #{conflict['repo_num']}:")
            print(f"    Master List: '{conflict['master_list_name']}'")
            print(f"    {conflict['source']}: '{conflict['tracker_name']}'")
        print()
    
    if analysis["verification_opportunities"]:
        print("VERIFICATION OPPORTUNITIES:")
        for opp in analysis["verification_opportunities"]:
            print(f"  Repo #{opp['repo_num']}: {opp['action']}")
            print(f"    Suggested Name: {opp['suggested_name']}")
            print(f"    Source: {opp['source']}")
        print()
    
    if analysis["discrepancies"]:
        print("DISCREPANCIES:")
        for disc in analysis["discrepancies"]:
            print(f"  Repo #{disc['repo_num']}: {disc['issue']}")
            print(f"    Recommendation: {disc.get('recommendation', 'N/A')}")
        print()
    
    if analysis["missing_in_master"]:
        print("REPOS MISSING IN MASTER LIST:")
        for repo in analysis["missing_in_master"]:
            print(f"  Repo #{repo['repo_num']}: {repo['name']} (from {repo['source']})")
        print()
    
    if analysis["missing_in_analysis"]:
        print("REPOS MISSING IN COMPREHENSIVE ANALYSIS:")
        for repo in analysis["missing_in_analysis"]:
            analyzed_status = "Analyzed" if repo['master_list_analyzed'] else "Not Analyzed"
            print(f"  Repo #{repo['repo_num']}: {repo['master_list_name']} ({analyzed_status})")
        print()
    
    print("=" * 80)


def main():
    """Main execution."""
    try:
        print("🔍 Starting Cross-Reference Analysis...")
        print()
        
        analysis = cross_reference_analysis()
        print_analysis_report(analysis)
        
        # Save analysis to file
        output_path = Path("agent_workspaces/Agent-5/cross_reference_analysis.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Analysis saved to: {output_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Ensure required files exist before running cross-reference analysis.")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

