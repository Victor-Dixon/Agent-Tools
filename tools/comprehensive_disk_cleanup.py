#!/usr/bin/env python3
"""
Comprehensive Disk Space Cleanup Tool - For GitHub Repo Consolidation
======================================================================

Cleans up all temporary files, old repos, and archives to free disk space
for GitHub repo consolidation operations.

<!-- SSOT Domain: infrastructure -->

USAGE:
    # Dry run (show what would be cleaned)
    python tools/comprehensive_disk_cleanup.py --dry-run
    
    # Cleanup temp_repos (older than 7 days)
    python tools/comprehensive_disk_cleanup.py --cleanup-temp-repos --days 7
    
    # Cleanup restore directory (if safe)
    python tools/comprehensive_disk_cleanup.py --cleanup-restore
    
    # Full cleanup
    python tools/comprehensive_disk_cleanup.py --full

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-01-27
"""

import argparse
import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

PROJECT_ROOT = Path(__file__).parent.parent


class ComprehensiveDiskCleanup:
    """Comprehensive cleanup for disk space"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.cleaned_items = []
        self.total_size_freed = 0
        
    def find_temp_merge_dirs(self) -> List[Path]:
        """Find temporary merge directories"""
        temp_dirs = []
        
        # Check system temp
        import tempfile
        temp_base = Path(tempfile.gettempdir())
        for path in temp_base.glob("repo_merge_*"):
            if path.is_dir():
                temp_dirs.append(path)
        for path in temp_base.glob("github_merge_*"):
            if path.is_dir():
                temp_dirs.append(path)
        
        return temp_dirs
    
    def find_old_temp_repos(self, days: int = 7) -> List[Path]:
        """Find old temp repos"""
        old_repos = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        temp_repos_dir = PROJECT_ROOT / "temp_repos"
        if not temp_repos_dir.exists():
            return old_repos
        
        for repo_dir in temp_repos_dir.iterdir():
            if repo_dir.is_dir():
                try:
                    mtime = datetime.fromtimestamp(repo_dir.stat().st_mtime)
                    if mtime < cutoff_date:
                        old_repos.append(repo_dir)
                except Exception:
                    pass
        
        return old_repos
    
    def get_size(self, path: Path) -> int:
        """Get total size of file or directory"""
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                total = 0
                for item in path.rglob("*"):
                    if item.is_file():
                        total += item.stat().st_size
                return total
        except Exception:
            pass
        return 0
    
    def cleanup_temp_dirs(self) -> Tuple[int, int]:
        """Cleanup temporary merge directories"""
        temp_dirs = self.find_temp_merge_dirs()
        cleaned = 0
        size_freed = 0
        
        for temp_dir in temp_dirs:
            try:
                size = self.get_size(temp_dir)
                if self.dry_run:
                    print(f"🧹 Would remove: {temp_dir} ({size / 1024**2:.2f} MB)")
                else:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    print(f"✅ Removed: {temp_dir} ({size / 1024**2:.2f} MB)")
                    self.cleaned_items.append(str(temp_dir))
                cleaned += 1
                size_freed += size
            except Exception as e:
                print(f"⚠️ Error cleaning {temp_dir}: {e}")
        
        return cleaned, size_freed
    
    def cleanup_temp_repos(self, days: int = 7) -> Tuple[int, int]:
        """Cleanup old temp repos"""
        old_repos = self.find_old_temp_repos(days)
        cleaned = 0
        size_freed = 0
        
        for repo_dir in old_repos:
            try:
                size = self.get_size(repo_dir)
                if self.dry_run:
                    print(f"🧹 Would remove: {repo_dir} ({size / 1024**2:.2f} MB)")
                else:
                    shutil.rmtree(repo_dir, ignore_errors=True)
                    print(f"✅ Removed: {repo_dir} ({size / 1024**2:.2f} MB)")
                    self.cleaned_items.append(str(repo_dir))
                cleaned += 1
                size_freed += size
            except Exception as e:
                print(f"⚠️ Error cleaning {repo_dir}: {e}")
        
        return cleaned, size_freed
    
    def cleanup_restore_directory(self) -> Tuple[int, int]:
        """Cleanup restore directory (if safe)"""
        restore_dir = PROJECT_ROOT / "Agent_Cellphone_V2_Repository_restore"
        if not restore_dir.exists():
            return 0, 0
        
        size = self.get_size(restore_dir)
        if self.dry_run:
            print(f"🧹 Would remove: {restore_dir} ({size / 1024**2:.2f} MB)")
            print("   ⚠️ WARNING: Restore directory - verify it's safe to remove!")
        else:
            shutil.rmtree(restore_dir, ignore_errors=True)
            print(f"✅ Removed: {restore_dir} ({size / 1024**2:.2f} MB)")
            self.cleaned_items.append(str(restore_dir))
        
        return 1 if not self.dry_run else 0, size
    
    def cleanup_full(self) -> Dict[str, any]:
        """Perform full cleanup"""
        print("=" * 60)
        print("🧹 COMPREHENSIVE DISK SPACE CLEANUP")
        print("=" * 60)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTE'}")
        print()
        
        # Cleanup temp directories
        print("📁 Cleaning temporary merge directories...")
        temp_cleaned, temp_size = self.cleanup_temp_dirs()
        
        # Cleanup old temp repos
        print("\n📦 Cleaning old temp repos (older than 7 days)...")
        repos_cleaned, repos_size = self.cleanup_temp_repos(days=7)
        
        # Cleanup restore directory (optional)
        print("\n📦 Cleaning restore directory (if safe)...")
        restore_cleaned, restore_size = self.cleanup_restore_directory()
        
        total_cleaned = temp_cleaned + repos_cleaned + restore_cleaned
        total_size = temp_size + repos_size + restore_size
        
        print("\n" + "=" * 60)
        print("📊 CLEANUP SUMMARY")
        print("=" * 60)
        print(f"Temp directories: {temp_cleaned} ({temp_size / 1024**2:.2f} MB)")
        print(f"Old temp repos: {repos_cleaned} ({repos_size / 1024**2:.2f} MB)")
        print(f"Restore directory: {restore_cleaned} ({restore_size / 1024**2:.2f} MB)")
        print(f"Total: {total_cleaned} items ({total_size / 1024**2:.2f} MB)")
        
        if self.dry_run:
            print("\n⚠️ DRY RUN - No files removed. Use --execute to clean.")
        else:
            print(f"\n✅ Cleanup complete! Freed {total_size / 1024**2:.2f} MB")
        
        return {
            "temp_dirs_cleaned": temp_cleaned,
            "repos_cleaned": repos_cleaned,
            "restore_cleaned": restore_cleaned,
            "total_cleaned": total_cleaned,
            "size_freed_mb": total_size / 1024**2,
            "dry_run": self.dry_run
        }


def main():
    parser = argparse.ArgumentParser(description="Comprehensive disk space cleanup")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default)")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (not dry run)")
    parser.add_argument("--cleanup-temp-dirs", action="store_true", help="Cleanup temp directories only")
    parser.add_argument("--cleanup-temp-repos", action="store_true", help="Cleanup temp repos only")
    parser.add_argument("--cleanup-restore", action="store_true", help="Cleanup restore directory")
    parser.add_argument("--days", type=int, default=7, help="Days threshold for old files (default: 7)")
    parser.add_argument("--full", action="store_true", help="Full cleanup (all options)")
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    cleanup = ComprehensiveDiskCleanup(dry_run=dry_run)
    
    if args.cleanup_temp_dirs:
        cleaned, size = cleanup.cleanup_temp_dirs()
        print(f"\n✅ Cleaned {cleaned} temp directories ({size / 1024**2:.2f} MB)")
    elif args.cleanup_temp_repos:
        cleaned, size = cleanup.cleanup_temp_repos(days=args.days)
        print(f"\n✅ Cleaned {cleaned} temp repos ({size / 1024**2:.2f} MB)")
    elif args.cleanup_restore:
        cleaned, size = cleanup.cleanup_restore_directory()
        print(f"\n✅ Cleaned restore directory ({size / 1024**2:.2f} MB)")
    elif args.full:
        result = cleanup.cleanup_full()
        sys.exit(0 if result["total_cleaned"] > 0 else 1)
    else:
        # Default: full cleanup (dry run)
        result = cleanup.cleanup_full()
        print("\n💡 Tip: Use --execute to actually clean files")
        sys.exit(0)


if __name__ == "__main__":
    main()

