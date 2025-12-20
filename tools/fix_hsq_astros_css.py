#!/usr/bin/env python3
"""
Fix Houston Sip Queen Astros CSS - Use Direct Colors
====================================================
Updates the CSS to use direct color values instead of CSS variables
for better compatibility and to ensure colors actually show.

Author: Agent-6
Date: 2025-12-18
"""

import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.wordpress_manager import WordPressManager
except ImportError:
    print("❌ WordPress Manager not available")
    sys.exit(1)


def get_fixed_astros_css() -> str:
    """Generate Astros color theme CSS with direct color values."""
    return """
/* Houston Sip Queen - Astros Brand Colors Theme */
/* Colors: Astros Navy Blue (#002D62) and Orange (#EB6E1F) */
/* Applied: 2025-12-18 - Fixed with direct color values */

/* Astros Color Palette - Direct Values */
:root {
    --astros-navy: #002D62;
    --astros-navy-dark: #001A3D;
    --astros-orange: #EB6E1F;
    --astros-orange-light: #FF8C42;
    --astros-white: #FFFFFF;
    --astros-light-gray: #F5F5F5;
}

/* Buttons - Direct Orange Color */
.wp-block-button__link,
.wp-element-button,
button:not(.wp-block-search__button),
input[type="submit"],
input[type="button"],
a.button,
.wp-block-button a,
.elementor-button,
.btn {
    border-radius: 50px !important;
    background-color: #EB6E1F !important;
    background: #EB6E1F !important;
    color: #FFFFFF !important;
    border: 2px solid #EB6E1F !important;
    padding: 12px 30px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
}

.wp-block-button__link:hover,
.wp-element-button:hover,
button:hover:not(.wp-block-search__button),
input[type="submit"]:hover,
input[type="button"]:hover,
a.button:hover,
.wp-block-button a:hover,
.elementor-button:hover,
.btn:hover {
    background-color: #002D62 !important;
    background: #002D62 !important;
    border-color: #002D62 !important;
    color: #FFFFFF !important;
    transform: translateY(-2px) !important;
}

/* Primary Navigation - Direct Navy Color */
.main-navigation,
nav:not(.wp-block-navigation__responsive-container-open),
.wp-block-navigation,
.site-navigation,
header nav,
.wp-block-navigation__responsive-container {
    background-color: #002D62 !important;
    background: #002D62 !important;
}

.main-navigation a,
nav a:not(.wp-block-navigation__responsive-container-close),
.wp-block-navigation a,
.site-navigation a,
header nav a {
    color: #FFFFFF !important;
}

.main-navigation a:hover,
nav a:hover:not(.wp-block-navigation__responsive-container-close),
.wp-block-navigation a:hover,
.site-navigation a:hover,
header nav a:hover {
    color: #EB6E1F !important;
}

/* Site Header Background - Direct Navy */
.site-header,
header:not(.wp-block-template-part),
.wp-site-blocks > header {
    background-color: #002D62 !important;
    background: #002D62 !important;
    color: #FFFFFF !important;
}

/* Links - Direct Orange Color */
a:not(.wp-block-button__link):not(.wp-element-button):not(button):not(.button) {
    color: #EB6E1F !important;
}

a:hover:not(.wp-block-button__link):not(.wp-element-button):not(button):not(.button) {
    color: #002D62 !important;
}

/* Headings - Direct Navy Color */
h1, h2, h3, h4, h5, h6,
.wp-block-heading,
.wp-block-post-title,
.entry-title,
.site-title {
    color: #002D62 !important;
}

/* Background Sections */
.has-astros-navy-background-color,
.wp-block-group.has-background[class*="background"],
section[class*="background"] {
    background-color: #002D62 !important;
    background: #002D62 !important;
    color: #FFFFFF !important;
}

.has-astros-orange-background-color {
    background-color: #EB6E1F !important;
    background: #EB6E1F !important;
    color: #FFFFFF !important;
}

/* Text Colors */
.has-astros-navy-color,
.text-navy {
    color: #002D62 !important;
}

.has-astros-orange-color,
.text-orange {
    color: #EB6E1F !important;
}

/* Override any inline styles or theme defaults */
* {
    --wp--preset--color--primary: #002D62 !important;
    --wp--preset--color--secondary: #EB6E1F !important;
}

/* Force colors on common WordPress/Block Editor elements */
.wp-block-button.is-style-outline .wp-block-button__link {
    border-color: #EB6E1F !important;
    color: #EB6E1F !important;
    background: transparent !important;
}

.wp-block-button.is-style-outline .wp-block-button__link:hover {
    background-color: #EB6E1F !important;
    color: #FFFFFF !important;
}
"""


