#!/usr/bin/env python3
"""
GitHub Architecture Audit - Agent-7
====================================

INDEPENDENT architectural analysis of GitHub repos.
NO bias from Agent-6's ROI analysis.
Architecture-first evaluation criteria.

Mission: Unbiased architecture review
Agent: Agent-7 (Architecture Specialist)
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import os

# Architecture Evaluation Criteria
class ArchitectureCriteria:
    """Architecture-focused evaluation framework."""
    
    # Core Architecture Principles
    SOLID_PRINCIPLES = ["Single Responsibility", "Open/Closed", "Liskov", "Interface Segregation", "Dependency Inversion"]
    CLEAN_CODE = ["Modularity", "Separation of Concerns", "DRY", "KISS", "YAGNI"]
    
    # Architecture Red Flags
    RED_FLAGS = [
        "monolithic_single_file",
        "circular_dependencies",
        "tight_coupling",
        "no_separation_of_concerns",
        "god_objects",
        "spaghetti_code"
    ]
    
    # Architecture Quality Indicators
    QUALITY_INDICATORS = [
        "clear_structure",
        "modular_design",
        "test_coverage",
        "documentation",
        "ci_cd_pipeline",
        "dependency_management"
    ]

def scan_repo_architecture(repo_path: Path) -> Dict[str, Any]:
    """Scan repository for architectural quality."""
    
    result = {
        "repo_name": repo_path.name,
        "architecture_score": 0,
        "structure_quality": "unknown",
        "modularity": "unknown",
        "red_flags": [],
        "strengths": [],
        "recommendation": "unknown",
        "tier": "unknown"
    }
    
    if not repo_path.exists():
        result["recommendation"] = "SKIP - Not cloned"
        return result
    
    # Check project structure
    has_src = (repo_path / "src").exists()
    has_tests = (repo_path / "tests").exists() or (repo_path / "test").exists()
    has_docs = (repo_path / "docs").exists() or (repo_path / "documentation").exists()
    has_config = (repo_path / "config").exists() or (repo_path / ".config").exists()
    
    # Check for architecture files
    has_architecture = any([
        (repo_path / f).exists() for f in 
        ["ARCHITECTURE.md", "docs/ARCHITECTURE.md", "DESIGN.md", "docs/DESIGN.md"]
    ])
    
    # Check for modularity indicators
    has_modules = has_src and len(list((repo_path / "src").glob("*"))) > 1 if has_src else False
    has_clear_layers = all([has_src, has_tests])
    
    # Count Python files for complexity assessment
    py_files = list(repo_path.glob("**/*.py"))
    py_files = [f for f in py_files if ".venv" not in str(f) and "venv" not in str(f) and "__pycache__" not in str(f)]
    
    # Count JS/TS files
    js_files = list(repo_path.glob("**/*.js")) + list(repo_path.glob("**/*.ts"))
    js_files = [f for f in js_files if "node_modules" not in str(f)]
    
    # Count total code files
    code_files = py_files + js_files
    
    # Check for dependency management
    has_requirements = (repo_path / "requirements.txt").exists()
    has_package_json = (repo_path / "package.json").exists()
    has_pyproject = (repo_path / "pyproject.toml").exists()
    has_setup_py = (repo_path / "setup.py").exists()
    
    # Check for CI/CD
    has_github_actions = (repo_path / ".github" / "workflows").exists()
    has_ci = has_github_actions
    
    # Check for tests
    test_files = []
    if has_tests:
        test_files = list((repo_path / "tests").glob("test_*.py")) if (repo_path / "tests").exists() else []
        if (repo_path / "test").exists():
            test_files.extend(list((repo_path / "test").glob("test_*.py")))
    
    # Check for README quality
    readme_files = list(repo_path.glob("README.md")) + list(repo_path.glob("README.rst"))
    has_readme = len(readme_files) > 0
    readme_size = readme_files[0].stat().st_size if readme_files else 0
    quality_readme = readme_size > 1000  # At least 1KB
    
    # Calculate architecture score (0-100)
    score = 0
    
    # Structure (30 points)
    if has_src: score += 10
    if has_tests: score += 10
    if has_clear_layers: score += 10
    
    # Modularity (20 points)
    if has_modules: score += 10
    if has_config: score += 5
    if has_docs: score += 5
    
    # Quality (20 points)
    if len(test_files) > 5: score += 10
    elif len(test_files) > 0: score += 5
    if quality_readme: score += 10
    elif has_readme: score += 5
    
    # Automation (15 points)
    if has_ci: score += 15
    
    # Documentation (15 points)
    if has_architecture: score += 10
    if has_docs: score += 5
    
    result["architecture_score"] = score
    
    # Assess structure quality
    if score >= 75:
        result["structure_quality"] = "EXCELLENT"
        result["tier"] = "TIER 1 - KEEP & SHOWCASE"
    elif score >= 50:
        result["structure_quality"] = "GOOD"
        result["tier"] = "TIER 2 - KEEP & IMPROVE"
    elif score >= 30:
        result["structure_quality"] = "FAIR"
        result["tier"] = "TIER 3 - CONSOLIDATE"
    else:
        result["structure_quality"] = "POOR"
        result["tier"] = "ARCHIVE - Low architectural value"
    
    # Identify red flags
    if len(code_files) < 3 and len(code_files) > 0:
        result["red_flags"].append("Too simple - single file project")
    
    if not has_tests and len(code_files) > 10:
        result["red_flags"].append("No tests for complex project")
    
    if not has_readme:
        result["red_flags"].append("No README")
    
    if len(code_files) > 50 and not has_src:
        result["red_flags"].append("Large project without clear structure")
    
    if not has_requirements and not has_package_json and len(py_files) > 0:
        result["red_flags"].append("No dependency management")
    
    # Identify strengths
    if has_clear_layers:
        result["strengths"].append("Clear layered architecture")
    
    if has_modules:
        result["strengths"].append("Modular design")
    
    if has_ci:
        result["strengths"].append("CI/CD automation")
    
    if len(test_files) > 10:
        result["strengths"].append("Good test coverage")
    
    if has_architecture:
        result["strengths"].append("Documented architecture")
    
    # Recommendation
    if score >= 75:
        result["recommendation"] = "KEEP - High architectural quality"
    elif score >= 50:
        result["recommendation"] = "KEEP - Good foundation, needs improvement"
    elif score >= 30:
        result["recommendation"] = "CONSOLIDATE - Merge with similar project"
    else:
        result["recommendation"] = "ARCHIVE - Poor architecture, not worth maintaining"
    
    # Additional metadata
    result["file_counts"] = {
        "python": len(py_files),
        "javascript": len(js_files),
        "tests": len(test_files),
        "total_code": len(code_files)
    }
    
    result["has_structure"] = {
        "src": has_src,
        "tests": has_tests,
        "docs": has_docs,
        "config": has_config,
        "ci_cd": has_ci,
        "architecture_doc": has_architecture
    }
    
    return result


def get_user_repos() -> List[str]:
    """Fetch list of user's GitHub repositories."""
    try:
        result = subprocess.run(
            ["gh", "repo", "list", "--json", "name", "--limit", "1000"],
            capture_output=True,
            text=True,
            check=True
        )
        repos_data = json.loads(result.stdout)
        return [repo["name"] for repo in repos_data]
    except Exception as e:
        print(f"⚠️ Could not fetch repo list via gh CLI: {e}")
        return []


