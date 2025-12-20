#!/usr/bin/env python3
"""
FTP Deployer - WordPress File Deployment Tool
==============================================

Deploys files to WordPress sites via FTP (port 21).
Uses Python's ftplib for reliable FTP connections.

<!-- SSOT Domain: infrastructure -->

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <400 lines
"""

import json
import logging
import os
import sys
import time
from ftplib import FTP, error_perm, error_temp
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from dotenv import load_dotenv, dotenv_values
    env_vars = dotenv_values(".env")
    for key, value in env_vars.items():
        if value and key not in os.environ:
            os.environ[key] = value
    load_dotenv()
except ImportError:
    pass

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_SHORT = 10
        HTTP_QUICK = 5
        HTTP_DEFAULT = 30

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class FTPDeployer:
    """FTP deployment manager for WordPress files."""
    
    def __init__(self, host: Optional[str] = None, username: Optional[str] = None,
                 password: Optional[str] = None, port: Optional[int] = None, site: Optional[str] = None):
        """Initialize FTP deployer with credentials."""
        # Load site-specific credentials if site is provided
        if site:
            site_creds = self._load_site_credentials(site)
            if site_creds:
                host = host or site_creds.get("host")
                username = username or site_creds.get("username")
                password = password or site_creds.get("password")
                port = port or site_creds.get("port")
        
        # Fallback to .env shared credentials
        self.host = host or os.getenv(
            "HOSTINGER_HOST") or os.getenv("SSH_HOST")
        self.username = username or os.getenv(
            "HOSTINGER_USER") or os.getenv("SSH_USER")
        self.password = password or os.getenv(
            "HOSTINGER_PASS") or os.getenv("SSH_PASS")
        
        # Parse port
        if port:
            self.port = int(port)
        else:
            port_str = os.getenv(
                "HOSTINGER_PORT") or os.getenv("SSH_PORT", "21")
            try:
                self.port = int(port_str)
            except ValueError:
                self.port = 21
        
        self.ftp: Optional[FTP] = None
        self.connected = False
    
    def _load_site_credentials(self, site: str) -> Optional[Dict]:
        """Load site-specific credentials from sites.json."""
        sites_json = Path(".deploy_credentials/sites.json")
        if not sites_json.exists():
            return None
        
        try:
            with open(sites_json) as f:
                sites_data = json.load(f)
            
            # Try exact match first
            site_data = sites_data.get(site)
            if site_data and site_data.get("host"):
                return site_data
            
            # Try variations
            for key, data in sites_data.items():
                if key.lower() == site.lower() or key.replace(".", "") == site.replace(".", ""):
                    if data.get("host"):
                        return data
        except Exception as e:
            logger.debug(f"Could not load site credentials: {e}")
        
        return None
    
    def connect(self, max_retries: int = 3, base_delay: float = 1.0) -> bool:
        """
        Connect to FTP server with retry logic.
        
        Returns:
            True if connection successful
        """
        if not self.host or not self.username or not self.password:
            missing = []
            if not self.host:
                missing.append("HOSTINGER_HOST")
            if not self.username:
                missing.append("HOSTINGER_USER")
            if not self.password:
                missing.append("HOSTINGER_PASS")
            logger.error(f"Missing credentials: {', '.join(missing)}")
            logger.error("Run: python tools/update_ftp_credentials.py")
            return False
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"Connecting to FTP server (attempt {attempt}/{max_retries})",
                    extra={
                        "host": self.host,
                        "port": self.port,
                        "username": self.username,
                    }
                )
                
                # Create FTP connection
                self.ftp = FTP()
                self.ftp.connect(self.host, self.port,
                                 timeout=TimeoutConstants.HTTP_SHORT)
                
                # Login
                self.ftp.login(self.username, self.password)
                
                # Set passive mode (required for most firewalls)
                self.ftp.set_pasv(True)
                
                # Test connection by getting current directory
                self.ftp.pwd()
                
                self.connected = True
                logger.info(
                    f"✅ Connected to {self.host}:{self.port} as {self.username}")
                return True
                
            except error_perm as e:
                error_msg = str(e)
                if "530" in error_msg or "Login incorrect" in error_msg:
                    logger.error(
                        f"❌ Authentication failed for {self.username}@{self.host}")
                    logger.error("Please verify:")
                    logger.error(
                        "  1. Username is correct (format: u{id}.{domain})")
                    logger.error(
                        "  2. Password is correct (reset in Hostinger if needed)")
                    logger.error(
                        "  3. FTP is enabled on your Hostinger account")
                    return False
                else:
                    logger.error(f"❌ Permission error: {e}")
                    if attempt == max_retries:
                        return False
                    time.sleep(base_delay * attempt)
                    continue
                    
            except (error_temp, OSError) as e:
                logger.warning(
                    f"⚠️  Connection error (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    logger.error(
                        f"❌ Failed to connect after {max_retries} attempts")
                    return False
                time.sleep(base_delay * attempt)
                continue
                
            except Exception as e:
                logger.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
                if attempt == max_retries:
                    return False
                time.sleep(base_delay * attempt)
                continue
        
        return False
    
    def disconnect(self):
        """Close FTP connection."""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                try:
                    self.ftp.close()
                except:
                    pass
            self.ftp = None
        self.connected = False
    
    def ensure_directory(self, remote_path: str) -> bool:
        """Ensure remote directory exists, creating if needed."""
        if not self.connected or not self.ftp:
            return False
        
        try:
            # Split path into components
            parts = [p for p in remote_path.split('/') if p]
            current_path = '/'
            
            # Navigate/create each directory
            for part in parts:
                current_path = f"{current_path}{part}/" if current_path != '/' else f"/{part}/"
                try:
                    self.ftp.cwd(current_path)
                except error_perm:
                    # Directory doesn't exist, create it
                    try:
                        self.ftp.mkd(current_path.rstrip('/'))
                        self.ftp.cwd(current_path)
                    except error_perm as e:
                        logger.error(
                            f"Failed to create directory {current_path}: {e}")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error ensuring directory {remote_path}: {e}")
            return False
    
    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """
        Upload file to FTP server.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path (e.g., /public_html/wp-content/themes/theme/functions.php)
        
        Returns:
            True if successful
        """
        if not self.connected or not self.ftp:
            if not self.connect():
                return False
        
        if not local_path.exists():
            logger.error(f"❌ Local file not found: {local_path}")
            return False
        
        try:
            # Ensure remote directory exists
            remote_dir = '/'.join(remote_path.split('/')[:-1])
            if remote_dir:
                if not self.ensure_directory(remote_dir):
                    logger.error(
                        f"❌ Failed to create remote directory: {remote_dir}")
                    return False
            
            # Change to remote directory
            if remote_dir:
                self.ftp.cwd(remote_dir)
            
            # Upload file
            remote_filename = remote_path.split('/')[-1]
            logger.info(f"📤 Uploading {local_path.name} to {remote_path}")
            
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_filename}', f)
            
            logger.info(f"✅ Successfully uploaded {remote_path}")
            return True
            
        except error_perm as e:
            logger.error(f"❌ Permission error uploading {remote_path}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"❌ Error uploading {remote_path}: {type(e).__name__}: {e}")
            return False
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test FTP connection and return status."""
        if not self.connect():
            return False, "Connection failed"
        
        try:
            # List current directory
            files = self.ftp.nlst()
            return True, f"Connected successfully. Found {len(files)} items in root directory."
        except Exception as e:
            return False, f"Connection test failed: {e}"
        finally:
            self.disconnect()


def load_site_configs() -> Dict[str, Dict]:
    """Load site configurations from multiple sources."""
    configs = {}
    
    # Default site configurations (from wordpress_manager.py)
    default_configs = {
        "southwestsecret": {
            "local_path": "D:/websites/southwestsecret.com",
            "theme_name": "southwestsecret",
            "remote_base": "/public_html/wp-content/themes/southwestsecret",
            "functions_path": "/public_html/wp-content/themes/southwestsecret/functions.php",
        },
        "prismblossom": {
            "local_path": "D:/websites/prismblossom.online",
            "theme_name": "prismblossom",
            "remote_base": "/public_html/wp-content/themes/prismblossom",
            "functions_path": "/public_html/wp-content/themes/prismblossom/functions.php",
        },
        "prismblossom.online": {
            "local_path": "D:/websites/prismblossom.online",
            "theme_name": "prismblossom",
            "remote_base": "/public_html/wp-content/themes/prismblossom",
            "functions_path": "/public_html/wp-content/themes/prismblossom/functions.php",
        },
        "freerideinvestor": {
            "local_path": "D:/websites/FreeRideInvestor",
            "theme_name": "freerideinvestor",
            "remote_base": "/public_html/wp-content/themes/freerideinvestor",
            "functions_path": "/public_html/wp-content/themes/freerideinvestor/functions.php",
        },
        "FreeRideInvestor": {
            "local_path": "D:/websites/FreeRideInvestor",
            "theme_name": "freerideinvestor",
            "remote_base": "/public_html/wp-content/themes/freerideinvestor",
            "functions_path": "/public_html/wp-content/themes/freerideinvestor/functions.php",
        },
        "ariajet": {
            "local_path": "D:/websites/ariajet.site",
            "theme_name": "ariajet",
            "remote_base": "/public_html/wp-content/themes/ariajet",
            "functions_path": "/public_html/wp-content/themes/ariajet/functions.php",
        },
        "ariajet.site": {
            "local_path": "D:/websites/ariajet.site",
            "theme_name": "ariajet",
            "remote_base": "/public_html/wp-content/themes/ariajet",
            "functions_path": "/public_html/wp-content/themes/ariajet/functions.php",
        },
    }
    
    # Load from sites.json if it exists
    sites_json = Path(".deploy_credentials/sites.json")
    if sites_json.exists():
        try:
            with open(sites_json) as f:
                sites_data = json.load(f)
            for site_key, site_data in sites_data.items():
                if site_key in default_configs:
                    # Merge with defaults
                    configs[site_key] = {
                        **default_configs[site_key], **site_data}
                else:
                    # New site from JSON
                    configs[site_key] = {
                        "local_path": site_data.get("local_path", f"D:/websites/{site_key}"),
                        "theme_name": site_data.get("theme_name"),
                        "remote_base": site_data.get("remote_path", "/public_html"),
                        "functions_path": site_data.get("functions_path", f"{site_data.get('remote_path', '/public_html')}/functions.php"),
                    }
        except Exception as e:
            logger.warning(f"Could not load sites.json: {e}")
    
    # Add defaults for sites not in JSON
    for site_key, config in default_configs.items():
        if site_key not in configs:
            configs[site_key] = config
    
    return configs


def detect_site_from_path(file_path: Path) -> Optional[str]:
    """Auto-detect site from file path."""
    file_str = str(file_path).replace("\\", "/")
    
    # Check against known site paths
    site_configs = load_site_configs()
    for site_key, config in site_configs.items():
        local_path = config.get("local_path", "").replace("\\", "/")
        if local_path and local_path.lower() in file_str.lower():
            return site_key
    
    # Try to extract site name from path
    path_parts = file_str.split("/")
    for part in path_parts:
        if part in site_configs:
            return part
        # Check without extension
        if "." in part:
            base = part.split(".")[0]
            if base in site_configs:
                return base
    
    return None


def deploy_wordpress_file(site: str, local_file: Path, remote_path: Optional[str] = None) -> bool:
    """Deploy WordPress file to specified site."""
    site_configs = load_site_configs()
    
    # Try to find site (case-insensitive, with variations)
    config = None
    site_key = None
    
    for key in site_configs.keys():
        if key.lower() == site.lower() or key.replace(".", "").lower() == site.replace(".", "").lower():
            config = site_configs[key]
            site_key = key
            break
    
    if not config:
        logger.error(f"Unknown site: {site}")
        logger.error(
            f"Available sites: {', '.join(sorted(site_configs.keys()))}")
        return False
    
    if not remote_path:
        # Auto-detect remote path based on local file
        if local_file.name == "functions.php":
            remote_path = config.get(
                "functions_path", f"{config['remote_base']}/functions.php")
        else:
            # Calculate relative path from local_path
            local_path = Path(config.get("local_path", ""))
            try:
                rel_path = local_file.relative_to(local_path)
                remote_path = f"{config['remote_base']}/{rel_path}".replace(
                    "\\", "/")
            except ValueError:
                # File not in local_path, just use filename
                remote_path = f"{config['remote_base']}/{local_file.name}"
    
    deployer = FTPDeployer(site=site_key)
    try:
        return deployer.upload_file(local_file, remote_path)
    finally:
        deployer.disconnect()


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FTP Deployer for WordPress Files"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test FTP connection"
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy file(s)"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Local file to deploy"
    )
    parser.add_argument(
        "--site",
        help="WordPress site (auto-detected from file path if not specified)"
    )
    parser.add_argument(
        "--list-sites",
        action="store_true",
        help="List all available sites"
    )
    parser.add_argument(
        "--remote-path",
        help="Remote file path (auto-detected if not specified)"
    )
    parser.add_argument(
        "--host",
        help="FTP host (overrides .env)"
    )
    parser.add_argument(
        "--username",
        help="FTP username (overrides .env)"
    )
    parser.add_argument(
        "--password",
        help="FTP password (overrides .env)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=21,
        help="FTP port (default: 21)"
    )
    
    args = parser.parse_args()
    
    # List sites if requested
    if args.list_sites:
        site_configs = load_site_configs()
        print("📋 Available Sites:")
        print("=" * 60)
        for site_key in sorted(site_configs.keys()):
            config = site_configs[site_key]
            local_path = config.get("local_path", "N/A")
            remote_base = config.get("remote_base", "N/A")
            print(f"  • {site_key}")
            print(f"    Local: {local_path}")
            print(f"    Remote: {remote_base}")
        sys.exit(0)
    
    deployer = FTPDeployer(
        host=args.host,
        username=args.username,
        password=args.password,
        port=args.port,
        site=args.site
    )
    
    try:
        if args.test:
            success, message = deployer.test_connection()
            if success:
                print(f"✅ {message}")
                sys.exit(0)
            else:
                print(f"❌ {message}")
                sys.exit(1)
        
        elif args.deploy:
            if not args.file:
                parser.error("--deploy requires --file")
            
            if not args.file.exists():
                print(f"❌ File not found: {args.file}")
                sys.exit(1)
            
            # Auto-detect site if not specified
            site = args.site
            if not site:
                site = detect_site_from_path(args.file)
                if site:
                    print(f"🔍 Auto-detected site: {site}")
                else:
                    print("❌ Could not auto-detect site from file path")
                    print(
                        "   Please specify --site or ensure file is in a known site directory")
                    print("\n   Available sites:")
                    site_configs = load_site_configs()
                    for site_key in sorted(site_configs.keys()):
                        print(f"     • {site_key}")
                    sys.exit(1)
            
            success = deploy_wordpress_file(
                site,
                args.file,
                args.remote_path
            )
            
            if success:
                print(f"✅ Successfully deployed {args.file.name}")
                sys.exit(0)
            else:
                print(f"❌ Failed to deploy {args.file.name}")
                sys.exit(1)
        
        else:
            parser.print_help()
    
    finally:
        deployer.disconnect()


if __name__ == '__main__':
    main()
