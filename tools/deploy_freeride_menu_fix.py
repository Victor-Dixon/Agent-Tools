#!/usr/bin/env python3
"""
Deploy FreeRideInvestor Menu Fix - Interactive Deployment Tool
================================================================

Deploys the enhanced functions.php that removes all Developer Tools links.
Can prompt for credentials if not configured.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from wordpress_manager import WordPressManager
import getpass

def prompt_for_credentials():
    """Prompt user for SFTP credentials."""
    print("\n" + "=" * 60)
    print("📋 SFTP Credentials Required")
    print("=" * 60)
    print("\nPlease provide Hostinger SFTP credentials:")
    print("(These will be used for this deployment only)\n")
    
    host = input("Host (e.g., ftp.hostinger.com): ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    port_str = input("Port (default 65002): ").strip() or "65002"
    
    try:
        port = int(port_str)
    except ValueError:
        port = 65002
    
    if not all([host, username, password]):
        print("❌ All fields are required")
        return None
    
    return {
        "host": host,
        "username": username,
        "password": password,
        "port": port
    }

def main():
    """Deploy FreeRideInvestor functions.php with menu fix."""
    print("=" * 60)
    print("🚀 FreeRideInvestor Menu Fix Deployment")
    print("=" * 60)
    print()
    
    # Initialize manager
    try:
        manager = WordPressManager("freerideinvestor")
    except Exception as e:
        print(f"❌ Failed to initialize manager: {e}")
        return 1
    
    # Check credentials
    if not manager.credentials:
        print("⚠️  No credentials found in .env or sites.json")
        print()
        
        # Prompt for credentials
        creds = prompt_for_credentials()
        if not creds:
            return 1
        
        # Temporarily set credentials
        manager.credentials = creds
        print("\n✅ Credentials set (temporary, not saved)")
    else:
        print("✅ Credentials loaded from config")
        print(f"   Host: {manager.credentials.get('host', 'N/A')}")
        print(f"   Port: {manager.credentials.get('port', 'N/A')}")
    
    print()
    
    # Get theme path
    try:
        theme_path = manager.get_theme_path()
        functions_file = theme_path / "functions.php"
    except Exception as e:
        print(f"❌ Failed to get theme path: {e}")
        return 1
    
    if not functions_file.exists():
        print(f"❌ functions.php not found: {functions_file}")
        return 1
    
    print(f"✅ Found functions.php: {functions_file}")
    print(f"   Size: {functions_file.stat().st_size:,} bytes")
    print()
    
    # Connect
    print("🔌 Connecting to server...")
    if not manager.connect():
        print("❌ Connection failed!")
        print("\nTroubleshooting:")
        print("  - Verify host, username, and password are correct")
        print("  - Check if SFTP port (65002) is open")
        print("  - Verify server is accessible")
        return 1
    
    print("✅ Connected successfully!")
    print()
    
    # Deploy
    print("📤 Deploying functions.php...")
    remote_path = f"{manager.config['remote_base']}/functions.php"
    print(f"   Remote: {remote_path}")
    
    if manager.deploy_file(functions_file, remote_path):
        print("✅ functions.php deployed successfully!")
        print()
        
        # Disconnect
        manager.disconnect()
        
        print("=" * 60)
        print("✅ DEPLOYMENT COMPLETE")
        print("=" * 60)
        print()
        print("📋 Next Steps:")
        print("  1. Clear WordPress menu cache:")
        print("     - Go to Appearance > Menus > Save Menu")
        print("     - Or Settings > Permalinks > Save Changes")
        print()
        print("  2. Check WordPress admin:")
        print("     - Go to Appearance > Menus")
        print("     - Manually remove any 'Developer Tool' items")
        print("     - Save menu")
        print()
        print("  3. Verify on live site:")
        print("     - Visit https://freerideinvestor.com")
        print("     - Check navigation menu (should show 0 Developer Tools links)")
        print()
        
        return 0
    else:
        print("❌ Deployment failed!")
        manager.disconnect()
        return 1

if __name__ == "__main__":
    sys.exit(main())




