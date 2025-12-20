#!/usr/bin/env python3
"""
Disk Space Optimization Tool - Agent-1
=======================================

Implements space-saving measures based on analysis.

<!-- SSOT Domain: infrastructure -->

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-01-27
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent


def cleanup_temp_repos(older_than_days: int = 7, dry_run: bool = True) -> dict:
    """Cleanup old temp_repos directories."""
    temp_repos_dir = PROJECT_ROOT / "temp_repos"
    if not temp_repos_dir.exists():
        return {"cleaned": 0, "size_freed": 0, "items": []}
    
    cutoff_date = datetime.now() - timedelta(days=older_than_days)
    cleaned = 0
    size_freed = 0
    items = []
    
    for repo_dir in temp_repos_dir.iterdir():
        if not repo_dir.is_dir():
            continue
        
        try:
            # Check modification time
            mtime = datetime.fromtimestamp(repo_dir.stat().st_mtime)
            if mtime < cutoff_date:
                # Calculate size
                size = 0
                for item in repo_dir.rglob("*"):
                    if item.is_file():
                        size += item.stat().st_size
                
                items.append({
                    "path": str(repo_dir.relative_to(PROJECT_ROOT)),
                    "size_mb": size / (1024 ** 2),
                    "modified": mtime.isoformat()
                })
                
                if not dry_run:
                    shutil.rmtree(repo_dir, ignore_errors=True)
                    print(f"✅ Removed: {repo_dir.name} ({size / (1024**2):.2f} MB)")
                else:
                    print(f"🧹 Would remove: {repo_dir.name} ({size / (1024**2):.2f} MB, modified: {mtime.date()})")
                
                cleaned += 1
                size_freed += size
        except Exception as e:
            print(f"⚠️  Error processing {repo_dir.name}: {e}")
    
    return {
        "cleaned": cleaned,
        "size_freed": size_freed,
        "size_freed_mb": size_freed / (1024 ** 2),
        "items": items
    }


def cleanup_python_cache(dry_run: bool = True) -> dict:
    """Cleanup Python __pycache__ directories."""
    cleaned = 0
    size_freed = 0
    
    for pycache_dir in PROJECT_ROOT.rglob("__pycache__"):
        try:
            size = 0
            for item in pycache_dir.rglob("*"):
                if item.is_file():
                    size += item.stat().st_size
            
            if size > 0:
                if not dry_run:
                    shutil.rmtree(pycache_dir, ignore_errors=True)
                    print(f"✅ Removed: {pycache_dir.relative_to(PROJECT_ROOT)} ({size / (1024**2):.2f} MB)")
                else:
                    print(f"🧹 Would remove: {pycache_dir.relative_to(PROJECT_ROOT)} ({size / (1024**2):.2f} MB)")
                
                cleaned += 1
                size_freed += size
        except Exception as e:
            pass  # Skip permission errors
    
    return {
        "cleaned": cleaned,
        "size_freed": size_freed,
        "size_freed_mb": size_freed / (1024 ** 2)
    }


def optimize_git_repo(dry_run: bool = True) -> dict:
    """Optimize git repository (gc, prune)."""
    git_dir = PROJECT_ROOT / ".git"
    if not git_dir.exists():
        return {"optimized": False, "size_freed": 0}
    
    # Run git gc --aggressive --prune=now
    if not dry_run:
        try:
            result = subprocess.run(
                ["git", "gc", "--aggressive", "--prune=now"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_EXTENDED
            )
            if result.returncode == 0:
                print("✅ Git repository optimized")
                return {"optimized": True, "size_freed": 0}
            else:
                print(f"⚠️  Git optimization returned: {result.returncode}")
        except Exception as e:
            print(f"⚠️  Error optimizing git: {e}")
    else:
        print("🧹 Would run: git gc --aggressive --prune=now")
    
    return {"optimized": False, "size_freed": 0}


def recommend_c_drive_cleanup() -> list:
    """Generate recommendations for C: drive cleanup."""
    recommendations = []
    
    # Check C: drive usage
    try:
        usage = shutil.disk_usage("C:\\")
        percent_used = (usage.used / usage.total) * 100
        
        if percent_used > 90:
            recommendations.append({
                "priority": "HIGH",
                "action": "C: drive is 91.8% full - immediate action needed",
                "suggestions": [
                    "Run Windows Disk Cleanup utility",
                    "Clear browser cache and temporary files",
                    "Move user data to D: drive if possible",
                    "Uninstall unused programs",
                    "Clear Recycle Bin"
                ]
            })
    except Exception:
        pass
    
    return recommendations


def main():
    """Main optimization function."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(description="Disk space optimization")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (not dry run)")
    parser.add_argument("--cleanup-temp-repos", action="store_true", help="Cleanup old temp_repos")
    parser.add_argument("--cleanup-pycache", action="store_true", help="Cleanup __pycache__")
    parser.add_argument("--optimize-git", action="store_true", help="Optimize git repository")
    parser.add_argument("--all", action="store_true", help="Run all optimizations")
    parser.add_argument("--days", type=int, default=7, help="Days threshold for temp repos (default: 7)")
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    print("=" * 60)
    print("💾 DISK SPACE OPTIMIZATION")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print()
    
    total_freed = 0
    
    if args.all or args.cleanup_temp_repos:
        print("📁 Cleaning old temp_repos...")
        result = cleanup_temp_repos(older_than_days=args.days, dry_run=dry_run)
        total_freed += result["size_freed"]
        print(f"   Cleaned: {result['cleaned']} directories ({result['size_freed_mb']:.2f} MB)")
        print()
    
    if args.all or args.cleanup_pycache:
        print("🐍 Cleaning Python __pycache__...")
        result = cleanup_python_cache(dry_run=dry_run)
        total_freed += result["size_freed"]
        print(f"   Cleaned: {result['cleaned']} directories ({result['size_freed_mb']:.2f} MB)")
        print()
    
    if args.all or args.optimize_git:
        print("🔧 Optimizing git repository...")
        result = optimize_git_repo(dry_run=dry_run)
        print()
    
    # Always show C: drive recommendations
    print("💡 C: Drive Recommendations:")
    recommendations = recommend_c_drive_cleanup()
    for rec in recommendations:
        print(f"   Priority: {rec['priority']}")
        print(f"   Action: {rec['action']}")
        print("   Suggestions:")
        for suggestion in rec['suggestions']:
            print(f"     - {suggestion}")
    
    print()
    print("=" * 60)
    if dry_run:
        print(f"📊 Total would be freed: {total_freed / (1024**2):.2f} MB")
        print("⚠️  DRY RUN - Use --execute to actually clean")
    else:
        print(f"✅ Total freed: {total_freed / (1024**2):.2f} MB")
    print("=" * 60)


if __name__ == "__main__":
    main()

