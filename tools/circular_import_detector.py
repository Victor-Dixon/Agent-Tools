#!/usr/bin/env python3
"""
Circular Import Detector - Agent Toolbelt V2
============================================

Detects potential circular import issues in Python codebase.
Helps identify import cycles that could cause ImportError.

V2 Compliance: <400 lines, focused utility
Author: Agent-1 (Integration & Core Systems Specialist)
Created: 2025-01-27
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class CircularImportDetector:
    """Detects circular imports in Python codebase."""

    def __init__(self, root_dir: Path):
        """Initialize detector with root directory."""
        self.root_dir = Path(root_dir)
        self.import_graph: Dict[str, Set[str]] = {}
        self.cycles: List[List[str]] = []

    def detect(self) -> List[List[str]]:
        """
        Detect circular imports in codebase.

        Returns:
            List of cycles, each cycle is a list of module paths
        """
        logger.info(f"🔍 Scanning {self.root_dir} for circular imports...")

        # Build import graph
        self._build_import_graph()

        # Find cycles
        self._find_cycles()

        return self.cycles

    def _build_import_graph(self):
        """Build graph of imports between modules."""
        python_files = list(self.root_dir.rglob("*.py"))

        for file_path in python_files:
            # Skip __pycache__ and virtual environments
            if "__pycache__" in str(file_path) or "venv" in str(file_path):
                continue

            try:
                module_name = self._get_module_name(file_path)
                imports = self._extract_imports(file_path)

                if module_name not in self.import_graph:
                    self.import_graph[module_name] = set()

                for imp in imports:
                    self.import_graph[module_name].add(imp)

            except Exception as e:
                logger.warning(f"⚠️ Failed to parse {file_path}: {e}")

    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        # Get relative path from root
        rel_path = file_path.relative_to(self.root_dir)

        # Convert to module name (remove .py, convert / to .)
        module_name = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")

        return module_name

    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract import statements from Python file."""
        imports = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split(".")[0])

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split(".")[0])

        except Exception as e:
            logger.debug(f"Failed to parse {file_path}: {e}")

        return imports

    def _find_cycles(self):
        """Find cycles in import graph using DFS."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str):
            """Depth-first search to find cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, set()):
                # Check if neighbor is in current path (cycle detected)
                if neighbor in rec_stack:
                    # Find cycle start
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    self.cycles.append(cycle.copy())

                elif neighbor not in visited:
                    dfs(neighbor)

            rec_stack.remove(node)
            path.pop()

        # Start DFS from each unvisited node
        for node in self.import_graph:
            if node not in visited:
                dfs(node)

    def report(self) -> str:
        """Generate human-readable report."""
        if not self.cycles:
            return "✅ No circular imports detected!"

        report = ["🚨 CIRCULAR IMPORTS DETECTED\n"]

        for i, cycle in enumerate(self.cycles, 1):
            report.append(f"Cycle {i}:")
            report.append(" → ".join(cycle))
            report.append("")

        return "\n".join(report)


def main():
    """Main entry point."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Detect circular imports in Python codebase"
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Root directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    root_dir = Path(args.root).resolve()

    if not root_dir.exists():
        print(f"❌ Error: Directory not found: {root_dir}")
        sys.exit(1)

    detector = CircularImportDetector(root_dir)
    cycles = detector.detect()

    report = detector.report()
    print(report)

    if cycles:
        print(f"\n📊 Found {len(cycles)} circular import cycle(s)")
        sys.exit(1)
    else:
        print("\n✅ No circular imports detected!")
        sys.exit(0)


if __name__ == "__main__":
    main()

