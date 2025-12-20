#!/usr/bin/env python3
"""
Run integration checks on Agent-7's 8 repos
Uses Agent-3's check_integration_issues.py and Agent-5's detect_venv_files.py
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

# Target repos (SSOT versions) to check
TARGET_REPOS = [
    {"name": "FocusForge", "repo": "FocusForge", "num": 24},
    {"name": "TBOWTactics", "repo": "TBOWTactics", "num": 26},
    {"name": "Superpowered-TTRPG", "repo": "Superpowered-TTRPG", "num": 50},
    {"name": "selfevolving_ai", "repo": "selfevolving_ai", "num": 39},
    {"name": "Agent_Cellphone", "repo": "Agent_Cellphone", "num": 6},
    {"name": "my-resume", "repo": "my-resume", "num": 12},
    {"name": "trading-leads-bot", "repo": "trading-leads-bot", "num": 17},
]

# Note: my-resume appears twice (my_resume and my_personal_templates both merge into it)
# So we only need to check it once

def clone_repo(repo_name, temp_dir):
    """Clone a repository."""
    repo_url = f"https://github.com/Dadudekc/{repo_name}.git"
    clone_dir = temp_dir / repo_name
    
    print(f"📥 Cloning {repo_name}...")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(clone_dir)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to clone {repo_name}: {result.stderr}")
        return None
    
    print(f"✅ Cloned {repo_name}")
    return clone_dir

def run_integration_check(repo_path, repo_name):
    """Run check_integration_issues.py on a repo."""
    print(f"\n🔍 Running integration check on {repo_name}...")
    result = subprocess.run(
        ["python", "tools/check_integration_issues.py", str(repo_path), repo_name],
        capture_output=True,
        text=True
    )
    
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

def run_venv_check(repo_path, repo_name):
    """Run detect_venv_files.py on a repo."""
    print(f"\n🔍 Running venv check on {repo_name}...")
    result = subprocess.run(
        ["python", "tools/detect_venv_files.py", str(repo_path)],
        capture_output=True,
        text=True
    )
    
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

def main():
    """Main execution."""
    print("=" * 60)
    print("Agent-7 Integration Checks - All 8 Repos")
    print("=" * 60)
    print()
    
    # Create temp directory
    temp_base = Path("D:/Temp")
    temp_base.mkdir(exist_ok=True)
    temp_dir = temp_base / f"integration_checks_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_dir.mkdir(exist_ok=True)
    
    print(f"📁 Temp directory: {temp_dir}")
    print()
    
    results = []
    
    # Process each repo
    for repo_info in TARGET_REPOS:
        repo_name = repo_info["name"]
        repo_num = repo_info["num"]
        
        print(f"\n{'='*60}")
        print(f"Processing: {repo_name} (Repo #{repo_num})")
        print(f"{'='*60}")
        
        # Clone repo
        repo_path = clone_repo(repo_name, temp_dir)
        if not repo_path:
            results.append({
                "repo": repo_name,
                "status": "clone_failed",
                "error": "Failed to clone repository"
            })
            continue
        
        # Run integration check
        integration_result = run_integration_check(repo_path, repo_name)
        
        # Run venv check
        venv_result = run_venv_check(repo_path, repo_name)
        
        # Compile results
        results.append({
            "repo": repo_name,
            "repo_num": repo_num,
            "status": "checked",
            "integration_check": {
                "returncode": integration_result["returncode"],
                "output": integration_result["stdout"]
            },
            "venv_check": {
                "returncode": venv_result["returncode"],
                "output": venv_result["stdout"]
            }
        })
        
        print(f"✅ Completed checks for {repo_name}")
    
    # Save results
    output_file = Path("agent_workspaces/Agent-7/integration_checks_results.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("Integration Checks Complete")
    print(f"{'='*60}")
    print(f"\n✅ Results saved to: {output_file}")
    print(f"📁 Temp directory (can be deleted): {temp_dir}")
    
    # Print summary
    print("\n📊 Summary:")
    for result in results:
        status = result.get("status", "unknown")
        print(f"  {result['repo']}: {status}")
    
    return results

if __name__ == "__main__":
    main()







