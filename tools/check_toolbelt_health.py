#!/usr/bin/env python3
"""
Toolbelt Health Check - Verify All Tools Work
=============================================

Checks if each tool in the agent toolbelt registry can be imported
and has the required main function. Reports broken or missing tools.

Author: Agent-2
V2 Compliant: <300 lines
"""

import importlib
import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import toolbelt registry
try:
    from tools.toolbelt_registry import TOOLS_REGISTRY
except ImportError:
    print("❌ Failed to import toolbelt registry")
    sys.exit(1)


def check_tool_import(tool_id: str, tool_config: dict[str, Any]) -> tuple[bool, str]:
    """
    Check if a tool can be imported.

    Returns:
        (success: bool, error_message: str)
    """
    module_name = tool_config.get("module", "")
    if not module_name:
        return False, "No module specified"

    try:
        module = importlib.import_module(module_name)
        return True, "OK"
    except ImportError as e:
        return False, f"ImportError: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def check_main_function(tool_id: str, tool_config: dict[str, Any]) -> tuple[bool, str]:
    """
    Check if a tool has the required main function.

    Returns:
        (success: bool, error_message: str)
    """
    module_name = tool_config.get("module", "")
    main_function_name = tool_config.get("main_function", "main")

    try:
        module = importlib.import_module(module_name)
        if hasattr(module, main_function_name):
            main_func = getattr(module, main_function_name)
            if callable(main_func):
                return True, "OK"
            else:
                return False, f"{main_function_name} exists but is not callable"
        else:
            return False, f"No {main_function_name}() function found"
    except ImportError:
        return False, "Module import failed (check import first)"
    except Exception as e:
        return False, f"Error: {e}"


def check_tool(tool_id: str, tool_config: dict[str, Any]) -> dict[str, Any]:
    """
    Check a single tool's health.

    Returns:
        Dictionary with check results
    """
    name = tool_config.get("name", tool_id)
    module_name = tool_config.get("module", "")

    # Check import
    import_ok, import_error = check_tool_import(tool_id, tool_config)

    # Check main function (only if import succeeded)
    main_ok, main_error = (False, "Skipped - import failed")
    if import_ok:
        main_ok, main_error = check_main_function(tool_id, tool_config)

    # Overall status
    status = "✅ HEALTHY" if (import_ok and main_ok) else "❌ BROKEN"

    return {
        "id": tool_id,
        "name": name,
        "module": module_name,
        "status": status,
        "import_ok": import_ok,
        "import_error": import_error,
        "main_ok": main_ok,
        "main_error": main_error,
        "healthy": import_ok and main_ok
    }


def main():
    """Main execution."""
    print("🔍 TOOLBELT HEALTH CHECK")
    print("=" * 60)
    print()

    if not TOOLS_REGISTRY:
        print("❌ No tools found in registry")
        return 1

    print(f"Checking {len(TOOLS_REGISTRY)} tools...\n")

    results = []
    for tool_id, tool_config in TOOLS_REGISTRY.items():
        result = check_tool(tool_id, tool_config)
        results.append(result)

        # Print status
        status_icon = "✅" if result["healthy"] else "❌"
        print(f"{status_icon} {result['name']} ({tool_id})")
        if not result["healthy"]:
            if not result["import_ok"]:
                print(f"   Import: {result['import_error']}")
            if not result["main_ok"]:
                print(f"   Main function: {result['main_error']}")

    # Summary
    healthy_count = sum(1 for r in results if r["healthy"])
    broken_count = len(results) - healthy_count

    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"   Total tools: {len(results)}")
    print(f"   ✅ Healthy: {healthy_count}")
    print(f"   ❌ Broken: {broken_count}")

    if broken_count > 0:
        print()
        print("🔧 BROKEN TOOLS:")
        for result in results:
            if not result["healthy"]:
                print(f"   - {result['name']} ({result['id']})")
                print(f"     Module: {result['module']}")
                if not result["import_ok"]:
                    print(f"     Issue: {result['import_error']}")
                elif not result["main_ok"]:
                    print(f"     Issue: {result['main_error']}")

    print()
    return 0 if broken_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())



