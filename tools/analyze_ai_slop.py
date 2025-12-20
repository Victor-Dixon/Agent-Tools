#!/usr/bin/env python3
"""
AI Slop Analyzer - Systematic Dead Code Detection
==================================================

Identifies unreferenced, deprecated, oversized, and potentially AI-generated
low-value code that can be safely deleted or quarantined.

Author: Agent-3 (Infrastructure & DevOps Specialist)
Purpose: Quantify and rank deletion candidates for repository cleanup
"""

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class AISlopAnalyzer:
    """Analyzer for identifying dead code and AI slop."""

    # Patterns that indicate deprecated/archived/experimental code
    DEPRECATED_PATTERNS = [
        r'deprecated',
        r'archive',
        r'_old\.py$',
        r'_backup\.py$',
        r'\.bak\.py$',
        r'tmp',
        r'temp',
        r'experimental',
        r'test_',
        r'example',
        r'_test\.py$',
        r'demo',
    ]

    # Directories to skip
    SKIP_DIRS = {
        '__pycache__', '.git', 'node_modules', '.venv', 'venv',
        '.pytest_cache', '.mypy_cache', 'build', 'dist',
    }

    # Entry point patterns (files that might be called directly)
    ENTRY_POINT_PATTERNS = [
        r'if __name__ == ["\']__main__["\']',
        r'python -m',
        r'#!/usr/bin/env python',
    ]

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.all_py_files: Dict[str, Path] = {}
        self.imports_map: Dict[str, Set[str]] = defaultdict(
            set)  # file -> imports from it
        self.file_sizes: Dict[str, int] = {}
        self.candidates: List[Dict] = []

    def find_all_python_files(self) -> None:
        """Find all Python files in the project."""
        print("🔍 Scanning for Python files...")

        for py_file in self.project_root.rglob('*.py'):
            # Skip excluded directories
            if any(skip in py_file.parts for skip in self.SKIP_DIRS):
                continue

            rel_path = str(py_file.relative_to(self.project_root))
            self.all_py_files[rel_path] = py_file

            # Count lines
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    self.file_sizes[rel_path] = sum(1 for _ in f)
            except Exception:
                self.file_sizes[rel_path] = 0

        print(f"   Found {len(self.all_py_files)} Python files")

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract all import statements from a Python file."""
        imports = set()

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

        except Exception:
            pass  # Skip files that can't be parsed

        return imports

    def build_import_graph(self) -> None:
        """Build a graph of which files import which modules."""
        print("🔗 Building import graph...")

        module_to_files = {}

        # Map module names to file paths
        for rel_path, file_path in self.all_py_files.items():
            module_name = self.path_to_module_name(rel_path)
            if module_name:
                module_to_files[module_name] = rel_path
                # Also add parent modules
                parts = module_name.split('.')
                for i in range(1, len(parts)):
                    parent = '.'.join(parts[:i])
                    if parent not in module_to_files:
                        module_to_files[parent] = None  # Partial match

        # Find imports for each file
        # Limit for performance
        for rel_path, file_path in list(self.all_py_files.items())[:1000]:
            imports = self.extract_imports(file_path)

            for imp in imports:
                # Try to find which file this import refers to
                if imp in module_to_files and module_to_files[imp]:
                    imported_file = module_to_files[imp]
                    self.imports_map[imported_file].add(rel_path)

    def path_to_module_name(self, rel_path: str) -> str:
        """Convert file path to module name."""
        # Remove .py extension
        module_path = rel_path.replace('.py', '').replace('\\', '/')

        # Remove __init__ suffix
        if module_path.endswith('/__init__'):
            module_path = module_path[:-9]
        elif module_path.endswith('__init__'):
            module_path = module_path[:-9]

        return module_path.replace('/', '.')

    def is_entry_point(self, file_path: Path) -> bool:
        """Check if file is likely an entry point (script)."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Check for shebang
            if content.startswith('#!/usr/bin/env python'):
                return True

            # Check for __main__ guard
            if re.search(r'if __name__\s*==\s*["\']__main__["\']', content):
                return True

        except Exception:
            pass

        return False

    def matches_deprecated_pattern(self, rel_path: str) -> bool:
        """Check if path matches deprecated/archive patterns."""
        lower_path = rel_path.lower()
        return any(re.search(pattern, lower_path) for pattern in self.DEPRECATED_PATTERNS)

    def analyze_candidates(self) -> None:
        """Analyze files and identify deletion candidates."""
        print("📊 Analyzing deletion candidates...")

        # Get entry points (files that are called directly)
        entry_points = set()
        for rel_path, file_path in self.all_py_files.items():
            if self.is_entry_point(file_path):
                entry_points.add(rel_path)

        print(f"   Found {len(entry_points)} entry points")

        # Categorize files
        for rel_path, file_path in self.all_py_files.items():
            size = self.file_sizes.get(rel_path, 0)
            is_imported = rel_path in self.imports_map and len(
                self.imports_map[rel_path]) > 0
            is_entry = rel_path in entry_points
            is_deprecated = self.matches_deprecated_pattern(rel_path)

            # Calculate deletion score (higher = more likely to be slop)
            score = 0
            reasons = []

            # Not imported by anything
            if not is_imported and not is_entry:
                score += 50
                reasons.append("Unreferenced (no imports, not entry point)")

            # Deprecated/archive pattern
            if is_deprecated:
                score += 40
                reasons.append("Deprecated/archive pattern in path")

            # Oversized and unreferenced
            if size > 800 and not is_imported and not is_entry:
                score += 30
                reasons.append(f"Oversized ({size} lines) and unreferenced")
            elif size > 1000:
                score += 20
                reasons.append(f"Very large file ({size} lines)")

            # In deprecated/archive directory
            if 'deprecated' in rel_path or 'archive' in rel_path:
                score += 35
                reasons.append("In deprecated/archive directory")

            # Test file without test runner reference
            if 'test_' in rel_path.lower() and not is_imported and not is_entry:
                score += 25
                reasons.append("Test file with no references")

            # Only add if score is significant
            if score > 30:
                candidate = {
                    'file': rel_path,
                    'score': score,
                    'size_lines': size,
                    'is_imported': is_imported,
                    'import_count': len(self.imports_map.get(rel_path, set())),
                    'is_entry_point': is_entry,
                    'is_deprecated_pattern': is_deprecated,
                    'reasons': reasons,
                    'category': self.categorize_file(rel_path, is_deprecated, size, is_imported, is_entry),
                }
                self.candidates.append(candidate)

    def categorize_file(self, rel_path: str, is_deprecated: bool, size: int,
                        is_imported: bool, is_entry: bool) -> str:
        """Categorize file for reporting."""
        if 'deprecated' in rel_path or 'archive' in rel_path:
            return 'DEPRECATED_DIRECTORY'
        elif is_deprecated:
            return 'DEPRECATED_PATTERN'
        elif size > 1000 and not is_imported and not is_entry:
            return 'OVERSIZED_UNREFERENCED'
        elif 'test_' in rel_path.lower() and not is_imported:
            return 'UNREFERENCED_TEST'
        elif not is_imported and not is_entry:
            return 'DEAD_CODE'
        else:
            return 'POTENTIAL_SLOP'

    def generate_report(self) -> Dict:
        """Generate analysis report."""
        # Sort by score (highest first)
        sorted_candidates = sorted(
            self.candidates, key=lambda x: x['score'], reverse=True)

        # Group by category
        by_category = defaultdict(list)
        for candidate in sorted_candidates:
            by_category[candidate['category']].append(candidate)

        # Calculate statistics
        total_files = len(self.all_py_files)
        candidate_count = len(self.candidates)
        total_slop_lines = sum(c['size_lines'] for c in self.candidates)

        # Estimate percentage
        total_lines = sum(self.file_sizes.values())
        slop_percentage = (total_slop_lines / total_lines *
                           100) if total_lines > 0 else 0
        file_percentage = (candidate_count / total_files *
                           100) if total_files > 0 else 0

        return {
            'summary': {
                'total_python_files': total_files,
                'deletion_candidates': candidate_count,
                'candidate_percentage': round(file_percentage, 2),
                'total_lines_all_files': total_lines,
                'total_lines_candidates': total_slop_lines,
                'lines_percentage': round(slop_percentage, 2),
            },
            'categories': {
                cat: {
                    'count': len(files),
                    'total_lines': sum(f['size_lines'] for f in files),
                    'files': files[:20]  # Top 20 per category
                }
                for cat, files in by_category.items()
            },
            'top_candidates': sorted_candidates[:50],  # Top 50 overall
        }


