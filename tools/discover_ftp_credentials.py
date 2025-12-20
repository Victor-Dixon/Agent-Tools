#!/usr/bin/env python3
"""
Discover FTP/SFTP Credentials for All Sites
============================================

Helps discover FTP credentials from Hostinger control panel for all sites.

Author: Agent-3 (Infrastructure & DevOps Specialist)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_sites_from_json() -> Dict[str, Dict]:
    """Load all sites from sites.json."""
    sites_file = Path(".deploy_credentials/sites.json")
    if not sites_file.exists():
        print("❌ sites.json not found!")
        return {}
    
    with open(sites_file) as f:
        return json.load(f)


def print_credential_guide():
    """Print step-by-step guide for finding FTP credentials."""
    print("\n" + "="*70)
    print("📋 HOW TO GET FTP/SFTP CREDENTIALS FROM HOSTINGER")
    print("="*70)
    print("\n1. Log into Hostinger Control Panel:")
    print("   👉 https://hpanel.hostinger.com/")
    print("\n2. For EACH domain, follow these steps:")
    print("   a) Click 'Websites' in the left menu")
    print("   b) Find your domain (e.g., ariajet.site)")
    print("   c) Click on the domain name")
    print("   d) Click 'Tools' tab")
    print("   e) Click 'FTP Account' or 'FTP Accounts'")
    print("   f) You'll see:")
    print("      • FTP Host (e.g., 157.173.214.121)")
    print("      • FTP Port (usually 21 for FTP, 22 for SFTP)")
    print("      • FTP Username (format: u{id}.{domain})")
    print("      • FTP Password (click 'Show' or 'Change' to see/reset)")
    print("\n3. Common Hostinger FTP Username Formats:")
    print("   • u{account_id}.{domain} (e.g., u996867598.freerideinvestor.com)")
    print("   • {cpanel_username} (cPanel username)")
    print("   • {email_prefix} (less common)")
    print("\n4. Port Numbers:")
    print("   • Port 21 = Standard FTP")
    print("   • Port 22 = SFTP (Secure FTP)")
    print("   • Port 65002 = Hostinger SFTP (alternative)")
    print("\n5. Host Address:")
    print("   • Usually: 157.173.214.121 (or similar IP)")
    print("   • Sometimes: ftp.{domain} or {domain}")
    print("   • Check in Hostinger FTP Account page")
    print("\n" + "="*70)


def print_sites_needing_credentials():
    """Print all sites that need credentials."""
    sites = get_sites_from_json()
    
    print("\n" + "="*70)
    print("📋 SITES IN sites.json - CREDENTIAL STATUS")
    print("="*70)
    
    sites_needing_creds = []
    sites_with_creds = []
    
    for site_name, config in sorted(sites.items()):
        host = config.get("host", "").strip()
        username = config.get("username", "").strip()
        password = config.get("password", "").strip()
        port = config.get("port", 21)
        remote_path = config.get("remote_path", "")
        
        has_creds = bool(host and username and password)
        
        status = "✅ COMPLETE" if has_creds else "❌ NEEDS CREDENTIALS"
        
        print(f"\n🔹 {site_name}")
        print(f"   Status: {status}")
        print(f"   Host: {host if host else '(empty)'}")
        print(f"   Username: {username if username else '(empty)'}")
        print(f"   Password: {'***' if password else '(empty)'}")
        print(f"   Port: {port}")
        print(f"   Remote Path: {remote_path}")
        
        if has_creds:
            sites_with_creds.append(site_name)
        else:
            sites_needing_creds.append(site_name)
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"✅ Sites with credentials: {len(sites_with_creds)}")
    print(f"   {', '.join(sites_with_creds) if sites_with_creds else 'None'}")
    print(f"\n❌ Sites needing credentials: {len(sites_needing_creds)}")
    print(f"   {', '.join(sites_needing_creds) if sites_needing_creds else 'None'}")
    print("\n" + "="*70)


def generate_hostinger_links():
    """Generate direct links to Hostinger FTP pages for each site."""
    sites = get_sites_from_json()
    
    print("\n" + "="*70)
    print("🔗 DIRECT LINKS TO HOSTINGER FTP PAGES")
    print("="*70)
    print("\nNote: Replace {domain} with actual domain name")
    print("\nBase URL: https://hpanel.hostinger.com/websites/{domain}/files/ftp-accounts")
    print("\nFor each site, navigate to:")
    
    unique_domains = set()
    for site_name in sites.keys():
        # Extract domain from site name
        domain = site_name.replace(".com", "").replace(".site", "").replace(".online", "")
        if "." in site_name:
            domain = site_name
        unique_domains.add(domain)
    
    for domain in sorted(unique_domains):
        print(f"\n  • {domain}:")
        print(f"    https://hpanel.hostinger.com/websites/{domain}/files/ftp-accounts")
    
    print("\n" + "="*70)


def test_credentials(site_name: str, host: str, username: str, password: str, port: int) -> bool:
    """Test FTP credentials."""
    try:
        from ftplib import FTP
        from ftplib import error_perm, error_temp
        
        print(f"\n🔍 Testing credentials for {site_name}...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Username: {username}")
        
        ftp = FTP()
        ftp.connect(host, port, timeout=TimeoutConstants.HTTP_SHORT)
        ftp.login(username, password)
        ftp.quit()
        
        print(f"✅ Connection successful!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def main():
    """Main CLI interface."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(description="Discover and verify FTP credentials")
    parser.add_argument("--guide", action="store_true", help="Show credential discovery guide")
    parser.add_argument("--status", action="store_true", help="Show credential status for all sites")
    parser.add_argument("--links", action="store_true", help="Generate Hostinger FTP links")
    parser.add_argument("--test", type=str, help="Test credentials for a specific site")
    parser.add_argument("--host", type=str, help="FTP host for testing")
    parser.add_argument("--username", type=str, help="FTP username for testing")
    parser.add_argument("--password", type=str, help="FTP password for testing")
    parser.add_argument("--port", type=int, default=21, help="FTP port (default: 21)")
    
    args = parser.parse_args()
    
    if args.guide:
        print_credential_guide()
    
    if args.status:
        print_sites_needing_credentials()
    
    if args.links:
        generate_hostinger_links()
    
    if args.test:
        if not all([args.host, args.username, args.password]):
            print("❌ Error: --host, --username, and --password required for testing")
            return
        
        test_credentials(args.test, args.host, args.username, args.password, args.port)
    
    if not any([args.guide, args.status, args.links, args.test]):
        # Show all by default
        print_credential_guide()
        print_sites_needing_credentials()
        generate_hostinger_links()
        
        print("\n💡 TIP: Use --guide, --status, or --links for specific information")
        print("   Use --test to verify credentials before adding to sites.json")


if __name__ == "__main__":
    main()





