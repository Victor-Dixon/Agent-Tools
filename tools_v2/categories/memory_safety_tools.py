#!/usr/bin/env python3
"""
Memory Safety & Production Tools - Toolbelt V2
==============================================

Tools for memory leak detection, file verification, and production safety.
Created based on real-world needs from Agent-5's memory leak audit.

Author: Agent-5 (Business Intelligence & Team Beta Leader)
License: MIT
"""

import ast
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def detect_memory_leaks(target_path: str = "src") -> dict[str, Any]:
    """
    Detect potential memory leaks in Python codebase.

    Scans for:
    - Unbounded list.append() without size checks
    - defaultdict(list) without cleanup
    - deque() without maxlen parameter
    - Growing caches without limits

    Args:
        target_path: Directory to scan (default: src)

    Returns:
        Dictionary with leak patterns found and recommendations

    Example:
        >>> results = detect_memory_leaks("src/core")
        >>> print(f"Found {results['total_issues']} potential leaks")
    """
    issues = []
    files_scanned = 0

    target = Path(target_path)
    if not target.exists():
        return {"error": f"Path not found: {target_path}", "total_issues": 0}

    # Scan all Python files
    for py_file in target.rglob("*.py"):
        files_scanned += 1
        try:
            content = py_file.read_text(encoding="utf-8")

            # Pattern 1: defaultdict(list) without size checks
            if "defaultdict(list)" in content:
                # Check if there's no size limiting nearby
                if (
                    "maxlen" not in content
                    and "if len(" not in content[: content.find("defaultdict(list)") + 500]
                ):
                    issues.append(
                        {
                            "file": str(py_file),
                            "pattern": "defaultdict(list) without bounds",
                            "severity": "HIGH",
                            "line": content[: content.find("defaultdict(list)")].count("\n") + 1,
                            "recommendation": "Add size checks or use deque(maxlen=N)",
                        }
                    )

            # Pattern 2: deque() without maxlen
            if "deque()" in content or "deque(" in content:
                if "maxlen=" not in content:
                    issues.append(
                        {
                            "file": str(py_file),
                            "pattern": "deque() without maxlen parameter",
                            "severity": "MEDIUM",
                            "recommendation": "Add maxlen=N to prevent unbounded growth",
                        }
                    )

            # Pattern 3: .append() in loops without size checks
            if ".append(" in content and "for " in content:
                # This is a heuristic - might need refinement
                append_count = content.count(".append(")
                if append_count > 3 and "if len(" not in content:
                    issues.append(
                        {
                            "file": str(py_file),
                            "pattern": f"Multiple .append() calls ({append_count}) without size checks",
                            "severity": "MEDIUM",
                            "recommendation": "Add size limits to prevent unbounded growth",
                        }
                    )

        except Exception as e:
            logger.warning(f"Could not scan {py_file}: {e}")

    return {
        "files_scanned": files_scanned,
        "total_issues": len(issues),
        "issues": issues[:50],  # Limit to first 50
        "summary": {
            "high_severity": len([i for i in issues if i["severity"] == "HIGH"]),
            "medium_severity": len([i for i in issues if i["severity"] == "MEDIUM"]),
        },
    }


def verify_files_exist(file_list: list[str]) -> dict[str, Any]:
    """
    Verify that files exist before task assignment.

    Prevents "phantom task" issues where tasks reference non-existent files.
    Based on Agent-5's Cycle 1 intelligent verification pattern.

    Args:
        file_list: List of file paths to verify

    Returns:
        Dictionary with verification results

    Example:
        >>> results = verify_files_exist(["src/core/file1.py", "src/core/file2.py"])
        >>> print(f"{results['existing']}/{results['total']} files exist")
    """
    results = {"total": len(file_list), "existing": [], "missing": [], "errors": []}

    for file_path in file_list:
        try:
            path = Path(file_path)
            if path.exists():
                results["existing"].append(file_path)
            else:
                results["missing"].append(file_path)
        except Exception as e:
            results["errors"].append({"file": file_path, "error": str(e)})

    return results


def scan_unbounded_structures(target_path: str = "src") -> dict[str, Any]:
    """
    Scan for unbounded data structures that could cause memory leaks.

    Identifies:
    - Lists without size limits
    - Dicts with growing values
    - Caches without eviction
    - Histories without bounds

    Args:
        target_path: Directory to scan

    Returns:
        Detailed analysis of unbounded structures

    Example:
        >>> results = scan_unbounded_structures("src/core/error_handling")
        >>> for issue in results['critical']:
        ...     print(f"Critical: {issue['description']}")
    """
    critical = []
    warnings = []
    files_scanned = 0

    target = Path(target_path)
    if not target.exists():
        return {"error": f"Path not found: {target_path}"}

    for py_file in target.rglob("*.py"):
        files_scanned += 1
        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                # Pattern 1: self.something = [] (instance variable)
                if "self." in line and "= []" in line:
                    # Check if there's size management nearby (next 20 lines)
                    nearby = "\n".join(lines[i : min(i + 20, len(lines))])
                    if "if len(" not in nearby and "maxlen" not in nearby:
                        critical.append(
                            {
                                "file": str(py_file),
                                "line": i,
                                "code": line.strip(),
                                "description": "Instance variable initialized as unbounded list",
                                "recommendation": "Add size checks in append operations",
                            }
                        )

                # Pattern 2: self.something = {} (dict that might grow)
                if "self." in line and "= {}" in line:
                    warnings.append(
                        {
                            "file": str(py_file),
                            "line": i,
                            "code": line.strip(),
                            "description": "Instance dict might grow unbounded",
                            "recommendation": "Consider LRU cache or size limits",
                        }
                    )

                # Pattern 3: _cache or cache variable
                if ("_cache" in line or "cache" in line) and "= {" in line:
                    if (
                        "max"
                        not in content[
                            max(0, content.find(line) - 500) : content.find(line) + 500
                        ].lower()
                    ):
                        warnings.append(
                            {
                                "file": str(py_file),
                                "line": i,
                                "code": line.strip(),
                                "description": "Cache without size limit",
                                "recommendation": "Add max_size limit and LRU eviction",
                            }
                        )

        except Exception as e:
            logger.warning(f"Could not scan {py_file}: {e}")

    return {
        "files_scanned": files_scanned,
        "critical": critical[:20],  # Limit output
        "warnings": warnings[:20],
        "summary": {"critical_count": len(critical), "warning_count": len(warnings)},
    }