def main():
    """Main entry point."""
    analyzer = AISlopAnalyzer(PROJECT_ROOT)

    print("=" * 80)
    print("🤖 AI SLOP ANALYZER")
    print("=" * 80)
    print()

    # Phase 1: Find all Python files
    analyzer.find_all_python_files()

    # Phase 2: Build import graph (limited for performance)
    analyzer.build_import_graph()

    # Phase 3: Analyze candidates
    analyzer.analyze_candidates()

    # Phase 4: Generate report
    report = analyzer.generate_report()

    # Print summary
    print()
    print("=" * 80)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 80)
    print()
    summary = report['summary']
    print(f"Total Python Files:        {summary['total_python_files']:,}")
    print(
        f"Deletion Candidates:       {summary['deletion_candidates']:,} ({summary['candidate_percentage']:.1f}%)")
    print(f"Total Lines (All Files):   {summary['total_lines_all_files']:,}")
    print(
        f"Total Lines (Candidates):  {summary['total_lines_candidates']:,} ({summary['lines_percentage']:.1f}%)")
    print()

    # Print category breakdown
    print("=" * 80)
    print("📁 CATEGORY BREAKDOWN")
    print("=" * 80)
    print()
    for category, data in sorted(report['categories'].items(),
                                 key=lambda x: x[1]['count'], reverse=True):
        print(f"{category}:")
        print(f"  Files: {data['count']:,}")
        print(f"  Lines: {data['total_lines']:,}")
        print()

    # Print top candidates
    print("=" * 80)
    print("🏆 TOP 20 DELETION CANDIDATES (by score)")
    print("=" * 80)
    print()
    for i, candidate in enumerate(report['top_candidates'][:20], 1):
        print(f"{i:2d}. {candidate['file']}")
        print(
            f"     Score: {candidate['score']}, Size: {candidate['size_lines']} lines")
        print(f"     Category: {candidate['category']}")
        print(f"     Reasons: {', '.join(candidate['reasons'])}")
        print()

    # Save full report
    report_file = PROJECT_ROOT / 'tools' / 'ai_slop_analysis_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"✅ Full report saved to: {report_file}")
    print()
    print("=" * 80)
    print("🐝 WE. ARE. SWARM. ⚡🔥")
    print("=" * 80)


if __name__ == '__main__':
    main()
