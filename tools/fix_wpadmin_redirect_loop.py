#!/usr/bin/env python3
"""
Fix WordPress wp-admin Redirect Loop
====================================
Fixes redirect loop where wp-admin redirects to /dashboard causing infinite loop.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from wordpress_manager import WordPressManager


def fix_wpadmin_redirect(site: str):
    """Fix wp-admin redirect loop."""
    print("=" * 60)
    print("🔧 Fix wp-admin Redirect Loop")
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
        
        # Path to .htaccess
        site_config = manager.SITE_CONFIGS.get(site, {})
        remote_base = site_config.get("remote_base", "")
        if remote_base:
            parts = remote_base.split("/")
            if len(parts) >= 3 and parts[0] == "domains":
                domain = parts[1]
                htaccess_path = f"domains/{domain}/public_html/.htaccess"
            else:
                htaccess_path = "/public_html/.htaccess"
        else:
            htaccess_path = "/public_html/.htaccess"
        
        sftp = manager.conn_manager.sftp
        
        # Check .htaccess for redirect rules
        print("📖 Checking .htaccess...")
        try:
            with sftp.open(htaccess_path, 'r') as f:
                content = f.read().decode('utf-8')
            
            print("✅ .htaccess found")
            print()
            
            # Look for problematic redirects
            problematic_patterns = [
                'RewriteRule.*dashboard',
                'RewriteRule.*wp-admin.*dashboard',
                'Redirect.*dashboard',
                'dashboard.*wp-admin'
            ]
            
            found_issues = []
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern in problematic_patterns:
                    if pattern.lower() in line.lower() and '#' not in line[:line.find(pattern.lower())]:
                        found_issues.append((i, line.strip()))
                        break
            
            if found_issues:
                print("⚠️  Found potential redirect issues:")
                for line_num, line in found_issues:
                    print(f"   Line {line_num}: {line}")
                print()
                
                # Backup .htaccess
                backup_path = htaccess_path + ".backup"
                print(f"💾 Creating backup: {backup_path}")
                with sftp.open(backup_path, 'w') as f:
                    f.write(content.encode('utf-8'))
                print("✅ Backup created")
                print()
                
                # Comment out problematic lines
                print("🔧 Commenting out problematic redirect rules...")
                new_lines = []
                for i, line in enumerate(lines, 1):
                    is_problematic = any((i, _) in found_issues for _ in [line.strip()])
                    if is_problematic and not line.strip().startswith('#'):
                        new_lines.append(f"# {line}  # COMMENTED OUT - causing redirect loop")
                        print(f"   Line {i}: Commented out")
                    else:
                        new_lines.append(line)
                
                new_content = '\n'.join(new_lines)
                
                # Write fixed .htaccess
                print()
                print("📝 Writing fixed .htaccess...")
                with sftp.open(htaccess_path, 'w') as f:
                    f.write(new_content.encode('utf-8'))
                print("✅ .htaccess updated")
                print()
                print("💡 Test wp-admin now. If issue persists, check theme functions.php for redirects.")
                
            else:
                print("✅ No obvious redirect issues in .htaccess")
                print()
                print("💡 The redirect loop may be caused by:")
                print("   1. Theme functions.php redirect code")
                print("   2. Plugin redirect (even if disabled, code may be cached)")
                print("   3. WordPress settings (Settings > General > Site Address)")
                print()
                print("   Try accessing: https://freerideinvestor.com/wp-login.php directly")
        
        except FileNotFoundError:
            print("⚠️  .htaccess not found (this is normal for some WordPress installs)")
            print()
            print("💡 The redirect loop may be caused by:")
            print("   1. Theme functions.php redirect code")
            print("   2. WordPress settings")
            print()
            print("   Try accessing: https://freerideinvestor.com/wp-login.php directly")
        
        except Exception as e:
            print(f"❌ Error reading .htaccess: {e}")
        
        manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix wp-admin redirect loop")
    parser.add_argument("--site", required=True, help="Site key")
    
    args = parser.parse_args()
    success = fix_wpadmin_redirect(args.site)
    sys.exit(0 if success else 1)

