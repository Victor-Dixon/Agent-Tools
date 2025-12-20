#!/usr/bin/env python3
"""
Check and Apply Houston Sip Queen Baby Blue Theme
==================================================

Checks current theme status and applies baby blue theme styling.

Author: Agent-2
Date: 2025-12-18
V2 Compliant: Yes
"""

from tools.wordpress_manager import WordPressManager
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def get_baby_blue_theme_css() -> str:
    """Generate baby blue theme CSS for Houston Sip Queen."""
    return """
/* Houston Sip Queen - Baby Blue Theme */
/* Applied: 2025-12-18 */

/* Baby Blue Color Palette */
:root {
    --hsq-baby-blue: #87CEEB;
    --hsq-sky-blue: #B0E0E6;
    --hsq-powder-blue: #B6E5D8;
    --hsq-navy: #1E3A5F;
    --hsq-white: #FFFFFF;
    --hsq-light-gray: #F5F5F5;
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
    color: var(--hsq-navy) !important;
}

/* Buttons - Baby Blue with rounded corners */
.wp-block-button__link,
.wp-element-button,
button,
input[type="submit"],
a.button {
    border-radius: 50px !important;
    background-color: var(--hsq-baby-blue) !important;
    color: var(--hsq-navy) !important;
    padding: 12px 32px !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

.wp-block-button__link:hover,
.wp-element-button:hover,
button:hover,
input[type="submit"]:hover,
a.button:hover {
    background-color: var(--hsq-navy) !important;
    color: var(--hsq-white) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
}

/* Hero Section - Baby Blue Gradient */
.wp-block-cover,
.hero-section {
    background: linear-gradient(135deg, var(--hsq-baby-blue) 0%, var(--hsq-sky-blue) 100%) !important;
    color: var(--hsq-navy) !important;
    min-height: 60vh !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Section Styling */
.wp-block-group,
section {
    padding: 60px 20px !important;
    background-color: var(--hsq-white) !important;
}

/* Body Background */
body {
    background-color: var(--hsq-light-gray) !important;
    color: var(--hsq-navy) !important;
}

p, li, span {
    color: var(--hsq-navy) !important;
    line-height: 1.7 !important;
}

/* Links - Baby Blue */
a {
    color: var(--hsq-baby-blue) !important;
    text-decoration: none !important;
    transition: color 0.3s ease !important;
}

a:hover {
    color: var(--hsq-navy) !important;
}

/* Mobile-First Responsive */
@media (max-width: 768px) {
    .wp-block-cover,
    .hero-section {
        min-height: 50vh !important;
        padding: 40px 20px !important;
    }
    
    h1 {
        font-size: 2rem !important;
    }
    
    h2 {
        font-size: 1.75rem !important;
    }
}

/* Navigation - Baby Blue Accent */
.wp-block-navigation,
nav {
    background-color: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px);
    border-bottom: 2px solid var(--hsq-baby-blue) !important;
}

.wp-block-navigation-item__content,
nav a {
    color: var(--hsq-navy) !important;
}

.wp-block-navigation-item__content:hover,
nav a:hover {
    color: var(--hsq-baby-blue) !important;
}

/* Footer - Baby Blue Background */
footer,
.wp-block-template-part[data-area="footer"] {
    background-color: var(--hsq-baby-blue) !important;
    color: var(--hsq-navy) !important;
    padding: 40px 20px !important;
}

footer a,
footer .wp-block-navigation-item__content {
    color: var(--hsq-navy) !important;
}

footer a:hover {
    color: var(--hsq-white) !important;
}
"""


def check_theme_status(manager: WordPressManager) -> dict:
    """Check current theme status."""
    print("🔍 Checking theme status...")

    # List themes
    themes = manager.list_themes()
    active_theme = None

    for theme in themes:
        if theme.get('status') == 'active':
            active_theme = theme
            break

    # Check if CSS file exists
    remote_base = manager.config.get("remote_base", "")
    if not remote_base:
        remote_base = "domains/houstonsipqueen.com/public_html/wp-content/themes/houstonsipqueen"

    css_file = f"{remote_base}/hsq_theme_css.php"
    css_exists = False

    try:
        manager.conn_manager.sftp.stat(css_file)
        css_exists = True
    except:
        css_exists = False

    return {
        "active_theme": active_theme,
        "all_themes": themes,
        "css_exists": css_exists,
        "css_path": css_file
    }


