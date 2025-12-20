#!/usr/bin/env python3
"""
Check all repos that need to be archived (not yet archived).

<!-- SSOT Domain: infrastructure -->
"""
import os
import sys
import requests
from pathlib import Path

try:
    from dotenv import load_dotenv
from src.core.config.timeout_constants import TimeoutConstants
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


def get_github_token():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def main():
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found")
        return 1
    
    owner = "Dadudekc"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    print("🔍 Checking repos that need archiving...\n")
    
    # All repos that should be archived (from consolidation work)
    repos_to_check = [
        {"name": "TheTradingRobotPlug", "repo_num": 38, "merged_into": "trading-leads-bot", "status": "Merged by Agent-8"},
        {"name": "LSTMmodel_trainer", "repo_num": 55, "merged_into": "MachineLearningModelMaker", "status": "PR #2 created"},
        {"name": "DreamBank", "repo_num": 3, "merged_into": "DreamVault", "status": "Merged into master"},
    ]
    
    print("📊 Repos Needing Archive:\n")
    
    need_archive = []
    already_archived = []
    not_found = []
    
    for repo_info in repos_to_check:
        repo_name = repo_info["name"]
        repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        
        try:
            response = requests.get(repo_url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 200:
                repo_data = response.json()
                archived = repo_data.get("archived", False)
                
                if archived:
                    print(f"✅ {repo_name} (Repo #{repo_info['repo_num']}) - ALREADY ARCHIVED")
                    already_archived.append(repo_info)
                else:
                    print(f"⚠️ {repo_name} (Repo #{repo_info['repo_num']}) - NEEDS ARCHIVING")
                    print(f"   Merged into: {repo_info['merged_into']}")
                    print(f"   Status: {repo_info['status']}")
                    print(f"   URL: {repo_data.get('html_url', 'N/A')}")
                    need_archive.append(repo_info)
            elif response.status_code == 404:
                print(f"❌ {repo_name} (Repo #{repo_info['repo_num']}) - NOT FOUND (may be deleted)")
                not_found.append(repo_info)
            else:
                print(f"⚠️ {repo_name} (Repo #{repo_info['repo_num']}) - Error: {response.status_code}")
        except Exception as e:
            print(f"❌ {repo_name} (Repo #{repo_info['repo_num']}) - Error: {e}")
        
        print()
    
    print("="*60)
    print(f"📊 Summary:")
    print(f"   Already Archived: {len(already_archived)}")
    print(f"   Needs Archiving: {len(need_archive)}")
    print(f"   Not Found: {len(not_found)}")
    print(f"   Total Checked: {len(repos_to_check)}")
    print()
    
    if need_archive:
        print("📋 Repos That Need Archiving:")
        for repo in need_archive:
            print(f"   - {repo['name']} (Repo #{repo['repo_num']}) → {repo['merged_into']}")
        print()
        print("💡 To archive via GitHub CLI:")
        for repo in need_archive:
            print(f"   gh repo archive {owner}/{repo['name']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

