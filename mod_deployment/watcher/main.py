#!/usr/bin/env python3
"""
Mod Update Watcher Service
==========================

Monitors Thunderstore for mod updates and handles automated deployment.

Features:
- Polls Thunderstore API for updates
- Deploys to staging server first
- Sends Discord notifications
- Promotes to production after staging approval
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import docker
import requests

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.thunderstore_client import ThunderstoreClient
from core.mod_manager import ModManager

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Send notifications to Discord webhook."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK")
    
    def send(self, title: str, description: str, color: int = 0x00ff00) -> bool:
        if not self.webhook_url:
            return False
        
        try:
            payload = {
                "embeds": [{
                    "title": title,
                    "description": description,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat(),
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
            )
            return response.status_code == 204
        except Exception as e:
            logger.warning(f"Discord notification failed: {e}")
            return False
    
    def notify_update_available(self, mod: str, current: str, latest: str):
        self.send(
            title="🔄 Mod Update Available",
            description=f"**{mod}**\n`{current}` → `{latest}`",
            color=0x3498db,  # Blue
        )
    
    def notify_deployment_started(self, mod: str, version: str, target: str):
        self.send(
            title="🚀 Deployment Started",
            description=f"**{mod}** v{version}\nTarget: {target}",
            color=0xf39c12,  # Orange
        )
    
    def notify_deployment_success(self, mod: str, version: str, target: str):
        self.send(
            title="✅ Deployment Successful",
            description=f"**{mod}** v{version}\nDeployed to: {target}",
            color=0x2ecc71,  # Green
        )
    
    def notify_deployment_failed(self, mod: str, version: str, error: str):
        self.send(
            title="❌ Deployment Failed",
            description=f"**{mod}** v{version}\nError: {error}",
            color=0xe74c3c,  # Red
        )
    
    def notify_health_issue(self, target: str, details: str):
        self.send(
            title="⚠️ Health Check Failed",
            description=f"**{target}**\n{details}",
            color=0xe74c3c,  # Red
        )


class ModWatcher:
    """
    Watches Thunderstore for mod updates and handles deployment.
    """
    
    def __init__(
        self,
        game: str = "lethal-company",
        check_interval: int = 3600,
        staging_container: str = "game-server-staging",
        production_container: str = "game-server-production",
        auto_deploy_staging: bool = True,
        auto_deploy_production: bool = False,
    ):
        self.game = game
        self.check_interval = check_interval
        self.staging_container = staging_container
        self.production_container = production_container
        self.auto_deploy_staging = auto_deploy_staging
        self.auto_deploy_production = auto_deploy_production
        
        self.client = ThunderstoreClient(game=game)
        self.notifier = DiscordNotifier()
        
        # State file for tracking
        self.state_file = Path("/data/watcher_state.json")
        self.state = self._load_state()
        
        # Docker client
        try:
            self.docker = docker.from_env()
        except Exception:
            self.docker = None
            logger.warning("Docker not available, running in local mode")
    
    def _load_state(self) -> Dict[str, Any]:
        """Load watcher state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "tracked_mods": {},  # mod -> installed version
            "pending_updates": {},  # mod -> {version, discovered_at}
            "deployment_history": [],
            "last_check": None,
        }
    
    def _save_state(self) -> None:
        """Save watcher state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2, default=str)
    
    def track_mod(self, mod: str, version: str) -> None:
        """Add a mod to tracking."""
        self.state["tracked_mods"][mod] = version
        self._save_state()
        logger.info(f"Now tracking: {mod} v{version}")
    
    def untrack_mod(self, mod: str) -> None:
        """Remove a mod from tracking."""
        if mod in self.state["tracked_mods"]:
            del self.state["tracked_mods"][mod]
            self._save_state()
            logger.info(f"Stopped tracking: {mod}")
    
    def check_for_updates(self) -> Dict[str, Dict[str, str]]:
        """Check tracked mods for updates."""
        if not self.state["tracked_mods"]:
            logger.info("No mods being tracked")
            return {}
        
        logger.info(f"Checking {len(self.state['tracked_mods'])} mods for updates...")
        
        updates = self.client.check_for_updates(self.state["tracked_mods"])
        
        for mod, info in updates.items():
            if mod not in self.state["pending_updates"]:
                self.state["pending_updates"][mod] = {
                    "current": info["current"],
                    "latest": info["latest"],
                    "discovered_at": datetime.now().isoformat(),
                }
                
                logger.info(f"Update available: {mod} {info['current']} -> {info['latest']}")
                self.notifier.notify_update_available(mod, info["current"], info["latest"])
        
        self.state["last_check"] = datetime.now().isoformat()
        self._save_state()
        
        return updates
    
    def deploy_to_container(
        self,
        container_name: str,
        mod: str,
        version: str,
    ) -> bool:
        """Deploy a mod update to a container."""
        if not self.docker:
            logger.error("Docker not available for deployment")
            return False
        
        try:
            container = self.docker.containers.get(container_name)
            
            logger.info(f"Deploying {mod} v{version} to {container_name}")
            self.notifier.notify_deployment_started(mod, version, container_name)
            
            # Execute install command in container
            exec_result = container.exec_run(
                cmd=[
                    "python3", "-c",
                    f"""
