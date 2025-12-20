#!/usr/bin/env python3
"""
GitHub Repository ROI Calculator
=================================

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use: python -m tools_v2.toolbelt bi.roi.repo <repo_path>
See: tools_v2/categories/bi_tools.py for the adapter.

Calculate ROI for keeping vs archiving GitHub repositories.
Part of GitHub Consolidation Strategy mission.

ROI = Value / Maintenance Effort

Value Factors:
- Community engagement (stars, forks, watchers)
- Development investment (commits, contributors)
- Code quality (tests, CI/CD, documentation)
- Uniqueness (not duplicate)

Maintenance Effort Factors:
- Codebase size (files, lines)
- Quality gaps (missing LICENSE, CI/CD, tests)
- Complexity (languages, dependencies)

Author: Agent-6 (Mission Planning & Optimization Specialist)
Created: 2025-10-14
Mission: GitHub Consolidation Strategy
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class RepoMetrics:
    """Repository metrics for ROI calculation."""
    
    name: str
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    commits: int = 0
    contributors: int = 0
    has_tests: bool = False
    has_ci_cd: bool = False
    has_license: bool = False
    has_readme: bool = False
    file_count: int = 0
    lines_of_code: int = 0
    languages: list[str] = None
    last_commit_days_ago: int = 0
    is_duplicate: bool = False
    uniqueness_score: int = 0  # 0-100
    
    def __post_init__(self):
        if self.languages is None:
            self.languages = []


def calculate_value_score(metrics: RepoMetrics) -> float:
    """Calculate repository value score."""
    score = 0.0
    
    # Community engagement (40% of value)
    score += metrics.stars * 20  # Stars are valuable
    score += metrics.forks * 10  # Forks show usage
    score += metrics.watchers * 5  # Watchers show interest
    
    # Development investment (30% of value)
    score += metrics.commits * 2  # Each commit has value
    score += metrics.contributors * 15  # Multiple contributors = collaboration
    
    # Code quality (20% of value)
    if metrics.has_tests:
        score += 50  # Tests show professionalism
    if metrics.has_ci_cd:
        score += 40  # CI/CD shows automation
    if metrics.has_license:
        score += 30  # LICENSE shows compliance
    if metrics.has_readme:
        score += 20  # README shows documentation
    
    # Uniqueness (10% of value)
    score += metrics.uniqueness_score * 3  # Unique features matter
    
    # Recency bonus
    if metrics.last_commit_days_ago < 30:
        score += 50  # Active repo bonus
    elif metrics.last_commit_days_ago < 90:
        score += 25  # Recent activity
    
    return score


def calculate_maintenance_effort(metrics: RepoMetrics) -> float:
    """Calculate maintenance effort score."""
    effort = 1.0  # Base effort
    
    # Codebase size (40% of effort)
    effort += metrics.file_count * 0.5  # Each file needs maintenance
    effort += metrics.lines_of_code / 1000  # LOC maintenance burden
    
    # Quality gaps (30% of effort)
    if not metrics.has_tests:
        effort += 20  # Need to add tests
    if not metrics.has_ci_cd:
        effort += 15  # Need to setup CI/CD
    if not metrics.has_license:
        effort += 10  # Need to add LICENSE
    if not metrics.has_readme:
        effort += 10  # Need to write docs
    
    # Complexity (20% of effort)
    effort += len(metrics.languages) * 5  # Multiple languages = complexity
    
    # Staleness penalty (10% of effort)
    if metrics.last_commit_days_ago > 365:
        effort += 30  # Old code needs refresh
    elif metrics.last_commit_days_ago > 180:
        effort += 15  # Moderately stale
    
    return effort


def calculate_roi(metrics: RepoMetrics) -> dict[str, Any]:
    """Calculate ROI for repository."""
    value = calculate_value_score(metrics)
    effort = calculate_maintenance_effort(metrics)
    roi = value / effort
    
    # Determine tier
    if roi >= 10:
        tier = "TIER 1: HIGH ROI - KEEP & POLISH"
        recommendation = "Keep, invest in professional polish"
    elif roi >= 5:
        tier = "TIER 2: MEDIUM ROI - CONSOLIDATE"
        recommendation = "Merge unique features into best version"
    else:
        tier = "TIER 3: LOW ROI - ARCHIVE"
        recommendation = "Archive immediately, not worth maintenance"
    
    return {
        "repo": metrics.name,
        "value_score": round(value, 2),
        "effort_score": round(effort, 2),
        "roi": round(roi, 2),
        "tier": tier,
        "recommendation": recommendation,
    }


def analyze_repository_portfolio(repos: list[RepoMetrics]) -> dict[str, Any]:
    """Analyze entire repository portfolio."""
    results = []
    
    for repo in repos:
        roi_result = calculate_roi(repo)
        results.append(roi_result)
    
    # Sort by ROI (highest first)
    results.sort(key=lambda x: x["roi"], reverse=True)
    
    # Categorize by tier
    tier_1 = [r for r in results if r["roi"] >= 10]
    tier_2 = [r for r in results if 5 <= r["roi"] < 10]
    tier_3 = [r for r in results if r["roi"] < 5]
    
    return {
        "total_repos": len(repos),
        "tier_1_count": len(tier_1),
        "tier_2_count": len(tier_2),
        "tier_3_count": len(tier_3),
        "tier_1": tier_1,
        "tier_2": tier_2,
        "tier_3": tier_3,
        "avg_roi": round(sum(r["roi"] for r in results) / len(results), 2),
    }


def generate_consolidation_strategy(analysis: dict[str, Any]) -> str:
    """Generate consolidation strategy report."""
    report = f"""# GitHub Portfolio Consolidation Strategy
