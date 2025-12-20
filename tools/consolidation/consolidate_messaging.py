#!/usr/bin/env python3
"""
Consolidate Messaging System
=============================

Safely consolidates messaging_cli.py duplicates.
"""

import shutil
from pathlib import Path


def consolidate_messaging(dry_run=True):
    """Consolidate messaging system files."""

    print("🔧 MESSAGING SYSTEM CONSOLIDATION")
    print("=" * 50)
    print()

    old_file = Path("src/services/messaging_cli.py")
    refactored_file = Path("src/services/messaging_cli_refactored.py")
    backup_file = Path("src/services/messaging_cli.backup")

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        print("⚠️  EXECUTION MODE - Files will be modified!")

    print()

    # Check files exist
    print("📁 Checking files...")
    if old_file.exists():
        print(f"  ✅ Found: {old_file} ({old_file.stat().st_size} bytes)")
    else:
        print(f"  ❌ Missing: {old_file}")
        return False

    if refactored_file.exists():
        print(f"  ✅ Found: {refactored_file} ({refactored_file.stat().st_size} bytes)")
    else:
        print(f"  ❌ Missing: {refactored_file}")
        return False

    print()

    # Plan
    print("📋 Consolidation Plan:")
    print("  1. Backup messaging_cli.py → messaging_cli.backup")
    print("  2. Delete messaging_cli.py")
    print("  3. Rename messaging_cli_refactored.py → messaging_cli.py")
    print()

    if dry_run:
        print("💡 To execute, run:")
        print("   python consolidate_messaging.py --execute")
        return True

    # Execute
    try:
        # Step 1: Backup
        print("📦 Step 1: Creating backup...")
        shutil.copy2(old_file, backup_file)
        print(f"  ✅ Backed up to: {backup_file}")

        # Step 2: Delete old
        print("🗑️  Step 2: Removing old version...")
        old_file.unlink()
        print(f"  ✅ Deleted: {old_file}")

        # Step 3: Rename refactored
        print("📝 Step 3: Renaming refactored version...")
        refactored_file.rename(old_file)
        print(f"  ✅ Renamed: {refactored_file} → {old_file}")

        print()
        print("=" * 50)
        print("🎉 CONSOLIDATION COMPLETE!")
        print("=" * 50)
        print()
        print("✅ Result:")
        print(f"  • Active: {old_file}")
        print(f"  • Backup: {backup_file}")
        print("  • Removed: messaging_cli_refactored.py")
        print()
        print("🧪 Test it:")
        print("   python src/services/messaging_cli.py --help")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n🔧 Attempting rollback...")

        # Rollback if possible
        try:
            if backup_file.exists() and not old_file.exists():
                backup_file.rename(old_file)
                print("✅ Rollback successful")
        except Exception as rollback_error:
            print(f"❌ Rollback failed: {rollback_error}")

        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Consolidate messaging system")
    parser.add_argument(
        "--execute", action="store_true", help="Actually consolidate (default is dry-run)"
    )

    args = parser.parse_args()

    success = consolidate_messaging(dry_run=not args.execute)

    if success and not args.execute:
        print()
        print("✅ Dry run successful - ready to consolidate")


if __name__ == "__main__":
    main()