def apply_baby_blue_theme(manager: WordPressManager) -> bool:
    """Apply baby blue theme CSS."""
    print("🎨 Applying baby blue theme...")

    remote_base = manager.config.get("remote_base", "")
    if not remote_base:
        remote_base = "domains/houstonsipqueen.com/public_html/wp-content/themes/houstonsipqueen"

    css_content = get_baby_blue_theme_css()
    php_code = f"""<?php
/**
 * Houston Sip Queen Baby Blue Theme CSS
 * Applied: 2025-12-18
 */

if (!defined('ABSPATH')) {{
    exit;
}}

function hsq_baby_blue_theme_css() {{
    ?>
    <style id="hsq-baby-blue-theme">
    {css_content}
    </style>
    <?php
}}
add_action('wp_head', 'hsq_baby_blue_theme_css', 999);
"""

    # Deploy CSS file using WordPressManager's deploy_file method
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_path.write_text(php_code, encoding='utf-8')

    try:
        # Use manager's deploy_file which handles directory creation
        success = manager.deploy_file(
            tmp_path,
            remote_path="hsq_baby_blue_theme.php",
            auto_flush_cache=False
        )

        if success:
            print(f"   ✅ Deployed baby blue theme CSS")
        else:
            print(f"   ❌ Failed to deploy CSS")
            tmp_path.unlink()
            return False

        tmp_path.unlink()
    except Exception as e:
        print(f"   ❌ Failed to deploy CSS: {e}")
        import traceback
        traceback.print_exc()
        if tmp_path.exists():
            tmp_path.unlink()
        return False

    # Create/Update functions.php to include the CSS
    func_content = """<?php
/**
 * Houston Sip Queen Theme Functions
 */

if (!defined('ABSPATH')) {
    exit;
}

// Houston Sip Queen Baby Blue Theme - Applied 2025-12-18
require_once get_template_directory() . '/hsq_baby_blue_theme.php';
"""

    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
            tmp_func = Path(tmp_file.name)
            tmp_func.write_text(func_content, encoding='utf-8')

        # Try to get existing functions.php first
        func_path = f"{remote_base}/functions.php"
        try:
            manager.conn_manager.sftp.get(func_path, str(tmp_func))
            existing_content = tmp_func.read_text(encoding='utf-8')

            # Check if already included
            if 'hsq_baby_blue_theme.php' in existing_content:
                print("   ℹ️  Baby blue theme already included in functions.php")
                tmp_func.unlink()
            else:
                # Remove old theme includes if present
                existing_content = existing_content.replace(
                    'require_once get_template_directory() . \'/hsq_theme_css.php\';', '')
                existing_content = existing_content.replace(
                    'require_once get_template_directory() . "/hsq_theme_css.php";', '')

                # Add new include
                existing_content = existing_content.rstrip()
                existing_content += "\n\n// Houston Sip Queen Baby Blue Theme - Applied 2025-12-18\n"
                existing_content += "require_once get_template_directory() . '/hsq_baby_blue_theme.php';\n"

                tmp_func.write_text(existing_content, encoding='utf-8')
                manager.deploy_file(
                    tmp_func, remote_path="functions.php", auto_flush_cache=False)
                print(f"   ✅ Updated functions.php to include baby blue theme")
                tmp_func.unlink()
        except FileNotFoundError:
            # Create new functions.php
            manager.deploy_file(
                tmp_func, remote_path="functions.php", auto_flush_cache=False)
            print(f"   ✅ Created functions.php with baby blue theme")
            tmp_func.unlink()
    except Exception as e:
        print(f"   ⚠️  Could not update functions.php: {e}")
        print(f"   Note: You may need to manually add: require_once get_template_directory() . '/hsq_baby_blue_theme.php';")

    return True


def main():
    """Main execution."""
    print("🍸 Houston Sip Queen - Baby Blue Theme Check & Apply")
    print("=" * 60)
    print()

    manager = WordPressManager("houstonsipqueen.com")

    if not manager.connect():
        print("❌ Failed to connect to WordPress")
        return 1

    # Check current status
    status = check_theme_status(manager)

    print(
        f"Active Theme: {status['active_theme'].get('name', 'Unknown') if status['active_theme'] else 'None'}")
    print(f"CSS File Exists: {'✅ Yes' if status['css_exists'] else '❌ No'}")
    print()

    # Apply baby blue theme
    if apply_baby_blue_theme(manager):
        print("\n✅ Baby blue theme applied successfully!")
    else:
        print("\n❌ Failed to apply baby blue theme")
        manager.disconnect()
        return 1

    # Flush cache
    print("\n🔄 Flushing cache...")
    manager.purge_caches()

    manager.disconnect()

    print("\n✅ Complete! Baby blue theme is now active.")
    print("   Refresh your site to see the changes.")

    return 0


if __name__ == '__main__':
    sys.exit(main())



