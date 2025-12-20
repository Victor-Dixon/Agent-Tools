#!/usr/bin/env python3
"""
Delete Old Dream.os Post
========================

Deletes the old unstyled Dream.os review post (ID: 43) since we have the new styled one (ID: 45).

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import sys
import json
from pathlib import Path

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


def load_blogging_config() -> dict:
    """Load blogging API configuration."""
    config_path = project_root / ".deploy_credentials" / "blogging_api.json"
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def delete_post(site_url: str, username: str, app_password: str, post_id: int) -> bool:
    """Delete a post from WordPress."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
    auth = HTTPBasicAuth(username, app_password)
    
    try:
        response = requests.delete(
            api_url,
            auth=auth,
            params={"force": True},
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
    """Delete old duplicate post."""
    print("=" * 60)
    print("DELETE OLD DREAM.OS POST")
    print("=" * 60)
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
    
    # Delete old post (ID: 43) - keep the new styled one (ID: 45)
    old_post_id = 43
    
    print(f"🗑️  Deleting old Dream.os post (ID: {old_post_id})...")
    print("   (Keeping new styled version: ID: 45)")
    print()
    
    if delete_post(site_url, username, app_password, old_post_id):
        print(f"✅ Successfully deleted post ID {old_post_id}")
        print()
        print("🎉 Cleanup complete! Only the styled version remains.")
        return 0
    else:
        print(f"❌ Failed to delete post ID {old_post_id}")
        return 1


if __name__ == "__main__":
    sys.exit(main())





