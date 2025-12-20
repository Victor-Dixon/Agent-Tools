#!/usr/bin/env python3
"""
Stage 1 Integration: Utility Classes Duplicate Resolution
==========================================================

Consolidates utilities/ and shared_utilities/ directories per duplication check report.
- shared_utilities/ is designated as SSOT
- utilities/ duplicates will be deprecated and migrated

Agent: Agent-5
Task: A5-STAGE1-DUPLICATE-001
Date: 2025-12-17
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Mapping: utilities/ → shared_utilities/ (SSOT)
UTILITY_MAPPING = {
    "cleanup_utilities.py": "cleanup_manager.py",
    "config_utilities.py": "configuration_manager_util.py",
    "error_utilities.py": "error_handler.py",
    "init_utilities.py": "initialization_manager.py",
    "result_utilities.py": "result_manager.py",
    "status_utilities.py": "status_manager.py",
}

UTILITIES_DIR = project_root / "src" / "core" / "utilities"
SHARED_UTILITIES_DIR = project_root / "src" / "core" / "shared_utilities"


def find_imports_using_utilities() -> Dict[str, List[str]]:
    """Find all files importing from utilities/ directory."""
    imports_map: Dict[str, List[str]] = {}

    for py_file in (project_root / "src").rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            if "utilities" in content:
                # Check for imports from utilities
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "from src.core.utilities" in line or "from .utilities" in line or "import utilities" in line:
                        rel_path = str(py_file.relative_to(project_root))
                        if rel_path not in imports_map:
                            imports_map[rel_path] = []
                        imports_map[rel_path].append(
                            f"Line {i}: {line.strip()}")
        except Exception as e:
            print(f"⚠️ Error reading {py_file}: {e}")

    return imports_map


def generate_deprecation_warnings() -> str:
    """Generate deprecation warning code to add to utilities/ files."""
    deprecation_template = '''
"""
⚠️ DEPRECATED - This module is deprecated.

This utility has been consolidated into shared_utilities/ as SSOT.
Please update imports to use shared_utilities instead.

Migration:
  OLD: from src.core.utilities.{old_module} import ...
  NEW: from src.core.shared_utilities.{new_module} import ...

This module will be removed in a future release.
"""

import warnings
warnings.warn(
    "utilities/ modules are deprecated. Use shared_utilities/ instead.",
    DeprecationWarning,
    stacklevel=2
)
'''
    return deprecation_template


def create_consolidation_report() -> str:
    """Create a detailed consolidation report."""
    imports_map = find_imports_using_utilities()

    report = """# Utility Classes Consolidation Report
**Date**: 2025-12-17  
**Agent**: Agent-5  
**Task**: A5-STAGE1-DUPLICATE-001  
**Purpose**: Consolidate utilities/ and shared_utilities/ per duplication check findings

---

## 📋 Consolidation Plan

### SSOT Designation
- **SSOT**: `src/core/shared_utilities/` ✅
- **Deprecated**: `src/core/utilities/` ⚠️

### File Mappings

| utilities/ (Deprecated) | shared_utilities/ (SSOT) |
|-------------------------|--------------------------|
| cleanup_utilities.py | cleanup_manager.py |
| config_utilities.py | configuration_manager_util.py |
| error_utilities.py | error_handler.py |
| init_utilities.py | initialization_manager.py |
| result_utilities.py | result_manager.py |
| status_utilities.py | status_manager.py |

---

## 🔍 Import Analysis

### Files Using utilities/ Imports

"""

    if imports_map:
        for file_path, import_lines in sorted(imports_map.items()):
            report += f"\n**{file_path}**\n"
            for line in import_lines:
                report += f"- {line}\n"
    else:
        report += "\n*No imports from utilities/ found.*\n"

    report += """
---

## ✅ Consolidation Steps

1. **Add Deprecation Warnings**
   - Add deprecation warnings to all utilities/ files
   - Direct users to shared_utilities/ alternatives

2. **Update Imports**
   - Update all imports from utilities/ to shared_utilities/
   - Use the mapping table above

3. **Verify Functionality**
   - Test that shared_utilities/ modules work correctly
   - Ensure no functionality is lost

4. **Remove Deprecated Files**
   - After migration complete, remove utilities/ directory
   - Update documentation

---

## 📊 Expected Impact

- **Duplicate Functions Eliminated**: ~6 (duplicate __init__ methods)
- **Code Consolidation**: utilities/ → shared_utilities/
- **Maintainability**: Single source of truth for utility classes

---

## 🔄 Next Steps

1. Run this script to generate deprecation warnings
2. Update all imports to use shared_utilities/
3. Test and verify functionality
4. Remove deprecated utilities/ directory

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""

    return report


def main():
    """Main execution."""
    print("🔍 Stage 1 Integration: Utility Classes Consolidation")
    print("=" * 60)

    # Create consolidation report
    print("\n📋 Generating consolidation report...")
    report = create_consolidation_report()
    report_file = project_root / "docs" / "STAGE1_UTILITY_CONSOLIDATION_REPORT.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report, encoding="utf-8")
    print(f"✅ Report saved: {report_file}")

    # Generate deprecation warnings for utilities/ files
    print("\n⚠️ Generating deprecation warnings...")
    deprecation_code = generate_deprecation_warnings()

    deprecated_count = 0
    for old_file, new_file in UTILITY_MAPPING.items():
        old_path = UTILITIES_DIR / old_file
        if old_path.exists():
            # Read existing content
            content = old_path.read_text(encoding="utf-8")

            # Add deprecation warning at the top (if not already present)
            if "DEPRECATED" not in content:
                new_content = deprecation_code + "\n" + content
                old_path.write_text(new_content, encoding="utf-8")
                print(f"  ✅ Added deprecation to {old_file}")
                deprecated_count += 1
            else:
                print(f"  ℹ️  {old_file} already has deprecation warning")

    print(f"\n✅ Added deprecation warnings to {deprecated_count} files")

    print("\n" + "=" * 60)
    print("📋 Next Steps:")
    print("1. Review consolidation report: docs/STAGE1_UTILITY_CONSOLIDATION_REPORT.md")
    print("2. Update imports from utilities/ to shared_utilities/")
    print("3. Test functionality")
    print("4. Remove deprecated utilities/ directory after migration")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

