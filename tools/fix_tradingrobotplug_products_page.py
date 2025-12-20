#!/usr/bin/env python3
"""
Fix TradingRobotPlug.com Products Page 404
===========================================

Creates the missing Products page for tradingrobotplug.com to fix the 404 navigation link.

Task: [SITE_AUDIT][HIGH][SA-TRADINGROBOTPLUGCOM-LINK-2FE3C97E]
Issue: tradingrobotplug.com: nav link 'Products' -> 404 (https://tradingrobotplug.com/products)

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
    username = os.environ.get("TRADINGROBOTPLUG_WP_USER")
    app_password = os.environ.get("TRADINGROBOTPLUG_WP_PASSWORD")
    
    if username and app_password:
        return {
            "username": username,
            "app_password": app_password
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
                    site_config = config.get("tradingrobotplug.com")
                    if site_config:
                        return {
                            "username": site_config.get("username"),
                            "app_password": site_config.get("app_password")
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


def create_products_page(site_url: str, username: str, app_password: str) -> Dict[str, Any]:
    """Create the Products page for tradingrobotplug.com."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    auth = HTTPBasicAuth(username, app_password.replace(" ", ""))
    
    # Check if page already exists
    existing = check_page_exists(site_url, "products", auth)
    if existing and existing.get("exists"):
        status = existing.get("status")
        if status == "publish":
            return {
                "success": True,
                "page_id": existing.get("page_id"),
                "link": existing.get("link"),
                "message": "Page already exists and is published"
            }
        else:
            # Page exists but not published - update it
            page_id = existing.get("page_id")
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
                    "message": "Page existed but was unpublished - now published"
                }
    
    # Create new page
    page_content = """<!-- wp:paragraph -->
<p>Welcome to TradingRobotPlug Products. Our automation tools and plugins help traders streamline their workflow and maximize efficiency.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Our Products</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Explore our range of trading automation solutions designed to save you time and improve your trading performance.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3>Coming Soon</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>We're constantly developing new tools and plugins. Check back soon for updates!</p>
<!-- /wp:paragraph -->"""
    
    page_data = {
        "title": "Products",
        "slug": "products",
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
                "message": "Page created successfully"
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
    site_url = "https://tradingrobotplug.com"
    
    print("🔧 Fixing TradingRobotPlug.com Products Page 404")
    print(f"   Site: {site_url}")
    print(f"   Target: /products")
    print()
    
    # Get credentials
    credentials = get_credentials()
    if not credentials:
        print("❌ WordPress credentials not found!")
        print()
        print("Please set environment variables:")
        print("  export TRADINGROBOTPLUG_WP_USER='your_username'")
        print("  export TRADINGROBOTPLUG_WP_PASSWORD='your_app_password'")
        print()
        print("Or create .deploy_credentials/blogging_api.json with:")
        print(json.dumps({
            "tradingrobotplug.com": {
                "username": "your_username",
                "app_password": "your_app_password"
            }
        }, indent=2))
        return 1
    
    # Create page
    result = create_products_page(
        site_url=site_url,
        username=credentials["username"],
        app_password=credentials["app_password"]
    )
    
    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"   {result.get('message')}")
        print(f"   Page ID: {result.get('page_id')}")
        print(f"   Link: {result.get('link')}")
        print()
        print("🎯 Task complete: Products page created/fixed")
        return 0
    else:
        print("❌ FAILED!")
        print(f"   Error: {result.get('error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

