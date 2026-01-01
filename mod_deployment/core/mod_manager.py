#!/usr/bin/env python3
"""
Mod Manager
===========

High-level mod management operations including install, update, remove.
Handles BepInEx plugin structure and mod configurations.

Author: Mod Deployment Automation Pipeline
"""

import json
import logging
import shutil
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .thunderstore_client import ThunderstoreClient
from .dependency_resolver import DependencyResolver, ResolutionStrategy, ResolutionResult

logger = logging.getLogger(__name__)


@dataclass
class InstalledMod:
    """Represents an installed mod."""
    identifier: str
    version: str
    install_date: str
    install_path: Path
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identifier": self.identifier,
            "version": self.version,
            "install_date": self.install_date,
            "install_path": str(self.install_path),
            "enabled": self.enabled,
            "dependencies": self.dependencies,
            "config_files": self.config_files,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstalledMod":
        return cls(
            identifier=data["identifier"],
            version=data["version"],
            install_date=data["install_date"],
            install_path=Path(data["install_path"]),
            enabled=data.get("enabled", True),
            dependencies=data.get("dependencies", []),
            config_files=data.get("config_files", []),
        )


@dataclass
class InstallResult:
    """Result of a mod installation operation."""
    success: bool
    mod_identifier: str
    version: str
    install_path: Optional[Path] = None
    error: Optional[str] = None
    dependencies_installed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "mod": self.mod_identifier,
            "version": self.version,
            "install_path": str(self.install_path) if self.install_path else None,
            "error": self.error,
            "dependencies_installed": self.dependencies_installed,
        }


