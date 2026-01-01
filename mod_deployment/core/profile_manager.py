#!/usr/bin/env python3
"""
Profile Manager
===============

Manages mod profiles for different server configurations.
Supports profile creation, switching, import/export.

Author: Mod Deployment Automation Pipeline
"""

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModProfile:
    """Represents a mod profile configuration."""
    name: str
    description: str
    game: str
    created_at: str
    updated_at: str
    mods: Dict[str, str]  # identifier -> version
    config_overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    is_active: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "game": self.game,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "mods": self.mods,
            "config_overrides": self.config_overrides,
            "tags": self.tags,
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModProfile":
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            game=data.get("game", "unknown"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            mods=data.get("mods", {}),
            config_overrides=data.get("config_overrides", {}),
            tags=data.get("tags", []),
            is_active=data.get("is_active", False),
        )


class ProfileManager:
    """
    Manage mod profiles for different server configurations.
    
    Features:
    - Create/delete profiles
    - Switch between profiles
    - Import/export profiles
    - Profile comparison
    """
    
    def __init__(
        self,
        profiles_dir: Path,
        game: str = "lethal-company",
    ):
        """
        Initialize the profile manager.
        
        Args:
            profiles_dir: Directory to store profiles
            game: Game identifier
        """
        self.profiles_dir = Path(profiles_dir)
        self.game = game
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        self._profiles: Dict[str, ModProfile] = {}
        self._active_profile: Optional[str] = None
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load all profiles from disk."""
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file) as f:
                    data = json.load(f)
                profile = ModProfile.from_dict(data)
                self._profiles[profile.name] = profile
                if profile.is_active:
                    self._active_profile = profile.name
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to load profile {profile_file}: {e}")
        
        logger.info(f"Loaded {len(self._profiles)} profiles")
    
    def _save_profile(self, profile: ModProfile) -> None:
        """Save a profile to disk."""
        profile_file = self.profiles_dir / f"{profile.name}.json"
        with open(profile_file, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)
    
    def create(
        self,
        name: str,
        description: str = "",
        mods: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> ModProfile:
        """
        Create a new profile.
        
        Args:
            name: Profile name (must be unique)
            description: Profile description
            mods: Initial mods configuration
            tags: Profile tags for organization
            
        Returns:
            Created ModProfile
        """
        if name in self._profiles:
            raise ValueError(f"Profile '{name}' already exists")
        
        now = datetime.now().isoformat()
        profile = ModProfile(
            name=name,
            description=description,
            game=self.game,
            created_at=now,
            updated_at=now,
            mods=mods or {},
            tags=tags or [],
        )
        
        self._profiles[name] = profile
        self._save_profile(profile)
        
        logger.info(f"Created profile: {name}")
        return profile
    
    def delete(self, name: str) -> bool:
        """Delete a profile."""
        if name not in self._profiles:
            logger.warning(f"Profile not found: {name}")
            return False
        
        # Cannot delete active profile
        if name == self._active_profile:
            logger.error(f"Cannot delete active profile: {name}")
            return False
        
        profile_file = self.profiles_dir / f"{name}.json"
        if profile_file.exists():
            profile_file.unlink()
        
        del self._profiles[name]
        logger.info(f"Deleted profile: {name}")
        return True
    
    def get(self, name: str) -> Optional[ModProfile]:
        """Get a profile by name."""
        return self._profiles.get(name)
    
    def list(self, tags: Optional[List[str]] = None) -> List[ModProfile]:
        """List all profiles, optionally filtered by tags."""
        profiles = list(self._profiles.values())
        
        if tags:
            profiles = [
                p for p in profiles
                if any(t in p.tags for t in tags)
            ]
        
        return profiles
    
    def get_active(self) -> Optional[ModProfile]:
        """Get the currently active profile."""
        if self._active_profile:
            return self._profiles.get(self._active_profile)
        return None
    
    def activate(self, name: str) -> bool:
        """
        Activate a profile.
        
        Args:
            name: Profile name to activate
            
        Returns:
            True if successful
        """
        if name not in self._profiles:
            logger.error(f"Profile not found: {name}")
            return False
        
        # Deactivate current profile
        if self._active_profile and self._active_profile in self._profiles:
            old_profile = self._profiles[self._active_profile]
            old_profile.is_active = False
            self._save_profile(old_profile)
        
        # Activate new profile
        new_profile = self._profiles[name]
        new_profile.is_active = True
        self._active_profile = name
        self._save_profile(new_profile)
        
        logger.info(f"Activated profile: {name}")
        return True
    
    def update_mods(
        self,
        name: str,
        mods: Dict[str, str],
        merge: bool = True,
    ) -> bool:
        """
        Update mods in a profile.
        
        Args:
            name: Profile name
            mods: Mods to add/update
            merge: Merge with existing (False = replace)
            
        Returns:
            True if successful
        """
        if name not in self._profiles:
            return False
        
        profile = self._profiles[name]
        
        if merge:
            profile.mods.update(mods)
        else:
            profile.mods = mods
        
        profile.updated_at = datetime.now().isoformat()
        self._save_profile(profile)
        
        return True
    
    def remove_mod(self, name: str, mod: str) -> bool:
        """Remove a mod from a profile."""
        if name not in self._profiles:
            return False
        
        profile = self._profiles[name]
        if mod in profile.mods:
            del profile.mods[mod]
            profile.updated_at = datetime.now().isoformat()
            self._save_profile(profile)
            return True
        
        return False
    
    def clone(
        self,
        source_name: str,
        new_name: str,
        description: Optional[str] = None,
    ) -> Optional[ModProfile]:
        """
        Clone a profile.
        
        Args:
            source_name: Profile to clone
            new_name: Name for new profile
            description: New description (or copy from source)
            
        Returns:
            New ModProfile or None
        """
        if source_name not in self._profiles:
            return None
        
        if new_name in self._profiles:
            raise ValueError(f"Profile '{new_name}' already exists")
        
        source = self._profiles[source_name]
        
        return self.create(
            name=new_name,
            description=description or f"Clone of {source_name}",
            mods=source.mods.copy(),
            tags=source.tags.copy(),
        )
    
    def export_profile(
        self,
        name: str,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Export a profile to a shareable file.
        
        Args:
            name: Profile name
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        if name not in self._profiles:
            raise ValueError(f"Profile not found: {name}")
        
        profile = self._profiles[name]
        output_path = output_path or Path(f"{name}_profile.json")
        
        # Include metadata for import
        export_data = {
            "format_version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "profile": profile.to_dict(),
        }
        
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported profile to {output_path}")
        return output_path
    
    def import_profile(
        self,
        import_path: Path,
        new_name: Optional[str] = None,
        overwrite: bool = False,
    ) -> ModProfile:
        """
        Import a profile from a file.
        
        Args:
            import_path: Path to profile file
            new_name: Rename profile on import
            overwrite: Overwrite if exists
            
        Returns:
            Imported ModProfile
        """
        with open(import_path) as f:
            data = json.load(f)
        
        # Handle both raw and exported formats
        if "profile" in data:
            profile_data = data["profile"]
        else:
            profile_data = data
        
        profile = ModProfile.from_dict(profile_data)
        
        if new_name:
            profile.name = new_name
        
        if profile.name in self._profiles and not overwrite:
            raise ValueError(f"Profile '{profile.name}' already exists")
        
        profile.is_active = False  # Never import as active
        self._profiles[profile.name] = profile
        self._save_profile(profile)
        
        logger.info(f"Imported profile: {profile.name}")
        return profile
    
    def compare(
        self,
        profile1_name: str,
        profile2_name: str,
    ) -> Dict[str, Any]:
        """
        Compare two profiles.
        
        Args:
            profile1_name: First profile
            profile2_name: Second profile
            
        Returns:
            Comparison result
        """
        if profile1_name not in self._profiles:
            raise ValueError(f"Profile not found: {profile1_name}")
        if profile2_name not in self._profiles:
            raise ValueError(f"Profile not found: {profile2_name}")
        
        p1 = self._profiles[profile1_name]
        p2 = self._profiles[profile2_name]
        
        mods1 = set(p1.mods.keys())
        mods2 = set(p2.mods.keys())
        
        only_in_p1 = mods1 - mods2
        only_in_p2 = mods2 - mods1
        in_both = mods1 & mods2
        
        version_diffs = {}
        for mod in in_both:
            if p1.mods[mod] != p2.mods[mod]:
                version_diffs[mod] = {
                    profile1_name: p1.mods[mod],
                    profile2_name: p2.mods[mod],
                }
        
        return {
            "profile1": profile1_name,
            "profile2": profile2_name,
            "only_in_profile1": list(only_in_p1),
            "only_in_profile2": list(only_in_p2),
            "in_both": list(in_both),
            "version_differences": version_diffs,
            "same_mods_count": len(in_both) - len(version_diffs),
        }
    
    def create_from_manifest(
        self,
        manifest_path: Path,
        name: str,
        description: str = "",
    ) -> ModProfile:
        """
        Create a profile from an existing mod_manifest.json.
        
        Args:
            manifest_path: Path to mod_manifest.json
            name: Profile name
            description: Profile description
            
        Returns:
            Created ModProfile
        """
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        mods = {}
        for mod_data in manifest.get("installed", []):
            mods[mod_data["identifier"]] = mod_data["version"]
        
        return self.create(
            name=name,
            description=description or f"Imported from {manifest_path.name}",
            mods=mods,
            tags=["imported"],
        )
