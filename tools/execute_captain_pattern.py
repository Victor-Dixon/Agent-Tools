#!/usr/bin/env python3
"""
Execute Captain Pattern - Full Workflow
========================================

Executes the complete Captain Restart Pattern V2:
1. Check agent statuses for staleness
2. Resume stalled agents with optimized resume messages
3. Assign tasks to all 8 agents from FULL_SWARM_ACTIVATION

Author: Agent-4 (Captain)
Date: 2025-12-05
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

from src.core.config.timeout_constants import TimeoutConstants

def check_agent_statuses() -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """Check all agent statuses and categorize by staleness."""
    
    agents = ['Agent-1', 'Agent-2', 'Agent-3', 'Agent-5', 'Agent-6', 'Agent-7', 'Agent-8', 'Agent-4']
    workspace_root = Path("agent_workspaces")
    
    fresh_agents = []
    warning_agents = []
    critical_agents = []
    auto_resume_agents = []
    
    now = datetime.now()
    
    for agent_id in agents:
        status_file = workspace_root / agent_id / "status.json"
        
        if not status_file.exists():
            auto_resume_agents.append({
                "agent_id": agent_id,
                "status": "NO_STATUS_FILE",
                "hours_old": None,
                "last_updated": None
            })
            continue
        
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            
            last_updated_str = status.get('last_updated', '')
            agent_status = status.get('status', 'UNKNOWN')
            mission = status.get('current_mission', 'N/A')
            
            if not last_updated_str:
                auto_resume_agents.append({
                    "agent_id": agent_id,
                    "status": agent_status,
                    "hours_old": None,
                    "last_updated": None,
                    "mission": mission
                })
                continue
            
            # Parse timestamp
            try:
                if 'T' in last_updated_str:
                    if last_updated_str.endswith('Z'):
                        last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
                    else:
                        last_updated = datetime.fromisoformat(last_updated_str)
                else:
                    last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S')
            except Exception:
                auto_resume_agents.append({
                    "agent_id": agent_id,
                    "status": agent_status,
                    "hours_old": None,
                    "last_updated": last_updated_str,
                    "mission": mission,
                    "error": "Invalid timestamp"
                })
                continue
            
            # Calculate hours since update
            if last_updated.tzinfo:
                hours_old = (now - last_updated.replace(tzinfo=None)).total_seconds() / 3600
            else:
                hours_old = (now - last_updated).total_seconds() / 3600
            
            agent_info = {
                "agent_id": agent_id,
                "status": agent_status,
                "hours_old": round(hours_old, 1),
                "last_updated": last_updated_str,
                "mission": mission[:60]
            }
            
            # Categorize by staleness thresholds
            if hours_old < 2:
                fresh_agents.append(agent_info)
            elif hours_old < 6:
                warning_agents.append(agent_info)
            elif hours_old < 12:
                critical_agents.append(agent_info)
            else:
                auto_resume_agents.append(agent_info)
                
        except Exception as e:
            auto_resume_agents.append({
                "agent_id": agent_id,
                "status": "ERROR",
                "hours_old": None,
                "last_updated": None,
                "error": str(e)
            })
    
    return fresh_agents, warning_agents, critical_agents, auto_resume_agents


def send_resume_message(agent_id: str, hours_old: float) -> bool:
    """Send optimized resume message to agent."""
    try:
        from src.core.optimized_stall_resume_prompt import generate_optimized_resume_prompt
        
        # Convert hours to minutes for stall duration
        stall_duration_minutes = hours_old * 60.0 if hours_old else 0.0
        
        # Generate optimized resume prompt with goal alignment
        resume_prompt = generate_optimized_resume_prompt(
            agent_id=agent_id,
            fsm_state=None,  # Will be loaded from status.json
            last_mission=None,  # Will be loaded from status.json
            stall_duration_minutes=stall_duration_minutes
        )
        
        # Send via messaging CLI
        project_root = Path(__file__).parent.parent
        cmd = [
            sys.executable,
            "-m",
            "src.services.messaging_cli",
            "--agent",
            agent_id,
            "--message",
            resume_prompt,
            "--priority",
            "urgent",
        ]
        
        env = {"PYTHONPATH": str(project_root)}
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_DEFAULT,
            env=env,
            cwd=str(project_root)
        )
        
        if result.returncode == 0:
            print(f"✅ Resume message sent to {agent_id}")
            return True
        else:
            print(f"⚠️ Failed to send resume to {agent_id}: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending resume to {agent_id}: {e}")
        return False


def send_task_assignment(agent_id: str, mission: str, tasks: List[str], priority: str = "HIGH") -> bool:
    """Send task assignment message to agent."""
    try:
        tasks_text = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
        
        message = f"""🚀 TASK ASSIGNMENT - {agent_id}

**Mission**: {mission}

**Tasks**:
{tasks_text}

**Instructions**:
- Execute these tasks immediately
- Report progress via Discord updates in your agent channel
- Update status.json with progress
- Use Force Multiplier Pattern if tasks are too large

**Priority**: {priority}

