#!/usr/bin/env python3
"""
Fix dadudekc.com Font Rendering Issue
=====================================

Fixes the missing letter 's' rendering issue by adding CSS with proper font fallbacks.
The issue is caused by a font that doesn't properly render the letter 's'.

Author: Auto
Date: 2025-12-17
V2 Compliant: Yes
"""

import sys
import json
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
    print("❌ requests library not available")
    sys.exit(1)

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30


def get_font_fix_css() -> str:
    """Generate CSS fix for font rendering issues."""
    return """
/* Font Rendering Fix for dadudekc.com - Fixes missing 's' character issue */
/* Applied: 2025-12-17 */

/* Override any problematic font-face declarations with proper fallbacks */
body,
body *,
.wp-block-post-content,
.wp-block-post-excerpt,
.wp-block-group,
.wp-block-cover,
h1, h2, h3, h4, h5, h6,
p, span, div, a, li, td, th {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol" !important;
}

/* Ensure all headings use safe fonts */
.wp-block-heading,
h1.wp-block-heading,
h2.wp-block-heading,
h3.wp-block-heading,
h4.wp-block-heading,
h5.wp-block-heading,
h6.wp-block-heading {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* Fix site title and navigation */
.wp-block-site-title,
.wp-block-site-title a,
.wp-block-navigation-item,
.wp-block-navigation-item__content {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* Fix footer text */
footer,
footer * {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* Ensure proper font rendering */
* {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}
"""


def deploy_php_fix_via_wp_manager(site_key: str = "dadudekc.com") -> bool:
    """
    Deploy PHP fix directly to functions.php using WordPress Manager and WP-CLI.

    This adds the CSS fix code directly to the theme's functions.php file.
    """
    try:
        from tools.wordpress_manager import WordPressManager

        print(
            f"🔧 Deploying font fix to functions.php via WordPress Manager for {site_key}...")
        manager = WordPressManager(site_key)

        # Read the PHP fix file to get the function code
        php_fix_path = project_root / "tools" / "dadudekc_font_fix_css.php"
        if not php_fix_path.exists():
            print(f"❌ PHP fix file not found: {php_fix_path}")
            return False

        php_content = php_fix_path.read_text(encoding='utf-8')
        # Extract just the function and add_action code (skip the opening PHP tag and comments)
        lines = php_content.split('\n')
        code_lines = []
        in_code = False
        for line in lines:
            if 'function dadudekc_font_rendering_fix()' in line:
                in_code = True
            if in_code:
                code_lines.append(line)

        php_code_to_add = '\n'.join(code_lines).strip()

        # Try to connect
        if not manager.connect():
            print("❌ Failed to connect to WordPress server")
            print(
                "   Please check your credentials in .deploy_credentials/sites.json or .env")
            return False

        # Deploy the PHP file to the theme directory first
        print("🔧 Deploying PHP fix file to theme...")

        # Deploy the PHP file to the theme
        remote_path = "dadudekc_font_fix_css.php"
        success = manager.deploy_file(
            php_fix_path, remote_path=remote_path, auto_flush_cache=True)

        if success:
            print(f"\n✅ PHP fix file deployed to theme directory!")

            # Try to add require statement to functions.php via WP-CLI
            print("\n🔧 Attempting to add require statement to functions.php...")
            require_line = "require_once get_template_directory() . '/dadudekc_font_fix_css.php';"

            # Use WP-CLI eval to append to functions.php if the line doesn't exist
            wp_eval_cmd = (
                f'eval "'
                f'\\$func_path = get_template_directory() . \\"/functions.php\\"; '
                f'\\$content = file_exists(\\$func_path) ? file_get_contents(\\$func_path) : \\"<?php\\\\n\\"; '
                f'if (strpos(\\$content, \\"dadudekc_font_fix_css\\") === false) {{ '
                f'  file_put_contents(\\$func_path, \\$content . PHP_EOL . \\"// Font fix - 2025-12-17\\\\n{require_line}\\\\n\\", FILE_APPEND | LOCK_EX); '
                f'  echo \\"SUCCESS\\"; '
                f'}} else {{ echo \\"EXISTS\\"; }}"'
            )

            stdout, stderr, code = manager.wp_cli(wp_eval_cmd)

            if code == 0 and "SUCCESS" in stdout:
                print(f"✅ Successfully added require statement to functions.php!")
                print(f"   Cache flushed automatically")
            elif "EXISTS" in stdout:
                print(f"ℹ️  Require statement already exists in functions.php")
            else:
                print(f"⚠️  Could not automatically add to functions.php")
                print(f"   Output: {stdout}")
                print(f"   Error: {stderr}")
                print(
                    f"\n📋 Please manually add this line to your theme's functions.php:")
                print(f"   {require_line}")
        else:
            print("❌ Failed to deploy PHP fix file")
            return False

        return success

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_css_via_wp_cli(site_key: str = "dadudekc.com") -> bool:
    """
    Add CSS fix via WP-CLI using WordPress Manager.

    This attempts to deploy a PHP file that adds the CSS fix.
    """
    return deploy_php_fix_via_wp_manager(site_key)


