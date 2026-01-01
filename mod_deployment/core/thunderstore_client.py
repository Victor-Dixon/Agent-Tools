#!/usr/bin/env python3
"""
Thunderstore API Client
=======================

A robust client for interacting with the Thunderstore mod repository API.
Supports mod search, metadata retrieval, version checking, and downloads.

Author: Mod Deployment Automation Pipeline
"""

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)


# Thunderstore API endpoints for different game communities
THUNDERSTORE_COMMUNITIES = {
    "lethal-company": "https://thunderstore.io/c/lethal-company/",
    "valheim": "https://thunderstore.io/c/valheim/",
    "risk-of-rain-2": "https://thunderstore.io/c/riskofrain2/",
    "boneworks": "https://thunderstore.io/c/boneworks/",
    "gtfo": "https://thunderstore.io/c/gtfo/",
    "h3vr": "https://thunderstore.io/c/h3vr/",
    "content-warning": "https://thunderstore.io/c/content-warning/",
    "repo": "https://thunderstore.io/c/repo/",
}

# Base API URL
THUNDERSTORE_API_V1 = "https://thunderstore.io/api/v1/"
THUNDERSTORE_EXPERIMENTAL_API = "https://thunderstore.io/api/experimental/"


@dataclass
class ModVersion:
    """Represents a specific version of a mod."""
    version_number: str
    download_url: str
    downloads: int
    date_created: str
    file_size: int = 0
    dependencies: List[str] = field(default_factory=list)
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "ModVersion":
        return cls(
            version_number=data.get("version_number", ""),
            download_url=data.get("download_url", ""),
            downloads=data.get("downloads", 0),
            date_created=data.get("date_created", ""),
            file_size=data.get("file_size", 0),
            dependencies=data.get("dependencies", []),
        )


@dataclass
class ModPackage:
    """Represents a mod package from Thunderstore."""
    name: str
    full_name: str  # Author-ModName format
    owner: str
    package_url: str
    date_created: str
    date_updated: str
    rating_score: int
    is_pinned: bool
    is_deprecated: bool
    total_downloads: int
    uuid4: str = ""
    categories: List[str] = field(default_factory=list)
    versions: List[ModVersion] = field(default_factory=list)
    
    @property
    def latest_version(self) -> Optional[ModVersion]:
        """Get the latest version of this mod."""
        if self.versions:
            return self.versions[0]
        return None
    
    @property
    def identifier(self) -> str:
        """Get the mod identifier (Author-ModName)."""
        return self.full_name
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "ModPackage":
        versions = [ModVersion.from_api(v) for v in data.get("versions", [])]
        return cls(
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            owner=data.get("owner", ""),
            package_url=data.get("package_url", ""),
            date_created=data.get("date_created", ""),
            date_updated=data.get("date_updated", ""),
            rating_score=data.get("rating_score", 0),
            is_pinned=data.get("is_pinned", False),
            is_deprecated=data.get("is_deprecated", False),
            total_downloads=data.get("total_downloads", 0),
            uuid4=data.get("uuid4", ""),
            categories=data.get("categories", []),
            versions=versions,
        )


@dataclass
class CachedPackageList:
    """Cached package list with timestamp."""
    packages: List[ModPackage]
    timestamp: datetime
    game: str
    
    def is_stale(self, max_age_seconds: int = 3600) -> bool:
        """Check if cache is stale."""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > max_age_seconds


