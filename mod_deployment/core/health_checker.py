#!/usr/bin/env python3
"""
Health Checker
==============

Server health monitoring and automated rollback for mod deployments.
Verifies server stability after mod updates.

Author: Mod Deployment Automation Pipeline
"""

import json
import logging
import shutil
import socket
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Server health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    status: HealthStatus
    timestamp: str
    checks_passed: int
    checks_failed: int
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "details": self.details,
            "errors": self.errors,
        }


@dataclass
class RollbackPoint:
    """Represents a rollback point."""
    id: str
    created_at: str
    description: str
    backup_path: Path
    mods_snapshot: Dict[str, str]
    health_status: HealthStatus
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "description": self.description,
            "backup_path": str(self.backup_path),
            "mods_snapshot": self.mods_snapshot,
            "health_status": self.health_status.value,
        }


class HealthChecker:
    """
    Server health monitoring for mod deployments.
    
    Features:
    - Pre/post deployment health checks
    - Server connectivity verification
    - Process monitoring
    - Automated rollback on failure
    - Health history tracking
    """
    
    def __init__(
        self,
        game_path: Path,
        server_host: str = "localhost",
        server_port: int = 7777,
        health_history_limit: int = 100,
    ):
        """
        Initialize the health checker.
        
        Args:
            game_path: Path to game installation
            server_host: Server hostname for connectivity checks
            server_port: Server port for connectivity checks
            health_history_limit: Max health history entries to keep
        """
        self.game_path = Path(game_path)
        self.server_host = server_host
        self.server_port = server_port
        self.health_history_limit = health_history_limit
        
        self.backup_path = self.game_path / "rollback_points"
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        self.health_file = self.game_path / "health_history.json"
        self._health_history: List[HealthCheckResult] = []
        self._rollback_points: Dict[str, RollbackPoint] = {}
        self._custom_checks: List[Callable[[], bool]] = []
        
        self._load_history()
        self._load_rollback_points()
    
    def _load_history(self) -> None:
        """Load health history from disk."""
        if self.health_file.exists():
            try:
                with open(self.health_file) as f:
                    data = json.load(f)
                # Just keep timestamps for now
                logger.info(f"Loaded {len(data.get('history', []))} health history entries")
            except (json.JSONDecodeError, KeyError):
                pass
    
    def _save_history(self) -> None:
        """Save health history to disk."""
        history_data = [h.to_dict() for h in self._health_history[-self.health_history_limit:]]
        with open(self.health_file, "w") as f:
            json.dump({"history": history_data}, f, indent=2)
    
    def _load_rollback_points(self) -> None:
        """Load rollback points from disk."""
        manifest_file = self.backup_path / "rollback_manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file) as f:
                    data = json.load(f)
                for rp_data in data.get("rollback_points", []):
                    rp = RollbackPoint(
                        id=rp_data["id"],
                        created_at=rp_data["created_at"],
                        description=rp_data["description"],
                        backup_path=Path(rp_data["backup_path"]),
                        mods_snapshot=rp_data["mods_snapshot"],
                        health_status=HealthStatus(rp_data["health_status"]),
                    )
                    self._rollback_points[rp.id] = rp
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to load rollback points: {e}")
    
    def _save_rollback_points(self) -> None:
        """Save rollback points manifest."""
        manifest_file = self.backup_path / "rollback_manifest.json"
        data = {
            "rollback_points": [rp.to_dict() for rp in self._rollback_points.values()]
        }
        with open(manifest_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def add_custom_check(self, check_fn: Callable[[], bool]) -> None:
        """Add a custom health check function."""
        self._custom_checks.append(check_fn)
    
    def check_port_connectivity(self) -> bool:
        """Check if server port is responding."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.server_host, self.server_port))
            sock.close()
            return result == 0
        except socket.error as e:
            logger.warning(f"Port check failed: {e}")
            return False
    
    def check_process_running(self, process_name: str = "") -> bool:
        """Check if server process is running."""
        if not process_name:
            # Common game server process names
            process_name = "Lethal Company"  # Default
        
        try:
            result = subprocess.run(
                ["pgrep", "-f", process_name],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # pgrep not available, try alternative
            try:
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return process_name.lower() in result.stdout.lower()
            except Exception:
                return True  # Assume running if can't check
    
    def check_bepinex_loaded(self) -> bool:
        """Check if BepInEx is properly loaded (via log file)."""
        log_file = self.game_path / "BepInEx" / "LogOutput.log"
        
        if not log_file.exists():
            return False
        
        try:
            with open(log_file) as f:
                content = f.read()
            
            # Check for BepInEx initialization
            if "BepInEx" in content and "Chainloader ready" in content:
                return True
            
            # Check for errors
            if "FATAL" in content or "Exception" in content:
                return False
            
            return True
        except Exception as e:
            logger.warning(f"BepInEx log check failed: {e}")
            return False
    
    def check_plugins_loaded(self) -> Dict[str, bool]:
        """Check which plugins are loaded from BepInEx log."""
        log_file = self.game_path / "BepInEx" / "LogOutput.log"
        plugins_loaded = {}
        
        if not log_file.exists():
            return plugins_loaded
        
        try:
            with open(log_file) as f:
                content = f.read()
            
            # Parse loaded plugins from log
            for line in content.split("\n"):
                if "Loading [" in line and "]" in line:
                    # Extract plugin name
                    start = line.find("[") + 1
                    end = line.find("]")
                    if start > 0 and end > start:
                        plugin_name = line[start:end].strip()
                        plugins_loaded[plugin_name] = True
            
            return plugins_loaded
        except Exception as e:
            logger.warning(f"Plugin load check failed: {e}")
            return plugins_loaded
    
    def check_disk_space(self, min_gb: float = 1.0) -> bool:
        """Check if sufficient disk space is available."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.game_path)
            free_gb = free / (1024 ** 3)
            return free_gb >= min_gb
        except Exception:
            return True  # Assume OK if can't check
    
    def run_health_check(
        self,
        include_connectivity: bool = True,
        include_process: bool = True,
        include_bepinex: bool = True,
    ) -> HealthCheckResult:
        """
        Run comprehensive health check.
        
        Args:
            include_connectivity: Check port connectivity
            include_process: Check process running
            include_bepinex: Check BepInEx loaded
            
        Returns:
            HealthCheckResult
        """
        checks_passed = 0
        checks_failed = 0
        details = {}
        errors = []
        
        # Disk space check
        disk_ok = self.check_disk_space()
        details["disk_space"] = disk_ok
        if disk_ok:
            checks_passed += 1
        else:
            checks_failed += 1
            errors.append("Low disk space")
        
        # Connectivity check
        if include_connectivity:
            port_ok = self.check_port_connectivity()
            details["port_connectivity"] = port_ok
            if port_ok:
                checks_passed += 1
            else:
                checks_failed += 1
                errors.append(f"Port {self.server_port} not responding")
        
        # Process check
        if include_process:
            process_ok = self.check_process_running()
            details["process_running"] = process_ok
            if process_ok:
                checks_passed += 1
            else:
                checks_failed += 1
                errors.append("Server process not running")
        
        # BepInEx check
        if include_bepinex:
            bepinex_ok = self.check_bepinex_loaded()
            details["bepinex_loaded"] = bepinex_ok
            if bepinex_ok:
                checks_passed += 1
            else:
                checks_failed += 1
                errors.append("BepInEx not loaded properly")
            
            # Plugins loaded
            plugins = self.check_plugins_loaded()
            details["plugins_loaded"] = len(plugins)
        
        # Custom checks
        for i, check_fn in enumerate(self._custom_checks):
            try:
                result = check_fn()
                details[f"custom_check_{i}"] = result
                if result:
                    checks_passed += 1
                else:
                    checks_failed += 1
                    errors.append(f"Custom check {i} failed")
            except Exception as e:
                checks_failed += 1
                errors.append(f"Custom check {i} error: {e}")
        
        # Determine overall status
        if checks_failed == 0:
            status = HealthStatus.HEALTHY
        elif checks_failed <= checks_passed:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY
        
        result = HealthCheckResult(
            status=status,
            timestamp=datetime.now().isoformat(),
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            details=details,
            errors=errors,
        )
        
        # Save to history
        self._health_history.append(result)
        self._save_history()
        
        logger.info(f"Health check: {status.value} ({checks_passed}/{checks_passed + checks_failed} passed)")
        return result
    
    def create_rollback_point(
        self,
        description: str,
        mods_snapshot: Dict[str, str],
    ) -> RollbackPoint:
        """
        Create a rollback point before deploying changes.
        
        Args:
            description: Description of the rollback point
            mods_snapshot: Current mods configuration
            
        Returns:
            Created RollbackPoint
        """
        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rp_id = f"rollback_{timestamp}"
        
        # Create backup directory
        backup_dir = self.backup_path / rp_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup BepInEx plugins
        plugins_src = self.game_path / "BepInEx" / "plugins"
        if plugins_src.exists():
            shutil.copytree(plugins_src, backup_dir / "plugins")
        
        # Backup config
        config_src = self.game_path / "BepInEx" / "config"
        if config_src.exists():
            shutil.copytree(config_src, backup_dir / "config")
        
        # Run health check to record current status
        health = self.run_health_check(
            include_connectivity=False,  # Server might be stopped
            include_process=False,
        )
        
        rollback_point = RollbackPoint(
            id=rp_id,
            created_at=datetime.now().isoformat(),
            description=description,
            backup_path=backup_dir,
            mods_snapshot=mods_snapshot,
            health_status=health.status,
        )
        
        self._rollback_points[rp_id] = rollback_point
        self._save_rollback_points()
        
        logger.info(f"Created rollback point: {rp_id}")
        return rollback_point
    
    def rollback(self, rollback_id: Optional[str] = None) -> bool:
        """
        Rollback to a previous state.
        
        Args:
            rollback_id: ID of rollback point (latest if None)
            
        Returns:
            True if successful
        """
        if not self._rollback_points:
            logger.error("No rollback points available")
            return False
        
        if rollback_id:
            if rollback_id not in self._rollback_points:
                logger.error(f"Rollback point not found: {rollback_id}")
                return False
            rp = self._rollback_points[rollback_id]
        else:
            # Get most recent
            rp = sorted(
                self._rollback_points.values(),
                key=lambda x: x.created_at,
                reverse=True,
            )[0]
        
        logger.info(f"Rolling back to: {rp.id}")
        
        try:
            # Restore plugins
            plugins_backup = rp.backup_path / "plugins"
            plugins_dest = self.game_path / "BepInEx" / "plugins"
            
            if plugins_backup.exists():
                if plugins_dest.exists():
                    shutil.rmtree(plugins_dest)
                shutil.copytree(plugins_backup, plugins_dest)
            
            # Restore config
            config_backup = rp.backup_path / "config"
            config_dest = self.game_path / "BepInEx" / "config"
            
            if config_backup.exists():
                if config_dest.exists():
                    shutil.rmtree(config_dest)
                shutil.copytree(config_backup, config_dest)
            
            logger.info(f"Rollback complete: {rp.id}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def list_rollback_points(self) -> List[Dict[str, Any]]:
        """List available rollback points."""
        return [rp.to_dict() for rp in sorted(
            self._rollback_points.values(),
            key=lambda x: x.created_at,
            reverse=True,
        )]
    
    def cleanup_old_rollback_points(self, keep: int = 5) -> int:
        """
        Remove old rollback points.
        
        Args:
            keep: Number of most recent points to keep
            
        Returns:
            Number of points removed
        """
        if len(self._rollback_points) <= keep:
            return 0
        
        sorted_points = sorted(
            self._rollback_points.values(),
            key=lambda x: x.created_at,
        )
        
        to_remove = sorted_points[:-keep]
        removed = 0
        
        for rp in to_remove:
            try:
                if rp.backup_path.exists():
                    shutil.rmtree(rp.backup_path)
                del self._rollback_points[rp.id]
                removed += 1
            except Exception as e:
                logger.warning(f"Failed to remove rollback point {rp.id}: {e}")
        
        self._save_rollback_points()
        logger.info(f"Cleaned up {removed} old rollback points")
        return removed
    
    def wait_for_healthy(
        self,
        timeout: int = 120,
        check_interval: int = 10,
        auto_rollback: bool = True,
        rollback_id: Optional[str] = None,
    ) -> bool:
        """
        Wait for server to become healthy after deployment.
        
        Args:
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks
            auto_rollback: Automatically rollback if unhealthy
            rollback_id: Rollback point to use
            
        Returns:
            True if healthy within timeout
        """
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            result = self.run_health_check()
            
            if result.is_healthy:
                logger.info("Server is healthy")
                return True
            
            if result.status == HealthStatus.DEGRADED:
                logger.warning("Server is degraded, continuing to monitor...")
            
            time.sleep(check_interval)
        
        logger.error("Timeout waiting for healthy server")
        
        if auto_rollback:
            logger.info("Auto-rollback triggered")
            self.rollback(rollback_id)
        
        return False
