#!/usr/bin/env python3
"""
Debate Execution Tracker Hook - Spreadsheet Integration
=======================================================

Hooks into debate execution tracking to:
1. Update execution tracker when agents complete tasks (artifact paths, commit hashes)
2. Convert debate trackers to spreadsheet tasks
3. Integrate with project metrics dashboard

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-07
V2 Compliant: Yes
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_execution_tracker(
    topic: str,
    agent_id: str,
    status: str = "completed",
    artifact_paths: Optional[List[str]] = None,
    commit_hash: Optional[str] = None,
    pr_url: Optional[str] = None,
    evidence: Optional[str] = None
) -> bool:
    """
    Update debate execution tracker when agent completes task.
    
    Args:
        topic: Debate topic
        agent_id: Agent ID
        status: Task status (completed, in_progress, blocked)
        artifact_paths: List of artifact file paths
        commit_hash: Git commit hash
        pr_url: PR URL if applicable
        evidence: Evidence of completion
        
    Returns:
        True if updated successfully
    """
    workflow_dir = project_root / "workflow_states"
    tracker_file = workflow_dir / f"{topic}_execution.json"
    
    if not tracker_file.exists():
        logger.warning(f"Execution tracker not found: {tracker_file}")
        return False
    
    try:
        # Load existing tracker
        with open(tracker_file, "r", encoding="utf-8") as f:
            tracker = json.load(f)
        
        # Update agent status
        if "agents" not in tracker:
            tracker["agents"] = {}
        
        if agent_id not in tracker["agents"]:
            tracker["agents"][agent_id] = {
                "status": "assigned",
                "started": None,
                "completed": None,
                "artifact_paths": [],
            }
        
        agent_data = tracker["agents"][agent_id]
        agent_data["status"] = status
        
        if status == "completed":
            agent_data["completed"] = datetime.now().isoformat()
            if not agent_data.get("started"):
                agent_data["started"] = datetime.now().isoformat()
        
        # Append artifact paths
        if artifact_paths:
            if "artifact_paths" not in agent_data:
                agent_data["artifact_paths"] = []
            agent_data["artifact_paths"].extend(artifact_paths)
            # Remove duplicates
            agent_data["artifact_paths"] = list(set(agent_data["artifact_paths"]))
        
        # Add commit hash
        if commit_hash:
            agent_data["commit_hash"] = commit_hash
        
        # Add PR URL
        if pr_url:
            agent_data["pr_url"] = pr_url
        
        # Add evidence
        if evidence:
            agent_data["evidence"] = evidence
        
        # Update overall status
        all_agents = tracker.get("agents", {})
        all_completed = all(
            agent.get("status") == "completed"
            for agent in all_agents.values()
        )
        if all_completed:
            tracker["status"] = "completed"
            tracker["completed"] = datetime.now().isoformat()
        
        # Save updated tracker
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(tracker, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Updated execution tracker for {agent_id} on topic {topic}")

        # Emit telemetry heartbeat (non-blocking)
        try:
            from src.core.activity_emitter import emit_activity_event

            emit_activity_event(
                event_type="TASK_COMPLETED",
                source="debate_tracker",
                agent_id=agent_id or "SYSTEM",
                summary=f"Debate tracker update: {topic} ({status})",
                artifact={
                    "topic": topic,
                    "report_path": str(tracker_file),
                    "commit": commit_hash,
                    "pr_url": pr_url,
                    "artifact_paths": artifact_paths or [],
                },
                meta={
                    "status": status,
                    "decision": tracker.get("decision"),
                },
            )
        except Exception:
            pass

        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update execution tracker: {e}")
        return False


def debate_trackers_to_spreadsheet_tasks(
    output_file: Optional[str] = None,
    include_completed: bool = False
) -> List[Dict[str, Any]]:
    """
    Convert debate execution trackers to spreadsheet tasks.
    
    Args:
        output_file: Output CSV file path
        include_completed: Include completed tasks
        
    Returns:
        List of task dictionaries
    """
    workflow_dir = project_root / "workflow_states"
    
    if not workflow_dir.exists():
        logger.warning(f"Workflow states directory not found: {workflow_dir}")
        return []
    
    tasks = []
    
    # Find all execution trackers
    for tracker_file in workflow_dir.glob("*_execution.json"):
        try:
            with open(tracker_file, "r", encoding="utf-8") as f:
                tracker = json.load(f)
            
            topic = tracker.get("topic", tracker_file.stem.replace("_execution", ""))
            decision = tracker.get("decision", "")
            status = tracker.get("status", "assigned")
            
            # Skip completed if not including
            if status == "completed" and not include_completed:
                continue
            
            # Convert agent assignments to tasks
            agents = tracker.get("agents", {})
            for agent_id, agent_data in agents.items():
                agent_status = agent_data.get("status", "assigned")
                
                # Skip completed if not including
                if agent_status == "completed" and not include_completed:
                    continue
                
                task = agent_data.get("task", "")
                if not task:
                    continue
                
                # Create spreadsheet task
                spreadsheet_task = {
                    "category": "Debate Execution",
                    "task_type": "open_pr",
                    "task_payload": f"[Debate: {topic}] {task}\n\nDecision: {decision}",
                    "priority": "HIGH" if status == "assigned" else "MEDIUM",
                    "status": "pending" if agent_status == "assigned" else agent_status,
                    "run_github": "false",  # Set to true when ready
                    "result_url": agent_data.get("pr_url", ""),
                    "error_msg": "",
                    "updated_at": agent_data.get("completed") or agent_data.get("started") or "",
                    "topic": topic,
                    "agent": agent_id,
                    "decision": decision,
                    "artifact_paths": ", ".join(agent_data.get("artifact_paths", [])),
                    "commit_hash": agent_data.get("commit_hash", ""),
                    "title": f"[Debate] {topic}: {task[:50]}",
                    "body": f"Debate Topic: {topic}\nDecision: {decision}\n\nTask: {task}\n\nArtifacts: {', '.join(agent_data.get('artifact_paths', []))}"
                }
                
                tasks.append(spreadsheet_task)
        
        except Exception as e:
            logger.warning(f"Failed to process tracker {tracker_file}: {e}")
            continue
    
    # Write to CSV if output file specified
    if tasks and output_file:
        import csv
        columns = [
            "category", "task_type", "task_payload", "priority", "status",
            "run_github", "result_url", "error_msg", "updated_at",
            "topic", "agent", "decision", "artifact_paths", "commit_hash",
            "title", "body"
        ]
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(tasks)
        
        logger.info(f"✅ Generated {len(tasks)} debate tasks: {output_file}")
    elif tasks:
        logger.info(f"✅ Generated {len(tasks)} debate tasks (in-memory)")
    
    return tasks


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Debate execution tracker integration"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update execution tracker"
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Debate topic"
    )
    parser.add_argument(
        "--agent",
        type=str,
        help="Agent ID"
    )
    parser.add_argument(
        "--status",
        type=str,
        choices=["completed", "in_progress", "blocked"],
        help="Task status"
    )
    parser.add_argument(
        "--artifact",
        type=str,
        action="append",
        help="Artifact path (can specify multiple)"
    )
    parser.add_argument(
        "--commit",
        type=str,
        help="Commit hash"
    )
    parser.add_argument(
        "--pr-url",
        type=str,
        help="PR URL"
    )
    parser.add_argument(
        "--evidence",
        type=str,
        help="Evidence of completion"
    )
    parser.add_argument(
        "--to-spreadsheet",
        type=str,
        help="Convert trackers to spreadsheet tasks"
    )
    parser.add_argument(
        "--include-completed",
        action="store_true",
        help="Include completed tasks in spreadsheet"
    )
    
    args = parser.parse_args()
    
    if args.update:
        if not args.topic or not args.agent:
            logger.error("--topic and --agent required for --update")
            sys.exit(1)
        
        success = update_execution_tracker(
            topic=args.topic,
            agent_id=args.agent,
            status=args.status or "completed",
            artifact_paths=args.artifact,
            commit_hash=args.commit,
            pr_url=args.pr_url,
            evidence=args.evidence
        )
        
        if success:
            logger.info("✅ Execution tracker updated")
        else:
            logger.error("❌ Failed to update tracker")
            sys.exit(1)
    
    elif args.to_spreadsheet:
        tasks = debate_trackers_to_spreadsheet_tasks(
            output_file=args.to_spreadsheet,
            include_completed=args.include_completed
        )
        logger.info(f"✅ Generated {len(tasks)} tasks in spreadsheet")
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

