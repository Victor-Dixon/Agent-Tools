#!/usr/bin/env python3
"""
Swarm Time Tool - Get Current Time for Agents
=============================================

CLI tool for agents to get the current accurate time/date.
Always use this tool to ensure correct timestamps.

Usage:
    python tools/get_swarm_time.py                    # Get readable timestamp
    python tools/get_swarm_time.py --iso               # Get ISO timestamp
    python tools/get_swarm_time.py --filename         # Get filename timestamp
    python tools/get_swarm_time.py --date             # Get date only (YYYY-MM-DD)
    python tools/get_swarm_time.py --all              # Get all formats

Author: Agent-4 (Captain)
Date: 2025-11-28
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.utils.swarm_time import (
    get_swarm_time,
    format_swarm_timestamp,
    format_swarm_timestamp_readable,
    format_swarm_timestamp_filename
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Get current swarm time in various formats"
    )
    parser.add_argument(
        "--iso",
        action="store_true",
        help="Output ISO 8601 timestamp"
    )
    parser.add_argument(
        "--filename",
        action="store_true",
        help="Output filename-safe timestamp"
    )
    parser.add_argument(
        "--date",
        action="store_true",
        help="Output date only (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Output all timestamp formats"
    )
    
    args = parser.parse_args()
    
    # Get current time
    current_time = get_swarm_time()
    
    # Output based on flags
    if args.all:
        print("📅 Current Swarm Time - All Formats:")
        print(f"  Readable:  {format_swarm_timestamp_readable(current_time)}")
        print(f"  ISO:       {format_swarm_timestamp(current_time)}")
        print(f"  Filename:  {format_swarm_timestamp_filename(current_time)}")
        print(f"  Date:      {current_time.strftime('%Y-%m-%d')}")
    elif args.iso:
        print(format_swarm_timestamp(current_time))
    elif args.filename:
        print(format_swarm_timestamp_filename(current_time))
    elif args.date:
        print(current_time.strftime('%Y-%m-%d'))
    else:
        # Default: readable format
        print(format_swarm_timestamp_readable(current_time))


if __name__ == "__main__":
    main()

