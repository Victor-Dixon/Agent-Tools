#!/usr/bin/env python3
"""Test SSOT preservation logic in cleanup script."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.cleanup_repository_for_migration import should_exclude_file

# Test cases
test_cases = [
    # SSOT documentation (should be KEPT)
    ("docs/architecture/ssot-domains/communication.md", False, "SSOT domain doc"),
    ("docs/architecture/ssot-standards/tagging.md", False, "SSOT standards doc"),
    ("docs/architecture/ssot-audits/communication-2025-12-03.md", False, "SSOT audit doc"),
    ("docs/architecture/ssot-remediation/status-2025-12-03.md", False, "SSOT remediation doc"),
    
    # Coordination artifacts (should be EXCLUDED)
    ("docs/organization/test.md", True, "Coordination artifact"),
    ("devlogs/test.md", True, "Devlog"),
    ("agent_workspaces/test.json", True, "Agent workspace"),
    
    # Templates/examples (should be KEPT)
    ("data/templates/test.txt", False, "Template file"),
    ("data/examples/test.txt", False, "Example file"),
    
    # Regular data (should be EXCLUDED)
    ("data/test.json", True, "Regular data file"),
]

print("=" * 70)
print("SSOT Preservation Validation Test")
print("=" * 70)
print()

passed = 0
failed = 0

for filepath, expected_exclude, description in test_cases:
    result = should_exclude_file(filepath)
    status = "✅ PASS" if result == expected_exclude else "❌ FAIL"
    action = "EXCLUDE" if result else "KEEP"
    expected_action = "EXCLUDE" if expected_exclude else "KEEP"
    
    print(f"{status} | {filepath:50} | {action:6} (expected: {expected_action:6}) | {description}")
    
    if result == expected_exclude:
        passed += 1
    else:
        failed += 1

print()
print("=" * 70)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 70)

sys.exit(0 if failed == 0 else 1)



