#!/usr/bin/env python3
"""
Project Import Audit Tool
==========================

Systematically test all Python imports to identify broken components.

Author: Agent-7 - Repository Cloning Specialist
Purpose: Quarantine broken components for systematic swarm fixing
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, List

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_import(module_path: str) -> tuple[bool, str]:
    """
    Test if a module can be imported.
    
    Returns:
        (success: bool, error_message: str)
    """
    try:
        importlib.import_module(module_path)
        return (True, "")
    except Exception as e:
        return (False, str(e))


def file_to_module_path(file_path: Path, project_root: Path) -> str:
    """Convert file path to module import path."""
    relative = file_path.relative_to(project_root)
    module_path = str(relative.with_suffix('')).replace('\\', '.').replace('/', '.')
    return module_path


def audit_imports(base_path: str = 'src') -> Dict[str, List]:
    """
    Audit all imports in a directory.
    
    Returns:
        {
            'working': [(file, module_path), ...],
            'broken': [(file, module_path, error), ...]
        }
    """
    project_root = Path(__file__).parent.parent
    base = project_root / base_path
    
    working = []
    broken = []
    skipped = []
    
    # Find all Python files
    py_files = [
        f for f in base.rglob('*.py')
        if '__pycache__' not in str(f)
        and f.name != '__init__.py'
        and 'test_' not in f.name
        and f.stat().st_size > 0  # Skip empty files
    ]
    
    print(f"🔍 Auditing {len(py_files)} Python files in {base_path}/\n")
    
    for i, file in enumerate(py_files, 1):
        try:
            module_path = file_to_module_path(file, project_root)
            
            # Progress indicator
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(py_files)} files tested...")
            
            success, error = test_import(module_path)
            
            if success:
                working.append((str(file.relative_to(project_root)), module_path))
            else:
                broken.append((str(file.relative_to(project_root)), module_path, error))
                
        except Exception as e:
            skipped.append((str(file.relative_to(project_root)), str(e)))
    
    return {
        'working': working,
        'broken': broken,
        'skipped': skipped,
        'total': len(py_files)
    }


def main():
    """Run import audit and generate report."""
    print("🔍 PROJECT IMPORT AUDIT\n")
    print("=" * 60)
    
    results = audit_imports('src')
    
    print(f"\n\n📊 AUDIT RESULTS:")
    print(f"  Total files tested: {results['total']}")
    print(f"  ✅ Working: {len(results['working'])}")
    print(f"  ❌ Broken: {len(results['broken'])}")
    print(f"  ⚠️ Skipped: {len(results['skipped'])}")
    
    # Show broken imports
    if results['broken']:
        print(f"\n\n❌ BROKEN IMPORTS ({len(results['broken'])}):")
        print("=" * 60)
        for file, module, error in results['broken']:
            print(f"\n  File: {file}")
            print(f"  Module: {module}")
            print(f"  Error: {error[:100]}...")
    
    # Save to quarantine
    quarantine_dir = Path('quarantine')
    quarantine_dir.mkdir(exist_ok=True)
    
    report_file = quarantine_dir / 'BROKEN_IMPORTS.md'
    with open(report_file, 'w') as f:
        f.write("# 🔴 BROKEN IMPORTS REPORT\n\n")
        f.write(f"**Date:** 2025-10-13\n")
        f.write(f"**Total Tested:** {results['total']}\n")
        f.write(f"**Working:** {len(results['working'])}\n")
        f.write(f"**Broken:** {len(results['broken'])}\n\n")
        f.write("---\n\n")
        
        if results['broken']:
            f.write("## ❌ BROKEN IMPORTS\n\n")
            for i, (file, module, error) in enumerate(results['broken'], 1):
                f.write(f"### {i}. `{file}`\n\n")
                f.write(f"**Module:** `{module}`\n\n")
                f.write(f"**Error:**\n```\n{error}\n```\n\n")
                f.write("**Priority:** TBD\n\n")
                f.write("**Assigned To:** TBD\n\n")
                f.write("---\n\n")
    
    print(f"\n\n✅ Report saved to: {report_file}")
    print(f"\n🐝 WE ARE SWARM - Audit complete! ⚡")
    
    return 0 if len(results['broken']) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

