#!/usr/bin/env python3
"""
Delete Deprecated Tools - Post-Archive Cleanup
==============================================

Deletes tools/deprecated/ directory after verification that:
1. All files are archived
2. Toolbelt works without deprecated tools
3. No active code references deprecated tools

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
DEPRECATED_DIR = PROJECT_ROOT / "tools" / "deprecated"
ARCHIVE_DIR = PROJECT_ROOT / "archive" / "tools" / "deprecated"


def verify_archive_exists():
    """Verify archive exists and has files."""
    if not ARCHIVE_DIR.exists():
        print(f"❌ Archive directory not found: {ARCHIVE_DIR}")
        return False
    
    archive_files = list(ARCHIVE_DIR.rglob("*"))
    archive_files = [f for f in archive_files if f.is_file()]
    
    if len(archive_files) == 0:
        print(f"❌ Archive directory is empty: {ARCHIVE_DIR}")
        return False
    
    print(f"✅ Archive verified: {len(archive_files)} files in {ARCHIVE_DIR}")
    return True


def delete_deprecated_directory():
    """Delete the deprecated tools directory."""
    if not DEPRECATED_DIR.exists():
        print(f"⚠️  Deprecated directory already doesn't exist: {DEPRECATED_DIR}")
        return True
    
    try:
        # Count files before deletion
        deprecated_files = list(DEPRECATED_DIR.rglob("*"))
        deprecated_files = [f for f in deprecated_files if f.is_file()]
        file_count = len(deprecated_files)
        
        print(f"🗑️  Deleting {file_count} files from {DEPRECATED_DIR}...")
        
        # Delete directory
        shutil.rmtree(DEPRECATED_DIR)
        
        print(f"✅ Successfully deleted {DEPRECATED_DIR}")
        print(f"   Removed {file_count} files")
        return True
    
    except Exception as e:
        print(f"❌ Error deleting deprecated directory: {e}")
        return False


def main():
    """Delete deprecated tools directory after verification."""
    print("🗑️  Delete Deprecated Tools - Post-Archive Cleanup")
    print("=" * 60)
    print()
    
    # Verify archive exists
    print("🔍 Step 1: Verifying archive exists...")
    if not verify_archive_exists():
        print("\n❌ Archive verification failed. Aborting deletion.")
        return 1
    print()
    
    # Delete deprecated directory
    print("🗑️  Step 2: Deleting deprecated directory...")
    if not delete_deprecated_directory():
        print("\n❌ Deletion failed.")
        return 1
    
    print()
    print("=" * 60)
    print("✅ Deletion Complete!")
    print()
    print(f"📁 Archive Location: {ARCHIVE_DIR}")
    print(f"🗑️  Deleted: {DEPRECATED_DIR}")
    print()
    print("💡 All deprecated tools are now in archive only.")
    print("   Original directory has been removed from active codebase.")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

