#!/usr/bin/env python3
"""
Update FTP Credentials in .env File
===================================

Updates .env file with correct FTP credentials discovered from Hostinger.

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv, dotenv_values
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

# Correct credentials discovered from Hostinger
CORRECT_CREDENTIALS = {
    "HOSTINGER_HOST": "157.173.214.121",
    "HOSTINGER_PORT": "21",  # FTP port (not SFTP)
    "HOSTINGER_USER": "u996867598.freerideinvestor.com",
    # Password must be set/reset by user in Hostinger control panel
}


def find_env_file() -> Optional[Path]:
    """Find .env file in common locations."""
    locations = [
        Path("D:/Agent_Cellphone_V2_Repository/.env"),
        Path(".env"),
        Path("D:/websites/.env"),
    ]
    
    for env_path in locations:
        if env_path.exists():
            return env_path
    
    # Return default location if not found
    return Path("D:/Agent_Cellphone_V2_Repository/.env")


def update_env_file(env_path: Path, credentials: dict, password: Optional[str] = None) -> bool:
    """Update .env file with credentials."""
    # Read existing .env
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding='utf-8').split('\n')
    
    # Track which keys we've updated
    updated_keys = set()
    new_lines = []
    
    # Process existing lines
    for line in lines:
        stripped = line.strip()
        
        # Keep comments and empty lines
        if not stripped or stripped.startswith('#'):
            new_lines.append(line)
            continue
        
        # Check if this line contains a credential we need to update
        if '=' in stripped:
            key = stripped.split('=')[0].strip()
            
            # Update matching keys
            if key in credentials:
                new_lines.append(f"{key}={credentials[key]}")
                updated_keys.add(key)
            elif key in ["HOSTINGER_HOST", "SSH_HOST", "HOST"] and "HOSTINGER_HOST" in credentials:
                new_lines.append(f"HOSTINGER_HOST={credentials['HOSTINGER_HOST']}")
                updated_keys.add("HOSTINGER_HOST")
            elif key in ["HOSTINGER_PORT", "SSH_PORT", "PORT"] and "HOSTINGER_PORT" in credentials:
                new_lines.append(f"HOSTINGER_PORT={credentials['HOSTINGER_PORT']}")
                updated_keys.add("HOSTINGER_PORT")
            elif key in ["HOSTINGER_USER", "SSH_USER", "USERNAME"] and "HOSTINGER_USER" in credentials:
                new_lines.append(f"HOSTINGER_USER={credentials['HOSTINGER_USER']}")
                updated_keys.add("HOSTINGER_USER")
            elif key in ["HOSTINGER_PASS", "SSH_PASS", "PASSWORD"] and password:
                new_lines.append(f"HOSTINGER_PASS={password}")
                updated_keys.add("HOSTINGER_PASS")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add missing credentials
    if "HOSTINGER_HOST" not in updated_keys and "HOSTINGER_HOST" in credentials:
        new_lines.append(f"\n# Hostinger FTP Credentials (Updated 2025-12-02)")
        new_lines.append(f"HOSTINGER_HOST={credentials['HOSTINGER_HOST']}")
    
    if "HOSTINGER_PORT" not in updated_keys and "HOSTINGER_PORT" in credentials:
        new_lines.append(f"HOSTINGER_PORT={credentials['HOSTINGER_PORT']}")
    
    if "HOSTINGER_USER" not in updated_keys and "HOSTINGER_USER" in credentials:
        new_lines.append(f"HOSTINGER_USER={credentials['HOSTINGER_USER']}")
    
    if password and "HOSTINGER_PASS" not in updated_keys:
        new_lines.append(f"HOSTINGER_PASS={password}")
    elif "HOSTINGER_PASS" not in updated_keys:
        new_lines.append("# HOSTINGER_PASS=<set password via Hostinger control panel>")
    
    # Write updated .env
    env_path.write_text('\n'.join(new_lines), encoding='utf-8')
    return True


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update .env file with correct FTP credentials"
    )
    parser.add_argument(
        "--password",
        help="FTP password (or set via Hostinger control panel)"
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Path to .env file (auto-detected if not specified)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    
    args = parser.parse_args()
    
    # Find .env file
    env_path = args.env_file or find_env_file()
    
    if not env_path and not args.dry_run:
        print(f"❌ .env file not found. Creating at: {env_path}")
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text("")
    
    print(f"📝 Updating .env file: {env_path}")
    print("\n✅ Correct Credentials:")
    print(f"   Host: {CORRECT_CREDENTIALS['HOSTINGER_HOST']}")
    print(f"   Port: {CORRECT_CREDENTIALS['HOSTINGER_PORT']} (FTP)")
    print(f"   Username: {CORRECT_CREDENTIALS['HOSTINGER_USER']}")
    
    if args.password:
        print(f"   Password: {'*' * len(args.password)}")
    else:
        print("   Password: <not set - reset via Hostinger control panel>")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        return
    
    # Update .env file
    try:
        update_env_file(env_path, CORRECT_CREDENTIALS, args.password)
        print(f"\n✅ Successfully updated {env_path}")
        print("\n📋 Next Steps:")
        print("   1. If password is not set, reset it in Hostinger control panel:")
        print("      https://hpanel.hostinger.com/websites/freerideinvestor.com/files/ftp-accounts")
        print("   2. Test FTP connection:")
        print("      python tools/ftp_deployer.py --test")
        print("   3. Deploy files:")
        print("      python tools/ftp_deployer.py --deploy --file D:/websites/FreeRideInvestor/functions.php")
    except Exception as e:
        print(f"\n❌ Error updating .env file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

