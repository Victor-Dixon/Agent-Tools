#!/usr/bin/env python3
"""
Professional Repository Analyzer

Comprehensive analysis of GitHub repositories including:
- Project categorization
- Duplicate/similarity detection
- Code quality metrics
- Technology stack identification
- Readiness assessment
- Consolidation recommendations

Usage:
    python tools/migration/repo_analyzer.py --analyze /path/to/repos
    python tools/migration/repo_analyzer.py --similarity /path/to/repos
    python tools/migration/repo_analyzer.py --report /path/to/repos
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import ast
except ImportError:
    ast = None


@dataclass
class RepoMetadata:
    """Metadata for a single repository."""

    name: str
    path: Path
    language: str = "unknown"
    primary_language: str = "unknown"
    languages: Dict[str, int] = field(default_factory=dict)
    file_count: int = 0
    total_lines: int = 0
    has_readme: bool = False
    has_license: bool = False
    has_requirements: bool = False
    has_package_json: bool = False
    has_pyproject: bool = False
    has_cargo: bool = False
    has_go_mod: bool = False
    technologies: Set[str] = field(default_factory=set)
    frameworks: Set[str] = field(default_factory=set)
    dependencies: Set[str] = field(default_factory=set)
    description: str = ""
    last_commit: Optional[str] = None
    commit_count: int = 0
    branch_count: int = 0
    tag_count: int = 0
    size_mb: float = 0.0
    is_empty: bool = False
    has_tests: bool = False
    test_framework: str = ""
    has_docs: bool = False
    has_ci: bool = False
    similarity_hash: str = ""
    project_type: str = "unknown"
    status: str = "unknown"  # active, archived, abandoned, duplicate
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["path"] = str(self.path)
        data["technologies"] = sorted(list(self.technologies))
        data["frameworks"] = sorted(list(self.frameworks))
        data["dependencies"] = sorted(list(self.dependencies))
        return data


class RepoAnalyzer:
    """Comprehensive repository analyzer."""

    # Technology indicators
    PYTHON_INDICATORS = ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", ".py"]
    NODE_INDICATORS = ["package.json", "yarn.lock", "package-lock.json", ".js", ".ts"]
    RUST_INDICATORS = ["Cargo.toml", "Cargo.lock", ".rs"]
    GO_INDICATORS = ["go.mod", "go.sum", ".go"]
    DOCKER_INDICATORS = ["Dockerfile", "docker-compose.yml", ".dockerignore"]

    # Framework indicators
    FRAMEWORKS = {
        "django": ["django", "manage.py"],
        "flask": ["flask", "app.py"],
        "fastapi": ["fastapi", "uvicorn"],
        "react": ["react", "create-react-app"],
        "vue": ["vue", "vue.config.js"],
        "next": ["next.config.js", "next"],
        "express": ["express", "app.js"],
        "spring": ["pom.xml", "application.properties"],
        "rails": ["Gemfile", "config.ru"],
    }

    def __init__(self, repos_dir: Path):
        """Initialize analyzer."""
        self.repos_dir = Path(repos_dir).expanduser().resolve()
        self.repos: Dict[str, RepoMetadata] = {}
        self.similarity_groups: Dict[str, List[str]] = defaultdict(list)

    def analyze_repo(self, repo_path: Path) -> RepoMetadata:
        """Analyze a single repository."""
        repo_name = repo_path.name
        print(f"  Analyzing {repo_name}...", end="\r")

        metadata = RepoMetadata(name=repo_name, path=repo_path)

        if not repo_path.exists() or not repo_path.is_dir():
            metadata.status = "invalid"
            return metadata

        # Check if it's a git repo
        if not (repo_path / ".git").exists():
            metadata.status = "not-git"
            return metadata

        # Basic file analysis
        self._analyze_files(repo_path, metadata)

        # Language detection
        self._detect_language(repo_path, metadata)

        # Technology stack
        self._detect_technologies(repo_path, metadata)

        # Dependencies
        self._detect_dependencies(repo_path, metadata)

        # Git information
        self._analyze_git(repo_path, metadata)

        # Project type
        self._detect_project_type(repo_path, metadata)

        # Similarity hash
        metadata.similarity_hash = self._calculate_similarity_hash(repo_path, metadata)

        # Status assessment
        self._assess_status(repo_path, metadata)

        return metadata

    def _analyze_files(self, repo_path: Path, metadata: RepoMetadata):
        """Analyze files in repository."""
        total_lines = 0
        file_count = 0
        languages = defaultdict(int)

        for file_path in repo_path.rglob("*"):
            if file_path.is_dir():
                continue

            # Skip .git and common ignore patterns
            if any(part.startswith(".") and part != ".gitignore" for part in file_path.parts):
                continue

            file_count += 1

            # Check for important files
            if file_path.name.lower() == "readme.md":
                metadata.has_readme = True
            elif file_path.name.lower() in ["license", "license.txt", "license.md"]:
                metadata.has_license = True
            elif file_path.name == "requirements.txt":
                metadata.has_requirements = True
            elif file_path.name == "package.json":
                metadata.has_package_json = True
            elif file_path.name == "pyproject.toml":
                metadata.has_pyproject = True
            elif file_path.name == "Cargo.toml":
                metadata.has_cargo = True
            elif file_path.name == "go.mod":
                metadata.has_go_mod = True
            elif file_path.name in ["Dockerfile", "docker-compose.yml"]:
                metadata.technologies.add("docker")
            elif file_path.name in [".github/workflows", ".gitlab-ci.yml", ".travis.yml"]:
                metadata.has_ci = True

            # Count lines
            try:
                if file_path.suffix:
                    ext = file_path.suffix[1:]  # Remove dot
                    if ext:
                        languages[ext] += 1

                # Count lines for text files
                if file_path.suffix in [".py", ".js", ".ts", ".rs", ".go", ".java", ".md", ".txt"]:
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            lines = len(f.readlines())
                            total_lines += lines
                    except Exception:
                        pass
            except Exception:
                pass

        metadata.file_count = file_count
        metadata.total_lines = total_lines
        metadata.languages = dict(languages)

    def _detect_language(self, repo_path: Path, metadata: RepoMetadata):
        """Detect primary programming language."""
        lang_counts = defaultdict(int)

        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in [".py"]:
                    lang_counts["Python"] += 1
                elif ext in [".js", ".jsx"]:
                    lang_counts["JavaScript"] += 1
                elif ext in [".ts", ".tsx"]:
                    lang_counts["TypeScript"] += 1
                elif ext in [".rs"]:
                    lang_counts["Rust"] += 1
                elif ext in [".go"]:
                    lang_counts["Go"] += 1
                elif ext in [".java"]:
                    lang_counts["Java"] += 1
                elif ext in [".cpp", ".cc", ".cxx"]:
                    lang_counts["C++"] += 1
                elif ext in [".c"]:
                    lang_counts["C"] += 1

        if lang_counts:
            metadata.primary_language = max(lang_counts.items(), key=lambda x: x[1])[0]
            metadata.language = metadata.primary_language

    def _detect_technologies(self, repo_path: Path, metadata: RepoMetadata):
        """Detect technologies and frameworks."""
        # Check for framework indicators
        for framework, indicators in self.FRAMEWORKS.items():
            for indicator in indicators:
                if (repo_path / indicator).exists() or any(
                    indicator in str(f) for f in repo_path.rglob("*")
                ):
                    metadata.frameworks.add(framework)
                    break

        # Check for test frameworks
        test_patterns = {
            "pytest": ["pytest", "test_", "_test.py"],
            "jest": ["jest", ".test.js", ".spec.js"],
            "mocha": ["mocha", ".test.js"],
            "unittest": ["unittest", "test_"],
            "junit": ["junit", "Test.java"],
        }

        for test_framework, patterns in test_patterns.items():
            for pattern in patterns:
                if any(pattern in str(f) for f in repo_path.rglob("*")):
                    metadata.has_tests = True
                    metadata.test_framework = test_framework
                    break

    def _detect_dependencies(self, repo_path: Path, metadata: RepoMetadata):
        """Detect dependencies from package files."""
        # Python
        if (repo_path / "requirements.txt").exists():
            try:
                with open(repo_path / "requirements.txt", "r") as f:
                    for line in f:
                        dep = line.strip().split("==")[0].split(">=")[0].split("<=")[0]
                        if dep and not dep.startswith("#"):
                            metadata.dependencies.add(dep.lower())
            except Exception:
                pass

        # Node.js
        if (repo_path / "package.json").exists():
            try:
                with open(repo_path / "package.json", "r") as f:
                    pkg_data = json.load(f)
                    deps = pkg_data.get("dependencies", {})
                    dev_deps = pkg_data.get("devDependencies", {})
                    for dep in list(deps.keys()) + list(dev_deps.keys()):
                        metadata.dependencies.add(dep.lower())
            except Exception:
                pass

    def _analyze_git(self, repo_path: Path, metadata: RepoMetadata):
        """Analyze git repository information."""
        try:
            # Last commit
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%ai", "--no-color"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split("|")
                if len(parts) == 2:
                    metadata.last_commit = parts[1]

            # Commit count
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                try:
                    metadata.commit_count = int(result.stdout.strip())
                except ValueError:
                    pass

            # Branch count
            result = subprocess.run(
                ["git", "branch", "-r"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                metadata.branch_count = len([b for b in result.stdout.split("\n") if b.strip()])

            # Tag count
            result = subprocess.run(
                ["git", "tag"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                metadata.tag_count = len([t for t in result.stdout.split("\n") if t.strip()])

        except Exception:
            pass

        # Repository size
        try:
            total_size = sum(f.stat().st_size for f in repo_path.rglob("*") if f.is_file())
            metadata.size_mb = total_size / (1024 * 1024)
        except Exception:
            pass

        # Check if empty
        metadata.is_empty = metadata.commit_count == 0

    def _detect_project_type(self, repo_path: Path, metadata: RepoMetadata):
        """Detect project type/category."""
        name_lower = metadata.name.lower()
        path_str = str(repo_path).lower()

        if "tool" in name_lower or "util" in name_lower:
            metadata.project_type = "tool"
        elif "api" in name_lower or "server" in name_lower:
            metadata.project_type = "api"
        elif "web" in name_lower or "frontend" in name_lower:
            metadata.project_type = "web"
        elif "bot" in name_lower:
            metadata.project_type = "bot"
        elif "lib" in name_lower or "library" in name_lower:
            metadata.project_type = "library"
        elif "agent" in name_lower or "swarm" in name_lower:
            metadata.project_type = "agent"
        elif metadata.has_package_json and "react" in metadata.frameworks:
            metadata.project_type = "web"
        elif metadata.has_requirements and "django" in metadata.frameworks:
            metadata.project_type = "web"
        elif metadata.has_requirements and "flask" in metadata.frameworks:
            metadata.project_type = "api"
        else:
            metadata.project_type = "application"

    def _calculate_similarity_hash(self, repo_path: Path, metadata: RepoMetadata) -> str:
        """Calculate a hash for similarity detection."""
        # Create hash based on key characteristics
        hash_input = f"{metadata.primary_language}|{metadata.project_type}|{len(metadata.dependencies)}"
        
        # Add top dependencies
        top_deps = sorted(list(metadata.dependencies))[:10]
        hash_input += "|" + "|".join(top_deps)
        
        # Add framework
        if metadata.frameworks:
            hash_input += "|" + "|".join(sorted(metadata.frameworks))
        
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]

    def _assess_status(self, repo_path: Path, metadata: RepoMetadata):
        """Assess repository status."""
        if metadata.is_empty:
            metadata.status = "empty"
        elif metadata.commit_count < 5:
            metadata.status = "new"
        elif not metadata.has_readme:
            metadata.status = "incomplete"
        elif metadata.last_commit:
            # Check if last commit is old (more than 1 year)
            try:
                from datetime import datetime, timezone
                last_date = datetime.fromisoformat(metadata.last_commit.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - last_date).days
                if age_days > 365:
                    metadata.status = "archived"
                else:
                    metadata.status = "active"
            except Exception:
                metadata.status = "active"
        else:
            metadata.status = "unknown"

    def analyze_all(self) -> Dict[str, RepoMetadata]:
        """Analyze all repositories."""
        if not self.repos_dir.exists():
            print(f"❌ Directory not found: {self.repos_dir}")
            return {}

        repos = [d for d in self.repos_dir.iterdir() if d.is_dir() and (d / ".git").exists()]

        print(f"📊 Analyzing {len(repos)} repositories...\n")

        for repo_path in repos:
            metadata = self.analyze_repo(repo_path)
            self.repos[metadata.name] = metadata
            print(f"  ✅ {metadata.name} analyzed")

        return self.repos

    def find_similar_repos(self) -> Dict[str, List[str]]:
        """Find similar/duplicate repositories."""
        similarity_groups = defaultdict(list)

        for name, metadata in self.repos.items():
            # Group by similarity hash
            similarity_groups[metadata.similarity_hash].append(name)

            # Also check name similarity
            for other_name, other_metadata in self.repos.items():
                if name == other_name:
                    continue

                # Check if names are similar
                name_words = set(name.lower().replace("-", " ").replace("_", " ").split())
                other_words = set(other_name.lower().replace("-", " ").replace("_", " ").split())

                if name_words & other_words:  # Has common words
                    if metadata.similarity_hash == other_metadata.similarity_hash:
                        # Same project characteristics
                        similarity_groups[f"similar_{name}"].append(other_name)

        # Filter to only groups with multiple repos
        return {k: v for k, v in similarity_groups.items() if len(v) > 1}

    def generate_report(self, output_file: str = "repo_analysis_report.json") -> Dict:
        """Generate comprehensive analysis report."""
        similar = self.find_similar_repos()

        report = {
            "analysis_date": datetime.now().isoformat(),
            "total_repos": len(self.repos),
            "repositories": {name: meta.to_dict() for name, meta in self.repos.items()},
            "similarity_groups": similar,
            "summary": {
                "by_language": defaultdict(int),
                "by_type": defaultdict(int),
                "by_status": defaultdict(int),
                "with_readme": 0,
                "with_license": 0,
                "with_tests": 0,
                "total_lines": 0,
                "total_size_mb": 0.0,
            },
        }

        # Calculate summary statistics
        for metadata in self.repos.values():
            report["summary"]["by_language"][metadata.primary_language] += 1
            report["summary"]["by_type"][metadata.project_type] += 1
            report["summary"]["by_status"][metadata.status] += 1
            if metadata.has_readme:
                report["summary"]["with_readme"] += 1
            if metadata.has_license:
                report["summary"]["with_license"] += 1
            if metadata.has_tests:
                report["summary"]["with_tests"] += 1
            report["summary"]["total_lines"] += metadata.total_lines
            report["summary"]["total_size_mb"] += metadata.size_mb

        # Convert defaultdicts to dicts
        report["summary"]["by_language"] = dict(report["summary"]["by_language"])
        report["summary"]["by_type"] = dict(report["summary"]["by_type"])
        report["summary"]["by_status"] = dict(report["summary"]["by_status"])

        # Save report
        output_path = Path(output_file)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def print_summary(self, report: Dict):
        """Print human-readable summary."""
        print("\n" + "=" * 80)
        print("📊 REPOSITORY ANALYSIS SUMMARY")
        print("=" * 80)

        summary = report["summary"]
        print(f"\n📦 Total Repositories: {report['total_repos']}")

        print(f"\n📝 Documentation:")
        print(f"   README: {summary['with_readme']}/{report['total_repos']}")
        print(f"   License: {summary['with_license']}/{report['total_repos']}")
        print(f"   Tests: {summary['with_tests']}/{report['total_repos']}")

        print(f"\n💻 Languages:")
        for lang, count in sorted(summary["by_language"].items(), key=lambda x: -x[1]):
            print(f"   {lang}: {count}")

        print(f"\n📂 Project Types:")
        for ptype, count in sorted(summary["by_type"].items(), key=lambda x: -x[1]):
            print(f"   {ptype}: {count}")

        print(f"\n📊 Status:")
        for status, count in sorted(summary["by_status"].items(), key=lambda x: -x[1]):
            print(f"   {status}: {count}")

        print(f"\n📏 Code Metrics:")
        print(f"   Total Lines: {summary['total_lines']:,}")
        print(f"   Total Size: {summary['total_size_mb']:.2f} MB")

        # Similarity groups
        similar = report.get("similarity_groups", {})
        if similar:
            print(f"\n🔍 Similar/Duplicate Projects Found: {len(similar)} groups")
            for group_id, repos in list(similar.items())[:10]:  # Show first 10
                if len(repos) > 1:
                    print(f"   • {', '.join(repos)}")
            if len(similar) > 10:
                print(f"   ... and {len(similar) - 10} more groups")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Professional repository analyzer")
    parser.add_argument(
        "repos_dir",
        nargs="?",
        default="/home/dream/Development/projects/repositories/old-account",
        help="Directory containing repositories",
    )
    parser.add_argument(
        "--output",
        default="repo_analysis_report.json",
        help="Output report file",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print summary, don't save full report",
    )

    args = parser.parse_args()

    analyzer = RepoAnalyzer(args.repos_dir)
    repos = analyzer.analyze_all()

    if not repos:
        print("❌ No repositories found or analyzed")
        return 1

    report = analyzer.generate_report(args.output)

    analyzer.print_summary(report)

    if not args.summary_only:
        print(f"\n✅ Full report saved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


