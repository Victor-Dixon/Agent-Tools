#!/usr/bin/env python3
"""
Backup Manager
==============

Manages game server backups including:
- Full world backups
- Incremental backups
- Scheduled backups
- Backup verification
"""

import hashlib
import json
import logging
import shutil
import tarfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import os

logger = logging.getLogger(__name__)


@dataclass
class BackupMetadata:
    """Metadata for a backup."""
    id: str
    created_at: str
    backup_type: str  # full, incremental, config
    game: str
    source_path: str
    backup_path: str
    size_bytes: int
    file_count: int
    checksum: str
    compression: str
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "backup_type": self.backup_type,
            "game": self.game,
            "source_path": self.source_path,
            "backup_path": self.backup_path,
            "size_bytes": self.size_bytes,
            "size_human": self._human_size(self.size_bytes),
            "file_count": self.file_count,
            "checksum": self.checksum,
            "compression": self.compression,
            "notes": self.notes,
            "tags": self.tags,
            "verified": self.verified,
        }
    
    @staticmethod
    def _human_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BackupMetadata":
        return cls(
            id=data["id"],
            created_at=data["created_at"],
            backup_type=data["backup_type"],
            game=data["game"],
            source_path=data["source_path"],
            backup_path=data["backup_path"],
            size_bytes=data["size_bytes"],
            file_count=data["file_count"],
            checksum=data["checksum"],
            compression=data["compression"],
            notes=data.get("notes", ""),
            tags=data.get("tags", []),
            verified=data.get("verified", False),
        )


@dataclass
class BackupPolicy:
    """Backup retention and scheduling policy."""
    name: str
    hourly_keep: int = 24      # Keep 24 hourly backups
    daily_keep: int = 7        # Keep 7 daily backups
    weekly_keep: int = 4       # Keep 4 weekly backups
    monthly_keep: int = 3      # Keep 3 monthly backups
    
    # What to backup
    include_worlds: bool = True
    include_configs: bool = True
    include_plugins: bool = True
    include_logs: bool = False
    
    # Compression
    compression: str = "gzip"  # gzip, zip, none
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hourly_keep": self.hourly_keep,
            "daily_keep": self.daily_keep,
            "weekly_keep": self.weekly_keep,
            "monthly_keep": self.monthly_keep,
            "include_worlds": self.include_worlds,
            "include_configs": self.include_configs,
            "include_plugins": self.include_plugins,
            "include_logs": self.include_logs,
            "compression": self.compression,
        }


