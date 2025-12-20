#!/usr/bin/env python3
"""
Test Remaining Plugins - Re-enable Safe Plugins
===============================================
Tests remaining plugins after identifying problematic one.
"""

import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from wordpress_manager import WordPressManager


def test_remaining_plugins(site: str, site_url: str, skip_plugins: list = None):
    """Test remaining plugins to see which are safe."""
    skip_plugins = skip_plugins or []
    
    print("=" * 60)
    print("🔍 Test Remaining Plugins")
    print("=" * 60)
    print(f"Site: {site}")
    print(f"URL: {site_url}")
    print(f"Skipping: {', '.join(skip_plugins)}")
    print()
    
    try:
        manager = WordPressManager(site)
        
        if not manager.connect():
            print("❌ Failed to connect to server")
            return False
        
        print("📡 Connected to server")
        print()
        
        # Path to plugins directories
        site_config = manager.SITE_CONFIGS.get(site, {})
        remote_base = site_config.get("remote_base", "")
        if remote_base:
            parts = remote_base.split("/")
            if len(parts) >= 3 and parts[0] == "domains":
                domain = parts[1]
                plugins_disabled_path = f"domains/{domain}/public_html/wp-content/plugins-disabled"
                plugins_path = f"domains/{domain}/public_html/wp-content/plugins"
            else:
                plugins_disabled_path = "/public_html/wp-content/plugins-disabled"
                plugins_path = "/public_html/wp-content/plugins"
        else:
            plugins_disabled_path = "/public_html/wp-content/plugins-disabled"
            plugins_path = "/public_html/wp-content/plugins"
        
        sftp = manager.conn_manager.sftp
        
        # List plugins in disabled folder
        print("📋 Listing disabled plugins...")
        try:
            plugins = sftp.listdir(plugins_disabled_path)
            # Filter out . and .. and non-directory items and skip_plugins
            plugin_dirs = []
            for plugin in plugins:
                if plugin in skip_plugins or plugin in ['.', '..', 'index.php']:
                    continue
                try:
                    plugin_path = f"{plugins_disabled_path}/{plugin}"
                    attrs = sftp.stat(plugin_path)
                    # Check if it's a directory
                    if attrs.st_mode & 0o040000:
                        plugin_dirs.append(plugin)
                except:
                    pass
            
            print(f"   Found {len(plugin_dirs)} plugins to test")
            print()
            
            if not plugin_dirs:
                print("✅ No plugins to test")
                manager.disconnect()
                return True
            
            # Ensure plugins folder exists
            try:
                sftp.stat(plugins_path)
            except FileNotFoundError:
                sftp.mkdir(plugins_path)
            
            safe_plugins = []
            problematic_plugins = []
            
            # Test each plugin
            for i, plugin in enumerate(plugin_dirs, 1):
                print(f"[{i}/{len(plugin_dirs)}] Testing: {plugin}")
                
                # Move plugin from disabled to enabled
                disabled_plugin_path = f"{plugins_disabled_path}/{plugin}"
                enabled_plugin_path = f"{plugins_path}/{plugin}"
                
                try:
                    sftp.rename(disabled_plugin_path, enabled_plugin_path)
                    print(f"   ✅ Enabled {plugin}")
                    
                    # Wait for WordPress to load
                    time.sleep(3)
                    
                    # Test site
                    try:
                        response = requests.get(site_url, timeout=10)
                        if response.status_code == 500:
                            print(f"   ❌ ERROR: {plugin} causes HTTP 500!")
                            problematic_plugins.append(plugin)
                            
                            # Move it back to disabled
                            sftp.rename(enabled_plugin_path, disabled_plugin_path)
                            print(f"   🔄 Disabled {plugin} again")
                        else:
                            print(f"   ✅ Site works with {plugin}")
                            safe_plugins.append(plugin)
                    except Exception as e:
                        print(f"   ⚠️  Error testing site: {e}")
                        # Move back to disabled on error
                        try:
                            sftp.rename(enabled_plugin_path, disabled_plugin_path)
                        except:
                            pass
                        problematic_plugins.append(plugin)
                        
                except Exception as e:
                    print(f"   ❌ Error enabling plugin: {e}")
            
            manager.disconnect()
            
            # Summary
            print()
            print("=" * 60)
            print("📊 TESTING SUMMARY")
            print("=" * 60)
            print()
            
            if safe_plugins:
                print(f"✅ Safe plugins ({len(safe_plugins)}):")
                for plugin in safe_plugins:
                    print(f"   - {plugin}")
                print()
            
            if problematic_plugins:
                print(f"❌ Problematic plugins ({len(problematic_plugins)}):")
                for plugin in problematic_plugins:
                    print(f"   - {plugin}")
                print()
            
            if not safe_plugins and not problematic_plugins:
                print("⚠️  No plugins tested")
            
            return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
            manager.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test remaining WordPress plugins")
    parser.add_argument("--site", required=True, help="Site key")
    parser.add_argument("--url", required=True, help="Site URL")
    parser.add_argument("--skip", nargs="+", help="Plugins to skip", default=[])
    
    args = parser.parse_args()
    success = test_remaining_plugins(args.site, args.url, skip_plugins=args.skip)
    sys.exit(0 if success else 1)

