#!/usr/bin/env python3
"""
Agent Fuel Monitor - Automated GAS Delivery System
===================================================

Ensures agents don't run out of gas during long missions.

PROMPTS ARE GAS - this tool delivers periodic fuel!

Captain Agent-4 - 2025-10-14
V2 Compliant: Yes
<!-- SSOT Domain: infrastructure -->
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class AgentFuelMonitor:
    """Monitor agent activity and deliver periodic GAS to keep them fueled."""
    
    def __init__(self, mission_name: str = "75_repo_analysis"):
        self.project_root = Path(__file__).parent.parent
        self.mission_name = mission_name
        self.fuel_log = self.project_root / "runtime" / f"{mission_name}_fuel_log.json"
        self.fuel_log.parent.mkdir(exist_ok=True)
        
        # Agent coordinates for PyAutoGUI
        self.agent_coords = {
            "Agent-1": (-1269, 481),
            "Agent-2": (-308, 480),
            "Agent-3": (-1269, 1001),
            "Agent-4": (-308, 1000),
            "Agent-5": (652, 421),
            "Agent-6": (1612, 419),
            "Agent-7": (698, 936),
            "Agent-8": (1611, 941),
        }
    
    def load_fuel_log(self) -> Dict:
        """Load fuel delivery log."""
        if self.fuel_log.exists():
            with open(self.fuel_log, 'r') as f:
                return json.load(f)
        return {
            "mission": self.mission_name,
            "started": datetime.now().isoformat(),
            "agents": {
                agent_id: {
                    "last_fueled": datetime.now().isoformat(),
                    "fuel_count": 1,  # Initial GAS already delivered
                    "status": "active",
                }
                for agent_id in self.agent_coords.keys() if agent_id != "Agent-4"
            }
        }
    
    def save_fuel_log(self, log: Dict):
        """Save fuel delivery log."""
        with open(self.fuel_log, 'w') as f:
            json.dump(log, f, indent=2)
    
    def check_agent_activity(self, agent_id: str) -> Dict:
        """Check if agent has been active (produced devlogs, updated status, etc.)."""
        agent_workspace = self.project_root / "agent_workspaces" / agent_id
        
        activity = {
            "devlogs_count": 0,
            "last_devlog": None,
            "status_updated": None,
            "inbox_processed": False,
        }
        
        # Check for devlogs
        devlogs_dir = self.project_root / "devlogs"
        if devlogs_dir.exists():
            agent_devlogs = list(devlogs_dir.glob(f"*{agent_id.lower()}*.md"))
            activity["devlogs_count"] = len(agent_devlogs)
            if agent_devlogs:
                latest = max(agent_devlogs, key=lambda p: p.stat().st_mtime)
                activity["last_devlog"] = latest.stat().st_mtime
        
        # Check status.json
        status_file = agent_workspace / "status.json"
        if status_file.exists():
            activity["status_updated"] = status_file.stat().st_mtime
        
        # Check inbox (should be empty or processed)
        inbox_dir = agent_workspace / "inbox"
        if inbox_dir.exists():
            inbox_files = list(inbox_dir.glob("*.md"))
            activity["inbox_processed"] = len(inbox_files) == 0
        
        return activity
    
    def needs_refuel(self, agent_id: str, log: Dict, current_cycle: int) -> tuple[bool, str]:
        """
        Determine if agent needs refueling (more GAS).
        
        CYCLE-BASED, not time-based!
        
        Returns:
            (needs_fuel, reason)
        """
        agent_log = log["agents"].get(agent_id, {})
        last_cycle_fueled = agent_log.get("last_cycle_fueled", 0)
        
        # Refuel every 2-3 cycles
        cycles_since_fuel = current_cycle - last_cycle_fueled
        
        if cycles_since_fuel >= 3:
            return True, f"{cycles_since_fuel} cycles since last fuel"
        
        # Check activity
        activity = self.check_agent_activity(agent_id)
        
        # If no devlogs yet and 1+ cycle since fuel = needs encouragement
        if activity["devlogs_count"] == 0 and cycles_since_fuel >= 1:
            return True, f"No devlogs yet, {cycles_since_fuel} cycles since fuel"
        
        return False, "Agent well-fueled"
    
    def generate_jet_fuel_message(self, agent_id: str, current_cycle: int, activity: Dict, repos_assigned: int) -> str:
        """
        Generate JET FUEL message based on agent's progress.
        
        JET FUEL = High-octane activation prompts with:
        1. SPECIFIC next action (not vague encouragement)
        2. CONCRETE examples
        3. IMMEDIATE execution command
        4. CLEAR success criteria
        """
        
        devlogs_done = activity["devlogs_count"]
        repos_remaining = repos_assigned - devlogs_done
        
        if devlogs_done == 0:
            # No progress yet - JET FUEL push with SPECIFIC action
            return f"""⚡ JET FUEL! Cycle {current_cycle} - EXECUTE NOW!