def main():
    """Execute independent architecture audit."""
    print("=" * 80)
    print("🏗️ GITHUB ARCHITECTURE AUDIT - AGENT-7")
    print("=" * 80)
    print("Mission: Unbiased architectural assessment")
    print("Approach: Architecture-first evaluation")
    print("Directive: Independent from ROI analysis")
    print("=" * 80)
    print()
    
    # Check if audit directory exists
    audit_dir = Path("D:/GitHub_Audit_Test")
    
    if not audit_dir.exists():
        print(f"❌ Audit directory not found: {audit_dir}")
        print("Will analyze using existing audit data...")
        # Fallback to reading from audit results
        audit_dir = None
    
    # Get list of repos to analyze
    if audit_dir and audit_dir.exists():
        repos_to_analyze = [d for d in audit_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        print(f"📦 Found {len(repos_to_analyze)} cloned repos in {audit_dir}")
    else:
        # Try to get from GitHub API
        repo_names = get_user_repos()
        if repo_names:
            print(f"📦 Found {len(repo_names)} repos from GitHub API")
            print("⚠️ Will analyze structure without cloning (limited assessment)")
            repos_to_analyze = []  # Can't analyze without clones
        else:
            print("❌ Could not get repo list. Cannot proceed.")
            return 1
    
    # Perform architecture analysis
    results = []
    tier_1_count = 0
    tier_2_count = 0
    tier_3_count = 0
    archive_count = 0
    
    for repo_path in repos_to_analyze:
        print(f"\n🔍 Analyzing: {repo_path.name}")
        print("-" * 60)
        
        result = scan_repo_architecture(repo_path)
        results.append(result)
        
        print(f"  Architecture Score: {result['architecture_score']}/100")
        print(f"  Structure Quality: {result['structure_quality']}")
        print(f"  Tier: {result['tier']}")
        print(f"  Recommendation: {result['recommendation']}")
        
        if result['strengths']:
            print(f"  ✅ Strengths: {', '.join(result['strengths'])}")
        
        if result['red_flags']:
            print(f"  ⚠️ Red Flags: {', '.join(result['red_flags'])}")
        
        # Count tiers
        if "TIER 1" in result['tier']:
            tier_1_count += 1
        elif "TIER 2" in result['tier']:
            tier_2_count += 1
        elif "TIER 3" in result['tier']:
            tier_3_count += 1
        elif "ARCHIVE" in result['tier']:
            archive_count += 1
    
    # Sort results by score
    results.sort(key=lambda x: x['architecture_score'], reverse=True)
    
    # Generate summary
    print()
    print("=" * 80)
    print("📊 ARCHITECTURE AUDIT SUMMARY")
    print("=" * 80)
    print(f"Total Repos Analyzed: {len(results)}")
    print()
    print(f"TIER 1 (KEEP & SHOWCASE): {tier_1_count} repos ({tier_1_count/len(results)*100:.1f}%)")
    print(f"TIER 2 (KEEP & IMPROVE): {tier_2_count} repos ({tier_2_count/len(results)*100:.1f}%)")
    print(f"TIER 3 (CONSOLIDATE): {tier_3_count} repos ({tier_3_count/len(results)*100:.1f}%)")
    print(f"ARCHIVE: {archive_count} repos ({archive_count/len(results)*100:.1f}%)")
    print()
    
    # Top performers
    print("🏆 TOP 5 ARCHITECTURAL QUALITY:")
    for i, result in enumerate(results[:5], 1):
        print(f"  {i}. {result['repo_name']} - Score: {result['architecture_score']}/100")
    
    print()
    print("⚠️ BOTTOM 5 (ARCHIVE CANDIDATES):")
    for i, result in enumerate(results[-5:], 1):
        print(f"  {i}. {result['repo_name']} - Score: {result['architecture_score']}/100")
    
    # Save results
    output_file = "GITHUB_ARCHITECTURE_AUDIT_RESULTS.json"
    with open(output_file, 'w') as f:
        json.dump({
            "audit_date": datetime.now().isoformat(),
            "agent": "Agent-7",
            "approach": "Architecture-first evaluation",
            "total_repos": len(results),
            "tier_breakdown": {
                "tier_1": tier_1_count,
                "tier_2": tier_2_count,
                "tier_3": tier_3_count,
                "archive": archive_count
            },
            "results": results
        }, f, indent=2)
    
    print()
    print(f"✅ Results saved: {output_file}")
    print()
    print(f"📊 ARCHIVE RECOMMENDATION: {archive_count}/{len(results)} repos ({archive_count/len(results)*100:.1f}%)")
    
    return 0


if __name__ == "__main__":
    exit(main())


