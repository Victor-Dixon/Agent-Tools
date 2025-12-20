#!/usr/bin/env python3
"""
Fix wp-admin Redirect to Dashboard
===================================
Fixes wp-admin redirecting to /dashboard causing infinite loop.
Adds exception in functions.php to allow wp-admin access.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from wordpress_manager import WordPressManager


def fix_wpadmin_redirect(site: str):
    """Fix wp-admin redirect by adding exception in functions.php."""
    print("=" * 60)
    print("🔧 Fix wp-admin Dashboard Redirect Loop")
    print("=" * 60)
    print(f"Site: {site}")
    print()
    
    try:
        manager = WordPressManager(site)
        
        if not manager.connect():
            print("❌ Failed to connect to server")
            return False
        
        print("📡 Connected to server")
        print()
        
        # Path to functions.php
        site_config = manager.SITE_CONFIGS.get(site, {})
        remote_base = site_config.get("remote_base", "")
        if remote_base:
            # functions.php is in theme root
            functions_path = remote_base.replace("/wp-content/themes/freerideinvestor", "") + "/wp-content/themes/freerideinvestor/functions.php"
        else:
            functions_path = "/public_html/wp-content/themes/freerideinvestor/functions.php"
        
        sftp = manager.conn_manager.sftp
        
        # Read functions.php
        print("📖 Reading functions.php...")
        try:
            with sftp.open(functions_path, 'r') as f:
                content = f.read().decode('utf-8')
            
            print("✅ functions.php found")
            print()
            
            # Check if fix already exists
            if "// Allow wp-admin access" in content or "is_admin()" in content and "restrict_access" in content:
                print("⚠️  Fix may already be present. Checking...")
                # Look for the specific fix pattern
                if "is_admin()" in content and "return;" in content.split("is_admin()")[1].split("\n")[0]:
                    print("✅ Fix already applied")
                    manager.disconnect()
                    return True
            
            # Find the restrict_access_and_premium_content function
            if "function restrict_access_and_premium_content()" not in content:
                print("⚠️  restrict_access_and_premium_content function not found")
                print("💡 The redirect may be coming from elsewhere")
                manager.disconnect()
                return False
            
            # Add exception for wp-admin at the start of the function
            print("🔧 Adding wp-admin exception...")
            
            # Find the function and add exception right after the AJAX/REST check
            lines = content.split('\n')
            new_lines = []
            in_function = False
            added_fix = False
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Find the function start
                if "function restrict_access_and_premium_content()" in line:
                    in_function = True
                    continue
                
                # After the function opening brace and AJAX/REST check, add wp-admin exception
                if in_function and not added_fix:
                    # Look for the AJAX/REST check block end
                    if "if ((defined('DOING_AJAX')" in line or "if (is_user_logged_in())" in line:
                        # Add exception after the AJAX/REST block
                        if "}" in lines[i+1] if i+1 < len(lines) else False:
                            # Add wp-admin exception
                            new_lines.append("")
                            new_lines.append("    // Allow wp-admin and wp-login.php access (fix redirect loop)")
                            new_lines.append("    if (is_admin() || (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/wp-admin') !== false) || (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/wp-login.php') !== false)) {")
                            new_lines.append("        return;")
                            new_lines.append("    }")
                            new_lines.append("")
                            added_fix = True
                            print("   ✅ Added wp-admin exception")
                            continue
            
            if not added_fix:
                # Try alternative: add at the very beginning of function
                print("   ⚠️  Could not find insertion point, trying alternative method...")
                new_lines = []
                for i, line in enumerate(lines):
                    if "function restrict_access_and_premium_content()" in line:
                        new_lines.append(line)
                        # Find the opening brace
                        if i+1 < len(lines) and "{" in lines[i+1]:
                            new_lines.append(lines[i+1])
                            # Add exception right after opening brace
                            new_lines.append("    // Allow wp-admin and wp-login.php access (fix redirect loop)")
                            new_lines.append("    if (is_admin() || (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/wp-admin') !== false) || (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/wp-login.php') !== false)) {")
                            new_lines.append("        return;")
                            new_lines.append("    }")
                            new_lines.append("")
                            added_fix = True
                            continue
                    new_lines.append(line)
            
            if added_fix:
                new_content = '\n'.join(new_lines)
                
                # Backup functions.php
                backup_path = functions_path + ".backup"
                print(f"💾 Creating backup: {backup_path}")
                with sftp.open(backup_path, 'w') as f:
                    f.write(content.encode('utf-8'))
                print("✅ Backup created")
                print()
                
                # Write fixed functions.php
                print("📝 Writing fixed functions.php...")
                with sftp.open(functions_path, 'w') as f:
                    f.write(new_content.encode('utf-8'))
                print("✅ functions.php updated")
                print()
                print("💡 wp-admin should now be accessible")
                print("   Test: https://freerideinvestor.com/wp-admin/")
            else:
                print("❌ Could not add fix automatically")
                print("💡 Manual fix needed in functions.php")
                print("   Add this at the start of restrict_access_and_premium_content():")
                print("   if (is_admin() || strpos($_SERVER['REQUEST_URI'], '/wp-admin') !== false) { return; }")
        
        except FileNotFoundError:
            print(f"❌ functions.php not found at: {functions_path}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix wp-admin redirect loop")
    parser.add_argument("--site", required=True, help="Site key")
    
    args = parser.parse_args()
    success = fix_wpadmin_redirect(args.site)
    sys.exit(0 if success else 1)

