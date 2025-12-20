#!/usr/bin/env python3
"""
Cleanup Obsolete Files
======================

Removes obsolete test/debug files that have been replaced by thea_automation.py.
Run with --dry-run to see what would be deleted without actually deleting.
"""

import argparse
from pathlib import Path

# Files that are obsolete and can be safely deleted
OBSOLETE_FILES = [
    "test_cookie_fix.py",
    "test_cookie_simple.py",
    "cookie_system_status.py",
    "COOKIE_SYSTEM_SUCCESS.md",
]

# Files that are replaced but you might want to keep as backup
REPLACED_FILES = [
    "simple_thea_communication.py",  # Replaced by thea_automation.py
    "setup_thea_cookies.py",  # Setup now integrated
]


def cleanup(dry_run=True, remove_replaced=False):
    """
    Clean up obsolete files.

    Args:
        dry_run: If True, only show what would be deleted
        remove_replaced: If True, also remove replaced files (backup recommended)
    """
    print("🧹 CLEANUP OBSOLETE FILES")
    print("=" * 50)
    print()

    files_to_remove = OBSOLETE_FILES.copy()

    if remove_replaced:
        files_to_remove.extend(REPLACED_FILES)
        print("⚠️  Including replaced files (backup recommended!)")

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be deleted")
    else:
        print("⚠️  DELETION MODE - Files will be deleted!")

    print()
    print("Files to remove:")
    print("-" * 30)

    removed_count = 0
    kept_count = 0

    for filename in files_to_remove:
        filepath = Path(filename)

        if filepath.exists():
            size = filepath.stat().st_size

            if dry_run:
                print(f"  ❌ Would delete: {filename} ({size} bytes)")
            else:
                try:
                    filepath.unlink()
                    print(f"  ✅ Deleted: {filename} ({size} bytes)")
                    removed_count += 1
                except Exception as e:
                    print(f"  ⚠️  Failed to delete {filename}: {e}")
        else:
            print(f"  ⏭️  Already gone: {filename}")
            kept_count += 1

    print()
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)

    if dry_run:
        print(f"Would delete: {len([f for f in files_to_remove if Path(f).exists()])} files")
        print(f"Already gone: {kept_count} files")
        print()
        print("💡 To actually delete, run:")
        print("   python cleanup_obsolete_files.py --execute")
    else:
        print(f"✅ Deleted: {removed_count} files")
        print(f"Already gone: {kept_count} files")
        print()
        print("🎉 Cleanup complete!")

    print()
    print("🔧 WHAT YOU SHOULD KEEP:")
    print("  ✅ thea_automation.py - NEW unified system")
    print("  ✅ thea_cookies.json - Your saved cookies")
    print("  ✅ response_detector.py - Required dependency")
    print("  ✅ test_unified_system.py - Tests")
    print("  ✅ CLEANUP_GUIDE.md - Documentation")


def main():
    parser = argparse.ArgumentParser(description="Cleanup obsolete Thea files")
    parser.add_argument(
        "--execute", action="store_true", help="Actually delete files (default is dry-run)"
    )
    parser.add_argument(
        "--include-replaced",
        action="store_true",
        help="Also remove replaced files like simple_thea_communication.py",
    )

    args = parser.parse_args()

    cleanup(dry_run=not args.execute, remove_replaced=args.include_replaced)


if __name__ == "__main__":
    main()
