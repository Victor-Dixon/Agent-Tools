#!/usr/bin/env python3
"""
Populate Tasks from Toolbelt Health Check
=========================================

Reads toolbelt health check results and generates task entries
for broken tools to add to MASTER_TASK_LOG.md.

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
    """Check if a tool can be imported."""
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
    """Check if a tool has the required main function."""
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


def categorize_issue(import_error: str, main_error: str) -> tuple[str, str]:
    """
    Categorize the issue and determine priority.

    Returns:
        (priority: str, category: str)
    """
    if "ImportError" in import_error or "No module named" in import_error:
        # Missing module - could be deprecated or moved
        if "deprecated" in import_error.lower() or "moved" in import_error.lower():
            return "MEDIUM", "Registry cleanup (deprecated/moved tool)"
        else:
            return "HIGH", "Missing module (tool may be broken or moved)"

    if "unexpected indent" in import_error.lower() or "SyntaxError" in import_error:
        return "HIGH", "Syntax error (fixable)"

    if "is not defined" in import_error or "name" in import_error.lower():
        return "HIGH", "Import error within module (fixable)"

    if "No main() function found" in main_error:
        return "MEDIUM", "Missing main() function (add entry point)"

    return "MEDIUM", "Unknown issue (needs investigation)"


def generate_task_entry(result: dict[str, Any]) -> str:
    """Generate a task entry for MASTER_TASK_LOG.md."""
    priority, category = categorize_issue(
        result["import_error"], result["main_error"]
    )

    issue_desc = result["import_error"] if not result["import_ok"] else result["main_error"]

    task_entry = f"- [ ] **{priority}**: Fix toolbelt tool '{result['name']}' ({result['id']}) - {category}\n"
    task_entry += f"  - Module: `{result['module']}`\n"
    task_entry += f"  - Issue: {issue_desc}\n"

    return task_entry


def main():
    """Main execution."""
    print("🔍 Generating tasks from toolbelt health check...\n")

    if not TOOLS_REGISTRY:
        print("❌ No tools found in registry")
        return 1

    broken_tools = []

    for tool_id, tool_config in TOOLS_REGISTRY.items():
        # Check import
        import_ok, import_error = check_tool_import(tool_id, tool_config)

        # Check main function
        main_ok, main_error = (False, "Skipped")
        if import_ok:
            main_ok, main_error = check_main_function(tool_id, tool_config)

        if not (import_ok and main_ok):
            broken_tools.append({
                "id": tool_id,
                "name": tool_config.get("name", tool_id),
                "module": tool_config.get("module", ""),
                "import_ok": import_ok,
                "import_error": import_error,
                "main_ok": main_ok,
                "main_error": main_error
            })

    if not broken_tools:
        print("✅ All tools are healthy! No tasks to generate.")
        return 0

    print(f"Found {len(broken_tools)} broken tools\n")
    print("=" * 60)
    print("GENERATED TASK ENTRIES FOR MASTER_TASK_LOG.md")
    print("=" * 60)
    print()

    # Group by priority
    high_priority = []
    medium_priority = []

    for tool in broken_tools:
        priority, _ = categorize_issue(
            tool["import_error"], tool["main_error"])
        task_entry = generate_task_entry(tool)

        if priority == "HIGH":
            high_priority.append(task_entry)
        else:
            medium_priority.append(task_entry)

    # Print HIGH priority tasks
    if high_priority:
        print("## HIGH PRIORITY TASKS (Toolbelt Health Check)")
        print()
        for entry in high_priority:
            print(entry)
        print()

    # Print MEDIUM priority tasks
    if medium_priority:
        print("## MEDIUM PRIORITY TASKS (Toolbelt Health Check)")
        print()
        for entry in medium_priority:
            print(entry)
        print()

    print("=" * 60)
    print(
        f"📊 Summary: {len(high_priority)} HIGH priority, {len(medium_priority)} MEDIUM priority")
    print()
    print("💡 Copy these entries to MASTER_TASK_LOG.md in the appropriate sections")

    return 0


if __name__ == "__main__":
    sys.exit(main())



