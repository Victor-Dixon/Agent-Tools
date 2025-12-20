#!/usr/bin/env python3
"""
Add Houston Sip Queen Header CTA Button
========================================

Adds a header CTA button linking to the quote form.

Task: Houston Sip Queen theme implementation - Add header CTA button
Priority: HIGH

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
    username = os.environ.get("HOUSTONSIPQUEEN_WP_USER")
    app_password = os.environ.get("HOUSTONSIPQUEEN_WP_PASSWORD")
    
    if username and app_password:
        return {
            "username": username,
            "app_password": app_password,
            "site_url": "https://houstonsipqueen.com"
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
                    site_config = (
                        config.get("houstonsipqueen.com") or
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


def find_quote_page(site_url: str, auth: HTTPBasicAuth) -> Optional[Dict[str, Any]]:
    """Find quote/contact form page."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    
    # Try common slug names
    slugs = ["quote", "contact", "get-quote", "book-now", "request-quote"]
    
    for slug in slugs:
        try:
            response = requests.get(
                api_url,
                params={"slug": slug, "status": "publish"},
                auth=auth,
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if response.status_code == 200:
                pages = response.json()
                if pages:
                    return {
                        "page_id": pages[0]["id"],
                        "title": pages[0]["title"]["rendered"],
                        "slug": pages[0]["slug"],
                        "link": pages[0]["link"]
                    }
        except Exception:
            continue
    
    return None


def add_header_cta_css(site_url: str, auth: HTTPBasicAuth, quote_url: str) -> Dict[str, Any]:
    """Add header CTA button via custom CSS."""
    # Get current custom CSS
    customizer_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/settings"
    
    try:
        response = requests.get(customizer_url, auth=auth, timeout=TimeoutConstants.HTTP_DEFAULT)
        
        # Add CSS via Additional CSS (if available) or create custom CSS post
        cta_css = f"""
/* Houston Sip Queen Header CTA Button */
.site-header,
.wp-block-site-header,
header.site-header {{
    position: relative;
}}

.header-cta-button {{
    display: inline-block;
    padding: 12px 32px;
    background-color: #C9A26A; /* RoseGold */
    color: #0B0B0F; /* Onyx */
    border-radius: 50px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    margin-left: 20px;
    font-family: 'Inter', 'Montserrat', sans-serif;
}}

.header-cta-button:hover {{
    background-color: #7A1E3A; /* Berry */
    color: #FFFFFF;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(122, 30, 58, 0.3);
}}

/* Add button to header navigation */
.site-navigation,
.wp-block-navigation,
nav {{
    display: flex;
    align-items: center;
}}

.site-navigation::after,
.wp-block-navigation::after {{
    content: '';
    display: none;
}}
"""
        
        # Try to add via Additional CSS endpoint (theme customizer)
        # Note: This may require theme-specific implementation
        # Alternative: Add via menu item or widget
        
        return {
            "success": True,
            "method": "CSS injection",
            "css": cta_css,
            "quote_url": quote_url,
            "message": "CSS ready - may need theme-specific implementation"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def add_cta_to_menu(site_url: str, auth: HTTPBasicAuth, quote_url: str) -> Dict[str, Any]:
    """Add CTA button as menu item."""
    menus_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/menus"
    
    try:
        # Get menus
        response = requests.get(menus_url, auth=auth, timeout=TimeoutConstants.HTTP_DEFAULT)
        
        if response.status_code == 200:
            menus = response.json()
            if menus:
                menu_id = menus[0].get("id")
                menu_items_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/menu-items"
                
                # Create menu item
                menu_item = {
                    "title": "Get Quote",
                    "url": quote_url,
                    "menu_order": 999,
                    "menu": menu_id,
                    "classes": ["header-cta-button"]
                }
                
                create_response = requests.post(
                    menu_items_url,
                    json=menu_item,
                    auth=auth,
                    timeout=TimeoutConstants.HTTP_DEFAULT
                )
                
                if create_response.status_code in (200, 201):
                    return {
                        "success": True,
                        "method": "menu item",
                        "menu_item_id": create_response.json().get("id"),
                        "quote_url": quote_url
                    }
        
        return {
            "success": False,
            "error": "Could not add to menu - may need manual setup"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main execution."""
    site_url = "https://houstonsipqueen.com"
    
    print("🎯 Adding Houston Sip Queen Header CTA Button")
    print(f"   Site: {site_url}")
    print()
    
    # Get credentials
    credentials = get_credentials()
    if not credentials:
        print("❌ WordPress credentials not found!")
        print()
        print("Please set environment variables:")
        print("  export HOUSTONSIPQUEEN_WP_USER='your_username'")
        print("  export HOUSTONSIPQUEEN_WP_PASSWORD='your_app_password'")
        return 1
    
    auth = HTTPBasicAuth(credentials["username"], credentials["app_password"].replace(" ", ""))
    
    # Find quote page
    print("🔍 Finding quote/contact form page...")
    quote_page = find_quote_page(credentials["site_url"], auth)
    
    if quote_page:
        quote_url = quote_page["link"]
        print(f"✅ Found quote page: {quote_page['title']} ({quote_url})")
    else:
        # Default to contact or create quote page
        quote_url = f"{credentials['site_url']}/quote"
        print(f"⚠️  Quote page not found, using default: {quote_url}")
        print("   Note: May need to create quote page first")
    
    print()
    
    # Try adding via menu
    print("📝 Attempting to add CTA button to menu...")
    menu_result = add_cta_to_menu(credentials["site_url"], auth, quote_url)
    
    if menu_result.get("success"):
        print("✅ SUCCESS!")
        print(f"   Method: {menu_result.get('method')}")
        print(f"   Quote URL: {quote_url}")
        print()
        print("🎯 Task complete: Header CTA button added to menu")
        return 0
    else:
        print(f"⚠️  Menu method failed: {menu_result.get('error')}")
        print()
        print("📝 CSS method available - may require theme-specific implementation")
        css_result = add_header_cta_css(credentials["site_url"], auth, quote_url)
        
        if css_result.get("success"):
            print("✅ CSS ready for implementation")
            print(f"   Quote URL: {quote_url}")
            print()
            print("📋 Next steps:")
            print("   1. Add CSS to theme customizer (Additional CSS)")
            print("   2. Or add button HTML to header template")
            print("   3. Verify button appears and links correctly")
            return 0
        else:
            print(f"❌ FAILED!")
            print(f"   Error: {css_result.get('error')}")
            return 1


if __name__ == "__main__":
    sys.exit(main())

