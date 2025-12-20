#!/usr/bin/env python3
"""
Debug FreeRideInvestor.com Login Issue
=======================================

Helps diagnose and fix HTTP 500 error preventing WordPress login.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import sys
import requests
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.wordpress_manager import WordPressManager
    HAS_WORDPRESS_MANAGER = True
except ImportError:
    HAS_WORDPRESS_MANAGER = False


def check_site_health(site_url: str) -> Dict[str, any]:
    """Check basic site health."""
    results = {
        "site_url": site_url,
        "homepage_accessible": False,
        "wp_admin_accessible": False,
        "rest_api_accessible": False,
        "status_code": None,
        "errors": []
    }
    
    print(f"🔍 Checking {site_url}...")
    print()
    
    # Check homepage
    try:
        response = requests.get(site_url, timeout=10, allow_redirects=True)
        results["status_code"] = response.status_code
        results["homepage_accessible"] = response.status_code == 200
        print(f"✅ Homepage: {response.status_code} {'OK' if response.status_code == 200 else 'ERROR'}")
    except Exception as e:
        results["errors"].append(f"Homepage check failed: {e}")
        print(f"❌ Homepage: Failed - {e}")
    
    # Check wp-admin
    wp_admin_url = f"{site_url}/wp-admin"
    try:
        response = requests.get(wp_admin_url, timeout=10, allow_redirects=True)
        results["wp_admin_accessible"] = response.status_code in [200, 302, 301]
        print(f"{'✅' if results['wp_admin_accessible'] else '❌'} wp-admin: {response.status_code}")
        if response.status_code == 500:
            results["errors"].append("HTTP 500 error on wp-admin")
    except Exception as e:
        results["errors"].append(f"wp-admin check failed: {e}")
        print(f"❌ wp-admin: Failed - {e}")
    
    # Check REST API
    rest_api_url = f"{site_url}/wp-json/"
    try:
        response = requests.get(rest_api_url, timeout=10)
        results["rest_api_accessible"] = response.status_code == 200
        print(f"{'✅' if results['rest_api_accessible'] else '❌'} REST API: {response.status_code}")
    except Exception as e:
        results["errors"].append(f"REST API check failed: {e}")
        print(f"❌ REST API: Failed - {e}")
    
    return results


def suggest_fixes(results: Dict) -> List[str]:
    """Suggest fixes based on diagnostic results."""
    suggestions = []
    
    if not results["homepage_accessible"]:
        suggestions.append("1. Check if site is down or DNS issues")
        suggestions.append("2. Verify hosting account is active")
    
    if not results["wp_admin_accessible"] or results["status_code"] == 500:
        suggestions.append("3. Enable WordPress debug mode to see error details")
        suggestions.append("4. Check wp-content/debug.log for PHP errors")
        suggestions.append("5. Check .htaccess file for syntax errors")
        suggestions.append("6. Check wp-config.php for errors")
        suggestions.append("7. Check PHP error logs in hosting control panel")
        suggestions.append("8. Temporarily disable plugins (rename plugins folder)")
        suggestions.append("9. Switch to default theme temporarily")
        suggestions.append("10. Check PHP memory limit (should be at least 128M)")
    
    if not results["rest_api_accessible"]:
        suggestions.append("11. Check if security plugins are blocking REST API")
        suggestions.append("12. Verify permalinks are set correctly")
    
    return suggestions


def enable_debug_mode() -> bool:
    """Enable WordPress debug mode via SFTP."""
    if not HAS_WORDPRESS_MANAGER:
        print("⚠️  WordPress manager not available")
        print("💡 Manual method:")
        print("   1. Connect via SFTP/FTP")
        print("   2. Edit wp-config.php")
        print("   3. Add before 'That's all, stop editing!':")
        print("      define('WP_DEBUG', true);")
        print("      define('WP_DEBUG_LOG', true);")
        print("      define('WP_DEBUG_DISPLAY', false);")
        return False
    
    try:
        print("🔧 Enabling WordPress debug mode...")
        manager = WordPressManager("freerideinvestor")
        
        if not manager.connect():
            print("❌ Failed to connect to server")
            print("💡 Check SFTP credentials in .deploy_credentials/sites.json")
            return False
        
        # Use the enable_wordpress_debug tool
        from tools.enable_wordpress_debug import enable_debug_mode
        success = enable_debug_mode("freerideinvestor", enable=True)
        
        manager.disconnect()
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main diagnostic function."""
    site_url = "https://freerideinvestor.com"
    
    print("=" * 60)
    print("🔧 FREERIDEINVESTOR.COM LOGIN DEBUGGING")
    print("=" * 60)
    print()
    
    # Step 1: Check site health
    print("STEP 1: Site Health Check")
    print("-" * 60)
    results = check_site_health(site_url)
    print()
    
    # Step 2: Show suggestions
    print("STEP 2: Suggested Fixes")
    print("-" * 60)
    suggestions = suggest_fixes(results)
    for suggestion in suggestions:
        print(f"   {suggestion}")
    print()
    
    # Step 3: Offer to enable debug mode
    if results.get("status_code") == 500 or not results.get("wp_admin_accessible"):
        print("STEP 3: Enable Debug Mode")
        print("-" * 60)
        response = input("Enable WordPress debug mode to see error details? (y/n): ").strip().lower()
        if response == 'y':
            enable_debug_mode()
            print()
            print("✅ Debug mode enabled!")
            print("💡 Next steps:")
            print("   1. Try accessing wp-admin again")
            print("   2. Check wp-content/debug.log for errors")
            print("   3. Check hosting error logs")
        print()
    
    # Step 4: Common fixes checklist
    print("STEP 4: Quick Fix Checklist")
    print("-" * 60)
    print("Common HTTP 500 fixes:")
    print("   □ Check .htaccess file (rename to .htaccess.bak to test)")
    print("   □ Increase PHP memory limit in wp-config.php")
    print("   □ Disable plugins (rename wp-content/plugins to plugins.bak)")
    print("   □ Switch to default theme")
    print("   □ Check database connection in wp-config.php")
    print("   □ Verify file permissions (755 for folders, 644 for files)")
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if results["wp_admin_accessible"]:
        print("✅ wp-admin is accessible - login should work")
    else:
        print("❌ wp-admin has issues - follow suggestions above")
        print()
        print("Most common fix: Check wp-content/debug.log after enabling debug mode")
    
    return 0 if results["wp_admin_accessible"] else 1


if __name__ == "__main__":
    sys.exit(main())

