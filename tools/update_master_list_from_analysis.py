#!/usr/bin/env python3
"""
Update Master Repo List from Comprehensive Analysis
====================================================

Extracts actual repo names from comprehensive analysis documents
and updates the master list to replace "Unknown" entries.

Author: Agent-4 (Captain)
Date: 2025-01-27
"""

import json
from pathlib import Path

def load_master_list():
    """Load current master list."""
    path = Path("data/github_75_repos_master_list.json")
    if path.exists():
        return json.loads(path.read_text())
    return {"repos": [], "stats": {}, "agents": {}}

def update_from_agent8_analysis():
    """Update repos 61-70 from Agent-8's comprehensive book."""
    # From Agent-8's REPOS_61-70_COMPREHENSIVE_BOOK.md
    # NOTE: There's a discrepancy - comprehensive book shows different mapping
    # But Agent-8's book clearly lists repos 1-10 as repos 61-70
    # Repo 1 in book = Auto_Blogger = Repo 61
    repos_61_70 = {
        61: "Auto_Blogger",
        62: "FreerideinvestorWebsite", 
        63: "stocktwits-analyzer",
        64: "InvestBuddyAdvisorUI",
        65: "prompts",
        66: "multi_web_rag",  # NOTE: Agent-1 says Victor.os is 66, but Agent-8 book shows multi_web_rag
        67: "machine-learning-pipeline",
        68: "plugin-architecture-demo",
        69: "automated-testing-framework",  # NOTE: Agent-1 says Dream.os is 69, but Agent-8 book shows this
        70: "config-management-system"
    }
    return repos_61_70

def update_from_comprehensive_book():
    """Update repos 71-75 from comprehensive analysis book."""
    # From archive/status_updates/GITHUB_75_REPOS_COMPREHENSIVE_ANALYSIS_BOOK.md
    repos_71_75 = {
        71: "FreeWork",
        72: "bolt-project",
        73: "SouthwestsSecretDjBoard",  # Note: Agent-6 says Victor.os is repo 73, but book says this
        74: "SWARM",
        75: "stocktwits-analyzer"  # Note: Agent-6 says Dream.os is repo 75, but book says this
    }
    return repos_71_75

def update_from_vision_analysis():
    """Update from vision attempts analysis."""
    # From Agent-1's analysis and Agent-6's legacy extraction
    vision_repos = {
        66: "Victor.os",  # Agent-1 says repo 66
        69: "Dream.os",   # Agent-1 says repo 69
        73: "Victor.os",  # Agent-6 says repo 73 (conflict with comprehensive book)
        75: "Dream.os"    # Agent-6 says repo 75 (conflict with comprehensive book)
    }
    return vision_repos

def update_master_list():
    """Update master list with actual repo names from analysis."""
    master = load_master_list()
    
    # Update repos 61-70 from Agent-8
    repos_61_70 = update_from_agent8_analysis()
    for num, name in repos_61_70.items():
        for repo in master["repos"]:
            if repo["num"] == num:
                if repo["name"] == "Unknown":
                    repo["name"] = name
                    repo["analyzed"] = True
                    repo["agent"] = "Agent-8"
                    print(f"✅ Updated repo {num}: {name}")
    
    # Update repos 71-75 from comprehensive book
    repos_71_75 = update_from_comprehensive_book()
    for num, name in repos_71_75.items():
        for repo in master["repos"]:
            if repo["num"] == num:
                if repo["name"] == "Unknown":
                    repo["name"] = name
                    repo["analyzed"] = True
                    repo["agent"] = "Captain"
                    print(f"✅ Updated repo {num}: {name}")
    
    # Handle vision repos (prioritize vision analysis over comprehensive book)
    vision_repos = update_from_vision_analysis()
    for num, name in vision_repos.items():
        for repo in master["repos"]:
            if repo["num"] == num:
                # Only update if still Unknown or if vision analysis takes precedence
                if repo["name"] == "Unknown" or num in [66, 69]:  # Prioritize Agent-1's findings for 66, 69
                    repo["name"] = name
                    repo["analyzed"] = True
                    if num in [66, 69]:
                        repo["agent"] = "Agent-8"  # These are in Agent-8's range
                    else:
                        repo["agent"] = "Captain"
                    print(f"✅ Updated repo {num}: {name} (vision attempt)")
    
    # Update stats
    analyzed = sum(1 for r in master["repos"] if r.get("analyzed", False))
    master["stats"]["analyzed"] = analyzed
    master["stats"]["pending"] = 75 - analyzed
    master["stats"]["completion_percent"] = (analyzed / 75) * 100
    
    # Save updated list
    output_path = Path("data/github_75_repos_master_list.json")
    output_path.write_text(json.dumps(master, indent=2))
    
    print(f"\n✅ Master list updated!")
    print(f"   Analyzed: {analyzed}/75 ({master['stats']['completion_percent']:.1f}%)")
    print(f"   Saved to: {output_path}")

if __name__ == "__main__":
    update_master_list()

