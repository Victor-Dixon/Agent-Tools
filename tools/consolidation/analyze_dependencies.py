#!/usr/bin/env python3
"""
Dependency Analysis Script for Tools Consolidation.

Analyzes dependencies in tools/ and tools_v2/ directories and generates
a comprehensive dependency map.

Usage:
    python tools/consolidation/analyze_dependencies.py [--output dependencies.json]
"""

import argparse
import sys
from pathlib import Path

from dependency_mapper import DependencyMapper


def main():
    """Main entry point for dependency analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze dependencies in tools/ and tools_v2/ directories"
    )
    parser.add_argument(
        "--output",
        default="dependencies.json",
        help="Output JSON file path (default: dependencies.json)",
    )
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Base directory for the project (default: current directory)",
    )

    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    tools_dir = base_dir / "tools"
    tools_v2_dir = base_dir / "tools_v2"

    if not tools_dir.exists():
        print(f"Error: {tools_dir} does not exist", file=sys.stderr)
        return 1

    print("🔍 Analyzing dependencies...")
    print(f"   Base directory: {base_dir}")
    print(f"   Tools directory: {tools_dir}")
    print(f"   Tools V2 directory: {tools_v2_dir}")

    mapper = DependencyMapper(base_dir=str(base_dir))

    # Scan directories
    print("\n📂 Scanning tools/ directory...")
    mapper.scan_directory(tools_dir)
    print(f"   Found {len(mapper.nodes)} tools in tools/")

    if tools_v2_dir.exists():
        print("\n📂 Scanning tools_v2/ directory...")
        initial_count = len(mapper.nodes)
        mapper.scan_directory(tools_v2_dir)
        print(f"   Found {len(mapper.nodes) - initial_count} additional tools in tools_v2/")

    # Build dependency graph
    print("\n🔗 Building dependency graph...")
    mapper.build_dependency_graph()
    print(f"   Graph contains {len(mapper.graph)} nodes")

    # Analyze results
    external_deps = mapper.get_external_dependencies()
    internal_deps = mapper.get_internal_dependencies()
    circular_deps = mapper.get_circular_dependencies()

    print(f"\n📊 Analysis Results:")
    print(f"   Total tools analyzed: {len(mapper.nodes)}")
    print(f"   External dependencies: {len(external_deps)}")
    print(f"   Internal dependencies: {len(internal_deps)}")
    print(f"   Circular dependencies: {len(circular_deps)}")

    if circular_deps:
        print(f"\n⚠️  Circular Dependencies Found:")
        for i, cycle in enumerate(circular_deps, 1):
            print(f"   {i}. {' -> '.join(cycle)}")

    # Export to JSON
    output_path = base_dir / args.output
    print(f"\n💾 Exporting to {output_path}...")
    mapper.export_to_json(str(output_path))
    print(f"   ✅ Dependency map exported successfully")

    return 0


if __name__ == "__main__":
    sys.exit(main())


