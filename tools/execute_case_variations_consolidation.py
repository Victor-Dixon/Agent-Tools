#!/usr/bin/env python3
"""
Execute Case Variations Consolidation
======================================

Autonomously executes case variation merges (12 repos, zero risk).
Author: Agent-4 (Captain) - Autonomous Execution
Date: 2025-11-26
"""

import sys
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config.timeout_constants import TimeoutConstants

from tools.repo_safe_merge import SafeRepoMerge

# Import GitHub Bypass System (Local-First Architecture)
try:
    from src.core.synthetic_github import get_synthetic_github
    from src.core.deferred_push_queue import get_deferred_push_queue
    GITHUB_BYPASS_AVAILABLE = True
except ImportError as e:
    GITHUB_BYPASS_AVAILABLE = False
    print(f"⚠️ GitHub Bypass System not available - using legacy method: {e}")


# Case variations from Master Plan (12 repos)
CASE_VARIATIONS = [
    {
        "source": "Dadudekc/focusforge",
        "target": "Dadudekc/FocusForge",
        "description": "focusforge → FocusForge (Repo #32 → #24)"
    },
    {
        "source": "Dadudekc/streamertools",
        "target": "Dadudekc/Streamertools",
        "description": "streamertools → Streamertools (Repo #31 → #25)"
    },
    {
        "source": "Dadudekc/tbowtactics",
        "target": "Dadudekc/TBOWTactics",
        "description": "tbowtactics → TBOWTactics (Repo #33 → #26)"
    },
    {
        "source": "Dadudekc/superpowered_ttrpg",
        "target": "Dadudekc/Superpowered-TTRPG",
        "description": "superpowered_ttrpg → Superpowered-TTRPG (Repo #37 → #30)"
    },
    {
        "source": "Dadudekc/dadudekcwebsite",
        "target": "Dadudekc/DaDudeKC-Website",
        "description": "dadudekcwebsite → DaDudeKC-Website (Repo #35 → #28)"
    },
    {
        "source": "Dadudekc/dadudekc",
        "target": "Dadudekc/DaDudekC",
        "description": "dadudekc → DaDudekC (Repo #36 → #29)"
    },
    {
        "source": "Dadudekc/fastapi",
        "target": "Dadudekc/fastapi",
        "description": "fastapi duplicate (Repo #34 → #21) - SKIP (external library)"
    },
    {
        "source": "Dadudekc/my_resume",
        "target": "Dadudekc/my-resume",
        "description": "my_resume → my-resume (Repo #53 → #12)"
    },
    {
        "source": "Dadudekc/bible-application",
        "target": "Dadudekc/bible-application",
        "description": "bible-application duplicate (Repo #13 → #9) - SKIP (same repo)"
    },
    {
        "source": "Dadudekc/projectscanner",
        "target": "Dadudekc/projectscanner",
        "description": "projectscanner duplicate (Repo #49 → #8) - SKIP (already integrated)"
    },
    {
        "source": "Dadudekc/TROOP",
        "target": "Dadudekc/TROOP",
        "description": "TROOP duplicate (Repo #60 → #16) - Verify first"
    },
    {
        "source": "Dadudekc/LSTMmodel_trainer",
        "target": "Dadudekc/LSTMmodel_trainer",
        "description": "LSTMmodel_trainer duplicate (Repo #55 → #18) - Check PR status first"
    }
]


def check_existing_prs():
    """Check if any PRs already exist for these merges."""
    if not GITHUB_BYPASS_AVAILABLE:
        print("⚠️ GitHub Bypass System not available - skipping PR check")
        return {}
    
    try:
        github = get_synthetic_github()
        existing_prs = {}
        
        # Check known PRs from previous work
        known_prs = [
            ("MachineLearningModelMaker", 2, "LSTMmodel_trainer merge")
        ]
        
        for repo, pr_num, desc in known_prs:
            # Use SyntheticGitHub to check PR status (non-blocking)
            success, pr_data = github.get_pr("Dadudekc", repo, pr_num)
            if success and pr_data and pr_data.get("merged"):
                existing_prs[desc] = pr_data
        
        return existing_prs
    except Exception as e:
        print(f"⚠️ Error checking existing PRs: {e}")
        return {}


def execute_case_variation_merge(source, target, description):
    """Execute a single case variation merge."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    # Skip duplicates and external libraries
    if "SKIP" in description or source == target or "Verify first" in description or "Check PR" in description:
        print(f"⏭️ Skipping: {description}")
        return {"status": "skipped", "reason": "duplicate, external, or needs verification"}
    
    try:
        # Extract repo names from full paths
        target_name = target.split("/")[-1]
        source_name = source.split("/")[-1]
        
        # Use repo_safe_merge.py via subprocess (CLI interface)
        result = subprocess.run(
            [
                sys.executable,
                "tools/repo_safe_merge.py",
                target,
                source,
                "--execute"
            ],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_EXTENDED,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"✅ Merge successful: {description}")
            if result.stdout:
                # Show key output lines
                lines = result.stdout.split('\n')
                for line in lines[-10:]:  # Last 10 lines
                    if line.strip() and ('✅' in line or 'PR' in line or 'merge' in line.lower()):
                        print(f"   {line}")
            return {"status": "success", "output": result.stdout[:500]}
        else:
            print(f"⚠️ Merge had issues: {description}")
            if result.stderr:
                error_lines = result.stderr.split('\n')[:5]
                for line in error_lines:
                    if line.strip():
                        print(f"   {line[:100]}")
            return {"status": "partial", "error": result.stderr[:200] if result.stderr else "Unknown error"}
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ Merge timed out: {description}")
        return {"status": "timeout"}
    except Exception as e:
        print(f"❌ Merge error: {description}")
        print(f"Error: {str(e)[:200]}")
        return {"status": "error", "error": str(e)[:200]}


def main():
    """Execute case variations consolidation autonomously."""
    print("="*60)
    print("🚀 CASE VARIATIONS CONSOLIDATION - AUTONOMOUS EXECUTION")
    print("="*60)
    print("\n🔥 GAS FLOWING - JET FUEL = AGI - AUTONOMOUS MODE ACTIVE\n")
    
    # Check existing PRs
    print("🔍 Checking existing PRs...")
    existing = check_existing_prs()
    if existing:
        print(f"✅ Found {len(existing)} existing merged PRs")
    
    results = []
    
    # Execute merges
    for merge_info in CASE_VARIATIONS:
        result = execute_case_variation_merge(
            merge_info["source"],
            merge_info["target"],
            merge_info["description"]
        )
        result["description"] = merge_info["description"]
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("📊 CONSOLIDATION SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = len(results) - successful - skipped
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"⏭️ Skipped: {skipped}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    
    if successful > 0:
        print("\n✅ Successfully merged:")
        for r in results:
            if r["status"] == "success":
                print(f"  - {r['description']}")
    
    if failed > 0:
        print("\n⚠️ Needs attention:")
        for r in results:
            if r["status"] in ["error", "timeout", "partial"]:
                print(f"  - {r['description']}: {r['status']}")
    
    print("\n🔥 AUTONOMOUS EXECUTION COMPLETE")
    print("="*60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

