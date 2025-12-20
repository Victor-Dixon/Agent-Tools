#!/usr/bin/env python3
"""Clean up broken files with special characters in names."""
from pathlib import Path
import shutil

root = Path(".")
assets = Path("assets")
assets.mkdir(exist_ok=True)

# Try to find and delete broken files
broken_patterns = [
    "rc.services.messaging_cli",
    "t status",
    "tatus --short",
    ".FullName"
]

deleted = 0
for file in root.iterdir():
    if not file.is_file():
        continue
    
    name = file.name
    # Check if it matches any broken pattern
    for pattern in broken_patterns:
        if pattern in name:
            try:
                file.unlink()
                deleted += 1
                print(f"✅ Deleted: {name}")
            except Exception as e:
                print(f"❌ Error deleting {name}: {e}")

# Move theme zip
zip_file = root / "ariajet-theme.zip"
if zip_file.exists():
    try:
        shutil.move(str(zip_file), str(assets / "ariajet-theme.zip"))
        print("✅ Moved ariajet-theme.zip to assets/")
    except Exception as e:
        print(f"❌ Error moving zip: {e}")

print(f"\n✅ Cleaned up {deleted} broken files")

