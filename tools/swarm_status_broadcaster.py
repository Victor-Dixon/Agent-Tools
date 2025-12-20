"""
Swarm Status Broadcaster - Automated messaging to multiple agents

PURPOSE: Simplify C-055 coordination by automating status broadcasts
CRITICAL FOR: Multi-agent coordination, reducing manual messaging overhead

<!-- SSOT Domain: infrastructure -->
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BroadcastMessage:
    """A message to broadcast to agents"""
    content: str
    priority: str = "regular"
    target_agents: Optional[List[str]] = None  # None = all agents
    use_pyautogui: bool = False


class SwarmStatusBroadcaster:
    """Broadcast status messages to multiple agents"""
    
    def __init__(self):
        self.all_agents = [
            "Agent-1", "Agent-2", "Agent-3", "Agent-4",
            "Agent-5", "Agent-6", "Agent-7", "Agent-8"
        ]
    
    def broadcast(
        self,
        message: str,
        priority: str = "regular",
        exclude_agents: Optional[List[str]] = None,
        include_only: Optional[List[str]] = None,
        use_pyautogui: bool = False
    ) -> Dict[str, bool]:
        """
        Broadcast message to agents
        
        Args:
            message: Message content
            priority: Message priority (regular/urgent)
            exclude_agents: Agents to exclude
            include_only: Only send to these agents
            use_pyautogui: Use PyAutoGUI for activation
        
        Returns:
            Dict of agent -> success status
        """
        # Determine target agents
        targets = include_only if include_only else self.all_agents
        if exclude_agents:
            targets = [a for a in targets if a not in exclude_agents]
        
        results = {}
        for agent in targets:
            success = self._send_to_agent(
                agent, message, priority, use_pyautogui
            )
            results[agent] = success
        
        return results
    
    def broadcast_c055_status(
        self,
        mission_id: str,
        completed: List[str],
        in_progress: List[str],
        pending: List[str],
        blockers: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """Broadcast C-055 coordination status"""
        
        message_parts = [
            f"📊 C-055 STATUS UPDATE - {mission_id}",
            "",
            f"✅ COMPLETED ({len(completed)}): {', '.join(completed) if completed else 'None'}",
            f"🔄 IN PROGRESS ({len(in_progress)}): {', '.join(in_progress) if in_progress else 'None'}",
            f"⏳ PENDING ({len(pending)}): {', '.join(pending) if pending else 'None'}"
        ]
        
        if blockers:
            message_parts.append(f"🚨 BLOCKERS: {', '.join(blockers)}")
        
        message_parts.append("")
        message_parts.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        message_parts.append("#C055-STATUS #SWARM-COORDINATION")
        
        message = "\n".join(message_parts)
        
        return self.broadcast(message, priority="regular")
    
    def broadcast_v2_progress(
        self,
        violations_fixed: int,
        violations_remaining: int,
        agents_working: List[str]
    ) -> Dict[str, bool]:
        """Broadcast V2 campaign progress"""
        
        total = violations_fixed + violations_remaining
        percent = (violations_fixed / total * 100) if total > 0 else 0
        
        message = f"""
📊 V2 CAMPAIGN PROGRESS UPDATE

✅ Fixed: {violations_fixed}
⏳ Remaining: {violations_remaining}
📈 Progress: {percent:.1f}%

🤖 Active Agents: {', '.join(agents_working)}

Keep pushing! Target: 100% compliance!
#V2-CAMPAIGN #SWARM-PROGRESS
"""
        return self.broadcast(message.strip(), priority="regular")
    
    def broadcast_achievement(
        self,
        agent: str,
        achievement: str,
        points: int
    ) -> Dict[str, bool]:
        """Broadcast agent achievement to celebrate success"""
        
        message = f"""
🏆 ACHIEVEMENT UNLOCKED!

Agent: {agent}
Achievement: {achievement}
Points: +{points}

Congratulations! Keep up the excellence!
#ACHIEVEMENT #SWARM-CELEBRATION
"""
        return self.broadcast(message.strip(), priority="regular")
    
    def _send_to_agent(
        self,
        agent: str,
        message: str,
        priority: str,
        use_pyautogui: bool
    ) -> bool:
        """Send message to a single agent"""
        try:
            cmd = [
                "python", "-m", "src.services.messaging_cli",
                "--agent", agent,
                "--message", message,
                "--priority", priority
            ]
            
            if use_pyautogui:
                cmd.append("--pyautogui")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_SHORT
            )
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"Failed to send to {agent}: {e}")
            return False
    
    def broadcast_with_template(
        self,
        template: str,
        replacements: Dict[str, str],
        **kwargs
    ) -> Dict[str, bool]:
        """Broadcast using a message template"""
        message = template
        for key, value in replacements.items():
            message = message.replace(f"{{{key}}}", str(value))
        
        return self.broadcast(message, **kwargs)


# Predefined templates
TEMPLATES = {
    "task_complete": """
✅ TASK COMPLETE: {task_id}

Agent: {agent}
Result: {result}
Points: +{points}

#TASK-COMPLETE #SWARM-PROGRESS
""",
    
    "blocker_identified": """
🚨 BLOCKER IDENTIFIED: {blocker}

Mission: {mission_id}
Impact: {impact}
Needs: {needs_agent}

Urgent coordination required!
#BLOCKER #URGENT
""",
    
    "phase_complete": """
🎉 PHASE COMPLETE: {phase}

Progress: {progress}
Next Phase: {next_phase}
Coordinator: {coordinator}

Keep the momentum!
#PHASE-COMPLETE #SWARM-MILESTONE
"""
}


def main():
    """CLI for swarm broadcasting"""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(
        description="Broadcast messages to swarm agents"
    )
    parser.add_argument(
        "--message",
        required=True,
        help="Message to broadcast"
    )
    parser.add_argument(
        "--priority",
        choices=["regular", "urgent"],
        default="regular",
        help="Message priority"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        help="Agents to exclude"
    )
    parser.add_argument(
        "--only",
        nargs="+",
        help="Only send to these agents"
    )
    parser.add_argument(
        "--pyautogui",
        action="store_true",
        help="Use PyAutoGUI for activation"
    )
    parser.add_argument(
        "--template",
        help="Use predefined template"
    )
    
    args = parser.parse_args()
    
    broadcaster = SwarmStatusBroadcaster()
    
    if args.template and args.template in TEMPLATES:
        print(f"Available template: {args.template}")
        print(TEMPLATES[args.template])
        return
    
    results = broadcaster.broadcast(
        message=args.message,
        priority=args.priority,
        exclude_agents=args.exclude,
        include_only=args.only,
        use_pyautogui=args.pyautogui
    )
    
    print("\n" + "=" * 80)
    print("BROADCAST RESULTS")
    print("=" * 80)
    
    success_count = sum(1 for s in results.values() if s)
    total_count = len(results)
    
    print(f"Sent: {success_count}/{total_count} agents")
    print("")
    
    for agent, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {agent}")
    
    print("")


if __name__ == "__main__":
    main()


