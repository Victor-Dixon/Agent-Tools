#!/usr/bin/env python3
"""
Fix FreeRideInvestor.com Blog Page 404
========================================

Creates the missing Blog page for freerideinvestor.com to fix the 404 footer link.

Task: [SITE_AUDIT][HIGH][SA-FREERIDEINVESTOR-LINK-F4ECC78E]
Issue: freerideinvestor: footer link 'Blog' -> 404 (https://freerideinvestor.com/blog)

Author: Agent-8 (SSOT & System Integration Specialist)
V2 Compliant: <300 lines
"""

import json
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
    """Get WordPress credentials from config file."""
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
                    site_config = config.get("freerideinvestor")
                    if site_config:
                        return {
                            "username": site_config.get("username"),
                            "app_password": site_config.get("app_password"),
                            "site_url": site_config.get("site_url", "https://freerideinvestor.com")
                        }
            except Exception as e:
                print(f"⚠️  Could not read config from {config_path}: {e}")
                continue
    
    return None


def check_page_exists(site_url: str, slug: str, auth: HTTPBasicAuth) -> Optional[Dict[str, Any]]:
    """Check if a WordPress page with the given slug exists."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    try:
        response = requests.get(
            api_url,
            params={"slug": slug},
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            pages = response.json()
            if pages:
                return {
                    "exists": True,
                    "page_id": pages[0]["id"],
                    "link": pages[0]["link"],
                    "status": pages[0].get("status", "unknown")
                }
        return {"exists": False}
    except Exception as e:
        print(f"⚠️  Error checking page existence: {e}")
        return None


def create_blog_page(site_url: str, username: str, app_password: str) -> Dict[str, Any]:
    """Create the Blog page for freerideinvestor.com."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    auth = HTTPBasicAuth(username, app_password.replace(" ", ""))
    
    # Check if page already exists
    existing = check_page_exists(site_url, "blog", auth)
    if existing and existing.get("exists"):
        page_id = existing.get("page_id")
        status = existing.get("status")
        
        if status == "publish":
            return {
                "success": True,
                "page_id": page_id,
                "link": existing.get("link"),
                "message": "Page already exists and is published",
                "action": "skipped"
            }
        else:
            # Page exists but not published - update it
            update_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages/{page_id}"
            update_response = requests.post(
                update_url,
                json={"status": "publish"},
                auth=auth,
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            if update_response.status_code in (200, 201):
                page = update_response.json()
                return {
                    "success": True,
                    "page_id": page_id,
                    "link": page.get("link"),
                    "message": "Page existed but was unpublished - now published",
                    "action": "updated"
                }
    
    # Create new page
    page_content = """<!-- wp:heading -->
<h1>Blog</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Welcome to the FreeRide Investor blog. Stay updated with the latest trading insights, strategy analysis, and market commentary.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Check back soon for new articles and updates!</p>
<!-- /wp:paragraph -->"""
    
    page_data = {
        "title": "Blog",
        "slug": "blog",
        "status": "publish",
        "content": page_content
    }
    
    try:
        response = requests.post(
            api_url,
            json=page_data,
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code in (200, 201):
            page = response.json()
            return {
                "success": True,
                "page_id": page.get("id"),
                "link": page.get("link"),
                "message": "Page created successfully",
                "action": "created"
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
    print("🔧 Fixing FreeRideInvestor.com Blog Page 404")
    print("   Site: https://freerideinvestor.com")
    print(f"   Target: /blog")
    print()
    
    # Get credentials
    credentials = get_credentials()
    if not credentials:
        print("❌ WordPress credentials not found!")
        print()
        print("Please create .deploy_credentials/blogging_api.json with:")
        print(json.dumps({
            "freerideinvestor": {
                "username": "your_username",
                "app_password": "your_app_password",
                "site_url": "https://freerideinvestor.com"
            }
        }, indent=2))
        return 1
    
    # Create page
    result = create_blog_page(
        site_url=credentials["site_url"],
        username=credentials["username"],
        app_password=credentials["app_password"]
    )
    
    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"   {result.get('message')}")
        print(f"   Action: {result.get('action', 'unknown')}")
        print(f"   Page ID: {result.get('page_id')}")
        print(f"   Link: {result.get('link')}")
        print()
        print("🎯 Task complete: Blog page created/fixed")
        return 0
    else:
        print("❌ FAILED!")
        print(f"   Error: {result.get('error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
