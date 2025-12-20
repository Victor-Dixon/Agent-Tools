#!/usr/bin/env python3
"""
Integration Workflow Automation - Agent-2
==========================================

Automated integration workflow for Stage 1 integration work.

<!-- SSOT Domain: infrastructure -->
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional
from src.core.config.timeout_constants import TimeoutConstants

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class IntegrationWorkflow:
    """Automated integration workflow."""
    
    def __init__(self, repo_name: str, repo_path: Optional[Path] = None):
        self.repo_name = repo_name
        self.repo_path = repo_path or Path(".")
        self.tools_dir = project_root / "tools"
    
    def phase_0_cleanup(self) -> bool:
        """Phase 0: Pre-Integration Cleanup."""
        print("📋 Phase 0: Pre-Integration Cleanup...")
        
        # Detect venv files
        print("  → Detecting venv files...")
        venv_tool = self.tools_dir / "detect_venv_files.py"
        if venv_tool.exists():
            result = subprocess.run(
                ["python", str(venv_tool), str(self.repo_path)],
                capture_output=True, text=True, timeout=TimeoutConstants.HTTP_EXTENDED
            )
            if result.returncode != 0:
                print(f"  ⚠️ Venv detection warning: {result.stderr}")
            else:
                print("  ✅ Venv detection complete")
        else:
            print("  ⚠️ Venv detection tool not found")
        
        # Detect duplicates
        print("  → Detecting duplicates...")
        dup_tool = self.tools_dir / "enhanced_duplicate_detector.py"
        if dup_tool.exists():
            result = subprocess.run(
                ["python", str(dup_tool), self.repo_name],
                capture_output=True, text=True, timeout=TimeoutConstants.HTTP_EXTENDED
            )
            if result.returncode != 0:
                print(f"  ⚠️ Duplicate detection warning: {result.stderr}")
            else:
                print("  ✅ Duplicate detection complete")
        else:
            print("  ⚠️ Duplicate detection tool not found")
        
        # Check integration issues
        print("  → Checking integration issues...")
        issues_tool = self.tools_dir / "check_integration_issues.py"
        if issues_tool.exists():
            result = subprocess.run(
                ["python", str(issues_tool), str(self.repo_path)],
                capture_output=True, text=True, timeout=TimeoutConstants.HTTP_EXTENDED
            )
            if result.returncode != 0:
                print(f"  ⚠️ Integration issues check warning: {result.stderr}")
            else:
                print("  ✅ Integration issues check complete")
        else:
            print("  ⚠️ Integration issues tool not found")
        
        print("  ✅ Phase 0 complete")
        return True
    
    def phase_1_pattern_extraction(self) -> bool:
        """Phase 1: Pattern Extraction."""
        print("📋 Phase 1: Pattern Extraction...")
        
        # Extract patterns
        print("  → Extracting patterns...")
        pattern_tool = self.tools_dir / "analyze_merged_repo_patterns.py"
        if pattern_tool.exists():
            result = subprocess.run(
                ["python", str(pattern_tool)],
                capture_output=True, text=True, timeout=TimeoutConstants.HTTP_EXTENDED
            )
            if result.returncode != 0:
                print(f"  ⚠️ Pattern extraction warning: {result.stderr}")
            else:
                print("  ✅ Pattern extraction complete")
        else:
            print("  ⚠️ Pattern extraction tool not found")
        
        print("  ✅ Phase 1 complete")
        return True
    
    def run_full_workflow(self) -> bool:
        """Run complete integration workflow."""
        print(f"🚀 Starting full integration workflow for {self.repo_name}")
        print("="*60)
        
        if not self.phase_0_cleanup():
            print("❌ Phase 0 failed")
            return False
        
        print()
        if not self.phase_1_pattern_extraction():
            print("❌ Phase 1 failed")
            return False
        
        print()
        print("="*60)
        print("✅ Full integration workflow complete")
        print("📋 Next: Phase 2 (Service Integration) - Manual steps required")
        print("   Reference: docs/integration/INTEGRATION_TEMPLATES.md")
        return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python tools/integration_workflow_automation.py <repo_name> [repo_path]")
        print("\nExample:")
        print("  python tools/integration_workflow_automation.py DreamVault")
        print("  python tools/integration_workflow_automation.py DreamVault /path/to/repo")
        return 1
    
    repo_name = sys.argv[1]
    repo_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    workflow = IntegrationWorkflow(repo_name, repo_path)
    success = workflow.run_full_workflow()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

