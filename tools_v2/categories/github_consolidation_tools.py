"""
GitHub Repository Consolidation Tools - Agent Toolbelt V2
=========================================================

Tools for reviewing, analyzing, and consolidating similar GitHub repositories.

Author: Agent-4 (Captain)
Date: 2025-01-27
V2 Compliance: <300 lines per tool
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..adapters.base_adapter import IToolAdapter, ToolResult
from ..core.tool_spec import ToolSpec

logger = logging.getLogger(__name__)


class GitHubRepoSimilarityAnalyzerTool(IToolAdapter):
    """Analyze GitHub repositories for similarity and consolidation opportunities."""

    def get_name(self) -> str:
        return "github.analyze_similar"

    def get_description(self) -> str:
        return "Analyze GitHub repositories to find similar/duplicate repos for consolidation"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="github.analyze_similar",
            version="1.0.0",
            category="github",
            summary="Analyze repo similarity for consolidation",
            required_params=[],
            optional_params={
                "github_username": None,
                "repo_list": None,
                "similarity_threshold": 0.7,
                "output_file": None,
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Analyze repository similarity."""
        try:
            github_username = params.get("github_username")
            repo_list = params.get("repo_list")
            threshold = params.get("similarity_threshold", 0.7)
            output_file = params.get("output_file")

            # Get repository list
            if repo_list:
                repos = repo_list if isinstance(repo_list, list) else [repo_list]
            elif github_username:
                repos = self._fetch_user_repos(github_username)
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message="Either github_username or repo_list required",
                    exit_code=1,
                )

            # Analyze similarity
            similarity_groups = self._analyze_similarity(repos, threshold)

            # Generate recommendations
            recommendations = self._generate_recommendations(similarity_groups)

            output = {
                "total_repos": len(repos),
                "similarity_groups": similarity_groups,
                "recommendations": recommendations,
                "consolidation_opportunities": len(similarity_groups),
            }

            # Save to file if requested
            if output_file:
                output_path = Path(output_file)
                output_path.write_text(json.dumps(output, indent=2))
                output["output_file"] = str(output_path)

            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"Repository similarity analysis failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )

    def _fetch_user_repos(self, username: str) -> List[str]:
        """Fetch user's repositories from GitHub."""
        try:
            # Try GitHub API first
            try:
                from src.tools.github_scanner import GitHubScanner
                scanner = GitHubScanner()
                repos_info = scanner.list_user_repositories(username=username)
                scanner.close()
                return [repo.full_name for repo in repos_info]
            except Exception as api_error:
                logger.debug(f"GitHub API failed, trying gh CLI: {api_error}")
            
            # Fallback to gh CLI
            result = subprocess.run(
                ["gh", "repo", "list", username, "--json", "name", "--limit", "1000"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                repos_data = json.loads(result.stdout)
                return [f"{username}/{repo['name']}" for repo in repos_data]
            else:
                logger.warning(f"Failed to fetch repos via gh CLI: {result.stderr}")
                return []
        except Exception as e:
            logger.warning(f"Failed to fetch repos: {e}")
            return []

    def _analyze_similarity(
        self, repos: List[str], threshold: float
    ) -> List[Dict[str, Any]]:
        """Analyze similarity between repositories."""
        groups = []
        analyzed = set()

        for i, repo1 in enumerate(repos):
            if repo1 in analyzed:
                continue

            similar = [repo1]
            for repo2 in repos[i + 1 :]:
                if repo2 in analyzed:
                    continue

                similarity = self._calculate_similarity(repo1, repo2)
                if similarity >= threshold:
                    similar.append(repo2)
                    analyzed.add(repo2)

            if len(similar) > 1:
                groups.append(
                    {
                        "repos": similar,
                        "similarity_score": self._get_group_similarity(similar),
                        "recommendation": self._recommend_primary(similar),
                    }
                )
                analyzed.add(repo1)

        return groups

    def _calculate_similarity(self, repo1: str, repo2: str) -> float:
        """Calculate similarity score between two repos."""
        # Name similarity (40% weight)
        name1 = repo1.split("/")[-1].lower()
        name2 = repo2.split("/")[-1].lower()
        name_sim = self._string_similarity(name1, name2)

        # Try to get repo metadata for better similarity
        desc_sim = 0.0
        lang_sim = 0.0
        
        try:
            from src.tools.github_scanner import GitHubScanner
            scanner = GitHubScanner()
            
            # Get repo info
            owner1, name1_only = repo1.split("/")
            owner2, name2_only = repo2.split("/")
            
            try:
                info1 = scanner.get_repository(owner1, name1_only)
                info2 = scanner.get_repository(owner2, name2_only)
                
                # Description similarity (30% weight)
                if info1.description and info2.description:
                    desc_sim = self._string_similarity(
                        info1.description.lower(), 
                        info2.description.lower()
                    )
                
                # Language similarity (20% weight)
                if info1.language and info2.language:
                    lang_sim = 1.0 if info1.language == info2.language else 0.0
                
                # Topics similarity (10% weight)
                topics_sim = 0.0
                if info1.topics and info2.topics:
                    topics1 = set(t.lower() for t in info1.topics)
                    topics2 = set(t.lower() for t in info2.topics)
                    if topics1 or topics2:
                        topics_sim = len(topics1 & topics2) / len(topics1 | topics2) if (topics1 | topics2) else 0.0
                
                scanner.close()
                
                # Weighted similarity
                return (name_sim * 0.4) + (desc_sim * 0.3) + (lang_sim * 0.2) + (topics_sim * 0.1)
            except Exception:
                scanner.close()
                pass
        except Exception:
            pass
        
        # Fallback to name similarity only
        return name_sim * 0.5

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (simple Jaccard)."""
        set1 = set(s1)
        set2 = set(s2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _get_group_similarity(self, repos: List[str]) -> float:
        """Get average similarity for a group."""
        if len(repos) < 2:
            return 1.0

        total = 0.0
        count = 0
        for i, repo1 in enumerate(repos):
            for repo2 in repos[i + 1 :]:
                total += self._calculate_similarity(repo1, repo2)
                count += 1

        return total / count if count > 0 else 0.0

    def _recommend_primary(self, repos: List[str]) -> Dict[str, Any]:
        """Recommend which repo should be primary using ROI calculator."""
        try:
            # Use ROI calculator to pick best repo
            from tools_v2.toolbelt_core import ToolbeltCore
            toolbelt = ToolbeltCore()
            
            best_repo = repos[0]
            best_roi = 0.0
            
            for repo in repos:
                try:
                    # Calculate ROI for this repo
                    roi_result = toolbelt.run("bi.roi.repo", {
                        "repo_path": repo,
                        "output_format": "json"
                    })
                    
                    if roi_result.success and roi_result.output:
                        # Parse ROI from output
                        import re
                        roi_match = re.search(r'"roi":\s*([\d.]+)', str(roi_result.output))
                        if roi_match:
                            roi = float(roi_match.group(1))
                            if roi > best_roi:
                                best_roi = roi
                                best_repo = repo
                except Exception:
                    continue
            
            return {
                "primary": best_repo,
                "reason": f"Highest ROI ({best_roi:.2f})" if best_roi > 0 else "First in list (ROI calculation failed)",
                "action": "consolidate_into",
                "roi": best_roi,
            }
        except Exception as e:
            logger.warning(f"ROI calculation failed, using first repo: {e}")
            return {
                "primary": repos[0],
                "reason": "First in list (ROI calculator unavailable)",
                "action": "consolidate_into",
            }

    def _generate_recommendations(
        self, groups: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate consolidation recommendations."""
        recommendations = []

        for group in groups:
            recommendations.append(
                {
                    "action": "consolidate",
                    "repos": group["repos"],
                    "primary": group["recommendation"]["primary"],
                    "secondary": [
                        r for r in group["repos"] if r != group["recommendation"]["primary"]
                    ],
                    "similarity": group["similarity_score"],
                    "steps": [
                        f"1. Review {group['recommendation']['primary']} as primary",
                        f"2. Extract unique features from secondary repos",
                        f"3. Merge into primary",
                        f"4. Archive secondary repos",
                    ],
                }
            )

        return recommendations


class GitHubRepoConsolidationPlannerTool(IToolAdapter):
    """Create detailed consolidation plan for similar repositories."""

    def get_name(self) -> str:
        return "github.plan_consolidation"

    def get_description(self) -> str:
        return "Create detailed consolidation plan for similar GitHub repositories"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="github.plan_consolidation",
            version="1.0.0",
            category="github",
            summary="Plan repository consolidation",
            required_params=["primary_repo", "secondary_repos"],
            optional_params={"output_file": None, "strategy": "merge"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        if not params.get("primary_repo"):
            return (False, ["primary_repo"])
        if not params.get("secondary_repos"):
            return (False, ["secondary_repos"])
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Create consolidation plan."""
        try:
            primary = params["primary_repo"]
            secondary = (
                params["secondary_repos"]
                if isinstance(params["secondary_repos"], list)
                else [params["secondary_repos"]]
            )
            strategy = params.get("strategy", "merge")
            output_file = params.get("output_file")

            # Analyze each repo
            primary_analysis = self._analyze_repo(primary)
            secondary_analyses = [self._analyze_repo(repo) for repo in secondary]

            # Create plan
            plan = {
                "primary_repo": primary,
                "secondary_repos": secondary,
                "strategy": strategy,
                "primary_analysis": primary_analysis,
                "secondary_analyses": secondary_analyses,
                "consolidation_steps": self._create_steps(
                    primary, secondary, strategy
                ),
                "estimated_effort": self._estimate_effort(secondary),
                "risks": self._identify_risks(primary, secondary),
            }

            # Save plan
            if output_file:
                plan_path = Path(output_file)
                plan_path.write_text(json.dumps(plan, indent=2))
                plan["plan_file"] = str(plan_path)

            return ToolResult(success=True, output=plan)

        except Exception as e:
            logger.error(f"Consolidation planning failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )

    def _analyze_repo(self, repo: str) -> Dict[str, Any]:
        """Analyze a single repository using GitHub API."""
        try:
            from src.tools.github_scanner import GitHubScanner
            scanner = GitHubScanner()
            
            owner, name = repo.split("/")
            info = scanner.get_repository(owner, name)
            languages = scanner.get_repository_languages(owner, name)
            
            scanner.close()
            
            return {
                "name": repo,
                "full_name": info.full_name,
                "description": info.description,
                "stars": info.stars,
                "forks": info.forks,
                "open_issues": info.open_issues,
                "last_updated": info.last_updated.isoformat() if info.last_updated else None,
                "languages": list(languages.keys()),
                "language": info.language,
                "topics": info.topics,
                "size_kb": info.size_kb,
                "url": info.url,
                "clone_url": info.clone_url,
            }
        except Exception as e:
            logger.warning(f"Failed to analyze repo {repo}: {e}")
            return {
                "name": repo,
                "stars": 0,
                "forks": 0,
                "last_updated": None,
                "languages": [],
                "has_tests": False,
                "has_ci_cd": False,
                "error": str(e),
            }

    def _create_steps(
        self, primary: str, secondary: List[str], strategy: str
    ) -> List[str]:
        """Create consolidation steps."""
        steps = [
            f"1. Review {primary} as primary repository",
            f"2. Clone all repositories for analysis",
        ]

        for repo in secondary:
            steps.append(f"3. Extract unique features from {repo}")
            steps.append(f"4. Compare with {primary}")

        steps.extend(
            [
                f"5. Merge unique features into {primary}",
                f"6. Test merged functionality",
                f"7. Update documentation in {primary}",
                f"8. Archive secondary repositories",
            ]
        )

        return steps

    def _estimate_effort(self, secondary: List[str]) -> Dict[str, Any]:
        """Estimate consolidation effort."""
        hours_per_repo = 4
        return {
            "total_hours": len(secondary) * hours_per_repo,
            "repos": len(secondary),
            "hours_per_repo": hours_per_repo,
        }

    def _identify_risks(
        self, primary: str, secondary: List[str]
    ) -> List[Dict[str, Any]]:
        """Identify consolidation risks."""
        return [
            {
                "risk": "Data loss",
                "mitigation": "Backup all repos before consolidation",
            },
            {
                "risk": "Breaking changes",
                "mitigation": "Test thoroughly before archiving",
            },
            {
                "risk": "External dependencies",
                "mitigation": "Check for external references to secondary repos",
            },
        ]


class GitHubRepoMergeExecutorTool(IToolAdapter):
    """
    Execute GitHub repository merges automatically.
    
    SSOT: Wraps tools/repo_safe_merge.py to maintain single source of truth.
    The actual merge logic is in repo_safe_merge.py (SafeRepoMerge class).
    """

    def get_name(self) -> str:
        return "github.execute_merge"

    def get_description(self) -> str:
        return "Execute GitHub repository merge automatically (wraps repo_safe_merge.py for SSOT compliance)"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="github.execute_merge",
            version="1.0.0",
            category="github",
            summary="Execute repository merge via repo_safe_merge.py (SSOT)",
            required_params=["target_repo", "source_repo"],
            optional_params={
                "merge_message": None,
                "commit_message": None,
                "dry_run": False,
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        if not params.get("target_repo"):
            return (False, ["target_repo"])
        if not params.get("source_repo"):
            return (False, ["source_repo"])
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """
        Execute repository merge by calling repo_safe_merge.py via subprocess.
        
        SSOT: Uses tools/repo_safe_merge.py as single source of truth.
        Avoids import issues by calling script directly.
        """
        try:
            target_repo = params["target_repo"]
            source_repo = params["source_repo"]
            dry_run = params.get("dry_run", False)

            # Get script path
            from pathlib import Path
            script_path = Path(__file__).resolve().parents[2] / "tools" / "repo_safe_merge.py"
            
            if not script_path.exists():
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"repo_safe_merge.py not found at {script_path}",
                    exit_code=1,
                )

            # Build command
            cmd = ["python", str(script_path), target_repo, source_repo]
            if not dry_run:
                cmd.append("--execute")

            # Execute script (SSOT implementation)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for merge operations
                cwd=Path(__file__).resolve().parents[2],
            )

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    output={
                        "status": "dry_run" if dry_run else "merged",
                        "target_repo": target_repo,
                        "source_repo": source_repo,
                        "message": f"Merge {'simulated' if dry_run else 'executed'} successfully via repo_safe_merge.py (SSOT)",
                        "stdout": result.stdout,
                    },
                )
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Merge failed: {result.stderr or result.stdout}",
                    exit_code=result.returncode,
                )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output=None,
                error_message="Merge operation timed out (exceeded 10 minutes)",
                exit_code=1,
            )
        except Exception as e:
            logger.error(f"Repository merge execution failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )

