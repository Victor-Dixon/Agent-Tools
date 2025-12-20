#!/usr/bin/env python3
"""
🐝 AGENT COORDINATION TOOL - Implementation Task Assigner
==========================================================

Assigns implementation tasks to agents based on file categories and agent specializations.

Usage:
    python tools/coordinate_implementation_tasks.py --action assign
    python tools/coordinate_implementation_tasks.py --action list
    python tools/coordinate_implementation_tasks.py --action status

Author: Agent-5 (Business Intelligence Specialist)
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ImplementationTaskCoordinator:
    """Coordinates implementation task assignments to agents."""

    # Agent specializations mapping
    AGENT_SPECIALIZATIONS = {
        "Agent-1": {
            "name": "Integration & Core Systems",
            "categories": ["core", "integration", "execution", "orchestration"],
            "keywords": ["integration", "core", "execution", "orchestration", "service"]
        },
        "Agent-2": {
            "name": "Architecture & Design",
            "categories": ["architecture", "design", "managers", "patterns"],
            "keywords": ["architecture", "design", "manager", "pattern", "coordination"]
        },
        "Agent-3": {
            "name": "Infrastructure & DevOps",
            "categories": ["infrastructure", "devops", "deployment", "config"],
            "keywords": ["infrastructure", "deployment", "config", "setup", "devops"]
        },
        "Agent-7": {
            "name": "Web Development",
            "categories": ["web", "frontend", "api", "controller", "view"],
            "keywords": ["web", "frontend", "api", "controller", "view", "discord"]
        },
        "Agent-8": {
            "name": "SSOT & System Integration",
            "categories": ["ssot", "system", "integration", "unified", "consolidation"],
            "keywords": ["ssot", "unified", "system", "consolidation", "integration"]
        }
    }

    def __init__(self, results_file: str = "agent_workspaces/Agent-5/functionality_existence_check.json"):
        """Initialize coordinator with results file."""
        self.results_file = Path(results_file)
        self.results = self._load_results()
        self.project_root = Path(__file__).parent.parent

    def _load_results(self) -> Dict:
        """Load functionality existence check results."""
        if not self.results_file.exists():
            logger.error(f"❌ Results file not found: {self.results_file}")
            return {"summary": {}, "files": []}
        
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error loading results: {e}")
            return {"summary": {}, "files": []}

    def _determine_agent_for_file(self, file_path: str) -> str:
        """Determine best agent for a file based on path and content."""
        file_path_lower = file_path.lower()
        
        # Score each agent based on path/keywords
        agent_scores = {}
        
        for agent_id, spec in self.AGENT_SPECIALIZATIONS.items():
            score = 0
            
            # Check path matches categories
            for category in spec["categories"]:
                if category in file_path_lower:
                    score += 2
            
            # Check path matches keywords
            for keyword in spec["keywords"]:
                if keyword in file_path_lower:
                    score += 1
            
            agent_scores[agent_id] = score
        
        # Find agent with highest score
        if agent_scores:
            best_agent = max(agent_scores, key=agent_scores.get)
            if agent_scores[best_agent] > 0:
                return best_agent
        
        # Default to Agent-1 for unmatched files
        return "Agent-1"

    def get_files_to_implement(self) -> List[Dict]:
        """Get list of files that need implementation (no existing functionality)."""
        files_to_implement = []
        
        for file_data in self.results.get("files", []):
            recommendation = file_data.get("recommendation", "")
            
            # Files that should be implemented
            if recommendation == "IMPLEMENT_OR_INTEGRATE":
                files_to_implement.append({
                    "file_path": file_data.get("file_path", ""),
                    "relative_path": file_data.get("relative_path", ""),
                    "agent": self._determine_agent_for_file(file_data.get("file_path", ""))
                })
        
        return files_to_implement

    def get_files_to_review(self) -> List[Dict]:
        """Get list of files that need review (duplicates/possible duplicates)."""
        files_to_review = []
        
        for file_data in self.results.get("files", []):
            recommendation = file_data.get("recommendation", "")
            functionality_exists = file_data.get("functionality_exists", False)
            
            # Files that need review
            if "POSSIBLE_DUPLICATE" in recommendation or functionality_exists:
                similar_files = file_data.get("similar_files", [])
                files_to_review.append({
                    "file_path": file_data.get("file_path", ""),
                    "relative_path": file_data.get("relative_path", ""),
                    "similar_files": similar_files,
                    "functionality_exists": functionality_exists,
                    "agent": "Agent-2"  # Architecture agent reviews duplicates
                })
        
        return files_to_review

    def assign_implementation_tasks(self, dry_run: bool = False) -> Dict[str, List[str]]:
        """Assign implementation tasks to agents."""
        files_to_implement = self.get_files_to_implement()
        
        # Group files by agent
        agent_assignments = {}
        
        for file_info in files_to_implement:
            agent_id = file_info["agent"]
            if agent_id not in agent_assignments:
                agent_assignments[agent_id] = []
            
            agent_assignments[agent_id].append(file_info)
        
        # Assign tasks to agents
        assigned_tasks = {}
        
        for agent_id, files in agent_assignments.items():
            agent_name = self.AGENT_SPECIALIZATIONS[agent_id]["name"]
            file_list = "\n".join([f"- {f['relative_path']}" for f in files[:10]])  # Limit to 10 per message
            
            message = f"""🔨 IMPLEMENTATION ASSIGNMENT - {len(files)} Files

