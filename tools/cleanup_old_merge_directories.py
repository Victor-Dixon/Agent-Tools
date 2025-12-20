"""
Cleanup Old Merge Directories
=============================

Removes old merge and conflict resolution directories from D:/Temp
to free up disk space for new merge operations.

Author: Agent-7 (Web Development Specialist)
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

def cleanup_old_directories(
    base_path: Path = Path("D:/Temp"),
    days_old: int = 7,
    dry_run: bool = False
) -> Tuple[List[Path], float]:
    """
    Clean up old merge and conflict resolution directories.
    
    Args:
        base_path: Base directory to clean (default: D:/Temp)
        days_old: Remove directories older than this many days
        dry_run: If True, only report what would be deleted
        
    Returns:
        Tuple of (deleted_directories, freed_space_gb)
    """
    if not base_path.exists():
        print(f"⚠️  Directory does not exist: {base_path}")
        return [], 0.0
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    deleted = []
    total_size = 0
    
    # Find old merge/conflict directories
    for item in base_path.iterdir():
        if not item.is_dir():
            continue
            
        # Check if it's a merge/conflict directory
        name = item.name.lower()
        is_merge_dir = (
            "merge" in name or
            "resolve" in name or
            "batch" in name or
            "conflict" in name
        )
        
        if not is_merge_dir:
            continue
        
        # Check age
        try:
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff_date:
                # Calculate size
                size = sum(
                    f.stat().st_size
                    for f in item.rglob("*")
                    if f.is_file()
                )
                total_size += size
                deleted.append(item)
                
                if not dry_run:
                    print(f"🗑️  Deleting: {item.name} ({size/1024/1024:.2f} MB, {mtime.strftime('%Y-%m-%d')})")
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    print(f"📋 Would delete: {item.name} ({size/1024/1024:.2f} MB, {mtime.strftime('%Y-%m-%d')})")
        except Exception as e:
            print(f"⚠️  Error processing {item.name}: {e}")
    
    freed_gb = total_size / (1024 ** 3)
    return deleted, freed_gb

def main():
    """Main cleanup function."""
    import sys
    
    dry_run = "--dry-run" in sys.argv
    
    print("=" * 60)
    print("🧹 Cleanup Old Merge Directories")
    print("=" * 60)
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be deleted")
        print()
    
    base_path = Path("D:/Temp")
    days_old = 7
    
    print(f"📁 Scanning: {base_path}")
    print(f"⏰ Removing directories older than {days_old} days")
    print()
    
    deleted, freed_gb = cleanup_old_directories(
        base_path=base_path,
        days_old=days_old,
        dry_run=dry_run
    )
    
    print()
    print("=" * 60)
    if dry_run:
        print(f"📊 DRY RUN RESULTS:")
    else:
        print(f"✅ CLEANUP COMPLETE:")
    print(f"   Directories: {len(deleted)}")
    print(f"   Space freed: {freed_gb:.2f} GB")
    print("=" * 60)
    
    if not dry_run and deleted:
        print()
        print("✅ Old merge directories cleaned up successfully!")
        print("🚀 Ready for new merge operations")

if __name__ == "__main__":
    main()




