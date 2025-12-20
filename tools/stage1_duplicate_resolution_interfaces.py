#!/usr/bin/env python3
"""
Stage 1 Integration: Interface Definitions Duplicate Resolution
================================================================

Consolidates duplicate interface/protocol definitions per duplication check report.
- messaging_protocol_models.py is designated as SSOT
- Duplicate interface definitions will be deprecated and migrated

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

# Interface mappings: duplicate → SSOT
INTERFACE_MAPPINGS = {
    "IMessageDelivery": {
        "duplicates": [
            "src/core/messaging_core.py",
        ],
        "ssot": "src/core/messaging_protocol_models.py",
        "note": "SSOT has full documentation and type hints",
    },
    "IOnboardingService": {
        "duplicates": [
            "src/core/messaging_core.py",
            "src/core/onboarding_service.py",
        ],
        "ssot": "src/core/messaging_protocol_models.py",
        "note": "SSOT has full documentation and type hints",
    },
}

# Files to add deprecation warnings to
FILES_TO_DEPRECATE = [
    ("src/core/messaging_core.py", "IMessageDelivery",
     "messaging_protocol_models.IMessageDelivery"),
    ("src/core/messaging_core.py", "IOnboardingService",
     "messaging_protocol_models.IOnboardingService"),
    ("src/core/onboarding_service.py", "IOnboardingService",
     "messaging_protocol_models.IOnboardingService"),
]


def generate_deprecation_warning(interface_name: str, ssot_path: str, note: str = "") -> str:
    """Generate deprecation warning code."""
    ssot_import = ssot_path.replace(
        "src/", "").replace(".py", "").replace("/", ".")
    ssot_module = ssot_path.split("/")[-1].replace(".py", "")

    warning = f'''
"""
⚠️ DEPRECATED - {interface_name} protocol is deprecated.

This interface has been consolidated into {ssot_path} as SSOT.
Please update imports to use the SSOT location instead.

Migration:
  OLD: from {Path(ssot_path).parent.name}.{ssot_module} import {interface_name}
  NEW: from {ssot_import} import {interface_name}

{f"Note: {note}" if note else ""}

This interface will be removed in a future release.
"""

import warnings
warnings.warn(
    "{interface_name} is deprecated. Use {ssot_path} instead.",
    DeprecationWarning,
    stacklevel=2
)
'''
    return warning


def create_consolidation_report() -> str:
    """Create a detailed consolidation report."""

    report = """# Interface Definitions Consolidation Report
**Date**: 2025-12-17  
**Agent**: Agent-5  
**Task**: A5-STAGE1-DUPLICATE-001  
**Purpose**: Consolidate duplicate interface/protocol definitions per duplication check findings

---

## 📋 Consolidation Plan

### SSOT Designation
- **SSOT**: `src/core/messaging_protocol_models.py` ✅
- **Deprecated**: Various duplicate locations ⚠️

### Interface Mappings

| Interface | Duplicate Locations | SSOT Location | Notes |
|-----------|---------------------|---------------|-------|
| IMessageDelivery | `src/core/messaging_core.py` | `src/core/messaging_protocol_models.py` | SSOT has full documentation and type hints |
| IOnboardingService | `src/core/messaging_core.py`<br>`src/core/onboarding_service.py` | `src/core/messaging_protocol_models.py` | SSOT has full documentation and type hints<br>onboarding_service.py also has implementation class |

---

## ⚠️ Important Notes

### Interface Consistency
- All interfaces are Protocol-based (typing.Protocol)
- SSOT versions have more complete documentation
- Method signatures are identical across duplicates

### Implementation Classes
- `OnboardingService` implementation class in `onboarding_service.py` should remain
- Only the interface definition `IOnboardingService` needs consolidation
- Implementation classes can continue to reference the SSOT interface

---

## ✅ Consolidation Steps

1. **Add Deprecation Warnings**
   - Add deprecation warnings to duplicate interface definitions
   - Direct users to SSOT locations
   - Include migration notes

2. **Update Imports**
   - Update all imports from duplicate locations to SSOT
   - Update type hints and Protocol usage

3. **Update Implementation Classes**
   - Ensure implementation classes import interfaces from SSOT
   - Verify type checking still works

