#!/usr/bin/env python3
"""
Deploy via SFTP/SSH - The Original Method
==========================================

Uses the existing wordpress_manager.py to deploy files via SFTP/SSH.
This is the method we've used successfully before - no plugins needed!

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from wordpress_manager import WordPressManager


def deploy_file(site: str, file_path: Path) -> bool:
    """
    Deploy a file to WordPress site via SFTP/SSH.
    
    Args:
        site: Site key (e.g., "freerideinvestor", "prismblossom.online")
        file_path: Local file path to deploy
        
    Returns:
        True if successful, False otherwise
    """
    print("=" * 60)
    print("🚀 SFTP/SSH Deployment - The Original Method")
    print("=" * 60)
    print(f"Site: {site}")
    print(f"File: {file_path}")
    print()
    
    try:
        # Initialize manager
        manager = WordPressManager(site)
        
        # Connect to server
        print("📡 Connecting to server...")
        if not manager.connect():
            print("❌ Failed to connect")
            print("💡 Check credentials in:")
            print("   - .deploy_credentials/sites.json")
            print("   - .env file (HOSTINGER_HOST, HOSTINGER_USER, HOSTINGER_PASS, HOSTINGER_PORT)")
            return False
        
        print("✅ Connected!")
        print()
        
        # Deploy file
        print(f"📤 Deploying {file_path.name}...")
        if manager.deploy_file(file_path):
            print(f"✅ File deployed successfully!")
            manager.disconnect()
            return True
        else:
            print(f"❌ Deployment failed")
            manager.disconnect()
            return False
            
    except ValueError as e:
        print(f"❌ Site configuration error: {e}")
        print("💡 Available sites:")
        print("   - freerideinvestor")
        print("   - prismblossom.online")
        print("   - southwestsecret")
        print("   - ariajet")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Deploy file via SFTP/SSH (the original method)"
    )
    parser.add_argument(
        "--site",
        required=True,
        help="Site key (e.g., freerideinvestor, prismblossom.online)"
    )
    parser.add_argument(
        "--file",
        required=True,
        type=Path,
        help="File path to deploy"
    )
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(f"❌ File not found: {args.file}")
        return 1
    
    success = deploy_file(args.site, args.file)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())




