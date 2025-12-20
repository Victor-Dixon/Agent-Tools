#!/usr/bin/env python3
"""
Add Typing Imports - Automated Fix
===================================

Automatically adds typing imports to Python files that are missing them.
Scans trading_robot, integrations, and tools directories.

Author: Agent-7 (Web Development Specialist)
"""

import re
from pathlib import Path
from typing import List, Tuple


def needs_typing_import(file_path: Path) -> bool:
    """Check if file needs typing import."""
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # Skip if already has typing import
        if re.search(r"^from typing import|^import typing", content, re.MULTILINE):
            return False
        
        # Skip __init__.py and test files
        if file_path.name == "__init__.py" or "test" in file_path.name.lower():
            return False
        
        # Skip if file is too small (likely empty or just comments)
        if len(content.strip()) < 50:
            return False
        
        # Check if file has function/class definitions that would benefit from typing
        has_functions = bool(re.search(r"def\s+\w+", content))
        has_classes = bool(re.search(r"class\s+\w+", content))
        
        return has_functions or has_classes
        
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return False


def add_typing_import(file_path: Path) -> bool:
    """Add typing import to file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # Find insertion point (after docstring or shebang, before other imports)
        lines = content.split("\n")
        insert_index = 0
        
        # Skip shebang
        if lines and lines[0].startswith("#!"):
            insert_index = 1
        
        # Skip encoding comment
        if insert_index < len(lines) and "coding" in lines[insert_index].lower():
            insert_index += 1
        
        # Skip docstring
        if insert_index < len(lines) and lines[insert_index].strip().startswith('"""'):
            insert_index += 1
            # Find end of docstring
            while insert_index < len(lines) and '"""' not in lines[insert_index]:
                insert_index += 1
            if insert_index < len(lines):
                insert_index += 1
        
        # Find first import or skip blank lines
        while insert_index < len(lines) and (
            lines[insert_index].strip() == "" or lines[insert_index].strip().startswith("#")
        ):
            insert_index += 1
        
        # Insert typing import
        typing_import = "from typing import Any, Dict, List, Optional, Tuple, Union\n"
        
        # Check if there are already imports
        if insert_index < len(lines) and "import" in lines[insert_index]:
            # Insert after existing imports
            while insert_index < len(lines) and (
                "import" in lines[insert_index] or lines[insert_index].strip() == ""
            ):
                insert_index += 1
            lines.insert(insert_index, typing_import)
        else:
            # Insert at current position
            if insert_index < len(lines) and lines[insert_index].strip() != "":
                lines.insert(insert_index, typing_import)
            else:
                lines.insert(insert_index, typing_import)
        
        # Write back
        new_content = "\n".join(lines)
        file_path.write_text(new_content, encoding="utf-8")
        return True
        
    except Exception as e:
        print(f"❌ Error adding typing import to {file_path}: {e}")
        return False


def scan_directory(directory: Path) -> List[Path]:
    """Scan directory for Python files needing typing imports."""
    files_to_fix = []
    
    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and virtual environments
        if "__pycache__" in str(py_file) or "venv" in str(py_file) or ".venv" in str(py_file):
            continue
        
        if needs_typing_import(py_file):
            files_to_fix.append(py_file)
    
    return files_to_fix


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    
    # Directories to scan
    directories = [
        project_root / "src" / "trading_robot",
        project_root / "src" / "integrations",
        project_root / "tools",
    ]
    
    print("🔍 Scanning for files missing typing imports...\n")
    
    all_files = []
    for directory in directories:
        if directory.exists():
            files = scan_directory(directory)
            all_files.extend(files)
            print(f"📁 {directory.name}: {len(files)} files need typing imports")
        else:
            print(f"⚠️  Directory not found: {directory}")
    
    print(f"\n📊 Total files to fix: {len(all_files)}\n")
    
    if not all_files:
        print("✅ No files need typing imports!")
        return
    
    # Ask for confirmation
    print("Files to fix:")
    for f in all_files[:20]:  # Show first 20
        print(f"  - {f.relative_to(project_root)}")
    if len(all_files) > 20:
        print(f"  ... and {len(all_files) - 20} more")
    
    print("\n⚠️  This will modify files. Continue? (y/n): ", end="")
    # For automation, default to 'n' - require explicit confirmation
    response = input().strip().lower()
    
    if response != "y":
        print("❌ Aborted.")
        return
    
    # Fix files
    print("\n🔧 Adding typing imports...\n")
    fixed = 0
    failed = 0
    
    for file_path in all_files:
        if add_typing_import(file_path):
            print(f"✅ Fixed: {file_path.relative_to(project_root)}")
            fixed += 1
        else:
            print(f"❌ Failed: {file_path.relative_to(project_root)}")
            failed += 1
    
    print(f"\n📊 Results:")
    print(f"  ✅ Fixed: {fixed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📁 Total: {len(all_files)}")


if __name__ == "__main__":
    main()




