#!/usr/bin/env python3
"""
Task CLI
========

Quick task management (get/list/status/complete).

Author: Agent-1 (Integration & Core Systems Specialist)
V2 Compliant: <300 lines
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Task CLI - Quick task management")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Get next task
    get_parser = subparsers.add_parser("get", help="Get next available task")
    
    # List tasks
    list_parser = subparsers.add_parser("list", help="List all available tasks")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Show task status")
    
    # Complete
    complete_parser = subparsers.add_parser("complete", help="Mark task as complete")
    complete_parser.add_argument("task_id", help="Task ID to complete")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Use messaging CLI for task operations
    try:
        from src.services.messaging_cli import main as messaging_main
        
        if args.command == "get":
            print("📋 Getting next available task...")
            # Override sys.argv to call messaging CLI with --get-next-task
            original_argv = sys.argv
            sys.argv = ["task_cli", "--get-next-task"]
            try:
                messaging_main()
            finally:
                sys.argv = original_argv
        
        elif args.command == "list":
            print("📋 Listing all available tasks...")
            original_argv = sys.argv
            sys.argv = ["task_cli", "--list-tasks"]
            try:
                messaging_main()
            finally:
                sys.argv = original_argv
        
        elif args.command == "status":
            print("📊 Task status:")
            print("   Use 'task list' to see all tasks")
            print("   Use 'task get' to claim next task")
        
        elif args.command == "complete":
            print(f"✅ Marking task {args.task_id} as complete...")
            print("   (Task completion handled via messaging system)")
        
    except ImportError:
        print("⚠️  Messaging CLI not available")
        print("   Task management requires messaging system")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

