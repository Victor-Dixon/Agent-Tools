#!/usr/bin/env python3
"""
Fix FreeRideInvestor wp-admin Redirect Loop
===========================================

Diagnoses and provides fixes for WordPress wp-admin redirect loop.

Author: Agent-2 (Architecture & Design Specialist)
"""

import requests
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def check_wp_admin_redirect(site_url: str) -> dict:
    """Check wp-admin redirect status."""
    wp_admin_url = f"{site_url}/wp-admin"
    
    print(f"🔍 Checking {wp_admin_url}...")
    
    try:
        # Follow redirects but limit to 5 to detect loop
        response = requests.get(
            wp_admin_url,
            timeout=10,
            allow_redirects=True,
            max_redirects=5
        )
        
        return {
            "status_code": response.status_code,
            "final_url": response.url,
            "redirect_count": len(response.history),
            "is_loop": response.url == wp_admin_url and response.status_code in [301, 302]
        }
    except requests.exceptions.TooManyRedirects:
        return {
            "status_code": None,
            "error": "Redirect loop detected (exceeded max redirects)",
            "is_loop": True
        }
    except Exception as e:
        return {
            "status_code": None,
            "error": str(e),
            "is_loop": False
        }


def check_site_url_config(site_url: str) -> dict:
    """Check WordPress site URL configuration via REST API."""
    rest_api_url = f"{site_url}/wp-json/wp/v2/"
    
    print(f"🔍 Checking WordPress configuration via REST API...")
    
    try:
        response = requests.get(rest_api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "rest_api_works": True,
                "site_name": data.get("name", "Unknown"),
                "site_url": data.get("url", "Unknown"),
                "home_url": data.get("home", "Unknown")
            }
        else:
            return {
                "rest_api_works": False,
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "rest_api_works": False,
            "error": str(e)
        }


def suggest_fixes(diagnosis: dict) -> list:
    """Suggest fixes based on diagnosis."""
    suggestions = []
    
    if diagnosis.get("is_loop"):
        suggestions.append("1. Fix WordPress Site URL in wp-config.php:")
        suggestions.append("   Add: define('WP_HOME','https://freerideinvestor.com');")
        suggestions.append("   Add: define('WP_SITEURL','https://freerideinvestor.com');")
        suggestions.append("")
        suggestions.append("2. Check .htaccess for redirect loops:")
        suggestions.append("   Temporarily rename .htaccess to .htaccess.bak")
        suggestions.append("")
        suggestions.append("3. Disable plugins that might cause redirects:")
        suggestions.append("   Security plugins, SSL plugins, maintenance mode plugins")
        suggestions.append("")
        suggestions.append("4. Check wp-config.php for redirect settings:")
        suggestions.append("   Remove or fix: FORCE_SSL_ADMIN, COOKIE_DOMAIN")
    
    return suggestions


def main():
    """Main diagnostic function."""
    site_url = "https://freerideinvestor.com"
    
    print("=" * 70)
    print("🔧 FREERIDEINVESTOR.COM WP-ADMIN REDIRECT LOOP FIX")
    print("=" * 70)
    print()
    
    # Check redirect status
    print("STEP 1: Checking wp-admin redirect status...")
    print("-" * 70)
    redirect_status = check_wp_admin_redirect(site_url)
    
    if redirect_status.get("is_loop"):
        print("❌ REDIRECT LOOP DETECTED")
        print(f"   Error: {redirect_status.get('error', 'Too many redirects')}")
    else:
        print(f"✅ Status: {redirect_status.get('status_code', 'Unknown')}")
        print(f"   Final URL: {redirect_status.get('final_url', 'N/A')}")
    
    print()
    
    # Check site configuration
    print("STEP 2: Checking WordPress configuration...")
    print("-" * 70)
    config = check_site_url_config(site_url)
    
    if config.get("rest_api_works"):
        print(f"✅ REST API working")
        print(f"   Site: {config.get('site_name', 'Unknown')}")
        print(f"   URL: {config.get('site_url', 'Unknown')}")
        print(f"   Home: {config.get('home_url', 'Unknown')}")
    else:
        print(f"❌ REST API check failed: {config.get('error', 'Unknown error')}")
    
    print()
    
    # Show suggestions
    print("STEP 3: Recommended Fixes")
    print("-" * 70)
    suggestions = suggest_fixes(redirect_status)
    for suggestion in suggestions:
        print(f"   {suggestion}")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if redirect_status.get("is_loop"):
        print("❌ wp-admin has redirect loop")
        print()
        print("MOST COMMON FIX:")
        print("   1. Access Hostinger File Manager")
        print("   2. Edit wp-config.php")
        print("   3. Add these lines BEFORE 'That's all, stop editing!':")
        print("      define('WP_HOME','https://freerideinvestor.com');")
        print("      define('WP_SITEURL','https://freerideinvestor.com');")
        print("   4. Save and test wp-admin")
    else:
        print("✅ wp-admin appears accessible (no redirect loop detected)")
    
    return 0 if not redirect_status.get("is_loop") else 1


if __name__ == "__main__":
    sys.exit(main())