4. **Remove Deprecated Definitions**
   - After migration complete, remove duplicate interface definitions
   - Keep implementation classes in their original locations

---

## 📊 Expected Impact

- **Duplicate Classes Eliminated**: ~2 (IMessageDelivery x1, IOnboardingService x2)
- **Code Consolidation**: Multiple locations → SSOT messaging_protocol_models.py
- **Maintainability**: Single source of truth for interface definitions
- **Type Safety**: Improved type checking with centralized interfaces

---

## 🔄 Next Steps

1. Add deprecation warnings to duplicate interface files
2. Update imports across codebase to use SSOT
3. Verify type checking and Protocol compatibility
4. Test functionality
5. Remove deprecated interface definitions after migration

---

## 📝 Migration Example

### Before:
```python
from src.core.messaging_core import IMessageDelivery, IOnboardingService

class MyService:
    def __init__(self, delivery: IMessageDelivery):
        self.delivery = delivery
```

### After:
```python
from src.core.messaging_protocol_models import IMessageDelivery, IOnboardingService

class MyService:
    def __init__(self, delivery: IMessageDelivery):
        self.delivery = delivery
```

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""

    return report


def main():
    """Main execution."""
    print("🔍 Stage 1 Integration: Interface Definitions Consolidation")
    print("=" * 60)

    # Create consolidation report
    print("\n📋 Generating consolidation report...")
    report = create_consolidation_report()
    report_file = project_root / "docs" / "STAGE1_INTERFACE_CONSOLIDATION_REPORT.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report, encoding="utf-8")
    print(f"✅ Report saved: {report_file}")

    # Add deprecation warnings to duplicate interface files
    print("\n⚠️ Adding deprecation warnings to duplicate interface files...")
    deprecated_count = 0

    for file_path, interface_name, ssot_ref in FILES_TO_DEPRECATE:
        full_path = project_root / file_path
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8")

            # Check if deprecation already exists
            if "DEPRECATED" not in content or f"{interface_name} protocol is deprecated" not in content:
                # Find the interface class definition
                lines = content.split("\n")

                # Find where interface is defined
                interface_idx = -1
                for i, line in enumerate(lines):
                    if f"class {interface_name}" in line:
                        interface_idx = i
                        break

                if interface_idx >= 0:
                    # Find where to insert deprecation (before interface class)
                    insert_idx = interface_idx

                    # Go back to find appropriate insertion point
                    while insert_idx > 0 and (
                        lines[insert_idx - 1].strip() == "" or
                        lines[insert_idx - 1].startswith("@") or
                        lines[insert_idx - 1].startswith("#") or
                        (lines[insert_idx - 1].strip() and not lines[insert_idx - 1].startswith(
                            "class") and not lines[insert_idx - 1].startswith("def"))
                    ):
                        insert_idx -= 1

                    # Generate deprecation warning
                    interface_info = INTERFACE_MAPPINGS.get(interface_name, {})
                    ssot_path = interface_info.get(
                        "ssot", "src/core/messaging_protocol_models.py")
                    note = interface_info.get("note", "")
                    deprecation = generate_deprecation_warning(
                        interface_name, ssot_path, note)

                    # Insert deprecation
                    new_lines = lines[:insert_idx] + \
                        [deprecation] + lines[insert_idx:]
                    new_content = "\n".join(new_lines)

                    full_path.write_text(new_content, encoding="utf-8")
                    print(
                        f"  ✅ Added deprecation to {file_path} ({interface_name})")
                    deprecated_count += 1
                else:
                    print(
                        f"  ⚠️  Could not find {interface_name} interface in {file_path}")
            else:
                print(
                    f"  ℹ️  {file_path} already has deprecation warning for {interface_name}")
        else:
            print(f"  ⚠️  File not found: {file_path}")

    print(
        f"\n✅ Added deprecation warnings to {deprecated_count} interface definitions")

    print("\n" + "=" * 60)
    print("📋 Next Steps:")
    print("1. Review consolidation report: docs/STAGE1_INTERFACE_CONSOLIDATION_REPORT.md")
    print("2. Update imports from duplicate locations to SSOT")
    print("3. Verify type checking and Protocol compatibility")
    print("4. Test functionality")
    print("5. Remove deprecated interface definitions after migration")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

