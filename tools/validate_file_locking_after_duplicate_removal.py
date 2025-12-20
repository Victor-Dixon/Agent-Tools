#!/usr/bin/env python3
"""
Validate File Locking System After Duplicate Removal
====================================================

Validates that the file_locking system works correctly after duplicate removal.
Batch 1 duplicate consolidation deleted: src/core/file_locking/operations/lock_operations.py
SSOT preserved: src/core/file_locking/file_locking_orchestrator.py

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def validate_imports() -> dict:
    """Validate that file_locking modules import correctly."""
    results = {
        "passed": [],
        "failed": [],
        "errors": []
    }

    modules_to_test = [
        "src.core.file_locking.file_locking_orchestrator",
        "src.core.file_locking.file_locking_manager",
        "src.core.file_locking.file_locking_engine",
        "src.core.file_locking.file_locking_models",
    ]

    for module_path in modules_to_test:
        try:
            __import__(module_path)
            results["passed"].append(module_path)
            print(f"✅ {module_path}")
        except ImportError as e:
            results["failed"].append(module_path)
            results["errors"].append(f"{module_path}: {str(e)}")
            print(f"❌ {module_path}: {str(e)}")
        except Exception as e:
            results["failed"].append(module_path)
            results["errors"].append(f"{module_path}: {str(e)}")
            print(f"⚠️  {module_path}: {str(e)}")

    return results


def validate_deleted_file() -> dict:
    """Validate that deleted duplicate file doesn't exist."""
    deleted_file = project_root / "src" / "core" / \
        "file_locking" / "operations" / "lock_operations.py"
    ssot_file = project_root / "src" / "core" / \
        "file_locking" / "file_locking_orchestrator.py"

    result = {
        "deleted_file_exists": deleted_file.exists(),
        "ssot_file_exists": ssot_file.exists(),
        "status": "PASS" if (not deleted_file.exists() and ssot_file.exists()) else "FAIL"
    }

    if deleted_file.exists():
        print(f"❌ Deleted file still exists: {deleted_file}")
    else:
        print(f"✅ Deleted file correctly removed: {deleted_file.name}")

    if ssot_file.exists():
        print(f"✅ SSOT file preserved: {ssot_file.name}")
    else:
        print(f"❌ SSOT file missing: {ssot_file.name}")

    return result


def main() -> int:
    """Main validation execution."""
    print("🔍 Validating File Locking System After Duplicate Removal")
    print("=" * 60)
    print()

    print("📋 Step 1: Validating deleted file removal")
    print("-" * 60)
    file_check = validate_deleted_file()
    print()

    print("📋 Step 2: Validating module imports")
    print("-" * 60)
    import_check = validate_imports()
    print()

    print("📊 Validation Summary")
    print("=" * 60)
    print(f"File Removal: {file_check['status']}")
    print(
        f"Module Imports: {len(import_check['passed'])}/{len(import_check['passed']) + len(import_check['failed'])} passed")

    if import_check["failed"]:
        print("\n❌ Failed Imports:")
        for error in import_check["errors"]:
            print(f"   - {error}")

    if file_check["status"] == "PASS" and not import_check["failed"]:
        print("\n✅ Validation PASSED - File locking system operational")
        return 0
    else:
        print("\n❌ Validation FAILED - Issues detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())

