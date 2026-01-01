#!/usr/bin/env python3
"""
Cloud Sync
==========

Synchronizes backups to cloud storage providers.
Supports S3-compatible storage (AWS, MinIO, B2, etc.).
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import subprocess

logger = logging.getLogger(__name__)


@dataclass
class CloudConfig:
    """Configuration for cloud storage."""
    provider: str  # s3, b2, gcs, azure
    bucket: str
    prefix: str = "game-backups"
    region: str = ""
    endpoint_url: str = ""  # For S3-compatible services
    access_key: str = ""
    secret_key: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "bucket": self.bucket,
            "prefix": self.prefix,
            "region": self.region,
            "endpoint_url": self.endpoint_url,
            # Don't include credentials
        }


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    files_uploaded: int
    files_skipped: int
    bytes_transferred: int
    duration_seconds: float
    errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "files_uploaded": self.files_uploaded,
            "files_skipped": self.files_skipped,
            "bytes_transferred": self.bytes_transferred,
            "duration_seconds": self.duration_seconds,
            "errors": self.errors,
        }


class CloudSync:
    """
    Synchronizes backups to cloud storage.
    
    Features:
    - Upload backups to S3-compatible storage
    - Incremental sync (only upload new/changed files)
    - Download backups from cloud
    - List remote backups
    - Cleanup old remote backups
    """
    
    def __init__(
        self,
        backup_path: Path,
        config: CloudConfig,
    ):
        self.backup_path = Path(backup_path)
        self.config = config
        
        # Track synced files
        self.sync_manifest_path = self.backup_path / ".cloud_sync_manifest.json"
        self._synced_files: Dict[str, str] = {}  # filename -> checksum
        self._load_manifest()
    
    def _load_manifest(self) -> None:
        """Load sync manifest."""
        if self.sync_manifest_path.exists():
            try:
                with open(self.sync_manifest_path) as f:
                    data = json.load(f)
                self._synced_files = data.get("synced_files", {})
            except Exception:
                pass
    
    def _save_manifest(self) -> None:
        """Save sync manifest."""
        data = {
            "provider": self.config.provider,
            "bucket": self.config.bucket,
            "last_sync": datetime.now().isoformat(),
            "synced_files": self._synced_files,
        }
        with open(self.sync_manifest_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def _get_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum for sync comparison."""
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()
    
    def _needs_upload(self, file_path: Path) -> bool:
        """Check if a file needs to be uploaded."""
        filename = file_path.name
        
        if filename not in self._synced_files:
            return True
        
        current_checksum = self._get_file_checksum(file_path)
        return current_checksum != self._synced_files[filename]
    
    def sync_to_cloud(self, force: bool = False) -> SyncResult:
        """
        Sync all backups to cloud storage.
        
        Args:
            force: Upload all files even if already synced
            
        Returns:
            SyncResult with details
        """
        start_time = datetime.now()
        uploaded = 0
        skipped = 0
        bytes_transferred = 0
        errors = []
        
        # Find backup files
        backup_files = list(self.backup_path.glob("*.tar.gz")) + \
                       list(self.backup_path.glob("*.zip")) + \
                       list(self.backup_path.glob("*.tar"))
        
        for file_path in backup_files:
            try:
                if force or self._needs_upload(file_path):
                    success = self._upload_file(file_path)
                    if success:
                        uploaded += 1
                        bytes_transferred += file_path.stat().st_size
                        self._synced_files[file_path.name] = self._get_file_checksum(file_path)
                    else:
                        errors.append(f"Failed to upload: {file_path.name}")
                else:
                    skipped += 1
            except Exception as e:
                errors.append(f"Error processing {file_path.name}: {e}")
        
        # Also upload manifest
        manifest_path = self.backup_path / "backup_manifest.json"
        if manifest_path.exists():
            self._upload_file(manifest_path)
        
        self._save_manifest()
        
        return SyncResult(
            success=len(errors) == 0,
            files_uploaded=uploaded,
            files_skipped=skipped,
            bytes_transferred=bytes_transferred,
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            errors=errors,
        )
    
    def _upload_file(self, file_path: Path) -> bool:
        """Upload a file to cloud storage."""
        remote_path = f"{self.config.prefix}/{file_path.name}"
        
        if self.config.provider == "s3":
            return self._upload_s3(file_path, remote_path)
        elif self.config.provider == "b2":
            return self._upload_b2(file_path, remote_path)
        elif self.config.provider == "local":
            return self._upload_local(file_path, remote_path)
        else:
            logger.warning(f"Unsupported provider: {self.config.provider}")
            return False
    
    def _upload_s3(self, file_path: Path, remote_path: str) -> bool:
        """Upload to S3 or S3-compatible storage."""
        try:
            import boto3
            
            session_kwargs = {}
            if self.config.access_key and self.config.secret_key:
                session_kwargs = {
                    "aws_access_key_id": self.config.access_key,
                    "aws_secret_access_key": self.config.secret_key,
                }
            
            client_kwargs = {}
            if self.config.endpoint_url:
                client_kwargs["endpoint_url"] = self.config.endpoint_url
            if self.config.region:
                client_kwargs["region_name"] = self.config.region
            
            s3 = boto3.client("s3", **session_kwargs, **client_kwargs)
            
            s3.upload_file(
                str(file_path),
                self.config.bucket,
                remote_path,
            )
            
            logger.info(f"Uploaded to S3: {remote_path}")
            return True
            
        except ImportError:
            # Fallback to AWS CLI
            return self._upload_s3_cli(file_path, remote_path)
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return False
    
    def _upload_s3_cli(self, file_path: Path, remote_path: str) -> bool:
        """Upload to S3 using AWS CLI."""
        try:
            s3_uri = f"s3://{self.config.bucket}/{remote_path}"
            
            cmd = ["aws", "s3", "cp", str(file_path), s3_uri]
            
            if self.config.endpoint_url:
                cmd.extend(["--endpoint-url", self.config.endpoint_url])
            
            result = subprocess.run(cmd, capture_output=True, timeout=3600)
            
            if result.returncode == 0:
                logger.info(f"Uploaded to S3 (CLI): {remote_path}")
                return True
            else:
                logger.error(f"AWS CLI error: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"AWS CLI upload failed: {e}")
            return False
    
    def _upload_b2(self, file_path: Path, remote_path: str) -> bool:
        """Upload to Backblaze B2."""
        try:
            cmd = [
                "b2", "upload-file",
                self.config.bucket,
                str(file_path),
                remote_path,
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=3600)
            
            if result.returncode == 0:
                logger.info(f"Uploaded to B2: {remote_path}")
                return True
            else:
                logger.error(f"B2 error: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"B2 upload failed: {e}")
            return False
    
    def _upload_local(self, file_path: Path, remote_path: str) -> bool:
        """Copy to a local 'cloud' directory (for testing)."""
        try:
            target_dir = Path(self.config.bucket) / self.config.prefix
            target_dir.mkdir(parents=True, exist_ok=True)
            
            import shutil
            shutil.copy2(file_path, target_dir / file_path.name)
            
            logger.info(f"Copied to local: {target_dir / file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Local copy failed: {e}")
            return False
    
    def list_remote_backups(self) -> List[Dict[str, Any]]:
        """List backups in cloud storage."""
        if self.config.provider == "s3":
            return self._list_s3()
        elif self.config.provider == "local":
            return self._list_local()
        return []
    
    def _list_s3(self) -> List[Dict[str, Any]]:
        """List files in S3 bucket."""
        try:
            import boto3
            
            session_kwargs = {}
            if self.config.access_key and self.config.secret_key:
                session_kwargs = {
                    "aws_access_key_id": self.config.access_key,
                    "aws_secret_access_key": self.config.secret_key,
                }
            
            client_kwargs = {}
            if self.config.endpoint_url:
                client_kwargs["endpoint_url"] = self.config.endpoint_url
            if self.config.region:
                client_kwargs["region_name"] = self.config.region
            
            s3 = boto3.client("s3", **session_kwargs, **client_kwargs)
            
            response = s3.list_objects_v2(
                Bucket=self.config.bucket,
                Prefix=self.config.prefix,
            )
            
            files = []
            for obj in response.get("Contents", []):
                files.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list S3: {e}")
            return []
    
    def _list_local(self) -> List[Dict[str, Any]]:
        """List files in local 'cloud' directory."""
        target_dir = Path(self.config.bucket) / self.config.prefix
        if not target_dir.exists():
            return []
        
        files = []
        for file_path in target_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "key": str(file_path),
                    "size": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
        
        return files
    
    def download_backup(self, remote_key: str, local_path: Path) -> bool:
        """
        Download a backup from cloud storage.
        
        Args:
            remote_key: Key/path of file in cloud
            local_path: Where to save locally
            
        Returns:
            True if successful
        """
        if self.config.provider == "s3":
            try:
                import boto3
                
                s3 = boto3.client("s3")
                s3.download_file(self.config.bucket, remote_key, str(local_path))
                return True
            except Exception as e:
                logger.error(f"Download failed: {e}")
                return False
        
        return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        local_files = set()
        for ext in ["*.tar.gz", "*.zip", "*.tar"]:
            local_files.update(f.name for f in self.backup_path.glob(ext))
        
        synced_files = set(self._synced_files.keys())
        
        return {
            "provider": self.config.provider,
            "bucket": self.config.bucket,
            "local_backup_count": len(local_files),
            "synced_count": len(synced_files & local_files),
            "pending_upload": len(local_files - synced_files),
            "orphaned_remote": len(synced_files - local_files),
        }
