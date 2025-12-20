#!/usr/bin/env python3
"""
Review Temp Repos - Consolidation Action
========================================

Reviews temp_repos directory to determine if files can be removed.
Part of CLI consolidation execution plan.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
TEMP_REPOS_DIR = PROJECT_ROOT / "temp_repos"


def analyze_temp_repos() -> Dict:
    """Analyze temp_repos directory structure and contents."""
    analysis = {
        "total_files": 0,
        "total_directories": 0,
        "file_types": defaultdict(int),
        "directories": [],
        "python_files": [],
        "size_mb": 0
    }
    
    if not TEMP_REPOS_DIR.exists():
        return {"error": "temp_repos directory does not exist"}
    
    # Analyze structure
    for item in TEMP_REPOS_DIR.rglob("*"):
        if item.is_file():
            analysis["total_files"] += 1
            suffix = item.suffix.lower()
            analysis["file_types"][suffix] += 1
            
            # Get file size
            try:
                size = item.stat().st_size
                analysis["size_mb"] += size
            except:
                pass
            
            if suffix == ".py":
                relative_path = str(item.relative_to(PROJECT_ROOT))
                analysis["python_files"].append(relative_path)
        
        elif item.is_dir():
            analysis["total_directories"] += 1
            relative_path = str(item.relative_to(PROJECT_ROOT))
            analysis["directories"].append(relative_path)
    
    analysis["size_mb"] = round(analysis["size_mb"] / (1024 * 1024), 2)
    
    return analysis


def check_references() -> Dict:
    """Check if temp_repos are referenced by active code."""
    references = {
        "src_references": [],
        "tools_references": [],
        "config_references": [],
        "total_references": 0
    }
    
    # Search for temp_repos references
    search_paths = [
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "tools",
        PROJECT_ROOT / "config"
    ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        for py_file in search_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "temp_repos" in content or "temp_repo" in content:
                    relative_path = str(py_file.relative_to(PROJECT_ROOT))
                    
                    if "src" in relative_path:
                        references["src_references"].append(relative_path)
                    elif "tools" in relative_path:
                        references["tools_references"].append(relative_path)
                    elif "config" in relative_path:
                        references["config_references"].append(relative_path)
            except:
                continue
    
    references["total_references"] = (
        len(references["src_references"]) +
        len(references["tools_references"]) +
        len(references["config_references"])
    )
    
    return references


def categorize_repos() -> Dict:
    """Categorize temp repos by purpose."""
    categories = defaultdict(list)
    
    if not TEMP_REPOS_DIR.exists():
        return {}
    
    for repo_dir in TEMP_REPOS_DIR.iterdir():
        if not repo_dir.is_dir():
            continue
        
        repo_name = repo_dir.name
        
        # Categorize by name patterns
        if "Thea" in repo_name:
            categories["thea_repos"].append(repo_name)
        elif "Dream" in repo_name or "dream" in repo_name:
            categories["dream_repos"].append(repo_name)
        elif "Auto" in repo_name or "auto" in repo_name:
            categories["auto_repos"].append(repo_name)
        else:
            categories["other_repos"].append(repo_name)
    
    return dict(categories)


def generate_recommendation(analysis: Dict, references: Dict, categories: Dict) -> Dict:
    """Generate removal recommendation."""
    recommendation = {
        "can_remove": False,
        "reason": "",
        "risk_level": "unknown",
        "action": ""
    }
    
    # Check references
    if references["total_references"] > 0:
        recommendation["can_remove"] = False
        recommendation["reason"] = f"Found {references['total_references']} references to temp_repos in active code"
        recommendation["risk_level"] = "HIGH"
        recommendation["action"] = "Review and remove references before deletion"
    else:
        recommendation["can_remove"] = True
        recommendation["reason"] = "No references found in active code"
        recommendation["risk_level"] = "LOW"
        recommendation["action"] = "Safe to archive and remove"
    
    return recommendation


def main():
    """Review temp_repos directory."""
    print("🔍 Reviewing temp_repos Directory...")
    print()
    
    # Analyze structure
    print("📊 Analyzing temp_repos structure...")
    analysis = analyze_temp_repos()
    
    if "error" in analysis:
        print(f"❌ {analysis['error']}")
        return
    
    print(f"   Total files: {analysis['total_files']}")
    print(f"   Total directories: {analysis['total_directories']}")
    print(f"   Python files: {len(analysis['python_files'])}")
    print(f"   Total size: {analysis['size_mb']} MB")
    print()
    
    # Check references
    print("🔍 Checking for references in active code...")
    references = check_references()
    
    print(f"   References in src/: {len(references['src_references'])}")
    print(f"   References in tools/: {len(references['tools_references'])}")
    print(f"   References in config/: {len(references['config_references'])}")
    print(f"   Total references: {references['total_references']}")
    print()
    
    if references['total_references'] > 0:
        print("⚠️  References Found:")
        for ref in references['src_references'][:5]:
            print(f"   - {ref}")
        for ref in references['tools_references'][:5]:
            print(f"   - {ref}")
        if len(references['src_references']) + len(references['tools_references']) > 10:
            print("   ... and more")
        print()
    
    # Categorize
    print("📋 Categorizing repos...")
    categories = categorize_repos()
    
    for category, repos in categories.items():
        print(f"   {category}: {len(repos)} repos")
        for repo in repos[:3]:
            print(f"      - {repo}")
        if len(repos) > 3:
            print(f"      ... and {len(repos) - 3} more")
    print()
    
    # Generate recommendation
    recommendation = generate_recommendation(analysis, references, categories)
    
    print("💡 Recommendation:")
    print(f"   Can Remove: {recommendation['can_remove']}")
    print(f"   Risk Level: {recommendation['risk_level']}")
    print(f"   Reason: {recommendation['reason']}")
    print(f"   Action: {recommendation['action']}")
    print()
    
    # Save report
    report = {
        "analysis": analysis,
        "references": references,
        "categories": categories,
        "recommendation": recommendation
    }
    
    output_file = PROJECT_ROOT / "docs" / "archive" / "consolidation" / "temp_repos_review.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Review saved to: {output_file}")


if __name__ == "__main__":
    main()

