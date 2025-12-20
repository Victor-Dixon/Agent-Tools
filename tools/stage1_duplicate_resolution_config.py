#!/usr/bin/env python3
"""
Stage 1 Integration: Configuration Classes Duplicate Resolution
================================================================

Consolidates duplicate configuration classes per duplication check report.
- config_dataclasses.py is designated as SSOT
- Duplicate config classes will be deprecated and migrated

Agent: Agent-5
Task: A5-STAGE1-DUPLICATE-001
Date: 2025-12-17
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Configuration class mappings: duplicate → SSOT
CONFIG_MAPPINGS = {
    "BrowserConfig": {
        "duplicates": [
            "src/core/config_browser.py",
            "src/infrastructure/browser/browser_models.py",
        ],
        "ssot": "src/core/config/config_dataclasses.py",
    },
    "ThresholdConfig": {
        "duplicates": [
            "src/core/config_thresholds.py",
        ],
        "ssot": "src/core/config/config_dataclasses.py",
    },
    "TimeoutConstants": {
        "duplicates": [
            "src/core/performance/coordination_performance_monitor.py",
        ],
        "ssot": "src/core/config/timeout_constants.py",
    },
}

# Files to add deprecation warnings to
FILES_TO_DEPRECATE = [
    ("src/core/config_browser.py", "BrowserConfig",
     "config_dataclasses.BrowserConfig"),
    ("src/infrastructure/browser/browser_models.py",
     "BrowserConfig", "config_dataclasses.BrowserConfig"),
    ("src/core/config_thresholds.py", "ThresholdConfig",
     "config_dataclasses.ThresholdConfig"),
]


def generate_deprecation_warning(class_name: str, ssot_path: str) -> str:
    """Generate deprecation warning code."""
    ssot_import = ssot_path.replace(
        "src/", "").replace(".py", "").replace("/", ".")
    return f'''
"""
⚠️ DEPRECATED - {class_name} is deprecated.

This class has been consolidated into {ssot_path} as SSOT.
Please update imports to use the SSOT location instead.

Migration:
  OLD: from {Path(ssot_path).parent.name}.{Path(ssot_path).stem} import {class_name}
  NEW: from {ssot_import} import {class_name}

This module/class will be removed in a future release.
"""

import warnings
warnings.warn(
    "{class_name} is deprecated. Use {ssot_path} instead.",
    DeprecationWarning,
    stacklevel=2
)
'''


def find_imports_using_configs() -> Dict[str, List[str]]:
    """Find all files importing duplicate config classes."""
    imports_map: Dict[str, List[str]] = {}

    for config_class, info in CONFIG_MAPPINGS.items():
        for dup_file in info["duplicates"]:
            dup_path = project_root / dup_file
            if dup_path.exists():
                module_name = dup_path.stem
                # Search for imports of this module
                for py_file in (project_root / "src").rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding="utf-8")
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if (
                                f"from {module_name}" in line
                                or f"import {module_name}" in line
                                or f"from .{module_name}" in line
                            ) and config_class in content:
                                rel_path = str(
                                    py_file.relative_to(project_root))
                                if rel_path not in imports_map:
                                    imports_map[rel_path] = []
                                imports_map[rel_path].append(
                                    f"Line {i}: {line.strip()}")
                    except Exception as e:
                        pass  # Skip files that can't be read

    return imports_map


def create_consolidation_report() -> str:
    """Create a detailed consolidation report."""
    imports_map = find_imports_using_configs()

    report = """# Configuration Classes Consolidation Report
**Date**: 2025-12-17  
**Agent**: Agent-5  
**Task**: A5-STAGE1-DUPLICATE-001  
**Purpose**: Consolidate duplicate configuration classes per duplication check findings

---

## 📋 Consolidation Plan

### SSOT Designation
- **SSOT**: `src/core/config/config_dataclasses.py` ✅ (for BrowserConfig, ThresholdConfig)
- **SSOT**: `src/core/config/timeout_constants.py` ✅ (for TimeoutConstants)
- **Deprecated**: Various duplicate locations ⚠️

### Class Mappings

| Config Class | Duplicate Locations | SSOT Location |
|--------------|---------------------|---------------|
| BrowserConfig | `src/core/config_browser.py`<br>`src/infrastructure/browser/browser_models.py` | `src/core/config/config_dataclasses.py` |
| ThresholdConfig | `src/core/config_thresholds.py` | `src/core/config/config_dataclasses.py` |
| TimeoutConstants | `src/core/performance/coordination_performance_monitor.py` | `src/core/config/timeout_constants.py` |

