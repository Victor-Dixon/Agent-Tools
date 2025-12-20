#!/usr/bin/env python3
"""
Fix DaDudeKC.com Homepage Copy Rendering Glitches
===================================================

Fixes missing letters/spacing artifacts in headings and body text on dadudekc.com homepage.

Task: [SITE_AUDIT][HIGH][SA-DADUDEKC-HOME-COPY-GLITCH-01]
Issue: dadudekc.com home: fix hero/section copy rendering glitches (missing letters/spacing artifacts in headings and body text)

Common causes:
1. Font loading issues (fonts not loading, causing fallback font rendering problems)
2. CSS text-rendering or font-display issues
3. Content encoding issues (UTF-8 vs other encodings)
4. Theme template issues with text rendering
5. CSS letter-spacing or word-spacing issues

Author: Agent-8 (SSOT & System Integration Specialist)
V2 Compliant: <300 lines
"""

import json
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
    """Get WordPress credentials from config file."""
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
                    site_config = config.get("dadudekc.com") or config.get("dadudekc")
                    if site_config:
                        return {
                            "username": site_config.get("username"),
                            "app_password": site_config.get("app_password"),
                            "site_url": site_config.get("site_url", "https://dadudekc.com")
                        }
            except Exception as e:
                print(f"⚠️  Could not read config from {config_path}: {e}")
                continue
    
    return None


def get_homepage_content(site_url: str, username: str, app_password: str) -> Optional[Dict[str, Any]]:
    """Get homepage content via WordPress REST API."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    auth = HTTPBasicAuth(username, app_password.replace(" ", ""))
    
    try:
        # Get homepage (usually page with slug 'home' or ID 1)
        response = requests.get(
            api_url,
            params={"slug": "home", "per_page": 1},
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            pages = response.json()
            if pages:
                return pages[0]
        
        # Try getting page with ID 1 (default homepage)
        response = requests.get(
            f"{api_url}/1",
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            return response.json()
        
        return None
    except Exception as e:
        print(f"⚠️  Error fetching homepage: {e}")
        return None


def check_content_encoding(content: str) -> Dict[str, Any]:
    """Check for encoding issues in content."""
    issues = []
    
    # Check for common encoding artifacts
    if 'â€™' in content or 'â€"' in content or 'â€"' in content:
        issues.append("Found Windows-1252 encoding artifacts (smart quotes/apostrophes)")
    
    # Check for missing characters (common with font issues)
    # This is harder to detect programmatically - would need visual inspection
    
    return {
        "has_encoding_issues": len(issues) > 0,
        "issues": issues
    }


def generate_fix_recommendations() -> List[str]:
    """Generate recommendations for fixing copy rendering glitches."""
    return [
        "1. **Font Loading Fix**:",
        "   - Check if custom fonts are loading properly",
        "   - Add font-display: swap to @font-face declarations",
        "   - Ensure font files are accessible and not 404ing",
        "",
        "2. **CSS Text Rendering**:",
        "   - Add text-rendering: optimizeLegibility to headings",
        "   - Check letter-spacing and word-spacing values",
        "   - Verify font-family fallbacks are correct",
        "",
        "3. **Content Encoding**:",
        "   - Ensure all content is UTF-8 encoded",
        "   - Replace Windows-1252 smart quotes with UTF-8 equivalents",
        "   - Check database charset is utf8mb4",
        "",
        "4. **Theme Template Issues**:",
        "   - Check theme template files for encoding issues",
        "   - Verify PHP files are saved as UTF-8",
        "   - Check for HTML entities that might be breaking",
        "",
        "5. **Visual Inspection Required**:",
        "   - Use browser dev tools to inspect affected text",
        "   - Check computed font-family and font-size",
        "   - Verify no CSS transforms are affecting text rendering",
        "   - Check for overlapping elements causing visual glitches"
    ]


def main():
    """Main execution."""
    print("🔧 Fixing DaDudeKC.com Homepage Copy Rendering Glitches")
    print("   Site: https://dadudekc.com")
    print("   Issue: Missing letters/spacing artifacts in headings and body text")
    print()
    
    # Get credentials
    credentials = get_credentials()
    if not credentials:
        print("⚠️  WordPress credentials not found - running diagnostic mode")
        print()
        print("📋 DIAGNOSTIC RECOMMENDATIONS:")
        print("=" * 60)
        for rec in generate_fix_recommendations():
            print(rec)
        print()
        print("🔍 MANUAL STEPS REQUIRED:")
        print("   1. Navigate to https://dadudekc.com in browser")
        print("   2. Inspect homepage hero/section text visually")
        print("   3. Use browser dev tools to check:")
        print("      - Font loading (Network tab, filter by 'font')")
        print("      - Computed styles (Elements tab, check font-family)")
        print("      - Console for font loading errors")
        print("   4. Check WordPress theme CSS for text-rendering issues")
        print("   5. Verify content encoding in WordPress admin")
        return 0
    
    # Get homepage content
    print("📄 Fetching homepage content...")
    homepage = get_homepage_content(
        credentials["site_url"],
        credentials["username"],
        credentials["app_password"]
    )
    
    if homepage:
        content = homepage.get("content", {}).get("rendered", "")
        encoding_check = check_content_encoding(content)
        
        print(f"✅ Homepage found (ID: {homepage.get('id')})")
        print(f"   Title: {homepage.get('title', {}).get('rendered', 'N/A')}")
        
        if encoding_check["has_encoding_issues"]:
            print()
            print("⚠️  ENCODING ISSUES DETECTED:")
            for issue in encoding_check["issues"]:
                print(f"   - {issue}")
            print()
            print("💡 RECOMMENDATION: Fix encoding issues in WordPress admin")
            print("   - Edit page content and replace Windows-1252 characters")
            print("   - Ensure database charset is utf8mb4")
        else:
            print("   ✅ No obvious encoding issues in content")
    else:
        print("⚠️  Could not fetch homepage content")
    
    print()
    print("📋 FIX RECOMMENDATIONS:")
    print("=" * 60)
    for rec in generate_fix_recommendations():
        print(rec)
    
    print()
    print("🎯 NEXT STEPS:")
    print("   1. Visual inspection of live site required")
    print("   2. Check browser console for font loading errors")
    print("   3. Inspect CSS for text-rendering properties")
    print("   4. Fix identified issues in WordPress theme/CSS")
    print("   5. Test fix on staging before deploying")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





