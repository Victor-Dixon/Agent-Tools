#!/usr/bin/env python3
"""
Unified GitHub - Consolidated GitHub Operations Tool
====================================================

<!-- SSOT Domain: infrastructure -->

Consolidates all GitHub operations into a single unified tool.
Replaces 28+ individual GitHub tools with modular GitHub system.

GitHub Categories:
- pr - PR operations (create, debug, fix)
- repo - Repository operations
- merge - Merge operations
- audit - Audit operations

Author: Agent-5 (Business Intelligence Specialist) - Executing Agent-8's Consolidation Plan
Date: 2025-12-06
V2 Compliant: Yes
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedGitHub:
    """Unified GitHub operations system consolidating all GitHub capabilities."""
    
    def __init__(self):
        """Initialize unified GitHub."""
        self.project_root = project_root
    
    def pr_create(self, repo: str, title: str, body: str, head: str, base: str = "main") -> Dict[str, Any]:
        """Create PR using unified PR creator."""
        try:
            from tools.unified_github_pr_creator import UnifiedGitHubPRCreator
            
            creator = UnifiedGitHubPRCreator()
            result = creator.create_pr(repo, title, body, head, base)
            return {
                "category": "pr",
                "action": "create",
                "repo": repo,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"PR creation failed: {e}")
            return {
                "category": "pr",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def pr_debug(self, repo: str = None, head: str = None) -> Dict[str, Any]:
        """Debug PR creation issues."""
        try:
            from tools.github_pr_debugger import GitHubPRDebugger
            
            debugger = GitHubPRDebugger()
            result = debugger.debug_all(repo, head)
            return {
                "category": "pr",
                "action": "debug",
                "repo": repo,
                "head": head,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"PR debugging failed: {e}")
            return {
                "category": "pr",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def pr_fix(self, repo: str = None, head: str = None) -> Dict[str, Any]:
        """Fix PR creation issues."""
        try:
            from tools.fix_github_prs import fix_pr_issues
            
            result = fix_pr_issues(repo, head)
            return {
                "category": "pr",
                "action": "fix",
                "repo": repo,
                "head": head,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"PR fix failed: {e}")
            return {
                "category": "pr",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def repo_audit(self, repo: str = None) -> Dict[str, Any]:
        """Audit GitHub repository."""
        try:
            from tools.audit_github_repos import audit_repo
            
            if repo:
                result = audit_repo(repo)
            else:
                result = audit_repo(None)
            
            return {
                "category": "repo",
                "action": "audit",
                "repo": repo,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Repository audit failed: {e}")
            return {
                "category": "repo",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def merge_analyze_failures(self) -> Dict[str, Any]:
        """Analyze merge failures."""
        try:
            from tools.analyze_merge_failures import analyze_failures
            
            result = analyze_failures()
            return {
                "category": "merge",
                "action": "analyze_failures",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Merge failure analysis failed: {e}")
            return {
                "category": "merge",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def merge_analyze_plans(self) -> Dict[str, Any]:
        """Analyze merge plans."""
        try:
            from tools.analyze_merge_plans import analyze_plans
            
            result = analyze_plans()
            return {
                "category": "merge",
                "action": "analyze_plans",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Merge plan analysis failed: {e}")
            return {
                "category": "merge",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def merge_complete(self, repo: str, branch: str) -> Dict[str, Any]:
        """Complete merge into main."""
        try:
            from tools.complete_merge_into_main import complete_merge
            
            result = complete_merge(repo, branch)
            return {
                "category": "merge",
                "action": "complete",
                "repo": repo,
                "branch": branch,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Merge completion failed: {e}")
            return {
                "category": "merge",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def audit_architecture(self, repo: str = None) -> Dict[str, Any]:
        """Audit GitHub repository architecture."""
        try:
            from tools.github_architecture_audit import audit_architecture
            
            if repo:
                result = audit_architecture(repo)
            else:
                result = audit_architecture(None)
            
            return {
                "category": "audit",
                "action": "architecture",
                "repo": repo,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Architecture audit failed: {e}")
            return {
                "category": "audit",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """CLI entry point for unified GitHub tool."""
    parser = argparse.ArgumentParser(
        description="Unified GitHub Operations Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tools.unified_github pr create --repo MyRepo --title "PR Title" --body "PR Body" --head feature-branch
  python -m tools.unified_github pr debug --repo MyRepo --head feature-branch
  python -m tools.unified_github pr fix --repo MyRepo --head feature-branch
  python -m tools.unified_github repo audit --repo MyRepo
  python -m tools.unified_github merge analyze-failures
  python -m tools.unified_github merge analyze-plans
  python -m tools.unified_github merge complete --repo MyRepo --branch feature-branch
  python -m tools.unified_github audit architecture --repo MyRepo
        """
    )
    
    parser.add_argument(
        "category",
        choices=["pr", "repo", "merge", "audit"],
        help="GitHub operation category"
    )
    
    parser.add_argument(
        "action",
        help="Action to perform within category"
    )
    
    parser.add_argument("--repo", help="Repository name")
    parser.add_argument("--title", help="PR title")
    parser.add_argument("--body", help="PR body")
    parser.add_argument("--head", help="Head branch")
    parser.add_argument("--base", default="main", help="Base branch (default: main)")
    parser.add_argument("--branch", help="Branch name for merge operations")
    
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    github = UnifiedGitHub()
    results = {}
    
    # Route to appropriate category method
    if args.category == "pr":
        if args.action == "create" and args.repo and args.title and args.head:
            results = github.pr_create(args.repo, args.title, args.body or "", args.head, args.base)
        elif args.action == "debug":
            results = github.pr_debug(args.repo, args.head)
        elif args.action == "fix":
            results = github.pr_fix(args.repo, args.head)
        else:
            results = {"error": f"Invalid PR action or missing parameters: {args.action}"}
    
    elif args.category == "repo":
        if args.action == "audit":
            results = github.repo_audit(args.repo)
        else:
            results = {"error": f"Unknown repo action: {args.action}"}
    
    elif args.category == "merge":
        if args.action == "analyze-failures":
            results = github.merge_analyze_failures()
        elif args.action == "analyze-plans":
            results = github.merge_analyze_plans()
        elif args.action == "complete" and args.repo and args.branch:
            results = github.merge_complete(args.repo, args.branch)
        else:
            results = {"error": f"Invalid merge action or missing parameters: {args.action}"}
    
    elif args.category == "audit":
        if args.action == "architecture":
            results = github.audit_architecture(args.repo)
        else:
            results = {"error": f"Unknown audit action: {args.action}"}
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        if "error" in results:
            print(f"❌ Error: {results['error']}")
        else:
            print(json.dumps(results, indent=2, default=str))
    
    return 0 if "error" not in results else 1


if __name__ == "__main__":
    sys.exit(main())

