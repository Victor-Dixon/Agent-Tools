#!/usr/bin/env python3
"""
Discover SFTP Credentials for All Sites
========================================

Uses Hostinger API helper to discover SFTP credentials for all configured sites
and updates sites.json with discovered information.

Author: Agent-4 (Captain - Strategic Oversight)
V2 Compliant: <400 lines
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.hostinger_api_helper import HostingerAPIHelper
    HAS_HELPER = True
except ImportError:
    HAS_HELPER = False
    print("❌ hostinger_api_helper not available")


def load_sites_json() -> Dict:
    """Load existing sites.json."""
    sites_file = project_root / ".deploy_credentials" / "sites.json"
    if sites_file.exists():
        try:
            with open(sites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading sites.json: {e}")
            return {}
    return {}


def save_sites_json(sites: Dict):
    """Save sites.json."""
    sites_file = project_root / ".deploy_credentials" / "sites.json"
    sites_file.parent.mkdir(parents=True, exist_ok=True)

    with open(sites_file, 'w', encoding='utf-8') as f:
        json.dump(sites, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved sites.json: {sites_file}")


def get_all_sites() -> list:
    """Get list of all sites from sites_registry.json."""
    registry_file = project_root / "sites_registry.json"
    if registry_file.exists():
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                return list(registry.keys())
        except Exception:
            pass

    # Fallback: use WordPressManager site configs
    try:
        from tools.wordpress_manager import WordPressManager
        return list(WordPressManager.SITE_CONFIGS.keys())
    except:
        return []


def discover_credentials_for_site(helper: HostingerAPIHelper, domain: str) -> Optional[Dict]:
    """Discover credentials for a single site."""
    print(f"\n🔍 Discovering credentials for {domain}...")

    try:
        credentials = helper.discover_sftp_credentials(domain)
        if credentials:
            print(
                f"✅ Found: host={credentials.get('host')}, port={credentials.get('port')}")
            return credentials
        else:
            print(f"⚠️  Could not discover credentials for {domain}")
            return None
    except Exception as e:
        print(f"❌ Error discovering {domain}: {e}")
        return None


def update_sites_json_with_credentials():
    """Discover credentials for all sites and update sites.json."""
    if not HAS_HELPER:
        print("❌ Hostinger API helper not available")
        return

    try:
        helper = HostingerAPIHelper()
    except ValueError as e:
        print(f"❌ {e}")
        print("💡 Set HOSTINGER_API_KEY in .env file")
        return

    # Load existing sites.json
    sites = load_sites_json()

    # Get all sites
    all_sites = get_all_sites()

    print(f"\n📋 Discovering credentials for {len(all_sites)} sites...")
    print("=" * 70)

    updated_count = 0
    needs_manual = []

    for site in all_sites:
        # Skip if already has complete credentials
        if site in sites:
            existing = sites[site]
            if existing.get("host") and existing.get("username") and existing.get("password"):
                print(f"⏭️  {site}: Already has complete credentials")
                continue

        # Discover credentials
        credentials = discover_credentials_for_site(helper, site)

        if credentials:
            # Initialize site entry if doesn't exist
            if site not in sites:
                sites[site] = {}

            # Update with discovered values (don't overwrite existing username/password)
            if credentials.get("host"):
                sites[site]["host"] = credentials["host"]
            if credentials.get("port"):
                sites[site]["port"] = credentials["port"]

            # Only update username/password if they were discovered (usually won't be)
            if credentials.get("username") and not sites[site].get("username"):
                sites[site]["username"] = credentials["username"]
            if credentials.get("password") and not sites[site].get("password"):
                sites[site]["password"] = credentials["password"]

            # Check if still needs manual credentials
            if not sites[site].get("username") or not sites[site].get("password"):
                needs_manual.append(site)

            updated_count += 1

    # Save updated sites.json
    if updated_count > 0:
        save_sites_json(sites)
        print(f"\n✅ Updated {updated_count} sites in sites.json")
    else:
        print("\nℹ️  No updates needed")

    # Report sites needing manual credentials
    if needs_manual:
        print(f"\n⚠️  {len(needs_manual)} sites need manual username/password:")
        print("   Run: python tools/discover_ftp_credentials.py --guide")
        print("\n   Sites needing credentials:")
        for site in needs_manual:
            print(f"     • {site}")
            if site in sites:
                print(f"       Host: {sites[site].get('host', 'N/A')}")
                print(f"       Port: {sites[site].get('port', 'N/A')}")

    print("\n" + "=" * 70)
    print("✅ Credential discovery complete!")
    print("\n💡 Next steps:")
    print("   1. Check sites.json for discovered credentials")
    print("   2. Add username/password manually from Hostinger control panel")
    print("   3. Test connection: python tools/wordpress_manager.py --site yoursite.com")


def main():
    """Main CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Discover SFTP credentials for all sites via Hostinger API"
    )
    parser.add_argument(
        "--site",
        help="Discover credentials for a specific site only"
    )

    args = parser.parse_args()

    if args.site:
        # Single site mode
        if not HAS_HELPER:
            print("❌ Hostinger API helper not available")
            return

        try:
            helper = HostingerAPIHelper()
            credentials = discover_credentials_for_site(helper, args.site)

            if credentials:
                print("\n✅ Discovered credentials:")
                print(f"   Host: {credentials.get('host', 'N/A')}")
                print(f"   Port: {credentials.get('port', 'N/A')}")
                print(
                    f"   Username: {credentials.get('username', 'N/A (needs manual)')}")
                print(
                    f"   Password: {'***' if credentials.get('password') else 'N/A (needs manual)'}")
        except ValueError as e:
            print(f"❌ {e}")
    else:
        # All sites mode
        update_sites_json_with_credentials()


if __name__ == "__main__":
    main()
