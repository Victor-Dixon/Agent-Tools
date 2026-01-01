#!/usr/bin/env python3
"""
MCP Server for Backup Automation
=================================

Exposes game server backup operations via Model Context Protocol.

Tools:
- create_backup: Create a new backup
- list_backups: List available backups
- restore_backup: Restore from a backup
- verify_backup: Verify backup integrity
- sync_to_cloud: Sync backups to cloud storage
- apply_retention: Apply retention policy to cleanup old backups
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backup_automation"))

try:
    from core.backup_manager import BackupManager, BackupPolicy
    from core.recovery_manager import RecoveryManager
    from core.cloud_sync import CloudSync, CloudConfig
    HAS_BACKUP = True
except ImportError as e:
    HAS_BACKUP = False
    import_error = str(e)


def create_backup(
    game_path: str,
    backup_path: str,
    game: str = "generic",
    backup_type: str = "full",
    notes: str = "",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new backup."""
    if not HAS_BACKUP:
        return {"success": False, "error": f"Backup not available: {import_error}"}
    
    try:
        manager = BackupManager(
            game_path=Path(game_path),
            backup_path=Path(backup_path),
            game=game,
        )
        
        metadata = manager.create_backup(
            backup_type=backup_type,
            notes=notes,
            tags=tags or [],
        )
        
        return {"success": True, "backup": metadata.to_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_backups(
    backup_path: str,
    backup_type: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """List available backups."""
    if not HAS_BACKUP:
        return {"success": False, "error": "Backup not available"}
    
    try:
        # Create manager with dummy game path
        manager = BackupManager(
            game_path=Path("/tmp"),
            backup_path=Path(backup_path),
        )
        
        backups = manager.list_backups(backup_type=backup_type, limit=limit)
        
        return {
            "success": True,
            "count": len(backups),
            "backups": [b.to_dict() for b in backups],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def restore_backup(
    backup_path: str,
    backup_id: str,
    target_path: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Restore from a backup."""
    if not HAS_BACKUP:
        return {"success": False, "error": "Backup not available"}
    
    try:
        manager = BackupManager(
            game_path=Path(target_path or "/tmp"),
            backup_path=Path(backup_path),
        )
        
        recovery = RecoveryManager(manager)
        
        result = recovery.restore(
            backup_id=backup_id,
            target_path=Path(target_path) if target_path else None,
            dry_run=dry_run,
        )
        
        return {"success": result.success, "result": result.to_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_backup(
    backup_path: str,
    backup_id: str,
) -> Dict[str, Any]:
    """Verify backup integrity."""
    if not HAS_BACKUP:
        return {"success": False, "error": "Backup not available"}
    
    try:
        manager = BackupManager(
            game_path=Path("/tmp"),
            backup_path=Path(backup_path),
        )
        
        result = manager.verify_backup(backup_id)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_storage_usage(backup_path: str) -> Dict[str, Any]:
    """Get backup storage usage statistics."""
    if not HAS_BACKUP:
        return {"success": False, "error": "Backup not available"}
    
    try:
        manager = BackupManager(
            game_path=Path("/tmp"),
            backup_path=Path(backup_path),
        )
        
        usage = manager.get_storage_usage()
        return {"success": True, "usage": usage}
    except Exception as e:
        return {"success": False, "error": str(e)}


def apply_retention(backup_path: str) -> Dict[str, Any]:
    """Apply retention policy to cleanup old backups."""
    if not HAS_BACKUP:
        return {"success": False, "error": "Backup not available"}
    
    try:
        manager = BackupManager(
            game_path=Path("/tmp"),
            backup_path=Path(backup_path),
        )
        
        deleted = manager.apply_retention_policy()
        return {"success": True, "deleted": deleted}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_backup_contents(
    backup_path: str,
    backup_id: str,
) -> Dict[str, Any]:
    """List contents of a backup."""
    if not HAS_BACKUP:
        return {"success": False, "error": "Backup not available"}
    
    try:
        manager = BackupManager(
            game_path=Path("/tmp"),
            backup_path=Path(backup_path),
        )
        
        recovery = RecoveryManager(manager)
        return recovery.list_backup_contents(backup_id)
    except Exception as e:
        return {"success": False, "error": str(e)}


def compare_backups(
    backup_path: str,
    backup_id_1: str,
    backup_id_2: str,
) -> Dict[str, Any]:
    """Compare two backups to see what changed."""
    if not HAS_BACKUP:
        return {"success": False, "error": "Backup not available"}
    
    try:
        manager = BackupManager(
            game_path=Path("/tmp"),
            backup_path=Path(backup_path),
        )
        
        recovery = RecoveryManager(manager)
        return recovery.compare_backups(backup_id_1, backup_id_2)
    except Exception as e:
        return {"success": False, "error": str(e)}


def sync_to_cloud(
    backup_path: str,
    provider: str = "s3",
    bucket: str = "",
    prefix: str = "game-backups",
    endpoint_url: str = "",
    force: bool = False,
) -> Dict[str, Any]:
    """Sync backups to cloud storage."""
    if not HAS_BACKUP:
        return {"success": False, "error": "Backup not available"}
    
    try:
        config = CloudConfig(
            provider=provider,
            bucket=bucket,
            prefix=prefix,
            endpoint_url=endpoint_url,
        )
        
        sync = CloudSync(
            backup_path=Path(backup_path),
            config=config,
        )
        
        result = sync.sync_to_cloud(force=force)
        return {"success": result.success, "result": result.to_dict()}
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
                            "create_backup": {
                                "description": "Create a new backup of game server data",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string", "description": "Path to game server"},
                                        "backup_path": {"type": "string", "description": "Where to store backups"},
                                        "game": {"type": "string", "default": "generic"},
                                        "backup_type": {"type": "string", "enum": ["full", "incremental", "config"]},
                                        "notes": {"type": "string"},
                                        "tags": {"type": "array", "items": {"type": "string"}},
                                    },
                                    "required": ["game_path", "backup_path"],
                                },
                            },
                            "list_backups": {
                                "description": "List available backups",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "backup_path": {"type": "string"},
                                        "backup_type": {"type": "string"},
                                        "limit": {"type": "integer", "default": 20},
                                    },
                                    "required": ["backup_path"],
                                },
                            },
                            "restore_backup": {
                                "description": "Restore game server from a backup",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "backup_path": {"type": "string"},
                                        "backup_id": {"type": "string"},
                                        "target_path": {"type": "string"},
                                        "dry_run": {"type": "boolean", "default": False},
                                    },
                                    "required": ["backup_path", "backup_id"],
                                },
                            },
                            "verify_backup": {
                                "description": "Verify backup integrity (checksum, readability)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "backup_path": {"type": "string"},
                                        "backup_id": {"type": "string"},
                                    },
                                    "required": ["backup_path", "backup_id"],
                                },
                            },
                            "get_storage_usage": {
                                "description": "Get backup storage usage statistics",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "backup_path": {"type": "string"},
                                    },
                                    "required": ["backup_path"],
                                },
                            },
                            "apply_retention": {
                                "description": "Apply retention policy to cleanup old backups",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "backup_path": {"type": "string"},
                                    },
                                    "required": ["backup_path"],
                                },
                            },
                            "list_backup_contents": {
                                "description": "List files inside a backup without extracting",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "backup_path": {"type": "string"},
                                        "backup_id": {"type": "string"},
                                    },
                                    "required": ["backup_path", "backup_id"],
                                },
                            },
                            "compare_backups": {
                                "description": "Compare two backups to see what changed",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "backup_path": {"type": "string"},
                                        "backup_id_1": {"type": "string"},
                                        "backup_id_2": {"type": "string"},
                                    },
                                    "required": ["backup_path", "backup_id_1", "backup_id_2"],
                                },
                            },
                            "sync_to_cloud": {
                                "description": "Sync backups to cloud storage (S3, B2, etc.)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "backup_path": {"type": "string"},
                                        "provider": {"type": "string", "enum": ["s3", "b2", "local"]},
                                        "bucket": {"type": "string"},
                                        "prefix": {"type": "string", "default": "game-backups"},
                                        "endpoint_url": {"type": "string"},
                                        "force": {"type": "boolean", "default": False},
                                    },
                                    "required": ["backup_path", "bucket"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "backup-automation", "version": "1.0.0"},
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

                if tool_name == "create_backup":
                    result = create_backup(**arguments)
                elif tool_name == "list_backups":
                    result = list_backups(**arguments)
                elif tool_name == "restore_backup":
                    result = restore_backup(**arguments)
                elif tool_name == "verify_backup":
                    result = verify_backup(**arguments)
                elif tool_name == "get_storage_usage":
                    result = get_storage_usage(**arguments)
                elif tool_name == "apply_retention":
                    result = apply_retention(**arguments)
                elif tool_name == "list_backup_contents":
                    result = list_backup_contents(**arguments)
                elif tool_name == "compare_backups":
                    result = compare_backups(**arguments)
                elif tool_name == "sync_to_cloud":
                    result = sync_to_cloud(**arguments)
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
