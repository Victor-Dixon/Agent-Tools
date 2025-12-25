#!/usr/bin/env python3
"""
Message Queue Debug Tool
========================

Comprehensive debugging tool for the message queue system.
Identifies and fixes common issues automatically.

Author: Agent-2
V2 Compliant: <300 lines
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def check_queue_file() -> Dict[str, Any]:
    """Check queue file status."""
    queue_file = project_root / "message_queue" / "queue.json"
    issues = []
    status = {
        "exists": queue_file.exists(),
        "size": 0,
        "valid": False,
        "entries": 0,
        "issues": []
    }

    if not queue_file.exists():
        issues.append("Queue file does not exist")
        status["issues"] = issues
        return status

    status["size"] = queue_file.stat().st_size

    # Try to load and validate
    try:
        with open(queue_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            issues.append(
                f"Queue file is not a JSON array (type: {type(data)})")
            status["issues"] = issues
            return status

        status["valid"] = True
        status["entries"] = len(data)

        # Validate entries
        for i, entry in enumerate(data):
            entry_issues = []
            if not isinstance(entry, dict):
                entry_issues.append(f"Entry {i} is not a dict")
            else:
                if not entry.get('queue_id'):
                    entry_issues.append(f"Entry {i} missing queue_id")
                if not entry.get('message'):
                    entry_issues.append(f"Entry {i} missing message")
                elif isinstance(entry.get('message'), dict):
                    if not entry['message'].get('recipient'):
                        entry_issues.append(f"Entry {i} missing recipient")
                    if not entry['message'].get('content'):
                        entry_issues.append(f"Entry {i} missing content")

            if entry_issues:
                issues.extend(entry_issues)

        status["issues"] = issues

    except json.JSONDecodeError as e:
        issues.append(f"JSON decode error: {e}")
        status["issues"] = issues
    except Exception as e:
        issues.append(f"Error reading queue file: {e}")
        status["issues"] = issues

    return status


def analyze_queue_entries() -> Dict[str, Any]:
    """Analyze queue entries for issues."""
    queue_file = project_root / "message_queue" / "queue.json"

    if not queue_file.exists():
        return {"error": "Queue file does not exist"}

    try:
        with open(queue_file, 'r', encoding='utf-8') as f:
            entries = json.load(f)

        if not isinstance(entries, list):
            return {"error": "Queue file is not a JSON array"}

        now = datetime.now()
        analysis = {
            "total": len(entries),
            "by_status": Counter(e.get('status', 'UNKNOWN') for e in entries),
            "stuck_messages": [],
            "failed_messages": [],
            "invalid_entries": [],
            "old_entries": []
        }

        # Find stuck messages (PROCESSING > 5 minutes)
        for entry in entries:
            if entry.get('status') == 'PROCESSING':
                updated_at = entry.get('updated_at')
                if updated_at:
                    try:
                        if isinstance(updated_at, str):
                            updated = datetime.fromisoformat(
                                updated_at.replace('Z', '+00:00'))
                        else:
                            updated = datetime.fromisoformat(str(updated_at))

                        if updated.tzinfo:
                            updated = updated.replace(tzinfo=None)

                        age_seconds = (now - updated).total_seconds()
                        if age_seconds > 300:  # 5 minutes
                            analysis["stuck_messages"].append({
                                "queue_id": entry.get('queue_id', 'unknown'),
                                "age_seconds": age_seconds,
                                "recipient": entry.get('message', {}).get('recipient', 'unknown') if isinstance(entry.get('message'), dict) else 'unknown'
                            })
                    except Exception:
                        # Can't parse date, consider stuck
                        analysis["stuck_messages"].append({
                            "queue_id": entry.get('queue_id', 'unknown'),
                            "age_seconds": "unknown",
                            "recipient": entry.get('message', {}).get('recipient', 'unknown') if isinstance(entry.get('message'), dict) else 'unknown'
                        })

        # Find failed messages
        for entry in entries:
            if entry.get('status') == 'FAILED':
                analysis["failed_messages"].append({
                    "queue_id": entry.get('queue_id', 'unknown'),
                    "error": entry.get('metadata', {}).get('last_error', 'unknown'),
                    "attempts": entry.get('delivery_attempts', 0)
                })

        # Find invalid entries
        for i, entry in enumerate(entries):
            if not entry.get('queue_id') or not entry.get('message'):
                analysis["invalid_entries"].append({
                    "index": i,
                    "queue_id": entry.get('queue_id', 'missing'),
                    "has_message": bool(entry.get('message'))
                })

        # Find old entries (> 7 days)
        max_age = timedelta(days=7)
        for entry in entries:
            created_at = entry.get('created_at')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        created = datetime.fromisoformat(
                            created_at.replace('Z', '+00:00'))
                    else:
                        created = datetime.fromisoformat(str(created_at))

                    if created.tzinfo:
                        created = created.replace(tzinfo=None)

                    age = now - created
                    if age > max_age:
                        analysis["old_entries"].append({
                            "queue_id": entry.get('queue_id', 'unknown'),
                            "age_days": age.days,
                            "status": entry.get('status', 'unknown')
                        })
                except Exception:
                    pass

        return analysis

    except Exception as e:
        return {"error": str(e)}


def check_lock_files() -> Dict[str, Any]:
    """Check for lock files."""
    queue_dir = project_root / "message_queue"
    lock_files = [
        "delivered.json.lock",
        "failed.json.lock",
        "pending.json.lock",
        "processing.json.lock",
        "queue.json.lock"
    ]

    found_locks = []
    for lock_file in lock_files:
        lock_path = queue_dir / lock_file
        if lock_path.exists():
            found_locks.append(lock_file)

    return {
        "found": found_locks,
        "count": len(found_locks),
        "healthy": len(found_locks) == 0
    }


def check_queue_processor_running() -> Dict[str, Any]:
    """Check if queue processor is running."""
    import psutil

    running_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('queue' in str(arg).lower() for arg in cmdline):
                running_processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cmdline": ' '.join(cmdline[:3])
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return {
        "running": len(running_processes) > 0,
        "processes": running_processes,
        "count": len(running_processes)
    }


def fix_queue_issues(auto_fix: bool = False) -> Dict[str, Any]:
    """Fix identified queue issues."""
    fixes_applied = []

    # Fix 1: Clear lock files
    lock_status = check_lock_files()
    if lock_status["found"]:
        if auto_fix:
            queue_dir = project_root / "message_queue"
            for lock_file in lock_status["found"]:
                try:
                    (queue_dir / lock_file).unlink()
                    fixes_applied.append(f"Cleared lock file: {lock_file}")
                except Exception as e:
                    fixes_applied.append(f"Failed to clear {lock_file}: {e}")
        else:
            fixes_applied.append(
                f"Lock files found (not cleared): {', '.join(lock_status['found'])}")

    # Fix 2: Reset stuck messages
    analysis = analyze_queue_entries()
    if "stuck_messages" in analysis and analysis["stuck_messages"]:
        if auto_fix:
            queue_file = project_root / "message_queue" / "queue.json"
            try:
                with open(queue_file, 'r', encoding='utf-8') as f:
                    entries = json.load(f)

                reset_count = 0
                for entry in entries:
                    if entry.get('status') == 'PROCESSING':
                        updated_at = entry.get('updated_at')
                        if updated_at:
                            try:
                                if isinstance(updated_at, str):
                                    updated = datetime.fromisoformat(
                                        updated_at.replace('Z', '+00:00'))
                                else:
                                    updated = datetime.fromisoformat(
                                        str(updated_at))

                                if updated.tzinfo:
                                    updated = updated.replace(tzinfo=None)

                                age_seconds = (
                                    datetime.now() - updated).total_seconds()
                                if age_seconds > 300:
                                    entry['status'] = 'PENDING'
                                    entry['updated_at'] = datetime.now(
                                    ).isoformat()
                                    reset_count += 1
                            except Exception:
                                # Reset if can't parse
                                entry['status'] = 'PENDING'
                                entry['updated_at'] = datetime.now().isoformat()
                                reset_count += 1

                if reset_count > 0:
                    # Backup first
                    backup_file = queue_file.parent / \
                        f"queue_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(entries, f, indent=2)

                    # Save fixed queue
                    with open(queue_file, 'w', encoding='utf-8') as f:
                        json.dump(entries, f, indent=2)

                    fixes_applied.append(
                        f"Reset {reset_count} stuck messages to PENDING")
            except Exception as e:
                fixes_applied.append(f"Failed to reset stuck messages: {e}")
        else:
            fixes_applied.append(
                f"Found {len(analysis['stuck_messages'])} stuck messages (not reset)")

    # Fix 3: Remove invalid entries
    if "invalid_entries" in analysis and analysis["invalid_entries"]:
        if auto_fix:
            queue_file = project_root / "message_queue" / "queue.json"
            try:
                with open(queue_file, 'r', encoding='utf-8') as f:
                    entries = json.load(f)

                valid_entries = [
                    e for e in entries
                    if e.get('queue_id') and e.get('message')
                ]

                removed_count = len(entries) - len(valid_entries)
                if removed_count > 0:
                    # Backup first
                    backup_file = queue_file.parent / \
                        f"queue_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(entries, f, indent=2)

                    # Save cleaned queue
                    with open(queue_file, 'w', encoding='utf-8') as f:
                        json.dump(valid_entries, f, indent=2)

                    fixes_applied.append(
                        f"Removed {removed_count} invalid entries")
            except Exception as e:
                fixes_applied.append(f"Failed to remove invalid entries: {e}")
        else:
            fixes_applied.append(
                f"Found {len(analysis['invalid_entries'])} invalid entries (not removed)")

    return {
        "fixes_applied": fixes_applied,
        "count": len(fixes_applied)
    }


def main():
    """Main debug routine."""
    import argparse

    parser = argparse.ArgumentParser(description="Debug message queue system")
    parser.add_argument("--fix", action="store_true",
                        help="Automatically fix issues")
    parser.add_argument("--verbose", "-v",
                        action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("=" * 70)
    print("MESSAGE QUEUE DEBUG REPORT")
    print("=" * 70)
    print()

    # Check queue file
    print("📋 Queue File Status:")
    queue_status = check_queue_file()
    print(f"  Exists: {queue_status['exists']}")
    print(f"  Size: {queue_status['size']:,} bytes")
    print(f"  Valid: {queue_status['valid']}")
    print(f"  Entries: {queue_status['entries']}")
    if queue_status['issues']:
        print(f"  ⚠️  Issues: {len(queue_status['issues'])}")
        for issue in queue_status['issues'][:5]:
            print(f"    - {issue}")
    else:
        print(f"  ✅ No issues found")
    print()

    # Analyze entries
    if queue_status['valid']:
        print("📊 Queue Analysis:")
        analysis = analyze_queue_entries()
        if "error" not in analysis:
            print(f"  Total entries: {analysis['total']}")
            print(f"  Status distribution:")
            for status, count in analysis['by_status'].most_common():
                print(f"    {status}: {count}")

            if analysis['stuck_messages']:
                print(
                    f"  ⚠️  Stuck messages: {len(analysis['stuck_messages'])}")
                for msg in analysis['stuck_messages'][:5]:
                    print(
                        f"    - {msg['queue_id'][:20]}... ({msg.get('age_seconds', 'unknown')}s)")

            if analysis['failed_messages']:
                print(
                    f"  ⚠️  Failed messages: {len(analysis['failed_messages'])}")

            if analysis['invalid_entries']:
                print(
                    f"  ⚠️  Invalid entries: {len(analysis['invalid_entries'])}")

            if analysis['old_entries']:
                print(
                    f"  ⚠️  Old entries (>7 days): {len(analysis['old_entries'])}")
        else:
            print(f"  ❌ Error: {analysis['error']}")
        print()

    # Check lock files
    print("🔒 Lock Files:")
    lock_status = check_lock_files()
    print(f"  Found: {lock_status['count']}")
    if lock_status['found']:
        print(f"  ⚠️  Lock files: {', '.join(lock_status['found'])}")
    else:
        print(f"  ✅ No lock files")
    print()

    # Check processor
    try:
        print("🔄 Queue Processor:")
        proc_status = check_queue_processor_running()
        print(f"  Running: {proc_status['running']}")
        if proc_status['processes']:
            for proc in proc_status['processes']:
                print(f"    PID {proc['pid']}: {proc['cmdline']}")
        else:
            print(f"  ⚠️  Queue processor not running")
        print()
    except ImportError:
        print("  ⚠️  psutil not available (cannot check processes)")
        print()

    # Fix issues if requested
    if args.fix:
        print("🔧 Applying Fixes:")
        fixes = fix_queue_issues(auto_fix=True)
        if fixes['fixes_applied']:
            for fix in fixes['fixes_applied']:
                print(f"  ✅ {fix}")
        else:
            print(f"  ✅ No fixes needed")
        print()

    # Recommendations
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    recommendations = []

    if not queue_status['valid']:
        recommendations.append("Fix queue file format or restore from backup")

    if analysis.get('stuck_messages'):
        recommendations.append(
            f"Reset {len(analysis['stuck_messages'])} stuck messages (run with --fix)")

    if lock_status['found']:
        recommendations.append(
            f"Clear {len(lock_status['found'])} lock files (run with --fix)")

    if not proc_status.get('running', True):
        recommendations.append(
            "Start queue processor: python tools/start_message_queue_processor.py")

    if not recommendations:
        print("✅ Queue appears healthy!")
    else:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

    print()


if __name__ == "__main__":
    main()
