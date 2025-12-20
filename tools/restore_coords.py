#!/usr/bin/env python3
"""Restore cursor_agent_coords.json from archive."""
from pathlib import Path
import shutil

archive = Path("docs/archive/root_cleanup_2025-12-14/cursor_agent_coords.json")
root = Path("cursor_agent_coords.json")

if archive.exists():
    shutil.copy(archive, root)
    print("✅ Restored cursor_agent_coords.json")
else:
    print("❌ File not in archive - checking if it exists elsewhere...")
    # Try to find it
    for path in Path(".").rglob("cursor_agent_coords.json"):
        if path != root:
            shutil.copy(path, root)
            print(f"✅ Restored from {path}")
            break
    else:
        print("❌ File not found anywhere")

