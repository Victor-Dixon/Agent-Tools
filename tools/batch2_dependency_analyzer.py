#!/usr/bin/env python3
"""
Batch 2 Integration Testing - Dependency Analysis Tool
=====================================================

Component 4: Dependency Management Verification
- Dependency isolation verification
- Configuration management validation
- Dependency direction analysis (circular dependency detection)

SSOT Domain: infrastructure
"""

import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque


class DependencyAnalyzer:
    """Analyze dependencies for Batch 2 merged repositories."""

    def __init__(self, repos_path: Path = Path("temp_repos")):
        self.repos_path = repos_path
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.repo_boundaries: Dict[str, Set[str]] = {}
        self.circular_dependencies: List[Tuple[str, str]] = []
        self.config_files: Dict[str, List[str]] = defaultdict(list)

    def analyze_repo(self, repo_name: str) -> Dict:
        """Analyze dependencies for a single repository."""
        repo_path = self.repos_path / repo_name
        if not repo_path.exists():
            return {"error": f"Repository {repo_name} not found"}

        # Build dependency graph
        self._build_dependency_graph(repo_path, repo_name)

        # Identify repo boundaries
        self._identify_repo_boundaries(repo_path, repo_name)

        # Find circular dependencies
        self._find_circular_dependencies()

        # Analyze configuration management
        self._analyze_configuration_management(repo_path, repo_name)

        return {
            "repo": repo_name,
            "dependencies": list(self.dependency_graph.keys()),
            "circular_dependencies": self.circular_dependencies,
            "config_files": self.config_files[repo_name],
            "boundaries": list(self.repo_boundaries.get(repo_name, set()))
        }

    def _build_dependency_graph(self, repo_path: Path, repo_name: str):
        """Build dependency graph by analyzing imports."""
        for py_file in repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                module_name = self._get_module_name(py_file, repo_path)
                with open(py_file, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=str(py_file))
                        imports = self._extract_imports(tree)
                        for imp in imports:
                            self.dependency_graph[module_name].add(imp)
                    except SyntaxError:
                        continue
            except Exception as e:
                print(
                    f"Warning: Could not analyze {py_file}: {e}", file=sys.stderr)

    def _get_module_name(self, file_path: Path, repo_path: Path) -> str:
        """Get module name from file path."""
        relative = file_path.relative_to(repo_path)
        parts = relative.parts[:-1] + (relative.stem,)
        return ".".join(parts)

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])
        return imports

    def _identify_repo_boundaries(self, repo_path: Path, repo_name: str):
        """Identify repository boundaries (what modules belong to this repo)."""
        boundaries = set()
        for py_file in repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            module_name = self._get_module_name(py_file, repo_path)
            boundaries.add(module_name)
        self.repo_boundaries[repo_name] = boundaries

    def _find_circular_dependencies(self):
        """Find circular dependencies using DFS."""
        visited = set()
        rec_stack = set()

        def has_cycle(node: str, path: List[str]) -> Optional[List[str]]:
            """Check for cycles starting from node."""
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                self.circular_dependencies.append(tuple(cycle))
                return cycle

            if node in visited:
                return None

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependency_graph.get(node, set()):
                cycle = has_cycle(neighbor, path)
                if cycle:
                    return cycle

            rec_stack.remove(node)
            path.pop()
            return None

        for node in self.dependency_graph:
            if node not in visited:
                has_cycle(node, [])

    def _analyze_configuration_management(self, repo_path: Path, repo_name: str):
        """Analyze configuration management (env files, config files, etc.)."""
        config_patterns = [
            "*.env",
            "*.config",
            "config*.py",
            "settings*.py",
            "*.yaml",
            "*.yml",
            "*.json"
        ]

        for pattern in config_patterns:
            for config_file in repo_path.rglob(pattern):
                if "__pycache__" not in str(config_file):
                    self.config_files[repo_name].append(
                        str(config_file.relative_to(repo_path)))

    def verify_dependency_isolation(self, repo_name: str) -> Dict:
        """Verify that dependencies are properly isolated."""
        repo_deps = self.dependency_graph
        repo_boundary = self.repo_boundaries.get(repo_name, set())

        violations = []
        for module, deps in repo_deps.items():
            if module in repo_boundary:
                # Check if this module depends on other repos
                for dep in deps:
                    # Check if dependency is outside this repo
                    is_external = True
                    for other_repo, other_boundary in self.repo_boundaries.items():
                        if other_repo != repo_name and dep in other_boundary:
                            violations.append({
                                "module": module,
                                "external_dependency": dep,
                                "external_repo": other_repo
                            })
                            is_external = False
                            break

                    # If external and not through adapter, it's a violation
                    if is_external and not any("adapter" in dep.lower() for dep in deps):
                        # Check if it's a shared dependency (acceptable)
                        if not dep.startswith("src.") and not dep.startswith("temp_repos."):
                            # This might be a shared dependency (like standard library)
                            continue

        return {
            "repo": repo_name,
            "isolated": len(violations) == 0,
            "violations": violations
        }

    def verify_dependency_direction(self) -> Dict:
        """Verify dependency direction (no cycles)."""
        return {
            "has_circular_dependencies": len(self.circular_dependencies) > 0,
            "circular_dependencies": [
                " → ".join(cycle) for cycle in self.circular_dependencies
            ]
        }

    def verify_configuration_management(self, repo_name: str) -> Dict:
        """Verify configuration management is properly abstracted."""
        config_files = self.config_files.get(repo_name, [])

        # Check for hardcoded paths, secrets, etc.
        issues = []
        repo_path = self.repos_path / repo_name

        for config_file in config_files:
            full_path = repo_path / config_file
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8")
                    # Check for hardcoded paths
                    if "/home/" in content or "C:\\" in content:
                        issues.append({
                            "file": config_file,
                            "issue": "hardcoded_path"
                        })
                    # Check for potential secrets (basic check)
                    if "password" in content.lower() and "=" in content:
                        if not any(keyword in content.lower() for keyword in ["env", "getenv", "os.environ"]):
                            issues.append({
                                "file": config_file,
                                "issue": "potential_secret"
                            })
                except Exception:
                    pass

        return {
            "repo": repo_name,
            "config_files": config_files,
            "issues": issues,
            "valid": len(issues) == 0
        }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch 2 Integration Testing - Dependency Analysis"
    )
    parser.add_argument(
        "--repos",
        type=str,
        nargs="+",
        default=["agentproject", "Auto_Blogger",
                 "crosbyultimateevents.com", "contract-leads", "Thea"],
        help="Repositories to analyze"
    )
    parser.add_argument(
        "--repos-path",
        type=str,
        default="temp_repos",
        help="Path to repositories directory"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file path"
    )
    parser.add_argument(
        "--check-isolation",
        action="store_true",
        help="Check dependency isolation"
    )
    parser.add_argument(
        "--check-direction",
        action="store_true",
        help="Check dependency direction (circular dependencies)"
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check configuration management"
    )

    args = parser.parse_args()

    repos_path = Path(args.repos_path)
    analyzer = DependencyAnalyzer(repos_path)

    results = {
        "repositories": [],
        "dependency_isolation": [],
        "dependency_direction": {},
        "configuration_management": []
    }

    # Analyze each repository
    for repo in args.repos:
        print(f"Analyzing {repo}...")
        repo_result = analyzer.analyze_repo(repo)
        results["repositories"].append(repo_result)

        # Check isolation if requested
        if args.check_isolation:
            isolation_result = analyzer.verify_dependency_isolation(repo)
            results["dependency_isolation"].append(isolation_result)

        # Check configuration if requested
        if args.check_config:
            config_result = analyzer.verify_configuration_management(repo)
            results["configuration_management"].append(config_result)

    # Check dependency direction if requested
    if args.check_direction:
        direction_result = analyzer.verify_dependency_direction()
        results["dependency_direction"] = direction_result

    # Output results
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(results, indent=2))

    # Print summary
    print("\n" + "="*60)
    print("DEPENDENCY ANALYSIS SUMMARY")
    print("="*60)

    if args.check_isolation:
        isolated_count = sum(
            1 for r in results["dependency_isolation"] if r["isolated"])
        print(
            f"Dependency Isolation: {isolated_count}/{len(results['dependency_isolation'])} repos isolated")

    if args.check_direction:
        has_cycles = results["dependency_direction"].get(
            "has_circular_dependencies", False)
        print(
            f"Dependency Direction: {'❌ Has circular dependencies' if has_cycles else '✅ No circular dependencies'}")
        if has_cycles:
            for cycle in results["dependency_direction"].get("circular_dependencies", [])[:5]:
                print(f"  - {cycle}")

    if args.check_config:
        valid_count = sum(
            1 for r in results["configuration_management"] if r["valid"])
        print(
            f"Configuration Management: {valid_count}/{len(results['configuration_management'])} repos valid")

    return 0 if (not args.check_direction or not results["dependency_direction"].get("has_circular_dependencies", False)) else 1


if __name__ == "__main__":
    sys.exit(main())
