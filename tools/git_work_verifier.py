"""
Git Work Verifier - Validates claimed work against actual git commits

PURPOSE: Prevent false credit claims by verifying work with git evidence
CRITICAL FOR: Entry #025 Integrity pillar
"""

import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class WorkClaim:
    """A claim of work completed"""
    agent: str
    file_path: str
    claimed_changes: str
    claimed_timestamp: datetime


@dataclass
class GitEvidence:
    """Git evidence for work"""
    commit_hash: str
    author: str
    timestamp: datetime
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    commit_message: str


@dataclass
class VerificationResult:
    """Result of verifying a work claim"""
    claim: WorkClaim
    verified: bool
    evidence: Optional[GitEvidence]
    confidence: str  # HIGH, MEDIUM, LOW, NONE
    reasoning: str


class GitWorkVerifier:
    """Verify work claims against git history"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
    
    def verify_claim(
        self,
        agent: str,
        file_path: str,
        claimed_changes: str,
        time_window_hours: int = 24
    ) -> VerificationResult:
        """
        Verify if an agent actually did claimed work
        
        Args:
            agent: Agent ID (e.g., "Agent-6")
            file_path: File that was allegedly modified
            claimed_changes: Description of changes
            time_window_hours: How far back to check (default 24h)
        
        Returns:
            VerificationResult with evidence and confidence level
        """
        claim = WorkClaim(
            agent=agent,
            file_path=file_path,
            claimed_changes=claimed_changes,
            claimed_timestamp=datetime.now()
        )
        
        # Get git history for the file
        evidence = self._get_git_evidence(file_path, time_window_hours)
        
        if not evidence:
            return VerificationResult(
                claim=claim,
                verified=False,
                evidence=None,
                confidence="NONE",
                reasoning=f"No git commits found for {file_path} in last {time_window_hours}h"
            )
        
        # Check if agent name appears in commits
        agent_commits = [e for e in evidence if agent.lower() in e.author.lower()]
        
        if agent_commits:
            latest = agent_commits[0]
            return VerificationResult(
                claim=claim,
                verified=True,
                evidence=latest,
                confidence="HIGH",
                reasoning=f"Git commit {latest.commit_hash[:8]} confirms work by {agent}"
            )
        
        # No matching agent commits
        if evidence:
            actual_author = evidence[0].author
            return VerificationResult(
                claim=claim,
                verified=False,
                evidence=evidence[0],
                confidence="NONE",
                reasoning=f"Git shows {file_path} modified by {actual_author}, not {agent}"
            )
        
        return VerificationResult(
            claim=claim,
            verified=False,
            evidence=None,
            confidence="LOW",
            reasoning="Unable to verify - insufficient git evidence"
        )
    
    def _get_git_evidence(
        self,
        file_path: str,
        hours: int
    ) -> List[GitEvidence]:
        """Get git commit history for a file"""
        try:
            # Get commits in time window
            since = datetime.now() - timedelta(hours=hours)
            since_str = since.strftime("%Y-%m-%d %H:%M:%S")
            
            cmd = [
                "git", "log",
                f"--since={since_str}",
                "--pretty=format:%H|%an|%ai|%s",
                "--numstat",
                "--", file_path
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return self._parse_git_log(result.stdout)
        
        except subprocess.CalledProcessError:
            return []
    
    def _parse_git_log(self, log_output: str) -> List[GitEvidence]:
        """Parse git log output into evidence objects"""
        evidence = []
        lines = log_output.strip().split("\n")
        
        i = 0
        while i < len(lines):
            if "|" in lines[i]:
                parts = lines[i].split("|")
                if len(parts) >= 4:
                    commit_hash = parts[0]
                    author = parts[1]
                    timestamp = datetime.fromisoformat(parts[2].replace(" ", "T", 1).rsplit(" ", 1)[0])
                    message = parts[3]
                    
                    # Next line might be numstat
                    files_changed = []
                    lines_added = 0
                    lines_deleted = 0
                    
                    if i + 1 < len(lines) and "\t" in lines[i + 1]:
                        stat_parts = lines[i + 1].split("\t")
                        if len(stat_parts) >= 3:
                            try:
                                lines_added = int(stat_parts[0]) if stat_parts[0] != "-" else 0
                                lines_deleted = int(stat_parts[1]) if stat_parts[1] != "-" else 0
                                files_changed = [stat_parts[2]]
                            except ValueError:
                                pass
                        i += 1
                    
                    evidence.append(GitEvidence(
                        commit_hash=commit_hash,
                        author=author,
                        timestamp=timestamp,
                        files_changed=files_changed,
                        lines_added=lines_added,
                        lines_deleted=lines_deleted,
                        commit_message=message
                    ))
            i += 1
        
        return evidence
    
    def verify_multiple_claims(
        self,
        claims: List[Dict]
    ) -> List[VerificationResult]:
        """Verify multiple work claims at once"""
        results = []
        for claim in claims:
            result = self.verify_claim(
                agent=claim["agent"],
                file_path=claim["file_path"],
                claimed_changes=claim["claimed_changes"],
                time_window_hours=claim.get("time_window_hours", 24)
            )
            results.append(result)
        return results
    
    def generate_report(
        self,
        results: List[VerificationResult]
    ) -> str:
        """Generate human-readable verification report"""
        report = []
        report.append("=" * 80)
        report.append("GIT WORK VERIFICATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        verified = [r for r in results if r.verified]
        unverified = [r for r in results if not r.verified]
        
        report.append(f"SUMMARY: {len(verified)}/{len(results)} claims verified")
        report.append("")
        
        if verified:
            report.append("✅ VERIFIED CLAIMS:")
            for r in verified:
                report.append(f"  - {r.claim.agent}: {r.claim.file_path}")
                report.append(f"    Evidence: {r.evidence.commit_hash[:8]}")
                report.append(f"    Confidence: {r.confidence}")
                report.append("")
        
        if unverified:
            report.append("❌ UNVERIFIED CLAIMS:")
            for r in unverified:
                report.append(f"  - {r.claim.agent}: {r.claim.file_path}")
                report.append(f"    Reason: {r.reasoning}")
                report.append(f"    Confidence: {r.confidence}")
                report.append("")
        
        return "\n".join(report)


def main():
    """CLI for git work verification"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify work claims against git evidence"
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent ID (e.g., Agent-6)"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="File path to verify"
    )
    parser.add_argument(
        "--changes",
        required=True,
        help="Description of claimed changes"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Time window in hours (default: 24)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format"
    )
    
    args = parser.parse_args()
    
    verifier = GitWorkVerifier()
    result = verifier.verify_claim(
        agent=args.agent,
        file_path=args.file,
        claimed_changes=args.changes,
        time_window_hours=args.hours
    )
    
    if args.json:
        print(json.dumps(asdict(result), default=str, indent=2))
    else:
        print("\n" + "=" * 80)
        print(f"VERIFICATION RESULT: {'✅ VERIFIED' if result.verified else '❌ UNVERIFIED'}")
        print("=" * 80)
        print(f"Agent: {result.claim.agent}")
        print(f"File: {result.claim.file_path}")
        print(f"Claimed: {result.claim.claimed_changes}")
        print(f"Confidence: {result.confidence}")
        print(f"Reasoning: {result.reasoning}")
        if result.evidence:
            print(f"\nGit Evidence:")
            print(f"  Commit: {result.evidence.commit_hash[:8]}")
            print(f"  Author: {result.evidence.author}")
            print(f"  Time: {result.evidence.timestamp}")
            print(f"  Changes: +{result.evidence.lines_added} -{result.evidence.lines_deleted}")
        print("")


if __name__ == "__main__":
    main()


