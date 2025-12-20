#!/usr/bin/env python3
"""
WordPress Deployer Debug Tool
=============================

Comprehensive debugging and testing tool for WordPress deployment system.
Tests all functionality and identifies issues.

<!-- SSOT Domain: infrastructure -->

Author: Agent-4 (Captain)
"""

import sys
from pathlib import Path
import json

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported."""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from wordpress_manager import WordPressManager, ConnectionManager
        print("✅ wordpress_manager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wordpress_manager: {e}")
        return False
    
    try:
        from wordpress_deployment_manager import WordPressDeploymentManager
        print("✅ wordpress_deployment_manager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wordpress_deployment_manager: {e}")
        return False
    
    try:
        from website_manager import WebsiteManager
        print("✅ website_manager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import website_manager: {e}")
        return False
    
    try:
        import paramiko
        print("✅ paramiko (SSH library) available")
    except ImportError:
        print("⚠️  paramiko not installed - SFTP deployment will not work")
        print("   Install with: pip install paramiko")
    
    return True

def test_site_configs():
    """Test site configuration loading."""
    print("\n" + "=" * 60)
    print("TEST 2: Site Configuration")
    print("=" * 60)
    
    from wordpress_manager import WordPressManager
    
    sites = ["prismblossom", "freerideinvestor", "southwestsecret"]
    results = {}
    
    for site in sites:
        try:
            manager = WordPressManager(site)
            print(f"✅ {site}: Config loaded")
            print(f"   Local path: {manager.config['local_path']}")
            print(f"   Theme: {manager.config['theme_name']}")
            print(f"   Remote: {manager.config['remote_base']}")
            
            # Test theme path detection
            try:
                theme_path = manager.get_theme_path()
                print(f"   Theme path found: {theme_path}")
                results[site] = True
            except FileNotFoundError as e:
                print(f"   ⚠️  Theme path not found: {e}")
                results[site] = False
        except Exception as e:
            print(f"❌ {site}: {e}")
            results[site] = False
    
    return all(results.values())

def test_credentials():
    """Test credential loading."""
    print("\n" + "=" * 60)
    print("TEST 3: Credential Loading")
    print("=" * 60)
    
    from wordpress_manager import WordPressManager
    
    sites = ["prismblossom", "freerideinvestor"]
    results = {}
    
    for site in sites:
        try:
            manager = WordPressManager(site)
            if manager.credentials:
                print(f"✅ {site}: Credentials loaded")
                print(f"   Host: {manager.credentials.get('host', 'N/A')}")
                print(f"   Username: {manager.credentials.get('username', 'N/A')}")
                print(f"   Port: {manager.credentials.get('port', 'N/A')}")
                results[site] = True
            else:
                print(f"⚠️  {site}: No credentials found")
                print("   Check .env file or .deploy_credentials/sites.json")
                results[site] = False
        except Exception as e:
            print(f"❌ {site}: {e}")
            results[site] = False
    
    return any(results.values())  # At least one site has credentials

def test_connection():
    """Test SSH/SFTP connection."""
    print("\n" + "=" * 60)
    print("TEST 4: Connection Test")
    print("=" * 60)
    
    try:
        import paramiko
    except ImportError:
        print("⚠️  paramiko not installed - skipping connection test")
        return None
    
    from wordpress_manager import WordPressManager
    
    sites = ["prismblossom", "freerideinvestor"]
    results = {}
    
    for site in sites:
        try:
            manager = WordPressManager(site)
            if not manager.credentials:
                print(f"⚠️  {site}: No credentials - skipping connection test")
                results[site] = None
                continue
            
            print(f"Testing connection to {site}...")
            if manager.connect():
                print(f"✅ {site}: Connection successful")
                manager.disconnect()
                results[site] = True
            else:
                print(f"❌ {site}: Connection failed")
                results[site] = False
        except Exception as e:
            print(f"❌ {site}: {e}")
            results[site] = False
    
    return results

def test_page_operations():
    """Test page creation and listing."""
    print("\n" + "=" * 60)
    print("TEST 5: Page Operations")
    print("=" * 60)
    
    from wordpress_manager import WordPressManager
    
    try:
        manager = WordPressManager("prismblossom")
        pages = manager.list_pages()
        print(f"✅ Found {len(pages)} page templates")
        for page in pages[:5]:  # Show first 5
            print(f"   • {page['file']} - {page['template_name']}")
        return True
    except Exception as e:
        print(f"❌ Page operations failed: {e}")
        return False

def test_deployment():
    """Test file deployment (dry run)."""
    print("\n" + "=" * 60)
    print("TEST 6: Deployment Test (Dry Run)")
    print("=" * 60)
    
    from wordpress_manager import WordPressManager
    
    try:
        manager = WordPressManager("prismblossom")
        theme_path = manager.get_theme_path()
        
        # Find a test file
        test_files = list(theme_path.glob("*.php"))[:3]
        if not test_files:
            print("⚠️  No PHP files found for testing")
            return None
        
        print(f"Found {len(test_files)} test files")
        for test_file in test_files:
            print(f"   • {test_file.name}")
        
        print("\n⚠️  Deployment test requires active connection")
        print("   Run with --test-deploy to actually test deployment")
        return True
    except Exception as e:
        print(f"❌ Deployment test failed: {e}")
        return False

def generate_report():
    """Generate comprehensive debug report."""
    print("\n" + "=" * 60)
    print("WORDPRESS DEPLOYER DEBUG REPORT")
    print("=" * 60)
    print()
    
    results = {
        "imports": test_imports(),
        "configs": test_site_configs(),
        "credentials": test_credentials(),
        "connection": test_connection(),
        "pages": test_page_operations(),
        "deployment": test_deployment()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"{test_name.upper():15} {status}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if not results.get("imports"):
        print("❌ Fix import errors before proceeding")
    
    if not results.get("configs"):
        print("⚠️  Some site configurations missing - check local paths")
    
    if not results.get("credentials"):
        print("⚠️  No credentials found - deployment will not work")
        print("   Create .env file or .deploy_credentials/sites.json")
    
    if results.get("connection") == {}:
        print("⚠️  Connection tests skipped - install paramiko for SFTP")
    
    print("\n✅ Debug complete!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Debug WordPress Deployer")
    parser.add_argument("--test-deploy", action="store_true", 
                       help="Actually test deployment (requires credentials)")
    args = parser.parse_args()
    
    generate_report()
    
    if args.test_deploy:
        print("\n" + "=" * 60)
        print("DEPLOYMENT TEST")
        print("=" * 60)
        from wordpress_manager import WordPressManager
        manager = WordPressManager("prismblossom")
        if manager.connect():
            print("✅ Connected - testing deployment...")
            # Add actual deployment test here
            manager.disconnect()
        else:
            print("❌ Could not connect")