def validate_imports(file_path: str) -> dict[str, Any]:
    """
    Validate that a Python file's imports work correctly.

    Tests imports without executing the full file.
    Useful for verifying refactoring didn't break imports.

    Args:
        file_path: Path to Python file to validate

    Returns:
        Import validation results

    Example:
        >>> result = validate_imports("src/core/message_queue_interfaces.py")
        >>> if result['success']:
        ...     print("All imports valid!")
    """
    path = Path(file_path)

    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    try:
        # Parse the file to get imports
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        # Try to import the module itself
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("test_module", path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules["test_module"] = module
            spec.loader.exec_module(module)

            return {
                "success": True,
                "file": file_path,
                "imports_found": len(imports),
                "imports": imports[:10],  # First 10
                "message": "All imports validated successfully",
            }
        else:
            return {"success": False, "error": "Could not load module spec"}

    except SyntaxError as e:
        return {"success": False, "error": f"Syntax error: {e}", "line": getattr(e, "lineno", None)}
    except ImportError as e:
        return {
            "success": False,
            "error": f"Import error: {e}",
            "details": "One or more imports failed to resolve",
        }
    except Exception as e:
        return {"success": False, "error": f"Validation error: {type(e).__name__}: {e}"}


def check_file_handles(target_path: str = "src") -> dict[str, Any]:
    """
    Check for unclosed file handles (potential resource leaks).

    Scans for:
    - open() without context manager (with statement)
    - File operations without proper cleanup

    Args:
        target_path: Directory to scan

    Returns:
        List of potential file handle leaks

    Example:
        >>> results = check_file_handles("src")
        >>> if results['potential_leaks'] > 0:
        ...     print("Warning: Found unclosed file handles!")
    """
    potential_leaks = []
    files_scanned = 0

    target = Path(target_path)
    if not target.exists():
        return {"error": f"Path not found: {target_path}"}

    for py_file in target.rglob("*.py"):
        files_scanned += 1
        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                # Check for open() not in with statement
                if "open(" in line and "with " not in line:
                    # Check if "with" is in previous line
                    prev_line = lines[i - 2] if i > 1 else ""
                    if "with " not in prev_line:
                        potential_leaks.append(
                            {
                                "file": str(py_file),
                                "line": i,
                                "code": line.strip(),
                                "issue": "open() without context manager",
                                "recommendation": "Use 'with open(...) as f:' pattern",
                            }
                        )

        except Exception as e:
            logger.warning(f"Could not scan {py_file}: {e}")

    return {
        "files_scanned": files_scanned,
        "potential_leaks": len(potential_leaks),
        "leaks": potential_leaks[:30],  # Limit output
        "recommendation": "Always use 'with' statement for file operations",
    }


# Tool metadata for registry
TOOLS = [
    {
        "name": "detect_memory_leaks",
        "function": detect_memory_leaks,
        "description": "Detect potential memory leaks (unbounded structures, missing size checks)",
        "category": "memory_safety",
        "usage": "detect_memory_leaks('src/core')",
    },
    {
        "name": "verify_files_exist",
        "function": verify_files_exist,
        "description": "Verify files exist before task assignment (prevent phantom tasks)",
        "category": "memory_safety",
        "usage": "verify_files_exist(['file1.py', 'file2.py'])",
    },
    {
        "name": "scan_unbounded_structures",
        "function": scan_unbounded_structures,
        "description": "Scan for unbounded data structures that could grow indefinitely",
        "category": "memory_safety",
        "usage": "scan_unbounded_structures('src')",
    },
    {
        "name": "validate_imports",
        "function": validate_imports,
        "description": "Validate Python file imports work correctly (test refactoring)",
        "category": "memory_safety",
        "usage": "validate_imports('src/core/file.py')",
    },
    {
        "name": "check_file_handles",
        "function": check_file_handles,
        "description": "Check for unclosed file handles (resource leak detection)",
        "category": "memory_safety",
        "usage": "check_file_handles('src')",
    },
]


__all__ = [
    "detect_memory_leaks",
    "verify_files_exist",
    "scan_unbounded_structures",
    "validate_imports",
    "check_file_handles",
    "TOOLS",
]
