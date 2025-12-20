#!/usr/bin/env python3
"""
Stage 1 Integration: Model Enums Duplicate Resolution
======================================================

Consolidates duplicate model enum classes per duplication check report.
- coordinator_models.py / coordination_models.py designated as SSOT
- Duplicate enum classes will be deprecated and migrated

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

# Model enum mappings: duplicate → SSOT
MODEL_ENUM_MAPPINGS = {
    "TaskStatus": {
        "duplicates": [
            "src/services/contract_system/models.py",
            "src/core/managers/execution/execution_operations.py",
        ],
        "ssot": "src/core/coordination/swarm/coordination_models.py",
        "note": "SSOT has: PENDING, IN_PROGRESS, COMPLETED, FAILED",
    },
    "Priority": {
        "duplicates": [
            "src/core/intelligent_context/unified_intelligent_context/models.py",
        ],
        "ssot": "src/core/coordination/swarm/coordination_models.py",
        "note": "SSOT has TaskPriority (LOW, MEDIUM, HIGH, CRITICAL) - use TaskPriority or alias",
    },
    "CoordinationStrategy": {
        "duplicates": [
            "src/workflows/models.py",
        ],
        "ssot": "src/core/coordination/swarm/coordination_models.py",
        "note": "SSOT has: COLLABORATIVE, INDEPENDENT, HIERARCHICAL - different from workflows version",
    },
}

# Files to add deprecation warnings to
FILES_TO_DEPRECATE = [
    ("src/services/contract_system/models.py",
     "TaskStatus", "coordination_models.TaskStatus"),
    ("src/core/managers/execution/execution_operations.py",
     "TaskStatus", "coordination_models.TaskStatus"),
    ("src/core/intelligent_context/unified_intelligent_context/models.py",
     "Priority", "coordination_models.TaskPriority"),
    ("src/workflows/models.py", "CoordinationStrategy",
     "coordination_models.CoordinationStrategy"),
]


def generate_deprecation_warning(class_name: str, ssot_path: str, note: str = "") -> str:
    """Generate deprecation warning code."""
    ssot_import = ssot_path.replace(
        "src/", "").replace(".py", "").replace("/", ".")
    ssot_module = ssot_path.split("/")[-1].replace(".py", "")

    warning = f'''
"""
⚠️ DEPRECATED - {class_name} enum is deprecated.

This enum has been consolidated into {ssot_path} as SSOT.
Please update imports to use the SSOT location instead.

Migration:
  OLD: from {Path(ssot_path).parent.name}.{ssot_module} import {class_name}
  NEW: from {ssot_import} import {class_name}

{f"Note: {note}" if note else ""}

This enum will be removed in a future release.
"""

import warnings
warnings.warn(
    "{class_name} is deprecated. Use {ssot_path} instead.",
    DeprecationWarning,
    stacklevel=2
)
'''
    return warning


def create_consolidation_report() -> str:
    """Create a detailed consolidation report."""

    report = """# Model Enums Consolidation Report
**Date**: 2025-12-17  
**Agent**: Agent-5  
**Task**: A5-STAGE1-DUPLICATE-001  
**Purpose**: Consolidate duplicate model enum classes per duplication check findings

---

## 📋 Consolidation Plan

### SSOT Designation
- **SSOT**: `src/core/coordination/swarm/coordination_models.py` ✅
- **Deprecated**: Various duplicate locations ⚠️

### Enum Mappings

| Enum Class | Duplicate Locations | SSOT Location | Notes |
|------------|---------------------|---------------|-------|
| TaskStatus | `src/services/contract_system/models.py`<br>`src/core/managers/execution/execution_operations.py` | `src/core/coordination/swarm/coordination_models.py` | SSOT: PENDING, IN_PROGRESS, COMPLETED, FAILED<br>Duplicates may have additional values (CANCELLED, RUNNING) |
| Priority | `src/core/intelligent_context/unified_intelligent_context/models.py` | `src/core/coordination/swarm/coordination_models.py` | SSOT: TaskPriority (LOW, MEDIUM, HIGH, CRITICAL)<br>Use TaskPriority or create alias |
| CoordinationStrategy | `src/workflows/models.py` | `src/core/coordination/swarm/coordination_models.py` | SSOT: COLLABORATIVE, INDEPENDENT, HIERARCHICAL<br>Workflows has different values (PARALLEL, SEQUENTIAL, etc.) - may need migration strategy |

---

## ⚠️ Important Notes

### TaskStatus Differences
- **SSOT**: PENDING, IN_PROGRESS, COMPLETED, FAILED
- **contract_system**: Also has CANCELLED
- **execution_operations**: Has RUNNING instead of IN_PROGRESS, also has CANCELLED

**Migration Strategy**: Map RUNNING → IN_PROGRESS, handle CANCELLED separately or add to SSOT if needed.

### Priority Differences
- **SSOT**: TaskPriority (LOW, MEDIUM, HIGH, CRITICAL)
- **unified_intelligent_context**: Priority (LOW, MEDIUM, HIGH, CRITICAL) - same values, different name

