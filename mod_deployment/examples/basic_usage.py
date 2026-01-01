#!/usr/bin/env python3
"""
Basic Usage Examples
====================

Demonstrates the core functionality of the mod deployment automation system.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.thunderstore_client import ThunderstoreClient
from core.dependency_resolver import DependencyResolver
from core.profile_manager import ProfileManager


def example_search_mods():
    """Search for mods on Thunderstore."""
    print("\n=== Searching Thunderstore ===")
    
    client = ThunderstoreClient(game="lethal-company")
    
    # Search for specific mods
    results = client.search_packages("BiggerLobby", limit=5)
    print(f"\nFound {len(results)} results for 'BiggerLobby':")
    for pkg in results:
        print(f"  - {pkg.full_name}")
        print(f"    Downloads: {pkg.total_downloads:,}")
        if pkg.latest_version:
            print(f"    Latest: v{pkg.latest_version.version_number}")


def example_get_trending():
    """Get trending mods."""
    print("\n=== Trending Mods ===")
    
    client = ThunderstoreClient(game="lethal-company")
    trending = client.get_trending(limit=10)
    
    print(f"\nTop 10 trending mods:")
    for i, pkg in enumerate(trending, 1):
        print(f"  {i}. {pkg.full_name} ({pkg.total_downloads:,} downloads)")


def example_resolve_dependencies():
    """Resolve mod dependencies."""
    print("\n=== Dependency Resolution ===")
    
    client = ThunderstoreClient(game="lethal-company")
    resolver = DependencyResolver(client)
    
    # Resolve dependencies for a set of mods
    mods_to_install = ["bizzlemip-BiggerLobby-2.6.0"]
    
    print(f"\nResolving dependencies for: {mods_to_install}")
    result = resolver.resolve(mods=mods_to_install)
    
    if result.success:
        print(f"\nResolved {len(result.resolved)} mods:")
        for mod_id in result.install_order:
            version = result.resolved.get(mod_id, "unknown")
            print(f"  - {mod_id}: {version}")
    else:
        print(f"\nResolution failed!")
        if result.conflicts:
            print(f"Conflicts: {result.conflicts}")
        if result.missing:
            print(f"Missing: {result.missing}")


def example_profile_management():
    """Create and manage mod profiles."""
    print("\n=== Profile Management ===")
    
    profiles_dir = Path("/tmp/mod_profiles")
    profiles_dir.mkdir(exist_ok=True)
    
    manager = ProfileManager(profiles_dir=profiles_dir, game="lethal-company")
    
    # Create a profile
    profile = manager.create(
        name="test-profile",
        description="Example test profile",
        mods={
            "BiggerLobby": "2.6.0",
            "MoreCompany": "1.7.2",
        },
        tags=["example", "qol"],
    )
    
    print(f"\nCreated profile: {profile.name}")
    print(f"  Description: {profile.description}")
    print(f"  Mods: {profile.mods}")
    
    # List profiles
    print(f"\nAll profiles:")
    for p in manager.list():
        status = "ACTIVE" if p.is_active else ""
        print(f"  - {p.name} ({len(p.mods)} mods) {status}")
    
    # Activate
    manager.activate("test-profile")
    print(f"\nActivated: test-profile")
    
    # Clean up
    manager.delete("test-profile")
    print(f"Deleted: test-profile")


def example_check_updates():
    """Check for mod updates."""
    print("\n=== Check for Updates ===")
    
    client = ThunderstoreClient(game="lethal-company")
    
    # Simulate installed mods (use older versions)
    installed_mods = {
        "bizzlemip-BiggerLobby": "2.5.0",
        "notnotnotswipez-MoreCompany": "1.7.0",
    }
    
    print(f"\nChecking updates for {len(installed_mods)} mods...")
    updates = client.check_for_updates(installed_mods)
    
    if updates:
        print(f"\nUpdates available:")
        for mod, info in updates.items():
            print(f"  - {mod}")
            print(f"    Current: {info['current']} -> Latest: {info['latest']}")
    else:
        print("\nAll mods are up to date!")


def main():
    """Run all examples."""
    print("=" * 60)
    print("MOD DEPLOYMENT AUTOMATION - USAGE EXAMPLES")
    print("=" * 60)
    
    try:
        example_search_mods()
        example_get_trending()
        example_resolve_dependencies()
        example_profile_management()
        example_check_updates()
        
    except Exception as e:
        print(f"\nNote: Some examples require network access to Thunderstore API")
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