def add_css_via_rest_api(site_url: str, username: str, app_password: str) -> bool:
    """
    Attempt to add CSS via WordPress REST API.

    Note: WordPress doesn't have a direct REST API endpoint for Additional CSS,
    so this would need to be done via a custom endpoint or by modifying theme files.
    """
    css_content = get_font_fix_css()

    # WordPress doesn't have a direct REST API for Additional CSS
    # We would need to either:
    # 1. Use a plugin that exposes an API
    # 2. Modify theme files directly via SFTP
    # 3. Use browser automation to access Customizer

    print("⚠️  WordPress REST API doesn't support Additional CSS directly")
    print("   Please use one of these methods:")
    print("   1. WordPress Admin → Appearance → Additional CSS")
    print("   2. Deploy CSS file to theme directory")
    print("   3. Use browser automation (not implemented here)")

    return False


def create_child_theme_css() -> bool:
    """
    Create a child theme CSS file that can be deployed.

    This creates a style.css for a child theme that includes the font fix.
    """
    css_content = get_font_fix_css()

    # Create child theme directory structure
    child_theme_dir = project_root / "temp_dadudekc_child_theme"
    child_theme_dir.mkdir(exist_ok=True)

    style_css_path = child_theme_dir / "style.css"

    # Create child theme style.css header
    child_theme_header = """/*
Theme Name: Accounting Grove Dark Child
Template: accounting-grove-dark
Version: 1.0.0
Description: Child theme for Accounting Grove Dark with font rendering fixes
*/
"""

    full_css = child_theme_header + "\n" + css_content
    style_css_path.write_text(full_css, encoding='utf-8')

    print(f"✅ Created child theme CSS file: {style_css_path}")
    print("   You can deploy this as a child theme or copy the CSS to Additional CSS")

    return True


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix dadudekc.com font rendering issue (missing 's' character)"
    )
    parser.add_argument(
        '--method',
        choices=['wp-cli', 'child-theme', 'output-only'],
        default='output-only',
        help='Method to apply the fix'
    )
    parser.add_argument(
        '--site',
        default='dadudekc.com',
        help='Site key for WordPress Manager'
    )

    args = parser.parse_args()

    print("🔧 Fixing dadudekc.com font rendering issue...")
    print("   Issue: Missing letter 's' in text rendering")
    print("   Cause: Font subsetting or font loading issue")
    print("   Fix: Add CSS with proper font fallbacks\n")

    success = False

    if args.method == 'wp-cli':
        success = add_css_via_wp_cli(args.site)
    elif args.method == 'child-theme':
        success = create_child_theme_css()
    else:  # output-only
        css_content = get_font_fix_css()
        print("="*70)
        print("CSS FIX CONTENT")
        print("="*70)
        print("Copy the CSS below to WordPress Admin → Appearance → Additional CSS")
        print("="*70)
        print(css_content)
        print("="*70)
        success = True

    if success:
        print("\n✅ Font fix CSS generated successfully!")
        print("\n📋 Next steps:")
        print("   1. Log in to WordPress Admin: https://dadudekc.com/wp-admin")
        print("   2. Go to Appearance → Additional CSS")
        print("   3. Paste the CSS fix content")
        print("   4. Click 'Publish'")
        print("   5. Clear cache and refresh the site")
    else:
        print("\n❌ Failed to generate/apply font fix")
        sys.exit(1)


if __name__ == '__main__':
    main()

