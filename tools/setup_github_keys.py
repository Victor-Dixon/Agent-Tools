#!/usr/bin/env python3
"""
GitHub Keys Setup Tool
======================

Uses GitHub API to programmatically add SSH and GPG keys to your GitHub account.

This is useful for:
- Setting up new GitHub accounts
- Automating key management
- Bulk key operations

Author: Agent-1 (Integration & Core Systems Specialist)
Created: 2025-12-09
License: MIT
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import subprocess
from typing import Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("❌ requests library required. Install with: pip install requests")

from dotenv import load_dotenv
load_dotenv()

# Try to use SSOT github_utils if available
try:
    from src.core.utils.github_utils import get_github_token as get_github_token_ssot
    USE_SSOT = True
except ImportError:
    USE_SSOT = False


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or .env file."""
    # Priority order:
    # 1. New professional development account token
    # 2. Standard GITHUB_TOKEN
    # 3. SSOT utility (if available)
    # 4. Direct .env reading
    
    # Try new professional development account token first
    token = os.getenv("FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN")
    if token:
        return token
    
    # Try standard GITHUB_TOKEN
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    
    # Try SSOT if available
    if USE_SSOT:
        try:
            token = get_github_token_ssot(project_root)
            if token:
                return token
        except Exception:
            pass
    
    # Fallback to direct .env reading
    env_file = project_root / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                # Try new token first
                if line.startswith("FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
                # Then standard token
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    
    return None


def read_ssh_key(key_path: str) -> Optional[str]:
    """Read SSH public key from file."""
    try:
        key_file = Path(key_path)
        if not key_file.exists():
            print(f"❌ SSH key file not found: {key_path}")
            return None
        
        with open(key_file, "r") as f:
            key_content = f.read().strip()
        
        # Validate it's a public key
        if not key_content.startswith(("ssh-rsa", "ssh-ed25519", "ecdsa-sha2", "ssh-dss")):
            print(f"❌ Invalid SSH public key format: {key_path}")
            return None
        
        return key_content
    except Exception as e:
        print(f"❌ Error reading SSH key: {e}")
        return None


def read_gpg_key(key_path: str) -> Optional[str]:
    """Read GPG public key from file."""
    try:
        key_file = Path(key_path)
        if not key_file.exists():
            print(f"❌ GPG key file not found: {key_path}")
            return None
        
        with open(key_file, "r") as f:
            key_content = f.read().strip()
        
        # Validate it's a GPG key
        if not key_content.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----"):
            print(f"❌ Invalid GPG public key format: {key_path}")
            return None
        
        return key_content
    except Exception as e:
        print(f"❌ Error reading GPG key: {e}")
        return None


def generate_ssh_key(key_path: str, key_type: str = "ed25519") -> bool:
    """Generate a new SSH key pair."""
    try:
        key_file = Path(key_path)
        if key_file.exists():
            print(f"⚠️ SSH key already exists: {key_path}")
            response = input("Overwrite? (y/N): ").strip().lower()
            if response != "y":
                return False
        
        # Generate SSH key
        print(f"🔑 Generating {key_type} SSH key pair...")
        result = subprocess.run(
            ["ssh-keygen", "-t", key_type, "-f", str(key_path), "-N", "", "-C", "github-setup"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ SSH key generated: {key_path}")
            print(f"   Public key: {key_path}.pub")
            return True
        else:
            print(f"❌ Failed to generate SSH key: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ ssh-keygen not found. Install OpenSSH to generate keys.")
        return False
    except Exception as e:
        print(f"❌ Error generating SSH key: {e}")
        return False


def add_ssh_key_to_github(token: str, key_content: str, title: str) -> bool:
    """Add SSH key to GitHub account via API."""
    if not REQUESTS_AVAILABLE:
        print("❌ requests library required")
        return False
    
    url = "https://api.github.com/user/keys"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "title": title,
        "key": key_content
    }
    
    try:
        print(f"📤 Adding SSH key '{title}' to GitHub...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 201:
            key_info = response.json()
            print(f"✅ SSH key added successfully!")
            print(f"   ID: {key_info.get('id')}")
            print(f"   Title: {key_info.get('title')}")
            print(f"   Key: {key_info.get('key', '')[:50]}...")
            return True
        else:
            error_msg = response.json().get("message", "Unknown error")
            print(f"❌ Failed to add SSH key: {error_msg}")
            if response.status_code == 401:
                print("   → Check if token has 'write:public_key' scope")
                print("   → For fine-grained tokens, ensure 'Public SSH keys' permission is granted")
            elif response.status_code == 403:
                print("   → Token may not have required permissions")
                print("   → For fine-grained tokens:")
                print("     - Go to: https://github.com/settings/tokens")
                print("     - Edit your token")
                print("     - Under 'Account permissions' → 'Public SSH keys' → Set to 'Read and write'")
            elif response.status_code == 422:
                print("   → Key might already exist or be invalid")
            return False
    except Exception as e:
        print(f"❌ Error adding SSH key: {e}")
        return False


def add_gpg_key_to_github(token: str, key_content: str, name: str = "GPG Key") -> bool:
    """Add GPG key to GitHub account via API."""
    if not REQUESTS_AVAILABLE:
        print("❌ requests library required")
        return False
    
    url = "https://api.github.com/user/gpg_keys"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "name": name,
        "armored_public_key": key_content
    }
    
    try:
        print(f"📤 Adding GPG key '{name}' to GitHub...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 201:
            key_info = response.json()
            print(f"✅ GPG key added successfully!")
            print(f"   ID: {key_info.get('id')}")
            print(f"   Name: {key_info.get('name')}")
            return True
        else:
            error_msg = response.json().get("message", "Unknown error")
            print(f"❌ Failed to add GPG key: {error_msg}")
            if response.status_code == 401:
                print("   → Check if token has 'write:gpg_key' scope")
                print("   → For fine-grained tokens, ensure 'GPG keys' permission is granted")
            elif response.status_code == 403:
                print("   → Token may not have required permissions")
                print("   → For fine-grained tokens:")
                print("     - Go to: https://github.com/settings/tokens")
                print("     - Edit your token")
                print("     - Under 'Account permissions' → 'GPG keys' → Set to 'Read and write'")
            elif response.status_code == 422:
                print("   → Key might already exist or be invalid")
            return False
    except Exception as e:
        print(f"❌ Error adding GPG key: {e}")
        return False


def list_github_keys(token: str, key_type: str = "ssh") -> bool:
    """List SSH or GPG keys on GitHub account."""
    if not REQUESTS_AVAILABLE:
        print("❌ requests library required")
        return False
    
    if key_type == "ssh":
        url = "https://api.github.com/user/keys"
    elif key_type == "gpg":
        url = "https://api.github.com/user/gpg_keys"
    else:
        print(f"❌ Invalid key type: {key_type} (use 'ssh' or 'gpg')")
        return False
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    try:
        print(f"📋 Listing {key_type.upper()} keys on GitHub...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            keys = response.json()
            if keys:
                print(f"\n✅ Found {len(keys)} {key_type.upper()} key(s):")
                for key in keys:
                    if key_type == "ssh":
                        print(f"   - {key.get('title')} (ID: {key.get('id')})")
                        print(f"     Key: {key.get('key', '')[:50]}...")
                    else:
                        print(f"   - {key.get('name')} (ID: {key.get('id')})")
                    print()
            else:
                print(f"   No {key_type.upper()} keys found")
            return True
        else:
            error_msg = response.json().get("message", "Unknown error")
            print(f"❌ Failed to list keys: {error_msg}")
            if response.status_code == 403:
                print("   → Token may not have required permissions")
                print("   → For fine-grained tokens:")
                print("     - Go to: https://github.com/settings/tokens")
                print("     - Edit your token")
                if key_type == "ssh":
                    print("     - Under 'Account permissions' → 'Public SSH keys' → Set to 'Read' or 'Read and write'")
                else:
                    print("     - Under 'Account permissions' → 'GPG keys' → Set to 'Read' or 'Read and write'")
            return False
    except Exception as e:
        print(f"❌ Error listing keys: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("🔑 GITHUB KEYS SETUP TOOL")
    print("=" * 60)
    print()
    
    # Check for requests library
    if not REQUESTS_AVAILABLE:
        print("❌ requests library required")
        print("   Install with: pip install requests")
        return 1
    
    # Get GitHub token
    token = get_github_token()
    if not token:
        print("❌ GitHub token not found")
        print()
        print("💡 Setup options:")
        print("   1. Set FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN environment variable")
        print("   2. Set GITHUB_TOKEN environment variable")
        print("   3. Add FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN=your_token to .env file")
        print("   4. Add GITHUB_TOKEN=your_token to .env file")
        print()
        print("📋 Required token scopes:")
        print("   - write:public_key (for SSH keys)")
        print("   - write:gpg_key (for GPG keys)")
        print()
        print("🔗 Create token at: https://github.com/settings/tokens")
        return 1
    
    # Detect which token was used
    token_source = "unknown"
    if os.getenv("FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN"):
        token_source = "FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN"
    elif os.getenv("GITHUB_TOKEN"):
        token_source = "GITHUB_TOKEN"
    else:
        token_source = ".env file"
    
    print(f"✅ GitHub token found: {token[:10]}... (from {token_source})")
    print()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Setup SSH and GPG keys on GitHub")
    parser.add_argument("--ssh-key", help="Path to SSH public key file")
    parser.add_argument("--gpg-key", help="Path to GPG public key file")
    parser.add_argument("--ssh-title", default="Auto-generated SSH Key", help="Title for SSH key")
    parser.add_argument("--gpg-name", default="Auto-generated GPG Key", help="Name for GPG key")
    parser.add_argument("--generate-ssh", help="Generate new SSH key at this path")
    parser.add_argument("--list-ssh", action="store_true", help="List SSH keys on GitHub")
    parser.add_argument("--list-gpg", action="store_true", help="List GPG keys on GitHub")
    
    args = parser.parse_args()
    
    success = True
    
    # List keys if requested
    if args.list_ssh:
        list_github_keys(token, "ssh")
    
    if args.list_gpg:
        list_github_keys(token, "gpg")
    
    # Generate SSH key if requested
    if args.generate_ssh:
        if generate_ssh_key(args.generate_ssh):
            # Auto-add the generated key
            pub_key_path = f"{args.generate_ssh}.pub"
            key_content = read_ssh_key(pub_key_path)
            if key_content:
                success = add_ssh_key_to_github(token, key_content, args.ssh_title) and success
    
    # Add SSH key if provided
    if args.ssh_key:
        key_content = read_ssh_key(args.ssh_key)
        if key_content:
            success = add_ssh_key_to_github(token, key_content, args.ssh_title) and success
    
    # Add GPG key if provided
    if args.gpg_key:
        key_content = read_gpg_key(args.gpg_key)
        if key_content:
            success = add_gpg_key_to_github(token, key_content, args.gpg_name) and success
    
    # If no actions specified, show help
    if not any([args.ssh_key, args.gpg_key, args.generate_ssh, args.list_ssh, args.list_gpg]):
        parser.print_help()
        print()
        print("💡 Examples:")
        print("   # Add existing SSH key")
        print("   python tools/setup_github_keys.py --ssh-key ~/.ssh/id_ed25519.pub")
        print()
        print("   # Generate and add new SSH key")
        print("   python tools/setup_github_keys.py --generate-ssh ~/.ssh/github_key")
        print()
        print("   # Add GPG key")
        print("   python tools/setup_github_keys.py --gpg-key ~/.gnupg/public_key.asc")
        print()
        print("   # List existing keys")
        print("   python tools/setup_github_keys.py --list-ssh --list-gpg")
        return 0
    
    print()
    if success:
        print("=" * 60)
        print("✅ SETUP COMPLETE!")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("❌ SOME OPERATIONS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

