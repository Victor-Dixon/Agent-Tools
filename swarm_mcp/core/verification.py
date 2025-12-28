"""
Automated Verification Harness
==============================

Ensures "claims" of work are backed by machine-verifiable proof.
No "done" without verification.
"""

import subprocess
import requests
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pathlib import Path

class VerificationType(Enum):
    PAGE_FETCH = "page_fetch"
    SCREENSHOT_DIFF = "screenshot_diff" # Placeholder for now
    UNIT_TEST = "unit_test"
    FILE_EXISTS = "file_exists"
    COMMAND_OUTPUT = "command_output"

@dataclass
class VerificationResult:
    type: VerificationType
    target: str
    passed: bool
    details: str
    timestamp: str

class VerificationHarness:
    """Runs automated checks to verify task completion."""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)

    def verify_page_fetch(self, url: str, expected_content: Optional[str] = None) -> VerificationResult:
        """Verify a URL returns 200 OK and optionally contains text."""
        try:
            response = requests.get(url, timeout=10)
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed and expected_content:
                if expected_content in response.text:
                    details += f", Content '{expected_content}' found."
                else:
                    passed = False
                    details += f", Content '{expected_content}' NOT found."
            
            return VerificationResult(
                type=VerificationType.PAGE_FETCH,
                target=url,
                passed=passed,
                details=details,
                timestamp="" # Filled by caller or now()
            )
        except Exception as e:
            return VerificationResult(
                type=VerificationType.PAGE_FETCH,
                target=url,
                passed=False,
                details=str(e),
                timestamp=""
            )

    def verify_unit_test(self, test_path: str) -> VerificationResult:
        """Run a specific unit test file."""
        import sys
        try:
            # Assume python/pytest for now
            cmd = [sys.executable, "-m", "pytest", test_path]
            result = subprocess.run(
                cmd, 
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            passed = result.returncode == 0
            details = result.stdout[-500:] if passed else result.stdout + "\n" + result.stderr
            
            return VerificationResult(
                type=VerificationType.UNIT_TEST,
                target=test_path,
                passed=passed,
                details=details.strip(),
                timestamp=""
            )
        except Exception as e:
            return VerificationResult(
                type=VerificationType.UNIT_TEST,
                target=test_path,
                passed=False,
                details=str(e),
                timestamp=""
            )

    def verify_file_exists(self, path: str) -> VerificationResult:
        """Check if a file exists."""
        full_path = self.workspace_root / path
        exists = full_path.exists()
        return VerificationResult(
            type=VerificationType.FILE_EXISTS,
            target=path,
            passed=exists,
            details=f"File {'exists' if exists else 'missing'}",
            timestamp=""
        )

    def run_suite(self, checks: List[Dict[str, Any]]) -> List[VerificationResult]:
        """Run a suite of verification checks."""
        results = []
        import datetime
        
        for check in checks:
            c_type = check.get("type")
            target = check.get("target")
            extra = check.get("extra", {})
            
            res = None
            if c_type == "page_fetch":
                res = self.verify_page_fetch(target, extra.get("expected_content"))
            elif c_type == "unit_test":
                res = self.verify_unit_test(target)
            elif c_type == "file_exists":
                res = self.verify_file_exists(target)
            
            if res:
                res.timestamp = datetime.datetime.now().isoformat()
                results.append(res)
                
        return results
