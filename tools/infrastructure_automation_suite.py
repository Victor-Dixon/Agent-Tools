#!/usr/bin/env python3
"""
Infrastructure Automation Suite
===============================

Comprehensive automation suite for infrastructure operations.
Combines all infrastructure tools into unified automation.

<!-- SSOT Domain: infrastructure -->

Author: Agent-3 (Infrastructure & DevOps) - JET FUEL AUTONOMOUS MODE
Created: 2025-01-27
Priority: CRITICAL
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfrastructureAutomationSuite:
    """Unified infrastructure automation suite."""

    def __init__(self):
        """Initialize automation suite."""
        self.tools_dir = Path("tools")

    def run_compression_automation(self) -> dict:
        """Run message compression automation."""
        try:
            result = subprocess.run(
                ["python", "tools/message_compression_automation.py"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_EXTENDED,
            )
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_infrastructure_health(self) -> dict:
        """Check infrastructure health."""
        try:
            result = subprocess.run(
                ["python", "tools/infrastructure_health_dashboard.py", "--json"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_MEDIUM,
            )
            if result.returncode == 0:
                return {"success": True, "health": json.loads(result.stdout)}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_repo_consolidation(self) -> dict:
        """Analyze repository consolidation opportunities."""
        try:
            result = subprocess.run(
                ["python", "tools/repo_consolidation_analyzer.py", "--json"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_MEDIUM,
            )
            if result.returncode == 0:
                return {"success": True, "analysis": json.loads(result.stdout)}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_full_automation(self) -> dict:
        """Run full infrastructure automation suite."""
        logger.info("🚀 Starting infrastructure automation suite...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "compression": self.run_compression_automation(),
            "health": self.check_infrastructure_health(),
            "consolidation": self.analyze_repo_consolidation(),
        }
        
        # Overall status
        all_success = all(
            r.get("success", False) for r in results.values() if isinstance(r, dict)
        )
        results["overall_status"] = "success" if all_success else "partial"
        
        logger.info(f"✅ Automation suite complete: {results['overall_status']}")
        return results

    def print_automation_report(self) -> None:
        """Print automation suite report."""
        results = self.run_full_automation()
        
        print("\n" + "="*70)
        print("🔧 INFRASTRUCTURE AUTOMATION SUITE")
        print("="*70)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Overall Status: {results['overall_status'].upper()}")
        print()
        
        # Compression
        comp = results.get("compression", {})
        print("📦 MESSAGE COMPRESSION:")
        print(f"  Status: {'✅ Success' if comp.get('success') else '❌ Failed'}")
        if comp.get("error"):
            print(f"  Error: {comp['error']}")
        print()
        
        # Health
        health = results.get("health", {})
        if health.get("success"):
            h_data = health.get("health", {})
            print("🔍 INFRASTRUCTURE HEALTH:")
            print(f"  Status: {h_data.get('overall_status', 'unknown')}")
            if "systems" in h_data:
                for sys_name, sys_data in h_data["systems"].items():
                    status = sys_data.get("status", "unknown")
                    emoji = "🟢" if status in ["healthy", "running"] else "🟡" if status == "warning" else "🔴"
                    print(f"  {emoji} {sys_name}: {status}")
        else:
            print("🔍 INFRASTRUCTURE HEALTH: ❌ Failed")
        print()
        
        # Consolidation
        consol = results.get("consolidation", {})
        if consol.get("success"):
            c_data = consol.get("analysis", {})
            print("📚 REPOSITORY CONSOLIDATION:")
            print(f"  Total Repos: {c_data.get('total_repos', 0)}")
            print(f"  Consolidation Groups: {c_data.get('consolidation_groups', 0)}")
            print(f"  Opportunities: {c_data.get('summary', {}).get('consolidation_opportunities', 0)}")
        else:
            print("📚 REPOSITORY CONSOLIDATION: ❌ Failed")
        print()
        
        print("="*70 + "\n")


def main():
    """CLI entry point."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(description="Infrastructure Automation Suite")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    suite = InfrastructureAutomationSuite()
    
    if args.json:
        results = suite.run_full_automation()
        print(json.dumps(results, indent=2))
    else:
        suite.print_automation_report()


if __name__ == "__main__":
    main()




