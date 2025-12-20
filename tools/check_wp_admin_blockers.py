#!/usr/bin/env python3
"""
Check WordPress Admin Blockers
===============================

Diagnoses security plugins and .htaccess rules that might block wp-admin access.

Author: Agent-2 (Architecture & Design Specialist)
"""

import requests
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_wp_admin_response(site_url: str) -> Dict:
    """Check wp-admin response for blocking patterns."""
    wp_admin_url = f"{site_url}/wp-admin"
    wp_login_url = f"{site_url}/wp-login.php"
    
    results = {
        "wp_admin_status": None,
        "wp_login_status": None,
        "wp_admin_redirects": [],
        "wp_login_redirects": [],
        "blocking_indicators": [],
        "security_plugin_indicators": []
    }
    
    print(f"🔍 Checking {wp_admin_url}...")
    
    try:
        # Check wp-admin with redirect tracking
        response = requests.get(
            wp_admin_url,
            timeout=10,
            allow_redirects=False  # Don't follow redirects to detect them
        )
        
        results["wp_admin_status"] = response.status_code
        
        # If redirected, check redirect location
        if response.status_code in [301, 302, 307, 308]:
            redirect_location = response.headers.get('Location', '')
            results["wp_admin_redirects"].append(redirect_location)
            results["wp_admin_final_url"] = redirect_location
            
            # Follow redirects manually to detect loops
            try:
                follow_response = requests.get(
                    wp_admin_url,
                    timeout=10,
                    allow_redirects=True,
                    max_redirects=5
                )
                results["wp_admin_final_status"] = follow_response.status_code
                results["wp_admin_redirects"] = [r.url for r in follow_response.history]
            except requests.exceptions.TooManyRedirects:
                results["blocking_indicators"].append("Redirect loop detected")
        else:
            results["wp_admin_final_url"] = response.url
        
        # Check for blocking indicators in response
        html = response.text.lower()
        
        # Common security plugin blocking messages
        blocking_patterns = [
            (r'wordfence', 'Wordfence security plugin'),
            (r'ithemes security', 'iThemes Security plugin'),
            (r'sucuri', 'Sucuri security plugin'),
            (r'all in one wp security', 'All In One WP Security plugin'),
            (r'bulletproof security', 'BulletProof Security plugin'),
            (r'better wp security', 'Better WP Security plugin'),
            (r'login lockdown', 'Login Lockdown plugin'),
            (r'limit login attempts', 'Limit Login Attempts plugin'),
            (r'wp fail2ban', 'WP Fail2Ban plugin'),
            (r'security.*blocked', 'Security plugin blocking'),
            (r'access.*denied', 'Access denied message'),
            (r'403.*forbidden', '403 Forbidden'),
            (r'blocked.*ip', 'IP blocked message'),
            (r'too many.*attempts', 'Too many login attempts'),
        ]
        
        for pattern, description in blocking_patterns:
            if re.search(pattern, html):
                results["blocking_indicators"].append(description)
                results["security_plugin_indicators"].append(description)
        
        # Check for .htaccess redirect patterns
        if response.status_code in [301, 302, 307, 308]:
            if len(response.history) > 3:
                results["blocking_indicators"].append("Multiple redirects (possible .htaccess loop)")
        
    except requests.exceptions.TooManyRedirects:
        results["blocking_indicators"].append("Redirect loop detected (exceeds max redirects)")
    except Exception as e:
        results["error"] = str(e)
    
    # Check wp-login.php
    try:
        login_response = requests.get(
            wp_login_url,
            timeout=10,
            allow_redirects=True,
            max_redirects=5
        )
        
        results["wp_login_status"] = login_response.status_code
        results["wp_login_redirects"] = [r.url for r in login_response.history]
        results["wp_login_final_url"] = login_response.url
        
    except Exception as e:
        results["login_error"] = str(e)
    
    return results


def check_rest_api_for_plugins(site_url: str) -> Dict:
    """Check REST API for plugin information."""
    rest_api_url = f"{site_url}/wp-json/wp/v2/"
    
    results = {
        "rest_api_accessible": False,
        "plugins_detected": [],
        "security_plugins": []
    }
    
    try:
        response = requests.get(rest_api_url, timeout=10)
        
        if response.status_code == 200:
            results["rest_api_accessible"] = True
            
            # Try to get plugin list (if accessible)
            plugins_url = f"{site_url}/wp-json/wp/v2/plugins"
            try:
                plugins_response = requests.get(plugins_url, timeout=10)
                if plugins_response.status_code == 200:
                    plugins_data = plugins_response.json()
                    results["plugins_detected"] = [p.get("name", "Unknown") for p in plugins_data]
            except:
                pass  # Plugin endpoint might not be accessible
            
    except Exception as e:
        results["error"] = str(e)
    
    # Common security plugin names to check
    security_plugin_names = [
        "wordfence",
        "ithemes-security",
        "sucuri",
        "all-in-one-wp-security",
        "bulletproof-security",
        "better-wp-security",
        "login-lockdown",
        "limit-login-attempts",
        "wp-fail2ban",
        "security",
        "wps-hide-login",
        "rename-wp-login",
    ]
    
    # Check if any security plugins are in detected plugins
    for plugin in results.get("plugins_detected", []):
        plugin_lower = plugin.lower()
        for sec_plugin in security_plugin_names:
            if sec_plugin in plugin_lower:
                results["security_plugins"].append(plugin)
    
    return results


