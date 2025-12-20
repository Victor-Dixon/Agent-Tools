#!/usr/bin/env python3
"""
Captain Task Assigner
=====================

Automates task assignment to agents based on priorities and specializations.
Uses swarm as force multiplier for parallel execution.

Author: Agent-5 (Acting as Captain)
Date: 2025-12-02
Priority: HIGH - Captain Operations
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from captain_swarm_coordinator import CaptainSwarmCoordinator


class CaptainTaskAssigner:
    """Automates task assignment to swarm agents."""

    def __init__(self):
        """Initialize task assigner."""
        self.coordinator = CaptainSwarmCoordinator()
        self.assignments_log: List[Dict[str, Any]] = []

    def assign_critical_tasks(self):
        """Assign critical priority tasks to appropriate agents."""
        assignments = []
        
        # Agent-1: Output Flywheel Phase 2
        task1 = self.coordinator.assign_task_to_agent(
            agent_id="Agent-1",
            task="Complete Output Flywheel Phase 2 - Implement 10 missing components",
            priority="CRITICAL",
            description="""
MISSING COMPONENTS:
- pipelines/build_artifact.py
- pipelines/trade_artifact.py  
- pipelines/life_aria_artifact.py
- processors/repo_scanner.py
- processors/story_extractor.py
- processors/readme_generator.py
- processors/build_log_generator.py
- processors/social_generator.py
- processors/trade_processor.py
- tools/run_output_flywheel.py

IMPACT: Blocks Output Flywheel v1.0 production readiness
TIMELINE: IMMEDIATE
            """.strip(),
        )
        assignments.append(task1)
        
        # Agent-2: PR Blockers
        task2 = self.coordinator.assign_task_to_agent(
            agent_id="Agent-2",
            task="Resolve 2 PR Blockers - DreamBank PR #1 and MeTuber PR #13",
            priority="CRITICAL",
            description="""
BLOCKED PRs:
1. DreamBank PR #1 (Dadudekc/DreamVault)
   - Remove draft status, mark ready for review, merge
   - URL: https://github.com/Dadudekc/DreamVault/pull/1

2. MeTuber PR #13 (Dadudekc/Streamertools)
   - Ready to merge, execute merge
   - URL: https://github.com/Dadudekc/Streamertools/pull/13

IMPACT: Blocks GitHub consolidation progress
TIMELINE: IMMEDIATE
            """.strip(),
        )
        assignments.append(task2)
        
        # Agent-3: Test Suite Validation
        task3 = self.coordinator.assign_task_to_agent(
            agent_id="Agent-3",
            task="Complete Test Suite Validation - CRITICAL BLOCKER",
            priority="CRITICAL",
            description="""
BLOCKS: File deletion execution (44 files waiting)

ACTION:
- Complete interrupted test suite validation
- Verify all tests pass
- Report validation status

IMPACT: Unblocks file deletion cleanup
TIMELINE: IMMEDIATE
            """.strip(),
        )
        assignments.append(task3)
        
        # Agent-7: Website Deployment
        task4 = self.coordinator.assign_task_to_agent(
            agent_id="Agent-7",
            task="Coordinate Website Deployment - 3 sites pending",
            priority="HIGH",
            description="""
PENDING DEPLOYMENTS:
1. prismblossom.online - CSS text rendering fix
2. FreeRideInvestor - Menu filter cleanup (18 Developer Tools links)
3. southwestsecret.com - (if applicable)

ACTION:
- Coordinate human deployment OR
- Find automation solution
- Verify deployments after completion

IMPACT: User-facing issues persist until deployed
TIMELINE: IMMEDIATE
            """.strip(),
        )
        assignments.append(task4)
        
        # Agent-8: File Deletion Content Comparison
        task5 = self.coordinator.assign_task_to_agent(
            agent_id="Agent-8",
            task="File Deletion Content Comparison - 30-35 duplicate files",
            priority="HIGH",
            description="""
ACTION:
- Complete content comparison for ~30-35 duplicate files
- Make final deletion decisions
- Verify SSOT compliance for config/ssot.py

IMPACT: Blocks cleanup, prevents false deletions
TIMELINE: Next session
            """.strip(),
        )
        assignments.append(task5)
        
        self.assignments_log.extend(assignments)
        return assignments

    def assign_technical_debt_markers(self, markers_file: Path):
        """Assign technical debt markers to agents by file ownership."""
        if not markers_file.exists():
            print(f"❌ Markers file not found: {markers_file}")
            return []
        
        with open(markers_file, "r", encoding="utf-8") as f:
            analysis = json.load(f)
        
        # Get critical markers (P0)
        critical_markers = [
            m for m in analysis.get("markers", [])
            if m.get("priority") == "P0 - Critical"
        ]
        
        # Group by file path for agent assignment
        file_markers = {}
        for marker in critical_markers[:50]:  # Top 50 critical
            file_path = marker.get("relative_path", "")
            if file_path not in file_markers:
                file_markers[file_path] = []
            file_markers[file_path].append(marker)
        
        # Assign based on file location patterns
        assignments = []
        
        # Agent-1: src/services, src/core
        agent1_files = [f for f in file_markers.keys() if "src/services" in f or "src/core" in f]
        if agent1_files:
            task = self.coordinator.assign_task_to_agent(
                agent_id="Agent-1",
                task=f"Resolve {len(agent1_files)} files with P0 Critical markers",
                priority="HIGH",
                description=f"Files: {', '.join(agent1_files[:5])}{'...' if len(agent1_files) > 5 else ''}",
            )
            assignments.append(task)
        
        # Agent-3: tests, infrastructure
        agent3_files = [f for f in file_markers.keys() if "test" in f.lower() or "infrastructure" in f.lower()]
        if agent3_files:
            task = self.coordinator.assign_task_to_agent(
                agent_id="Agent-3",
                task=f"Resolve {len(agent3_files)} files with P0 Critical markers",
                priority="HIGH",
                description=f"Files: {', '.join(agent3_files[:5])}{'...' if len(agent3_files) > 5 else ''}",
            )
            assignments.append(task)
        
        return assignments

    def save_assignments_log(self, log_file: Path):
        """Save assignments log."""
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_data = {
            "assignments": self.assignments_log,
            "total_assignments": len(self.assignments_log),
            "timestamp": datetime.now().isoformat(),
        }
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
        
        print(f"✅ Assignments log saved: {log_file}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Captain Task Assigner")
    parser.add_argument("--assign-critical", action="store_true", help="Assign critical tasks")
    parser.add_argument("--assign-markers", type=Path, help="Assign technical debt markers from analysis file")
    parser.add_argument("--log", type=Path, default=Path("agent_workspaces/Agent-5/assignments_log.json"), help="Assignments log file")
    
    args = parser.parse_args()
    
    assigner = CaptainTaskAssigner()
    
    if args.assign_critical:
        print("🚨 Assigning critical tasks...")
        assignments = assigner.assign_critical_tasks()
        print(f"✅ Assigned {len(assignments)} critical tasks")
        
        for assignment in assignments:
            print(f"  - {assignment['agent']}: {assignment['task']}")
        
        assigner.save_assignments_log(args.log)
    
    if args.assign_markers:
        print(f"🎯 Assigning technical debt markers from {args.assign_markers}...")
        assignments = assigner.assign_technical_debt_markers(args.assign_markers)
        print(f"✅ Assigned {len(assignments)} marker resolution tasks")
        
        assigner.save_assignments_log(args.log)


if __name__ == "__main__":
    main()




