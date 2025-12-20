#!/usr/bin/env python3
"""
Cache Refresh Tool
==================

Forces a complete refresh of project scanner cache.
Use when scan data is outdated or after major consolidation work.

Usage:
    python tools/refresh_cache.py
    python tools/refresh_cache.py --hard  # Delete cache first
    python tools/refresh_cache.py --verify  # Check cache freshness

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-10-13
License: MIT
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def check_cache_freshness() -> dict:
    """Check how old the cache files are."""
    cache_files = [
        "dependency_cache.json",
        "project_analysis.json",
        "test_analysis.json",
        "chatgpt_project_context.json"
    ]
    
    freshness = {}
    for cache_file in cache_files:
        path = Path(cache_file)
        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            age_hours = (datetime.now() - mtime).total_seconds() / 3600
            freshness[cache_file] = {
                "exists": True,
                "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                "age_hours": round(age_hours, 1),
                "status": "fresh" if age_hours < 24 else "stale" if age_hours < 168 else "very_stale"
            }
        else:
            freshness[cache_file] = {
                "exists": False,
                "status": "missing"
            }
    
    return freshness


def delete_cache_files(analysis_chunks: bool = False) -> dict:
    """Delete cache files."""
    deleted = []
    errors = []
    
    cache_files = [
        "dependency_cache.json",
        "project_analysis.json", 
        "test_analysis.json",
        "chatgpt_project_context.json"
    ]
    
    for cache_file in cache_files:
        path = Path(cache_file)
        if path.exists():
            try:
                path.unlink()
                deleted.append(cache_file)
            except Exception as e:
                errors.append(f"{cache_file}: {e}")
    
    # Optionally delete analysis_chunks
    if analysis_chunks:
        chunks_dir = Path("analysis_chunks")
        if chunks_dir.exists():
            try:
                shutil.rmtree(chunks_dir)
                deleted.append("analysis_chunks/")
            except Exception as e:
                errors.append(f"analysis_chunks/: {e}")
    
    return {"deleted": deleted, "errors": errors}


def refresh_cache(hard_reset: bool = False, analysis_chunks: bool = False) -> dict:
    """Refresh project scanner cache."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "hard_reset": hard_reset
    }
    
    # Hard reset: delete first
    if hard_reset:
        print("🗑️  Performing HARD RESET - deleting cache files...")
        delete_result = delete_cache_files(analysis_chunks)
        result["deleted"] = delete_result["deleted"]
        result["errors"] = delete_result["errors"]
        
        if delete_result["errors"]:
            print(f"⚠️  Some files could not be deleted:")
            for error in delete_result["errors"]:
                print(f"  - {error}")
        else:
            print(f"✅ Deleted {len(delete_result['deleted'])} cache files/directories")
    
    # Run scanner
    print("\n🔄 Running project scanner with fresh data...")
    try:
        import subprocess
from src.core.config.timeout_constants import TimeoutConstants
        result_proc = subprocess.run(
            [sys.executable, "tools/run_project_scan.py"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_EXTENDED  # 5 minute timeout
        )
        
        if result_proc.returncode == 0:
            result["scan_success"] = True
            result["message"] = "Cache refreshed successfully"
            print("✅ Project scan completed successfully!")
        else:
            result["scan_success"] = False
            result["message"] = "Scan failed"
            result["error"] = result_proc.stderr
            print(f"❌ Scan failed: {result_proc.stderr}")
    except subprocess.TimeoutExpired:
        result["scan_success"] = False
        result["message"] = "Scan timed out after 5 minutes"
        print("⏱️  Scan timed out - project may be too large")
    except Exception as e:
        result["scan_success"] = False
        result["message"] = f"Error running scanner: {e}"
        print(f"❌ Error: {e}")
    
    # Check new cache freshness
    if result.get("scan_success"):
        new_freshness = check_cache_freshness()
        result["cache_freshness"] = new_freshness
    
    return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Refresh project scanner cache",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Soft refresh (keep cache, regenerate)
    python tools/refresh_cache.py
    
    # Hard reset (delete cache first)
    python tools/refresh_cache.py --hard
    
    # Include analysis chunks in deletion
    python tools/refresh_cache.py --hard --analysis-chunks
    
    # Check cache freshness only
    python tools/refresh_cache.py --verify

Use this tool when scan data is outdated or giving incorrect results!
        """
    )
    
    parser.add_argument('--hard', action='store_true', 
                       help='Hard reset: delete cache files first')
    parser.add_argument('--analysis-chunks', action='store_true',
                       help='Also delete analysis_chunks/ directory (with --hard)')
    parser.add_argument('--verify', action='store_true',
                       help='Only check cache freshness, do not refresh')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    
    args = parser.parse_args()
    
    # Verify only
    if args.verify:
        freshness = check_cache_freshness()
        if args.json:
            print(json.dumps(freshness, indent=2))
        else:
            print("\n" + "="*70)
            print("🔍 CACHE FRESHNESS REPORT")
            print("="*70)
            for file, info in freshness.items():
                print(f"\n📁 {file}:")
                if info["exists"]:
                    print(f"  Modified: {info['modified']}")
                    print(f"  Age: {info['age_hours']} hours")
                    print(f"  Status: {info['status']}")
                else:
                    print(f"  Status: MISSING")
            print("\n" + "="*70 + "\n")
        sys.exit(0)
    
    # Refresh cache
    print("\n" + "="*70)
    print("🔄 PROJECT CACHE REFRESH")
    print("="*70 + "\n")
    
    result = refresh_cache(args.hard, args.analysis_chunks)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "="*70)
        print("📊 REFRESH SUMMARY")
        print("="*70)
        print(f"\nTimestamp: {result['timestamp']}")
        print(f"Hard Reset: {result['hard_reset']}")
        print(f"Success: {result.get('scan_success', False)}")
        print(f"Message: {result.get('message', 'Unknown')}")
        print("\n" + "="*70 + "\n")
    
    sys.exit(0 if result.get("scan_success") else 1)


if __name__ == "__main__":
    main()

