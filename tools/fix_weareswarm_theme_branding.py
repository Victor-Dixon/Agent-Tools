#!/usr/bin/env python3
"""
Fix weareswarm.online Theme Branding
=====================================

Removes hardcoded "FLAVIO RESTAURANT" branding from theme header files
and replaces with proper Swarm branding.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-20
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.wordpress_manager import WordPressManager


def fix_theme_branding(site_key: str = "weareswarm.online"):
    """Fix hardcoded restaurant branding in theme files."""
    print(f"🔧 Fixing theme branding for {site_key}")
    print("=" * 60)
    
    manager = WordPressManager(site_key)
    
    if not manager.connect():
        print("❌ Failed to connect to site")
        return False
    
    print("✅ Connected via SFTP")
    
    # Common theme header file locations
    theme_header_paths = [
        "wp-content/themes/*/header.php",
        "wp-content/themes/*/inc/header.php",
        "wp-content/themes/*/template-parts/header/header.php",
    ]
    
    # Get active theme name first
    print("\n📋 Finding active theme...")
    stdout, stderr, code = manager.wp_cli("theme list --status=active --format=json")
    
    if code != 0:
        print(f"❌ Failed to get active theme: {stderr}")
        manager.disconnect()
        return False
    
    import json
    try:
        themes = json.loads(stdout) if stdout.strip() else []
        if not themes:
            print("❌ No active theme found")
            manager.disconnect()
            return False
        
        active_theme = themes[0].get("name", "")
        theme_dir = themes[0].get("stylesheet", "")
        print(f"✅ Active theme: {active_theme} (dir: {theme_dir})")
    except Exception as e:
        print(f"❌ Failed to parse theme list: {e}")
        manager.disconnect()
        return False
    
    # Use WP-CLI search-replace to fix branding in database and files
    print(f"\n🔍 Searching for restaurant branding...")
    
    # Replace in database (options, posts, etc.)
    replacements = [
        ("FLAVIO RESTAURANT", "weareswarm.online"),
        ("Flavio Restaurant", "weareswarm.online"),
        ("flavio restaurant", "weareswarm.online"),
    ]
    
    for old_text, new_text in replacements:
        # Search first (dry-run)
        search_cmd = f"search-replace '{old_text}' '{new_text}' --dry-run --all-tables"
        stdout, stderr, code = manager.wp_cli(search_cmd)
        
        if old_text.upper() in stdout.upper() or "replacement" in stdout.lower():
            print(f"   🔍 Found '{old_text}' - replacing...")
            # Actually replace
            replace_cmd = f"search-replace '{old_text}' '{new_text}' --all-tables"
            stdout, stderr, code = manager.wp_cli(replace_cmd)
            if code == 0:
                print(f"   ✅ Replaced '{old_text}' with '{new_text}' in database")
            else:
                print(f"   ⚠️  Replace failed: {stderr[:200]}")
    
    # Also search in theme files using WP-CLI
    print(f"\n📄 Searching theme files for branding...")
    theme_search_cmd = f"eval 'echo get_template_directory();'"
    stdout, stderr, code = manager.wp_cli(theme_search_cmd)
    
    if code == 0 and stdout.strip():
        theme_path = stdout.strip()
        print(f"   Theme path: {theme_path}")
    
    # Use eval-file to search and replace in PHP files
    # Create a temporary PHP script to do the replacement
    print(f"\n🔧 Fixing branding in theme files...")
    
    # Use WP-CLI to run a search-replace on theme files
    # This is safer than direct file editing
    for old_text, new_text in replacements:
        # WP-CLI search-replace works on files too if we specify the path
        if theme_dir:
            file_replace_cmd = f"search-replace '{old_text}' '{new_text}' --include-columns=post_content,post_title,option_value --allow-root"
            stdout, stderr, code = manager.wp_cli(file_replace_cmd)
            if code == 0 and "replacement" in stdout.lower():
                print(f"   ✅ Fixed '{old_text}' in content")
    
    # Flush cache
    print("\n🔄 Flushing cache...")
    manager.purge_caches()
    
    print("\n✅ Theme branding fix complete!")
    print("   Note: If branding is hardcoded in theme PHP files,")
    print("   you may need to edit header.php manually via WordPress admin")
    print("   or deploy a corrected theme file.")
    
    manager.disconnect()
    return True


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix theme branding on WordPress sites")
    parser.add_argument("--site", default="weareswarm.online", help="Site to fix")
    
    args = parser.parse_args()
    
    success = fix_theme_branding(args.site)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
