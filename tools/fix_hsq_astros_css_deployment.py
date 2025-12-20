#!/usr/bin/env python3
"""
Fix Houston Sip Queen Astros CSS Deployment
===========================================
Deploys CSS to the correct theme directory by finding where it actually should be

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


def get_astros_css_content() -> str:
    """Get Astros theme CSS content."""
    # Import from the apply script
    import importlib.util
    apply_script = project_root / "tools" / "apply_hsq_astros_theme.py"
    spec = importlib.util.spec_from_file_location(
        "apply_hsq_astros_theme", apply_script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_astros_theme_css()


def find_actual_theme_directory(manager: WordPressManager) -> str:
    """Find the actual theme directory path."""
    # Use WP-CLI to get theme path
    stdout, stderr, code = manager.wp_cli(
        "eval 'echo get_template_directory();' --allow-root")

    if code == 0 and stdout:
        theme_dir = stdout.strip()
        # Extract just the theme directory name from full path
        if '/themes/' in theme_dir:
            theme_name = theme_dir.split('/themes/')[-1]
            return theme_name
        return theme_dir

    # Fallback: check common locations
    base_paths = [
        "domains/houstonsipqueen.com/public_html/wp-content/themes",
    ]

    theme_name = "twentytwentyfive"

    for base in base_paths:
        theme_path = f"{base}/{theme_name}"
        try:
            manager.conn_manager.sftp.stat(f"{theme_path}/style.css")
            return theme_path
        except:
            continue

    return None


def main():
    """Fix CSS deployment to correct location."""
    print("=" * 60)
    print("🔧 Fix Houston Sip Queen Astros CSS Deployment")
    print("=" * 60)
    print()

    manager = WordPressManager("houstonsipqueen.com")

    if not manager.connect():
        print("❌ Failed to connect")
        return 1

    print("✅ Connected")
    print()

    # Get actual theme directory
    print("🔍 Finding actual theme directory...")
    theme_path = find_actual_theme_directory(manager)

    if not theme_path:
        print("❌ Could not find theme directory")
        manager.disconnect()
        return 1

    print(f"✅ Found theme directory: {theme_path}")
    print()

    # Get CSS content
    css_content = get_astros_css_content()

    # Create PHP file with CSS
    css_filename = "hsq_astros_theme_css.php"
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

    # Deploy CSS file
    css_file_path = f"{theme_path}/{css_filename}"
    print(f"📤 Deploying {css_filename}...")

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(php_code)

    success = manager.conn_manager.upload_file(tmp_path, css_file_path)
    tmp_path.unlink()

    if not success:
        print(f"❌ Failed to deploy CSS file")
        manager.disconnect()
        return 1

    print(f"✅ Deployed {css_filename}")
    print()

    # Update functions.php
    func_path = f"{theme_path}/functions.php"
    print("📝 Updating functions.php...")

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
        tmp_func_path = Path(tmp_file.name)

    try:
        manager.conn_manager.sftp.get(func_path, str(tmp_func_path))
        content = tmp_func_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        content = "<?php\n"
        print("   ℹ️  functions.php not found, creating new file")

    if css_filename not in content:
        content = content.rstrip()
        content += f"\n\n// Houston Sip Queen Astros Brand Theme CSS - Applied 2025-12-18\n"
        content += f"require_once get_template_directory() . '/{css_filename}';\n"
        tmp_func_path.write_text(content, encoding='utf-8')

        manager.conn_manager.sftp.put(str(tmp_func_path), func_path)
        print(f"   ✅ Updated functions.php with {css_filename} include")
        tmp_func_path.unlink()
    else:
        print(f"   ℹ️  {css_filename} already included in functions.php")
        tmp_func_path.unlink()

    # Flush cache
    print()
    print("🔄 Flushing cache...")
    manager.purge_caches()

    manager.disconnect()

    print()
    print("✅ CSS deployed to correct location!")
    print(f"   Path: {theme_path}/{css_filename}")
    print()
    print("💡 Refresh the site to see Astros colors")

    return 0


if __name__ == "__main__":
    sys.exit(main())

