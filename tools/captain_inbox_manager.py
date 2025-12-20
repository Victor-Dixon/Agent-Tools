#!/usr/bin/env python3
"""
Captain Inbox Manager
=====================

Helps Captain Agent-4 manage inbox messages efficiently.
Categorizes, summarizes, and generates batch responses.

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <300 lines
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def categorize_message(file_path: Path) -> Dict[str, Any]:
    """
    Categorize a message file.
    
    Args:
        file_path: Path to message file
        
    Returns:
        Dict with category, priority, agent, and summary
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Extract metadata
        category = "unknown"
        priority = "normal"
        agent = "unknown"
        summary = ""
        
        # Check for priority markers
        if "🚨 URGENT" in content or "URGENT" in content.upper():
            priority = "urgent"
        elif "HIGH PRIORITY" in content.upper() or "HIGH" in content.upper():
            priority = "high"
        elif "CRITICAL" in content.upper():
            priority = "critical"
        
        # Check for agent mentions
        for agent_id in ["Agent-1", "Agent-2", "Agent-3", "Agent-5", "Agent-6", "Agent-7", "Agent-8"]:
            if agent_id in content:
                agent = agent_id
                break
        
        # Categorize by content
        if "ACKNOWLEDGMENT" in content.upper() or "ACKNOWLEDGED" in content.upper():
            category = "acknowledgment"
        elif "COMPLETE" in content.upper() or "COMPLETED" in content.upper():
            category = "completion"
        elif "STATUS" in content.upper() or "REPORT" in content.upper():
            category = "status_report"
        elif "ERROR" in content.upper() or "BLOCKER" in content.upper():
            category = "error_blocker"
        elif "TASK" in content.upper() or "ASSIGNMENT" in content.upper():
            category = "task_assignment"
        elif "TECHNICAL DEBT" in content.upper():
            category = "technical_debt"
        
        # Extract summary (first 200 chars)
        lines = content.split('\n')
        for line in lines[:20]:
            if line.strip() and not line.startswith('#') and not line.startswith('**'):
                summary = line.strip()[:200]
                break
        
        return {
            "file": str(file_path.name),
            "category": category,
            "priority": priority,
            "agent": agent,
            "summary": summary,
            "date": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "file": str(file_path.name),
            "category": "error",
            "priority": "normal",
            "agent": "unknown",
            "summary": f"Error reading file: {e}",
            "date": "unknown"
        }


def analyze_inbox(inbox_path: Path) -> Dict[str, Any]:
    """
    Analyze Captain's inbox.
    
    Args:
        inbox_path: Path to Agent-4 inbox
        
    Returns:
        Dict with analysis results
    """
    messages = []
    categories = {}
    priorities = {"urgent": 0, "critical": 0, "high": 0, "normal": 0}
    agents = {}
    
    for msg_file in inbox_path.glob("*.md"):
        msg_info = categorize_message(msg_file)
        messages.append(msg_info)
        
        # Count categories
        cat = msg_info["category"]
        categories[cat] = categories.get(cat, 0) + 1
        
        # Count priorities
        prio = msg_info["priority"]
        priorities[prio] = priorities.get(prio, 0) + 1
        
        # Count agents
        agent = msg_info["agent"]
        if agent != "unknown":
            agents[agent] = agents.get(agent, 0) + 1
    
    # Sort by priority and date
    messages.sort(key=lambda x: (
        {"urgent": 0, "critical": 1, "high": 2, "normal": 3}.get(x["priority"], 4),
        x["date"]
    ))
    
    return {
        "total_messages": len(messages),
        "categories": categories,
        "priorities": priorities,
        "agents": agents,
        "messages": messages
    }


def generate_summary_report(analysis: Dict[str, Any]) -> str:
    """Generate a summary report."""
    report = []
    report.append("# 📊 Captain Inbox Analysis Report")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n**Total Messages**: {analysis['total_messages']}")
    
    report.append("\n## 📋 **By Priority**")
    for priority, count in sorted(analysis['priorities'].items(), key=lambda x: {"urgent": 0, "critical": 1, "high": 2, "normal": 3}.get(x[0], 4)):
        report.append(f"- **{priority.upper()}**: {count}")
    
    report.append("\n## 📂 **By Category**")
    for category, count in sorted(analysis['categories'].items(), key=lambda x: -x[1]):
        report.append(f"- **{category}**: {count}")
    
    report.append("\n## 👥 **By Agent**")
    for agent, count in sorted(analysis['agents'].items(), key=lambda x: -x[1]):
        report.append(f"- **{agent}**: {count} messages")
    
    report.append("\n## 🚨 **Urgent/Critical Messages**")
    urgent_msgs = [m for m in analysis['messages'] if m['priority'] in ['urgent', 'critical']]
    if urgent_msgs:
        for msg in urgent_msgs[:10]:
            report.append(f"- **{msg['file']}** ({msg['priority']}) - {msg['agent']}: {msg['summary'][:100]}")
    else:
        report.append("- No urgent/critical messages")
    
    report.append("\n## 📝 **Recent Messages** (Last 10)")
    for msg in analysis['messages'][:10]:
        report.append(f"- **{msg['file']}** ({msg['date']}) - {msg['agent']}: {msg['summary'][:100]}")
    
    return "\n".join(report)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Captain Inbox Manager")
    parser.add_argument("--analyze", action="store_true", help="Analyze inbox")
    parser.add_argument("--summary", action="store_true", help="Generate summary report")
    parser.add_argument("--output", type=Path, help="Output file for report")
    
    args = parser.parse_args()
    
    inbox_path = project_root / "agent_workspaces" / "Agent-4" / "inbox"
    
    if not inbox_path.exists():
        print(f"❌ Inbox not found: {inbox_path}")
        return 1
    
    analysis = analyze_inbox(inbox_path)
    
    if args.summary or args.analyze:
        report = generate_summary_report(analysis)
        
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding='utf-8')
            print(f"✅ Report saved to: {args.output}")
        else:
            print(report)
    
    # Always print quick stats
    print(f"\n📊 Quick Stats:")
    print(f"   Total: {analysis['total_messages']} messages")
    print(f"   Urgent/Critical: {analysis['priorities'].get('urgent', 0) + analysis['priorities'].get('critical', 0)}")
    print(f"   High: {analysis['priorities'].get('high', 0)}")
    print(f"   Normal: {analysis['priorities'].get('normal', 0)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

