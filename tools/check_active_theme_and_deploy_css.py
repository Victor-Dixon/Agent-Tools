#!/usr/bin/env python3
"""
Check Active Theme and Deploy CSS to Correct Directory
======================================================
Checks what theme is actually active and deploys CSS to that theme's directory

Author: Agent-5
Date: 2025-12-18
"""

import sys
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


def main():
    """Check active theme and deploy CSS correctly."""
    print("=" * 60)
    print("🔍 Check Active Theme & Deploy CSS")
    print("=" * 60)
    print()

    # Get manager
    manager = WordPressManager("houstonsipqueen.com")

    if not manager.connect():
        print("❌ Failed to connect")
        return 1

    print("✅ Connected")
    print()

    # List themes to find active one
    print("📋 Checking active theme...")
    themes = manager.list_themes()

    active_theme = None
    for theme in themes:
        if theme.get('status') == 'active':
            active_theme = theme
            break

    if not active_theme:
        print("❌ Could not find active theme")
        manager.disconnect()
        return 1

    theme_name = active_theme.get('name', '')
    theme_slug = active_theme.get('name', '').lower().replace(' ', '-')

    print(f"✅ Active theme: {theme_name} (slug: {theme_slug})")
    print()

    # Determine base path - get from config or use default
    remote_base = manager.config.get("remote_base", "")
    if not remote_base:
        # Use default path structure
        remote_base = "domains/houstonsipqueen.com/public_html/wp-content/themes"
    else:
        # If remote_base is set to a theme directory, get parent
        if '/themes/' in remote_base:
            remote_base = remote_base.rsplit(
                '/themes/', 1)[0] + '/wp-content/themes'
        elif '/wp-content/themes' not in remote_base:
            remote_base = remote_base + '/wp-content/themes'

    # Common theme directory names
    possible_theme_dirs = [
        theme_slug,
        theme_name.lower().replace(' ', ''),
        'twentytwentyfive',
        'houstonsipqueen'
    ]

    print("🔍 Checking theme directory...")

    actual_theme_dir = None
    # First try the active theme name directly
    actual_theme_dir = theme_slug
    theme_path = f"{remote_base}/{actual_theme_dir}"

    # Verify it exists
    try:
        manager.conn_manager.sftp.stat(f"{theme_path}/style.css")
        print(f"   ✅ Verified theme directory: {actual_theme_dir}")
    except:
        # Try alternative directories
        print(f"   ⚠️  {actual_theme_dir} not found, trying alternatives...")
        for theme_dir in possible_theme_dirs:
            if theme_dir == actual_theme_dir:
                continue
            theme_path = f"{remote_base}/{theme_dir}"
            try:
                manager.conn_manager.sftp.stat(f"{theme_path}/style.css")
                actual_theme_dir = theme_dir
                print(f"   ✅ Found theme directory: {theme_dir}")
                break
            except:
                continue

    if not actual_theme_dir:
        # Try using WP-CLI to get theme directory
        print("   ⚠️  Could not find theme directory, trying WP-CLI...")
        stdout, stderr, code = manager.wp_cli(
            "theme list --status=active --format=json")
        if code == 0:
            import json
            try:
                themes_data = json.loads(stdout)
                if themes_data and isinstance(themes_data, list):
                    active = [t for t in themes_data if t.get(
                        'status') == 'active']
                    if active:
                        actual_theme_dir = active[0].get('name', '')
                        print(
                            f"   ✅ Using theme from WP-CLI: {actual_theme_dir}")
            except:
                pass

    if not actual_theme_dir:
        print("   ❌ Could not determine theme directory")
        manager.disconnect()
        return 1

    theme_base = f"{remote_base}/{actual_theme_dir}"
    print()
    print(f"📁 Theme directory: {theme_base}")
    print()

    # Check if CSS already exists in this directory
    css_filename = "hsq_astros_theme_css.php"
    css_path = f"{theme_base}/{css_filename}"

    print(f"🔍 Checking for CSS file...")
    css_exists = False
    try:
        manager.conn_manager.sftp.stat(css_path)
        css_exists = True
        print(f"   ✅ CSS file already exists in {actual_theme_dir}")
    except:
        print(f"   ⚠️  CSS file not found in {actual_theme_dir}")

    # Deploy CSS to the correct theme directory
    if not css_exists or True:  # Always redeploy to ensure it's in the right place
        print()
        print("📤 Deploying CSS to correct theme directory...")

        css_content = get_astros_css_content()

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

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write(php_code)

        success = manager.conn_manager.upload_file(tmp_path, css_path)
        tmp_path.unlink()

        if not success:
            print(f"   ❌ Failed to deploy CSS file")
            manager.disconnect()
            return 1

        print(f"   ✅ Deployed {css_filename} to {actual_theme_dir}")

    # Update functions.php in the correct theme directory
    func_path = f"{theme_base}/functions.php"
    print()
    print("📝 Updating functions.php...")

    try:
        import tempfile
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

    except Exception as e:
        print(f"   ⚠️  Warning: Could not update functions.php: {e}")

    # Flush cache
    print()
    print("🔄 Flushing cache...")
    manager.purge_caches()

    manager.disconnect()

    print()
    print("✅ CSS deployed to active theme directory!")
    print(f"   Theme: {theme_name}")
    print(f"   Directory: {actual_theme_dir}")
    print()
    print("💡 Refresh the site to see Astros colors")

    return 0


if __name__ == "__main__":
    sys.exit(main())

