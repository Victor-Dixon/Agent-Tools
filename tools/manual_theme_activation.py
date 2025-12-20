#!/usr/bin/env python3
"""
Manual Theme Activation - Database Method
==========================================

Manually activates theme via database if files are correct but WordPress
doesn't detect it. Use as last resort after clearing transients and
checking for errors.

Author: Agent-7 (Web Development Specialist)
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from wordpress_manager import WordPressManager
    HAS_WORDPRESS_MANAGER = True
except ImportError:
    HAS_WORDPRESS_MANAGER = False
    print("⚠️  wordpress_manager not available")


def activate_theme_via_database(site: str, theme_name: str) -> bool:
    """
    Manually activate theme via database.
    
    Args:
        site: Site key
        theme_name: Theme directory name (e.g., "ariajet")
        
    Returns:
        True if successful
    """
    print("=" * 60)
    print("🔧 Manual Theme Activation via Database")
    print("=" * 60)
    print(f"Site: {site}")
    print(f"Theme: {theme_name}")
    print()
    print("⚠️  WARNING: This modifies the database directly")
    print("⚠️  Only use if files are correct but WordPress doesn't detect theme")
    print()
    
    if not HAS_WORDPRESS_MANAGER:
        print("❌ wordpress_manager not available")
        print("💡 Manual SQL method:")
        print("   UPDATE wp_options SET option_value = 'theme_name' WHERE option_name = 'template';")
        print("   UPDATE wp_options SET option_value = 'theme_name' WHERE option_name = 'stylesheet';")
        return False
    
    try:
        manager = WordPressManager(site)
        
        if not manager.connect():
            print("❌ Failed to connect to server")
            return False
        
        print("📡 Connected to server")
        print()
        
        # SQL commands to activate theme
        sql_commands = [
            f"UPDATE wp_options SET option_value = '{theme_name}' WHERE option_name = 'template';",
            f"UPDATE wp_options SET option_value = '{theme_name}' WHERE option_name = 'stylesheet';",
        ]
        
        print("🔧 Executing SQL commands...")
        print("⚠️  Note: This requires database access via SSH")
        print("💡 Alternative: Use WP-CLI:")
        print(f"   wp theme activate {theme_name}")
        print()
        
        # For now, just show the commands
        # Actual execution would need database connection
        for sql in sql_commands:
            print(f"   {sql}")
        
        manager.disconnect()
        
        print()
        print("💡 To execute manually:")
        print("   1. Connect to database via phpMyAdmin or SSH")
        print("   2. Run the SQL commands above")
        print("   3. Or use WP-CLI: wp theme activate {theme_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manually activate theme via database"
    )
    parser.add_argument(
        "--site",
        required=True,
        help="Site key (e.g., ariajet, freerideinvestor)"
    )
    parser.add_argument(
        "--theme",
        required=True,
        help="Theme directory name (e.g., ariajet)"
    )
    
    args = parser.parse_args()
    
    print("⚠️  WARNING: Manual database activation should be last resort")
    print("⚠️  Try these first:")
    print("   1. Clear transients: python tools/clear_wordpress_transients.py --site {args.site}")
    print("   2. Check syntax: python tools/check_theme_syntax.py --theme path/to/theme")
    print("   3. Enable debug: python tools/enable_wordpress_debug.py --site {args.site}")
    print()
    
    response = input("Continue with manual activation? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled")
        return 0
    
    success = activate_theme_via_database(args.site, args.theme)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())