## ROI-Optimized Execution Plan

**Total Repositories:** {analysis['total_repos']}  
**Average ROI:** {analysis['avg_roi']}  
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}

---

## 📊 ROI DISTRIBUTION

**TIER 1: HIGH ROI ({analysis['tier_1_count']} repos)** - KEEP & POLISH
- ROI ≥10
- Action: Professional polish (LICENSE, CI/CD, tests, docs)
- Effort: 2-3 hours per repo
- Priority: HIGH

**TIER 2: MEDIUM ROI ({analysis['tier_2_count']} repos)** - CONSOLIDATE
- ROI 5-10  
- Action: Merge unique features into best versions
- Effort: 4-6 hours per consolidation
- Priority: MEDIUM

**TIER 3: LOW ROI ({analysis['tier_3_count']} repos)** - ARCHIVE
- ROI <5
- Action: Archive immediately
- Effort: 5 minutes per repo
- Priority: QUICK WINS

---

## 🎯 RECOMMENDED EXECUTION ORDER

### Phase 1: Quick Wins (Week 1)
**Archive Tier 3** ({analysis['tier_3_count']} repos)
- Effort: ~{analysis['tier_3_count'] * 5} minutes total
- Impact: {analysis['total_repos']} → {analysis['total_repos'] - analysis['tier_3_count']} repos
- ROI: MAXIMUM (low effort, high impact)

### Phase 2: Strategic Consolidation (Week 2-3)
**Merge Tier 2** ({analysis['tier_2_count']} repos)
- Effort: ~{analysis['tier_2_count'] * 5} hours
- Impact: Preserve unique features
- ROI: HIGH

### Phase 3: Professional Polish (Week 4-6)
**Polish Tier 1** ({analysis['tier_1_count']} repos)
- Effort: ~{analysis['tier_1_count'] * 2.5} hours
- Impact: Portfolio-ready presentation
- ROI: LONG-TERM VALUE

---

## 💎 EXPECTED OUTCOMES

**Portfolio Transformation:**
- Before: {analysis['total_repos']} repos (overwhelming)
- After: ~{analysis['tier_1_count'] + int(analysis['tier_2_count'] / 2)} repos (focused)
- Reduction: {round((1 - (analysis['tier_1_count'] + int(analysis['tier_2_count'] / 2)) / analysis['total_repos']) * 100)}%

**Value Creation:**
- Professional presentation
- Clear project narrative
- Best version of each idea
- Showcase-ready portfolio

---

*Generated by: GitHub Repo ROI Calculator*  
*Agent-6 (Mission Planning & Optimization Specialist)*  
*🐝 WE ARE SWARM ⚡*
"""
    
    return report


__all__ = [
    "RepoMetrics",
    "calculate_value_score",
    "calculate_maintenance_effort",
    "calculate_roi",
    "analyze_repository_portfolio",
    "generate_consolidation_strategy",
]


if __name__ == "__main__":
    # Example usage
    print("GitHub Repository ROI Calculator")
    print("=" * 50)
    print("\nThis tool calculates ROI for repository consolidation decisions.")
    print("\nUsage:")
    print("  from github_repo_roi_calculator import RepoMetrics, calculate_roi")
    print("\n  metrics = RepoMetrics(")
    print("      name='my-repo',")
    print("      stars=10, commits=50, has_tests=True")
    print("  )")
    print("  result = calculate_roi(metrics)")
    print("\n🐝 WE ARE SWARM ⚡")

