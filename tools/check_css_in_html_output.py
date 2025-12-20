#!/usr/bin/env python3
"""
Check if Astros CSS is Actually Output in HTML
==============================================
Checks the actual HTML output to see if CSS is being loaded

Author: Agent-5
Date: 2025-12-18
"""

import sys
import requests
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30


def check_css_in_html(url: str = "https://houstonsipqueen.com/home/"):
    """Check if Astros CSS is in the HTML output."""
    print("=" * 60)
    print("🔍 Checking CSS in HTML Output")
    print("=" * 60)
    print()
    print(f"Fetching: {url}")
    print()

    try:
        response = requests.get(url, timeout=TimeoutConstants.HTTP_DEFAULT)
        html = response.text

        # Check for CSS markers
        has_astros_navy = "--astros-navy" in html
        has_astros_orange = "--astros-orange" in html
        has_style_tag = "hsq-astros-theme-styles" in html
        has_function = "hsq_astros_theme_styles" in html

        print("📊 CSS Check Results:")
        print()
        print(f"   Contains --astros-navy: {has_astros_navy}")
        print(f"   Contains --astros-orange: {has_astros_orange}")
        print(
            f"   Contains style tag ID 'hsq-astros-theme-styles': {has_style_tag}")
        print(f"   Contains function name: {has_function}")
        print()

        if has_astros_navy and has_astros_orange:
            print("✅ Astros CSS is present in HTML output!")
            print()
            print("💡 If colors still don't appear:")
            print("   1. Check browser console for CSS errors")
            print("   2. Check if other CSS is overriding with higher specificity")
            print("   3. Check if CSS is being loaded after page render")
            return True
        else:
            print("❌ Astros CSS is NOT in HTML output")
            print()
            print("💡 This means the CSS function is not being called.")
            print("   Possible causes:")
            print("   1. functions.php is not loading the CSS file")
            print("   2. CSS file has a PHP error preventing execution")
            print("   3. CSS file is in the wrong theme directory")
            print("   4. WordPress is using a different functions.php")

            # Show what's actually in the head
            if "<head" in html:
                head_start = html.find("<head")
                head_end = html.find("</head>") + 7
                head_content = html[head_start:head_end]

                if "style" in head_content.lower():
                    print()
                    print("📝 Found style tags in head, checking content...")
                    # Count style tags
                    style_count = head_content.lower().count("<style")
                    print(f"   Found {style_count} <style> tag(s) in <head>")
                else:
                    print()
                    print("   ⚠️  No <style> tags found in <head>")

            return False

    except Exception as e:
        print(f"❌ Error fetching page: {e}")
        return False


if __name__ == "__main__":
    success = check_css_in_html()
    sys.exit(0 if success else 1)

