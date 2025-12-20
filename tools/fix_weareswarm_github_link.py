#!/usr/bin/env python3
"""
Fix weareswarm.online Footer GitHub Link
==========================================

Fixes broken GitHub link in footer of weareswarm.online.
Task: [SITE_AUDIT][MEDIUM][SA-WEARESWARMON-FOOTER-8B862C52]
Author: Agent-8 (SSOT & System Integration Specialist)
V2 Compliant: <300 lines
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("❌ requests library required. Install with: pip install requests")
    sys.exit(1)

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_QUICK = 5
        HTTP_DEFAULT = 30


def get_credentials() -> Optional[Dict[str, str]]:
    """Get WordPress credentials from environment or config file."""
    username = os.environ.get("WEARESWARMON_WP_USER")
    app_password = os.environ.get("WEARESWARMON_WP_PASSWORD")

    if username and app_password:
        return {
            "username": username,
            "app_password": app_password
        }

    config_paths = [
        Path(".deploy_credentials/blogging_api.json"),
        Path("config/blogging_api.json"),
        Path(project_root / ".deploy_credentials/blogging_api.json"),
        Path(project_root / "config/blogging_api.json"),
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    site_config = config.get("weareswarm.online") or config.get("weareswarmonline")
                    if site_config:
                        return {
                            "username": site_config.get("username"),
                            "app_password": site_config.get("app_password")
                        }
            except Exception as e:
                print(f"⚠️  Could not read config from {config_path}: {e}")
                continue

    return None


def get_footer_menu_id(site_url: str, auth: HTTPBasicAuth) -> Optional[int]:
    """Get footer menu ID from WordPress."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/menus"
    try:
        response = requests.get(
            api_url,
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        if response.status_code == 200:
            menus = response.json()
            for menu in menus:
                if 'footer' in menu.get('name', '').lower() or menu.get('slug', '') == 'footer':
                    return menu.get('id')
    except Exception as e:
        print(f"⚠️  Error fetching menus: {e}")
    
    return None


def get_menu_items(site_url: str, menu_id: int, auth: HTTPBasicAuth) -> list:
    """Get menu items for a menu."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/menu-items"
    try:
        response = requests.get(
            api_url,
            params={"menus": menu_id},
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"⚠️  Error fetching menu items: {e}")
    
    return []


def update_github_link(site_url: str, username: str, app_password: str, correct_url: str = None) -> Dict[str, Any]:
    """Update GitHub link in footer menu."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/menu-items"
    auth = HTTPBasicAuth(username, app_password.replace(" ", ""))

    # Try to find footer menu
    menu_id = get_footer_menu_id(site_url, auth)
    if not menu_id:
        return {
            "success": False,
            "error": "Footer menu not found. May need to update via WordPress admin or theme customizer."
        }

    # Get menu items
    menu_items = get_menu_items(site_url, menu_id, auth)
    
    # Find GitHub link
    github_item = None
    for item in menu_items:
        if 'github' in item.get('title', {}).get('rendered', '').lower() or \
           'github.com' in item.get('url', '').lower():
            github_item = item
            break

    if not github_item:
        return {
            "success": False,
            "error": "GitHub menu item not found in footer menu"
        }

    # Determine correct URL
    if not correct_url:
        # Default: remove link or set to placeholder
        # Since we don't have public repo URL, we'll set to a placeholder
        correct_url = "#"  # Or could be removed entirely

    # Update menu item
    item_id = github_item.get('id')
    update_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/menu-items/{item_id}"
    
    update_data = {
        "url": correct_url
    }

    try:
        response = requests.post(
            update_url,
            json=update_data,
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )

        if response.status_code in (200, 201):
            return {
                "success": True,
                "message": f"GitHub link updated to: {correct_url}",
                "item_id": item_id
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main execution."""
    site_url = "https://weareswarm.online"
    broken_url = "https://github.com/Agent_Cellphone_V2_Repository"

    print("🔧 Fixing weareswarm.online Footer GitHub Link")
    print(f"   Site: {site_url}")
    print(f"   Broken URL: {broken_url}")
    print()

    credentials = get_credentials()
    if not credentials:
        print("❌ WordPress credentials not found!")
        print("Please set environment variables or create .deploy_credentials/blogging_api.json")
        print()
        print("📋 RECOMMENDATION:")
        print("   Since the repository may not have a public GitHub URL, options are:")
        print("   1. Remove the GitHub link from footer")
        print("   2. Update to correct repository URL (if public)")
        print("   3. Set link to '#' (placeholder)")
        print()
        print("   This can be done via WordPress admin:")
        print("   - Appearance > Menus > Footer Menu > Edit GitHub link")
        return 1

    # For now, we'll set to placeholder since we don't have confirmed public repo URL
    # User can update this later with correct URL
    result = update_github_link(
        site_url=site_url,
        username=credentials["username"],
        app_password=credentials["app_password"],
        correct_url="#"  # Placeholder - should be updated with actual repo URL
    )

    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"   {result.get('message')}")
        print()
        print("⚠️  NOTE: Link set to '#' placeholder")
        print("   Update with correct GitHub repository URL if available")
        print("   Or remove link entirely via WordPress admin")
        return 0
    else:
        print("❌ FAILED!")
        print(f"   Error: {result.get('error')}")
        print()
        print("📋 MANUAL FIX REQUIRED:")
        print("   1. Log into WordPress admin")
        print("   2. Go to Appearance > Menus")
        print("   3. Find Footer menu")
        print("   4. Edit or remove GitHub link")
        print("   5. Save menu")
        return 1


if __name__ == "__main__":
    sys.exit(main())





