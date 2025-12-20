"""
Work Attribution Tool - Properly attribute work to agents based on git history

PURPOSE: Ensure agents get credit for actual work they did
PREVENTS: False credit, misattribution, point inflation
"""

import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class WorkItem:
    """A piece of work done by an agent"""
    agent: str
    file_path: str
    commit_hash: str
    timestamp: datetime
    lines_added: int
    lines_deleted: int
    commit_message: str
    files_in_commit: List[str]


class WorkAttributionTool:
    """Attribution tool to properly credit agents for their work"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.agent_patterns = [
            "Agent-1", "Agent-2", "Agent-3", "Agent-4",
            "Agent-5", "Agent-6", "Agent-7", "Agent-8"
        ]
    
    def get_agent_work(
        self,
        agent: str,
        hours: int = 24,
        file_pattern: Optional[str] = None
    ) -> List[WorkItem]:
        """
        Get all work done by a specific agent
        
        Args:
            agent: Agent ID
            hours: Time window to check
            file_pattern: Optional file pattern filter
        
        Returns:
            List of WorkItems for the agent
        """
        since = datetime.now() - timedelta(hours=hours)
        since_str = since.strftime("%Y-%m-%d %H:%M:%S")
        
        cmd = [
            "git", "log",
            f"--since={since_str}",
            "--author=Agent",  # Filter to agent commits
            "--pretty=format:%H|%an|%ai|%s",
            "--numstat"
        ]
        
        if file_pattern:
            cmd.extend(["--", file_pattern])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            all_work = self._parse_git_log(result.stdout)
            
            # Filter to specific agent
            return [w for w in all_work if agent.lower() in w.agent.lower()]
        
        except subprocess.CalledProcessError:
            return []
    
    def get_all_agents_work(
        self,
        hours: int = 24
    ) -> Dict[str, List[WorkItem]]:
        """Get work done by all agents in time window"""
        work_by_agent = defaultdict(list)
        
        for agent in self.agent_patterns:
            work = self.get_agent_work(agent, hours)
            if work:
                work_by_agent[agent].extend(work)
        
        return dict(work_by_agent)
    
    def verify_agent_did_work(
        self,
        agent: str,
        file_path: str,
        hours: int = 24
    ) -> bool:
        """Check if agent actually worked on a file"""
        work = self.get_agent_work(agent, hours, file_path)
        return len(work) > 0
    
    def who_worked_on_file(
        self,
        file_path: str,
        hours: int = 24
    ) -> List[str]:
        """Find which agents worked on a specific file"""
        all_work = self.get_all_agents_work(hours)
        agents = set()
        
        for agent, work_items in all_work.items():
            for item in work_items:
                if file_path in item.files_in_commit:
                    agents.add(agent)
        
        return sorted(list(agents))
    
    def generate_attribution_report(
        self,
        hours: int = 24
    ) -> str:
        """Generate comprehensive attribution report"""
        all_work = self.get_all_agents_work(hours)
        
        report = []
        report.append("=" * 80)
        report.append(f"WORK ATTRIBUTION REPORT (Last {hours}h)")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total_commits = sum(len(work) for work in all_work.values())
        report.append(f"Total Commits: {total_commits}")
        report.append(f"Active Agents: {len(all_work)}")
        report.append("")
        
        # By agent
        for agent in sorted(all_work.keys()):
            work_items = all_work[agent]
            total_lines = sum(w.lines_added + w.lines_deleted for w in work_items)
            files_touched = set()
            for w in work_items:
                files_touched.update(w.files_in_commit)
            
            report.append(f"🤖 {agent}")
            report.append(f"   Commits: {len(work_items)}")
            report.append(f"   Lines Changed: {total_lines}")
            report.append(f"   Files Touched: {len(files_touched)}")
            report.append("")
            
            # Recent commits
            for item in work_items[:3]:  # Show last 3
                report.append(f"   ✅ {item.commit_hash[:8]}: {item.commit_message[:60]}")
                report.append(f"      {item.timestamp.strftime('%Y-%m-%d %H:%M')}")
                report.append(f"      +{item.lines_added} -{item.lines_deleted}")
            
            if len(work_items) > 3:
                report.append(f"   ... and {len(work_items) - 3} more commits")
            report.append("")
        
        return "\n".join(report)
    
    def _parse_git_log(self, log_output: str) -> List[WorkItem]:
        """Parse git log into WorkItems"""
        work_items = []
        lines = log_output.strip().split("\n")
        
        i = 0
        current_commit = None
        current_files = []
        
        while i < len(lines):
            line = lines[i]
            
            if "|" in line:
                # Commit line
                parts = line.split("|")
                if len(parts) >= 4:
                    commit_hash = parts[0]
                    author = parts[1]
                    timestamp_str = parts[2].replace(" ", "T", 1).rsplit(" ", 1)[0]
                    timestamp = datetime.fromisoformat(timestamp_str)
                    message = parts[3]
                    
                    current_commit = {
                        "commit_hash": commit_hash,
                        "author": author,
                        "timestamp": timestamp,
                        "message": message
                    }
                    current_files = []
            
            elif "\t" in line and current_commit:
                # Stat line
                parts = line.split("\t")
                if len(parts) >= 3:
                    try:
                        added = int(parts[0]) if parts[0] != "-" else 0
                        deleted = int(parts[1]) if parts[1] != "-" else 0
                        file_path = parts[2]
                        
                        current_files.append(file_path)
                        
                        work_items.append(WorkItem(
                            agent=current_commit["author"],
                            file_path=file_path,
                            commit_hash=current_commit["commit_hash"],
                            timestamp=current_commit["timestamp"],
                            lines_added=added,
                            lines_deleted=deleted,
                            commit_message=current_commit["message"],
                            files_in_commit=current_files.copy()
                        ))
                    except ValueError:
                        pass
            
            i += 1
        
        return work_items


def main():
    """CLI for work attribution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Attribute work to agents based on git history"
    )
    parser.add_argument(
        "--agent",
        help="Specific agent to check"
    )
    parser.add_argument(
        "--file",
        help="Specific file to check"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Time window in hours (default: 24)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all agents' work"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format"
    )
    
    args = parser.parse_args()
    
    tool = WorkAttributionTool()
    
    if args.file:
        # Who worked on this file?
        agents = tool.who_worked_on_file(args.file, args.hours)
        print(f"\n{'='*80}")
        print(f"Agents who worked on {args.file}:")
        print(f"{'='*80}")
        if agents:
            for agent in agents:
                work = tool.get_agent_work(agent, args.hours, args.file)
                print(f"\n🤖 {agent}: {len(work)} commit(s)")
                for item in work:
                    print(f"   {item.commit_hash[:8]}: {item.commit_message}")
        else:
            print("No agent work found for this file.")
        print("")
    
    elif args.agent:
        # Specific agent's work
        work = tool.get_agent_work(args.agent, args.hours)
        
        if args.json:
            print(json.dumps([asdict(w) for w in work], default=str, indent=2))
        else:
            print(f"\n{'='*80}")
            print(f"Work by {args.agent} (Last {args.hours}h)")
            print(f"{'='*80}")
            if work:
                for item in work:
                    print(f"\n✅ {item.commit_hash[:8]}")
                    print(f"   File: {item.file_path}")
                    print(f"   Time: {item.timestamp}")
                    print(f"   Changes: +{item.lines_added} -{item.lines_deleted}")
                    print(f"   Message: {item.commit_message}")
            else:
                print(f"No work found for {args.agent} in last {args.hours}h")
            print("")
    
    elif args.all:
        # All agents report
        print(tool.generate_attribution_report(args.hours))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


