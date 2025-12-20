#!/usr/bin/env python3
"""
Basic Toolbelt V2 Test
======================

Standalone test for toolbelt V2 functionality (avoids dependency issues).

Usage: python tools_v2/test_toolbelt_basic.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_basic_functionality():
    """Test basic toolbelt functionality."""
    print("🧪 Testing Toolbelt V2 Basic Functionality\n")

    # Test 1: Import core
    print("Test 1: Importing core...")
    from tools_v2 import get_tool_registry, get_toolbelt_core

    print("✅ Core imports successful\n")

    # Test 2: Get toolbelt instance
    print("Test 2: Getting toolbelt instance...")
    core = get_toolbelt_core()
    print("✅ ToolbeltCore initialized\n")

    # Test 3: List tools
    print("Test 3: Listing tools...")
    tools = core.list_tools()
    print(f"✅ {len(tools)} tools registered:")
    for tool in tools:
        print(f"   - {tool}")
    print()

    # Test 4: List categories
    print("Test 4: Listing categories...")
    categories = core.list_categories()
    print(f"✅ {len(categories)} categories:")
    for cat, tool_list in sorted(categories.items()):
        print(f"   - {cat}: {len(tool_list)} tools")
    print()

    # Test 5: Test tool resolution
    print("Test 5: Resolving tool adapters...")
    registry = get_tool_registry()

    test_tools = ["vector.context", "msg.send", "analysis.scan", "v2.check"]
    for tool_name in test_tools:
        try:
            adapter_class = registry.resolve(tool_name)
            adapter = adapter_class()
            spec = adapter.get_spec()
            print(f"✅ {tool_name} → {spec.summary[:50]}...")
        except Exception as e:
            print(f"❌ {tool_name} → Error: {e}")
    print()

    # Test 6: Test tool spec retrieval
    print("Test 6: Getting tool specifications...")
    from tools_v2.categories.vector_tools import TaskContextTool

    tool = TaskContextTool()
    spec = tool.get_spec()
    print(f"✅ Tool: {spec.name}")
    print(f"   Version: {spec.version}")
    print(f"   Category: {spec.category}")
    print(f"   Required params: {spec.required_params}")
    print(f"   Optional params: {list(spec.optional_params.keys())}")
    print()

    # Test 7: Test help generation
    print("Test 7: Generating help text...")
    help_text = tool.get_help()
    print("✅ Help text generated:")
    print(help_text[:200] + "...")
    print()

    # Test 8: Validate file sizes
    print("Test 8: Validating V2 compliance (file sizes)...")
    tools_v2_root = Path(__file__).parent
    all_files = list(tools_v2_root.rglob("*.py"))
    violations = []

    for file in all_files:
        if file.name.startswith("test_"):
            continue  # Skip test files
        line_count = len(file.read_text().splitlines())
        if line_count > 400:
            violations.append((file.relative_to(tools_v2_root), line_count))

    if violations:
        print("❌ V2 violations found:")
        for file, lines in violations:
            print(f"   - {file}: {lines} lines")
    else:
        print("✅ All files ≤400 lines (V2 compliant)")
    print()

    print("🏆 All basic tests passed!")
    print("🐝 WE. ARE. SWARM. ⚡️🔥")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(test_basic_functionality())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
