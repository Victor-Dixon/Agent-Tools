#!/usr/bin/env python3
"""
Verify Hostinger SFTP Credentials
==================================

Tests SFTP connection with different username formats and provides diagnostics.

Author: Agent-7 (Web Development Specialist)
"""

import os
import sys
from pathlib import Path

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False
    print("❌ paramiko not installed. Install with: pip install paramiko")

try:
    from dotenv import load_dotenv, find_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

def load_credentials():
    """Load credentials from .env."""
    if HAS_DOTENV:
        env_path = find_dotenv()
        if env_path:
            load_dotenv(env_path)
    
    host = os.getenv("HOSTINGER_HOST") or os.getenv("SSH_HOST")
    username = os.getenv("HOSTINGER_USER") or os.getenv("SSH_USER")
    password = os.getenv("HOSTINGER_PASS") or os.getenv("SSH_PASS")
    port_str = os.getenv("HOSTINGER_PORT") or os.getenv("SSH_PORT", "65002")
    
    try:
        port = int(port_str)
    except ValueError:
        port = 65002
    
    return {
        "host": host,
        "username": username,
        "password": password,
        "port": port
    }

def test_connection(host: str, username: str, password: str, port: int = 65002):
    """Test SFTP connection."""
    if not HAS_PARAMIKO:
        return False, "paramiko not installed"
    
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Try to list directory to verify connection
        sftp.listdir(".")
        
        sftp.close()
        transport.close()
        return True, "Connection successful!"
    except paramiko.AuthenticationException:
        return False, "Authentication failed - check username and password"
    except paramiko.SSHException as e:
        return False, f"SSH error: {str(e)}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def try_username_variations(base_username: str, domain: str = "freerideinvestor.com"):
    """Generate username variations to try."""
    variations = [
        base_username,  # Just username
        f"{base_username}@{domain}",  # username@domain
        f"{base_username}@hostinger.com",  # username@hostinger.com
        domain.split(".")[0],  # Domain name without extension
    ]
    
    # If base_username contains @, extract username part
    if "@" in base_username:
        username_part = base_username.split("@")[0]
        variations.insert(0, username_part)
        variations.append(f"{username_part}@{domain}")
    
    return list(set(variations))  # Remove duplicates

def main():
    """Main verification function."""
    print("=" * 60)
    print("🔍 Hostinger SFTP Credential Verification")
    print("=" * 60)
    print()
    
    if not HAS_PARAMIKO:
        print("❌ paramiko not installed")
        print("   Install with: pip install paramiko")
        return 1
    
    # Load credentials
    creds = load_credentials()
    
    if not all([creds["host"], creds["username"], creds["password"]]):
        print("❌ Missing credentials in .env:")
        if not creds["host"]:
            print("   - HOSTINGER_HOST")
        if not creds["username"]:
            print("   - HOSTINGER_USER")
        if not creds["password"]:
            print("   - HOSTINGER_PASS")
        return 1
    
    print("📋 Current Credentials:")
    print(f"   Host: {creds['host']}")
    print(f"   Port: {creds['port']}")
    print(f"   Username: {creds['username']}")
    print(f"   Password: {'*' * len(creds['password'])}")
    print()
    
    # Test with current credentials
    print("🔌 Testing connection with current credentials...")
    success, message = test_connection(
        creds["host"],
        creds["username"],
        creds["password"],
        creds["port"]
    )
    
    if success:
        print(f"✅ {message}")
        print()
        print("✅ Credentials are correct! Ready for deployment.")
        return 0
    else:
        print(f"❌ {message}")
        print()
        
        # Try username variations
        print("🔍 Trying username variations...")
        domain = "freerideinvestor.com"
        variations = try_username_variations(creds["username"], domain)
        
        for variation in variations:
            if variation == creds["username"]:
                continue  # Already tried
            
            print(f"   Trying: {variation}...", end=" ")
            success, msg = test_connection(
                creds["host"],
                variation,
                creds["password"],
                creds["port"]
            )
            
            if success:
                print(f"✅ SUCCESS!")
                print()
                print(f"✅ Correct username format: {variation}")
                print()
                print("💡 Update .env with:")
                print(f"   HOSTINGER_USER={variation}")
                return 0
            else:
                print(f"❌ {msg.split(' - ')[0] if ' - ' in msg else 'Failed'}")
        
        print()
        print("❌ All username variations failed")
        print()
        print("💡 Troubleshooting:")
        print("  1. Verify password is correct in Hostinger control panel")
        print("  2. Check if SFTP is enabled for your hosting account")
        print("  3. Verify host IP is correct (may vary by server)")
        print("  4. Try connecting via FTP client (FileZilla) to verify credentials")
        print("  5. Check Hostinger support documentation for SFTP username format")
        return 1

if __name__ == "__main__":
    sys.exit(main())




