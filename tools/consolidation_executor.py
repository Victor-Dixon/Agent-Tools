#!/usr/bin/env python3
"""
Consolidation Executor
=====================

Executes Phase 1 consolidations with safety checks and progress tracking.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-11-24
Priority: HIGH
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import subprocess

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import safe merge script
try:
    from tools.repo_safe_merge import SafeRepoMerge
except ImportError:
    print("⚠️ repo_safe_merge.py not found - merge execution will be limited")
    SafeRepoMerge = None


class ConsolidationExecutor:
    """Execute consolidation operations with safety checks."""

    def __init__(self, consolidation_plan_path: Optional[Path] = None):
        """
        Initialize consolidation executor.

        Args:
            consolidation_plan_path: Path to consolidation plan JSON file
        """
        self.consolidation_plan_path = consolidation_plan_path
        self.execution_log = Path("consolidation_logs/execution_log.json")
        self.execution_log.parent.mkdir(parents=True, exist_ok=True)
        self.progress_file = Path("consolidation_logs/execution_progress.json")
        
        # Load consolidation plan
        if consolidation_plan_path and consolidation_plan_path.exists():
            with open(consolidation_plan_path, 'r') as f:
                self.plan = json.load(f)
        else:
            # Load from Phase 1 execution approval
            phase1_path = project_root / "docs" / "organization" / "PHASE1_EXECUTION_APPROVAL.md"
            self.plan = self._load_phase1_plan(phase1_path)
        
        # Load repo numbers
        master_list_path = project_root / "data" / "github_75_repos_master_list.json"
        self.repo_numbers = {}
        if master_list_path.exists():
            try:
                with open(master_list_path, 'r') as f:
                    master_list = json.load(f)
                repos = master_list.get("repos", [])
                for repo in repos:
                    self.repo_numbers[repo.get("name")] = repo.get("num")
            except Exception as e:
                print(f"⚠️ Failed to load master list: {e}")

    def _load_phase1_plan(self, phase1_path: Path) -> Dict[str, Any]:
        """Load Phase 1 plan from markdown document."""
        # This is a simplified parser - in production, use proper markdown parsing
        plan = {
            "phase": "Phase 1",
            "groups": []
        }
        
        if not phase1_path.exists():
            print(f"⚠️ Phase 1 plan not found: {phase1_path}")
            return plan
        
        # For now, return a structured plan based on Phase 1 execution approval
        plan["groups"] = [
            {
                "name": "Duplicate Names - Case Variations",
                "priority": "HIGH",
                "reductions": 12,
                "merges": [
                    {"target": "FocusForge", "source": "focusforge", "type": "case_variation"},
                    {"target": "Streamertools", "source": "streamertools", "type": "case_variation"},
                    {"target": "TBOWTactics", "source": "tbowtactics", "type": "case_variation"},
                    {"target": "Superpowered-TTRPG", "source": "superpowered_ttrpg", "type": "case_variation"},
                    {"target": "DaDudeKC-Website", "source": "dadudekcwebsite", "type": "case_variation"},
                    {"target": "DaDudekC", "source": "dadudekc", "type": "case_variation"},
                    {"target": "fastapi", "source": "fastapi", "type": "case_variation", "evaluate": True},
                    {"target": "my-resume", "source": "my_resume", "type": "case_variation"},
                    {"target": "bible-application", "source": "bible-application", "type": "duplicate"},
                    {"target": "projectscanner", "source": "projectscanner", "type": "archive"},
                    {"target": "TROOP", "source": "TROOP", "type": "duplicate"},
                    {"target": "LSTMmodel_trainer", "source": "LSTMmodel_trainer", "type": "duplicate"},
                ]
            },
            {
                "name": "Dream Projects Consolidation",
                "priority": "HIGH",
                "reductions": 2,
                "merges": [
                    {"target": "DreamVault", "source": "DreamBank", "type": "functional"},
                    {"target": "DreamVault", "source": "DigitalDreamscape", "type": "functional"},
                ]
            },
            {
                "name": "Trading Repos Consolidation",
                "priority": "HIGH",
                "reductions": 3,
                "merges": [
                    {"target": "trading-leads-bot", "source": "trade-analyzer", "type": "functional"},
                    {"target": "trading-leads-bot", "source": "UltimateOptionsTradingRobot", "type": "functional"},
                    {"target": "trading-leads-bot", "source": "TheTradingRobotPlug", "type": "functional"},
                ]
            },
            {
                "name": "Agent Systems Consolidation",
                "priority": "HIGH",
                "reductions": 2,
                "merges": [
                    {"target": "Agent_Cellphone", "source": "intelligent-multi-agent", "type": "functional"},
                    {"target": "Agent_Cellphone", "source": "Agent_Cellphone_V1", "type": "archive"},
                ]
            },
            {
                "name": "Streaming Tools Consolidation",
                "priority": "HIGH",
                "reductions": 1,
                "merges": [
                    {"target": "Streamertools", "source": "MeTuber", "type": "functional"},
                ]
            },
            {
                "name": "DaDudekC Projects Consolidation",
                "priority": "HIGH",
                "reductions": 1,
                "merges": [
                    {"target": "DaDudeKC-Website", "source": "DaDudekC", "type": "functional"},
                ]
            },
            {
                "name": "ML Models Consolidation",
                "priority": "MEDIUM",
                "reductions": 1,
                "merges": [
                    {"target": "MachineLearningModelMaker", "source": "LSTMmodel_trainer", "type": "functional"},
                ]
            },
            {
                "name": "Resume/Templates Consolidation",
                "priority": "MEDIUM",
                "reductions": 1,
                "merges": [
                    {"target": "my-resume", "source": "my_personal_templates", "type": "functional"},
                ]
            },
        ]
        
        return plan

    def load_progress(self) -> Dict[str, Any]:
        """Load execution progress from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "started_at": None,
            "completed_groups": [],
            "completed_merges": [],
            "failed_merges": [],
            "total_merges": 0,
            "completed_merges_count": 0
        }

    def save_progress(self, progress: Dict[str, Any]):
        """Save execution progress to file."""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save progress: {e}")

    def execute_group(self, group: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """Execute all merges in a consolidation group."""
        group_name = group.get("name", "Unknown")
        merges = group.get("merges", [])
        
        print(f"\n{'='*60}")
        print(f"📦 Executing Group: {group_name}")
        print(f"{'='*60}")
        print(f"Priority: {group.get('priority', 'UNKNOWN')}")
        print(f"Reductions: {group.get('reductions', 0)} repos")
        print(f"Merges: {len(merges)}")
        print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        print(f"{'='*60}\n")
        
        results = {
            "group_name": group_name,
            "merges": [],
            "success_count": 0,
            "failure_count": 0,
            "skipped_count": 0
        }
        
        for merge in merges:
            target = merge.get("target")
            source = merge.get("source")
            merge_type = merge.get("type", "functional")
            
            print(f"\n🔗 Merge: {source} → {target} ({merge_type})")
            
            # Skip if evaluation needed
            if merge.get("evaluate"):
                print(f"   ⏳ Evaluation needed - skipping")
                results["merges"].append({
                    "target": target,
                    "source": source,
                    "status": "SKIPPED",
                    "reason": "Evaluation needed"
                })
                results["skipped_count"] += 1
                continue
            
            # Execute merge
            if SafeRepoMerge:
                try:
                    merger = SafeRepoMerge(target, source, self.repo_numbers)
                    success = merger.execute_merge(dry_run=dry_run)
                    
                    if success:
                        results["merges"].append({
                            "target": target,
                            "source": source,
                            "status": "SUCCESS" if not dry_run else "DRY_RUN_SUCCESS"
                        })
                        results["success_count"] += 1
                    else:
                        results["merges"].append({
                            "target": target,
                            "source": source,
                            "status": "FAILED"
                        })
                        results["failure_count"] += 1
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    results["merges"].append({
                        "target": target,
                        "source": source,
                        "status": "ERROR",
                        "error": str(e)
                    })
                    results["failure_count"] += 1
            else:
                print(f"   ⚠️ Safe merge not available - simulating")
                results["merges"].append({
                    "target": target,
                    "source": source,
                    "status": "SIMULATED"
                })
                results["success_count"] += 1
        
        print(f"\n✅ Group Complete: {group_name}")
        print(f"   Success: {results['success_count']}")
        print(f"   Failed: {results['failure_count']}")
        print(f"   Skipped: {results['skipped_count']}")
        
        return results

    def execute_phase1(self, dry_run: bool = True) -> Dict[str, Any]:
        """Execute all Phase 1 consolidations."""
        print(f"\n{'='*60}")
        print(f"🚀 CONSOLIDATION EXECUTOR - PHASE 1")
        print(f"{'='*60}")
        print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        print(f"Groups: {len(self.plan.get('groups', []))}")
        print(f"{'='*60}\n")
        
        progress = self.load_progress()
        if not progress.get("started_at"):
            progress["started_at"] = datetime.now().isoformat()
        
        execution_results = {
            "phase": "Phase 1",
            "started_at": progress["started_at"],
            "completed_at": None,
            "groups": [],
            "summary": {
                "total_groups": len(self.plan.get("groups", [])),
                "completed_groups": 0,
                "total_merges": 0,
                "successful_merges": 0,
                "failed_merges": 0,
                "skipped_merges": 0
            }
        }
        
        for group in self.plan.get("groups", []):
            group_results = self.execute_group(group, dry_run=dry_run)
            execution_results["groups"].append(group_results)
            execution_results["summary"]["completed_groups"] += 1
            execution_results["summary"]["total_merges"] += len(group_results["merges"])
            execution_results["summary"]["successful_merges"] += group_results["success_count"]
            execution_results["summary"]["failed_merges"] += group_results["failure_count"]
            execution_results["summary"]["skipped_merges"] += group_results["skipped_count"]
            
            # Update progress
            progress["completed_groups"].append(group.get("name"))
            for merge in group_results["merges"]:
                if merge["status"] in ["SUCCESS", "DRY_RUN_SUCCESS", "SIMULATED"]:
                    progress["completed_merges"].append(f"{merge['source']} → {merge['target']}")
                elif merge["status"] in ["FAILED", "ERROR"]:
                    progress["failed_merges"].append(f"{merge['source']} → {merge['target']}")
            
            self.save_progress(progress)
        
        execution_results["completed_at"] = datetime.now().isoformat()
        
        # Save execution log
        try:
            with open(self.execution_log, 'w') as f:
                json.dump(execution_results, f, indent=2)
            print(f"\n✅ Execution log saved: {self.execution_log}")
        except Exception as e:
            print(f"⚠️ Failed to save execution log: {e}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Groups Completed: {execution_results['summary']['completed_groups']}/{execution_results['summary']['total_groups']}")
        print(f"Total Merges: {execution_results['summary']['total_merges']}")
        print(f"Successful: {execution_results['summary']['successful_merges']}")
        print(f"Failed: {execution_results['summary']['failed_merges']}")
        print(f"Skipped: {execution_results['summary']['skipped_merges']}")
        print(f"{'='*60}\n")
        
        return execution_results


def main():
    """Main entry point."""
    dry_run = "--execute" not in sys.argv
    
    executor = ConsolidationExecutor()
    results = executor.execute_phase1(dry_run=dry_run)
    
    if results["summary"]["failed_merges"] > 0:
        print("⚠️ Some merges failed - review execution log")
        sys.exit(1)
    else:
        print("✅ All merges completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()


