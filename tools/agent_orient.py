#!/usr/bin/env python3
"""
Agent Orientation Tool - Quick Discovery & Reference
Combines Agent-7's "enhance existing" + Agent-3's "auto-discovery"
"""
import sys
import json
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent


def quick_start():
    """2-minute overview - everything an agent needs to start"""
    print("""
🐝 AGENT QUICK START (2 MIN)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 YOUR FIRST 5 COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. See all tools:        python tools/agent_orient.py tools
2. Find anything:        python tools/agent_orient.py search "keyword"
3. Check your workspace: ls agent_workspaces/Agent-X/
4. Read inbox:          cat agent_workspaces/Agent-X/inbox/*
5. See systems:         python tools/agent_orient.py systems

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR MISSION WORKFLOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Check inbox for mission → agent_workspaces/Agent-X/inbox/
2. Find tools you need   → python tools/agent_orient.py search
3. Execute mission       → Use discovered tools
4. Report completion     → Update status.json, create devlog

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 EMERGENCY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Stuck?          → python tools/agent_orient.py help
- Need Captain?   → Message Agent-4 (Captain)
- Find tool docs? → cat AGENT_TOOLS_DOCUMENTATION.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ YOU'RE READY! Check your inbox and start your mission! 🚀
    """)


def list_systems():
    """Auto-discover all systems from project structure"""
    print("\n🗂️  PROJECT SYSTEMS\n")
    
    systems = {
        "Core": "src/core/ - Core functionality & engines",
        "Services": "src/services/ - Business logic services",
        "Web": "src/web/ - Frontend & API",
        "Domain": "src/domain/ - Domain models & entities",
        "Infrastructure": "src/infrastructure/ - External integrations",
        "Analytics": "src/analytics/ - Analytics & reporting",
        "Utils": "src/utils/ - Utilities & helpers",
        "Quality": "src/quality/ - Testing & QA",
        "Tools": "tools/ - Agent tools & utilities",
        "Swarm Brain": "swarm_brain/ - Knowledge repository"
    }
    
    for name, desc in systems.items():
        print(f"  • {name:15} → {desc}")
    
    print("\n💡 Explore: ls src/ to see all subsystems")


def list_tools():
    """Show available tools from toolbelt"""
    print("\n🛠️  TOP 20 AGENT TOOLS\n")
    
    tools = [
        ("analysis.*", "Project analysis & scanning"),
        ("test.*", "Testing tools (coverage, mutation, smoke)"),
        ("v2.*", "V2 compliance checking"),
        ("captain.*", "Captain coordination tools"),
        ("brain.*", "Swarm Brain knowledge access"),
        ("proposal.*", "Democratic proposal system"),
        ("agent.*", "Agent utilities"),
        ("obs.*", "Observability & monitoring"),
        ("mem.*", "Memory & performance tools"),
        ("integration.*", "Integration testing"),
        ("val.*", "Validation tools"),
        ("config.*", "Configuration management"),
        ("infra.*", "Infrastructure tools"),
        ("discord.*", "Discord integration"),
        ("advisor.*", "AI advisor tools"),
        ("debate.*", "Democratic debate system"),
        ("msgtask.*", "Message-task integration"),
        ("oss.*", "Open source contribution"),
        ("workflow.*", "Workflow optimization"),
        ("session.*", "Session management")
    ]
    
    for tool, desc in tools:
        print(f"  • {tool:20} → {desc}")
    
    print("\n📚 Full list: cat AGENT_TOOLS_DOCUMENTATION.md")
    print("💡 Try: python -m tools_v2.toolbelt_core (interactive)")


def search(query: str):
    """Simple search across key files"""
    print(f"\n🔍 SEARCHING FOR: '{query}'\n")
    
    # Search in key documentation files
    search_files = [
        "AGENT_TOOLS_DOCUMENTATION.md",
        "AGENTS.md",
        "README.md",
        "swarm_brain/DOCUMENTATION_INDEX.md"
    ]
    
    results = []
    for file in search_files:
        filepath = PROJECT_ROOT / file
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if query.lower() in content.lower():
                    # Find line with match
                    for i, line in enumerate(content.split('\n'), 1):
                        if query.lower() in line.lower():
                            results.append((file, i, line.strip()))
                            break
    
    if results:
        for file, line_no, line in results[:10]:  # Top 10
            print(f"  📄 {file}:{line_no}")
            print(f"     {line[:80]}...\n")
    else:
        print(f"  ❌ No results found for '{query}'")
        print("\n  💡 Try:")
        print(f"     - grep -r '{query}' src/")
        print(f"     - python -m tools.swarm_brain.search '{query}'")


def show_help():
    """Show all available commands"""
    print("""
🆘 AGENT ORIENTATION - HELP

COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  python tools/agent_orient.py quick      → 2-min quick start
  python tools/agent_orient.py systems    → List all systems
  python tools/agent_orient.py tools      → List available tools
  python tools/agent_orient.py search X   → Search for anything
  python tools/agent_orient.py help       → Show this help

KEY FILES TO KNOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  AGENT_TOOLS_DOCUMENTATION.md    → Complete tool reference
  AGENTS.md                        → Swarm information
  README.md                        → Project overview
  swarm_brain/                     → Knowledge base

YOUR WORKSPACE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  agent_workspaces/Agent-X/inbox/     → Your missions
  agent_workspaces/Agent-X/status.json → Your status
  devlogs/                            → Session summaries

WORKFLOWS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. Mission: Check inbox → Execute → Report
  2. Tool discovery: Search → Find tool → Use it
  3. Help: This tool → Docs → Swarm Brain → Captain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)


def main():
    if len(sys.argv) < 2:
        quick_start()
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd in ['quick', 'start', 'quickstart']:
        quick_start()
    elif cmd in ['systems', 'sys']:
        list_systems()
    elif cmd in ['tools', 'tool']:
        list_tools()
    elif cmd in ['search', 'find']:
        if len(sys.argv) < 3:
            print("Usage: python tools/agent_orient.py search 'keyword'")
        else:
            search(' '.join(sys.argv[2:]))
    elif cmd in ['help', 'h', '--help', '-h']:
        show_help()
    else:
        print(f"Unknown command: {cmd}")
        print("Run: python tools/agent_orient.py help")


if __name__ == "__main__":
    main()

