import sys
import os
import json
from pathlib import Path

# Add workspace to path
sys.path.insert(0, os.getcwd())

def simulate_agent_usage():
    print("🤖 Simulating Agent Tool Usage (MCP Server)")
    print("==========================================")

    try:
        from swarm_mcp.servers.tools import list_available_tools, execute_toolbelt, TOOLS_REGISTRY
    except ImportError as e:
        print(f"❌ Failed to import MCP tools server: {e}")
        return

    # 1. List Tools
    print("\n🔍 1. Agent asks: 'What tools are available?'")
    tools = list_available_tools()
    print(f"✅ Server responds: {tools['count']} tools available")
    
    # Display first few tools
    for t in tools['tools'][:3]:
        print(f"   - {t['name']} (ID: {t['id']})")
        print(f"     Description: {t['description']}")

    # 2. Showcase Specific Tools
    showcase_scenarios = [
        {
            "id": "monitor",
            "name": "System Monitor",
            "args": [], 
            "description": "Checks system health (Queue, Service, Disk...)"
        },
        {
            "id": "validator",
            "name": "System Validator",
            "args": ["--help"], 
            "description": "Validates project (Help)"
        },
        {
            "id": "agent",
            "name": "Agent Tools",
            "args": ["--help"],
            "description": "Agent tools help"
        }
    ]
    
    print("\n🚀 2. Showcasing Tool Execution")
    print("-------------------------------")
    
    for scenario in showcase_scenarios:
        tool_id = scenario["id"]
        if tool_id not in TOOLS_REGISTRY:
            print(f"⚠️ Tool '{tool_id}' not found, skipping.")
            continue
            
        print(f"\n🔹 Scenario: {scenario['description']}")
        print(f"   Agent calls: run_tool('{tool_id}', arguments='{' '.join(scenario['args'])}')")
        
        flag = TOOLS_REGISTRY[tool_id]["flags"][0]
        # execute_toolbelt expects the flag and then list of args
        # But our fix in __main__.py handles sys.argv correctly now.
        
        result = execute_toolbelt(flag, scenario["args"])
        
        if result["success"]:
            print("   ✅ Execution successful!")
            
            # Print a snippet of stdout
            output = result["stdout"].strip()
            lines = output.split('\n')
            snippet = "\n      ".join(lines[:10])
            if len(lines) > 10:
                snippet += "\n      ... (truncated)"
            
            print(f"   Output:\n      {snippet}")
        else:
            print("   ❌ Execution failed")
            print(f"   Error: {result.get('error') or result.get('stderr')}")
            # Also print stdout in case of failure (e.g. help text or partial output)
            if result.get("stdout"):
                 print(f"   Stdout (partial): {result['stdout'][:200]}...")

if __name__ == "__main__":
    simulate_agent_usage()
