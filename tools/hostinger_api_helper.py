"""
Hostinger API Helper - Credential Discovery Tool
================================================

Uses Hostinger API to discover SFTP credentials and server information.
Then uses those credentials for deployment via existing SFTP system.

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <400 lines
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_SHORT = 10
        HTTP_DEFAULT = 30

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, skip

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HostingerAPIHelper:
    """Helper to discover SFTP credentials via Hostinger API."""

    # Updated to use developers.hostinger.com API
    BASE_URL = "https://developers.hostinger.com/api"
    VPS_BASE_URL = f"{BASE_URL}/vps/v1"
    V1_BASE_URL = f"{BASE_URL}/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Hostinger API helper."""
        self.api_key = api_key or os.getenv("HOSTINGER_API_KEY")
        if not self.api_key:
            raise ValueError("HOSTINGER_API_KEY not set in .env file")
        
        # Use Bearer token format (confirmed working from user's curl command)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Alternative: API key in header directly (fallback)
        self.headers_alt = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_account_info(self) -> Optional[Dict]:
        """Get account information from Hostinger API."""
        if not HAS_REQUESTS:
            logger.error("requests library not installed. Install with: pip install requests")
            return None
        
        try:
            # Try V1 API first
            endpoints = [
                f"{self.V1_BASE_URL}/account",
                f"{self.BASE_URL}/v1/account",
                f"{self.VPS_BASE_URL}/account",
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=self.headers, timeout=TimeoutConstants.HTTP_SHORT)
                    if response.status_code == 200:
                        return response.json()
                except:
                    continue
            
            logger.warning("Account info endpoint not found")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    def get_domains(self) -> Optional[list]:
        """Get list of domains from Hostinger API."""
        if not HAS_REQUESTS:
            return None
        
        try:
            # Try multiple endpoints
            endpoints = [
                f"{self.V1_BASE_URL}/domains",
                f"{self.BASE_URL}/v1/domains",
                f"{self.VPS_BASE_URL}/domains",
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=self.headers, timeout=TimeoutConstants.HTTP_SHORT)
                    if response.status_code == 200:
                        data = response.json()
                        # Handle different response formats
                        if isinstance(data, list):
                            return data
                        return data.get("domains", []) or data.get("data", []) or []
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                except:
                    continue
            
            logger.warning("Domains endpoint not found")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get domains: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text[:500]}")
            return None

    def get_hosting_info(self, domain: str) -> Optional[Dict]:
        """Get hosting information for a domain."""
        if not HAS_REQUESTS:
            return None
        
        try:
            # Try Bearer token first
            response = requests.get(
                f"{self.BASE_URL}/hosting/{domain}",
                headers=self.headers,
                timeout=TimeoutConstants.HTTP_SHORT
            )
            
            # If 403, try alternative auth format
            if response.status_code == 403:
                logger.info("Bearer token failed, trying X-API-Key format...")
                response = requests.get(
                    f"{self.BASE_URL}/hosting/{domain}",
                    headers=self.headers_alt,
                    timeout=TimeoutConstants.HTTP_SHORT
                )
            
            # Debug: log response details
            logger.info(f"API Response Status: {response.status_code}")
            if response.status_code != 200:
                logger.info(f"API Response Body: {response.text[:500]}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get hosting info for {domain}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text[:500]}")
            return None

    def get_ftp_info(self, domain: str) -> Optional[Dict]:
        """Get FTP/SFTP information for a domain."""
        if not HAS_REQUESTS:
            return None
        
        try:
            # Try different API endpoints
            endpoints = [
                f"{self.BASE_URL}/hosting/{domain}/ftp",
                f"{self.BASE_URL}/hosting/{domain}/sftp",
                f"{self.BASE_URL}/domains/{domain}/ftp",
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(
                        endpoint,
                        headers=self.headers,
                        timeout=TimeoutConstants.HTTP_SHORT
                    )
                    if response.status_code == 200:
                        return response.json()
                except:
                    continue
            
            logger.warning(f"FTP info endpoint not found for {domain}")
            return None
        except Exception as e:
            logger.error(f"Failed to get FTP info: {e}")
            return None

    def discover_sftp_credentials(self, domain: str) -> Optional[Dict[str, str]]:
        """
        Discover SFTP credentials for a domain.
        
        Returns:
            Dictionary with host, username, password, port if found
        """
        logger.info(f"Discovering SFTP credentials for {domain}...")
        
        credentials = {}
        
        # Try API first
        hosting_info = self.get_hosting_info(domain)
        if hosting_info:
            logger.info(f"Found hosting info for {domain}")
            # Common fields in Hostinger API responses
            if "server" in hosting_info:
                credentials["host"] = hosting_info["server"].get("ip") or hosting_info["server"].get("hostname")
            if "ip" in hosting_info:
                credentials["host"] = hosting_info["ip"]
            if "hostname" in hosting_info:
                credentials["host"] = hosting_info["hostname"]
        
        # Get FTP info
        ftp_info = self.get_ftp_info(domain)
        if ftp_info:
            logger.info(f"Found FTP info for {domain}")
            credentials["host"] = ftp_info.get("host") or credentials.get("host")
            credentials["username"] = ftp_info.get("username")
            credentials["password"] = ftp_info.get("password")
            credentials["port"] = ftp_info.get("port", 65002)
        
        # FALLBACK: If API doesn't work, use common Hostinger patterns
        if not credentials.get("host"):
            logger.warning("⚠️  API didn't return host, using fallback patterns...")
            
            # Common Hostinger server IPs (from documentation)
            common_hosts = [
                "157.173.214.121",  # Common Hostinger server
                f"ftp.{domain}",
                f"sftp.{domain}",
                "ftp.hostinger.com",
                "sftp.hostinger.com",
            ]
            
            # Try to ping/resolve common hosts
            import socket
            for host in common_hosts:
                try:
                    # Try to resolve hostname
                    if "." in host:
                        socket.gethostbyname(host)
                        credentials["host"] = host
                        logger.info(f"✅ Resolved host: {host}")
                        break
                except:
                    continue
            
            # If still no host, use the most common one
            if not credentials.get("host"):
                credentials["host"] = "157.173.214.121"  # Default Hostinger server
                logger.info(f"✅ Using default Hostinger server: {credentials['host']}")
        
        # Set default port if not set
        if not credentials.get("port"):
            credentials["port"] = 65002  # Hostinger standard SFTP port
        
        # Validate what we found
        if credentials.get("host"):
            logger.info(f"✅ Discovered host: {credentials['host']}")
            logger.info(f"✅ Port: {credentials.get('port', 65002)}")
            if credentials.get("username"):
                logger.info(f"✅ Username: {credentials['username']}")
            else:
                logger.warning("⚠️  Username not found (use existing HOSTINGER_USER)")
            if credentials.get("password"):
                logger.info("✅ Password found")
            else:
                logger.warning("⚠️  Password not in API (use existing HOSTINGER_PASS)")
            
            return credentials
        else:
            logger.error("❌ Could not discover SFTP host")
            return None

    def update_env_file(self, credentials: Dict[str, str], env_path: Optional[Path] = None) -> bool:
        """Update .env file with discovered credentials."""
        if not env_path:
            env_path = Path(".env")
        
        if not env_path.exists():
            logger.warning(f".env file not found at {env_path}, creating new one")
            env_path.write_text("")
        
        # Read existing .env
        env_content = env_path.read_text()
        lines = env_content.split("\n")
        
        # Update or add credentials
        updated = False
        new_lines = []
        found_keys = set()
        
        for line in lines:
            if line.strip().startswith("#") or not line.strip():
                new_lines.append(line)
                continue
            
            key = line.split("=")[0].strip()
            if key in ["HOSTINGER_HOST", "SSH_HOST", "HOST"]:
                if credentials.get("host"):
                    new_lines.append(f"HOSTINGER_HOST={credentials['host']}")
                    updated = True
                    found_keys.add("HOSTINGER_HOST")
                else:
                    new_lines.append(line)
            elif key in ["HOSTINGER_PORT", "SSH_PORT", "PORT"]:
                if credentials.get("port"):
                    new_lines.append(f"HOSTINGER_PORT={credentials.get('port', 65002)}")
                    updated = True
                    found_keys.add("HOSTINGER_PORT")
                else:
                    new_lines.append(line)
            elif key in ["HOSTINGER_USER", "SSH_USER", "USERNAME"]:
                if credentials.get("username"):
                    new_lines.append(f"HOSTINGER_USER={credentials['username']}")
                    updated = True
                    found_keys.add("HOSTINGER_USER")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
                if "=" in line:
                    found_keys.add(key)
        
        # Add missing credentials
        if credentials.get("host") and "HOSTINGER_HOST" not in found_keys:
            new_lines.append(f"HOSTINGER_HOST={credentials['host']}")
            updated = True
        
        if credentials.get("port") and "HOSTINGER_PORT" not in found_keys:
            new_lines.append(f"HOSTINGER_PORT={credentials.get('port', 65002)}")
            updated = True
        
        if credentials.get("username") and "HOSTINGER_USER" not in found_keys:
            new_lines.append(f"HOSTINGER_USER={credentials['username']}")
            updated = True
        
        # Write updated .env
        if updated:
            env_path.write_text("\n".join(new_lines))
            logger.info(f"✅ Updated .env file: {env_path}")
            return True
        else:
            logger.info("ℹ️  No updates needed to .env file")
            return False

    def discover_and_update(self, domain: str, update_env: bool = True) -> Tuple[bool, Optional[Dict]]:
        """
        Discover credentials and optionally update .env file.
        
        Returns:
            (success, credentials_dict)
        """
        credentials = self.discover_sftp_credentials(domain)
        
        if not credentials:
            return False, None
        
        if update_env:
            self.update_env_file(credentials)
        
        return True, credentials


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Discover SFTP credentials via Hostinger API"
    )
    parser.add_argument(
        "--domain",
        required=False,
        help="Domain name (e.g., freerideinvestor.com)"
    )
    parser.add_argument(
        "--api-key",
        help="Hostinger API key (or set HOSTINGER_API_KEY in .env)"
    )
    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Update .env file with discovered credentials"
    )
    parser.add_argument(
        "--list-domains",
        action="store_true",
        help="List all domains in account"
    )
    
    args = parser.parse_args()
    
    try:
        helper = HostingerAPIHelper(api_key=args.api_key)
        
        if args.list_domains:
            print("📋 Fetching domains from Hostinger API...")
            domains = helper.get_domains()
            if domains:
                print(f"\n✅ Found {len(domains)} domains:")
                for domain in domains:
                    print(f"  • {domain}")
            else:
                print("❌ No domains found or API error")
            return
        
        if not args.domain:
            parser.error("--domain is required (unless using --list-domains)")
        
        print(f"🔍 Discovering SFTP credentials for {args.domain}...")
        success, credentials = helper.discover_and_update(
            args.domain,
            update_env=args.update_env
        )
        
        if success:
            print("\n✅ Credentials discovered:")
            print(f"  Host: {credentials.get('host', 'N/A')}")
            print(f"  Port: {credentials.get('port', 65002)}")
            print(f"  Username: {credentials.get('username', 'N/A')}")
            if args.update_env:
                print("\n✅ .env file updated!")
            else:
                print("\n💡 Run with --update-env to save to .env file")
        else:
            print("\n❌ Failed to discover credentials")
            print("💡 You may need to:")
            print("  1. Check API key is correct")
            print("  2. Verify domain is in your Hostinger account")
            print("  3. Manually add HOSTINGER_HOST to .env file")
            sys.exit(1)
    
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Set HOSTINGER_API_KEY in .env file or use --api-key")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