IMMEDIATE ACTION: Pick your FIRST repo (repo #1 of {repos_assigned})

STEPS (30 minutes):
1. Clone repo: git clone <url>
2. Read README (5 min)
3. Check last commit date
4. Write 1-paragraph purpose
5. Write 1-paragraph utility for Agent_Cellphone_V2
6. Post devlog to Discord NOW

EXAMPLE: "This is a trading bot. Utility: Agent-6 could use the ROI calculation logic in optimization module."

DO IT NOW! Post first devlog this cycle! 🚀"""
        
        elif devlogs_done < repos_assigned // 3:
            # Early progress - JET FUEL with momentum
            return f"""⚡ JET FUEL! Cycle {current_cycle} - MOMENTUM BUILDING!

PROGRESS: {devlogs_done}/{repos_assigned} devlogs ✅
REMAINING: {repos_remaining} repos

NEXT ACTION: Repo #{devlogs_done + 1} THIS CYCLE

PROVEN PATTERN (works for you):
1. Quick scan (15 min)
2. Purpose + utility draft (10 min)
3. Post devlog (5 min)
4. DONE!

You've got the rhythm! Do repo #{devlogs_done + 1} NOW! 🎯"""
        
        elif devlogs_done < repos_assigned * 2 // 3:
            # Mid-progress - JET FUEL for the middle grind
            return f"""⚡ JET FUEL! Cycle {current_cycle} - CRUSHING IT!

PROGRESS: {devlogs_done}/{repos_assigned} done! 🏆
REMAINING: {repos_remaining} - YOU'RE HALFWAY!

THIS CYCLE: Complete 2 repos (double fuel!)

Repo #{devlogs_done + 1}: [QUICK 20-min analysis]
Repo #{devlogs_done + 2}: [QUICK 20-min analysis]

You're a machine! Keep the pace! EXECUTE NOW! 🚀"""
        
        else:
            # Near completion - JET FUEL final push
            return f"""⚡ JET FUEL! Cycle {current_cycle} - FINAL SPRINT!

PROGRESS: {devlogs_done}/{repos_assigned}! ALMOST THERE! 🎉
REMAINING: Only {repos_remaining} left!

FINISH LINE: In sight!

THIS CYCLE: Close it out!
- Repo #{devlogs_done + 1}: EXECUTE NOW
{f'- Repo #{devlogs_done + 2}: EXECUTE NOW' if repos_remaining > 1 else ''}

LEGENDARY FINISH! Complete mission this cycle! 🏆"""
    
    def deliver_fuel(self, agent_id: str, message: str) -> bool:
        """Deliver GAS to agent via PyAutoGUI messaging."""
        try:
            import subprocess
            
            cmd = [
                "python", "-m", "src.services.messaging_cli",
                "--agent", agent_id,
                "--message", message,
                "--priority", "regular",
                "--pyautogui"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Failed to deliver fuel to {agent_id}: {e}")
            return False
    
    def monitor_and_refuel(self, dry_run: bool = False) -> Dict:
        """
        Monitor all agents and deliver GAS as needed.
        
        Args:
            dry_run: If True, only report what would be done
            
        Returns:
            Report of actions taken
        """
        print("🔍 AGENT FUEL MONITOR - CHECKING ALL AGENTS")
        print("=" * 60)
        print()
        
        log = self.load_fuel_log()
        report = {
            "timestamp": datetime.now().isoformat(),
            "agents_checked": 0,
            "fuel_delivered": 0,
            "agents_well_fueled": 0,
            "actions": []
        }
        
        for agent_id in sorted(self.agent_coords.keys()):
            if agent_id == "Agent-4":  # Skip Captain
                continue
            
            report["agents_checked"] += 1
            
            # Check if needs fuel
            needs_fuel, reason = self.needs_refuel(agent_id, log)
            
            activity = self.check_agent_activity(agent_id)
            
            print(f"📊 {agent_id}:")
            print(f"   Devlogs: {activity['devlogs_count']}")
            print(f"   Last fuel: {log['agents'][agent_id]['last_fueled'][:19]}")
            print(f"   Needs fuel: {needs_fuel} ({reason})")
            
            if needs_fuel:
                fuel_count = log["agents"][agent_id]["fuel_count"] + 1
                message = self.generate_fuel_message(agent_id, fuel_count, activity)
                
                print(f"   ⚡ DELIVERING FUEL #{fuel_count}...")
                
                if not dry_run:
                    success = self.deliver_fuel(agent_id, message)
                    
                    if success:
                        # Update log
                        log["agents"][agent_id]["last_fueled"] = datetime.now().isoformat()
                        log["agents"][agent_id]["fuel_count"] = fuel_count
                        report["fuel_delivered"] += 1
                        print(f"   ✅ Fuel delivered!")
                    else:
                        print(f"   ❌ Fuel delivery failed")
                else:
                    print(f"   [DRY RUN] Would deliver: {message[:50]}...")
                
                report["actions"].append({
                    "agent": agent_id,
                    "action": "fuel_delivered",
                    "fuel_count": fuel_count,
                    "reason": reason
                })
            else:
                report["agents_well_fueled"] += 1
                print(f"   ✅ Well-fueled")
            
            print()
        
        if not dry_run:
            self.save_fuel_log(log)
        
        print("=" * 60)
        print(f"✅ MONITOR COMPLETE")
        print(f"   Agents checked: {report['agents_checked']}")
        print(f"   Fuel delivered: {report['fuel_delivered']}")
        print(f"   Well-fueled: {report['agents_well_fueled']}")
        print()
        
        return report
    
    def schedule_monitoring(self, interval_hours: int = 4):
        """
        Schedule periodic monitoring (prints cron/task scheduler command).
        
        Args:
            interval_hours: Hours between checks
        """
        script_path = Path(__file__).absolute()
        
        print(f"🕐 SCHEDULE FUEL MONITORING (every {interval_hours} hours)")
        print("=" * 60)
        print()
        print("Add to Windows Task Scheduler:")
        print(f"  python {script_path}")
        print(f"  Trigger: Repeat every {interval_hours} hours")
        print()
        print("Or add to cron (Linux/Mac):")
        print(f"  0 */{interval_hours} * * * python {script_path}")
        print()


def main():
    """CLI entry point."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(description="Monitor agents and deliver periodic GAS")
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't deliver fuel")
    parser.add_argument("--schedule", action="store_true", help="Show scheduling instructions")
    parser.add_argument("--mission", default="75_repo_analysis", help="Mission name")
    
    args = parser.parse_args()
    
    monitor = AgentFuelMonitor(mission_name=args.mission)
    
    if args.schedule:
        monitor.schedule_monitoring(interval_hours=4)
    else:
        monitor.monitor_and_refuel(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

