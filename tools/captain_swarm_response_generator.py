#!/usr/bin/env python3
"""
🐝 CAPTAIN SWARM RESPONSE GENERATOR
===================================

Automatically generates and sends Captain responses to all agents
based on their status.json files. Helps overloaded Agent-4 respond
to workspace messages efficiently.

V2 Compliance: <300 lines, single responsibility
Author: Agent-1 (Captain Support)
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CaptainSwarmResponseGenerator:
    """Generates Captain responses for all agents based on status files."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the generator."""
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = project_root
        self.agent_workspaces = project_root / "agent_workspaces"

    def read_agent_status(self, agent_id: str) -> dict[str, Any] | None:
        """Read agent status.json file."""
        status_file = self.agent_workspaces / agent_id / "status.json"
        if not status_file.exists():
            return None
        try:
            return json.loads(status_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Error reading {agent_id} status: {e}")
            return None

    def generate_response(self, agent_id: str, status: dict[str, Any]) -> str:
        """Generate appropriate Captain response based on agent status."""
        agent_name = status.get("agent_name", agent_id)
        current_mission = status.get("current_mission", "")
        current_tasks = status.get("current_tasks", [])
        last_updated = status.get("last_updated", "")
        next_actions = status.get("next_actions", [])
        
        # Analyze status
        completed_tasks = [t for t in current_tasks if "✅" in t or "COMPLETE" in t.upper()]
        active_tasks = [t for t in current_tasks if "⏳" in t or "ACTIVE" in t.upper()]
        blockers = [t for t in current_tasks if "🚨" in t or "BLOCKER" in t.upper()]
        
        # Generate response based on status
        response = f"""✅ CAPTAIN ACKNOWLEDGMENT: {agent_id} Status Review

**Agent**: {agent_name}
**Last Updated**: {last_updated}
**Mission**: {current_mission[:100] if current_mission else "Active operations"}

## 📊 STATUS SUMMARY

"""
        
        if completed_tasks:
            response += f"**✅ Completed Tasks**: {len(completed_tasks)} tasks complete\n"
            if len(completed_tasks) <= 3:
                for task in completed_tasks[:3]:
                    response += f"- {task[:80]}...\n"
        
        if active_tasks:
            response += f"\n**⏳ Active Tasks**: {len(active_tasks)} tasks in progress\n"
            if len(active_tasks) <= 3:
                for task in active_tasks[:3]:
                    response += f"- {task[:80]}...\n"
        
        if blockers:
            response += f"\n**🚨 Blockers**: {len(blockers)} blockers identified\n"
            for blocker in blockers[:3]:
                # Extract key blocker info
                blocker_text = blocker[:150] if len(blocker) > 150 else blocker
                response += f"- {blocker_text}\n"
        
        response += "\n## 🎯 NEXT STEPS\n\n"
        
        if next_actions:
            for action in next_actions[:3]:
                action_text = action[:120] if len(action) > 120 else action
                response += f"- {action_text}\n"
        else:
            response += "- Continue excellent work\n"
            response += "- Update status.json regularly\n"
            response += "- Post devlog when complete\n"
        
        response += "\n## 💬 CAPTAIN NOTES\n\n"
        
        # More specific notes based on actual status
        if blockers:
            # Identify specific blocker types
            blocker_keywords = []
            for blocker in blockers:
                blocker_lower = blocker.lower()
                if "circular import" in blocker_lower or "import" in blocker_lower:
                    blocker_keywords.append("circular import")
                if "disk space" in blocker_lower or "space" in blocker_lower:
                    blocker_keywords.append("disk space")
                if "github" in blocker_lower or "pr" in blocker_lower:
                    blocker_keywords.append("GitHub/PR")
                if "test" in blocker_lower:
                    blocker_keywords.append("test coverage")
            
            if blocker_keywords:
                response += f"🚨 **BLOCKERS DETECTED**: {', '.join(set(blocker_keywords[:3]))}. Captain coordinating resolution.\n\n"
            else:
                response += "🚨 **BLOCKERS DETECTED**: Captain reviewing blockers and coordinating resolution.\n\n"
        elif len(completed_tasks) > len(active_tasks) * 2:
            response += "✅ **EXCELLENT PROGRESS**: Strong completion rate ({:.0f}% completion ratio). Maintain momentum!\n\n".format(
                (len(completed_tasks) / max(len(active_tasks), 1)) * 100
            )
        elif len(completed_tasks) > len(active_tasks):
            response += "✅ **GOOD PROGRESS**: More completions than active tasks. Keep executing!\n\n"
        else:
            response += "⏳ **ACTIVE WORK**: {active} active tasks progressing. Continue execution.\n\n".format(
                active=len(active_tasks)
            )
        
        response += """**WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀**

---
*Auto-generated Captain response via Swarm Response Generator*
"""
        
        return response

    def send_response(self, agent_id: str, response: str) -> bool:
        """Send response via messaging system."""
        try:
            sys.path.insert(0, str(self.project_root))
            
            from src.core.messaging_core import (
                UnifiedMessagePriority,
                UnifiedMessageTag,
                UnifiedMessageType,
                send_message,
            )
            
            success = send_message(
                content=response,
                sender="Captain Agent-4",
                recipient=agent_id,
                message_type=UnifiedMessageType.TEXT,
                priority=UnifiedMessagePriority.REGULAR,
                tags=[UnifiedMessageTag.CAPTAIN],
            )
            
            if success:
                logger.info(f"✅ Response sent to {agent_id}")
            else:
                logger.warning(f"⚠️ Failed to send response to {agent_id}")
            
            return success
        except Exception as e:
            logger.error(f"❌ Error sending response to {agent_id}: {e}")
            return False

    def process_all_agents(self, auto_send: bool = False) -> dict[str, Any]:
        """Process all agents and generate responses."""
        agents = ["Agent-1", "Agent-2", "Agent-3", "Agent-5", "Agent-6", "Agent-7", "Agent-8"]
        
        results = {
            "total": len(agents),
            "processed": 0,
            "responses": [],
            "errors": [],
        }
        
        for agent_id in agents:
            try:
                status = self.read_agent_status(agent_id)
                if not status:
                    results["errors"].append({"agent": agent_id, "error": "Status file not found"})
                    continue
                
                response = self.generate_response(agent_id, status)
                
                response_data = {
                    "agent": agent_id,
                    "response": response,
                    "sent": False,
                }
                
                if auto_send:
                    success = self.send_response(agent_id, response)
                    response_data["sent"] = success
                
                results["responses"].append(response_data)
                results["processed"] += 1
                
            except Exception as e:
                logger.error(f"❌ Error processing {agent_id}: {e}")
                results["errors"].append({"agent": agent_id, "error": str(e)})
        
        return results

    def generate_summary_report(self, results: dict[str, Any]) -> str:
        """Generate summary report."""
        report = f"""# 📊 CAPTAIN SWARM RESPONSE REPORT

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- **Total Agents**: {results['total']}
- **Processed**: {results['processed']}
- **Responses Generated**: {len(results['responses'])}
- **Errors**: {len(results['errors'])}

## Responses Generated
"""
        for resp in results["responses"]:
            status = "✅ SENT" if resp.get("sent") else "📝 READY"
            report += f"\n### {status}: {resp['agent']}\n"
            report += f"**Response Preview**: {resp['response'][:150]}...\n"
        
        if results["errors"]:
            report += "\n## Errors\n"
            for error in results["errors"]:
                report += f"- **{error.get('agent', 'Unknown')}**: {error.get('error', 'Unknown error')}\n"
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Captain Swarm Response Generator")
    parser.add_argument("--process", action="store_true", help="Process all agents and generate responses")
    parser.add_argument("--auto-send", action="store_true", help="Automatically send responses")
    parser.add_argument("--report", action="store_true", help="Generate summary report")
    
    args = parser.parse_args()
    
    generator = CaptainSwarmResponseGenerator()
    
    if args.process:
        results = generator.process_all_agents(auto_send=args.auto_send)
        
        if args.report:
            report = generator.generate_summary_report(results)
            print(report)
            
            # Save report
            report_path = generator.project_root / "agent_workspaces" / "Agent-4" / "swarm_response_report.md"
            report_path.write_text(report, encoding="utf-8")
            print(f"\n✅ Report saved to: {report_path}")
        else:
            print(f"\n📊 Processed {results['processed']} agents")
            print(f"✅ Generated {len(results['responses'])} responses")
            if results['errors']:
                print(f"❌ {len(results['errors'])} errors")


if __name__ == "__main__":
    main()

