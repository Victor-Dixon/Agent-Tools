#!/usr/bin/env python3
"""Check if /dashboard page exists and what it does."""

import requests
import sys

def check_dashboard(url):
    """Check dashboard page."""
    print("=" * 60)
    print("Checking /dashboard Page")
    print("=" * 60)
    print(f"URL: {url}/dashboard")
    print()
    
    # Check dashboard page
    try:
        r = requests.get(f"{url}/dashboard", timeout=10, allow_redirects=False)
        print(f"Status Code: {r.status_code}")
        if r.status_code in [301, 302, 307, 308]:
            print(f"Redirect Location: {r.headers.get('Location', 'N/A')}")
        print(f"Content Length: {len(r.text)} bytes")
        print()
        
        # Check with redirects
        r2 = requests.get(f"{url}/dashboard", timeout=10, allow_redirects=True, max_redirects=5)
        print(f"With Redirects - Status: {r2.status_code}")
        print(f"Final URL: {r2.url}")
        print(f"Has redirect loop: {'⚠️  Yes' if 'dashboard' in r2.url and r2.status_code != 200 else '✅ No'}")
        print()
        
        # Check content
        if "wp-admin" in r2.text.lower() or "login" in r2.text.lower():
            print("✅ Page contains login/admin references")
        if "redirect" in r2.text.lower():
            print("⚠️  Page contains redirect code")
        
    except requests.exceptions.TooManyRedirects:
        print("❌ REDIRECT LOOP detected on /dashboard page!")
        print("💡 The /dashboard page is causing infinite redirects")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("Solution")
    print("=" * 60)
    print("If /dashboard causes redirect loop:")
    print("  1. Delete or rename the /dashboard page in WordPress")
    print("  2. Or fix the page template to not redirect")
    print("  3. Or change WordPress admin redirect settings")
    print()
    print("Alternative: Use wp-login.php directly:")
    print(f"  {url}/wp-login.php")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://freerideinvestor.com"
    check_dashboard(url)

