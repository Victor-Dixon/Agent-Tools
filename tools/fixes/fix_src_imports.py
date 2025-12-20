#!/usr/bin/env python3
"""
Fix src. imports across the codebase
====================================

This script systematically fixes imports that start with 'src.'
by removing the unnecessary prefix when running from project root.
"""

import os
import re
from pathlib import Path


def fix_src_imports():
    """Fix all src. imports in the codebase."""
    project_root = Path(__file__).parent
    fixed_count = 0

    # Find all Python files
    for py_file in project_root.rglob("*.py"):
        # Skip files in venv and certain directories
        if any(skip in str(py_file) for skip in ["venv", "__pycache__", ".git"]):
            continue

        try:
            # Read the file
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for src. imports
            original_content = content
            lines = content.split('\n')
            modified_lines = []

            for line in lines:
                # Fix imports starting with 'from src.'
                line = re.sub(r'^(\s*)from src\.(.+)$', r'\1from \2', line)
                # Fix imports starting with 'import src.'
                line = re.sub(r'^(\s*)import src\.(.+)$', r'\1import \2', line)
                modified_lines.append(line)

            new_content = '\n'.join(modified_lines)

            # Only write if there were changes
            if new_content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                fixed_count += 1
                print(f"✅ Fixed {py_file}")

        except Exception as e:
            print(f"❌ Error processing {py_file}: {e}")

    print(f"\n🎉 Fixed {fixed_count} files with src. import issues")
    return fixed_count


if __name__ == "__main__":
    fix_src_imports()
