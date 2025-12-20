#!/usr/bin/env python3
"""
Resolve Master List Duplicate Repo Names
=========================================

Resolves duplicate repo names in github_75_repos_master_list.json.

Task: A8-SSOT-MASTER-LIST-001
Priority: HIGH

Author: Agent-8 (SSOT & System Integration Specialist)
V2 Compliant: <300 lines
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

project_root = Path(__file__).resolve().parent.parent
master_list_path = project_root / "data" / "github_75_repos_master_list.json"


def load_master_list() -> Dict:
    """Load master list JSON file."""
    if not master_list_path.exists():
        print(f"❌ Master list not found: {master_list_path}")
        sys.exit(1)
    
    with open(master_list_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_duplicates(repos: List[Dict]) -> Dict[str, List[Dict]]:
    """Find duplicate repo names (case-insensitive)."""
    name_map = defaultdict(list)
    
    for repo in repos:
        name = repo.get('name', '').strip()
        if name:
            name_map[name.lower()].append(repo)
    
    # Return only duplicates
    return {k: v for k, v in name_map.items() if len(v) > 1}


def find_malformed_names(repos: List[Dict]) -> List[Dict]:
    """Find repos with malformed names (spaces, empty, etc.)."""
    malformed = []
    
    for repo in repos:
        name = repo.get('name', '').strip()
        if not name or ' ' in name:
            malformed.append(repo)
    
    return malformed


def normalize_name(name: str) -> str:
    """Normalize repo name (remove spaces, fix casing)."""
    # Remove spaces
    name = name.replace(' ', '')
    # Fix common casing issues
    if name.lower() == 'dadudekc':
        return 'DaDudeKC'
    elif name.lower() == 'dadudekcwebsite':
        return 'DaDudeKC-Website'
    elif name.lower() == 'myresume':
        return 'my-resume'
    elif name.lower() == 'my_resume':
        return 'my-resume'
    elif name.lower() == 'superpoweredttrpg' or name.lower() == 'superpowered_ttrpg':
        return 'Superpowered-TTRPG'
    elif 'thetradingrobotplug' in name.lower():
        return 'TradingRobotPlug'
    
    return name


def resolve_duplicates(repos: List[Dict], duplicates: Dict[str, List[Dict]]) -> Tuple[List[Dict], List[str]]:
    """Resolve duplicate repo names."""
    resolved_repos = []
    resolutions = []
    
    # Track which names we've seen (normalized)
    seen_names = set()
    
    for repo in repos:
        original_name = repo.get('name', '').strip()
        normalized = normalize_name(original_name)
        
        # Check if this is a duplicate
        if original_name.lower() in duplicates:
            dup_group = duplicates[original_name.lower()]
            
            # If we've already added this normalized name, skip
            if normalized.lower() in seen_names:
                resolutions.append(
                    f"Skipped duplicate: '{original_name}' (num {repo['num']}) "
                    f"- already have normalized version"
                )
                continue
            
            # Use normalized name
            repo_copy = repo.copy()
            repo_copy['name'] = normalized
            resolved_repos.append(repo_copy)
            seen_names.add(normalized.lower())
            
            if original_name != normalized:
                resolutions.append(
                    f"Normalized: '{original_name}' → '{normalized}' (num {repo['num']})"
                )
        else:
            # Not a duplicate, but check for malformed names
            if ' ' in original_name:
                normalized = normalize_name(original_name)
                repo_copy = repo.copy()
                repo_copy['name'] = normalized
                resolved_repos.append(repo_copy)
                resolutions.append(
                    f"Fixed malformed: '{original_name}' → '{normalized}' (num {repo['num']})"
                )
            else:
                resolved_repos.append(repo)
                seen_names.add(original_name.lower())
    
    return resolved_repos, resolutions


def main():
    """Main execution."""
    print("🔧 Resolving Master List Duplicate Repo Names")
    print(f"   File: {master_list_path}")
    print()
    
    # Load master list
    data = load_master_list()
    repos = data.get('repos', [])
    
    print(f"📊 Analysis:")
    print(f"   Total repos: {len(repos)}")
    
    # Find duplicates
    duplicates = find_duplicates(repos)
    print(f"   Case-insensitive duplicates: {len(duplicates)}")
    
    if duplicates:
        print()
        print("🔍 Duplicate groups found:")
        for name_lower, dup_repos in duplicates.items():
            print(f"   '{name_lower}':")
            for repo in dup_repos:
                print(f"     - '{repo['name']}' (num {repo['num']})")
    
    # Find malformed names
    malformed = find_malformed_names(repos)
    print(f"   Malformed names (spaces/empty): {len(malformed)}")
    
    if malformed:
        print()
        print("🔍 Malformed names found:")
        for repo in malformed:
            print(f"   - num {repo['num']}: '{repo['name']}'")
    
    # Resolve duplicates
    if duplicates or malformed:
        print()
        print("🔧 Resolving duplicates and malformed names...")
        resolved_repos, resolutions = resolve_duplicates(repos, duplicates)
        
        print()
        print("📋 Resolutions applied:")
        for resolution in resolutions:
            print(f"   {resolution}")
        
        # Update data
        data['repos'] = resolved_repos
        
        # Backup original
        backup_path = master_list_path.with_suffix('.json.backup')
        print()
        print(f"💾 Creating backup: {backup_path.name}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(load_master_list(), f, indent=2)
        
        # Write resolved version
        print(f"💾 Writing resolved version...")
        with open(master_list_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print()
        print("✅ SUCCESS!")
        print(f"   Resolved {len(duplicates)} duplicate groups")
        print(f"   Fixed {len(malformed)} malformed names")
        print(f"   Total repos: {len(resolved_repos)}")
        return 0
    else:
        print()
        print("✅ No duplicates or malformed names found - master list is clean!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