def suggest_fixes(diagnosis: Dict) -> List[str]:
    """Suggest fixes based on diagnosis."""
    suggestions = []
    
    if diagnosis.get("blocking_indicators"):
        suggestions.append("🔒 SECURITY PLUGIN OR .htaccess BLOCKING DETECTED")
        suggestions.append("")
        suggestions.append("Fix 1: Disable Security Plugins (via SFTP/File Manager)")
        suggestions.append("   1. Access site via SFTP or Hostinger File Manager")
        suggestions.append("   2. Navigate to: wp-content/plugins/")
        suggestions.append("   3. Rename security plugin folders (add -disabled suffix)")
        suggestions.append("   4. Common security plugins to check:")
        for indicator in diagnosis.get("security_plugin_indicators", []):
            suggestions.append(f"      - {indicator}")
        suggestions.append("")
        suggestions.append("Fix 2: Check .htaccess File")
        suggestions.append("   1. Access site via SFTP or File Manager")
        suggestions.append("   2. Navigate to: public_html/.htaccess")
        suggestions.append("   3. Look for rules blocking wp-admin or wp-login.php")
        suggestions.append("   4. Common blocking patterns:")
        suggestions.append("      - RewriteRule.*wp-admin")
        suggestions.append("      - RewriteRule.*wp-login")
        suggestions.append("      - Deny from all")
        suggestions.append("   5. Temporarily rename .htaccess to .htaccess.bak to test")
        suggestions.append("")
        suggestions.append("Fix 3: Check wp-config.php")
        suggestions.append("   1. Look for: define('DISALLOW_FILE_EDIT', true)")
        suggestions.append("   2. Look for: define('WP_DEBUG', false)")
        suggestions.append("   3. Check for custom login URL settings")
        suggestions.append("")
        suggestions.append("Fix 4: Whitelist Your IP (if IP blocking)")
        suggestions.append("   1. Access security plugin settings (if accessible)")
        suggestions.append("   2. Add your IP to whitelist")
        suggestions.append("   3. Or disable IP blocking temporarily")
    
    if diagnosis.get("wp_admin_status") in [403, 401]:
        suggestions.append("")
        suggestions.append("🔐 AUTHENTICATION REQUIRED")
        suggestions.append("   Status 403/401 means authentication is required")
        suggestions.append("   This is normal - you need to log in")
        suggestions.append("   Try: https://freerideinvestor.com/wp-login.php")
    
    if len(diagnosis.get("wp_admin_redirects", [])) > 3:
        suggestions.append("")
        suggestions.append("🔄 REDIRECT LOOP DETECTED")
        suggestions.append("   Multiple redirects indicate redirect loop")
        suggestions.append("   See: docs/FREERIDE_WP_ADMIN_REDIRECT_LOOP_FIX.md")
    
    return suggestions


def main():
    """Main diagnostic function."""
    site_url = "https://freerideinvestor.com"
    
    print("=" * 70)
    print("🔒 WORDPRESS ADMIN BLOCKER DIAGNOSTIC")
    print("=" * 70)
    print()
    
    # Step 1: Check wp-admin response
    print("STEP 1: Checking wp-admin access...")
    print("-" * 70)
    admin_check = check_wp_admin_response(site_url)
    
    print(f"   wp-admin Status: {admin_check.get('wp_admin_status', 'Unknown')}")
    print(f"   wp-login.php Status: {admin_check.get('wp_login_status', 'Unknown')}")
    
    if admin_check.get("blocking_indicators"):
        print()
        print("   ⚠️  BLOCKING INDICATORS DETECTED:")
        for indicator in admin_check["blocking_indicators"]:
            print(f"      - {indicator}")
    
    if admin_check.get("wp_admin_redirects"):
        print()
        print(f"   Redirects: {len(admin_check['wp_admin_redirects'])} redirects detected")
        if len(admin_check["wp_admin_redirects"]) > 3:
            print("   ⚠️  Multiple redirects - possible redirect loop")
    
    print()
    
    # Step 2: Check REST API for plugins
    print("STEP 2: Checking for security plugins...")
    print("-" * 70)
    plugin_check = check_rest_api_for_plugins(site_url)
    
    if plugin_check.get("rest_api_accessible"):
        print("   ✅ REST API accessible")
        if plugin_check.get("security_plugins"):
            print()
            print("   ⚠️  SECURITY PLUGINS DETECTED:")
            for plugin in plugin_check["security_plugins"]:
                print(f"      - {plugin}")
        else:
            print("   ℹ️  No security plugins detected via REST API")
    else:
        print("   ⚠️  REST API not accessible (may be blocked)")
    
    print()
    
    # Step 3: Show suggestions
    print("STEP 3: Recommended Fixes")
    print("-" * 70)
    suggestions = suggest_fixes(admin_check)
    for suggestion in suggestions:
        print(f"   {suggestion}")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if admin_check.get("blocking_indicators"):
        print("❌ wp-admin appears to be blocked")
        print()
        print("MOST LIKELY CAUSES:")
        print("   1. Security plugin blocking access")
        print("   2. .htaccess rules blocking wp-admin")
        print("   3. IP address blocked by security plugin")
        print()
        print("IMMEDIATE ACTION:")
        print("   1. Access site via SFTP/File Manager")
        print("   2. Disable security plugins (rename plugin folders)")
        print("   3. Check .htaccess for blocking rules")
        print("   4. Test wp-admin access")
    else:
        print("✅ No obvious blocking detected")
        print("   wp-admin may be accessible - try logging in")
        print("   URL: https://freerideinvestor.com/wp-login.php")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

