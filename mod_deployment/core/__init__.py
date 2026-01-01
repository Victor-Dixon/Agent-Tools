"""
Thunderstore Mod Deployment Core
================================

A comprehensive automation library for Thunderstore mod management.
Supports multiple games including Lethal Company, Valheim, Risk of Rain 2, etc.

Features:
- Thunderstore API integration
- Dependency resolution
- Mod installation/updates
- Profile management
- Health checks and rollback
"""

from .thunderstore_client import ThunderstoreClient
from .mod_manager import ModManager
from .dependency_resolver import DependencyResolver
from .profile_manager import ProfileManager
from .health_checker import HealthChecker

__all__ = [
    "ThunderstoreClient",
    "ModManager", 
    "DependencyResolver",
    "ProfileManager",
    "HealthChecker",
]

__version__ = "1.0.0"
