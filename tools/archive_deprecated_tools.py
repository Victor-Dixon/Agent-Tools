#!/usr/bin/env python3
"""
Archive Deprecated Tools - Consolidation Action
===============================================

Archives 176 deprecated tools to archive directory.
This is Priority 1 action from consolidation execution plan.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path(__file__).parent.parent
DEPRECATED_DIR = PROJECT_ROOT / "tools" / "deprecated"
ARCHIVE_DIR = PROJECT_ROOT / "archive" / "tools" / "deprecated"
ARCHIVE_MANIFEST = ARCHIVE_DIR / "ARCHIVE_MANIFEST.json"


def create_archive_structure():
    """Create archive directory structure."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created archive directory: {ARCHIVE_DIR}")


def get_deprecated_files() -> List[Path]:
    """Get all files in deprecated directory."""
    deprecated_files = []
    
    if not DEPRECATED_DIR.exists():
        print(f"⚠️  Deprecated directory not found: {DEPRECATED_DIR}")
        return []
    
    for file_path in DEPRECATED_DIR.rglob("*"):
        if file_path.is_file():
            deprecated_files.append(file_path)
    
    return deprecated_files


def archive_files(files: List[Path]) -> Dict:
    """Archive files to archive directory, preserving structure."""
    archived = []
    failed = []
    total_size = 0
    
    for file_path in files:
        try:
            # Get relative path from deprecated directory
            relative_path = file_path.relative_to(DEPRECATED_DIR)
            archive_path = ARCHIVE_DIR / relative_path
            
            # Create parent directories
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, archive_path)
            
            # Get file size
            file_size = file_path.stat().st_size
            total_size += file_size
            
            archived.append({
                "original_path": str(file_path.relative_to(PROJECT_ROOT)),
                "archive_path": str(archive_path.relative_to(PROJECT_ROOT)),
                "size_bytes": file_size,
                "archived_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            failed.append({
                "file": str(file_path.relative_to(PROJECT_ROOT)),
                "error": str(e)
            })
    
    return {
        "archived": archived,
        "failed": failed,
        "total_files": len(archived),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "archived_at": datetime.now().isoformat()
    }


def create_manifest(archive_info: Dict):
    """Create archive manifest file."""
    manifest_data = {
        "archive_info": archive_info,
        "source_directory": str(DEPRECATED_DIR.relative_to(PROJECT_ROOT)),
        "archive_directory": str(ARCHIVE_DIR.relative_to(PROJECT_ROOT)),
        "created_at": datetime.now().isoformat(),
        "note": "Deprecated tools archived as part of consolidation execution plan"
    }
    
    with open(ARCHIVE_MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)
    
    print(f"✅ Created archive manifest: {ARCHIVE_MANIFEST}")


def main():
    """Archive deprecated tools."""
    print("📦 Archiving deprecated tools...")
    print()
    
    # Create archive structure
    create_archive_structure()
    
    # Get deprecated files
    deprecated_files = get_deprecated_files()
    
    if not deprecated_files:
        print("⚠️  No deprecated files found to archive.")
        return
    
    print(f"📊 Found {len(deprecated_files)} files to archive")
    print()
    
    # Archive files
    print("📦 Archiving files...")
    archive_info = archive_files(deprecated_files)
    
    print()
    print("📊 Archive Summary:")
    print(f"   ✅ Archived: {archive_info['total_files']} files")
    print(f"   ❌ Failed: {len(archive_info['failed'])} files")
    print(f"   💾 Total Size: {archive_info['total_size_mb']} MB")
    print()
    
    if archive_info['failed']:
        print("⚠️  Failed Files:")
        for failure in archive_info['failed']:
            print(f"   - {failure['file']}: {failure['error']}")
        print()
    
    # Create manifest
    create_manifest(archive_info)
    
    print("✅ Archive complete!")
    print()
    print(f"📁 Archive Location: {ARCHIVE_DIR}")
    print(f"📄 Manifest: {ARCHIVE_MANIFEST}")
    print()
    print("💡 Next Steps:")
    print("   1. Verify archive contents")
    print("   2. Remove original deprecated directory (if confirmed safe)")
    print("   3. Update consolidation progress")


if __name__ == "__main__":
    main()

