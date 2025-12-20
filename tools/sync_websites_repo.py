#!/usr/bin/env python3
"""
Websites Repository Sync Tool
==============================

Automatically syncs changes from main project to websites repository.
Can be triggered manually or via GitHub Actions.

Usage:
    # Sync specific files/directories
    python tools/sync_websites_repo.py --files "src/web/*" "docs/websites/*"
    
    # Sync everything configured
    python tools/sync_websites_repo.py --all
    
    # Dry run (preview changes)
    python tools/sync_websites_repo.py --all --dry-run

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class WebsitesRepoSync:
    """Syncs changes from main project to websites repository."""
    
    def __init__(
        self,
        websites_path: Optional[Path] = None,
        dry_run: bool = False
    ):
        """
        Initialize sync tool.
        
        Args:
            websites_path: Path to websites repository (default: D:/websites)
            dry_run: If True, preview changes without applying
        """
        self.project_root = project_root
        self.websites_path = websites_path or Path("D:/websites")
        self.dry_run = dry_run
        
        # Sync configuration: source -> destination mappings
        self.sync_config = {
            # Web components from main project
            "src/web/": "src/web/",
            "src/discord_commander/web/": "src/discord_commander/web/",
            
            # Website-related documentation
            "docs/websites/": "docs/",
            "docs/deployment/": "docs/deployment/",
            
            # Website tools
            "tools/website_*.py": "tools/",
            "tools/deploy_*.py": "tools/",
            
            # Configuration files
            ".env.example": ".env.example",
        }
        
        # Files to exclude
        self.exclude_patterns = [
            "__pycache__",
            "*.pyc",
            ".git",
            "node_modules",
            ".env",
            "*.log"
        ]
    
    def check_git_repo(self, path: Path) -> bool:
        """Check if path is a git repository."""
        git_dir = path / ".git"
        return git_dir.exists() and git_dir.is_dir()
    
    def ensure_websites_repo(self) -> bool:
        """Ensure websites repository exists and is initialized."""
        if not self.websites_path.exists():
            print(f"❌ Websites path does not exist: {self.websites_path}")
            return False
        
        if not self.check_git_repo(self.websites_path):
            print(f"⚠️  Websites path is not a git repository: {self.websites_path}")
            print("   Initializing git repository...")
            if not self.dry_run:
                try:
                    subprocess.run(
                        ["git", "init"],
                        cwd=self.websites_path,
                        check=True,
                        capture_output=True
                    )
                    print("✅ Git repository initialized")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to initialize git: {e}")
                    return False
            else:
                print("   [DRY RUN] Would initialize git repository")
        
        return True
    
    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from sync."""
        path_str = str(file_path)
        return any(pattern in path_str for pattern in self.exclude_patterns)
    
    def sync_file(self, source: Path, dest: Path) -> bool:
        """
        Sync a single file or directory.
        
        Args:
            source: Source path in main project
            dest: Destination path in websites repo
        
        Returns:
            True if sync successful
        """
        if not source.exists():
            print(f"⚠️  Source does not exist: {source}")
            return False
        
        if self.should_exclude(source):
            return False
        
        # Resolve destination path
        dest_full = self.websites_path / dest
        dest_full.parent.mkdir(parents=True, exist_ok=True)
        
        if self.dry_run:
            print(f"   [DRY RUN] Would sync: {source} -> {dest_full}")
            return True
        
        try:
            if source.is_file():
                shutil.copy2(source, dest_full)
                print(f"✅ Synced file: {source.name} -> {dest}")
            elif source.is_dir():
                if dest_full.exists():
                    shutil.rmtree(dest_full)
                shutil.copytree(source, dest_full, ignore=shutil.ignore_patterns(*self.exclude_patterns))
                print(f"✅ Synced directory: {source.name} -> {dest}")
            return True
        except Exception as e:
            print(f"❌ Failed to sync {source}: {e}")
            return False
    
    def sync_all(self) -> Dict[str, int]:
        """
        Sync all configured files/directories.
        
        Returns:
            Dictionary with sync statistics
        """
        if not self.ensure_websites_repo():
            return {"success": 0, "failed": 0, "skipped": 0}
        
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        print(f"\n{'='*60}")
        print(f"🔄 SYNCING TO WEBSITES REPOSITORY")
        print(f"{'='*60}")
        print(f"Source: {self.project_root}")
        print(f"Destination: {self.websites_path}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"{'='*60}\n")
        
        for source_pattern, dest_pattern in self.sync_config.items():
            # Handle glob patterns
            if "*" in source_pattern:
                # Find matching files
                import glob
                matches = glob.glob(str(self.project_root / source_pattern), recursive=True)
                for match in matches:
                    source = Path(match)
                    # Calculate relative destination
                    rel_source = source.relative_to(self.project_root)
                    dest = Path(dest_pattern) / rel_source.name
                    if self.sync_file(source, dest):
                        stats["success"] += 1
                    else:
                        stats["failed"] += 1
            else:
                source = self.project_root / source_pattern
                dest = Path(dest_pattern)
                
                if not source.exists():
                    stats["skipped"] += 1
                    continue
                
                if self.sync_file(source, dest):
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
        
        return stats
    
    def sync_files(self, file_paths: List[str]) -> Dict[str, int]:
        """
        Sync specific files.
        
        Args:
            file_paths: List of file paths relative to project root
        
        Returns:
            Dictionary with sync statistics
        """
        if not self.ensure_websites_repo():
            return {"success": 0, "failed": 0, "skipped": 0}
        
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        print(f"\n{'='*60}")
        print(f"🔄 SYNCING SPECIFIC FILES")
        print(f"{'='*60}\n")
        
        for file_path in file_paths:
            source = self.project_root / file_path
            dest = Path(file_path)  # Keep same structure
            
            if not source.exists():
                print(f"⚠️  File does not exist: {file_path}")
                stats["skipped"] += 1
                continue
            
            if self.sync_file(source, dest):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        return stats
    
    def commit_and_push(self, message: Optional[str] = None) -> bool:
        """
        Commit and push changes to websites repository.
        
        Args:
            message: Commit message (auto-generated if None)
        
        Returns:
            True if successful
        """
        if self.dry_run:
            print("\n[DRY RUN] Would commit and push changes")
            return True
        
        if not self.check_git_repo(self.websites_path):
            print("❌ Not a git repository, cannot commit")
            return False
        
        try:
            # Check if there are changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.websites_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                print("ℹ️  No changes to commit")
                return True
            
            # Add all changes
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.websites_path,
                check=True,
                capture_output=True
            )
            
            # Commit
            if not message:
                message = f"Auto-sync from main project - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.websites_path,
                check=True,
                capture_output=True
            )
            
            print(f"✅ Committed changes: {message}")
            
            # Push
            subprocess.run(
                ["git", "push", "origin", "master"],
                cwd=self.websites_path,
                check=True,
                capture_output=True
            )
            
            print("✅ Pushed to remote repository")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            if e.stdout:
                print(f"   stdout: {e.stdout.decode()}")
            if e.stderr:
                print(f"   stderr: {e.stderr.decode()}")
            return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sync changes from main project to websites repository"
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='Specific files to sync (relative to project root)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Sync all configured files'
    )
    parser.add_argument(
        '--websites-path',
        type=Path,
        help='Path to websites repository (default: D:/websites)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying'
    )
    parser.add_argument(
        '--commit',
        action='store_true',
        help='Commit and push changes after sync'
    )
    parser.add_argument(
        '--message',
        help='Custom commit message'
    )
    
    args = parser.parse_args()
    
    if not args.files and not args.all:
        parser.error("Must specify --files or --all")
    
    sync = WebsitesRepoSync(
        websites_path=args.websites_path,
        dry_run=args.dry_run
    )
    
    if args.all:
        stats = sync.sync_all()
    else:
        stats = sync.sync_files(args.files)
    
    print(f"\n{'='*60}")
    print(f"📊 SYNC STATISTICS")
    print(f"{'='*60}")
    print(f"✅ Success: {stats['success']}")
    print(f"❌ Failed: {stats['failed']}")
    print(f"⏭️  Skipped: {stats['skipped']}")
    print(f"{'='*60}\n")
    
    if args.commit and not args.dry_run:
        sync.commit_and_push(args.message)
    
    sys.exit(0 if stats['failed'] == 0 else 1)


if __name__ == '__main__':
    main()

