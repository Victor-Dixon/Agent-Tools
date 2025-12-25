#!/usr/bin/env python3
"""
Unified Verifier - Consolidated Verification Tool
=================================================

<!-- SSOT Domain: qa -->

Consolidates all verification capabilities into a single unified tool.
Replaces 25+ individual verification tools with modular verification system.

Verification Categories:
- repo: Repository verification
- merge: Merge verification
- file: File verification
- cicd: CI/CD verification
- credentials: Credential verification

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-06
V2 Compliant: Yes (<400 lines)
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedVerifier:
    """Unified verification system consolidating all verification capabilities."""
    
    def __init__(self):
        """Initialize unified verifier."""
        self.project_root = project_root
        
    def verify_repo(self, action: str = "phase1", **kwargs) -> Dict[str, Any]:
        """Handle repository verification operations."""
        try:
            if action == "phase1":
                from tools.verify_phase1_repos import verify_phase1_repos
                result = verify_phase1_repos()
                return {
                    "category": "repo",
                    "action": "phase1",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "archived":
                from tools.verify_archived_repos import verify_archived_repos
                result = verify_archived_repos()
                return {
                    "category": "repo",
                    "action": "archived",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "merge-status":
                from tools.verify_repo_merge_status import verify_merge_status
                result = verify_merge_status()
                return {
                    "category": "repo",
                    "action": "merge-status",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "repo",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["phase1", "archived", "merge-status"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Repo verification failed: {e}")
            return {
                "category": "repo",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def verify_merge(self, action: str = "batch1", **kwargs) -> Dict[str, Any]:
        """Handle merge verification operations."""
        try:
            if action == "batch1":
                from tools.verify_batch1_main_branches import verify_branches
                from tools.verify_batch1_main_content import verify_content
                from tools.verify_batch1_merge_commits import verify_commits
                
                branches = verify_branches()
                content = verify_content()
                commits = verify_commits()
                
                return {
                    "category": "merge",
                    "action": "batch1",
                    "branches": branches,
                    "content": content,
                    "commits": commits,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "batch2":
                from tools.verify_batch2_prs import verify_prs
                from tools.verify_batch2_target_repos import verify_targets
                
                prs = verify_prs()
                targets = verify_targets()
                
                return {
                    "category": "merge",
                    "action": "batch2",
                    "prs": prs,
                    "targets": targets,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "contract-leads":
                from tools.verify_contract_leads_merge import verify_merge
                result = verify_merge()
                return {
                    "category": "merge",
                    "action": "contract-leads",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "failed":
                from tools.verify_failed_merge_repos import verify_failed
                result = verify_failed()
                return {
                    "category": "merge",
                    "action": "failed",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "merge",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["batch1", "batch2", "contract-leads", "failed"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Merge verification failed: {e}")
            return {
                "category": "merge",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def verify_file(self, action: str = "usage", **kwargs) -> Dict[str, Any]:
        """Handle file verification operations."""
        try:
            file_path = kwargs.get("file")
            
            if action == "usage":
                from tools.verify_file_usage_enhanced import verify_file_usage
                if file_path:
                    result = verify_file_usage(file_path)
                else:
                    result = verify_file_usage()
                return {
                    "category": "file",
                    "action": "usage",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "comprehensive":
                from tools.verify_file_comprehensive import verify_comprehensive
                if file_path:
                    result = verify_comprehensive(file_path)
                else:
                    result = verify_comprehensive()
                return {
                    "category": "file",
                    "action": "comprehensive",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "ssot":
                from tools.verify_bulk_deletion_ssot import verify_ssot
                result = verify_ssot()
                return {
                    "category": "file",
                    "action": "ssot",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "file",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["usage", "comprehensive", "ssot"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"File verification failed: {e}")
            return {
                "category": "file",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def verify_cicd(self, action: str = "github", **kwargs) -> Dict[str, Any]:
        """Handle CI/CD verification operations."""
        try:
            if action == "github":
                from tools.verify_github_repo_cicd import verify_cicd
                repo = kwargs.get("repo")
                if repo:
                    result = verify_cicd(repo)
                else:
                    result = verify_cicd()
                return {
                    "category": "cicd",
                    "action": "github",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "merged":
                from tools.verify_merged_repo_cicd_enhanced import verify_merged_cicd
                result = verify_merged_cicd()
                return {
                    "category": "cicd",
                    "action": "merged",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "cicd",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["github", "merged"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"CI/CD verification failed: {e}")
            return {
                "category": "cicd",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def verify_credentials(self, action: str = "hostinger", **kwargs) -> Dict[str, Any]:
        """Handle credential verification operations."""
        try:
            if action == "hostinger":
                from tools.verify_hostinger_credentials import verify_credentials
                result = verify_credentials()
                return {
                    "category": "credentials",
                    "action": "hostinger",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif action == "discord":
                from tools.verify_discord_buttons import verify_buttons
                result = verify_buttons()
                return {
                    "category": "credentials",
                    "action": "discord",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "credentials",
                    "error": f"Unknown action: {action}",
                    "available_actions": ["hostinger", "discord"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Credential verification failed: {e}")
            return {
                "category": "credentials",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for unified verifier."""
    parser = argparse.ArgumentParser(
        description="Unified Verifier - Consolidated Verification Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--category",
        choices=["repo", "merge", "file", "cicd", "credentials", "all"],
        default="all",
        help="Category of verification operations"
    )
    
    parser.add_argument(
        "--action",
        type=str,
        help="Specific action to perform (varies by category)"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="File path for file-specific operations"
    )
    
    parser.add_argument(
        "--repo",
        type=str,
        help="Repository name for repo-specific operations"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    verifier = UnifiedVerifier()
    results = []
    
    categories = ["repo", "merge", "file", "cicd", "credentials"] if args.category == "all" else [args.category]
    
    for category in categories:
        action = args.action or {
            "repo": "phase1",
            "merge": "batch1",
            "file": "usage",
            "cicd": "github",
            "credentials": "hostinger"
        }.get(category, "phase1")
        
        kwargs = {
            "file": args.file,
            "repo": args.repo
        }
        
        if category == "repo":
            result = verifier.verify_repo(action=action, **kwargs)
        elif category == "merge":
            result = verifier.verify_merge(action=action, **kwargs)
        elif category == "file":
            result = verifier.verify_file(action=action, **kwargs)
        elif category == "cicd":
            result = verifier.verify_cicd(action=action, **kwargs)
        elif category == "credentials":
            result = verifier.verify_credentials(action=action, **kwargs)
        else:
            result = {
                "category": category,
                "error": "Unknown category",
                "timestamp": datetime.now().isoformat()
            }
        
        results.append(result)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            if "error" in result:
                print(f"❌ {result['category']}: {result['error']}")
            else:
                print(f"✅ {result['category']}: {result.get('action', 'completed')}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

