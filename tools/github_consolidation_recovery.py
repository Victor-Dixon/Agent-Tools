#!/usr/bin/env python3
"""
GitHub Consolidation Recovery Script
====================================

Executes recovery plan for GitHub consolidation blockers.
Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-11-29
Priority: CRITICAL
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to use GitHub bypass system
try:
    from src.core.synthetic_github import get_synthetic_github
    from src.core.deferred_push_queue import get_deferred_push_queue
    GITHUB_BYPASS_AVAILABLE = True
except ImportError:
    GITHUB_BYPASS_AVAILABLE = False

# Fallback token loading
def get_github_token() -> Optional[str]:
    """Get GitHub token from environment."""
    import os
from src.core.config.timeout_constants import TimeoutConstants
    return os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")


def verify_repo_exists(owner: str, repo: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify repository existence using REST API.
    
    Returns:
        Dict with exists (bool), archived (bool), status_code, and details
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_SHORT)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "exists": True,
                "archived": data.get("archived", False),
                "status_code": 200,
                "full_name": data.get("full_name"),
                "html_url": data.get("html_url"),
                "default_branch": data.get("default_branch", "main"),
                "private": data.get("private", False),
            }
        elif response.status_code == 404:
            return {
                "exists": False,
                "archived": False,
                "status_code": 404,
                "error": "Repository not found",
            }
        elif response.status_code == 403:
            return {
                "exists": None,  # Unknown (might be private)
                "archived": False,
                "status_code": 403,
                "error": "Access forbidden (may be private or rate-limited)",
            }
        else:
            return {
                "exists": None,
                "archived": False,
                "status_code": response.status_code,
                "error": f"Unexpected status: {response.status_code}",
            }
    except Exception as e:
        return {
            "exists": None,
            "archived": False,
            "status_code": None,
            "error": str(e),
        }


def verify_skipped_merges() -> Dict[str, Any]:
    """Verify 4 skipped merges using Repository Verification Protocol."""
    owner = "Dadudekc"
    token = get_github_token()
    
    skipped_merges = [
        {
            "source": "trade-analyzer",
            "target": "trading-leads-bot",
            "description": "trade-analyzer → trading-leads-bot",
        },
        {
            "source": "intelligent-multi-agent",
            "target": "Agent_Cellphone",
            "description": "intelligent-multi-agent → Agent_Cellphone",
        },
        {
            "source": "Agent_Cellphone_V1",
            "target": "Agent_Cellphone",
            "description": "Agent_Cellphone_V1 → Agent_Cellphone",
        },
        {
            "source": "my_personal_templates",
            "target": "my-resume",
            "description": "my_personal_templates → my-resume",
        },
    ]
    
    print("🔍 Verifying 4 Skipped Merges (Repository Verification Protocol)")
    print("=" * 70)
    
    results = []
    for merge in skipped_merges:
        source = merge["source"]
        target = merge["target"]
        description = merge["description"]
        
        print(f"\n📋 {description}")
        print(f"   Verifying source: {owner}/{source}")
        
        source_result = verify_repo_exists(owner, source, token)
        
        print(f"   Verifying target: {owner}/{target}")
        target_result = verify_repo_exists(owner, target, token)
        
        merge_result = {
            "merge": description,
            "source_repo": f"{owner}/{source}",
            "target_repo": f"{owner}/{target}",
            "source_exists": source_result.get("exists"),
            "target_exists": target_result.get("exists"),
            "source_status": source_result.get("status_code"),
            "target_status": target_result.get("status_code"),
            "action": None,
        }
        
        if source_result.get("exists") is False:
            print(f"   ✅ Source repo not found (404) - correctly skipped")
            merge_result["action"] = "SKIP (source not found)"
        elif source_result.get("exists") is True:
            print(f"   ⚠️ Source repo EXISTS - retry merge!")
            merge_result["action"] = "RETRY (source exists)"
        else:
            print(f"   ⚠️ Source repo status unknown: {source_result.get('error', 'Unknown')}")
            merge_result["action"] = "UNKNOWN"
        
        if target_result.get("exists") is False:
            print(f"   ❌ Target repo not found (404)")
            merge_result["action"] = f"{merge_result['action']} - TARGET MISSING"
        
        results.append(merge_result)
    
    return {"skipped_merges": results}


def check_pr_status() -> Dict[str, Any]:
    """Check PR status for all completed merges."""
    owner = "Dadudekc"
    token = get_github_token()
    
    # Batch 2 completed merges
    completed_merges = [
        {
            "repo": "DreamVault",
            "pr_number": 4,
            "description": "DigitalDreamscape → DreamVault",
        },
        {
            "repo": "DreamVault",
            "pr_number": 3,
            "description": "Thea → DreamVault",
        },
        {
            "repo": "Streamertools",
            "pr_number": 13,
            "description": "MeTuber → Streamertools",
        },
        {
            "repo": "DreamVault",
            "pr_number": 1,
            "description": "DreamBank → DreamVault",
        },
        {
            "repo": "DaDudeKC-Website",
            "description": "DaDudekC → DaDudeKC-Website",
            "check_branch": "DaDudekC",
        },
        {
            "repo": "MachineLearningModelMaker",
            "description": "LSTMmodel_trainer → MachineLearningModelMaker",
            "check_branch": "LSTMmodel_trainer",
        },
    ]
    
    print("\n\n🔍 Checking PR Status for Completed Merges")
    print("=" * 70)
    
    results = []
    
    # Use GitHub bypass system if available
    if GITHUB_BYPASS_AVAILABLE:
        try:
            github = get_synthetic_github()
            for merge in completed_merges:
                repo = merge["repo"]
                description = merge["description"]
                
                print(f"\n📋 {description}")
                print(f"   Repo: {owner}/{repo}")
                
                if "pr_number" in merge:
                    pr_number = merge["pr_number"]
                    success, pr_data = github.get_pr(owner, repo, pr_number)
                    
                    if success and pr_data:
                        state = pr_data.get('state', 'unknown')
                        merged = pr_data.get('merged', False)
                        url = pr_data.get('html_url', 'N/A')
                        
                        print(f"   PR #{pr_number}: {state}")
                        print(f"   Merged: {merged}")
                        print(f"   URL: {url}")
                        
                        results.append({
                            "merge": description,
                            "repo": repo,
                            "pr_number": pr_number,
                            "state": state,
                            "merged": merged,
                            "url": url,
                        })
                    else:
                        print(f"   ❌ PR #{pr_number} not found or error")
                        results.append({
                            "merge": description,
                            "repo": repo,
                            "pr_number": pr_number,
                            "state": "not_found",
                            "merged": False,
                        })
        except Exception as e:
            print(f"   ⚠️ Error using GitHub bypass: {e}")
    
    # Fallback to REST API
    if not results and token:
        for merge in completed_merges:
            repo = merge["repo"]
            description = merge["description"]
            
            if "pr_number" in merge:
                pr_number = merge["pr_number"]
                url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": f"token {token}",
                }
                
                try:
                    response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_SHORT)
                    if response.status_code == 200:
                        pr_data = response.json()
                        state = pr_data.get('state', 'unknown')
                        merged = pr_data.get('merged', False)
                        html_url = pr_data.get('html_url', 'N/A')
                        
                        print(f"\n📋 {description}")
                        print(f"   PR #{pr_number}: {state}")
                        print(f"   Merged: {merged}")
                        print(f"   URL: {html_url}")
                        
                        results.append({
                            "merge": description,
                            "repo": repo,
                            "pr_number": pr_number,
                            "state": state,
                            "merged": merged,
                            "url": html_url,
                        })
                except Exception as e:
                    print(f"   ⚠️ Error checking PR: {e}")
    
    return {"pr_status": results}


def check_deferred_queue() -> Dict[str, Any]:
    """Check deferred push queue status."""
    print("\n\n📦 Checking Deferred Push Queue")
    print("=" * 70)
    
    try:
        if GITHUB_BYPASS_AVAILABLE:
            queue = get_deferred_push_queue()
            pending_ops = queue.get_pending_operations()
            
            print(f"✅ Found {len(pending_ops)} pending operations in deferred queue")
            
            for op in pending_ops:
                print(f"   - {op.get('repo', 'Unknown')} / {op.get('branch', 'Unknown')}")
                print(f"     Reason: {op.get('reason', 'Unknown')}")
                print(f"     Status: {op.get('status', 'Unknown')}")
            
            return {
                "pending_count": len(pending_ops),
                "operations": pending_ops,
            }
        else:
            # Check file directly
            queue_file = Path("deferred_push_queue.json")
            if queue_file.exists():
                with open(queue_file, 'r') as f:
                    data = json.load(f)
                    pending = data.get("pending_pushes", [])
                    print(f"✅ Found {len(pending)} pending operations")
                    return {
                        "pending_count": len(pending),
                        "operations": pending,
                    }
            else:
                print("ℹ️ No deferred push queue file found")
                return {"pending_count": 0, "operations": []}
    except Exception as e:
        print(f"⚠️ Error checking deferred queue: {e}")
        return {"error": str(e)}


def main():
    """Execute recovery plan."""
    print("🚀 GitHub Consolidation Recovery - Execution Starting")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Task 1: Verify 4 skipped merges
    print("\n" + "=" * 70)
    print("TASK 1: Verify 4 Skipped Merges")
    print("=" * 70)
    results["skipped_merges"] = verify_skipped_merges()
    
    # Task 2: Check PR status
    print("\n" + "=" * 70)
    print("TASK 2: Check PR Status")
    print("=" * 70)
    results["pr_status"] = check_pr_status()
    
    # Task 3: Check deferred queue
    print("\n" + "=" * 70)
    print("TASK 3: Monitor Deferred Push Queue")
    print("=" * 70)
    results["deferred_queue"] = check_deferred_queue()
    
    # Generate summary report
    print("\n\n" + "=" * 70)
    print("📊 RECOVERY EXECUTION SUMMARY")
    print("=" * 70)
    
    skipped = results.get("skipped_merges", {}).get("skipped_merges", [])
    prs = results.get("pr_status", {}).get("pr_status", [])
    queue = results.get("deferred_queue", {})
    
    print(f"\n✅ Skipped Merges Verified: {len(skipped)}/4")
    print(f"✅ PRs Checked: {len(prs)}")
    print(f"✅ Deferred Queue Operations: {queue.get('pending_count', 0)}")
    
    # Save report
    report_file = Path("devlogs/2025-11-29_agent-1_github_consolidation_recovery_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Full report saved to: {report_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

