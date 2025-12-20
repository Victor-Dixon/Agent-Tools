#!/usr/bin/env python3
"""
Pin Houston Sip Queen Announcement Post
========================================

Pins the announcement post (ID: 6) to the top of the blog.

Task: Houston Sip Queen pin post task - HIGH priority
Post ID: 6
Post Title: "Houston Sip Queen is Live — Luxury Mobile Bartending for Your Event"

Author: Agent-7 (Web Development Specialist)
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
    # Try environment variables first
    username = os.environ.get("HOUSTONSIPQUEEN_WP_USER")
    app_password = os.environ.get("HOUSTONSIPQUEEN_WP_PASSWORD")
    
    if username and app_password:
        return {
            "username": username,
            "app_password": app_password,
            "site_url": "https://houstonsipqueen.com"
        }
    
    # Try config file
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
                    # Try different possible keys
                    site_config = (
                        config.get("houstonsipqueen.com") or
                        config.get("houstonsipqueen") or
                        config.get("houstonsipqueen")
                    )
                    if site_config:
                        return {
                            "username": site_config.get("username"),
                            "app_password": site_config.get("app_password"),
                            "site_url": site_config.get("site_url", "https://houstonsipqueen.com")
                        }
            except Exception as e:
                print(f"⚠️  Could not read config from {config_path}: {e}")
                continue
    
    return None


def pin_post(site_url: str, username: str, app_password: str, post_id: int) -> Dict[str, Any]:
    """Pin a WordPress post to the top of the blog."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
    auth = HTTPBasicAuth(username, app_password.replace(" ", ""))
    
    # First, get current post to verify it exists
    try:
        response = requests.get(
            api_url,
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Post not found or inaccessible: HTTP {response.status_code}"
            }
        
        post = response.json()
        post_title = post.get("title", {}).get("rendered", "Unknown")
        
        # Pin the post by setting sticky status
        # WordPress REST API uses the 'sticky' parameter
        update_data = {
            "sticky": True
        }
        
        update_response = requests.post(
            api_url,
            json=update_data,
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if update_response.status_code in (200, 201):
            updated_post = update_response.json()
            return {
                "success": True,
                "post_id": post_id,
                "post_title": post_title,
                "link": updated_post.get("link"),
                "sticky": updated_post.get("sticky", False),
                "message": "Post pinned successfully"
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {update_response.status_code}: {update_response.text[:200]}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main execution."""
    site_url = "https://houstonsipqueen.com"
    post_id = 6  # From tasks_backlog.md
    
    print("📌 Pinning Houston Sip Queen Announcement Post")
    print(f"   Site: {site_url}")
    print(f"   Post ID: {post_id}")
    print()
    
    # Get credentials
    credentials = get_credentials()
    if not credentials:
        print("❌ WordPress credentials not found!")
        print()
        print("Please set environment variables:")
        print("  export HOUSTONSIPQUEEN_WP_USER='your_username'")
        print("  export HOUSTONSIPQUEEN_WP_PASSWORD='your_app_password'")
        print()
        print("Or create .deploy_credentials/blogging_api.json with:")
        print(json.dumps({
            "houstonsipqueen.com": {
                "username": "your_username",
                "app_password": "your_app_password",
                "site_url": "https://houstonsipqueen.com"
            }
        }, indent=2))
        return 1
    
    # Pin post
    result = pin_post(
        site_url=credentials["site_url"],
        username=credentials["username"],
        app_password=credentials["app_password"],
        post_id=post_id
    )
    
    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"   {result.get('message')}")
        print(f"   Post: {result.get('post_title')}")
        print(f"   Post ID: {result.get('post_id')}")
        print(f"   Link: {result.get('link')}")
        print(f"   Sticky: {result.get('sticky')}")
        print()
        print("🎯 Task complete: Post pinned to top of blog")
        return 0
    else:
        print("❌ FAILED!")
        print(f"   Error: {result.get('error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

