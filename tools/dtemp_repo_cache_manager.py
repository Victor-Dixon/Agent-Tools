#!/usr/bin/env python3
"""
D:/Temp repo cache manager.

Keeps the D-drive clone cache healthy by:
* Ensuring the cache root exists
* Reporting usage (per-directory + totals)
* Pruning stale directories by age
* Enforcing a soft size cap (oldest directories removed first)

Usage examples:
    python tools/dtemp_repo_cache_manager.py --status
    python tools/dtemp_repo_cache_manager.py --ensure --status
    python tools/dtemp_repo_cache_manager.py --prune-older-than 36
    python tools/dtemp_repo_cache_manager.py --max-size-gb 8 --dry-run
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


DEFAULT_CACHE_ROOT = os.environ.get("D_DRIVE_TEMP_DIR", r"D:/Temp/repo_cache")


@dataclass
class CacheEntry:
    path: Path
    size_bytes: int
    created_at: datetime
    modified_at: datetime

    @property
    def age_hours(self) -> float:
        return (datetime.now() - self.modified_at).total_seconds() / 3600


def human_readable(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    if num_bytes <= 0:
        return "0 B"
    idx = 0
    value = float(num_bytes)
    while value >= 1024 and idx < len(units) - 1:
        value /= 1024
        idx += 1
    return f"{value:.2f} {units[idx]}"


def resolve_cache_root(path: Optional[str]) -> Path:
    root = Path(path or DEFAULT_CACHE_ROOT)
    return root.expanduser().resolve()


def ensure_cache_root(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def scan_directory_size(path: Path) -> Tuple[int, datetime, datetime]:
    total = 0
    ctime = path.stat().st_ctime
    mtime = path.stat().st_mtime
    oldest = datetime.fromtimestamp(ctime)
    newest = datetime.fromtimestamp(mtime)

    for root, dirs, files in os.walk(path):
        for fname in files:
            fpath = Path(root) / fname
            try:
                stats = fpath.stat()
            except FileNotFoundError:
                continue
            total += stats.st_size
            f_ctime = datetime.fromtimestamp(stats.st_ctime)
            f_mtime = datetime.fromtimestamp(stats.st_mtime)
            if f_ctime < oldest:
                oldest = f_ctime
            if f_mtime > newest:
                newest = f_mtime
    return total, oldest, newest


def load_cache_entries(cache_root: Path) -> List[CacheEntry]:
    entries: List[CacheEntry] = []
    if not cache_root.exists():
        return entries

    for child in cache_root.iterdir():
        if not child.is_dir():
            continue
        size, created, modified = scan_directory_size(child)
        entries.append(CacheEntry(child, size, created, modified))
    entries.sort(key=lambda entry: entry.modified_at)
    return entries


def print_status(cache_root: Path, entries: List[CacheEntry]) -> None:
    total_size = sum(entry.size_bytes for entry in entries)
    print(f"Cache root: {cache_root}")
    print(f"Entries  : {len(entries)}")
    print(f"Total    : {human_readable(total_size)}")
    print("-" * 60)
    for entry in entries:
        print(
            f"{entry.path.name:<40} "
            f"{human_readable(entry.size_bytes):>12}  "
            f"age {entry.age_hours:>6.1f}h  "
            f"modified {entry.modified_at:%Y-%m-%d %H:%M}"
        )
    if not entries:
        print("(no cache entries found)")


def prune_by_age(
    entries: List[CacheEntry], hours: float, dry_run: bool = False
) -> Tuple[int, int]:
    cutoff = datetime.now() - timedelta(hours=hours)
    removed, freed = 0, 0
    for entry in entries:
        if entry.modified_at <= cutoff:
            removed += 1
            freed += entry.size_bytes
            print(
                f"{'[dry-run]' if dry_run else '[delete]'} "
                f"{entry.path} ({human_readable(entry.size_bytes)})"
            )
            if not dry_run:
                shutil.rmtree(entry.path, ignore_errors=True)
    return removed, freed


def enforce_max_size(
    entries: List[CacheEntry], max_gb: float, dry_run: bool = False
) -> Tuple[int, int]:
    if max_gb <= 0:
        return 0, 0
    max_bytes = max_gb * 1024**3
    total = sum(entry.size_bytes for entry in entries)
    removed = 0
    freed = 0
    if total <= max_bytes:
        return removed, freed

    print(
        f"Total cache size {human_readable(total)} exceeds limit "
        f"{human_readable(int(max_bytes))}. Removing oldest entries..."
    )
    for entry in entries:
        if total <= max_bytes:
            break
        removed += 1
        freed += entry.size_bytes
        total -= entry.size_bytes
        print(
            f"{'[dry-run]' if dry_run else '[delete]'} "
            f"{entry.path} ({human_readable(entry.size_bytes)})"
        )
        if not dry_run:
            shutil.rmtree(entry.path, ignore_errors=True)
    return removed, freed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage the D:/Temp repository cache used for merge tooling."
    )
    parser.add_argument("--cache-dir", help="Override cache root (default: D:/Temp/repo_cache)")
    parser.add_argument("--ensure", action="store_true", help="Create cache root if it is missing")
    parser.add_argument("--status", action="store_true", help="Print cache status (default action)")
    parser.add_argument(
        "--prune-older-than",
        type=float,
        metavar="HOURS",
        help="Delete cache entries whose latest modification is older than the provided hours",
    )
    parser.add_argument(
        "--max-size-gb",
        type=float,
        metavar="GB",
        help="Enforce a soft ceiling for total cache size (removes oldest entries first)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletions without removing files",
    )
    args = parser.parse_args()

    cache_root = resolve_cache_root(args.cache_dir)
    if args.ensure:
        ensure_cache_root(cache_root)
        print(f"Ensured cache root exists: {cache_root}")

    entries = load_cache_entries(cache_root)

    removed = freed = 0
    if args.prune_older_than:
        removed, freed = prune_by_age(entries, args.prune_older_than, args.dry_run)
        print(
            f"Prune summary: removed {removed} entries, "
            f"freed {human_readable(freed)}"
        )
        # Refresh entries after deletion
        entries = load_cache_entries(cache_root)

    if args.max_size_gb:
        rem, fr = enforce_max_size(entries, args.max_size_gb, args.dry_run)
        removed += rem
        freed += fr
        if rem:
            entries = load_cache_entries(cache_root)

    if args.status or (not args.prune_older_than and not args.max_size_gb and not args.ensure):
        print_status(cache_root, entries)
        if removed or freed:
            print(
                f"\nTotal removals: {removed}, total freed: {human_readable(freed)}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

