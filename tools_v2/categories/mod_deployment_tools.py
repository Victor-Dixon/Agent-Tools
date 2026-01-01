#!/usr/bin/env python3
"""
Mod Deployment Tools - Agent Toolbelt V2
=========================================

Thunderstore mod deployment automation tools for game servers.
Supports automated installation, updates, dependency resolution, and rollback.

V2 Compliance: <400 lines
Author: Mod Deployment Automation Pipeline
Date: 2025-01-27
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add mod_deployment to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mod_deployment"))

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec

logger = logging.getLogger(__name__)


class ThunderstoreSearchTool(IToolAdapter):
    """Search Thunderstore for mods."""
    
    def get_name(self) -> str:
        return "thunderstore_search"
    
    def get_description(self) -> str:
        return "Search Thunderstore for mods by name, get trending/recent mods"
    
    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="thunderstore_search",
            version="1.0.0",
            category="mod_deployment",
            summary="Search Thunderstore mod repository",
            required_params=["query"],
            optional_params={"game": "lethal-company", "limit": 20, "include_deprecated": False}
        )
    
    def validate(self, params: Dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)
    
    def execute(self, params: Dict[str, Any] = None, context: Dict[str, Any] | None = None) -> ToolResult:
        try:
            from core.thunderstore_client import ThunderstoreClient
            
            params = params or {}
            query = params.get("query", "")
            game = params.get("game", "lethal-company")
            limit = params.get("limit", 20)
            include_deprecated = params.get("include_deprecated", False)
            
            client = ThunderstoreClient(game=game)
            
            if query.lower() == "trending":
                results = client.get_trending(limit=limit)
            elif query.lower() == "recent":
                results = client.get_recently_updated(limit=limit)
            else:
                results = client.search_packages(
                    query=query,
                    include_deprecated=include_deprecated,
                    limit=limit,
                )
            
            output = {
                "query": query,
                "game": game,
                "count": len(results),
                "results": [
                    {
                        "name": pkg.full_name,
                        "owner": pkg.owner,
                        "downloads": pkg.total_downloads,
                        "rating": pkg.rating_score,
                        "latest_version": pkg.latest_version.version_number if pkg.latest_version else "N/A",
                        "deprecated": pkg.is_deprecated,
                    }
                    for pkg in results
                ]
            }
            
            return ToolResult(success=True, output=output)
            
        except Exception as e:
            logger.error(f"Thunderstore search failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class ModInstallTool(IToolAdapter):
    """Install mods from Thunderstore."""
    
    def get_name(self) -> str:
        return "mod_install"
    
    def get_description(self) -> str:
        return "Install a mod from Thunderstore with automatic dependency resolution"
    
    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mod_install",
            version="1.0.0",
            category="mod_deployment",
            summary="Install Thunderstore mod with dependencies",
            required_params=["game_path", "mod"],
            optional_params={"version": None, "game": "lethal-company", "dry_run": False}
        )
    
    def validate(self, params: Dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)
    
    def execute(self, params: Dict[str, Any] = None, context: Dict[str, Any] | None = None) -> ToolResult:
        try:
            from core.mod_manager import ModManager
            
            params = params or {}
            game_path = Path(params["game_path"])
            mod = params["mod"]
            version = params.get("version")
            game = params.get("game", "lethal-company")
            dry_run = params.get("dry_run", False)
            
            manager = ModManager(game_path=game_path, game=game)
            result = manager.install(mod=mod, version=version, dry_run=dry_run)
            
            return ToolResult(success=result.success, output=result.to_dict())
            
        except Exception as e:
            logger.error(f"Mod install failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class ModUpdateTool(IToolAdapter):
    """Check and apply mod updates."""
    
    def get_name(self) -> str:
        return "mod_update"
    
    def get_description(self) -> str:
        return "Check for and apply mod updates from Thunderstore"
    
    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mod_update",
            version="1.0.0",
            category="mod_deployment",
            summary="Update installed mods",
            required_params=["game_path"],
            optional_params={"mod": None, "game": "lethal-company", "dry_run": False}
        )
    
    def validate(self, params: Dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)
    
    def execute(self, params: Dict[str, Any] = None, context: Dict[str, Any] | None = None) -> ToolResult:
        try:
            from core.mod_manager import ModManager
            
            params = params or {}
            game_path = Path(params["game_path"])
            mod = params.get("mod")
            game = params.get("game", "lethal-company")
            dry_run = params.get("dry_run", False)
            
            manager = ModManager(game_path=game_path, game=game)
            results = manager.update(mod=mod, dry_run=dry_run)
            
            output = {
                "updates_found": len(results),
                "dry_run": dry_run,
                "results": [r.to_dict() for r in results]
            }
            
            return ToolResult(success=True, output=output)
            
        except Exception as e:
            logger.error(f"Mod update failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class ModDependencyResolverTool(IToolAdapter):
    """Resolve mod dependencies."""
    
    def get_name(self) -> str:
        return "mod_dependency_resolver"
    
    def get_description(self) -> str:
        return "Resolve dependencies for mods, detect conflicts, calculate install order"
    
    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mod_dependency_resolver",
            version="1.0.0",
            category="mod_deployment",
            summary="Resolve mod dependencies and conflicts",
            required_params=["mods"],
            optional_params={"game": "lethal-company", "installed": None}
        )
    
    def validate(self, params: Dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)
    
    def execute(self, params: Dict[str, Any] = None, context: Dict[str, Any] | None = None) -> ToolResult:
        try:
            from core.thunderstore_client import ThunderstoreClient
            from core.dependency_resolver import DependencyResolver
            
            params = params or {}
            mods = params["mods"]
            if isinstance(mods, str):
                mods = [mods]
            game = params.get("game", "lethal-company")
            installed = params.get("installed", {})
            
            client = ThunderstoreClient(game=game)
            resolver = DependencyResolver(client)
            result = resolver.resolve(mods=mods, installed=installed)
            
            return ToolResult(success=result.success, output=result.to_dict())
            
        except Exception as e:
            logger.error(f"Dependency resolution failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class ModProfileTool(IToolAdapter):
    """Manage mod profiles."""
    
    def get_name(self) -> str:
        return "mod_profile"
    
    def get_description(self) -> str:
        return "Create, switch, and manage mod profiles for different server configurations"
    
    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mod_profile",
            version="1.0.0",
            category="mod_deployment",
            summary="Manage mod profiles",
            required_params=["action"],
            optional_params={
                "profiles_dir": None, "name": None, "description": "",
                "mods": None, "game": "lethal-company", "source_name": None
            }
        )
    
    def validate(self, params: Dict[str, Any]) -> tuple[bool, list[str]]:
        if params.get("action") not in ["list", "create", "delete", "activate", "clone", "compare"]:
            return False, ["action must be one of: list, create, delete, activate, clone, compare"]
        return True, []
    
    def execute(self, params: Dict[str, Any] = None, context: Dict[str, Any] | None = None) -> ToolResult:
        try:
            from core.profile_manager import ProfileManager
            
            params = params or {}
            action = params["action"]
            profiles_dir = Path(params.get("profiles_dir") or Path.home() / ".mod_deployment" / "profiles")
            game = params.get("game", "lethal-company")
            
            manager = ProfileManager(profiles_dir=profiles_dir, game=game)
            
            if action == "list":
                profiles = manager.list()
                output = {"profiles": [p.to_dict() for p in profiles]}
                
            elif action == "create":
                name = params.get("name")
                if not name:
                    return ToolResult(success=False, error_message="name required for create")
                profile = manager.create(
                    name=name,
                    description=params.get("description", ""),
                    mods=params.get("mods", {}),
                )
                output = {"created": profile.to_dict()}
                
            elif action == "delete":
                name = params.get("name")
                if not name:
                    return ToolResult(success=False, error_message="name required for delete")
                success = manager.delete(name)
                output = {"deleted": success, "name": name}
                
            elif action == "activate":
                name = params.get("name")
                if not name:
                    return ToolResult(success=False, error_message="name required for activate")
                success = manager.activate(name)
                output = {"activated": success, "name": name}
                
            elif action == "clone":
                source = params.get("source_name")
                name = params.get("name")
                if not source or not name:
                    return ToolResult(success=False, error_message="source_name and name required")
                profile = manager.clone(source, name, params.get("description"))
                output = {"cloned": profile.to_dict() if profile else None}
                
            elif action == "compare":
                name = params.get("name")
                source = params.get("source_name")
                if not name or not source:
                    return ToolResult(success=False, error_message="name and source_name required")
                output = manager.compare(source, name)
            
            return ToolResult(success=True, output=output)
            
        except Exception as e:
            logger.error(f"Profile operation failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class ServerHealthCheckTool(IToolAdapter):
    """Check game server health after mod deployment."""
    
    def get_name(self) -> str:
        return "server_health_check"
    
    def get_description(self) -> str:
        return "Run health checks on game server, verify BepInEx loaded, check connectivity"
    
    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="server_health_check",
            version="1.0.0",
            category="mod_deployment",
            summary="Check game server health",
            required_params=["game_path"],
            optional_params={"server_host": "localhost", "server_port": 7777}
        )
    
    def validate(self, params: Dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)
    
    def execute(self, params: Dict[str, Any] = None, context: Dict[str, Any] | None = None) -> ToolResult:
        try:
            from core.health_checker import HealthChecker
            
            params = params or {}
            game_path = Path(params["game_path"])
            server_host = params.get("server_host", "localhost")
            server_port = params.get("server_port", 7777)
            
            checker = HealthChecker(
                game_path=game_path,
                server_host=server_host,
                server_port=server_port,
            )
            result = checker.run_health_check()
            
            return ToolResult(success=result.is_healthy, output=result.to_dict())
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class ModRollbackTool(IToolAdapter):
    """Rollback mod deployment to a previous state."""
    
    def get_name(self) -> str:
        return "mod_rollback"
    
    def get_description(self) -> str:
        return "Create rollback points and rollback to previous mod configurations"
    
    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="mod_rollback",
            version="1.0.0",
            category="mod_deployment",
            summary="Rollback mod deployment",
            required_params=["game_path", "action"],
            optional_params={"rollback_id": None, "description": "", "mods_snapshot": None}
        )
    
    def validate(self, params: Dict[str, Any]) -> tuple[bool, list[str]]:
        if params.get("action") not in ["list", "create", "rollback", "cleanup"]:
            return False, ["action must be one of: list, create, rollback, cleanup"]
        return True, []
    
    def execute(self, params: Dict[str, Any] = None, context: Dict[str, Any] | None = None) -> ToolResult:
        try:
            from core.health_checker import HealthChecker
            
            params = params or {}
            game_path = Path(params["game_path"])
            action = params["action"]
            
            checker = HealthChecker(game_path=game_path)
            
            if action == "list":
                points = checker.list_rollback_points()
                output = {"rollback_points": points}
                
            elif action == "create":
                description = params.get("description", "Manual rollback point")
                mods_snapshot = params.get("mods_snapshot", {})
                point = checker.create_rollback_point(description, mods_snapshot)
                output = {"created": point.to_dict()}
                
            elif action == "rollback":
                rollback_id = params.get("rollback_id")
                success = checker.rollback(rollback_id)
                output = {"rolled_back": success, "rollback_id": rollback_id}
                
            elif action == "cleanup":
                removed = checker.cleanup_old_rollback_points(keep=5)
                output = {"removed_count": removed}
            
            return ToolResult(success=True, output=output)
            
        except Exception as e:
            logger.error(f"Rollback operation failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


__all__ = [
    "ThunderstoreSearchTool",
    "ModInstallTool",
    "ModUpdateTool",
    "ModDependencyResolverTool",
    "ModProfileTool",
    "ServerHealthCheckTool",
    "ModRollbackTool",
]
