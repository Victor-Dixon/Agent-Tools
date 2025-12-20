#!/usr/bin/env python3
"""
Verify Dream.os CI Status
==========================

Checks if CI is passing after the fix.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import sys
import requests
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.config.timeout_constants import TimeoutConstants
    TIMEOUT = TimeoutConstants.HTTP_DEFAULT
except ImportError:
    TIMEOUT = 30


def check_ci_status():
    """Check CI status for Dream.os repository."""
    repo = "Victor-Dixon/Dream.os"
    api_url = f"https://api.github.com/repos/{repo}/actions/runs"
    
    print("=" * 60)
    print("🔍 DREAM.OS CI STATUS CHECK")
    print("=" * 60)
    print(f"Repository: {repo}")
    print()
    
    try:
        # Get latest workflow runs
        response = requests.get(
            api_url,
            params={"per_page": 5, "branch": "main"},
            timeout=TIMEOUT
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
        
        runs = response.json().get("workflow_runs", [])
        
        if not runs:
            print("⚠️  No workflow runs found")
            print("   CI might not be configured yet")
            return False
        
        latest_run = runs[0]
        status = latest_run.get("status")
        conclusion = latest_run.get("conclusion")
        workflow_name = latest_run.get("name", "Unknown")
        run_number = latest_run.get("run_number")
        html_url = latest_run.get("html_url")
        created_at = latest_run.get("created_at")
        
        print(f"📊 Latest Run: #{run_number} - {workflow_name}")
        print(f"   Status: {status}")
        print(f"   Conclusion: {conclusion or 'pending'}")
        print(f"   Created: {created_at}")
        print(f"   URL: {html_url}")
        print()
        
        # Status interpretation
        if status == "completed":
            if conclusion == "success":
                print("✅ CI PASSING!")
                return True
            elif conclusion == "failure":
                print("❌ CI FAILING")
                print("   Check the workflow run for details")
                return False
            elif conclusion == "cancelled":
                print("⚠️  CI CANCELLED")
                return False
            else:
                print(f"⚠️  CI {conclusion}")
                return False
        elif status == "in_progress":
            print("🟡 CI RUNNING...")
            print("   Check back in a few minutes")
            return None
        elif status == "queued":
            print("🟡 CI QUEUED...")
            print("   Waiting to start")
            return None
        else:
            print(f"⚠️  CI Status: {status}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    result = check_ci_status()
    
    print()
    print("=" * 60)
    if result is True:
        print("✅ CI VERIFICATION: PASSING")
    elif result is False:
        print("❌ CI VERIFICATION: FAILING")
    else:
        print("🟡 CI VERIFICATION: PENDING")
    print("=" * 60)
    
    return 0 if result is True else 1


if __name__ == "__main__":
    sys.exit(main())