**Migration Strategy**: Simple rename/alias to TaskPriority.

### CoordinationStrategy Differences
- **SSOT**: COLLABORATIVE, INDEPENDENT, HIERARCHICAL
- **workflows**: PARALLEL, SEQUENTIAL, DECISION_TREE, AUTONOMOUS

**Migration Strategy**: These represent different concepts. May need to:
1. Keep both with different names
2. Create mapping between them
3. Expand SSOT to include both sets

---

## ✅ Consolidation Steps

1. **Add Deprecation Warnings**
   - Add deprecation warnings to duplicate enum files
   - Direct users to SSOT locations
   - Include migration notes

2. **Verify Enum Compatibility**
   - Check if duplicate enums have additional values needed in SSOT
   - Determine if SSOT needs expansion or if values can be mapped

3. **Update Imports**
   - Update all imports from duplicate locations to SSOT
   - Handle value mapping where necessary

4. **Create Migration Guide**
   - Document value mappings
   - Provide code examples for migration

5. **Remove Deprecated Files**
   - After migration complete, remove duplicate enum definitions
   - Update documentation

---

## 📊 Expected Impact

- **Duplicate Classes Eliminated**: ~5 (TaskStatus x2, Priority x1, CoordinationStrategy x1, plus related)
- **Code Consolidation**: Multiple locations → SSOT coordination models
- **Maintainability**: Single source of truth for model enums

---

## 🔄 Next Steps

1. Review enum value differences between duplicates and SSOT
2. Determine if SSOT needs expansion or if mapping is sufficient
3. Add deprecation warnings to duplicate enum files
4. Create value mapping documentation
5. Update imports across codebase
6. Test functionality
7. Remove deprecated enum definitions after migration

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""

    return report


def main():
    """Main execution."""
    print("🔍 Stage 1 Integration: Model Enums Consolidation")
    print("=" * 60)

    # Create consolidation report
    print("\n📋 Generating consolidation report...")
    report = create_consolidation_report()
    report_file = project_root / "docs" / \
        "STAGE1_MODEL_ENUMS_CONSOLIDATION_REPORT.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report, encoding="utf-8")
    print(f"✅ Report saved: {report_file}")

    # Add deprecation warnings to duplicate enum files
    print("\n⚠️ Adding deprecation warnings to duplicate enum files...")
    deprecated_count = 0

    for file_path, class_name, ssot_ref in FILES_TO_DEPRECATE:
        full_path = project_root / file_path
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8")

            # Check if deprecation already exists
            if "DEPRECATED" not in content or f"{class_name} enum is deprecated" not in content:
                # Find the enum class definition
                lines = content.split("\n")

                # Find where enum is defined
                enum_idx = -1
                for i, line in enumerate(lines):
                    if f"class {class_name}" in line or f"{class_name}(Enum)" in line:
                        enum_idx = i
                        break

                if enum_idx >= 0:
                    # Find where to insert deprecation (before enum class, after previous class/docstring)
                    insert_idx = enum_idx

                    # Go back to find appropriate insertion point (after previous class/import)
                    while insert_idx > 0 and (
                        lines[insert_idx - 1].strip() == "" or
                        lines[insert_idx - 1].startswith("@") or
                        lines[insert_idx - 1].startswith("#") or
                        (lines[insert_idx - 1].strip() and not lines[insert_idx - 1].startswith(
                            "class") and not lines[insert_idx - 1].startswith("def"))
                    ):
                        insert_idx -= 1

                    # Generate deprecation warning
                    enum_info = MODEL_ENUM_MAPPINGS.get(class_name, {})
                    ssot_path = enum_info.get(
                        "ssot", "src/core/coordination/swarm/coordination_models.py")
                    note = enum_info.get("note", "")
                    deprecation = generate_deprecation_warning(
                        class_name, ssot_path, note)

                    # Insert deprecation
                    new_lines = lines[:insert_idx] + \
                        [deprecation] + lines[insert_idx:]
                    new_content = "\n".join(new_lines)

                    full_path.write_text(new_content, encoding="utf-8")
                    print(
                        f"  ✅ Added deprecation to {file_path} ({class_name})")
                    deprecated_count += 1
                else:
                    print(
                        f"  ⚠️  Could not find {class_name} enum in {file_path}")
            else:
                print(
                    f"  ℹ️  {file_path} already has deprecation warning for {class_name}")
        else:
            print(f"  ⚠️  File not found: {file_path}")

    print(
        f"\n✅ Added deprecation warnings to {deprecated_count} enum definitions")

    print("\n" + "=" * 60)
    print("📋 Next Steps:")
    print("1. Review consolidation report: docs/STAGE1_MODEL_ENUMS_CONSOLIDATION_REPORT.md")
    print("2. Review enum value differences and determine migration strategy")
    print("3. Update imports from duplicate locations to SSOT")
    print("4. Handle value mapping where necessary")
    print("5. Test functionality")
    print("6. Remove deprecated enum definitions after migration")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

