#!/usr/bin/env python3
"""
Verify Toolbelt After Archive - Pre-Deletion Check
===================================================

Verifies toolbelt functionality after archiving deprecated tools.
Run before deleting tools/deprecated/ directory.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_toolbelt_imports():
    """Test that toolbelt modules import successfully."""
    print("🔍 Testing toolbelt imports...")
    
    try:
        # Import toolbelt.py (the main module, not the package)
        import tools.toolbelt as toolbelt_module
        print("  ✅ tools.toolbelt module imports successfully")
    except Exception as e:
        print(f"  ❌ tools.toolbelt module import failed: {e}")
        return False
    
    try:
        from tools.toolbelt_registry import ToolRegistry
        print("  ✅ toolbelt_registry.py imports successfully")
    except Exception as e:
        print(f"  ❌ toolbelt_registry.py import failed: {e}")
        return False
    
    try:
        from tools.toolbelt_help import HelpGenerator
        print("  ✅ toolbelt_help.py imports successfully")
    except Exception as e:
        print(f"  ❌ toolbelt_help.py import failed: {e}")
        return False
    
    try:
        from tools.toolbelt_runner import ToolRunner
        print("  ✅ toolbelt_runner.py imports successfully")
    except Exception as e:
        print(f"  ❌ toolbelt_runner.py import failed: {e}")
        return False
    
    return True


def test_toolbelt_registry():
    """Test that toolbelt registry works."""
    print("\n🔍 Testing toolbelt registry...")
    
    try:
        from tools.toolbelt_registry import ToolRegistry
        registry = ToolRegistry()
        tools = registry.list_tools()
        print(f"  ✅ Registry loaded {len(tools)} tools")
        
        # Check for any deprecated references
        for tool in tools:
            module = tool.get('module', '')
            if 'deprecated' in module.lower():
                print(f"  ⚠️  Warning: Tool '{tool['name']}' references deprecated module: {module}")
                return False
        
        print("  ✅ No deprecated references found in registry")
        return True
    except Exception as e:
        print(f"  ❌ Registry test failed: {e}")
        return False


def test_toolbelt_help():
    """Test that toolbelt help system works."""
    print("\n🔍 Testing toolbelt help system...")
    
    try:
        from tools.toolbelt_help import HelpGenerator
        from tools.toolbelt_registry import ToolRegistry
        
        registry = ToolRegistry()
        help_gen = HelpGenerator(registry)
        help_text = help_gen.generate_help()
        
        if len(help_text) > 0:
            print(f"  ✅ Help system generates {len(help_text)} characters of help text")
            return True
        else:
            print("  ❌ Help system generated empty text")
            return False
    except Exception as e:
        print(f"  ❌ Help system test failed: {e}")
        return False


def main():
    """Run all toolbelt verification tests."""
    print("🛠️  Toolbelt Verification - Pre-Deletion Check")
    print("=" * 60)
    print()
    
    results = []
    
    # Test imports
    results.append(("Imports", test_toolbelt_imports()))
    
    # Test registry
    results.append(("Registry", test_toolbelt_registry()))
    
    # Test help
    results.append(("Help System", test_toolbelt_help()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print()
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ All tests passed! Toolbelt is safe to use after archive.")
        print("💡 Safe to delete tools/deprecated/ directory")
        return 0
    else:
        print("❌ Some tests failed! Do not delete tools/deprecated/ yet.")
        print("💡 Investigate failures before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())