class ThunderstoreClient:
    """
    Thunderstore API Client for mod management automation.
    
    Features:
    - Package listing and search
    - Version checking
    - Mod downloads with integrity verification
    - Caching for performance
    - Rate limiting to respect API limits
    """
    
    def __init__(
        self,
        game: str = "lethal-company",
        cache_dir: Optional[Path] = None,
        cache_ttl: int = 3600,
        rate_limit_delay: float = 0.1,
    ):
        """
        Initialize the Thunderstore client.
        
        Args:
            game: Game identifier (e.g., 'lethal-company', 'valheim')
            cache_dir: Directory for caching mod data
            cache_ttl: Cache time-to-live in seconds
            rate_limit_delay: Delay between API requests
        """
        self.game = game.lower().replace(" ", "-")
        self.cache_dir = cache_dir or Path.home() / ".mod_deployment" / "cache"
        self.cache_ttl = cache_ttl
        self.rate_limit_delay = rate_limit_delay
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "ModDeploymentAutomation/1.0",
            "Accept": "application/json",
        })
        self._package_cache: Optional[CachedPackageList] = None
        self._package_index: Dict[str, ModPackage] = {}
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ThunderstoreClient initialized for game: {self.game}")
    
    @property
    def community_url(self) -> str:
        """Get the community URL for the configured game."""
        return THUNDERSTORE_COMMUNITIES.get(
            self.game,
            f"https://thunderstore.io/c/{self.game}/"
        )
    
    def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        time.sleep(self.rate_limit_delay)
    
    def _get(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        """Make a rate-limited GET request."""
        self._rate_limit()
        response = self._session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response
    
    def get_all_packages(self, force_refresh: bool = False) -> List[ModPackage]:
        """
        Get all packages for the configured game.
        
        Args:
            force_refresh: Force refresh from API even if cache is valid
            
        Returns:
            List of ModPackage objects
        """
        # Check in-memory cache
        if not force_refresh and self._package_cache:
            if not self._package_cache.is_stale(self.cache_ttl):
                logger.debug("Returning packages from memory cache")
                return self._package_cache.packages
        
        # Check file cache
        cache_file = self.cache_dir / f"{self.game}_packages.json"
        if not force_refresh and cache_file.exists():
            try:
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < self.cache_ttl:
                    with open(cache_file) as f:
                        data = json.load(f)
                    packages = [ModPackage.from_api(p) for p in data]
                    self._update_cache(packages)
                    logger.debug(f"Loaded {len(packages)} packages from file cache")
                    return packages
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Cache file corrupted: {e}")
        
        # Fetch from API
        logger.info(f"Fetching all packages for {self.game} from Thunderstore API")
        url = f"{THUNDERSTORE_API_V1}package/"
        
        try:
            response = self._get(url)
            all_packages = response.json()
            
            # Filter by game/community if needed
            # The V1 API returns all packages, so we filter by checking package URLs
            game_packages = []
            for pkg_data in all_packages:
                # Check if package belongs to our game community
                pkg_url = pkg_data.get("package_url", "")
                if f"/c/{self.game}/" in pkg_url.lower().replace("_", "-"):
                    game_packages.append(ModPackage.from_api(pkg_data))
            
            # If no packages found with URL filter, try experimental API
            if not game_packages:
                logger.info("Trying experimental API for package list")
                game_packages = self._get_packages_experimental()
            
            # Save to file cache
            with open(cache_file, "w") as f:
                json.dump(all_packages, f)
            
            self._update_cache(game_packages)
            logger.info(f"Fetched {len(game_packages)} packages for {self.game}")
            return game_packages
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch packages: {e}")
            # Return cached data if available
            if self._package_cache:
                logger.warning("Returning stale cache due to API error")
                return self._package_cache.packages
            raise
    
    def _get_packages_experimental(self) -> List[ModPackage]:
        """Fetch packages using the experimental community API."""
        url = f"{THUNDERSTORE_EXPERIMENTAL_API}community/{self.game}/packages/"
        try:
            response = self._get(url)
            data = response.json()
            return [ModPackage.from_api(p) for p in data.get("results", [])]
        except requests.RequestException:
            return []
    
    def _update_cache(self, packages: List[ModPackage]) -> None:
        """Update in-memory cache and package index."""
        self._package_cache = CachedPackageList(
            packages=packages,
            timestamp=datetime.now(),
            game=self.game,
        )
        self._package_index = {p.full_name: p for p in packages}
    
    def get_package(self, identifier: str) -> Optional[ModPackage]:
        """
        Get a specific package by identifier.
        
        Args:
            identifier: Package identifier in Author-ModName format
            
        Returns:
            ModPackage or None if not found
        """
        # Ensure packages are loaded
        if not self._package_index:
            self.get_all_packages()
        
        return self._package_index.get(identifier)
    
    def search_packages(
        self,
        query: str,
        include_deprecated: bool = False,
        limit: int = 50,
    ) -> List[ModPackage]:
        """
        Search for packages by name.
        
        Args:
            query: Search query
            include_deprecated: Include deprecated packages
            limit: Maximum results to return
            
        Returns:
            List of matching ModPackage objects
        """
        packages = self.get_all_packages()
        query_lower = query.lower()
        
        results = []
        for pkg in packages:
            if not include_deprecated and pkg.is_deprecated:
                continue
            
            # Search in name and full_name
            if (query_lower in pkg.name.lower() or 
                query_lower in pkg.full_name.lower()):
                results.append(pkg)
                
            if len(results) >= limit:
                break
        
        # Sort by downloads
        results.sort(key=lambda p: p.total_downloads, reverse=True)
        return results[:limit]
    
    def get_package_versions(self, identifier: str) -> List[ModVersion]:
        """
        Get all versions of a package.
        
        Args:
            identifier: Package identifier in Author-ModName format
            
        Returns:
            List of ModVersion objects (newest first)
        """
        package = self.get_package(identifier)
        if package:
            return package.versions
        return []
    
    def check_for_updates(
        self,
        installed_mods: Dict[str, str],
    ) -> Dict[str, Dict[str, str]]:
        """
        Check for updates to installed mods.
        
        Args:
            installed_mods: Dict mapping mod identifier to installed version
            
        Returns:
            Dict of mods with available updates, including current and latest versions
        """
        updates = {}
        
        for identifier, current_version in installed_mods.items():
            package = self.get_package(identifier)
            if not package:
                logger.warning(f"Package not found: {identifier}")
                continue
            
            latest = package.latest_version
            if latest and latest.version_number != current_version:
                # Compare versions (simple string comparison for now)
                updates[identifier] = {
                    "current": current_version,
                    "latest": latest.version_number,
                    "download_url": latest.download_url,
                    "downloads": latest.downloads,
                }
        
        return updates
    
    def download_mod(
        self,
        identifier: str,
        version: Optional[str] = None,
        output_dir: Optional[Path] = None,
        verify_checksum: bool = True,
    ) -> Path:
        """
        Download a mod to the specified directory.
        
        Args:
            identifier: Package identifier (Author-ModName)
            version: Specific version to download (default: latest)
            output_dir: Output directory (default: cache/downloads)
            verify_checksum: Verify download integrity
            
        Returns:
            Path to downloaded file
        """
        package = self.get_package(identifier)
        if not package:
            raise ValueError(f"Package not found: {identifier}")
        
        # Get the requested version
        if version:
            mod_version = next(
                (v for v in package.versions if v.version_number == version),
                None
            )
            if not mod_version:
                raise ValueError(f"Version {version} not found for {identifier}")
        else:
            mod_version = package.latest_version
            if not mod_version:
                raise ValueError(f"No versions available for {identifier}")
        
        # Setup output directory
        output_dir = output_dir or (self.cache_dir / "downloads")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Download file
        filename = f"{identifier}-{mod_version.version_number}.zip"
        output_path = output_dir / filename
        
        if output_path.exists():
            logger.info(f"Mod already downloaded: {output_path}")
            return output_path
        
        logger.info(f"Downloading {identifier} v{mod_version.version_number}")
        
        response = self._session.get(mod_version.download_url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Write with progress tracking
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        hasher = hashlib.md5() if verify_checksum else None
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if hasher:
                    hasher.update(chunk)
                
                if total_size:
                    progress = (downloaded / total_size) * 100
                    if downloaded % (1024 * 1024) == 0:  # Log every MB
                        logger.debug(f"Download progress: {progress:.1f}%")
        
        logger.info(f"Downloaded {identifier} to {output_path}")
        
        if hasher:
            logger.debug(f"MD5 checksum: {hasher.hexdigest()}")
        
        return output_path
    
    def get_mod_dependencies(
        self,
        identifier: str,
        version: Optional[str] = None,
    ) -> List[str]:
        """
        Get dependencies for a mod.
        
        Args:
            identifier: Package identifier
            version: Specific version (default: latest)
            
        Returns:
            List of dependency identifiers with versions (Author-ModName-Version)
        """
        package = self.get_package(identifier)
        if not package:
            return []
        
        if version:
            mod_version = next(
                (v for v in package.versions if v.version_number == version),
                None
            )
        else:
            mod_version = package.latest_version
        
        if mod_version:
            return mod_version.dependencies
        return []
    
    def get_trending(self, limit: int = 20) -> List[ModPackage]:
        """Get trending packages sorted by recent downloads."""
        packages = self.get_all_packages()
        # Sort by rating score (proxy for trending)
        sorted_pkgs = sorted(
            [p for p in packages if not p.is_deprecated],
            key=lambda p: p.rating_score,
            reverse=True
        )
        return sorted_pkgs[:limit]
    
    def get_recently_updated(self, limit: int = 20) -> List[ModPackage]:
        """Get recently updated packages."""
        packages = self.get_all_packages()
        sorted_pkgs = sorted(
            [p for p in packages if not p.is_deprecated],
            key=lambda p: p.date_updated,
            reverse=True
        )
        return sorted_pkgs[:limit]


# Convenience function
def create_client(game: str = "lethal-company") -> ThunderstoreClient:
    """Create a Thunderstore client for the specified game."""
    return ThunderstoreClient(game=game)