class BackupManager:
    """
    Manages game server backups.
    
    Features:
    - Full and incremental backups
    - Scheduled backups with retention policies
    - Backup verification
    - Multiple compression options
    """
    
    # Default paths to backup for common games
    GAME_PATHS = {
        "minecraft": {
            "worlds": ["world", "world_nether", "world_the_end"],
            "configs": ["server.properties", "bukkit.yml", "spigot.yml", "plugins"],
            "plugins": ["plugins"],
        },
        "valheim": {
            "worlds": [".config/unity3d/IronGate/Valheim/worlds_local"],
            "configs": ["BepInEx/config"],
            "plugins": ["BepInEx/plugins"],
        },
        "lethal-company": {
            "worlds": ["saves"],
            "configs": ["BepInEx/config"],
            "plugins": ["BepInEx/plugins"],
        },
        "palworld": {
            "worlds": ["Pal/Saved/SaveGames"],
            "configs": ["Pal/Saved/Config"],
            "plugins": ["BepInEx/plugins"],
        },
    }
    
    def __init__(
        self,
        game_path: Path,
        backup_path: Path,
        game: str = "generic",
        policy: Optional[BackupPolicy] = None,
    ):
        self.game_path = Path(game_path)
        self.backup_path = Path(backup_path)
        self.game = game.lower()
        self.policy = policy or BackupPolicy(name="default")
        
        self.backup_path.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.backup_path / "backup_manifest.json"
        
        self._backups: Dict[str, BackupMetadata] = {}
        self._load_manifest()
    
    def _load_manifest(self) -> None:
        """Load backup manifest."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path) as f:
                    data = json.load(f)
                for backup_data in data.get("backups", []):
                    backup = BackupMetadata.from_dict(backup_data)
                    self._backups[backup.id] = backup
            except Exception as e:
                logger.warning(f"Failed to load manifest: {e}")
    
    def _save_manifest(self) -> None:
        """Save backup manifest."""
        data = {
            "version": "1.0",
            "game": self.game,
            "game_path": str(self.game_path),
            "policy": self.policy.to_dict(),
            "backups": [b.to_dict() for b in self._backups.values()],
        }
        with open(self.manifest_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def _get_paths_to_backup(self) -> List[Path]:
        """Get list of paths to backup based on policy and game."""
        paths = []
        
        game_config = self.GAME_PATHS.get(self.game, {})
        
        if self.policy.include_worlds:
            for world_path in game_config.get("worlds", ["worlds", "saves", "world"]):
                full_path = self.game_path / world_path
                if full_path.exists():
                    paths.append(full_path)
        
        if self.policy.include_configs:
            for config_path in game_config.get("configs", ["config", "BepInEx/config"]):
                full_path = self.game_path / config_path
                if full_path.exists():
                    paths.append(full_path)
        
        if self.policy.include_plugins:
            for plugin_path in game_config.get("plugins", ["plugins", "BepInEx/plugins"]):
                full_path = self.game_path / plugin_path
                if full_path.exists():
                    paths.append(full_path)
        
        if self.policy.include_logs:
            for log_path in ["logs", "log", "BepInEx/LogOutput.log"]:
                full_path = self.game_path / log_path
                if full_path.exists():
                    paths.append(full_path)
        
        return paths
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def create_backup(
        self,
        backup_type: str = "full",
        notes: str = "",
        tags: Optional[List[str]] = None,
    ) -> BackupMetadata:
        """
        Create a new backup.
        
        Args:
            backup_type: Type of backup (full, incremental, config)
            notes: Optional notes about the backup
            tags: Optional tags for categorization
            
        Returns:
            BackupMetadata for the created backup
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"{self.game}_{backup_type}_{timestamp}"
        
        # Determine paths to backup
        paths = self._get_paths_to_backup()
        
        if not paths:
            raise ValueError(f"No valid paths found to backup at {self.game_path}")
        
        # Create backup file
        if self.policy.compression == "zip":
            backup_file = self.backup_path / f"{backup_id}.zip"
            file_count = self._create_zip_backup(paths, backup_file)
        elif self.policy.compression == "gzip":
            backup_file = self.backup_path / f"{backup_id}.tar.gz"
            file_count = self._create_tar_backup(paths, backup_file)
        else:
            backup_file = self.backup_path / f"{backup_id}.tar"
            file_count = self._create_tar_backup(paths, backup_file, compress=False)
        
        # Calculate checksum
        checksum = self._calculate_checksum(backup_file)
        
        # Create metadata
        metadata = BackupMetadata(
            id=backup_id,
            created_at=datetime.now().isoformat(),
            backup_type=backup_type,
            game=self.game,
            source_path=str(self.game_path),
            backup_path=str(backup_file),
            size_bytes=backup_file.stat().st_size,
            file_count=file_count,
            checksum=checksum,
            compression=self.policy.compression,
            notes=notes,
            tags=tags or [],
        )
        
        self._backups[backup_id] = metadata
        self._save_manifest()
        
        logger.info(f"Created backup: {backup_id} ({metadata._human_size(metadata.size_bytes)})")
        return metadata
    
    def _create_zip_backup(self, paths: List[Path], output: Path) -> int:
        """Create a ZIP backup."""
        file_count = 0
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in paths:
                if path.is_file():
                    arcname = path.relative_to(self.game_path)
                    zf.write(path, arcname)
                    file_count += 1
                elif path.is_dir():
                    for file_path in path.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(self.game_path)
                            zf.write(file_path, arcname)
                            file_count += 1
        return file_count
    
    def _create_tar_backup(
        self, 
        paths: List[Path], 
        output: Path,
        compress: bool = True,
    ) -> int:
        """Create a TAR backup."""
        file_count = 0
        mode = "w:gz" if compress else "w"
        
        with tarfile.open(output, mode) as tf:
            for path in paths:
                if path.exists():
                    arcname = str(path.relative_to(self.game_path))
                    tf.add(path, arcname)
                    if path.is_file():
                        file_count += 1
                    else:
                        file_count += sum(1 for f in path.rglob("*") if f.is_file())
        
        return file_count
    
    def verify_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Verify a backup's integrity.
        
        Args:
            backup_id: ID of backup to verify
            
        Returns:
            Verification result
        """
        if backup_id not in self._backups:
            return {"success": False, "error": "Backup not found"}
        
        metadata = self._backups[backup_id]
        backup_file = Path(metadata.backup_path)
        
        if not backup_file.exists():
            return {"success": False, "error": "Backup file missing"}
        
        # Verify checksum
        current_checksum = self._calculate_checksum(backup_file)
        checksum_valid = current_checksum == metadata.checksum
        
        # Try to read the archive
        readable = False
        file_count = 0
        
        try:
            if metadata.compression == "zip":
                with zipfile.ZipFile(backup_file, "r") as zf:
                    file_count = len(zf.namelist())
                    readable = zf.testzip() is None
            else:
                with tarfile.open(backup_file, "r:*") as tf:
                    file_count = len(tf.getnames())
                    readable = True
        except Exception as e:
            return {"success": False, "error": f"Archive corrupted: {e}"}
        
        # Update metadata
        metadata.verified = checksum_valid and readable
        self._save_manifest()
        
        return {
            "success": checksum_valid and readable,
            "backup_id": backup_id,
            "checksum_valid": checksum_valid,
            "readable": readable,
            "file_count": file_count,
            "expected_file_count": metadata.file_count,
        }
    
    def list_backups(
        self,
        backup_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[BackupMetadata]:
        """List backups with optional filtering."""
        backups = list(self._backups.values())
        
        if backup_type:
            backups = [b for b in backups if b.backup_type == backup_type]
        
        # Sort by creation time, newest first
        backups.sort(key=lambda b: b.created_at, reverse=True)
        
        return backups[:limit]
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        if backup_id not in self._backups:
            return False
        
        metadata = self._backups[backup_id]
        backup_file = Path(metadata.backup_path)
        
        try:
            if backup_file.exists():
                backup_file.unlink()
            del self._backups[backup_id]
            self._save_manifest()
            logger.info(f"Deleted backup: {backup_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False
    
    def apply_retention_policy(self) -> Dict[str, int]:
        """
        Apply retention policy to delete old backups.
        
        Returns:
            Summary of deleted backups by type
        """
        deleted = {"hourly": 0, "daily": 0, "weekly": 0, "monthly": 0}
        now = datetime.now()
        
        # Group backups by age category
        for backup in list(self._backups.values()):
            backup_time = datetime.fromisoformat(backup.created_at)
            age = now - backup_time
            
            # Determine which retention limit applies
            if age < timedelta(hours=24):
                # Hourly backups
                hourly_backups = [
                    b for b in self._backups.values()
                    if (now - datetime.fromisoformat(b.created_at)) < timedelta(hours=24)
                ]
                if len(hourly_backups) > self.policy.hourly_keep:
                    # Delete oldest
                    oldest = min(hourly_backups, key=lambda b: b.created_at)
                    if self.delete_backup(oldest.id):
                        deleted["hourly"] += 1
            
            elif age < timedelta(days=7):
                # Daily backups
                daily_backups = [
                    b for b in self._backups.values()
                    if timedelta(hours=24) <= (now - datetime.fromisoformat(b.created_at)) < timedelta(days=7)
                ]
                if len(daily_backups) > self.policy.daily_keep:
                    oldest = min(daily_backups, key=lambda b: b.created_at)
                    if self.delete_backup(oldest.id):
                        deleted["daily"] += 1
            
            elif age < timedelta(days=30):
                # Weekly backups
                weekly_backups = [
                    b for b in self._backups.values()
                    if timedelta(days=7) <= (now - datetime.fromisoformat(b.created_at)) < timedelta(days=30)
                ]
                if len(weekly_backups) > self.policy.weekly_keep:
                    oldest = min(weekly_backups, key=lambda b: b.created_at)
                    if self.delete_backup(oldest.id):
                        deleted["weekly"] += 1
            
            else:
                # Monthly backups
                monthly_backups = [
                    b for b in self._backups.values()
                    if (now - datetime.fromisoformat(b.created_at)) >= timedelta(days=30)
                ]
                if len(monthly_backups) > self.policy.monthly_keep:
                    oldest = min(monthly_backups, key=lambda b: b.created_at)
                    if self.delete_backup(oldest.id):
                        deleted["monthly"] += 1
        
        return deleted
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """Get backup storage usage statistics."""
        total_size = sum(b.size_bytes for b in self._backups.values())
        backup_count = len(self._backups)
        
        by_type = {}
        for backup in self._backups.values():
            if backup.backup_type not in by_type:
                by_type[backup.backup_type] = {"count": 0, "size": 0}
            by_type[backup.backup_type]["count"] += 1
            by_type[backup.backup_type]["size"] += backup.size_bytes
        
        # Get disk space
        try:
            stat = shutil.disk_usage(self.backup_path)
            disk_free = stat.free
            disk_total = stat.total
        except:
            disk_free = 0
            disk_total = 0
        
        return {
            "total_backups": backup_count,
            "total_size_bytes": total_size,
            "total_size_human": BackupMetadata._human_size(total_size),
            "by_type": by_type,
            "disk_free_bytes": disk_free,
            "disk_total_bytes": disk_total,
            "disk_free_human": BackupMetadata._human_size(disk_free),
        }
