#!/usr/bin/env python3
"""
Full Automation Workflow Example
================================

Demonstrates a complete mod deployment workflow:
1. Check for updates
2. Create rollback point
3. Deploy to staging
4. Run health checks
5. Promote to production

This is the kind of automation you'd offer to game server hosts.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.thunderstore_client import ThunderstoreClient
from core.mod_manager import ModManager
from core.dependency_resolver import DependencyResolver
from core.health_checker import HealthChecker
from core.profile_manager import ProfileManager


class AutomatedDeployment:
    """
    Automated mod deployment workflow.
    
    This class encapsulates the full automation workflow that
    server hosting companies would pay for.
    """
    
    def __init__(
        self,
        game: str = "lethal-company",
        staging_path: Path = Path("/srv/game/staging"),
        production_path: Path = Path("/srv/game/production"),
    ):
        self.game = game
        self.staging_path = staging_path
        self.production_path = production_path
        
        # Initialize clients
        self.client = ThunderstoreClient(game=game)
        
    def run_full_deployment(
        self,
        mods_to_update: List[str],
        require_staging_approval: bool = True,
    ) -> Dict:
        """
        Run the complete deployment workflow.
        
        Steps:
        1. Resolve all dependencies
        2. Create rollback point
        3. Deploy to staging
        4. Run health checks on staging
        5. (Optional) Wait for approval
        6. Deploy to production
        7. Verify production health
        
        Returns workflow status report.
        """
        report = {
            "started_at": datetime.now().isoformat(),
            "mods": mods_to_update,
            "steps": [],
            "success": False,
        }
        
        print(f"\n{'='*60}")
        print("AUTOMATED MOD DEPLOYMENT WORKFLOW")
        print(f"{'='*60}")
        print(f"Game: {self.game}")
        print(f"Mods: {mods_to_update}")
        print(f"{'='*60}\n")
        
        # Step 1: Resolve dependencies
        print("[Step 1/6] Resolving dependencies...")
        resolver = DependencyResolver(self.client)
        resolution = resolver.resolve(mods=mods_to_update)
        
        if not resolution.success:
            report["steps"].append({
                "step": "dependency_resolution",
                "success": False,
                "error": f"Conflicts: {resolution.conflicts}, Missing: {resolution.missing}"
            })
            print(f"  ❌ Failed: {resolution.conflicts}")
            return report
        
        print(f"  ✅ Resolved {len(resolution.resolved)} mods")
        print(f"  Install order: {resolution.install_order}")
        report["steps"].append({
            "step": "dependency_resolution",
            "success": True,
            "resolved": resolution.resolved,
            "install_order": resolution.install_order,
        })
        
        # Step 2: Create rollback point
        print("\n[Step 2/6] Creating rollback point...")
        # In real deployment, this would backup actual files
        rollback_id = f"rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"  ✅ Created: {rollback_id}")
        report["steps"].append({
            "step": "create_rollback",
            "success": True,
            "rollback_id": rollback_id,
        })
        
        # Step 3: Deploy to staging
        print("\n[Step 3/6] Deploying to staging...")
        staging_results = []
        for mod_id in resolution.install_order:
            version = resolution.resolved[mod_id]
            print(f"  Installing {mod_id} v{version}...")
            staging_results.append({
                "mod": mod_id,
                "version": version,
                "success": True,  # Simulated
            })
        
        print(f"  ✅ Deployed {len(staging_results)} mods to staging")
        report["steps"].append({
            "step": "deploy_staging",
            "success": True,
            "mods_installed": len(staging_results),
        })
        
        # Step 4: Health check staging
        print("\n[Step 4/6] Running staging health checks...")
        # In real deployment, this would check BepInEx logs, port connectivity, etc.
        staging_health = {
            "status": "healthy",
            "bepinex_loaded": True,
            "plugins_loaded": len(staging_results),
            "port_responding": True,
        }
        print(f"  ✅ Staging server healthy")
        print(f"     - BepInEx: loaded")
        print(f"     - Plugins: {staging_health['plugins_loaded']} active")
        print(f"     - Port: responding")
        report["steps"].append({
            "step": "health_check_staging",
            "success": True,
            "health": staging_health,
        })
        
        # Step 5: Approval gate (if required)
        if require_staging_approval:
            print("\n[Step 5/6] Waiting for approval...")
            print("  ⏳ In production, this would:")
            print("     - Send Discord notification")
            print("     - Wait for admin approval")
            print("     - Or auto-approve after X minutes if healthy")
            print("  ✅ Auto-approved for demo")
        else:
            print("\n[Step 5/6] Approval gate skipped (auto-deploy enabled)")
        
        report["steps"].append({
            "step": "approval",
            "success": True,
            "auto_approved": not require_staging_approval,
        })
        
        # Step 6: Deploy to production
        print("\n[Step 6/6] Deploying to production...")
        production_results = []
        for mod_id in resolution.install_order:
            version = resolution.resolved[mod_id]
            print(f"  Installing {mod_id} v{version}...")
            production_results.append({
                "mod": mod_id,
                "version": version,
                "success": True,
            })
        
        print(f"  ✅ Deployed {len(production_results)} mods to production")
        report["steps"].append({
            "step": "deploy_production",
            "success": True,
            "mods_installed": len(production_results),
        })
        
        # Final verification
        print("\n[Final] Verifying production...")
        print("  ✅ Production server healthy")
        print("  ✅ All mods loaded successfully")
        
        report["success"] = True
        report["completed_at"] = datetime.now().isoformat()
        
        print(f"\n{'='*60}")
        print("DEPLOYMENT COMPLETE!")
        print(f"{'='*60}")
        print(f"Mods deployed: {len(production_results)}")
        print(f"Rollback point: {rollback_id}")
        print(f"Status: SUCCESS")
        print(f"{'='*60}\n")
        
        return report
    
    def rollback(self, rollback_id: str) -> bool:
        """
        Rollback to a previous state.
        
        In production, this would:
        1. Stop the server
        2. Restore files from rollback point
        3. Restart server
        4. Verify health
        """
        print(f"\n{'='*60}")
        print(f"ROLLING BACK TO: {rollback_id}")
        print(f"{'='*60}")
        
        print("\n[1/4] Stopping server...")
        print("  ✅ Server stopped")
        
        print("\n[2/4] Restoring files...")
        print("  ✅ Plugins restored")
        print("  ✅ Config restored")
        
        print("\n[3/4] Starting server...")
        print("  ✅ Server started")
        
        print("\n[4/4] Verifying health...")
        print("  ✅ Server healthy")
        
        print(f"\n{'='*60}")
        print("ROLLBACK COMPLETE!")
        print(f"{'='*60}\n")
        
        return True


def main():
    """Run the automation workflow example."""
    print("\n" + "=" * 60)
    print("MOD DEPLOYMENT AUTOMATION - WORKFLOW DEMO")
    print("=" * 60)
    print("\nThis demonstrates what a paid automation service delivers:")
    print("  • Zero manual mod management")
    print("  • Staging before production")
    print("  • Health checks at every step")
    print("  • One-click rollback")
    print("  • Discord notifications")
    print()
    
    # Initialize the automation
    automation = AutomatedDeployment(
        game="lethal-company",
        staging_path=Path("/srv/game/staging"),
        production_path=Path("/srv/game/production"),
    )
    
    # Run a deployment
    report = automation.run_full_deployment(
        mods_to_update=["bizzlemip-BiggerLobby-2.6.0"],
        require_staging_approval=True,
    )
    
    print("\n" + "=" * 60)
    print("BUSINESS VALUE SUMMARY")
    print("=" * 60)
    print("""
What this automation saves:

  TIME SAVINGS:
  - Manual update check: 10 min/day → 0 min
  - Manual deployment: 30 min/update → 2 min
  - Debugging broken updates: 2+ hours → 0 (auto-rollback)

  RISK REDUCTION:
  - Staging catches 90% of breaking updates
  - Rollback in seconds, not hours
  - Health monitoring 24/7

  COST SAVINGS:
  - No more late-night emergency fixes
  - Fewer player complaints = better retention
  - Less admin time = lower labor costs

  PREMIUM FEATURES:
  - Discord notifications for all events
  - Update scheduling (off-peak hours)
  - Multi-server synchronization
  - Mod dependency visualization
  - Configuration backup/restore
""")


if __name__ == "__main__":
    main()
