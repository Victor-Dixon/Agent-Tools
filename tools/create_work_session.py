#!/usr/bin/env python3
"""
Work Session File Creation Helper CLI
======================================

Creates work_session.json files for Output Flywheel v1.1.
Simplifies session file creation with interactive prompts and validation.

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <300 lines
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def generate_session_id() -> str:
    """Generate a UUID session ID."""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current ISO 8601 timestamp."""
    return datetime.now().isoformat()


def create_session_file(
    session_type: str,
    agent_id: str,
    output_path: Optional[Path] = None,
    repo_path: Optional[Path] = None,
    duration_minutes: Optional[int] = None,
    files_changed: Optional[int] = None,
    commits: Optional[int] = None,
    auto_extract_git: bool = False
) -> Path:
    """
    Create a work_session.json file.
    
    Args:
        session_type: Type of session (build, trade, life_aria)
        agent_id: Agent identifier (e.g., 'Agent-7')
        output_path: Where to save the file (default: systems/output_flywheel/data/)
        repo_path: Path to repository (for build sessions)
        duration_minutes: Session duration
        files_changed: Number of files changed
        commits: Number of commits
        auto_extract_git: Automatically extract git commits
        
    Returns:
        Path to created file
    """
    # Validate session type
    valid_types = ["build", "trade", "life_aria"]
    if session_type not in valid_types:
        raise ValueError(f"Invalid session_type: {session_type}. Must be one of {valid_types}")
    
    # Validate agent_id format
    if not agent_id.startswith("Agent-") or not agent_id.split("-")[1].isdigit():
        raise ValueError(f"Invalid agent_id: {agent_id}. Must be in format 'Agent-N'")
    
    # Default output path
    if output_path is None:
        output_path = project_root / "systems" / "output_flywheel" / "data" / f"work_session_{generate_session_id()}.json"
    else:
        output_path = Path(output_path)
        if output_path.is_dir():
            output_path = output_path / f"work_session_{generate_session_id()}.json"
    
    # Create base session structure
    session_data = {
        "session_id": generate_session_id(),
        "session_type": session_type,
        "timestamp": get_timestamp(),
        "agent_id": agent_id,
        "metadata": {},
        "source_data": {},
        "artifacts": {},
        "pipeline_status": {}
    }
    
    # Add metadata
    if duration_minutes is not None:
        session_data["metadata"]["duration_minutes"] = duration_minutes
    if files_changed is not None:
        session_data["metadata"]["files_changed"] = files_changed
    if commits is not None:
        session_data["metadata"]["commits"] = commits
    
    # Add source data
    if repo_path:
        session_data["source_data"]["repo_path"] = str(repo_path)
    
    # Auto-extract git commits if requested
    if auto_extract_git and repo_path:
        try:
            git_commits = extract_git_commits(repo_path)
            if git_commits:
                session_data["source_data"]["git_commits"] = git_commits
                session_data["metadata"]["commits"] = len(git_commits)
                print(f"✅ Extracted {len(git_commits)} git commits")
        except Exception as e:
            print(f"⚠️  Warning: Could not extract git commits: {e}")
    
    # Set pipeline status based on session type
    if session_type == "build":
        session_data["pipeline_status"]["build_artifact"] = "pending"
        session_data["pipeline_status"]["trade_artifact"] = "not_applicable"
        session_data["pipeline_status"]["life_aria_artifact"] = "not_applicable"
    elif session_type == "trade":
        session_data["pipeline_status"]["build_artifact"] = "not_applicable"
        session_data["pipeline_status"]["trade_artifact"] = "pending"
        session_data["pipeline_status"]["life_aria_artifact"] = "not_applicable"
    elif session_type == "life_aria":
        session_data["pipeline_status"]["build_artifact"] = "not_applicable"
        session_data["pipeline_status"]["trade_artifact"] = "not_applicable"
        session_data["pipeline_status"]["life_aria_artifact"] = "pending"
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created work session file: {output_path}")
    print(f"   Session ID: {session_data['session_id']}")
    print(f"   Type: {session_type}")
    print(f"   Agent: {agent_id}")
    
    return output_path


def extract_git_commits(repo_path: Path, limit: int = 50) -> list:
    """
    Extract git commits from repository.
    
    Args:
        repo_path: Path to git repository
        limit: Maximum number of commits to extract
        
    Returns:
        List of commit dictionaries
    """
    import subprocess
    
    repo_path = Path(repo_path)
    if not (repo_path / ".git").exists():
        raise ValueError(f"Not a git repository: {repo_path}")
    
    # Get recent commits
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "log", f"--max-count={limit}", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
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
            files_result = subprocess.run(
                ["git", "-C", str(repo_path), "show", "--name-only", "--pretty=format:", commit_hash],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_SHORT
            )
            
            files = []
            if files_result.returncode == 0:
                files = [f.strip() for f in files_result.stdout.strip().split('\n') if f.strip()]
            
            commits.append({
                "hash": commit_hash,
                "message": message,
                "author": f"{author_name} <{author_email}>",
                "timestamp": date_str,
                "files": files
            })
        
        return commits
        
    except subprocess.TimeoutExpired:
        raise ValueError("Git command timed out")
    except FileNotFoundError:
        raise ValueError("Git not found - install Git to use auto-extraction")
    except Exception as e:
        raise ValueError(f"Error extracting commits: {e}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create work_session.json file for Output Flywheel"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["build", "trade", "life_aria"],
        help="Session type"
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent ID (e.g., Agent-7)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: systems/output_flywheel/data/work_session_<uuid>.json)"
    )
    parser.add_argument(
        "--repo",
        type=Path,
        help="Repository path (for build sessions)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Session duration in minutes"
    )
    parser.add_argument(
        "--files-changed",
        type=int,
        help="Number of files changed"
    )
    parser.add_argument(
        "--commits",
        type=int,
        help="Number of commits"
    )
    parser.add_argument(
        "--auto-extract-git",
        action="store_true",
        help="Automatically extract git commits from repository"
    )
    
    args = parser.parse_args()
    
    try:
        output_path = create_session_file(
            session_type=args.type,
            agent_id=args.agent,
            output_path=args.output,
            repo_path=args.repo,
            duration_minutes=args.duration,
            files_changed=args.files_changed,
            commits=args.commits,
            auto_extract_git=args.auto_extract_git
        )
        print(f"\n✅ Success! Session file created: {output_path}")
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