**Assignment**: Professional implementation of files where functionality doesn't exist.

**Files to Implement** ({len(files)} total):
{file_list}
{"... and more (see full list)" if len(files) > 10 else ""}

**Requirements**:
1. ✅ Verified functionality doesn't exist elsewhere
2. ✅ Follow V2 compliance standards
3. ✅ Use existing architecture patterns
4. ✅ Integrate properly into system
5. ✅ Add comprehensive tests
6. ✅ Document usage

**Reference**: agent_workspaces/Agent-5/PROFESSIONAL_IMPLEMENTATION_WORKFLOW.md

**Action**: Implement professionally following standards.

📝 DISCORD DEVLOG REMINDER: Create a Discord devlog after completing each file.
"""
            
            assigned_tasks[agent_id] = {
                "files": files,
                "message": message
            }
            
            if not dry_run:
                # Send message to agent
                cmd = [
                    sys.executable, "-m", "src.services.messaging_cli",
                    "--agent", agent_id,
                    "--message", message,
                    "--priority", "normal"
                ]
                
                logger.info(f"📨 Assigning {len(files)} files to {agent_id}...")
                try:
                    result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info(f"✅ Successfully assigned tasks to {agent_id}")
                    else:
                        logger.error(f"❌ Failed to assign tasks to {agent_id}: {result.stderr}")
                except Exception as e:
                    logger.error(f"❌ Error assigning tasks to {agent_id}: {e}")
        
        return assigned_tasks

    def assign_review_tasks(self, dry_run: bool = False) -> Dict[str, List[str]]:
        """Assign review tasks for duplicates to Agent-2."""
        files_to_review = self.get_files_to_review()
        
        if not files_to_review:
            logger.info("ℹ️ No files need review")
            return {}
        
        # Group by agent (mostly Agent-2 for architecture review)
        agent_assignments = {}
        
        for file_info in files_to_review:
            agent_id = file_info["agent"]
            if agent_id not in agent_assignments:
                agent_assignments[agent_id] = []
            
            agent_assignments[agent_id].append(file_info)
        
        assigned_tasks = {}
        
        for agent_id, files in agent_assignments.items():
            agent_name = self.AGENT_SPECIALIZATIONS[agent_id]["name"]
            file_list = "\n".join([f"- {f['relative_path']} (similar: {len(f.get('similar_files', []))} files)" for f in files[:10]])
            
            message = f"""🔍 DUPLICATE REVIEW ASSIGNMENT - {len(files)} Files

**Assignment**: Review files for duplicate functionality.

**Files to Review** ({len(files)} total):
{file_list}
{"... and more (see full list)" if len(files) > 10 else ""}

