#!/usr/bin/env python3
"""
SSOT Config Validator - Validates config_ssot usage and facade mapping
============================================================

<!-- SSOT Domain: qa -->

Validates that config_ssot is used correctly and facade/shims remain mapped
during config updates. Prevents SSOT violations in config consolidation.

USAGE:
    # Validate config_ssot usage in a file
    python tools/ssot_config_validator.py --file src/path/to/file.py
    
    # Validate config_ssot usage in a directory
    python tools/ssot_config_validator.py --dir src/services/
    
    # Check facade mapping integrity
    python tools/ssot_config_validator.py --check-facade
    
    # Generate report
    python tools/ssot_config_validator.py --file src/path/to/file.py --report

Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-01-27
V2 Compliant: Yes (<400 lines)
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent


class SSOTConfigValidator:
    """Validates config_ssot usage and facade mapping"""
    
    # Valid config_ssot imports
    VALID_SSOT_IMPORTS = [
        "from src.core.config_ssot import",
        "import src.core.config_ssot",
        "from src.core import config_ssot",
    ]
    
    # Deprecated config imports (should use config_ssot)
    DEPRECATED_IMPORTS = [
        "from src.core.config_core import",
        "from src.core.unified_config import",
        "from src.core.config_browser import",
        "from src.core.config_thresholds import",
        "from src.shared_utils.config import",
        "from src.services.config import",
    ]
    
    # Facade shim files (should remain mapped)
    FACADE_SHIMS = [
        "src/core/config_core.py",
        "src/core/unified_config.py",
        "src/core/config_browser.py",
        "src/core/config_thresholds.py",
        "src/shared_utils/config.py",
    ]
    
    def __init__(self):
        self.violations: List[Dict] = []
        self.warnings: List[Dict] = []
        self.valid_imports: List[Dict] = []
        self.facade_status: Dict[str, bool] = {}
        
    def validate_file(self, file_path: Path) -> Tuple[bool, List[Dict]]:
        """Validate config_ssot usage in a file"""
        if not file_path.exists():
            return False, [{"type": "error", "message": f"File not found: {file_path}"}]
        
        if not file_path.suffix == ".py":
            return False, [{"type": "warning", "message": f"Not a Python file: {file_path}"}]
        
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return False, [{"type": "error", "message": f"Syntax error: {e}"}]
        except Exception as e:
            return False, [{"type": "error", "message": f"Error reading file: {e}"}]
        
        issues = []
        
        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                import_str = self._get_import_string(node)
                if any(dep in import_str for dep in self.DEPRECATED_IMPORTS):
                    issues.append({
                        "type": "violation",
                        "severity": "high",
                        "message": f"Deprecated config import: {import_str}",
                        "line": node.lineno,
                        "file": str(file_path),
                        "recommendation": "Use 'from src.core.config_ssot import ...' instead"
                    })
                elif any(valid in import_str for valid in self.VALID_SSOT_IMPORTS):
                    self.valid_imports.append({
                        "file": str(file_path),
                        "line": node.lineno,
                        "import": import_str
                    })
        
        # Check for direct config access (should use config_ssot functions)
        # This is a simplified check - could be enhanced
        if "config_core" in content and "config_ssot" not in content:
            if file_path.name not in ["config_core.py", "config_ssot.py"]:
                issues.append({
                    "type": "warning",
                    "severity": "medium",
                    "message": "Possible direct config_core usage without config_ssot",
                    "line": 0,
                    "file": str(file_path),
                    "recommendation": "Verify config_ssot usage"
                })
        
        return len(issues) == 0, issues
    
    def _get_import_string(self, node: ast.ImportFrom) -> str:
        """Get import string from AST node"""
        module = node.module or ""
        names = ", ".join([alias.name for alias in node.names])
        return f"from {module} import {names}"
    
    def check_facade_mapping(self) -> Dict[str, bool]:
        """Check that facade shim files remain mapped to config_ssot"""
        facade_status = {}
        
        for shim_path in self.FACADE_SHIMS:
            full_path = PROJECT_ROOT / shim_path
            if not full_path.exists():
                facade_status[shim_path] = False
                self.warnings.append({
                    "type": "warning",
                    "message": f"Facade shim not found: {shim_path}",
                    "severity": "high"
                })
                continue
            
            try:
                content = full_path.read_text(encoding="utf-8")
                # Check if shim imports from config_ssot
                if "config_ssot" in content or "from src.core.config_ssot" in content:
                    facade_status[shim_path] = True
                else:
                    facade_status[shim_path] = False
                    self.warnings.append({
                        "type": "warning",
                        "message": f"Facade shim may not be mapped: {shim_path}",
                        "severity": "medium"
                    })
            except Exception as e:
                facade_status[shim_path] = False
                self.warnings.append({
                    "type": "error",
                    "message": f"Error checking facade shim {shim_path}: {e}",
                    "severity": "high"
                })
        
        self.facade_status = facade_status
        return facade_status
    
    def validate_directory(self, dir_path: Path) -> Tuple[bool, Dict]:
        """Validate config_ssot usage in a directory"""
        if not dir_path.exists() or not dir_path.is_dir():
            return False, {"error": f"Directory not found: {dir_path}"}
        
        results = {
            "files_checked": 0,
            "files_valid": 0,
            "files_with_violations": 0,
            "violations": [],
            "warnings": []
        }
        
        for py_file in dir_path.rglob("*.py"):
            results["files_checked"] += 1
            is_valid, issues = self.validate_file(py_file)
            
            if is_valid:
                results["files_valid"] += 1
            else:
                results["files_with_violations"] += 1
                for issue in issues:
                    if issue["type"] == "violation":
                        results["violations"].append(issue)
                    elif issue["type"] == "warning":
                        results["warnings"].append(issue)
        
        return results["files_with_violations"] == 0, results
    
    def generate_report(self, file_path: Path = None, dir_path: Path = None) -> str:
        """Generate validation report"""
        report_lines = [
            "=" * 60,
            "SSOT CONFIG VALIDATION REPORT",
            "=" * 60,
            ""
        ]
        
        if file_path:
            is_valid, issues = self.validate_file(file_path)
            report_lines.append(f"File: {file_path}")
            report_lines.append(f"Status: {'✅ VALID' if is_valid else '❌ VIOLATIONS FOUND'}")
            report_lines.append("")
            
            if issues:
                report_lines.append("Issues Found:")
                for issue in issues:
                    severity = issue.get("severity", "unknown")
                    report_lines.append(f"  [{severity.upper()}] Line {issue.get('line', '?')}: {issue.get('message', '')}")
                    if "recommendation" in issue:
                        report_lines.append(f"    → {issue['recommendation']}")
        
        elif dir_path:
            is_valid, results = self.validate_directory(dir_path)
            report_lines.append(f"Directory: {dir_path}")
            report_lines.append(f"Files Checked: {results.get('files_checked', 0)}")
            report_lines.append(f"Files Valid: {results.get('files_valid', 0)}")
            report_lines.append(f"Files with Violations: {results.get('files_with_violations', 0)}")
            report_lines.append("")
            
            if results.get("violations"):
                report_lines.append("Violations:")
                for violation in results["violations"][:10]:  # Limit to 10
                    report_lines.append(f"  {violation.get('file', '?')}:{violation.get('line', '?')} - {violation.get('message', '')}")
        
        # Facade mapping status
        facade_status = self.check_facade_mapping()
        report_lines.append("")
        report_lines.append("Facade Mapping Status:")
        for shim, status in facade_status.items():
            status_icon = "✅" if status else "❌"
            report_lines.append(f"  {status_icon} {shim}")
        
        # Valid imports found
        if self.valid_imports:
            report_lines.append("")
            report_lines.append(f"Valid config_ssot imports found: {len(self.valid_imports)}")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description="SSOT Config Validator")
    parser.add_argument("--file", type=str, help="File to validate")
    parser.add_argument("--dir", type=str, help="Directory to validate")
    parser.add_argument("--check-facade", action="store_true", help="Check facade mapping")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    
    args = parser.parse_args()
    
    validator = SSOTConfigValidator()
    
    if args.check_facade:
        facade_status = validator.check_facade_mapping()
        print("\n🔍 Facade Mapping Status:")
        for shim, status in facade_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {shim}")
        return 0 if all(facade_status.values()) else 1
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = PROJECT_ROOT / file_path
        
        is_valid, issues = validator.validate_file(file_path)
        
        if args.report:
            print(validator.generate_report(file_path=file_path))
        else:
            if is_valid:
                print(f"✅ {file_path}: VALID")
            else:
                print(f"❌ {file_path}: VIOLATIONS FOUND")
                for issue in issues:
                    print(f"  [{issue.get('severity', 'unknown').upper()}] {issue.get('message', '')}")
        
        return 0 if is_valid else 1
    
    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.is_absolute():
            dir_path = PROJECT_ROOT / dir_path
        
        is_valid, results = validator.validate_directory(dir_path)
        
        if args.report:
            print(validator.generate_report(dir_path=dir_path))
        else:
            print(f"Files Checked: {results.get('files_checked', 0)}")
            print(f"Files Valid: {results.get('files_valid', 0)}")
            print(f"Files with Violations: {results.get('files_with_violations', 0)}")
        
        return 0 if is_valid else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