def main():
    """Main entry point."""
    print("=" * 60)
    print("🔧 Fix Houston Sip Queen Astros CSS")
    print("=" * 60)
    print()

    # Try common site keys
    site_keys = ["houstonsipqueen", "houstonsipqueen.com", "hsq"]

    manager = None
    site_key = None

    for key in site_keys:
        try:
            manager = WordPressManager(key)
            if manager.config:
                site_key = key
                print(f"✅ Found site configuration: {key}")
                break
        except Exception as e:
            continue

    if not manager or not manager.config:
        print("❌ Could not find site configuration for houstonsipqueen")
        return 1

    print(f"Site: {site_key}")
    print()

    if not manager.connect():
        print("❌ Failed to connect to server")
        return 1

    print("✅ Connected to server")
    print()

    # Get remote base path
    remote_base = manager.config.get("remote_base", "")
    if not remote_base:
        remote_base = "domains/houstonsipqueen.com/public_html/wp-content/themes/houstonsipqueen"

    print("🔧 Fixing Astros CSS with direct color values...")
    print()

    # Get fixed CSS content
    css_content = get_fixed_astros_css()

    # Create PHP file with CSS
    php_code = f"""<?php
/**
 * Houston Sip Queen - Astros Brand Theme CSS (FIXED)
 * Colors: Astros Navy Blue (#002D62) and Orange (#EB6E1F)
 * Applied: 2025-12-18
 * Fixed: 2025-12-18 - Using direct color values for better compatibility
 */

if (!defined('ABSPATH')) {{
    exit;
}}

function hsq_astros_theme_styles() {{
    ?>
    <style id="hsq-astros-theme-styles">
{css_content}
    </style>
    <?php
}}
add_action('wp_head', 'hsq_astros_theme_styles', 999);
"""

    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write(php_code)

        # Deploy CSS file
        css_filename = "hsq_astros_theme_css.php"
        remote_css_path = f"{remote_base}/{css_filename}"

        print(f"📤 Deploying fixed {css_filename}...")
        success = manager.conn_manager.upload_file(tmp_path, remote_css_path)

        # Clean up temp file
        tmp_path.unlink()

        if not success:
            print("❌ Failed to deploy CSS file")
            manager.disconnect()
            return 1

        print(f"✅ Deployed fixed {css_filename}")
        print("   - Using direct color values (#002D62, #EB6E1F)")
        print("   - Higher priority (999) for wp_head action")
        print("   - More comprehensive selectors")
        print()

        # Flush cache
        print("🔄 Flushing cache...")
        manager.purge_caches()

        manager.disconnect()

        print()
        print("✅ Astros CSS fixed and deployed!")
        print()
        print("🎨 Changes:")
        print("   - Direct color values instead of CSS variables")
        print("   - Higher priority (999) to override other styles")
        print("   - More comprehensive selectors")
        print()
        print("💡 Hard refresh your browser (Ctrl+F5) to see changes")
        return 0

    except Exception as e:
        print(f"❌ Error fixing CSS: {e}")
        import traceback
        traceback.print_exc()
        if manager:
            manager.disconnect()
        return 1


if __name__ == "__main__":
    sys.exit(main())

