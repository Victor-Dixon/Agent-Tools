#!/usr/bin/env python3
"""
Disk Space Cleanup Tool - For Batch 2 Merge Operations
======================================================

Cleans up temporary files and directories from merge operations to resolve
disk space errors blocking git clone operations.

USAGE:
    # Dry run (show what would be cleaned)
    python tools/disk_space_cleanup.py --dry-run
    
    # Cleanup merge temp directories
    python tools/disk_space_cleanup.py --cleanup-temp
    
    # Cleanup old backups/logs
    python tools/disk_space_cleanup.py --cleanup-old --days 7
    
    # Full cleanup
    python tools/disk_space_cleanup.py --full

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


class DiskSpaceCleanup:
    """Cleanup temporary files from merge operations"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.cleaned_items = []
        self.total_size_freed = 0
        
    def find_temp_merge_dirs(self) -> List[Path]:
        """Find temporary merge directories"""
        temp_dirs = []
        
        # Check common temp locations
        temp_patterns = [
            "repo_merge_*",
            "github_merge_*",
            "temp/repo_*",
            "temp/git_*",
        ]
        
        for pattern in temp_patterns:
            # Search in current directory and temp/
            for base in [PROJECT_ROOT, PROJECT_ROOT / "temp"]:
                if base.exists():
                    for path in base.glob(pattern):
                        if path.is_dir():
                            temp_dirs.append(path)
        
        # Also check system temp
        import tempfile
        temp_base = Path(tempfile.gettempdir())
        for path in temp_base.glob("repo_merge_*"):
            if path.is_dir():
                temp_dirs.append(path)
        for path in temp_base.glob("github_merge_*"):
            if path.is_dir():
                temp_dirs.append(path)
        
        return temp_dirs
    
    def find_old_backups(self, days: int = 7) -> List[Path]:
        """Find old backup files"""
        old_backups = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        backup_dirs = [
            PROJECT_ROOT / "consolidation_backups",
            PROJECT_ROOT / "consolidation_logs",
            PROJECT_ROOT / "temp_repos",  # Add temp_repos for cleanup
        ]
        
        for backup_dir in backup_dirs:
            if not backup_dir.exists():
                continue
                
            for backup_file in backup_dir.rglob("*"):
                if backup_file.is_file():
                    try:
                        mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                        if mtime < cutoff_date:
                            old_backups.append(backup_file)
                    except Exception:
                        pass
        
        return old_backups
    
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
    
    def cleanup_old_backups(self, days: int = 7) -> Tuple[int, int]:
        """Cleanup old backup files"""
        old_backups = self.find_old_backups(days)
        cleaned = 0
        size_freed = 0
        
        for backup_file in old_backups:
            try:
                size = self.get_size(backup_file)
                if self.dry_run:
                    print(f"🧹 Would remove: {backup_file} ({size / 1024**2:.2f} MB)")
                else:
                    backup_file.unlink()
                    print(f"✅ Removed: {backup_file} ({size / 1024**2:.2f} MB)")
                    self.cleaned_items.append(str(backup_file))
                cleaned += 1
                size_freed += size
            except Exception as e:
                print(f"⚠️ Error cleaning {backup_file}: {e}")
        
        return cleaned, size_freed
    
    def cleanup_full(self) -> Dict[str, any]:
        """Perform full cleanup"""
        print("=" * 60)
        print("🧹 DISK SPACE CLEANUP")
        print("=" * 60)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTE'}")
        print()
        
        # Cleanup temp directories
        print("📁 Cleaning temporary merge directories...")
        temp_cleaned, temp_size = self.cleanup_temp_dirs()
        
        # Cleanup old backups
        print("\n📦 Cleaning old backup files (older than 7 days)...")
        backup_cleaned, backup_size = self.cleanup_old_backups(days=7)
        
        total_cleaned = temp_cleaned + backup_cleaned
        total_size = temp_size + backup_size
        
        print("\n" + "=" * 60)
        print("📊 CLEANUP SUMMARY")
        print("=" * 60)
        print(f"Temp directories: {temp_cleaned} ({temp_size / 1024**2:.2f} MB)")
        print(f"Old backups: {backup_cleaned} ({backup_size / 1024**2:.2f} MB)")
        print(f"Total: {total_cleaned} items ({total_size / 1024**2:.2f} MB)")
        
        if self.dry_run:
            print("\n⚠️ DRY RUN - No files removed. Use --execute to clean.")
        else:
            print(f"\n✅ Cleanup complete! Freed {total_size / 1024**2:.2f} MB")
        
        return {
            "temp_dirs_cleaned": temp_cleaned,
            "backups_cleaned": backup_cleaned,
            "total_cleaned": total_cleaned,
            "size_freed_mb": total_size / 1024**2,
            "dry_run": self.dry_run
        }


def main():
    parser = argparse.ArgumentParser(description="Disk space cleanup for merge operations")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default)")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (not dry run)")
    parser.add_argument("--cleanup-temp", action="store_true", help="Cleanup temp directories only")
    parser.add_argument("--cleanup-old", action="store_true", help="Cleanup old backups only")
    parser.add_argument("--days", type=int, default=7, help="Days threshold for old files (default: 7)")
    parser.add_argument("--full", action="store_true", help="Full cleanup (temp + old backups)")
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    cleanup = DiskSpaceCleanup(dry_run=dry_run)
    
    if args.cleanup_temp:
        cleaned, size = cleanup.cleanup_temp_dirs()
        print(f"\n✅ Cleaned {cleaned} temp directories ({size / 1024**2:.2f} MB)")
    elif args.cleanup_old:
        cleaned, size = cleanup.cleanup_old_backups(days=args.days)
        print(f"\n✅ Cleaned {cleaned} old backups ({size / 1024**2:.2f} MB)")
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
