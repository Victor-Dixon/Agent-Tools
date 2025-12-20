#!/usr/bin/env python3
"""
WordPress API Connectivity Test Script
======================================

Tests API connectivity for all configured WordPress sites.
Validates credentials and REST API availability.

Usage:
    python tools/test_blogging_api_connectivity.py [--site SITE_ID]

Author: Agent-2 (Architecture & Design Specialist)
V2 Compliant: <400 lines
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
    print("❌ ERROR: requests library not installed")
    print("   Install with: pip install requests")
    sys.exit(1)

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_QUICK = 5
        HTTP_DEFAULT = 30


def test_rest_api(site_url: str) -> Dict[str, Any]:
    """Test if WordPress REST API is accessible."""
    try:
        api_url = f"{site_url.rstrip('/')}/wp-json/"
        response = requests.get(
            api_url,
            timeout=TimeoutConstants.HTTP_QUICK
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "api_available": True,
                "wp_version": data.get("version", "unknown"),
                "name": data.get("name", "unknown")
            }
        else:
            return {
                "success": False,
                "api_available": False,
                "error": f"HTTP {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "api_available": False,
            "error": str(e)
        }


def test_authentication(
    site_url: str,
    username: str,
    app_password: str
) -> Dict[str, Any]:
    """Test WordPress authentication with Application Password."""
    try:
        # Test authentication by accessing user endpoint
        api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/users/me"
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(username, app_password),
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                "success": True,
                "authenticated": True,
                "user_id": user_data.get("id"),
                "user_name": user_data.get("name"),
                "user_role": user_data.get("roles", [])
            }
        elif response.status_code == 401:
            return {
                "success": False,
                "authenticated": False,
                "error": "Authentication failed - check username and app_password"
            }
        else:
            return {
                "success": False,
                "authenticated": False,
                "error": f"HTTP {response.status_code}: {response.text[:100]}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "authenticated": False,
            "error": str(e)
        }


def test_site_connectivity(site_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test full connectivity for a single site."""
    site_url = config.get("site_url")
    username = config.get("username")
    app_password = config.get("app_password")
    
    # Check if credentials are configured
    if username == "REPLACE_WITH_WORDPRESS_USERNAME" or \
       app_password == "REPLACE_WITH_APPLICATION_PASSWORD":
        return {
            "site_id": site_id,
            "configured": False,
            "message": "⚠️  Credentials not configured (using placeholders)"
        }
    
    print(f"\n🔍 Testing {site_id} ({site_url})...")
    
    # Test REST API availability
    api_test = test_rest_api(site_url)
    
    # Test authentication
    auth_test = test_authentication(site_url, username, app_password)
    
    return {
        "site_id": site_id,
        "site_url": site_url,
        "configured": True,
        "api_test": api_test,
        "auth_test": auth_test,
        "overall_success": api_test.get("success") and auth_test.get("success")
    }


def main():
    """Main test function."""
    config_path = Path(".deploy_credentials/blogging_api.json")
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        print("   Create it from: .deploy_credentials/blogging_api.json.example")
        sys.exit(1)
    
    # Load configuration
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        sys.exit(1)
    
    # Check for site filter
    site_filter = None
    if len(sys.argv) > 1 and sys.argv[1] == "--site":
        if len(sys.argv) > 2:
            site_filter = sys.argv[2]
        else:
            print("❌ --site requires a site ID")
            sys.exit(1)
    
    print("=" * 60)
    print("WordPress API Connectivity Test")
    print("=" * 60)
    
    results = []
    sites_to_test = {site_filter: config[site_filter]} if site_filter else config
    
    for site_id, site_config in sites_to_test.items():
        result = test_site_connectivity(site_id, site_config)
        results.append(result)
        
        # Print results
        if not result.get("configured"):
            print(f"   {result['message']}")
        else:
            api_test = result.get("api_test", {})
            auth_test = result.get("auth_test", {})
            
            # API Test
            if api_test.get("success"):
                print(f"   ✅ REST API: Available (WP {api_test.get('wp_version', 'unknown')})")
            else:
                print(f"   ❌ REST API: {api_test.get('error', 'Unknown error')}")
            
            # Auth Test
            if auth_test.get("success"):
                user_name = auth_test.get("user_name", "unknown")
                user_role = ", ".join(auth_test.get("user_role", []))
                print(f"   ✅ Authentication: Success (User: {user_name}, Role: {user_role})")
            else:
                print(f"   ❌ Authentication: {auth_test.get('error', 'Unknown error')}")
            
            # Overall
            if result.get("overall_success"):
                print(f"   ✅ {site_id}: FULLY OPERATIONAL")
            else:
                print(f"   ⚠️  {site_id}: Issues detected")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    configured = [r for r in results if r.get("configured")]
    operational = [r for r in configured if r.get("overall_success")]
    
    print(f"Total sites: {len(results)}")
    print(f"Configured: {len(configured)}/{len(results)}")
    print(f"Operational: {len(operational)}/{len(configured)}")
    
    if len(operational) == len(configured) and len(configured) > 0:
        print("\n✅ All configured sites are operational!")
    elif len(configured) == 0:
        print("\n⚠️  No sites have credentials configured yet.")
        print("   Edit .deploy_credentials/blogging_api.json with your credentials.")
    else:
        print(f"\n⚠️  {len(configured) - len(operational)} site(s) have issues.")
    
    return 0 if len(operational) == len(configured) else 1


if __name__ == "__main__":
    sys.exit(main())
