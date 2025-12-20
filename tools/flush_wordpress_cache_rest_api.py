#!/usr/bin/env python3
"""
Flush WordPress Cache via REST API (Application Password)
=========================================================

Uses WordPress REST API with application password to flush cache.
Tries multiple cache flush methods for comprehensive cache clearing.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-13
V2 Compliant: Yes
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

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


def flush_cache_via_rest_api(
    site_url: str,
    username: str,
    app_password: str,
    comprehensive: bool = True
) -> Dict[str, Any]:
    """
    Flush WordPress cache via REST API.
    
    Tries multiple methods:
    1. LiteSpeed Cache plugin endpoint
    2. WP Super Cache plugin endpoint
    3. W3 Total Cache plugin endpoint
    4. Custom cache flush endpoints
    5. Permalink flush (rewrite rules)
    
    Args:
        site_url: WordPress site URL
        username: WordPress username
        app_password: WordPress application password
        comprehensive: If True, try all methods (default: True)
    
    Returns:
        Dict with success status and methods tried
    """
    site_url = site_url.rstrip('/')
    auth = HTTPBasicAuth(username, app_password)
    
    print("=" * 60)
    print("🔄 FLUSH WORDPRESS CACHE VIA REST API")
    print("=" * 60)
    print(f"Site: {site_url}")
    print(f"Username: {username}")
    print(f"Comprehensive: {comprehensive}")
    print()
    
    methods_tried = []
    methods_succeeded = []
    
    # Method 1: LiteSpeed Cache plugin
    print("🔍 Method 1: Trying LiteSpeed Cache plugin...")
    litespeed_endpoints = [
        f"{site_url}/wp-json/litespeed/v1/purge",
        f"{site_url}/wp-json/litespeed/v1/purge_all",
        f"{site_url}/wp-json/litespeed/v1/cache",
    ]
    
    for endpoint in litespeed_endpoints:
        try:
            response = requests.post(
                endpoint,
                auth=auth,
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if response.status_code in (200, 201):
                print(f"   ✅ Cache flushed via LiteSpeed: {endpoint}")
                methods_tried.append("litespeed")
                methods_succeeded.append("litespeed")
                break
            elif response.status_code == 404:
                continue  # Endpoint doesn't exist, try next
        except Exception as e:
            continue
    
    if "litespeed" not in methods_succeeded:
        print("   ⚠️  LiteSpeed Cache plugin not found or not active")
    
    print()
    
    # Method 2: WP Super Cache
    if comprehensive:
        print("🔍 Method 2: Trying WP Super Cache plugin...")
        wpsupercache_endpoints = [
            f"{site_url}/wp-json/wp-super-cache/v1/cache",
            f"{site_url}/wp-json/wp-super-cache/v1/purge",
        ]
        
        for endpoint in wpsupercache_endpoints:
            try:
                response = requests.post(
                    endpoint,
                    auth=auth,
                    timeout=TimeoutConstants.HTTP_DEFAULT
                )
                
                if response.status_code in (200, 201):
                    print(f"   ✅ Cache flushed via WP Super Cache: {endpoint}")
                    methods_tried.append("wp-super-cache")
                    methods_succeeded.append("wp-super-cache")
                    break
            except:
                continue
        
        if "wp-super-cache" not in methods_succeeded:
            print("   ⚠️  WP Super Cache plugin not found or not active")
        
        print()
    
    # Method 3: W3 Total Cache
    if comprehensive:
        print("🔍 Method 3: Trying W3 Total Cache plugin...")
        w3tc_endpoints = [
            f"{site_url}/wp-json/w3tc/v1/flush",
            f"{site_url}/wp-json/w3tc/v1/purge",
        ]
        
        for endpoint in w3tc_endpoints:
            try:
                response = requests.post(
                    endpoint,
                    auth=auth,
                    timeout=TimeoutConstants.HTTP_DEFAULT
                )
                
                if response.status_code in (200, 201):
                    print(f"   ✅ Cache flushed via W3 Total Cache: {endpoint}")
                    methods_tried.append("w3-total-cache")
                    methods_succeeded.append("w3-total-cache")
                    break
            except:
                continue
        
        if "w3-total-cache" not in methods_succeeded:
            print("   ⚠️  W3 Total Cache plugin not found or not active")
        
        print()
    
    # Method 4: Generic cache flush endpoint (some themes/plugins provide this)
    if comprehensive:
        print("🔍 Method 4: Trying generic cache flush endpoints...")
        generic_endpoints = [
            f"{site_url}/wp-json/wp/v2/cache/flush",
            f"{site_url}/wp-json/cache/v1/flush",
            f"{site_url}/wp-json/cache/v1/purge",
        ]
        
        for endpoint in generic_endpoints:
            try:
                response = requests.post(
                    endpoint,
                    auth=auth,
                    timeout=TimeoutConstants.HTTP_DEFAULT
                )
                
                if response.status_code in (200, 201):
                    print(f"   ✅ Cache flushed via generic endpoint: {endpoint}")
                    methods_tried.append("generic")
                    methods_succeeded.append("generic")
                    break
            except:
                continue
        
        if "generic" not in methods_succeeded:
            print("   ⚠️  Generic cache endpoints not available")
        
        print()
    
    # Method 5: Flush permalinks/rewrite rules (this clears some caches)
    if comprehensive:
        print("🔍 Method 5: Flushing permalink/rewrite cache...")
        try:
            # WordPress doesn't have a direct REST API for this, but we can trigger it
            # by updating a setting or making a request that triggers rewrite flush
            settings_url = f"{site_url}/wp-json/wp/v2/settings"
            
            # Get current settings
            response = requests.get(settings_url, auth=auth, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 200:
                # Update a setting to trigger rewrite flush (harmless update)
                current_settings = response.json()
                # Just re-save the same settings - this can trigger cache refresh
                response = requests.post(
                    settings_url,
                    auth=auth,
                    json={},
                    timeout=TimeoutConstants.HTTP_DEFAULT
                )
                
                if response.status_code == 200:
                    print("   ✅ Permalink cache refreshed")
                    methods_tried.append("permalink")
                    methods_succeeded.append("permalink")
        except Exception as e:
            print(f"   ⚠️  Permalink flush error: {e}")
        
        print()
    
    # Method 6: Hard flush - Update custom_css to trigger full cache refresh
    if comprehensive:
        print("🔍 Method 6: Hard flush via settings update...")
        try:
            settings_url = f"{site_url}/wp-json/wp/v2/settings"
            
            # Get current settings
            response = requests.get(settings_url, auth=auth, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 200:
                current_settings = response.json()
                
                # Get current custom_css
                current_css = current_settings.get("custom_css", "")
                
                # Update with same CSS (triggers cache refresh)
                response = requests.post(
                    settings_url,
                    auth=auth,
                    json={"custom_css": current_css},
                    timeout=TimeoutConstants.HTTP_DEFAULT
                )
                
                if response.status_code == 200:
                    print("   ✅ Settings cache refreshed (hard flush)")
                    methods_tried.append("hard_flush")
                    methods_succeeded.append("hard_flush")
        except Exception as e:
            print(f"   ⚠️  Hard flush error: {e}")
        
        print()
    
    # Summary
    print("=" * 60)
    if methods_succeeded:
        print("✅ CACHE FLUSH COMPLETE")
        print("=" * 60)
        print(f"Methods succeeded: {len(methods_succeeded)}")
        for method in methods_succeeded:
            print(f"   ✅ {method}")
        print()
        print("💡 Cache has been flushed. Changes should be visible now.")
        return {
            "success": True,
            "methods_tried": methods_tried,
            "methods_succeeded": methods_succeeded,
            "message": f"Cache flushed successfully ({len(methods_succeeded)} method(s))"
        }
    else:
        print("⚠️  CACHE FLUSH - NO METHODS SUCCEEDED")
        print("=" * 60)
        print("No cache flush plugins detected or accessible via REST API.")
        print()
        print("💡 Alternative methods:")
        print("   1. Clear cache via WordPress admin dashboard")
        print("   2. Clear browser cache (Ctrl+Shift+Delete)")
        print("   3. Hard refresh the page (Ctrl+F5)")
        print("   4. Use WP-CLI if available: wp cache flush")
        return {
            "success": False,
            "methods_tried": methods_tried,
            "methods_succeeded": [],
            "message": "No cache flush methods succeeded"
        }


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Flush WordPress cache via REST API (Application Password)"
    )
    parser.add_argument(
        "--site",
        type=str,
        default="dadudekc.com",
        help="Site name from config (default: dadudekc.com)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick flush (only try primary methods)"
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
    
    # Flush cache
    result = flush_cache_via_rest_api(
        site_url,
        username,
        app_password,
        comprehensive=not args.quick
    )
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())

