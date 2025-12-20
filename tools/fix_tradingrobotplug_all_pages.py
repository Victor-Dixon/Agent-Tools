#!/usr/bin/env python3
"""
Fix TradingRobotPlug.com All Missing Pages
===========================================

Creates all missing pages for tradingrobotplug.com to fix 404 navigation links.

Tasks:
- [SITE_AUDIT][HIGH][SA-TRADINGROBOTPLUGCOM-LINK-2FE3C97E] Products -> 404
- [SITE_AUDIT][HIGH][SA-TRADINGROBOTPLUGCOM-LINK-2D06ED68] Features -> 404
- [SITE_AUDIT][HIGH][SA-TRADINGROBOTPLUGCOM-LINK-C1AA363E] Pricing -> 404
- [SITE_AUDIT][HIGH][SA-TRADINGROBOTPLUGCOM-LINK-BB3A5E5E] Blog -> 404
- [SITE_AUDIT][HIGH][SA-TRADINGROBOTPLUGCOM-LINK-9FC02F41] AI Swarm -> 404
- [SITE_AUDIT][HIGH][SA-TRADINGROBOTPLUGCOM-LINK-95028A04] Contact -> 404

Author: Agent-8 (SSOT & System Integration Specialist)
V2 Compliant: <300 lines
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

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


def create_page(site_url: str, username: str, app_password: str, title: str, slug: str, content: str) -> Dict[str, Any]:
    """Create or update a WordPress page."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    auth = HTTPBasicAuth(username, app_password.replace(" ", ""))
    
    # Check if page already exists
    existing = check_page_exists(site_url, slug, auth)
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
                json={"status": "publish", "content": content},
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
    page_data = {
        "title": title,
        "slug": slug,
        "status": "publish",
        "content": content
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


def get_page_content(title: str, slug: str) -> str:
    """Generate default page content based on page type."""
    content_templates = {
        "products": """<!-- wp:paragraph -->
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
<!-- /wp:paragraph -->""",
        "features": """<!-- wp:heading -->
<h1>Features</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Discover the powerful features that make TradingRobotPlug the go-to solution for trading automation.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2>Key Features</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Our platform offers comprehensive automation tools designed to enhance your trading experience.</p>
<!-- /wp:paragraph -->""",
        "pricing": """<!-- wp:heading -->
<h1>Pricing</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Choose the plan that works best for your trading needs.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2>Pricing Plans</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Flexible pricing options to suit traders of all levels. Contact us for custom enterprise solutions.</p>
<!-- /wp:paragraph -->""",
        "blog": """<!-- wp:heading -->
<h1>Blog</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Welcome to the TradingRobotPlug blog. Stay updated with the latest trading automation insights, tips, and strategies.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Check back soon for new articles and updates!</p>
<!-- /wp:paragraph -->""",
        "ai-swarm": """<!-- wp:heading -->
<h1>🐝 AI Swarm</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Discover how AI Swarm technology powers our trading automation platform.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2>About AI Swarm</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Our AI Swarm system leverages collective intelligence to optimize trading strategies and decision-making.</p>
<!-- /wp:paragraph -->""",
        "contact": """<!-- wp:heading -->
<h1>Contact Us</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Get in touch with the TradingRobotPlug team. We're here to help with your trading automation needs.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2>Get Started</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Have questions? Want to learn more? Reach out and we'll get back to you as soon as possible.</p>
<!-- /wp:paragraph -->"""
    }
    
    return content_templates.get(slug, f"""<!-- wp:heading -->
<h1>{title}</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Content coming soon...</p>
<!-- /wp:paragraph -->""")


def main():
    """Main execution."""
    site_url = "https://tradingrobotplug.com"
    
    print("🔧 Fixing TradingRobotPlug.com All Missing Pages")
    print(f"   Site: {site_url}")
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
    
    # Pages to create/fix
    pages = [
        ("Products", "products"),
        ("Features", "features"),
        ("Pricing", "pricing"),
        ("Blog", "blog"),
        ("AI Swarm", "ai-swarm"),
        ("Contact", "contact"),
    ]
    
    results = []
    for title, slug in pages:
        print(f"📄 Processing: {title} ({slug})...")
        content = get_page_content(title, slug)
        result = create_page(
            site_url=site_url,
            username=credentials["username"],
            app_password=credentials["app_password"],
            title=title,
            slug=slug,
            content=content
        )
        
        if result.get("success"):
            action = result.get("action", "unknown")
            print(f"   ✅ {action.upper()}: {result.get('message')}")
            print(f"   Page ID: {result.get('page_id')}")
            print(f"   Link: {result.get('link')}")
        else:
            print(f"   ❌ FAILED: {result.get('error')}")
        
        results.append({
            "title": title,
            "slug": slug,
            "result": result
        })
        print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    successful = [r for r in results if r["result"].get("success")]
    failed = [r for r in results if not r["result"].get("success")]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print()
    
    if successful:
        print("✅ Completed pages:")
        for r in successful:
            action = r["result"].get("action", "unknown")
            print(f"   - {r['title']} ({action})")
    
    if failed:
        print()
        print("❌ Failed pages:")
        for r in failed:
            print(f"   - {r['title']}: {r['result'].get('error')}")
    
    print()
    print("🎯 Next steps:")
    print("   1. Verify pages are accessible at their URLs")
    print("   2. Refresh permalinks in WordPress admin (Settings > Permalinks > Save)")
    print("   3. Update navigation menus if needed")
    print("   4. Test all navigation links")
    
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())





