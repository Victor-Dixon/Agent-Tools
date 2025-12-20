#!/usr/bin/env python3
"""
Import Chain Validator - Find Missing Imports
=============================================

<!-- SSOT Domain: qa -->

Validates import chains and identifies missing modules.
Based on the messaging_core import issue I fixed.

Author: Agent-8 (Quality Assurance) - Thread Experience Tool
Created: 2025-10-14
"""

import argparse
import importlib.util
import sys
from pathlib import Path


def test_import(module_path: str) -> dict:
    """
    Test if a module can be imported.
    
    Returns dict with:
    - success: bool
    - error: str or None
    - missing_modules: list of missing module names
    """
    result = {
        "success": False,
        "error": None,
        "missing_modules": []
    }
    
    try:
        # Try to import the module
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result["success"] = True
            
    except ModuleNotFoundError as e:
        result["error"] = str(e)
        # Extract missing module name
        missing = str(e).split("'")[1] if "'" in str(e) else "unknown"
        result["missing_modules"].append(missing)
        
    except ImportError as e:
        result["error"] = str(e)
        # Try to extract what failed to import
        error_str = str(e)
        if "cannot import name" in error_str:
            missing = error_str.split("'")[1] if "'" in error_str else "unknown"
            result["missing_modules"].append(missing)
    
    except Exception as e:
        result["error"] = f"Other error: {str(e)}"
    
    return result


def find_import_statements(file_path: Path) -> list[str]:
    """Find all import statements in a file."""
    imports = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(stripped)
    except:
        pass
    
    return imports


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import Chain Validator - Find missing imports"
    )
    parser.add_argument("file", help="Python file to validate")
    parser.add_argument("--fix-suggestions", action="store_true", help="Show fix suggestions")
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: {args.file} not found")
        return 1
    
    print(f"\n🔍 VALIDATING IMPORTS: {args.file}")
    print("="*80)
    
    # Test import
    result = test_import(str(file_path))
    
    if result["success"]:
        print("✅ ALL IMPORTS WORKING!")
        print("="*80 + "\n")
        return 0
    
    # Show error
    print(f"❌ IMPORT ERROR:")
    print(f"   {result['error']}")
    
    if result["missing_modules"]:
        print(f"\n🚨 MISSING MODULES ({len(result['missing_modules'])}):")
        for module in result["missing_modules"]:
            print(f"   - {module}")
    
    # Show current imports
    imports = find_import_statements(file_path)
    if imports:
        print(f"\n📋 CURRENT IMPORTS ({len(imports)}):")
        for imp in imports[:10]:  # Show first 10
            print(f"   {imp}")
        if len(imports) > 10:
            print(f"   ... and {len(imports) - 10} more")
    
    if args.fix_suggestions and result["missing_modules"]:
        print(f"\n💡 FIX SUGGESTIONS:")
        for module in result["missing_modules"]:
            print(f"\n   Missing: {module}")
            print(f"   1. Check if module exists: find . -name '{module}.py'")
            print(f"   2. Check __init__.py exports")
            print(f"   3. Consider creating the module if needed")
            print(f"   4. Update imports to use correct path")
    
    print("="*80 + "\n")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())

