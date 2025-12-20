#!/usr/bin/env python3
"""
Fix Theme Header Branding - Direct File Edit
============================================

Downloads, edits, and re-uploads theme header.php to remove hardcoded branding.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-20
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.wordpress_manager import WordPressManager


def fix_header_branding(site_key: str = "weareswarm.online"):
    """Fix hardcoded branding in theme header.php file."""
    print(f"🔧 Fixing theme header branding for {site_key}")
    print("=" * 60)
    
    manager = WordPressManager(site_key)
    
    if not manager.connect():
        print("❌ Failed to connect to site")
        return False
    
    print("✅ Connected via SFTP")
    
    # Get active theme
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
        
        # Get theme directory - use name if stylesheet is empty
        theme_dir = themes[0].get("stylesheet", "") or themes[0].get("name", "").lower().replace(" ", "-")
        if not theme_dir:
            # Fallback: try template field
            theme_dir = themes[0].get("template", "")
        print(f"✅ Active theme: {themes[0].get('name', 'Unknown')}")
        print(f"✅ Theme directory: {theme_dir}")
    except Exception as e:
        print(f"❌ Failed to parse theme list: {e}")
        manager.disconnect()
        return False
    
    # Header file path - check remote_base format
    remote_base = manager.config.get('remote_base', '')
    print(f"\n📋 Remote base: {remote_base}")
    
    # Construct full remote path
    if remote_base.startswith('/'):
        # Absolute path
        header_file = f"{remote_base}/wp-content/themes/{theme_dir}/header.php"
    else:
        # Relative path - need to prepend home directory
        username = manager.credentials.get('username', 'u996867598')
        header_file = f"/home/{username}/domains/{site_key}/public_html/wp-content/themes/{theme_dir}/header.php"
    
    remote_path = header_file
    print(f"\n📄 Downloading header file: {remote_path}")
    
    # Download file to temp location
    tmp_path = None
    try:
        # Create temp file
        tmp_path = Path(tempfile.mktemp(suffix='.php'))
        
        # Use SFTP get to download the file
        manager.conn_manager.sftp.get(remote_path, str(tmp_path))
        
        # Read content
        content = tmp_path.read_text(encoding='utf-8')
        original_content = content
        
        print(f"✅ Downloaded header file ({len(content)} bytes)")
        
        # Check if Flavio branding exists
        if "FLAVIO" not in content.upper() and "RESTAURANT" not in content.upper():
            print("✅ No restaurant branding found in header file")
            manager.disconnect()
            return True
        
        print("🔍 Found restaurant branding - removing...")
        
        # Replace Flavio Restaurant branding
        replacements = [
            ("FLAVIO RESTAURANT", "weareswarm.online"),
            ("Flavio Restaurant", "weareswarm.online"),
            ("flavio restaurant", "weareswarm.online"),
            ("FLAVIO", "weareswarm.online"),
            ("Flavio", "weareswarm.online"),
        ]
        
        changes_made = False
        for old_text, new_text in replacements:
            if old_text in content:
                content = content.replace(old_text, new_text)
                print(f"   ✅ Replaced '{old_text}' with '{new_text}'")
                changes_made = True
        
        if changes_made:
            # Write updated content
            tmp_path.write_text(content, encoding='utf-8')
            
            # Upload back
            print(f"\n📤 Uploading fixed header file...")
            success = manager.conn_manager.upload_file(tmp_path, remote_path)
            
            if success:
                print(f"✅ Header file updated successfully!")
                
                # Flush cache
                print("\n🔄 Flushing cache...")
                manager.purge_caches()
                
                print("\n✅ Theme header branding fixed!")
                print("   Refresh the site to see changes")
            else:
                print(f"❌ Failed to upload header file")
                return False
        else:
            print("⚠️  No changes needed")
        
    except Exception as e:
        print(f"❌ Error fixing header branding: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up temp file
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except:
                pass
        manager.disconnect()
    
    return True


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix theme header branding on WordPress sites")
    parser.add_argument("--site", default="weareswarm.online", help="Site to fix")
    
    args = parser.parse_args()
    
    success = fix_header_branding(args.site)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
