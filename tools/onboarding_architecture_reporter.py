#!/usr/bin/env python3
"""
Onboarding Architecture Reporter
=================================

Generates a concise summary of the onboarding module structure by analyzing
source files and documenting the shim-over-helpers pattern.

V2 Compliance: <300 lines, single responsibility
Author: Agent-2
Date: 2025-12-15
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def analyze_onboarding_services() -> Dict[str, any]:
    """Analyze onboarding service files and extract structure."""
    services_dir = project_root / "src" / "services"
    onboarding_dir = services_dir / "onboarding"

    results = {
        "services": {},
        "helpers": {},
        "public_apis": [],
        "test_coverage": {}
    }

    # Analyze HardOnboardingService
    hard_service_path = services_dir / "hard_onboarding_service.py"
    if hard_service_path.exists():
        content = hard_service_path.read_text(encoding="utf-8")
        lines = len(content.splitlines())
        results["services"]["HardOnboardingService"] = {
            "file": str(hard_service_path.relative_to(project_root)),
            "lines": lines,
            "v2_compliant": lines < 400,
            "delegates_to": []
        }

        # Check for helper delegations
        if "onboarding_helpers" in content:
            results["services"]["HardOnboardingService"]["delegates_to"].append(
                "onboarding_helpers")
        if "agent_instructions" in content:
            results["services"]["HardOnboardingService"]["delegates_to"].append(
                "agent_instructions")

    # Analyze SoftOnboardingService
    soft_service_path = services_dir / "soft_onboarding_service.py"
    if soft_service_path.exists():
        content = soft_service_path.read_text(encoding="utf-8")
        lines = len(content.splitlines())
        results["services"]["SoftOnboardingService"] = {
            "file": str(soft_service_path.relative_to(project_root)),
            "lines": lines,
            "v2_compliant": lines < 400,
            "delegates_to": []
        }

        # Check for helper delegations
        if "coordinate_loader" in content:
            results["services"]["SoftOnboardingService"]["delegates_to"].append(
                "coordinate_loader")
        if "MessageCoordinator" in content:
            results["services"]["SoftOnboardingService"]["delegates_to"].append(
                "messaging_system")

    # Analyze helper modules
    if onboarding_dir.exists():
        for helper_file in onboarding_dir.glob("*.py"):
            if helper_file.name == "__init__.py":
                continue

            content = helper_file.read_text(encoding="utf-8")
            lines = len(content.splitlines())
            module_name = helper_file.stem

            results["helpers"][module_name] = {
                "file": str(helper_file.relative_to(project_root)),
                "lines": lines,
                "v2_compliant": lines < 300,
                "public_functions": []
            }

            # Extract public function names (simple heuristic)
            for line in content.splitlines():
                if line.strip().startswith("def ") and not line.strip().startswith("def _"):
                    func_name = line.strip().split("def ")[1].split("(")[0]
                    results["helpers"][module_name]["public_functions"].append(
                        func_name)

    # Check test coverage
    test_file = project_root / "tests" / "unit" / \
        "services" / "test_onboarding_services.py"
    if test_file.exists():
        content = test_file.read_text(encoding="utf-8")
        results["test_coverage"] = {
            "file": str(test_file.relative_to(project_root)),
            "exists": True,
            "locks_public_apis": "hard_onboard_agent" in content and "soft_onboard_agent" in content
        }
    else:
        results["test_coverage"] = {"exists": False}

    return results


def generate_report(analysis: Dict[str, any]) -> str:
    """Generate a markdown report from analysis results."""
    report = ["# Onboarding Architecture Summary", ""]
    report.append(f"**Generated**: {Path(__file__).stat().st_mtime}")
    report.append("")

    # Services section
    report.append("## Service Shims")
    report.append("")
    for service_name, info in analysis["services"].items():
        report.append(f"### `{service_name}`")
        report.append(f"- **File**: `{info['file']}`")
        report.append(f"- **Lines**: {info['lines']}")
        report.append(
            f"- **V2 Compliant**: {'✅' if info['v2_compliant'] else '❌'}")
        if info["delegates_to"]:
            report.append(
                f"- **Delegates to**: {', '.join(info['delegates_to'])}")
        report.append("")

    # Helpers section
    report.append("## Helper Modules")
    report.append("")
    for helper_name, info in analysis["helpers"].items():
        report.append(f"### `{helper_name}`")
        report.append(f"- **File**: `{info['file']}`")
        report.append(f"- **Lines**: {info['lines']}")
        report.append(
            f"- **V2 Compliant**: {'✅' if info['v2_compliant'] else '❌'}")
        if info["public_functions"]:
            report.append(
                f"- **Public Functions**: {', '.join(info['public_functions'])}")
        report.append("")

    # Test coverage section
    report.append("## Test Coverage")
    report.append("")
    if analysis["test_coverage"].get("exists"):
        report.append(
            f"- **Test File**: `{analysis['test_coverage']['file']}`")
        report.append(
            f"- **Locks Public APIs**: {'✅' if analysis['test_coverage'].get('locks_public_apis') else '❌'}")
    else:
        report.append("- **Test File**: ❌ Not found")
    report.append("")

    # Pattern validation
    report.append("## Pattern Validation")
    report.append("")
    all_services_compliant = all(s["v2_compliant"]
                                 for s in analysis["services"].values())
    all_helpers_compliant = all(h["v2_compliant"]
                                for h in analysis["helpers"].values())
    has_delegations = any(len(s["delegates_to"]) >
                          0 for s in analysis["services"].values())

    report.append(
        f"- **Services V2 Compliant**: {'✅' if all_services_compliant else '❌'}")
    report.append(
        f"- **Helpers V2 Compliant**: {'✅' if all_helpers_compliant else '❌'}")
    report.append(
        f"- **Shim Pattern (Delegations)**: {'✅' if has_delegations else '⚠️'}")
    report.append("")

    return "\n".join(report)


def main():
    """Main entry point."""
    print("🔍 Analyzing onboarding architecture...")

    analysis = analyze_onboarding_services()
    report = generate_report(analysis)

    # Save report
    output_path = project_root / "docs" / "architecture" / \
        "ONBOARDING_ARCHITECTURE_SUMMARY.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(f"✅ Report generated: {output_path.relative_to(project_root)}")
    print("\n" + report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
