#!/usr/bin/env python3
"""
Cleanup DadudeKC.com WordPress Site
====================================

Helps remove duplicate and inappropriate content from dadudekc.com.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("❌ requests library not available")
    sys.exit(1)

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30


def load_blogging_config() -> Dict[str, Any]:
    """Load blogging API configuration."""
    config_path = project_root / ".deploy_credentials" / "blogging_api.json"
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def delete_post(site_url: str, username: str, app_password: str, post_id: int, force: bool = True) -> bool:
    """Delete a post from WordPress."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
    auth = HTTPBasicAuth(username, app_password)
    
    try:
        response = requests.delete(
            api_url,
            auth=auth,
            params={"force": force},
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def delete_page(site_url: str, username: str, app_password: str, page_id: int, force: bool = True) -> bool:
    """Delete a page from WordPress."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages/{page_id}"
    auth = HTTPBasicAuth(username, app_password)
    
    try:
        response = requests.delete(
            api_url,
            auth=auth,
            params={"force": force},
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Main cleanup function."""
    print("=" * 60)
    print("DADUDEKC.COM SITE CLEANUP")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will DELETE content from your WordPress site!")
    print()
    
    # Load config
    config = load_blogging_config()
    
    if "dadudekc.com" not in config:
        print("❌ dadudekc.com not found in blogging config")
        return 1
    
    site_config = config["dadudekc.com"]
    site_url = site_config["site_url"]
    username = site_config["username"]
    app_password = site_config["app_password"]
    
    # Based on audit, these are the items to clean up:
    # Duplicate Developer Tools pages: 36, 35, 34 (keep 5)
    # Duplicate Game Showcase pages: 38, 37 (both should probably go)
    # Duplicate Dream.os posts: 44 (keep 43, or vice versa - keep the styled one)
    
    items_to_delete = {
        "pages": [
            {"id": 36, "title": "Developer Tools", "reason": "Duplicate"},
            {"id": 35, "title": "Developer Tools", "reason": "Duplicate"},
            {"id": 34, "title": "Developer Tools", "reason": "Duplicate"},
            {"id": 38, "title": "🎮 Interactive Games Showcase", "reason": "Not appropriate for code review site"},
            {"id": 37, "title": "🎮 Interactive Games Showcase", "reason": "Not appropriate for code review site"},
        ],
        "posts": [
            {"id": 44, "title": "A Professional Review of My Vibe-Coded Project: Dream.os", "reason": "Duplicate (keep 43)"},
        ]
    }
    
    print("Items to delete:")
    print()
    print("📄 PAGES:")
    for item in items_to_delete["pages"]:
        print(f"   ID {item['id']}: {item['title']} - {item['reason']}")
    print()
    print("📝 POSTS:")
    for item in items_to_delete["posts"]:
        print(f"   ID {item['id']}: {item['title']} - {item['reason']}")
    print()
    
    confirm = input("❓ Proceed with deletion? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("❌ Cancelled")
        return 0
    
    print()
    print("🗑️  Deleting items...")
    print()
    
    deleted_pages = 0
    deleted_posts = 0
    
    # Delete pages
    for item in items_to_delete["pages"]:
        print(f"Deleting page ID {item['id']}: {item['title']}...")
        if delete_page(site_url, username, app_password, item['id']):
            print(f"   ✅ Deleted")
            deleted_pages += 1
        else:
            print(f"   ❌ Failed")
    
    print()
    
    # Delete posts
    for item in items_to_delete["posts"]:
        print(f"Deleting post ID {item['id']}: {item['title']}...")
        if delete_post(site_url, username, app_password, item['id']):
            print(f"   ✅ Deleted")
            deleted_posts += 1
        else:
            print(f"   ❌ Failed")
    
    print()
    print("=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"✅ Deleted {deleted_pages} page(s)")
    print(f"✅ Deleted {deleted_posts} post(s)")
    print()
    print("🎉 Cleanup complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





