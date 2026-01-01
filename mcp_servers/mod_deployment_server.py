#!/usr/bin/env python3
"""
MCP Server for Mod Deployment Automation
=========================================

Exposes Thunderstore mod deployment operations via Model Context Protocol.
Enables AI agents to automate game server mod management.

Features:
- Search Thunderstore mods
- Install/update/remove mods
- Dependency resolution
- Profile management
- Health checks and rollback
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mod_deployment"))

try:
    from core.thunderstore_client import ThunderstoreClient
    from core.mod_manager import ModManager
    from core.dependency_resolver import DependencyResolver
    from core.profile_manager import ProfileManager
    from core.health_checker import HealthChecker
    HAS_MOD_DEPLOYMENT = True
except ImportError as e:
    HAS_MOD_DEPLOYMENT = False
    import_error = str(e)


def search_mods(
    query: str,
    game: str = "lethal-company",
    limit: int = 20,
) -> Dict[str, Any]:
    """Search Thunderstore for mods."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": f"Mod deployment not available: {import_error}"}
    
    try:
        client = ThunderstoreClient(game=game)
        
        if query.lower() == "trending":
            results = client.get_trending(limit=limit)
        elif query.lower() == "recent":
            results = client.get_recently_updated(limit=limit)
        else:
            results = client.search_packages(query=query, limit=limit)
        
        return {
            "success": True,
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
                }
                for pkg in results
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_mod_info(
    mod: str,
    game: str = "lethal-company",
) -> Dict[str, Any]:
    """Get detailed information about a mod."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": "Mod deployment not available"}
    
    try:
        client = ThunderstoreClient(game=game)
        package = client.get_package(mod)
        
        if not package:
            return {"success": False, "error": f"Package not found: {mod}"}
        
        return {
            "success": True,
            "mod": {
                "name": package.name,
                "full_name": package.full_name,
                "owner": package.owner,
                "downloads": package.total_downloads,
                "rating": package.rating_score,
                "deprecated": package.is_deprecated,
                "categories": package.categories,
                "versions": [
                    {
                        "version": v.version_number,
                        "downloads": v.downloads,
                        "date": v.date_created,
                        "dependencies": v.dependencies,
                    }
                    for v in package.versions[:5]  # Last 5 versions
                ]
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def install_mod(
    game_path: str,
    mod: str,
    version: Optional[str] = None,
    game: str = "lethal-company",
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Install a mod from Thunderstore."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": "Mod deployment not available"}
    
    try:
        manager = ModManager(game_path=Path(game_path), game=game)
        result = manager.install(mod=mod, version=version, dry_run=dry_run)
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_mods(
    game_path: str,
    mod: Optional[str] = None,
    game: str = "lethal-company",
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Check for and apply mod updates."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": "Mod deployment not available"}
    
    try:
        manager = ModManager(game_path=Path(game_path), game=game)
        results = manager.update(mod=mod, dry_run=dry_run)
        return {
            "success": True,
            "updates_found": len(results),
            "dry_run": dry_run,
            "results": [r.to_dict() for r in results]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_installed_mods(
    game_path: str,
    game: str = "lethal-company",
) -> Dict[str, Any]:
    """List installed mods."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": "Mod deployment not available"}
    
    try:
        manager = ModManager(game_path=Path(game_path), game=game)
        installed = manager.list_installed()
        status = manager.get_status()
        return {
            "success": True,
            "status": status,
            "mods": installed,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def resolve_dependencies(
    mods: List[str],
    game: str = "lethal-company",
    installed: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Resolve dependencies for mods."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": "Mod deployment not available"}
    
    try:
        client = ThunderstoreClient(game=game)
        resolver = DependencyResolver(client)
        result = resolver.resolve(mods=mods, installed=installed or {})
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_server_health(
    game_path: str,
    server_host: str = "localhost",
    server_port: int = 7777,
) -> Dict[str, Any]:
    """Check game server health."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": "Mod deployment not available"}
    
    try:
        checker = HealthChecker(
            game_path=Path(game_path),
            server_host=server_host,
            server_port=server_port,
        )
        result = checker.run_health_check()
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_rollback_point(
    game_path: str,
    description: str,
    mods_snapshot: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Create a rollback point before deployment."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": "Mod deployment not available"}
    
    try:
        checker = HealthChecker(game_path=Path(game_path))
        point = checker.create_rollback_point(description, mods_snapshot or {})
        return {"success": True, "rollback_point": point.to_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def rollback(
    game_path: str,
    rollback_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Rollback to a previous state."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": "Mod deployment not available"}
    
    try:
        checker = HealthChecker(game_path=Path(game_path))
        success = checker.rollback(rollback_id)
        return {"success": success, "rollback_id": rollback_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


def manage_profile(
    action: str,
    profiles_dir: Optional[str] = None,
    name: Optional[str] = None,
    description: str = "",
    mods: Optional[Dict[str, str]] = None,
    game: str = "lethal-company",
    source_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Manage mod profiles."""
    if not HAS_MOD_DEPLOYMENT:
        return {"success": False, "error": "Mod deployment not available"}
    
    try:
        profiles_path = Path(profiles_dir) if profiles_dir else Path.home() / ".mod_deployment" / "profiles"
        manager = ProfileManager(profiles_dir=profiles_path, game=game)
        
        if action == "list":
            profiles = manager.list()
            return {"success": True, "profiles": [p.to_dict() for p in profiles]}
        
        elif action == "create":
            if not name:
                return {"success": False, "error": "name required"}
            profile = manager.create(name=name, description=description, mods=mods or {})
            return {"success": True, "profile": profile.to_dict()}
        
        elif action == "activate":
            if not name:
                return {"success": False, "error": "name required"}
            success = manager.activate(name)
            return {"success": success, "activated": name}
        
        elif action == "delete":
            if not name:
                return {"success": False, "error": "name required"}
            success = manager.delete(name)
            return {"success": success, "deleted": name}
        
        elif action == "clone":
            if not source_name or not name:
                return {"success": False, "error": "source_name and name required"}
            profile = manager.clone(source_name, name, description)
            return {"success": True, "profile": profile.to_dict() if profile else None}
        
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


# MCP Server Protocol
def main():
    """MCP server main loop."""
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "search_mods": {
                                "description": "Search Thunderstore for mods by name, or get trending/recent mods",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "Search query (or 'trending'/'recent')"},
                                        "game": {"type": "string", "default": "lethal-company", "description": "Game (lethal-company, valheim, etc.)"},
                                        "limit": {"type": "integer", "default": 20, "description": "Max results"},
                                    },
                                    "required": ["query"],
                                },
                            },
                            "get_mod_info": {
                                "description": "Get detailed information about a specific mod",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "mod": {"type": "string", "description": "Mod identifier (Author-ModName)"},
                                        "game": {"type": "string", "default": "lethal-company"},
                                    },
                                    "required": ["mod"],
                                },
                            },
                            "install_mod": {
                                "description": "Install a mod from Thunderstore with dependency resolution",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string", "description": "Path to game installation"},
                                        "mod": {"type": "string", "description": "Mod identifier"},
                                        "version": {"type": "string", "description": "Specific version (default: latest)"},
                                        "game": {"type": "string", "default": "lethal-company"},
                                        "dry_run": {"type": "boolean", "default": False},
                                    },
                                    "required": ["game_path", "mod"],
                                },
                            },
                            "update_mods": {
                                "description": "Check for and apply mod updates",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string", "description": "Path to game installation"},
                                        "mod": {"type": "string", "description": "Specific mod (default: all)"},
                                        "game": {"type": "string", "default": "lethal-company"},
                                        "dry_run": {"type": "boolean", "default": False},
                                    },
                                    "required": ["game_path"],
                                },
                            },
                            "list_installed_mods": {
                                "description": "List all installed mods",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string"},
                                        "game": {"type": "string", "default": "lethal-company"},
                                    },
                                    "required": ["game_path"],
                                },
                            },
                            "resolve_dependencies": {
                                "description": "Resolve dependencies for mods, detect conflicts",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "mods": {"type": "array", "items": {"type": "string"}, "description": "List of mods"},
                                        "game": {"type": "string", "default": "lethal-company"},
                                        "installed": {"type": "object", "description": "Currently installed mods"},
                                    },
                                    "required": ["mods"],
                                },
                            },
                            "check_server_health": {
                                "description": "Check game server health after mod deployment",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string"},
                                        "server_host": {"type": "string", "default": "localhost"},
                                        "server_port": {"type": "integer", "default": 7777},
                                    },
                                    "required": ["game_path"],
                                },
                            },
                            "create_rollback_point": {
                                "description": "Create a rollback point before deployment",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string"},
                                        "description": {"type": "string"},
                                        "mods_snapshot": {"type": "object"},
                                    },
                                    "required": ["game_path", "description"],
                                },
                            },
                            "rollback": {
                                "description": "Rollback to a previous state",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string"},
                                        "rollback_id": {"type": "string", "description": "ID (default: latest)"},
                                    },
                                    "required": ["game_path"],
                                },
                            },
                            "manage_profile": {
                                "description": "Manage mod profiles (list, create, activate, delete, clone)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string", "enum": ["list", "create", "activate", "delete", "clone"]},
                                        "profiles_dir": {"type": "string"},
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "mods": {"type": "object"},
                                        "game": {"type": "string", "default": "lethal-company"},
                                        "source_name": {"type": "string", "description": "For clone action"},
                                    },
                                    "required": ["action"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "mod-deployment-server", "version": "1.0.0"},
                },
            }
        )
    )

    # Handle tool calls
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "search_mods":
                    result = search_mods(**arguments)
                elif tool_name == "get_mod_info":
                    result = get_mod_info(**arguments)
                elif tool_name == "install_mod":
                    result = install_mod(**arguments)
                elif tool_name == "update_mods":
                    result = update_mods(**arguments)
                elif tool_name == "list_installed_mods":
                    result = list_installed_mods(**arguments)
                elif tool_name == "resolve_dependencies":
                    result = resolve_dependencies(**arguments)
                elif tool_name == "check_server_health":
                    result = check_server_health(**arguments)
                elif tool_name == "create_rollback_point":
                    result = create_rollback_point(**arguments)
                elif tool_name == "rollback":
                    result = rollback(**arguments)
                elif tool_name == "manage_profile":
                    result = manage_profile(**arguments)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
                        }
                    )
                )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if 'request' in dir() else None,
                        "error": {"code": -32603, "message": str(e)},
                    }
                )
            )


if __name__ == "__main__":
    main()
