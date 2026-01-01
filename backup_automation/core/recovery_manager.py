#!/usr/bin/env python3
"""
Recovery Manager
================

Handles restoration from backups with safety checks
and point-in-time recovery support.
"""

import json
import logging
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .backup_manager import BackupMetadata, BackupManager

logger = logging.getLogger(__name__)


@dataclass
class RecoveryResult:
    """Result of a recovery operation."""
    success: bool
    backup_id: str
    restored_path: str
    files_restored: int
    duration_seconds: float
    pre_recovery_backup_id: Optional[str] = None
    errors: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "backup_id": self.backup_id,
            "restored_path": self.restored_path,
            "files_restored": self.files_restored,
            "duration_seconds": self.duration_seconds,
            "pre_recovery_backup_id": self.pre_recovery_backup_id,
            "errors": self.errors or [],
        }


class RecoveryManager:
    """
    Manages recovery/restoration operations.
    
    Features:
    - Full restoration from backup
    - Selective file restoration
    - Pre-recovery safety backup
    - Dry-run mode
    - Recovery verification
    """
    
    def __init__(
        self,
        backup_manager: BackupManager,
        always_backup_before_restore: bool = True,
    ):
        self.backup_manager = backup_manager
        self.always_backup = always_backup_before_restore
    
    def restore(
        self,
        backup_id: str,
        target_path: Optional[Path] = None,
        dry_run: bool = False,
        selective_paths: Optional[List[str]] = None,
    ) -> RecoveryResult:
        """
        Restore from a backup.
        
        Args:
            backup_id: ID of backup to restore from
            target_path: Where to restore (default: original location)
            dry_run: Preview without actually restoring
            selective_paths: Only restore specific paths
            
        Returns:
            RecoveryResult with details
        """
        start_time = datetime.now()
        errors = []
        pre_backup_id = None
        
        # Find backup
        backups = {b.id: b for b in self.backup_manager.list_backups(limit=1000)}
        if backup_id not in backups:
            return RecoveryResult(
                success=False,
                backup_id=backup_id,
                restored_path="",
                files_restored=0,
                duration_seconds=0,
                errors=["Backup not found"],
            )
        
        metadata = backups[backup_id]
        backup_file = Path(metadata.backup_path)
        
        if not backup_file.exists():
            return RecoveryResult(
                success=False,
                backup_id=backup_id,
                restored_path="",
                files_restored=0,
                duration_seconds=0,
                errors=["Backup file missing"],
            )
        
        # Determine target
        target = target_path or Path(metadata.source_path)
        
        logger.info(f"{'[DRY-RUN] ' if dry_run else ''}Restoring {backup_id} to {target}")
        
        # Create pre-recovery backup if enabled and not dry run
        if self.always_backup and not dry_run and target.exists():
            try:
                pre_backup = self.backup_manager.create_backup(
                    backup_type="pre-recovery",
                    notes=f"Automatic backup before restoring {backup_id}",
                    tags=["auto", "pre-recovery"],
                )
                pre_backup_id = pre_backup.id
                logger.info(f"Created pre-recovery backup: {pre_backup_id}")
            except Exception as e:
                errors.append(f"Failed to create pre-recovery backup: {e}")
        
        if dry_run:
            # Just list what would be restored
            files_count = self._count_files_in_backup(backup_file, metadata.compression)
            return RecoveryResult(
                success=True,
                backup_id=backup_id,
                restored_path=str(target),
                files_restored=files_count,
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                errors=["DRY-RUN: No files actually restored"],
            )
        
        # Perform restoration
        try:
            files_restored = self._extract_backup(
                backup_file,
                target,
                metadata.compression,
                selective_paths,
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return RecoveryResult(
                success=True,
                backup_id=backup_id,
                restored_path=str(target),
                files_restored=files_restored,
                duration_seconds=duration,
                pre_recovery_backup_id=pre_backup_id,
                errors=errors if errors else None,
            )
            
        except Exception as e:
            logger.error(f"Restoration failed: {e}")
            errors.append(str(e))
            
            return RecoveryResult(
                success=False,
                backup_id=backup_id,
                restored_path=str(target),
                files_restored=0,
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                pre_recovery_backup_id=pre_backup_id,
                errors=errors,
            )
    
    def _count_files_in_backup(self, backup_file: Path, compression: str) -> int:
        """Count files in a backup without extracting."""
        try:
            if compression == "zip":
                with zipfile.ZipFile(backup_file, "r") as zf:
                    return len([n for n in zf.namelist() if not n.endswith("/")])
            else:
                with tarfile.open(backup_file, "r:*") as tf:
                    return len([m for m in tf.getmembers() if m.isfile()])
        except Exception:
            return 0
    
    def _extract_backup(
        self,
        backup_file: Path,
        target: Path,
        compression: str,
        selective: Optional[List[str]] = None,
    ) -> int:
        """Extract backup to target directory."""
        target.mkdir(parents=True, exist_ok=True)
        files_restored = 0
        
        if compression == "zip":
            with zipfile.ZipFile(backup_file, "r") as zf:
                members = zf.namelist()
                
                if selective:
                    members = [m for m in members if any(
                        m.startswith(s) or s in m for s in selective
                    )]
                
                for member in members:
                    if not member.endswith("/"):
                        zf.extract(member, target)
                        files_restored += 1
        else:
            with tarfile.open(backup_file, "r:*") as tf:
                members = tf.getmembers()
                
                if selective:
                    members = [m for m in members if any(
                        m.name.startswith(s) or s in m.name for s in selective
                    )]
                
                for member in members:
                    if member.isfile():
                        tf.extract(member, target)
                        files_restored += 1
        
        return files_restored
    
    def list_backup_contents(self, backup_id: str) -> Dict[str, Any]:
        """
        List contents of a backup without extracting.
        
        Args:
            backup_id: Backup to inspect
            
        Returns:
            Contents listing
        """
        backups = {b.id: b for b in self.backup_manager.list_backups(limit=1000)}
        if backup_id not in backups:
            return {"success": False, "error": "Backup not found"}
        
        metadata = backups[backup_id]
        backup_file = Path(metadata.backup_path)
        
        if not backup_file.exists():
            return {"success": False, "error": "Backup file missing"}
        
        files = []
        directories = set()
        total_size = 0
        
        try:
            if metadata.compression == "zip":
                with zipfile.ZipFile(backup_file, "r") as zf:
                    for info in zf.infolist():
                        if info.is_dir():
                            directories.add(info.filename)
                        else:
                            files.append({
                                "path": info.filename,
                                "size": info.file_size,
                                "compressed": info.compress_size,
                            })
                            total_size += info.file_size
            else:
                with tarfile.open(backup_file, "r:*") as tf:
                    for member in tf.getmembers():
                        if member.isdir():
                            directories.add(member.name)
                        elif member.isfile():
                            files.append({
                                "path": member.name,
                                "size": member.size,
                            })
                            total_size += member.size
            
            return {
                "success": True,
                "backup_id": backup_id,
                "file_count": len(files),
                "directory_count": len(directories),
                "total_uncompressed_size": total_size,
                "files": files[:100],  # First 100 files
                "directories": list(directories)[:50],
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compare_backups(
        self,
        backup_id_1: str,
        backup_id_2: str,
    ) -> Dict[str, Any]:
        """
        Compare two backups to see what changed.
        
        Args:
            backup_id_1: First backup (typically older)
            backup_id_2: Second backup (typically newer)
            
        Returns:
            Comparison result
        """
        contents_1 = self.list_backup_contents(backup_id_1)
        contents_2 = self.list_backup_contents(backup_id_2)
        
        if not contents_1.get("success") or not contents_2.get("success"):
            return {
                "success": False,
                "error": "Could not read one or both backups",
            }
        
        files_1 = {f["path"]: f["size"] for f in contents_1.get("files", [])}
        files_2 = {f["path"]: f["size"] for f in contents_2.get("files", [])}
        
        paths_1 = set(files_1.keys())
        paths_2 = set(files_2.keys())
        
        added = paths_2 - paths_1
        removed = paths_1 - paths_2
        common = paths_1 & paths_2
        
        modified = []
        for path in common:
            if files_1[path] != files_2[path]:
                modified.append({
                    "path": path,
                    "old_size": files_1[path],
                    "new_size": files_2[path],
                })
        
        return {
            "success": True,
            "backup_1": backup_id_1,
            "backup_2": backup_id_2,
            "added": list(added),
            "removed": list(removed),
            "modified": modified,
            "unchanged_count": len(common) - len(modified),
        }
