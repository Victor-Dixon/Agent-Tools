#!/usr/bin/env python3
"""
Automated Git Commit Extraction Tool
====================================

Extracts git commits from a repository and formats them for Output Flywheel.
Can be used standalone or integrated into session file creation.

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <300 lines
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class GitCommitExtractor:
    """Extracts git commits from a repository."""
    
    def __init__(self, repo_path: Path):
        """Initialize extractor with repository path."""
        self.repo_path = Path(repo_path)
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")
    
    def extract_commits(
        self,
        limit: int = 50,
        since: Optional[str] = None,
        until: Optional[str] = None,
        author: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract commits from repository.
        
        Args:
            limit: Maximum number of commits to extract
            since: Extract commits since this date (ISO format or relative like "1 week ago")
            until: Extract commits until this date
            author: Filter by author name or email
            
        Returns:
            List of commit dictionaries
        """
        # Build git log command
        cmd = ["git", "-C", str(self.repo_path), "log"]
        
        if limit:
            cmd.extend(["--max-count", str(limit)])
        
        if since:
            cmd.extend(["--since", since])
        
        if until:
            cmd.extend(["--until", until])
        
        if author:
            cmd.extend(["--author", author])
        
        # Format: hash|author_name|author_email|date|message
        cmd.extend([
            "--pretty=format:%H|%an|%ae|%ad|%s",
            "--date=iso"
        ])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_DEFAULT,
                check=False
            )
            
            if result.returncode != 0:
                raise ValueError(f"Git command failed: {result.stderr}")
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|', 4)
                if len(parts) < 5:
                    continue
                
                commit_hash, author_name, author_email, date_str, message = parts
                
                # Get files changed
                files = self._get_commit_files(commit_hash)
                
                # Get stats (lines added/removed)
                stats = self._get_commit_stats(commit_hash)
                
                commits.append({
                    "hash": commit_hash,
                    "message": message,
                    "author": f"{author_name} <{author_email}>",
                    "author_name": author_name,
                    "author_email": author_email,
                    "timestamp": date_str,
                    "files": files,
                    "stats": stats
                })
            
            return commits
            
        except subprocess.TimeoutExpired:
            raise ValueError("Git command timed out - repository may be too large")
        except FileNotFoundError:
            raise ValueError("Git not found - install Git to use this tool")
        except Exception as e:
            raise ValueError(f"Error extracting commits: {e}")
    
    def _get_commit_files(self, commit_hash: str) -> List[str]:
        """Get list of files changed in a commit."""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "show", "--name-only", "--pretty=format:", commit_hash],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_SHORT,
                check=False
            )
            
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                return files
            return []
        except:
            return []
    
    def _get_commit_stats(self, commit_hash: str) -> Dict[str, int]:
        """Get commit statistics (lines added/removed)."""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "show", "--stat", "--pretty=format:", commit_hash],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_SHORT,
                check=False
            )
            
            if result.returncode != 0:
                return {"lines_added": 0, "lines_removed": 0}
            
            # Parse stats from output
            lines_added = 0
            lines_removed = 0
            
            for line in result.stdout.split('\n'):
                if '|' in line and ('+' in line or '-' in line):
                    # Format: "file.py | 10 +5 -3"
                    parts = line.split('|')
                    if len(parts) == 2:
                        stats_part = parts[1].strip()
                        if '+' in stats_part:
                            try:
                                added = int(stats_part.split('+')[1].split()[0])
                                lines_added += added
                            except:
                                pass
                        if '-' in stats_part:
                            try:
                                removed = int(stats_part.split('-')[1].split()[0])
                                lines_removed += removed
                            except:
                                pass
            
            return {
                "lines_added": lines_added,
                "lines_removed": lines_removed
            }
        except:
            return {"lines_added": 0, "lines_removed": 0}
    
    def get_summary_stats(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics from commits."""
        if not commits:
            return {
                "total_commits": 0,
                "total_files_changed": 0,
                "total_lines_added": 0,
                "total_lines_removed": 0,
                "unique_authors": 0
            }
        
        total_files = set()
        total_lines_added = 0
        total_lines_removed = 0
        authors = set()
        
        for commit in commits:
            total_files.update(commit.get("files", []))
            stats = commit.get("stats", {})
            total_lines_added += stats.get("lines_added", 0)
            total_lines_removed += stats.get("lines_removed", 0)
            authors.add(commit.get("author", ""))
        
        return {
            "total_commits": len(commits),
            "total_files_changed": len(total_files),
            "total_lines_added": total_lines_added,
            "total_lines_removed": total_lines_removed,
            "unique_authors": len(authors)
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract git commits for Output Flywheel"
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Repository path (default: current directory)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of commits (default: 50)"
    )
    parser.add_argument(
        "--since",
        help="Extract commits since date (ISO format or relative like '1 week ago')"
    )
    parser.add_argument(
        "--until",
        help="Extract commits until date"
    )
    parser.add_argument(
        "--author",
        help="Filter by author name or email"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file (default: print to stdout)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Include summary statistics"
    )
    
    args = parser.parse_args()
    
    try:
        extractor = GitCommitExtractor(args.repo)
        commits = extractor.extract_commits(
            limit=args.limit,
            since=args.since,
            until=args.until,
            author=args.author
        )
        
        output_data = {
            "repo_path": str(args.repo),
            "extracted_at": datetime.now().isoformat(),
            "commits": commits
        }
        
        if args.summary:
            output_data["summary"] = extractor.get_summary_stats(commits)
        
        # Output
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Extracted {len(commits)} commits to {args.output}")
        else:
            print(json.dumps(output_data, indent=2, ensure_ascii=False))
        
        return 0
        
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
from src.core.config.timeout_constants import TimeoutConstants
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())




