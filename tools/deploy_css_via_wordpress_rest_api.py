#!/usr/bin/env python3
"""
Deploy CSS to WordPress via REST API (Application Password)
===========================================================

Uses WordPress REST API with application password to update custom CSS.
Updates the custom_css theme mod via wp-json/wp/v2/settings endpoint.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-13
V2 Compliant: Yes
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("❌ requests library not available")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

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


def load_css_fix() -> str:
    """Load the CSS readability fix."""
    css_path = project_root / "docs" / "DADUDEKC_BLOG_READABILITY_FIX.css"
    
    if not css_path.exists():
        print(f"⚠️  CSS fix file not found: {css_path}")
        return ""
    
    return css_path.read_text(encoding='utf-8')


def update_custom_css_via_rest_api(
    site_url: str,
    username: str,
    app_password: str,
    css_content: str
) -> Dict[str, Any]:
    """
    Update WordPress custom CSS via REST API.
    
    WordPress stores custom CSS in theme mods. We'll try multiple approaches:
    1. wp-json/wp/v2/settings endpoint (if available)
    2. wp-json/wp/v2/theme-mods endpoint (if available)
    3. Direct theme mod update via custom endpoint
    
    Args:
        site_url: WordPress site URL
        username: WordPress username
        app_password: WordPress application password
        css_content: CSS content to add
    
    Returns:
        Dict with success status and message
    """
    site_url = site_url.rstrip('/')
    auth = HTTPBasicAuth(username, app_password)
    
    print("=" * 60)
    print("🚀 DEPLOY CSS VIA WORDPRESS REST API")
    print("=" * 60)
    print(f"Site: {site_url}")
    print(f"Username: {username}")
    print(f"CSS Size: {len(css_content):,} characters")
    print()
    
    # Method 1: Try wp-json/wp/v2/settings endpoint
    print("🔍 Method 1: Trying wp-json/wp/v2/settings endpoint...")
    settings_url = f"{site_url}/wp-json/wp/v2/settings"
    
    try:
        # First, get current settings to see structure
        response = requests.get(settings_url, auth=auth, timeout=TimeoutConstants.HTTP_DEFAULT)
        
        if response.status_code == 200:
            settings = response.json()
            print("✅ Settings endpoint accessible")
            
            # Try to update custom_css setting
            update_data = {"custom_css": css_content}
            response = requests.post(
                settings_url,
                auth=auth,
                json=update_data,
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if response.status_code == 200:
                print("✅ CSS updated via settings endpoint!")
                return {"success": True, "method": "settings", "message": "CSS updated successfully"}
            else:
                print(f"⚠️  Settings update returned: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        else:
            print(f"⚠️  Settings endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Settings endpoint error: {e}")
    
    print()
    
    # Method 2: Try customizer/theme-mods endpoint
    print("🔍 Method 2: Trying customizer endpoint...")
    # WordPress doesn't have a direct REST API for customizer, but some plugins add it
    # Try common customizer plugin endpoints
    
    customizer_endpoints = [
        f"{site_url}/wp-json/customizer/v1/css",
        f"{site_url}/wp-json/wp/v2/theme-mods",
        f"{site_url}/wp-json/customize/v1/css",
    ]
    
    for endpoint in customizer_endpoints:
        try:
            response = requests.post(
                endpoint,
                auth=auth,
                json={"css": css_content},
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if response.status_code == 200:
                print(f"✅ CSS updated via {endpoint}!")
                return {"success": True, "method": "customizer", "message": "CSS updated successfully"}
        except:
            continue
    
    print("⚠️  Customizer endpoints not available")
    print()
    
    # Method 3: Create/update a custom CSS post
    print("🔍 Method 3: Creating custom CSS post...")
    posts_url = f"{site_url}/wp-json/wp/v2/posts"
    
    # Check if custom CSS post already exists
    try:
        response = requests.get(
            posts_url,
            auth=auth,
            params={"search": "custom-css-readability-fix", "per_page": 1},
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        existing_posts = response.json() if response.status_code == 200 else []
        
        if existing_posts:
            # Update existing post
            post_id = existing_posts[0]["id"]
            update_url = f"{posts_url}/{post_id}"
            
            # Create HTML with style tag
            html_content = f'<style id="blog-readability-fix">\n{css_content}\n</style>'
            
            response = requests.post(
                update_url,
                auth=auth,
                json={"content": html_content, "status": "publish"},
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if response.status_code == 200:
                print(f"✅ Updated existing CSS post (ID: {post_id})")
                return {
                    "success": True,
                    "method": "post_update",
                    "message": f"CSS post updated (ID: {post_id})",
                    "post_id": post_id
                }
        else:
            # Create new post
            html_content = f'<style id="blog-readability-fix">\n{css_content}\n</style>'
            
            response = requests.post(
                posts_url,
                auth=auth,
                json={
                    "title": "Custom CSS - Blog Readability Fix",
                    "content": html_content,
                    "status": "publish",
                    "slug": "custom-css-readability-fix"
                },
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if response.status_code == 201:
                post_data = response.json()
                post_id = post_data["id"]
                print(f"✅ Created CSS post (ID: {post_id})")
                print("⚠️  Note: This creates a post, not Additional CSS")
                print("   You'll need to enqueue this CSS in your theme's functions.php")
                return {
                    "success": True,
                    "method": "post_create",
                    "message": f"CSS post created (ID: {post_id})",
                    "post_id": post_id,
                    "note": "Requires theme integration"
                }
    except Exception as e:
        print(f"⚠️  Post method error: {e}")
    
    print()
    print("=" * 60)
    print("❌ ALL METHODS FAILED")
    print("=" * 60)
    print()
    print("WordPress REST API doesn't directly support Additional CSS updates.")
    print("The custom CSS is stored in theme mods which aren't exposed via REST API.")
    print()
    print("💡 Alternative solutions:")
    print("   1. Use browser automation: tools/deploy_css_to_wordpress_customizer.py")
    print("   2. Deploy CSS file to theme and enqueue in functions.php")
    print("   3. Use WordPress Customizer manually")
    print()
    
    return {
        "success": False,
        "message": "WordPress REST API doesn't support Additional CSS updates",
        "alternatives": [
            "Use browser automation tool",
            "Deploy CSS file to theme directory",
            "Manual Customizer update"
        ]
    }


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Deploy CSS to WordPress via REST API (Application Password)"
    )
    parser.add_argument(
        "--site",
        type=str,
        default="dadudekc.com",
        help="Site name from config (default: dadudekc.com)"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_blogging_config()
    
    site_key = args.site
    if site_key not in config:
        print(f"❌ {site_key} not found in blogging config")
        return 1
    
    site_config = config[site_key]
    site_url = site_config["site_url"]
    username = site_config["username"]
    app_password = site_config["app_password"]
    
    if not app_password:
        print(f"❌ Application password not configured for {site_key}")
        print("   Add 'app_password' to blogging_api.json")
        return 1
    
    # Load CSS fix
    css_fix = load_css_fix()
    if not css_fix:
        print("❌ Could not load CSS fix file")
        return 1
    
    # Deploy CSS
    result = update_custom_css_via_rest_api(site_url, username, app_password, css_fix)
    
    if result["success"]:
        print()
        print("=" * 60)
        print("✅ SUCCESS")
        print("=" * 60)
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Message: {result.get('message', '')}")
        if "post_id" in result:
            print(f"Post ID: {result['post_id']}")
        if "note" in result:
            print(f"Note: {result['note']}")
        return 0
    else:
        print()
        print("=" * 60)
        print("❌ FAILED")
        print("=" * 60)
        print(f"Message: {result.get('message', 'Unknown error')}")
        if "alternatives" in result:
            print("\nAlternatives:")
            for alt in result["alternatives"]:
                print(f"   - {alt}")
        return 1


if __name__ == "__main__":
    sys.exit(main())