import sys
sys.path.insert(0, '/app')
from core.mod_manager import ModManager
manager = ModManager(game_path='/app', game='{self.game}')
result = manager.install('{mod}', version='{version}')
print('SUCCESS' if result.success else 'FAILED')
print(result.error if result.error else '')
"""
                ],
                demux=True,
            )
            
            stdout = exec_result.output[0].decode() if exec_result.output[0] else ""
            stderr = exec_result.output[1].decode() if exec_result.output[1] else ""
            
            if "SUCCESS" in stdout:
                logger.info(f"Deployment successful: {mod} to {container_name}")
                self.notifier.notify_deployment_success(mod, version, container_name)
                
                # Record deployment
                self.state["deployment_history"].append({
                    "mod": mod,
                    "version": version,
                    "target": container_name,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                })
                self._save_state()
                
                return True
            else:
                error = stderr or stdout
                logger.error(f"Deployment failed: {error}")
                self.notifier.notify_deployment_failed(mod, version, error)
                return False
                
        except docker.errors.NotFound:
            logger.error(f"Container not found: {container_name}")
            return False
        except Exception as e:
            logger.error(f"Deployment error: {e}")
            self.notifier.notify_deployment_failed(mod, version, str(e))
            return False
    
    def restart_container(self, container_name: str) -> bool:
        """Restart a container after mod deployment."""
        if not self.docker:
            return False
        
        try:
            container = self.docker.containers.get(container_name)
            logger.info(f"Restarting container: {container_name}")
            container.restart(timeout=30)
            return True
        except Exception as e:
            logger.error(f"Failed to restart container: {e}")
            return False
    
    def wait_for_healthy(self, container_name: str, timeout: int = 120) -> bool:
        """Wait for container to become healthy."""
        if not self.docker:
            return True
        
        try:
            container = self.docker.containers.get(container_name)
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                container.reload()
                health = container.attrs.get("State", {}).get("Health", {})
                status = health.get("Status", "unknown")
                
                if status == "healthy":
                    logger.info(f"Container healthy: {container_name}")
                    return True
                elif status == "unhealthy":
                    logger.error(f"Container unhealthy: {container_name}")
                    return False
                
                time.sleep(5)
            
            logger.warning(f"Health check timeout: {container_name}")
            return False
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    def promote_to_production(self, mod: str, version: str) -> bool:
        """Promote a mod from staging to production."""
        if not self.auto_deploy_production:
            logger.info(f"Manual approval required for production deployment of {mod}")
            return False
        
        # Deploy to production
        success = self.deploy_to_container(self.production_container, mod, version)
        
        if success:
            # Update tracked version
            self.state["tracked_mods"][mod] = version
            
            # Remove from pending
            if mod in self.state["pending_updates"]:
                del self.state["pending_updates"][mod]
            
            self._save_state()
        
        return success
    
    def process_updates(self) -> None:
        """Process pending updates with staged deployment."""
        updates = self.check_for_updates()
        
        if not updates:
            logger.info("No updates available")
            return
        
        for mod, info in updates.items():
            latest_version = info["latest"]
            
            # Deploy to staging first
            if self.auto_deploy_staging:
                logger.info(f"Deploying {mod} to staging for testing...")
                
                staging_success = self.deploy_to_container(
                    self.staging_container,
                    mod,
                    latest_version,
                )
                
                if staging_success:
                    # Restart and wait for healthy
                    self.restart_container(self.staging_container)
                    
                    if self.wait_for_healthy(self.staging_container):
                        logger.info(f"Staging deployment verified: {mod}")
                        
                        # Auto-promote to production if enabled
                        if self.auto_deploy_production:
                            self.promote_to_production(mod, latest_version)
                    else:
                        logger.error(f"Staging health check failed for {mod}")
                        self.notifier.notify_health_issue(
                            self.staging_container,
                            f"After deploying {mod} v{latest_version}"
                        )
    
    def run(self) -> None:
        """Run the watcher main loop."""
        logger.info(f"Starting mod watcher for {self.game}")
        logger.info(f"Check interval: {self.check_interval}s")
        logger.info(f"Tracking {len(self.state['tracked_mods'])} mods")
        
        while True:
            try:
                self.process_updates()
            except Exception as e:
                logger.error(f"Watcher error: {e}")
            
            logger.info(f"Next check in {self.check_interval}s...")
            time.sleep(self.check_interval)


def main():
    """Main entry point."""
    watcher = ModWatcher(
        game=os.getenv("GAME", "lethal-company"),
        check_interval=int(os.getenv("CHECK_INTERVAL", "3600")),
        staging_container=os.getenv("STAGING_CONTAINER", "game-server-staging"),
        production_container=os.getenv("PRODUCTION_CONTAINER", "game-server-production"),
        auto_deploy_staging=os.getenv("AUTO_DEPLOY_TO_STAGING", "true").lower() == "true",
        auto_deploy_production=os.getenv("AUTO_DEPLOY_TO_PRODUCTION", "false").lower() == "true",
    )
    
    # Track mods from environment if specified
    tracked_mods = os.getenv("TRACKED_MODS", "")
    if tracked_mods:
        for mod_spec in tracked_mods.split(","):
            parts = mod_spec.strip().split(":")
            if len(parts) == 2:
                watcher.track_mod(parts[0], parts[1])
            elif len(parts) == 1:
                watcher.track_mod(parts[0], "0.0.0")
    
    watcher.run()


if __name__ == "__main__":
    main()
