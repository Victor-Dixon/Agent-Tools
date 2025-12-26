#!/usr/bin/env python3
"""
Unified Debugger & Forensics Tool
=================================

System-wide debugging interface that:
1. Checks Swarm infrastructure (Queue, Agents, Services)
2. Analyzes logs for error patterns
3. Provides forensic insights on agent failures

Architecture: WE ARE SWARM
"""

import sys
import json
import glob
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

# Import existing debug tools logic where possible or reimplement lightweight versions
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def check_queue_health() -> dict:
    """Check message queue health (lightweight wrapper)."""
    try:
        from tools.debug.debug_message_queue import check_queue_file, analyze_queue_entries, check_lock_files
        
        status = check_queue_file()
        locks = check_lock_files()
        
        if status.get("valid"):
            analysis = analyze_queue_entries()
            return {
                "status": "healthy" if not analysis.get("stuck_messages") and not locks["found"] else "degraded",
                "pending": analysis.get("by_status", {}).get("PENDING", 0),
                "stuck": len(analysis.get("stuck_messages", [])),
                "locks": len(locks["found"]),
                "details": "Queue operational" if status["valid"] else "Queue file invalid"
            }
        return {"status": "critical", "details": "Queue file invalid or missing"}
    except ImportError:
        return {"status": "unknown", "details": "Could not import queue debug tools"}

def scan_logs_for_errors(hours: int = 24) -> dict:
    """Scan recent log files for errors."""
    log_patterns = [
        "error", "exception", "traceback", "failed", "critical"
    ]
    
    log_files = []
    # Add common log locations
    log_files.extend(glob.glob("logs/*.log"))
    log_files.extend(glob.glob("*.log"))
    
    errors = []
    cutoff = datetime.now() - timedelta(hours=hours)
    
    for log_file in log_files:
        try:
            path = Path(log_file)
            if path.stat().st_mtime < cutoff.timestamp():
                continue
                
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    line_lower = line.lower()
                    if any(p in line_lower for p in log_patterns):
                        errors.append({
                            "file": log_file,
                            "line": i,
                            "content": line.strip()[:100]
                        })
        except Exception:
            pass
            
    return {
        "count": len(errors),
        "files_scanned": len(log_files),
        "top_errors": errors[:10]
    }

def check_agent_processes() -> dict:
    """Check running agent processes."""
    try:
        import psutil
        agents = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = " ".join(proc.info['cmdline'] or [])
                if "python" in cmd and "agent" in cmd:
                    agents.append({
                        "pid": proc.info['pid'],
                        "cmd": cmd[:50] + "..."
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return {"count": len(agents), "agents": agents}
    except ImportError:
        return {"error": "psutil not installed"}

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unified Swarm Debugger")
    parser.add_argument("--logs", action="store_true", help="Scan logs for errors")
    parser.add_argument("--queue", action="store_true", help="Check queue health")
    parser.add_argument("--process", action="store_true", help="Check processes")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    args = parser.parse_args()
    
    if not any([args.logs, args.queue, args.process, args.all]):
        args.all = True
        
    print("🕵️  UNIFIED SWARM FORENSICS")
    print("=" * 60)
    
    if args.all or args.process:
        print("\n🤖 Process Check:")
        procs = check_agent_processes()
        if "error" in procs:
            print(f"  ⚠️  {procs['error']}")
        else:
            print(f"  Running Agent Processes: {procs['count']}")
            for a in procs['agents']:
                print(f"  - [{a['pid']}] {a['cmd']}")

    if args.all or args.queue:
        print("\nbn📨 Queue Health:")
        q_health = check_queue_health()
        status_icon = "✅" if q_health["status"] == "healthy" else "⚠️" if q_health["status"] == "degraded" else "❌"
        print(f"  {status_icon} Status: {q_health['status'].upper()}")
        print(f"  - Pending: {q_health.get('pending', '?')}")
        print(f"  - Stuck: {q_health.get('stuck', '?')}")
        print(f"  - Locks: {q_health.get('locks', '?')}")

    if args.all or args.logs:
        print("\n📜 Log Analysis (Last 24h):")
        logs = scan_logs_for_errors()
        print(f"  Files Scanned: {logs['files_scanned']}")
        print(f"  Errors Found: {logs['count']}")
        if logs['count'] > 0:
            print("  Top Errors:")
            for e in logs['top_errors']:
                print(f"  - {e['file']}:{e['line']} -> {e['content']}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