**Requirements**:
1. ✅ Compare with similar files
2. ✅ Determine if duplicate or unique
3. ✅ Use better version if duplicate
4. ✅ Delete obsolete duplicates
5. ✅ Merge if partial duplicates

**Reference**: agent_workspaces/Agent-5/functionality_existence_check.json

**Action**: Review each file and determine action (use existing, merge, or delete).

📝 DISCORD DEVLOG REMINDER: Create a Discord devlog after completing review.
"""
            
            assigned_tasks[agent_id] = {
                "files": files,
                "message": message
            }
            
            if not dry_run:
                cmd = [
                    sys.executable, "-m", "src.services.messaging_cli",
                    "--agent", agent_id,
                    "--message", message,
                    "--priority", "normal"
                ]
                
                logger.info(f"📨 Assigning {len(files)} review tasks to {agent_id}...")
                try:
                    result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info(f"✅ Successfully assigned review tasks to {agent_id}")
                    else:
                        logger.error(f"❌ Failed to assign review tasks to {agent_id}: {result.stderr}")
                except Exception as e:
                    logger.error(f"❌ Error assigning review tasks to {agent_id}: {e}")
        
        return assigned_tasks

    def list_tasks(self):
        """List all tasks that need assignment."""
        files_to_implement = self.get_files_to_implement()
        files_to_review = self.get_files_to_review()
        
        print("\n" + "=" * 70)
        print("📋 IMPLEMENTATION TASK SUMMARY")
        print("=" * 70)
        
        print(f"\n✅ Files to Implement: {len(files_to_implement)}")
        print(f"🔍 Files to Review: {len(files_to_review)}")
        
        # Group by agent
        implementation_by_agent = {}
        for file_info in files_to_implement:
            agent_id = file_info["agent"]
            if agent_id not in implementation_by_agent:
                implementation_by_agent[agent_id] = []
            implementation_by_agent[agent_id].append(file_info)
        
        print(f"\n📊 Implementation Tasks by Agent:")
        for agent_id, files in sorted(implementation_by_agent.items()):
            agent_name = self.AGENT_SPECIALIZATIONS[agent_id]["name"]
            print(f"  {agent_id} ({agent_name}): {len(files)} files")
        
        print(f"\n🔍 Review Tasks:")
        print(f"  Agent-2 (Architecture & Design): {len(files_to_review)} files")
        
        print("\n" + "=" * 70 + "\n")

    def print_status(self):
        """Print current status of tasks."""
        self.list_tasks()
        
        summary = self.results.get("summary", {})
        print("📊 SUMMARY:")
        print(f"  Total checked: {summary.get('total_checked', 0)}")
        print(f"  Functionality exists: {summary.get('functionality_exists', 0)}")
        print(f"  Possible duplicates: {summary.get('possible_duplicates', 0)}")
        print(f"  No existing functionality: {summary.get('no_existing_functionality', 0)}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Coordinate implementation task assignments to agents"
    )
    
    parser.add_argument(
        "--action",
        choices=["assign", "assign-review", "list", "status"],
        default="list",
        help="Action to perform"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview assignments without sending messages"
    )
    
    args = parser.parse_args()
    
    coordinator = ImplementationTaskCoordinator()
    
    if args.action == "list":
        coordinator.list_tasks()
    elif args.action == "status":
        coordinator.print_status()
    elif args.action == "assign":
        logger.info("🚀 Assigning implementation tasks to agents...")
        if args.dry_run:
            logger.info("🔍 DRY RUN MODE - No messages will be sent")
        assigned = coordinator.assign_implementation_tasks(dry_run=args.dry_run)
        logger.info(f"✅ Assigned tasks to {len(assigned)} agents")
    elif args.action == "assign-review":
        logger.info("🚀 Assigning review tasks to agents...")
        if args.dry_run:
            logger.info("🔍 DRY RUN MODE - No messages will be sent")
        assigned = coordinator.assign_review_tasks(dry_run=args.dry_run)
        logger.info(f"✅ Assigned review tasks to {len(assigned)} agents")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥\n")


if __name__ == "__main__":
    main()