class ModManager:
    """
    High-level mod management for game servers.
    
    Features:
    - Install/update/remove mods
    - Dependency resolution
    - BepInEx structure management
    - Mod enable/disable
    - Configuration preservation
    """
    
    # Standard BepInEx directory structure
    BEPINEX_STRUCTURE = {
        "plugins": "BepInEx/plugins",
        "patchers": "BepInEx/patchers",
        "config": "BepInEx/config",
        "core": "BepInEx/core",
    }
    
    def __init__(
        self,
        game_path: Path,
        client: Optional[ThunderstoreClient] = None,
        game: str = "lethal-company",
        auto_dependencies: bool = True,
    ):
        """
        Initialize the mod manager.
        
        Args:
            game_path: Path to game installation
            client: ThunderstoreClient (created if not provided)
            game: Game identifier
            auto_dependencies: Automatically install dependencies
        """
        self.game_path = Path(game_path)
        self.client = client or ThunderstoreClient(game=game)
        self.auto_dependencies = auto_dependencies
        self.resolver = DependencyResolver(self.client)
        
        # Paths
        self.bepinex_path = self.game_path / "BepInEx"
        self.plugins_path = self.bepinex_path / "plugins"
        self.config_path = self.bepinex_path / "config"
        self.manifest_path = self.game_path / "mod_manifest.json"
        self.backup_path = self.game_path / "mod_backups"
        
        # Load installed mods manifest
        self._installed: Dict[str, InstalledMod] = {}
        self._load_manifest()
        
        logger.info(f"ModManager initialized for {self.game_path}")
    
    def _load_manifest(self) -> None:
        """Load the installed mods manifest."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path) as f:
                    data = json.load(f)
                for mod_data in data.get("installed", []):
                    mod = InstalledMod.from_dict(mod_data)
                    self._installed[mod.identifier] = mod
                logger.info(f"Loaded {len(self._installed)} installed mods")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to load manifest: {e}")
    
    def _save_manifest(self) -> None:
        """Save the installed mods manifest."""
        data = {
            "version": "1.0",
            "game": self.client.game,
            "game_path": str(self.game_path),
            "last_updated": datetime.now().isoformat(),
            "installed": [mod.to_dict() for mod in self._installed.values()],
        }
        with open(self.manifest_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def _ensure_bepinex_structure(self) -> None:
        """Ensure BepInEx directory structure exists."""
        for subdir in self.BEPINEX_STRUCTURE.values():
            (self.game_path / subdir).mkdir(parents=True, exist_ok=True)
    
    def get_installed(self) -> Dict[str, str]:
        """Get dict of installed mods (identifier -> version)."""
        return {mod.identifier: mod.version for mod in self._installed.values()}
    
    def is_installed(self, identifier: str) -> bool:
        """Check if a mod is installed."""
        return identifier in self._installed
    
    def get_installed_version(self, identifier: str) -> Optional[str]:
        """Get installed version of a mod."""
        if identifier in self._installed:
            return self._installed[identifier].version
        return None
    
    def install(
        self,
        mod: str,
        version: Optional[str] = None,
        include_dependencies: bool = True,
        dry_run: bool = False,
    ) -> InstallResult:
        """
        Install a mod.
        
        Args:
            mod: Mod identifier (Author-ModName)
            version: Specific version to install
            include_dependencies: Install dependencies automatically
            dry_run: Don't actually install, just check
            
        Returns:
            InstallResult with details
        """
        # Parse mod identifier
        parts = mod.split("-")
        if len(parts) >= 2:
            identifier = f"{parts[0]}-{parts[1]}"
        else:
            identifier = mod
        
        logger.info(f"Installing {identifier}" + (f" v{version}" if version else ""))
        
        # Get package info
        package = self.client.get_package(identifier)
        if not package:
            return InstallResult(
                success=False,
                mod_identifier=identifier,
                version=version or "unknown",
                error=f"Package not found: {identifier}",
            )
        
        # Determine version
        if version:
            target_version = version
        elif package.latest_version:
            target_version = package.latest_version.version_number
        else:
            return InstallResult(
                success=False,
                mod_identifier=identifier,
                version="unknown",
                error="No versions available",
            )
        
        # Check if already installed
        if self.is_installed(identifier):
            installed_version = self.get_installed_version(identifier)
            if installed_version == target_version:
                return InstallResult(
                    success=True,
                    mod_identifier=identifier,
                    version=target_version,
                    install_path=self._installed[identifier].install_path,
                    error="Already installed at this version",
                )
        
        # Resolve dependencies
        deps_installed = []
        if include_dependencies and self.auto_dependencies:
            result = self.resolver.resolve(
                mods=[f"{identifier}-{target_version}"],
                installed=self.get_installed(),
            )
            
            if not result.success and result.missing:
                logger.warning(f"Missing dependencies: {result.missing}")
            
            # Install dependencies first
            for dep_id in result.install_order:
                if dep_id == identifier:
                    continue
                if dep_id not in self._installed:
                    dep_result = self._install_single(
                        dep_id, 
                        result.resolved.get(dep_id),
                        dry_run,
                    )
                    if dep_result.success:
                        deps_installed.append(dep_id)
        
        # Install the main mod
        if dry_run:
            return InstallResult(
                success=True,
                mod_identifier=identifier,
                version=target_version,
                dependencies_installed=deps_installed,
            )
        
        result = self._install_single(identifier, target_version, dry_run=False)
        result.dependencies_installed = deps_installed
        return result
    
    def _install_single(
        self,
        identifier: str,
        version: Optional[str],
        dry_run: bool = False,
    ) -> InstallResult:
        """Install a single mod without dependency resolution."""
        if dry_run:
            return InstallResult(
                success=True,
                mod_identifier=identifier,
                version=version or "latest",
            )
        
        try:
            # Download mod
            zip_path = self.client.download_mod(identifier, version)
            
            # Ensure BepInEx structure
            self._ensure_bepinex_structure()
            
            # Extract to plugins folder
            mod_folder = self.plugins_path / identifier
            mod_folder.mkdir(parents=True, exist_ok=True)
            
            config_files = []
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for member in zf.namelist():
                    # Handle different mod structures
                    if member.startswith("BepInEx/"):
                        # Standard BepInEx structure
                        target = self.game_path / member
                        if member.endswith("/"):
                            target.mkdir(parents=True, exist_ok=True)
                        else:
                            target.parent.mkdir(parents=True, exist_ok=True)
                            with zf.open(member) as src, open(target, "wb") as dst:
                                dst.write(src.read())
                            if "config" in member.lower() and member.endswith(".cfg"):
                                config_files.append(str(target))
                    elif member.startswith("plugins/"):
                        # Plugins subfolder
                        target = self.bepinex_path / member
                        if member.endswith("/"):
                            target.mkdir(parents=True, exist_ok=True)
                        else:
                            target.parent.mkdir(parents=True, exist_ok=True)
                            with zf.open(member) as src, open(target, "wb") as dst:
                                dst.write(src.read())
                    elif not member.endswith("/"):
                        # Extract to mod folder
                        target = mod_folder / member
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(member) as src, open(target, "wb") as dst:
                            dst.write(src.read())
            
            # Get dependencies
            deps = self.client.get_mod_dependencies(identifier, version)
            dep_ids = [d.rsplit("-", 1)[0] if "-" in d else d for d in deps]
            
            # Record installation
            installed_mod = InstalledMod(
                identifier=identifier,
                version=version or "latest",
                install_date=datetime.now().isoformat(),
                install_path=mod_folder,
                dependencies=dep_ids,
                config_files=config_files,
            )
            self._installed[identifier] = installed_mod
            self._save_manifest()
            
            logger.info(f"Installed {identifier} v{version} to {mod_folder}")
            
            return InstallResult(
                success=True,
                mod_identifier=identifier,
                version=version or "latest",
                install_path=mod_folder,
            )
            
        except Exception as e:
            logger.error(f"Failed to install {identifier}: {e}")
            return InstallResult(
                success=False,
                mod_identifier=identifier,
                version=version or "unknown",
                error=str(e),
            )
    
    def update(
        self,
        mod: Optional[str] = None,
        dry_run: bool = False,
    ) -> List[InstallResult]:
        """
        Update installed mods.
        
        Args:
            mod: Specific mod to update (updates all if None)
            dry_run: Check for updates without installing
            
        Returns:
            List of InstallResult for each update
        """
        results = []
        
        if mod:
            mods_to_check = {mod: self._installed.get(mod)}
            mods_to_check = {k: v for k, v in mods_to_check.items() if v}
        else:
            mods_to_check = self._installed
        
        if not mods_to_check:
            logger.info("No mods to update")
            return results
        
        # Check for updates
        updates = self.client.check_for_updates(
            {m.identifier: m.version for m in mods_to_check.values()}
        )
        
        for identifier, update_info in updates.items():
            logger.info(
                f"Update available for {identifier}: "
                f"{update_info['current']} -> {update_info['latest']}"
            )
            
            if not dry_run:
                # Backup current version
                self._backup_mod(identifier)
                
                # Install new version
                result = self.install(
                    identifier,
                    version=update_info['latest'],
                    include_dependencies=True,
                )
                results.append(result)
            else:
                results.append(InstallResult(
                    success=True,
                    mod_identifier=identifier,
                    version=update_info['latest'],
                ))
        
        return results
    
    def remove(
        self,
        mod: str,
        remove_config: bool = False,
        remove_dependents: bool = False,
    ) -> bool:
        """
        Remove an installed mod.
        
        Args:
            mod: Mod identifier
            remove_config: Also remove configuration files
            remove_dependents: Remove mods that depend on this one
            
        Returns:
            True if successful
        """
        if mod not in self._installed:
            logger.warning(f"Mod not installed: {mod}")
            return False
        
        installed_mod = self._installed[mod]
        
        # Check for dependents
        dependents = self._get_dependents(mod)
        if dependents and not remove_dependents:
            logger.error(f"Cannot remove {mod}: required by {dependents}")
            return False
        
        # Remove dependents first
        if dependents and remove_dependents:
            for dep in dependents:
                self.remove(dep, remove_config=remove_config)
        
        try:
            # Remove mod files
            if installed_mod.install_path.exists():
                shutil.rmtree(installed_mod.install_path)
                logger.info(f"Removed {installed_mod.install_path}")
            
            # Remove config if requested
            if remove_config:
                for config_file in installed_mod.config_files:
                    config_path = Path(config_file)
                    if config_path.exists():
                        config_path.unlink()
                        logger.info(f"Removed config: {config_file}")
            
            # Update manifest
            del self._installed[mod]
            self._save_manifest()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove {mod}: {e}")
            return False
    
    def _get_dependents(self, mod: str) -> List[str]:
        """Get list of mods that depend on the given mod."""
        dependents = []
        for installed_mod in self._installed.values():
            if mod in installed_mod.dependencies:
                dependents.append(installed_mod.identifier)
        return dependents
    
    def _backup_mod(self, mod: str) -> Optional[Path]:
        """Backup an installed mod before update."""
        if mod not in self._installed:
            return None
        
        installed_mod = self._installed[mod]
        if not installed_mod.install_path.exists():
            return None
        
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{mod}_{installed_mod.version}_{timestamp}"
        backup_dest = self.backup_path / backup_name
        
        shutil.copytree(installed_mod.install_path, backup_dest)
        logger.info(f"Backed up {mod} to {backup_dest}")
        
        return backup_dest
    
    def enable(self, mod: str) -> bool:
        """Enable a disabled mod."""
        if mod not in self._installed:
            return False
        self._installed[mod].enabled = True
        self._save_manifest()
        return True
    
    def disable(self, mod: str) -> bool:
        """Disable a mod without removing it."""
        if mod not in self._installed:
            return False
        self._installed[mod].enabled = False
        self._save_manifest()
        # Could also rename folder to add .disabled suffix
        return True
    
    def list_installed(self) -> List[Dict[str, Any]]:
        """List all installed mods."""
        return [mod.to_dict() for mod in self._installed.values()]
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall mod status."""
        installed_count = len(self._installed)
        enabled_count = sum(1 for m in self._installed.values() if m.enabled)
        
        # Check for updates
        updates = self.client.check_for_updates(self.get_installed())
        
        return {
            "game": self.client.game,
            "game_path": str(self.game_path),
            "installed_count": installed_count,
            "enabled_count": enabled_count,
            "disabled_count": installed_count - enabled_count,
            "updates_available": len(updates),
            "pending_updates": list(updates.keys()),
        }
