#!/usr/bin/env python3
"""
Import Validator - Detect Missing Imports Before Runtime
Validates all imports in a file or directory to prevent runtime errors.

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use 'python -m tools_v2.toolbelt refactor.validate_imports' instead.
This file will be removed in future version.

Migrated to: tools_v2/categories/import_fix_tools.py → ImportValidatorTool
Registry: refactor.validate_imports

Author: Agent-4 (Captain)
Deprecated: 2025-01-27 (Agent-6 - V2 Tools Flattening)
"""

import warnings

warnings.warn(
    "⚠️ DEPRECATED: This tool has been migrated to tools_v2. "
    "Use 'python -m tools_v2.toolbelt refactor.validate_imports' instead. "
    "This file will be removed in future version.",
    DeprecationWarning,
    stacklevel=2
)

# Legacy compatibility - delegate to tools_v2
# For migration path, use: python -m tools_v2.toolbelt refactor.validate_imports

import sys
import ast
from pathlib import Path
from typing import List, Tuple

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))


def extract_imports(file_path: Path) -> List[Tuple[str, int]]:
    """Extract all import statements from a file."""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append((f"{module}.{alias.name}" if module else alias.name, node.lineno))
    except Exception as e:
        print(f"⚠️  Could not parse {file_path}: {e}")
    
    return imports


def validate_import(import_name: str) -> Tuple[bool, str]:
    """Validate if an import is available."""
    try:
        parts = import_name.split('.')
        module_name = parts[0]
        
        # Try to import the module
        __import__(module_name)
        return True, "✅ Valid"
    except ImportError as e:
        return False, f"❌ Missing: {e}"
    except Exception as e:
        return False, f"⚠️  Error: {e}"


def validate_file_imports(file_path: Path) -> dict:
    """Validate all imports in a file."""
    # Delegate to tools_v2 adapter if available
    try:
        from tools_v2.categories.import_fix_tools import ImportValidatorTool
        
        tool = ImportValidatorTool()
        result = tool.execute({"path": str(file_path)}, None)
        
        if result.success:
            broken = result.output.get("broken_imports", [])
            if broken:
                print(f"❌ {len(broken)} broken imports found in {file_path}")
                for imp in broken[:5]:
                    print(f"  - {imp.get('import')}: {imp.get('error')}")
            else:
                print(f"✅ All imports valid in {file_path}")
            return result.output
        else:
            print(f"❌ Error: {result.error_message}")
            return {"broken_imports": []}
    except ImportError:
        # Fallback to original implementation
        imports = extract_imports(file_path)
        results = {
            'file': str(file_path),
            'total_imports': len(imports),
            'valid': [],
            'invalid': []
        }
        
        for import_name, line_no in imports:
            is_valid, message = validate_import(import_name)
            
            if is_valid:
                results['valid'].append({
                    'import': import_name,
                    'line': line_no,
                    'status': message
                })
            else:
                results['invalid'].append({
                    'import': import_name,
                    'line': line_no,
                    'status': message
                })
        
        return results


def main():
    """Validate imports in specified file or directory."""
    
    if len(sys.argv) < 2:
        print("Usage: python captain_import_validator.py <file-or-directory>")
        print("\nExamples:")
        print("  python captain_import_validator.py src/core/messaging_pyautogui.py")
        print("  python captain_import_validator.py src/services/")
        print("\n⚠️  DEPRECATED: Use 'python -m tools_v2.toolbelt refactor.validate_imports' instead")
        return 1
    
    target = Path(sys.argv[1])
    
    if not target.exists():
        print(f"❌ Path not found: {target}")
        return 1
    
    # Collect files to validate
    files_to_check = []
    if target.is_file():
        files_to_check.append(target)
    else:
        files_to_check = list(target.rglob("*.py"))
    
    print(f"\n🔍 Validating imports in {len(files_to_check)} file(s)...\n")
    
    total_invalid = 0
    for file_path in files_to_check:
        results = validate_file_imports(file_path)
        invalid = results.get('invalid', [])
        total_invalid += len(invalid)
    
    if total_invalid == 0:
        print(f"\n✅ All imports valid across {len(files_to_check)} files!")
        return 0
    else:
        print(f"\n❌ {total_invalid} broken imports found across {len(files_to_check)} files")
        return 1


if __name__ == "__main__":
    sys.exit(main())
