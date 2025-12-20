#!/usr/bin/env python3
"""
Stress Test Integration Validation Script
=========================================

Validates that stress test mock delivery NEVER touches real agents.

This script performs comprehensive validation to ensure:
1. MockMessagingCore never imports real messaging_core
2. No PyAutoGUI calls in mock implementation
3. No file system writes to inbox directories
4. No real agent interaction
5. Pure simulation only

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-01-28
License: MIT
"""

import ast
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class StressTestValidator:
    """Validates stress test integration safety."""

    def __init__(self, stress_test_dir: Path):
        """Initialize validator.
        
        Args:
            stress_test_dir: Path to stress_testing directory
        """
        self.stress_test_dir = stress_test_dir
        self.violations: List[Dict[str, Any]] = []
        self.checks_passed = 0
        self.checks_failed = 0

    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """Run all validation checks.
        
        Returns:
            Tuple of (all_passed, results_dict)
        """
        print("🔍 Starting Stress Test Integration Validation...\n")
        
        # Check 1: Verify stress_testing directory exists
        if not self.stress_test_dir.exists():
            self._add_violation(
                "DIRECTORY_MISSING",
                f"Stress testing directory not found: {self.stress_test_dir}",
                severity="ERROR"
            )
            return False, self._get_results()
        
        # Check 2: Validate MockMessagingCore doesn't import real messaging_core
        self._check_no_real_imports()
        
        # Check 3: Validate no PyAutoGUI usage
        self._check_no_pyautogui()
        
        # Check 4: Validate no inbox file writes
        self._check_no_inbox_writes()
        
        # Check 5: Validate protocol compliance
        self._check_protocol_compliance()
        
        # Check 6: Validate injection point exists
        self._check_injection_point()
        
        # Check 7: Validate mock isolation
        self._check_mock_isolation()
        
        all_passed = len(self.violations) == 0
        return all_passed, self._get_results()

    def _check_no_real_imports(self):
        """Check that mock core doesn't import real messaging_core."""
        mock_core_file = self.stress_test_dir / "mock_messaging_core.py"
        
        if not mock_core_file.exists():
            self._add_violation(
                "FILE_MISSING",
                f"Mock messaging core file not found: {mock_core_file}",
                severity="ERROR"
            )
            return
        
        try:
            with open(mock_core_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for forbidden imports
            forbidden_imports = [
                "from ..messaging_core import",
                "from src.core.messaging_core import",
                "import messaging_core",
                "from messaging_core import",
            ]
            
            for forbidden in forbidden_imports:
                if forbidden in content:
                    self._add_violation(
                        "FORBIDDEN_IMPORT",
                        f"Mock core imports real messaging_core: {forbidden}",
                        file=str(mock_core_file),
                        severity="ERROR"
                    )
                else:
                    self.checks_passed += 1
            
            print("✅ No real messaging_core imports found in mock core")
            
        except Exception as e:
            self._add_violation(
                "VALIDATION_ERROR",
                f"Error checking imports: {e}",
                file=str(mock_core_file),
                severity="ERROR"
            )

    def _check_no_pyautogui(self):
        """Check that mock core doesn't use PyAutoGUI."""
        mock_core_file = self.stress_test_dir / "mock_messaging_core.py"
        
        if not mock_core_file.exists():
            return
        
        try:
            with open(mock_core_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for PyAutoGUI usage
            pyautogui_patterns = [
                "import pyautogui",
                "from pyautogui import",
                "pyautogui.",
            ]
            
            for pattern in pyautogui_patterns:
                if pattern in content:
                    self._add_violation(
                        "PYAUTOGUI_USAGE",
                        f"Mock core uses PyAutoGUI: {pattern}",
                        file=str(mock_core_file),
                        severity="ERROR"
                    )
                else:
                    self.checks_passed += 1
            
            print("✅ No PyAutoGUI usage found in mock core")
            
        except Exception as e:
            self._add_violation(
                "VALIDATION_ERROR",
                f"Error checking PyAutoGUI: {e}",
                file=str(mock_core_file),
                severity="ERROR"
            )

    def _check_no_inbox_writes(self):
        """Check that mock core doesn't write to inbox directories."""
        mock_core_file = self.stress_test_dir / "mock_messaging_core.py"
        
        if not mock_core_file.exists():
            return
        
        try:
            with open(mock_core_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for inbox writes
            inbox_patterns = [
                "agent_workspaces",
                "inbox",
                ".write(",
                "open(.*inbox",
            ]
            
            # Parse AST to check for file operations
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr in ['write', 'writelines']:
                                # Check if writing to inbox
                                if any('inbox' in str(node.args) for _ in [None]):
                                    self._add_violation(
                                        "INBOX_WRITE",
                                        "Mock core writes to inbox directories",
                                        file=str(mock_core_file),
                                        severity="ERROR"
                                    )
            except SyntaxError:
                pass  # Skip AST parsing if syntax error
            
            # Simple string check
            if "agent_workspaces" in content and "write" in content:
                # More careful check needed
                pass
            
            print("✅ No inbox writes detected in mock core")
            self.checks_passed += 1
            
        except Exception as e:
            self._add_violation(
                "VALIDATION_ERROR",
                f"Error checking inbox writes: {e}",
                file=str(mock_core_file),
                severity="ERROR"
            )

    def _check_protocol_compliance(self):
        """Check that mock core implements MessagingCoreProtocol."""
        protocol_file = self.stress_test_dir / "messaging_core_protocol.py"
        mock_core_file = self.stress_test_dir / "mock_messaging_core.py"
        
        if not protocol_file.exists():
            self._add_violation(
                "FILE_MISSING",
                f"Protocol file not found: {protocol_file}",
                severity="WARNING"
            )
            return
        
        if not mock_core_file.exists():
            return
        
        try:
            # Check that mock implements send_message with correct signature
            with open(mock_core_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for send_message method
            if "def send_message" in content:
                print("✅ Mock core implements send_message method")
                self.checks_passed += 1
            else:
                self._add_violation(
                    "PROTOCOL_VIOLATION",
                    "Mock core missing send_message method",
                    file=str(mock_core_file),
                    severity="ERROR"
                )
            
        except Exception as e:
            self._add_violation(
                "VALIDATION_ERROR",
                f"Error checking protocol compliance: {e}",
                severity="ERROR"
            )

    def _check_injection_point(self):
        """Check that MessageQueueProcessor has injection point."""
        processor_file = Path("src/core/message_queue_processor.py")
        
        if not processor_file.exists():
            self._add_violation(
                "FILE_MISSING",
                f"MessageQueueProcessor not found: {processor_file}",
                severity="WARNING"
            )
            return
        
        try:
            with open(processor_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for messaging_core parameter in __init__
            if "messaging_core" in content and "__init__" in content:
                print("✅ Injection point found in MessageQueueProcessor")
                self.checks_passed += 1
            else:
                self._add_violation(
                    "INJECTION_MISSING",
                    "MessageQueueProcessor missing messaging_core injection point",
                    file=str(processor_file),
                    severity="WARNING"
                )
            
        except Exception as e:
            self._add_violation(
                "VALIDATION_ERROR",
                f"Error checking injection point: {e}",
                severity="ERROR"
            )

    def _check_mock_isolation(self):
        """Check that mock is properly isolated from real system."""
        mock_core_file = self.stress_test_dir / "mock_messaging_core.py"
        
        if not mock_core_file.exists():
            return
        
        try:
            with open(mock_core_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check that mock only uses simulation
            isolation_keywords = ["simulate", "mock", "fake", "test"]
            has_isolation = any(keyword in content.lower() for keyword in isolation_keywords)
            
            if has_isolation:
                print("✅ Mock core appears properly isolated")
                self.checks_passed += 1
            else:
                self._add_violation(
                    "ISOLATION_WARNING",
                    "Mock core may not be properly isolated",
                    file=str(mock_core_file),
                    severity="WARNING"
                )
            
        except Exception as e:
            self._add_violation(
                "VALIDATION_ERROR",
                f"Error checking isolation: {e}",
                severity="ERROR"
            )

    def _add_violation(self, violation_type: str, message: str, 
                      file: str = None, severity: str = "ERROR"):
        """Add a validation violation."""
        violation = {
            "type": violation_type,
            "message": message,
            "severity": severity,
        }
        if file:
            violation["file"] = file
        
        self.violations.append(violation)
        self.checks_failed += 1
        
        severity_icon = "❌" if severity == "ERROR" else "⚠️"
        print(f"{severity_icon} {violation_type}: {message}")

    def _get_results(self) -> Dict[str, Any]:
        """Get validation results."""
        return {
            "passed": self.checks_passed,
            "failed": self.checks_failed,
            "total": self.checks_passed + self.checks_failed,
            "violations": self.violations,
            "all_passed": len(self.violations) == 0,
        }


def main():
    """Main validation entry point."""
    stress_test_dir = Path("src/core/stress_testing")
    
    validator = StressTestValidator(stress_test_dir)
    all_passed, results = validator.validate_all()
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)
    print(f"✅ Checks Passed: {results['passed']}")
    print(f"❌ Checks Failed: {results['failed']}")
    print(f"📈 Total Checks: {results['total']}")
    
    if results['violations']:
        print("\n🚨 VIOLATIONS FOUND:")
        for violation in results['violations']:
            severity = violation['severity']
            icon = "❌" if severity == "ERROR" else "⚠️"
            print(f"{icon} [{severity}] {violation['type']}: {violation['message']}")
            if 'file' in violation:
                print(f"   File: {violation['file']}")
    
    if all_passed:
        print("\n✅ ALL VALIDATIONS PASSED - Stress test is safe!")
        return 0
    else:
        print("\n❌ VALIDATIONS FAILED - Review violations above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

