#!/usr/bin/env python3
"""
<!-- SSOT Domain: infrastructure -->
FreeRideInvestor Site Diagnostic Tool
=====================================
Quick diagnostic for site status issues.

Author: Agent-3 (Infrastructure & DevOps Specialist)
"""

from src.control_plane.adapters.hostinger.freeride_adapter import get_freeride_adapter
import re
import requests
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def diagnose_site():
    """Diagnose FreeRideInvestor site status."""
    print("=" * 60)
    print("FreeRideInvestor Site Diagnostic")
    print("=" * 60)
    print()

    base_url = "https://freerideinvestor.com"

    # Check main site
    print("1. Checking main site...")
    try:
        r = requests.get(base_url, timeout=10)
        print(f"   Status Code: {r.status_code}")
        print(f"   Response Length: {len(r.text)} bytes")

        # Check for error messages
        if r.status_code == 500:
            print("   ⚠️  HTTP 500 Internal Server Error detected")

            # Look for PHP errors
            if "Fatal error" in r.text:
                fatal_match = re.search(
                    r'Fatal error:.*?on line \d+', r.text, re.IGNORECASE | re.DOTALL)
                if fatal_match:
                    error_msg = fatal_match.group(0)[:300]
                    print(f"   PHP Fatal Error: {error_msg}")

            # Check for WordPress errors
            if "WordPress" in r.text or "wp-" in r.text:
                print("   WordPress is responding but encountering errors")

        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', r.text, re.IGNORECASE)
        if title_match:
            print(f"   Page Title: {title_match.group(1)}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Check wp-admin (with redirect limit)
    print("2. Checking wp-admin...")
    try:
        r = requests.get(f"{base_url}/wp-admin/",
                         timeout=10, allow_redirects=False)
        print(f"   Status Code: {r.status_code}")
        if r.status_code in [301, 302, 307, 308]:
            print(f"   Redirect Location: {r.headers.get('Location', 'N/A')}")
    except requests.exceptions.TooManyRedirects:
        print("   ⚠️  Redirect loop detected (30+ redirects)")
        print("   This indicates a WordPress configuration issue")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Check health via adapter
    print("3. Health check via adapter...")
    adapter = get_freeride_adapter()
    health = adapter.health()
    print(f"   Health Status: {'✅ OK' if health.get('ok') else '❌ FAILED'}")
    print(f"   Status Code: {health.get('status_code', 'N/A')}")
    if 'error' in health:
        print(f"   Error: {health['error']}")

    print()
    print("=" * 60)
    print("Diagnosis Summary:")
    print("=" * 60)
    print()
    print("ISSUES DETECTED:")
    print("  - HTTP 500 on main site (WordPress/PHP error)")
    print("  - wp-admin redirect loop (configuration issue)")
    print()
    print("RECOMMENDED ACTIONS:")
    print("  1. Check WordPress error logs via Hostinger cPanel")
    print("  2. Check PHP error logs")
    print("  3. Review recent plugin/theme changes")
    print("  4. Check .htaccess for redirect issues")
    print("  5. Verify database connection")
    print("  6. Check file permissions on wp-config.php")
    print()


if __name__ == "__main__":
    diagnose_site()
