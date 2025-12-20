#!/usr/bin/env python3
"""
Apply Houston Sip Queen Astros Color Theme
==========================================
Applies Astros colors (navy blue and orange) to houstonsipqueen.com theme

Author: Agent-5
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


def get_astros_theme_css() -> str:
    """Generate Astros color theme CSS for Houston Sip Queen."""
    return """
/* Houston Sip Queen - Astros Brand Colors Theme */
/* Colors: Astros Navy Blue (#002D62) and Orange (#EB6E1F) */
/* Applied: 2025-12-18 */

/* Astros Color Palette */
:root {
    --astros-navy: #002D62;
    --astros-navy-dark: #001A3D;
    --astros-orange: #EB6E1F;
    --astros-orange-light: #FF8C42;
    --astros-white: #FFFFFF;
    --astros-light-gray: #F5F5F5;
}

/* Typography */
body, 
body * {
    font-family: 'Inter', 'Montserrat', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

h1, h2, h3, h4, h5, h6,
.wp-block-heading {
    font-family: 'Playfair Display', 'Cinzel', Georgia, serif !important;
    font-weight: 700;
    color: var(--astros-navy) !important;
}

/* Buttons - Astros Orange with Navy text or Navy with Orange accent */
.wp-block-button__link,
.wp-element-button,
button,
input[type="submit"],
a.button {
    border-radius: 50px !important;
    background-color: var(--astros-orange) !important;
    color: var(--astros-white) !important;
    border: 2px solid var(--astros-orange) !important;
    padding: 12px 30px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
}

.wp-block-button__link:hover,
.wp-element-button:hover,
button:hover,
input[type="submit"]:hover,
a.button:hover {
    background-color: var(--astros-navy) !important;
    border-color: var(--astros-navy) !important;
    color: var(--astros-white) !important;
    transform: translateY(-2px) !important;
}

/* Primary Navigation - Astros Navy */
.main-navigation,
nav,
.wp-block-navigation {
    background-color: var(--astros-navy) !important;
}

.main-navigation a,
nav a,
.wp-block-navigation a {
    color: var(--astros-white) !important;
}

.main-navigation a:hover,
nav a:hover,
.wp-block-navigation a:hover {
    color: var(--astros-orange) !important;
}

/* Site Header Background */
.site-header,
header {
    background-color: var(--astros-navy) !important;
    color: var(--astros-white) !important;
}

/* Accent Colors */
a {
    color: var(--astros-orange) !important;
}

a:hover {
    color: var(--astros-navy) !important;
}

/* Background Sections - Alternating */
.has-astros-navy-background-color,
.wp-block-group.has-background {
    background-color: var(--astros-navy) !important;
    color: var(--astros-white) !important;
}

.has-astros-orange-background-color {
    background-color: var(--astros-orange) !important;
    color: var(--astros-white) !important;
}

/* Text Colors */
.has-astros-navy-color {
    color: var(--astros-navy) !important;
}

.has-astros-orange-color {
    color: var(--astros-orange) !important;
}

/* Footer - Astros Navy */
.site-footer,
footer {
    background-color: var(--astros-navy-dark) !important;
    color: var(--astros-white) !important;
}

.site-footer a,
footer a {
    color: var(--astros-orange) !important;
}

.site-footer a:hover,
footer a:hover {
    color: var(--astros-orange-light) !important;
}

/* Cards and Content Blocks */
.wp-block-group,
.wp-block-columns {
    border-left: 4px solid var(--astros-orange) !important;
    padding-left: 20px !important;
}

/* Borders and Dividers */
hr,
.wp-block-separator {
    border-color: var(--astros-orange) !important;
    border-width: 2px !important;
}

/* Form Elements */
input[type="text"],
input[type="email"],
input[type="tel"],
textarea,
select {
    border: 2px solid var(--astros-navy) !important;
    border-radius: 8px !important;
    padding: 10px 15px !important;
}

input[type="text"]:focus,
input[type="email"]:focus,
input[type="tel"]:focus,
textarea:focus,
select:focus {
    border-color: var(--astros-orange) !important;
    outline: 2px solid var(--astros-orange-light) !important;
    outline-offset: 2px !important;
}
"""


def main():
    """Apply Astros theme CSS to Houston Sip Queen."""
    print("=" * 60)
    print("⚾ Houston Sip Queen - Astros Brand Theme")
    print("=" * 60)
    print()

    # Try common site keys for houstonsipqueen
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

    # Get remote base path for twentytwentyfive theme
    remote_base = manager.config.get("remote_base", "")
    if not remote_base:
        remote_base = "domains/houstonsipqueen.com/public_html/wp-content/themes/twentytwentyfive"

    print("🎨 Applying Astros brand colors (Navy Blue & Orange)...")
    print()

    # Get CSS content
    css_content = get_astros_theme_css()

    # Create PHP file with CSS
    php_code = f"""<?php
/**
 * Houston Sip Queen - Astros Brand Theme CSS
 * Colors: Astros Navy Blue (#002D62) and Orange (#EB6E1F)
 * Applied: 2025-12-18
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
add_action('wp_head', 'hsq_astros_theme_styles', 100);
"""

    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write(php_code)

        # Deploy CSS file
        css_filename = "hsq_astros_theme_css.php"
        remote_css_path = f"{remote_base}/{css_filename}"

        print(f"📤 Deploying {css_filename}...")
        success = manager.conn_manager.upload_file(tmp_path, remote_css_path)

        # Clean up temp file
        tmp_path.unlink()

        if not success:
            print("❌ Failed to deploy CSS file")
            manager.disconnect()
            return 1

        print(f"✅ Deployed {css_filename}")
        print()

        # Update functions.php to require the CSS file
        func_path = f"{remote_base}/functions.php"

        print("📝 Updating functions.php...")
        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
                tmp_func_path = Path(tmp_file.name)

            # Download existing functions.php
            try:
                manager.conn_manager.sftp.get(func_path, str(tmp_func_path))
                content = tmp_func_path.read_text(encoding='utf-8')
            except FileNotFoundError:
                content = "<?php\n"
                print("   ℹ️  functions.php not found, creating new file")

            # Check if already included
            if css_filename in content:
                print(
                    f"   ℹ️  {css_filename} already included in functions.php")
            else:
                content = content.rstrip()
                content += f"\n\n// Houston Sip Queen Astros Brand Theme CSS - Applied 2025-12-18\n"
                content += f"require_once get_template_directory() . '/{css_filename}';\n"
                tmp_func_path.write_text(content, encoding='utf-8')

                # Upload updated functions.php
                manager.conn_manager.sftp.put(str(tmp_func_path), func_path)
                print(
                    f"   ✅ Updated functions.php with {css_filename} include")
                tmp_func_path.unlink()

        except Exception as e:
            print(f"   ⚠️  Warning: Could not update functions.php: {e}")
            print(
                f"   💡 Manually add: require_once get_template_directory() . '/{css_filename}';")

        # Flush cache
        print()
        print("🔄 Flushing cache...")
        manager.purge_caches()

        manager.disconnect()

        print()
        print("✅ Astros brand theme applied successfully!")
        print()
        print("🎨 Astros brand colors:")
        print("   - Navy Blue (#002D62) - Primary")
        print("   - Orange (#EB6E1F) - Accent")
        print()
        print("💡 Refresh your site to see the changes")
        return 0

    except Exception as e:
        print(f"❌ Error applying theme: {e}")
        import traceback
        traceback.print_exc()
        if manager:
            manager.disconnect()
        return 1


if __name__ == "__main__":
    sys.exit(main())

