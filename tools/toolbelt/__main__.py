"""
CLI Toolbelt Entry Point
========================

Main entry point for the unified CLI toolbelt.
Routes flags to specific tool modules based on the registry.

Usage:
    python -m tools.toolbelt [FLAG] [ARGS...]
"""

import sys
import importlib
import logging
from typing import NoReturn

# Import registry from parent package
try:
    from tools.toolbelt_registry import ToolRegistry
except ImportError:
    # Handle case where we might be running from inside tools/toolbelt
    sys.path.append("...")
    from tools.toolbelt_registry import ToolRegistry

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def main() -> NoReturn:
    """Main entry point."""
    registry = ToolRegistry()
    
    # 1. Parse arguments to find flag
    if len(sys.argv) < 2:
        print_help(registry)
        sys.exit(1)
        
    flag = sys.argv[1]
    
    # Handle help explicitly
    if flag in ["--help", "-h"]:
        print_help(registry)
        sys.exit(0)
        
    if flag == "--list":
        print_tools(registry)
        sys.exit(0)
        
    # 2. Lookup tool
    tool_config = registry.get_tool_for_flag(flag)
    
    if not tool_config:
        logger.error(f"❌ Unknown flag: {flag}")
        print("\nAvailable tools:")
        print_tools(registry)
        sys.exit(1)
        
    # 3. Execute tool
    module_name = tool_config["module"]
    function_name = tool_config["main_function"]
    
    try:
        # Import module
        module = importlib.import_module(module_name)
        
        # Get function
        if not hasattr(module, function_name):
            logger.error(f"❌ Entry point '{function_name}' not found in {module_name}")
            sys.exit(1)
            
        entry_point = getattr(module, function_name)
        
        # Prepare arguments
        # Remove the flag that routed us here
        # sys.argv[0] is the script path
        # sys.argv[1] is the flag (e.g. --monitor)
        # We want to present [module_name, args...] to the called module
        
        sys.argv = [module_name] + sys.argv[2:]
        
        logger.info(f"🚀 Executing {tool_config['name']} ({module_name})...")
        sys.exit(entry_point())
        
    except ImportError as e:
        logger.error(f"❌ Could not import module {module_name}: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error executing {tool_config['name']}: {e}")
        sys.exit(1)

def print_help(registry: ToolRegistry):
    """Print help message."""
    print("🐺 Swarm CLI Toolbelt")
    print("=====================")
    print("Usage: python -m tools.toolbelt [FLAG] [ARGS...]")
    print("\nCommon Flags:")
    print("  --help, -h    Show this help")
    print("  --list        List all available tools")
    print("\nUnified Tools:")
    for tool in registry.list_tools():
        flags = ", ".join(tool["flags"])
        print(f"  {flags:<20} {tool['description']}")

def print_tools(registry: ToolRegistry):
    """List all tools."""
    print("Available Tools:")
    for tool in registry.list_tools():
        print(f"\n🔹 {tool['name']}")
        print(f"   Flags: {', '.join(tool['flags'])}")
        print(f"   Desc:  {tool['description']}")

if __name__ == "__main__":
    main()