🐝 WE. ARE. SWARM. ⚡🔥"""
        
        project_root = Path(__file__).parent.parent
        cmd = [
            sys.executable,
            "-m",
            "src.services.messaging_cli",
            "--agent",
            agent_id,
            "--message",
            message,
            "--priority",
            priority.lower(),
        ]
        
        env = {"PYTHONPATH": str(project_root)}
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_DEFAULT,
            env=env,
            cwd=str(project_root)
        )
        
        if result.returncode == 0:
            print(f"✅ Task assignment sent to {agent_id}")
            return True
        else:
            print(f"⚠️ Failed to send assignment to {agent_id}: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending assignment to {agent_id}: {e}")
        return False


def load_full_swarm_activation() -> Dict[str, Dict]:
    """Load task assignments from FULL_SWARM_ACTIVATION document."""
    activation_file = Path("agent_workspaces/Agent-4/FULL_SWARM_ACTIVATION_2025-12-05.md")
    
    if not activation_file.exists():
        return {}
    
    try:
        content = activation_file.read_text(encoding='utf-8')
        assignments = {}
        
        # Parse agent sections
        import re
        agent_pattern = r'### \*\*(Agent-\d+):\s*(.+?)\*\*\s*\n\*\*Mission\*\*:\s*(.+?)\n\*\*Tasks\*\*:\s*\n(.*?)(?=\n---|\n### \*\*|$)'
        
        matches = re.finditer(agent_pattern, content, re.DOTALL)
        
        for match in matches:
            agent_id = match.group(1)
            agent_name = match.group(2)
            mission = match.group(3).strip()
            tasks_section = match.group(4)
            
            # Extract tasks (numbered list items)
            task_lines = []
            for line in tasks_section.split('\n'):
                line = line.strip()
                if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                    # Clean up task text
                    task_text = re.sub(r'^\d+\.\s+\*\*(?:URGENT|HIGH|MEDIUM|CRITICAL)\*\*:\s*', '', line)
                    if task_text:
                        task_lines.append(task_text[:200])  # Limit length
            
            if task_lines:
                assignments[agent_id] = {
                    "mission": mission,
                    "tasks": task_lines[:3],  # Top 3 tasks
                    "priority": "CRITICAL" if "CRITICAL" in tasks_section else "HIGH"
                }
        
        return assignments
        
    except Exception as e:
        print(f"⚠️ Error loading FULL_SWARM_ACTIVATION: {e}")
        return {}


def main():
    """Execute Captain Pattern workflow."""
    print("=" * 70)
    print("CAPTAIN PATTERN EXECUTION - Full Workflow")
    print("=" * 70)
    print()
    
    # Step 1: Check agent statuses
    print("Step 1: Checking agent statuses...")
    fresh, warning, critical, auto_resume = check_agent_statuses()
    
    print(f"\n📊 Status Summary:")
    print(f"  🟢 Fresh (<2h): {len(fresh)}")
    print(f"  🟡 Warning (2-6h): {len(warning)}")
    print(f"  🟠 Critical (6-12h): {len(critical)}")
    print(f"  🔴 Auto-Resume (>12h): {len(auto_resume)}")
    print()
    
    # Step 2: Resume stalled agents
    agents_to_resume = critical + auto_resume
    if agents_to_resume:
        print("Step 2: Resuming stalled agents...")
        for agent in agents_to_resume:
            hours_old = agent.get('hours_old', 0) or 12.0  # Default to 12h if unknown
            print(f"  - Resuming {agent['agent_id']} ({hours_old}h stale)...")
            send_resume_message(agent['agent_id'], hours_old)
            print()
    
    # Step 3: Load task assignments
    print("Step 3: Loading task assignments from FULL_SWARM_ACTIVATION...")
    assignments = load_full_swarm_activation()
    print(f"  ✅ Loaded assignments for {len(assignments)} agents")
    print()
    
    # Step 4: Assign tasks to all agents
    print("Step 4: Assigning tasks to all 8 agents...")
    
    # Agents to assign tasks to
    all_agents = ['Agent-1', 'Agent-2', 'Agent-3', 'Agent-5', 'Agent-6', 'Agent-7', 'Agent-8']
    
    for agent_id in all_agents:
        if agent_id in assignments:
            assignment = assignments[agent_id]
            print(f"  - Assigning tasks to {agent_id}...")
            
            # Determine priority (URGENT for stale agents, HIGH for others)
            is_stale = any(a['agent_id'] == agent_id for a in agents_to_resume)
            priority = "URGENT" if is_stale else assignment.get('priority', 'HIGH')
            
            send_task_assignment(
                agent_id=agent_id,
                mission=assignment['mission'],
                tasks=assignment['tasks'],
                priority=priority
            )
            print()
    
    print("=" * 70)
    print("✅ CAPTAIN PATTERN EXECUTION COMPLETE")
    print("=" * 70)
    print(f"  - Resumed: {len(agents_to_resume)} agents")
    print(f"  - Assigned tasks: {len(assignments)} agents")
    print()


if __name__ == "__main__":
    main()


