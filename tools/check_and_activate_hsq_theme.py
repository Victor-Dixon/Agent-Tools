#!/usr/bin/env python3
"""
Check and Activate Houston Sip Queen Theme
==========================================
Uses WordPress Manager to list available themes and activate one for houstonsipqueen.com

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


def main():
    """Check themes and activate for Houston Sip Queen."""
    print("=" * 60)
    print("🎨 Houston Sip Queen - Theme Activation")
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
        print("💡 Tried keys:", site_keys)
        print()
        print("Available site configs are typically in .env or site-specific config files")
        return 1

    print(f"Site: {site_key}")
    print()

    # List available themes
    print("📋 Listing available themes...")
    try:
        themes = manager.list_themes()
        if themes:
            print(f"Found {len(themes)} theme(s):")
            print()
            for theme in themes:
                name = theme.get('name', 'Unknown')
                status = theme.get('status', 'Unknown')
                active_marker = " (ACTIVE)" if status == 'active' else ""
                print(f"  - {name}: {status}{active_marker}")
            print()

            # Check if there's already an active theme
            active_themes = [t for t in themes if t.get('status') == 'active']
            if active_themes:
                active_theme = active_themes[0]
                print(f"✅ Active theme: {active_theme.get('name')}")
                print()
                print("ℹ️  Theme is already active. No action needed.")
                return 0

            # Try to activate a common theme or the first available
            if themes:
                # Prefer themes that might be suitable for Houston Sip Queen
                preferred_names = [
                    'twentytwentyfour', 'twentytwentythree', 'twentytwenty', 'astra', 'generatepress']

                theme_to_activate = None
                for preferred in preferred_names:
                    for theme in themes:
                        if preferred.lower() in theme.get('name', '').lower():
                            theme_to_activate = theme
                            break
                    if theme_to_activate:
                        break

                if not theme_to_activate:
                    # Use first inactive theme
                    inactive_themes = [
                        t for t in themes if t.get('status') != 'active']
                    if inactive_themes:
                        theme_to_activate = inactive_themes[0]

                if theme_to_activate:
                    theme_name = theme_to_activate.get('name', '')
                    print(f"🎨 Activating theme: {theme_name}")
                    success = manager.activate_theme(theme_name)
                    if success:
                        print(
                            f"✅ Theme '{theme_name}' activated successfully!")
                        return 0
                    else:
                        print(f"❌ Failed to activate theme '{theme_name}'")
                        return 1
        else:
            print("⚠️  No themes found")
            print("💡 Theme list might be empty or WP-CLI not available")
            return 1

    except Exception as e:
        print(f"❌ Error listing themes: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

