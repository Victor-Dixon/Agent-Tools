#!/usr/bin/env python3
"""
Verify Houston Sip Queen Astros CSS is Loading
==============================================
Checks if the Astros theme CSS is properly deployed and included in functions.php

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


def verify_css_deployment(manager: WordPressManager) -> bool:
    """Verify CSS file is deployed and included in functions.php."""
    print("=" * 60)
    print("🔍 Verifying Astros CSS Deployment")
    print("=" * 60)
    print()

    if not manager.connect():
        print("❌ Failed to connect to server")
        return False

    print("✅ Connected to server")
    print()

    # Get remote base path
    remote_base = manager.config.get("remote_base", "")
    if not remote_base:
        remote_base = "domains/houstonsipqueen.com/public_html/wp-content/themes/twentytwentyfive"

    css_filename = "hsq_astros_theme_css.php"
    func_path = f"{remote_base}/functions.php"
    css_path = f"{remote_base}/{css_filename}"

    print(f"Checking files in: {remote_base}")
    print()

    # Check if CSS file exists
    print("1️⃣  Checking CSS file...")
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.php') as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            manager.conn_manager.sftp.get(css_path, str(tmp_path))
            css_content = tmp_path.read_text(encoding='utf-8')
            tmp_path.unlink()

            # Check for Astros color variables
            has_navy = "--astros-navy" in css_content
            has_orange = "--astros-orange" in css_content
            has_function = "hsq_astros_theme_styles" in css_content

            print(f"   ✅ CSS file exists: {css_path}")
            print(f"   ✅ Contains --astros-navy: {has_navy}")
            print(f"   ✅ Contains --astros-orange: {has_orange}")
            print(
                f"   ✅ Contains function hsq_astros_theme_styles: {has_function}")

            if has_navy and has_orange and has_function:
                print("   ✅ CSS file is valid")
                css_valid = True
            else:
                print("   ⚠️  CSS file may be incomplete")
                css_valid = False

        except FileNotFoundError:
            print(f"   ❌ CSS file not found: {css_path}")
            css_valid = False
            tmp_path.unlink()

    except Exception as e:
        print(f"   ❌ Error checking CSS file: {e}")
        css_valid = False

    print()

    # Check if functions.php includes the CSS file
    print("2️⃣  Checking functions.php...")
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.php') as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            manager.conn_manager.sftp.get(func_path, str(tmp_path))
            func_content = tmp_path.read_text(encoding='utf-8')
            tmp_path.unlink()

            # Check if CSS file is included
            has_include = css_filename in func_content
            has_require = f"require_once" in func_content and css_filename in func_content

            print(f"   ✅ functions.php exists: {func_path}")
            print(f"   ✅ Contains {css_filename}: {has_include}")
            print(f"   ✅ Has require_once statement: {has_require}")

            if has_include:
                # Show the relevant line
                for line in func_content.split('\n'):
                    if css_filename in line:
                        print(f"   📝 Include line: {line.strip()}")
                        break

                func_valid = True
            else:
                print(f"   ❌ {css_filename} not found in functions.php")
                func_valid = False

        except FileNotFoundError:
            print(f"   ⚠️  functions.php not found (may be using default)")
            func_valid = False
            tmp_path.unlink()

    except Exception as e:
        print(f"   ❌ Error checking functions.php: {e}")
        func_valid = False

    print()

    # Summary
    print("=" * 60)
    print("📊 Verification Summary")
    print("=" * 60)
    print()

    if css_valid and func_valid:
        print("✅ CSS is properly deployed and included")
        print("✅ Astros theme should be active on the site")
        print()
        print("💡 If colors don't appear, try:")
        print("   1. Hard refresh the browser (Ctrl+F5)")
        print("   2. Clear browser cache")
        print("   3. Check browser console for errors")
        return True
    elif css_valid and not func_valid:
        print("⚠️  CSS file exists but may not be included in functions.php")
        print("💡 The CSS file is deployed but may need manual inclusion")
        return False
    elif not css_valid:
        print("❌ CSS file is missing or invalid")
        print("💡 Run apply_hsq_astros_theme.py to deploy the CSS")
        return False
    else:
        print("❌ Verification failed")
        return False


def main():
    """Main entry point."""
    # Try common site keys
    site_keys = ["houstonsipqueen", "houstonsipqueen.com", "hsq"]

    manager = None
    site_key = None

    for key in site_keys:
        try:
            manager = WordPressManager(key)
            if manager.config:
                site_key = key
                break
        except Exception:
            continue

    if not manager or not manager.config:
        print("❌ Could not find site configuration for houstonsipqueen")
        return 1

    success = verify_css_deployment(manager)

    if manager:
        manager.disconnect()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