---

## 🔍 Import Analysis

### Files Using Duplicate Config Imports

"""

    if imports_map:
        for file_path, import_lines in sorted(imports_map.items()):
            report += f"\n**{file_path}**\n"
            for line in import_lines:
                report += f"- {line}\n"
    else:
        report += "\n*No imports from duplicate config locations found.*\n"

    report += """
---

## ✅ Consolidation Steps

1. **Add Deprecation Warnings**
   - Add deprecation warnings to duplicate config class files
   - Direct users to SSOT locations

2. **Update Imports**
   - Update all imports from duplicate locations to SSOT
   - Use the mapping table above

3. **Verify Functionality**
   - Test that SSOT config classes work correctly
   - Ensure no functionality is lost
   - Check for API differences between duplicates

4. **Remove Deprecated Files**
   - After migration complete, remove or consolidate duplicate files
   - Update documentation

---

## 📊 Expected Impact

- **Duplicate Classes Eliminated**: ~3 (BrowserConfig, ThresholdConfig, TimeoutConstants)
- **Code Consolidation**: Multiple locations → SSOT config files
- **Maintainability**: Single source of truth for configuration classes

---

## 🔄 Next Steps

1. Review duplicate config class implementations
2. Ensure SSOT versions have all needed functionality
3. Add deprecation warnings to duplicate files
4. Update imports across codebase
5. Test and verify functionality
6. Remove deprecated files after migration

---

## ⚠️ Notes

- `BrowserConfig` appears in 3 locations with potentially different APIs
- Need to verify all functionality is preserved in SSOT version
- Some duplicates may have additional properties/methods to migrate

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""

    return report


def main():
    """Main execution."""
    print("🔍 Stage 1 Integration: Configuration Classes Consolidation")
    print("=" * 60)

    # Create consolidation report
    print("\n📋 Generating consolidation report...")
    report = create_consolidation_report()
    report_file = project_root / "docs" / "STAGE1_CONFIG_CONSOLIDATION_REPORT.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report, encoding="utf-8")
    print(f"✅ Report saved: {report_file}")

    # Add deprecation warnings to duplicate files
    print("\n⚠️ Adding deprecation warnings to duplicate config files...")
    deprecated_count = 0

    for file_path, class_name, ssot_ref in FILES_TO_DEPRECATE:
        full_path = project_root / file_path
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8")

            # Check if deprecation already exists
            if "DEPRECATED" not in content or f"{class_name} is deprecated" not in content:
                # Find where to insert deprecation (after module docstring or at top)
                lines = content.split("\n")
                insert_idx = 0

                # Skip shebang and encoding comments
                if lines and lines[0].startswith("#!"):
                    insert_idx = 1
                while insert_idx < len(lines) and (
                    lines[insert_idx].startswith("#") or
                    lines[insert_idx].startswith('"""') or
                    lines[insert_idx].strip() == ""
                ):
                    if lines[insert_idx].startswith('"""'):
                        # Find end of docstring
                        insert_idx += 1
                        while insert_idx < len(lines) and not lines[insert_idx].strip().endswith('"""'):
                            insert_idx += 1
                        insert_idx += 1
                        break
                    insert_idx += 1

                # Generate deprecation warning
                ssot_path = CONFIG_MAPPINGS[class_name]["ssot"]
                deprecation = generate_deprecation_warning(
                    class_name, ssot_path)

                # Insert deprecation
                new_lines = lines[:insert_idx] + \
                    [deprecation] + lines[insert_idx:]
                new_content = "\n".join(new_lines)

                full_path.write_text(new_content, encoding="utf-8")
                print(f"  ✅ Added deprecation to {file_path} ({class_name})")
                deprecated_count += 1
            else:
                print(f"  ℹ️  {file_path} already has deprecation warning")

    print(f"\n✅ Added deprecation warnings to {deprecated_count} files")

    print("\n" + "=" * 60)
    print("📋 Next Steps:")
    print("1. Review consolidation report: docs/STAGE1_CONFIG_CONSOLIDATION_REPORT.md")
    print("2. Verify SSOT config classes have all needed functionality")
    print("3. Update imports from duplicate locations to SSOT")
    print("4. Test functionality")
    print("5. Remove deprecated files after migration complete")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

