#!/usr/bin/env python3
"""
Unified WordPress Management Tool
==================================

Single comprehensive tool for all WordPress operations:
- Page creation and setup
- File deployment (SFTP/SSH)
- Database table creation
- Menu management
- Content updates
- WP-CLI commands

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
V2 Exception: Approved (1080 lines) - See docs/V2_COMPLIANCE_EXCEPTIONS.md
"""

import json
import logging
import os
import re
import socket
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Load .env file if available
try:
    from dotenv import load_dotenv, dotenv_values
    env_vars = dotenv_values(".env")
    # Merge into os.environ
    for key, value in env_vars.items():
        if value and key not in os.environ:
            os.environ[key] = value
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, skip

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

# Ensure we have at least basic logging configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages SSH/SFTP connections."""

    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = None
        self.sftp = None
        self.transport = None

    def connect(self, max_retries: int = 3, base_delay: float = 0.5) -> bool:
        """
        Establish SSH connection with structured diagnostics and safe retry.

        Logs each failure stage (DNS/TCP, SSH handshake, auth, SFTP init)
        without ever logging secrets.
        """
        if not HAS_PARAMIKO:
            logger.error(
                "paramiko not installed - install with: pip install paramiko")
            return False

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Attempting SFTP connection",
                    extra={
                        "stage": "connect_start",
                        "host": self.host,
                        "port": self.port,
                        "username": self.username,
                        "attempt": attempt,
                        "max_retries": max_retries,
                    },
                )

                # DNS / TCP stage
                try:
                    self.transport = paramiko.Transport((self.host, self.port))
                except (socket.gaierror, OSError) as e:
                    logger.error(
                        "DNS/TCP connection failed "
                        f"for {self.host}:{self.port} (stage=dns_tcp, attempt={attempt}/{max_retries}): {e}"
                    )
                    if attempt == max_retries:
                        return False
                    time.sleep(base_delay * attempt)
                    continue

                # SSH authentication stage
                try:
                    self.transport.connect(
                        username=self.username, password=self.password)
                except paramiko.AuthenticationException:
                    logger.error(
                        "Authentication failed "
                        f"for {self.username}@{self.host}:{self.port} (stage=auth)"
                    )
                    logger.error(
                        "Please verify username and password are correct")
                    return False
                except paramiko.SSHException as e:
                    logger.error(
                        f"SSH handshake/auth error for {self.host}:{self.port} "
                        f"(stage=ssh_handshake, attempt={attempt}/{max_retries}): {e}"
                    )
                    if attempt == max_retries:
                        return False
                    time.sleep(base_delay * attempt)
                    continue

                # SSH client + SFTP stage
                try:
                    self.client = paramiko.SSHClient()
                    self.client.set_missing_host_key_policy(
                        paramiko.AutoAddPolicy())
                    self.client.connect(
                        hostname=self.host,
                        port=self.port,
                        username=self.username,
                        password=self.password,
                    )
                    self.sftp = paramiko.SFTPClient.from_transport(
                        self.transport)
                except paramiko.SSHException as e:
                    logger.error(
                        f"SFTP channel initialization failed for {self.host}:{self.port} "
                        f"(stage=sftp_init, attempt={attempt}/{max_retries}): {e}"
                    )
                    if attempt == max_retries:
                        return False
                    time.sleep(base_delay * attempt)
                    continue

                logger.info(
                    f"SFTP connection established successfully to {self.host}:{self.port} "
                    f"(username={self.username}, attempt={attempt}/{max_retries})"
                )
                return True

            except Exception as e:
                logger.error(
                    f"Unexpected connection failure for {self.host}:{self.port} "
                    f"(stage=unknown, attempt={attempt}/{max_retries}): {type(e).__name__}: {e}"
                )
                if attempt == max_retries:
                    return False
                time.sleep(base_delay * attempt)
                continue

    def disconnect(self):
        """Close connections."""
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
        if self.transport:
            self.transport.close()
        self.client = None
        self.sftp = None
        self.transport = None

    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """Upload file via SFTP with recursive dir ensure."""
        if not self.sftp:
            return False
        try:
            self._ensure_remote_dir(remote_path)
            self.sftp.put(str(local_path), remote_path)
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False

    def _ensure_remote_dir(self, remote_path: str):
        """Recursively ensure remote directory exists (using relative paths)."""
        # Remove leading slash if present (paths should be relative)
        remote_path = remote_path.lstrip("/")
        remote_dir = '/'.join(remote_path.split('/')[:-1])
        if not remote_dir:
            return
        parts = remote_dir.split("/")
        current = ""
        for part in parts:
            if not part:  # Skip empty parts
                continue
            current = f"{current}/{part}" if current else part
            try:
                self.sftp.stat(current)
            except FileNotFoundError:
                try:
                    self.sftp.mkdir(current)
                except Exception:
                    # If created concurrently, verify existence; otherwise raise
                    try:
                        self.sftp.stat(current)
                    except Exception as e:
                        raise e

    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """Execute SSH command."""
        if not self.client:
            return "", "Not connected", 1
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            return stdout.read().decode(), stderr.read().decode(), exit_code
        except Exception as e:
            return "", str(e), 1


class WordPressManager:
    """Unified WordPress management tool."""

    SITE_CONFIGS = {
        "southwestsecret": {
            "local_path": "D:/websites/southwestsecret.com",
            "theme_name": "southwestsecret",
            "remote_base": "domains/southwestsecret.com/public_html/wp-content/themes/southwestsecret",
            "function_prefix": "southwestsecret"
        },
        "prismblossom": {
            "local_path": "D:/websites/prismblossom.online",
            "theme_name": "prismblossom",
            "remote_base": "domains/prismblossom.online/public_html/wp-content/themes/prismblossom",
            "function_prefix": "prismblossom"
        },
        "prismblossom.online": {
            "local_path": "D:/websites/prismblossom.online",
            "theme_name": "prismblossom",
            "remote_base": "domains/prismblossom.online/public_html/wp-content/themes/prismblossom",
            "function_prefix": "prismblossom"
        },
        "freerideinvestor": {
            "local_path": "D:/websites/FreeRideInvestor",
            "theme_name": "freerideinvestor-modern",
            "remote_base": "domains/freerideinvestor.com/public_html/wp-content/themes/freerideinvestor-modern",
            "function_prefix": "freerideinvestor"
        },
        "FreeRideInvestor": {
            "local_path": "D:/websites/FreeRideInvestor",
            "theme_name": "freerideinvestor-modern",
            "remote_base": "domains/freerideinvestor.com/public_html/wp-content/themes/freerideinvestor-modern",
            "function_prefix": "freerideinvestor"
        },
        "ariajet": {
            "local_path": "D:/websites/ariajet.site",
            "theme_name": "ariajet",
            "remote_base": "domains/ariajet.site/public_html/wp-content/themes/ariajet",
            "function_prefix": "ariajet"
        },
        "ariajet.site": {
            "local_path": "D:/websites/ariajet.site",
            "theme_name": "ariajet",
            "remote_base": "domains/ariajet.site/public_html/wp-content/themes/ariajet",
            "function_prefix": "ariajet"
        },
        "weareswarm.online": {
            "local_path": "D:/websites/Swarm_website/wp-content/themes/swarm-theme",
            "theme_name": "swarm-theme",
            "remote_base": "domains/weareswarm.online/public_html/wp-content/themes/swarm-theme",
            "function_prefix": "swarm"
        },
        "weareswarm.site": {
            "local_path": "D:/websites/Swarm_website/wp-content/themes/swarm-theme",
            "theme_name": "swarm-theme",
            "remote_base": "domains/weareswarm.site/public_html/wp-content/themes/swarm-theme",
            "function_prefix": "swarm"
        },
        "tradingrobotplug.com": {
            "local_path": "D:/websites/tradingrobotplug.com/wp-content/themes/tradingrobotplug",
            "theme_name": "tradingrobotplug",
            "remote_base": "domains/tradingrobotplug.com/public_html/wp-content/themes/tradingrobotplug",
            "function_prefix": "tradingrobotplug"
        },
        "dadudekc.com": {
            "local_path": "D:/websites/dadudekc.com/wp-content/themes/dadudekc",
            "theme_name": "dadudekc",
            "remote_base": "domains/dadudekc.com/public_html/wp-content/themes/dadudekc",
            "function_prefix": "dadudekc"
        },
        "crosbyultimateevents.com": {
            "local_path": "D:/Agent_Cellphone_V2_Repository/temp_repos/crosbyultimateevents.com",
            "theme_name": "crosbyultimateevents",
            "remote_base": "domains/crosbyultimateevents.com/public_html/wp-content/themes/crosbyultimateevents",
            "function_prefix": "crosbyultimateevents"
        },
        "houstonsipqueen.com": {
            "local_path": "D:/websites/houstonsipqueen.com",
            "theme_name": "houstonsipqueen",
            "remote_base": "domains/houstonsipqueen.com/public_html/wp-content/themes/houstonsipqueen",
            "function_prefix": "houstonsipqueen"
        },
        "digitaldreamscape.site": {
            "local_path": "D:/websites/digitaldreamscape.site",
            "theme_name": "digitaldreamscape",
            "remote_base": "domains/digitaldreamscape.site/public_html/wp-content/themes/digitaldreamscape",
            "function_prefix": "digitaldreamscape"
        }
    }

    def __init__(self, site_key: str = "prismblossom", dry_run: bool = False):
        """Initialize WordPress manager."""
        self.site_key = site_key
        self.dry_run = dry_run
        self.config = self.SITE_CONFIGS.get(site_key)
        if not self.config:
            raise ValueError(f"Unknown site: {site_key}")

        self.conn_manager: Optional[ConnectionManager] = None
        self.credentials: Optional[dict] = None
        self._load_credentials()
        # Optional overrides (can be set from CLI)
        self.override_port: Optional[int] = None
        self.override_username: Optional[str] = None
        self.override_remote_base: Optional[str] = None
        self.override_wp_cli_path: Optional[str] = None

        if self.dry_run:
            logger.info("🔍 DRY-RUN MODE ENABLED - No changes will be made")

    def _load_credentials(self):
        """Load deployment credentials from sites.json or .env environment variables."""
        # First try sites.json
        creds_file = Path(
            "D:/Agent_Cellphone_V2_Repository/.deploy_credentials/sites.json")
        if creds_file.exists():
            try:
                with open(creds_file) as f:
                    all_creds = json.load(f)
                self.credentials = (
                    all_creds.get(self.site_key) or
                    all_creds.get(f"{self.site_key}.online") or
                    all_creds.get(self.site_key.replace(".online", ""))
                )
                # Validate credentials are not empty
                if self.credentials:
                    # Normalize port and allow remote_base/remote_path overrides per-site
                    try:
                        self.credentials["port"] = int(
                            self.credentials.get("port", 65002))
                    except Exception:
                        self.credentials["port"] = 65002
                    if self.credentials.get("remote_base"):
                        self.config["remote_base"] = self.credentials["remote_base"]
                    if self.credentials.get("remote_path"):
                        self.credentials["remote_path"] = self.credentials["remote_path"]

                    if self._validate_credentials(self.credentials):
                        logger.info(
                            f"Loaded credentials from sites.json for {self.site_key}")
                        return
                    else:
                        logger.warning(
                            f"Credentials found in sites.json for {self.site_key} but are empty/invalid")
                        self.credentials = None
            except Exception as e:
                logger.error(
                    f"Failed to load credentials from sites.json: {e}")

        # Try .env file in multiple locations
        env_locations = [
            Path("D:/Agent_Cellphone_V2_Repository/.env"),
            Path(".env"),
            Path("D:/websites/.env"),
            Path(__file__).parent.parent / ".env"
        ]

        env_loaded = False
        for env_path in env_locations:
            if env_path.exists():
                try:
                    from dotenv import load_dotenv
                    load_dotenv(env_path)
                    env_loaded = True
                    logger.info(f"Loaded .env file from: {env_path}")
                    break
                except Exception as e:
                    logger.debug(f"Could not load .env from {env_path}: {e}")

        # Fallback to .env environment variables (shared Hostinger credentials)
        host = os.getenv("HOSTINGER_HOST") or os.getenv(
            "SSH_HOST") or os.getenv("HOST")
        username = os.getenv("HOSTINGER_USER") or os.getenv(
            "SSH_USER") or os.getenv("USERNAME")
        password = os.getenv("HOSTINGER_PASS") or os.getenv(
            "SSH_PASS") or os.getenv("PASSWORD")
        port_str = os.getenv("HOSTINGER_PORT") or os.getenv(
            "SSH_PORT") or os.getenv("PORT", "65002")

        # Validate credentials are not empty
        if host and username and password and host.strip() and username.strip() and password.strip():
            try:
                port = int(port_str)
            except ValueError:
                port = 65002  # Default Hostinger SFTP port

            self.credentials = {
                "host": host.strip(),
                "username": username.strip(),
                "password": password.strip(),
                "port": port
            }
            if self._validate_credentials(self.credentials):
                logger.info(
                    f"Loaded credentials from .env environment variables for {self.site_key}")
            else:
                logger.warning(
                    f"Credentials from .env are invalid for {self.site_key}")
                self.credentials = None
        else:
            missing = []
            if not host or not host.strip():
                missing.append("HOSTINGER_HOST/SSH_HOST")
            if not username or not username.strip():
                missing.append("HOSTINGER_USER/SSH_USER")
            if not password or not password.strip():
                missing.append("HOSTINGER_PASS/SSH_PASS")
            logger.warning(
                f"Missing credentials for {self.site_key}: {', '.join(missing)}")
            self.credentials = None

    def _validate_credentials(self, creds: dict) -> bool:
        """Validate credentials are not empty."""
        if not creds:
            return False
        host = creds.get("host", "").strip()
        username = creds.get("username", "").strip()
        password = creds.get("password", "").strip()
        return bool(host and username and password)

    def get_theme_path(self) -> Path:
        """Get local theme directory path."""
        theme_name = self.config["theme_name"]
        theme_paths = [
            # Prioritize wp-content/themes path first
            Path(self.config["local_path"]) /
            "wp-content" / "themes" / theme_name,
            Path(self.config["local_path"]) / "wordpress-theme" / theme_name,
            # For FreeRideInvestor where theme is in root (fallback)
            Path(self.config["local_path"]),
        ]
        for path in theme_paths:
            if path.exists():
                return path
        raise FileNotFoundError(
            f"Theme directory not found for {self.site_key}")

    def get_plugin_path(self, plugin_name: str) -> Path:
        """Get local plugin directory path."""
        plugin_paths = [
            Path(self.config["local_path"]) /
            "wordpress-plugins" / plugin_name,
            Path(self.config["local_path"]) /
            "wp-content" / "plugins" / plugin_name,
            Path(self.config["local_path"]) / "plugins" / plugin_name,
        ]
        for path in plugin_paths:
            if path.exists():
                return path
        raise FileNotFoundError(
            f"Plugin directory not found: {plugin_name} for {self.site_key}")

    # ========== PAGE MANAGEMENT ==========

    def create_page(self, page_name: str, page_slug: Optional[str] = None,
                    template_content: Optional[str] = None) -> bool:
        """Create WordPress page with template."""
        page_slug = page_slug or page_name.lower().replace(' ', '-')
        template_name = f"page-{page_slug}.php"
        theme_path = self.get_theme_path()

        if not template_content:
            template_content = f"""<?php
/**
 * Template Name: {page_name}
 * @package {self.config['theme_name'].title()}
 */
get_header();
?>
<section class="{page_slug}-section">
    <div class="container">
        <h1>{page_name}</h1>
        <p>Content goes here...</p>
    </div>
</section>
<?php get_footer(); ?>"""

        # Create template file
        template_file = theme_path / template_name
        template_file.write_text(template_content, encoding='utf-8')

        # Add to functions.php
        function_code = self._generate_page_function(
            page_name, page_slug, template_name)
        self._add_to_functions_php(function_code)

        print(f"✅ Page '{page_name}' created!")
        return True

    def _generate_page_function(self, page_name: str, page_slug: str, template_name: str) -> str:
        """Generate page creation function."""
        prefix = self.config["function_prefix"]
        function_name = f"{prefix}_create_{page_slug.replace('-', '_')}_page"
        return f"""// Create {page_name} page
function {function_name}() {{
    if (get_page_by_path('{page_slug}')) return;
    ${page_slug}_page = array(
        'post_title' => '{page_name}',
        'post_name' => '{page_slug}',
        'post_status' => 'publish',
        'post_type' => 'page',
        'page_template' => '{template_name}'
    );
    wp_insert_post(${page_slug}_page);
}}
add_action('after_switch_theme', '{function_name}');"""

    def _add_to_functions_php(self, code: str):
        """Add code to functions.php."""
        theme_path = self.get_theme_path()
        functions_file = theme_path / "functions.php"
        content = functions_file.read_text(encoding='utf-8')
        if code not in content:
            content += f"\n\n{code}\n"
            functions_file.write_text(content, encoding='utf-8')

    # ========== DEPLOYMENT ==========

    def connect(self) -> bool:
        """Connect to deployment server."""
        if not self.credentials:
            logger.error(f"No credentials available for {self.site_key}")
            logger.error("Please configure credentials in:")
            logger.error("  1. .deploy_credentials/sites.json (site-specific)")
            logger.error(
                "  2. .env file (HOSTINGER_HOST, HOSTINGER_USER, HOSTINGER_PASS, HOSTINGER_PORT)")
            return False

        host = self.credentials.get("host", "").strip()
        username = self.credentials.get("username", "").strip()
        password = self.credentials.get("password", "").strip()
        port = self.credentials.get("port", 65002)

        # Apply CLI overrides when provided
        if self.override_port:
            port = self.override_port
            self.credentials["port"] = port
        if self.override_username:
            username = self.override_username
            self.credentials["username"] = username
        if self.override_remote_base:
            self.config["remote_base"] = self.override_remote_base

        # Validate credentials
        missing = []
        if not host:
            missing.append("host")
        if not username:
            missing.append("username")
        if not password:
            missing.append("password")

        if missing:
            logger.error(
                f"Missing credentials for {self.site_key}: {', '.join(missing)}")
            logger.error(
                "Please check .deploy_credentials/sites.json or .env file")
            return False

        try:
            self.conn_manager = ConnectionManager(
                host, username, password, port)
            if self.conn_manager.connect():
                logger.info(f"Connected to {host}:{port} as {username}")
                return True
            else:
                logger.error(f"Connection failed to {host}:{port}")
                logger.error("Please verify:")
                logger.error("  - Host address is correct")
                logger.error("  - Username and password are correct")
                logger.error(
                    "  - Port number is correct (default: 65002 for Hostinger SFTP)")
                logger.error("  - Firewall allows SFTP/SSH connections")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from server."""
        if self.conn_manager:
            self.conn_manager.disconnect()

    def deploy_file(
        self,
        local_path: Path,
        remote_path: Optional[str] = None,
        auto_flush_cache: bool = True
    ) -> bool:
        """
        Deploy single file to server.

        Args:
            local_path: Local file path to deploy
            remote_path: Optional remote path (auto-detected if not provided)
            auto_flush_cache: If True, automatically flush cache after deployment

        Returns:
            True if deployment succeeded
        """
        if self.dry_run:
            if not remote_path:
                theme_path = self.get_theme_path()
                if theme_path in local_path.parents:
                    rel_path = local_path.relative_to(theme_path)
                    remote_path = f"{self.config['remote_base']}/{rel_path}"
                else:
                    remote_path = f"{self.config['remote_base']}/{local_path.name}"
            logger.info(
                f"🔍 DRY-RUN: Would deploy {local_path} → {remote_path}")
            if auto_flush_cache:
                logger.info(
                    "🔍 DRY-RUN: Would auto-flush cache after deployment")
            return True

        if not self.conn_manager:
            if not self.connect():
                return False
        if not remote_path:
            theme_path = self.get_theme_path()
            if theme_path in local_path.parents:
                rel_path = local_path.relative_to(theme_path)
                remote_path = f"{self.config['remote_base']}/{rel_path}"
            else:
                remote_path = f"{self.config['remote_base']}/{local_path.name}"

        success = self.conn_manager.upload_file(local_path, remote_path)

        # Automatically flush cache after successful deployment
        if success and auto_flush_cache:
            logger.info("🔄 Auto-flushing cache after deployment...")
            self.purge_caches(use_comprehensive_flush=True)

        return success

    def deploy_theme(
        self,
        pattern: str = "*.php",
        auto_flush_cache: bool = True
    ) -> int:
        """
        Deploy all theme files matching pattern.

        Args:
            pattern: File pattern to match (e.g., "*.php", "*.css")
            auto_flush_cache: If True, automatically flush cache after deployment

        Returns:
            Number of files successfully deployed
        """
        if not self.connect():
            return 0
        theme_path = self.get_theme_path()
        files_deployed = 0

        # Deploy files without auto-flush (we'll flush once at the end)
        for file_path in theme_path.glob(pattern):
            if self.deploy_file(file_path, auto_flush_cache=False):
                files_deployed += 1
                print(f"✅ Deployed: {file_path.name}")

        # Flush cache once after all files are deployed
        if files_deployed > 0 and auto_flush_cache:
            logger.info("🔄 Auto-flushing cache after theme deployment...")
            self.purge_caches(use_comprehensive_flush=True)

        return files_deployed

    # ========== PLUGIN DEPLOYMENT ==========

    def deploy_plugin_file(
        self,
        local_path: Path,
        plugin_name: str,
        remote_path: Optional[str] = None,
        auto_flush_cache: bool = True
    ) -> bool:
        """
        Deploy single plugin file to server.

        Args:
            local_path: Local file path to deploy
            plugin_name: Plugin directory name
            remote_path: Optional remote path (auto-detected if not provided)
            auto_flush_cache: If True, automatically flush cache after deployment

        Returns:
            True if deployment succeeded
        """
        if self.dry_run:
            if not remote_path:
                plugin_path = self.get_plugin_path(plugin_name)
                if plugin_path in local_path.parents:
                    rel_path = local_path.relative_to(plugin_path)
                    # Convert Windows path separators to Unix forward slashes
                    rel_path_str = str(rel_path).replace('\\', '/')
                    remote_path = f"domains/{self.site_key.replace('.com', '')}.com/public_html/wp-content/plugins/{plugin_name}/{rel_path_str}"
                else:
                    remote_path = f"domains/{self.site_key.replace('.com', '')}.com/public_html/wp-content/plugins/{plugin_name}/{local_path.name}"
            logger.info(
                f"🔍 DRY-RUN: Would deploy plugin file {local_path} → {remote_path}")
            if auto_flush_cache:
                logger.info(
                    "🔍 DRY-RUN: Would auto-flush cache after deployment")
            return True

        if not self.conn_manager:
            if not self.connect():
                return False

        if not remote_path:
            plugin_path = self.get_plugin_path(plugin_name)
            if plugin_path in local_path.parents:
                rel_path = local_path.relative_to(plugin_path)
                # Convert Windows path separators to Unix forward slashes
                rel_path_str = str(rel_path).replace('\\', '/')
                # Extract domain from remote_base or construct from site_key
                if "/public_html" in self.config.get("remote_base", ""):
                    domain_path = self.config["remote_base"].split(
                        "/wp-content")[0]
                else:
                    domain = self.site_key.replace(".com", "").replace(
                        ".online", "").replace(".site", "")
                    domain_path = f"domains/{domain}.com/public_html"
                remote_path = f"{domain_path}/wp-content/plugins/{plugin_name}/{rel_path_str}"
            else:
                domain = self.site_key.replace(".com", "").replace(
                    ".online", "").replace(".site", "")
                remote_path = f"domains/{domain}.com/public_html/wp-content/plugins/{plugin_name}/{local_path.name}"

        success = self.conn_manager.upload_file(local_path, remote_path)

        # Automatically flush cache after successful deployment
        if success and auto_flush_cache:
            logger.info("🔄 Auto-flushing cache after plugin deployment...")
            self.purge_caches(use_comprehensive_flush=True)

        return success

    def deploy_plugin(
        self,
        plugin_name: str,
        pattern: str = "**/*",
        auto_flush_cache: bool = True
    ) -> int:
        """
        Deploy all plugin files matching pattern.

        Args:
            plugin_name: Plugin directory name
            pattern: File pattern to match (e.g., "**/*", "*.php", "*.css")
            auto_flush_cache: If True, automatically flush cache after deployment

        Returns:
            Number of files successfully deployed
        """
        if not self.connect():
            return 0

        try:
            plugin_path = self.get_plugin_path(plugin_name)
        except FileNotFoundError as e:
            logger.error(str(e))
            return 0

        files_deployed = 0

        # Deploy files without auto-flush (we'll flush once at the end)
        for file_path in plugin_path.rglob(pattern):
            if file_path.is_file():
                # Skip hidden files and common ignore patterns
                if file_path.name.startswith('.') or file_path.name in ['Thumbs.db', '.DS_Store']:
                    continue
                if self.deploy_plugin_file(file_path, plugin_name, auto_flush_cache=False):
                    files_deployed += 1
                    rel_path = file_path.relative_to(plugin_path)
                    print(f"✅ Deployed: {rel_path}")

        # Flush cache once after all files are deployed
        if files_deployed > 0 and auto_flush_cache:
            logger.info("🔄 Auto-flushing cache after plugin deployment...")
            self.purge_caches(use_comprehensive_flush=True)

        return files_deployed

    # ========== DATABASE ==========

    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """Create database table code."""
        prefix = self.config["function_prefix"]
        function_name = f"{prefix}_create_{table_name}_table"
        column_defs = [f"        {k} {v}" for k, v in columns.items()]
        code = f"""// Create {table_name} table
function {function_name}() {{
    global $wpdb;
    $table_name = $wpdb->prefix . '{table_name}';
    $charset_collate = $wpdb->get_charset_collate();
    $sql = "CREATE TABLE IF NOT EXISTS $table_name (
{chr(10).join(column_defs)}
    ) $charset_collate;";
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}}
add_action('after_switch_theme', '{function_name}');"""
        self._add_to_functions_php(code)
        return True

    # ========== MENU ==========

    def add_to_menu(self, page_slug: str, menu_text: Optional[str] = None) -> bool:
        """Add page to navigation menu."""
        menu_text = menu_text or page_slug.replace('-', ' ').title()
        prefix = self.config["function_prefix"]
        code = f"""// Add {menu_text} to menu
function {prefix}_add_{page_slug}_menu($items, $args) {{
    if ($args->theme_location == 'primary') {{
        ${page_slug}_page = get_page_by_path('{page_slug}');
        ${page_slug}_url = ${page_slug}_page ? get_permalink(${page_slug}_page->ID) : home_url('/{page_slug}');
        $items .= '<li><a href="' . esc_url(${page_slug}_url) . '">{menu_text}</a></li>';
    }}
    return $items;
}}
add_filter('wp_nav_menu_items', '{prefix}_add_{page_slug}_menu', 10, 2);"""
        self._add_to_functions_php(code)
        return True

    # ========== WP-CLI ==========

    def wp_cli(self, command: str) -> Tuple[str, str, int]:
        """Execute WP-CLI command using relative paths."""
        if not self.conn_manager:
            if not self.connect():
                return "", "Not connected", 1
        wp_path = (
            self.override_wp_cli_path
            or self.credentials.get("wp_cli_path", "wp")
        )

        # Construct WordPress root path from remote_base (relative path)
        # remote_base format: "domains/{domain}/public_html/wp-content/themes/{theme}"
        # WordPress root: "domains/{domain}/public_html"
        remote_base = self.config.get("remote_base", "")
        if remote_base:
            # Extract WordPress root from theme path
            # Remove "/wp-content/themes/{theme}" to get to public_html
            if "/wp-content/themes/" in remote_base:
                wp_root = remote_base.split("/wp-content/themes/")[0]
            elif "/public_html" in remote_base:
                wp_root = remote_base.split("/public_html")[0] + "/public_html"
            else:
                # Fallback: try to use remote_path from credentials
                wp_root = self.credentials.get("remote_path", "domains")
                if wp_root.startswith("/"):
                    wp_root = wp_root.lstrip("/")
        else:
            # Fallback to credentials or default
            wp_root = self.credentials.get("remote_path", "domains")
            if wp_root.startswith("/"):
                wp_root = wp_root.lstrip("/")

        # Use relative path (no leading slash)
        full_cmd = f"cd {wp_root} && {wp_path} {command}"
        return self.conn_manager.execute_command(full_cmd)

    def update_post_status(self, post_id: int, status: str = "publish") -> bool:
        """
        Update WordPress post status using WP-CLI.

        Args:
            post_id: WordPress post ID
            status: New status (publish, draft, private, etc.)

        Returns:
            True if successful
        """
        if self.dry_run:
            logger.info(
                f"🔍 DRY-RUN: Would update post {post_id} to status '{status}'")
            return True

        stdout, stderr, code = self.wp_cli(
            f"post update {post_id} --post_status={status}")
        if code == 0:
            logger.info(f"✅ Post {post_id} updated to status '{status}'")
            return True
        else:
            logger.error(f"❌ Failed to update post {post_id}: {stderr}")
            return False

    # ========== THEME MANAGEMENT ==========

    def replace_theme(
        self,
        new_theme_path: Path,
        backup: bool = True,
        auto_flush_cache: bool = True
    ) -> bool:
        """
        Replace entire theme on server.

        Args:
            new_theme_path: Local path to new theme directory
            backup: Whether to backup existing theme first
            auto_flush_cache: If True, automatically flush cache after deployment

        Returns:
            True if successful
        """
        if not self.connect():
            return False

        try:
            remote_theme_dir = self.config['remote_base']

            # Backup existing theme if requested
            if backup:
                backup_cmd = f"cp -r {remote_theme_dir} {remote_theme_dir}.backup"
                stdout, stderr, code = self.conn_manager.execute_command(
                    backup_cmd)
                if code == 0:
                    print(f"✅ Backup created: {remote_theme_dir}.backup")

            # Deploy all files from new theme
            files_deployed = 0
            for file_path in new_theme_path.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(new_theme_path)
                    remote_path = f"{remote_theme_dir}/{rel_path}"
                    if self.conn_manager.upload_file(file_path, remote_path):
                        files_deployed += 1

            print(f"✅ Theme replaced: {files_deployed} files deployed")

            # Automatically flush cache after successful theme replacement
            if files_deployed > 0 and auto_flush_cache:
                logger.info("🔄 Auto-flushing cache after theme replacement...")
                self.purge_caches(use_comprehensive_flush=True)

            return True
        except Exception as e:
            logger.error(f"Theme replacement failed: {e}")
            return False

    def activate_theme(
        self,
        theme_name: Optional[str] = None,
        use_browser_fallback: bool = True,
        auto_login: bool = False
    ) -> bool:
        """
        Activate theme using multiple methods.

        Tries methods in order:
        1. WP-CLI (fastest, preferred)
        2. Browser automation (fallback if WP-CLI fails)

        Args:
            theme_name: Theme name (defaults to configured theme)
            use_browser_fallback: If True, fall back to browser automation if WP-CLI fails
            auto_login: If True, attempt auto-login for browser method (requires WORDPRESS_USER/PASS in .env)

        Returns:
            True if successful
        """
        if not theme_name:
            theme_name = self.config['theme_name']

        # Method 1: Try WP-CLI first (fastest)
        logger.info(
            f"🎨 Attempting to activate theme '{theme_name}' via WP-CLI...")
        stdout, stderr, code = self.wp_cli(f"theme activate {theme_name}")

        if code == 0:
            logger.info(f"✅ Theme '{theme_name}' activated via WP-CLI")
            print(f"✅ Theme '{theme_name}' activated")
            return True

        # WP-CLI failed, log the error
        logger.warning(f"⚠️  WP-CLI activation failed: {stderr or stdout}")

        # Method 2: Fall back to browser automation if enabled
        if use_browser_fallback:
            logger.info(
                f"🌐 Falling back to browser automation for theme activation...")
            return self._activate_theme_via_browser(theme_name, auto_login)

        logger.error(f"❌ Theme activation failed: {stderr}")
        return False

    def _activate_theme_via_browser(
        self,
        theme_name: str,
        auto_login: bool = False
    ) -> bool:
        """
        Activate theme via browser automation (fallback method).

        Args:
            theme_name: Theme name to activate
            auto_login: If True, attempt auto-login using .env credentials

        Returns:
            True if successful
        """
        try:
            from tools.activate_wordpress_theme import activate_theme as browser_activate
        except ImportError:
            logger.error(
                "❌ Browser automation not available (selenium not installed)")
            logger.info("💡 Install with: pip install selenium")
            return False

        site_url = self._get_site_url()
        if not site_url:
            logger.error(
                "❌ Could not determine site URL for browser activation")
            return False

        logger.info(
            f"🌐 Using browser automation to activate '{theme_name}' on {site_url}")
        try:
            success = browser_activate(
                site_url=site_url,
                theme_name=theme_name,
                auto_login=auto_login,
                wait_timeout=60
            )
            if success:
                logger.info(
                    f"✅ Theme '{theme_name}' activated via browser automation")
                print(f"✅ Theme '{theme_name}' activated via browser")
            return success
        except Exception as e:
            logger.error(f"❌ Browser automation failed: {e}")
            return False

    def list_themes(self) -> List[Dict[str, str]]:
        """List all available themes."""
        stdout, stderr, code = self.wp_cli("theme list --format=json")
        if code == 0:
            try:
                themes = json.loads(stdout)
                return themes
            except:
                return []
        return []

    # ========== UTILITIES ==========

    def list_pages(self) -> List[Dict[str, str]]:
        """List all page templates."""
        theme_path = self.get_theme_path()
        pages = []
        for template_file in theme_path.glob("page-*.php"):
            try:
                content = template_file.read_text(encoding='utf-8')
                template_name = None
                for line in content.split('\n'):
                    if 'Template Name:' in line:
                        template_name = line.split(
                            'Template Name:')[-1].strip()
                        break
                pages.append({
                    'file': template_file.name,
                    'template_name': template_name or 'Unknown',
                    'path': str(template_file)
                })
            except Exception as e:
                logger.error(f"Error reading {template_file}: {e}")
        return pages

    def verify(self) -> Dict[str, any]:
        """Verify WordPress setup."""
        results = {'theme_exists': False,
                   'functions_exists': False, 'pages': 0}
        try:
            theme_path = self.get_theme_path()
            results['theme_exists'] = theme_path.exists()
            results['functions_exists'] = (
                theme_path / "functions.php").exists()
            results['pages'] = len(list(theme_path.glob("page-*.php")))
        except Exception as e:
            logger.error(f"Verification error: {e}")
        return results

    # ========== MENU / CACHE HELPERS ==========
    def assign_primary_menu(
        self,
        menu_name: str = "Main",
        add_home: bool = True,
        home_url: Optional[str] = None,
    ) -> bool:
        """Create/assign a primary menu; optionally add a Home link."""
        if not self.connect():
            return False
        menus_json, _, _ = self.wp_cli("menu list --format=json")
        menus = json.loads(menus_json) if menus_json.strip() else []
        menu_id = None
        for m in menus:
            if m.get("name") == menu_name:
                menu_id = m.get("term_id")
                break
        if not menu_id:
            self.wp_cli(f"menu create {menu_name}")
            menus_json, _, _ = self.wp_cli("menu list --format=json")
            menus = json.loads(menus_json) if menus_json.strip() else []
            for m in menus:
                if m.get("name") == menu_name:
                    menu_id = m.get("term_id")
                    break
        if not menu_id:
            logger.error("Menu creation/lookup failed")
            return False
        items_json, _, _ = self.wp_cli(
            f"menu item list {menu_name} --format=json")
        items = json.loads(items_json) if items_json.strip() else []
        if add_home and not items:
            target_url = home_url or self.credentials.get(
                "home_url", "https://freerideinvestor.com"
            )
            self.wp_cli(
                f"menu item add-custom {menu_name} 'Home' {target_url}"
            )
        self.wp_cli(f"menu location assign {menu_name} primary")
        return True

    def purge_caches(self, use_comprehensive_flush: bool = True) -> bool:
        """
        Purge WordPress cache using multiple methods.

        Tries methods in order:
        1. WP-CLI (litespeed-purge + cache flush)
        2. WordPress REST API (if credentials available)
        3. WP-CLI rewrite flush (for permalink cache)

        Args:
            use_comprehensive_flush: If True, tries multiple methods; 
                                    if False, only uses WP-CLI

        Returns:
            True if at least one method succeeded
        """
        logger.info("🔄 Attempting WordPress cache flush...")
        success_count = 0

        # Method 1: WP-CLI cache flush (primary method)
        try:
            logger.info("   Trying WP-CLI cache flush...")
            stdout1, stderr1, code1 = self.wp_cli("litespeed-purge all")
            stdout2, stderr2, code2 = self.wp_cli("cache flush")

            if code1 == 0 or code2 == 0:
                logger.info("   ✅ Cache flushed via WP-CLI")
                success_count += 1
            else:
                logger.warning(
                    f"   ⚠️  WP-CLI cache flush warnings: {stderr1 or stderr2}")
        except Exception as e:
            logger.warning(f"   ⚠️  WP-CLI method failed: {e}")

        # Method 2: WP-CLI rewrite flush (for permalink cache)
        try:
            logger.info("   Trying WP-CLI rewrite flush...")
            stdout, stderr, code = self.wp_cli("rewrite flush")
            if code == 0:
                logger.info("   ✅ Rewrite rules flushed via WP-CLI")
                success_count += 1
            else:
                logger.warning(f"   ⚠️  Rewrite flush warning: {stderr}")
        except Exception as e:
            logger.warning(f"   ⚠️  Rewrite flush failed: {e}")

        # Method 3: WordPress REST API (if comprehensive flush enabled)
        if use_comprehensive_flush:
            try:
                wp_username = os.getenv('WP_ADMIN_USERNAME')
                wp_password = os.getenv('WP_ADMIN_PASSWORD')
                site_url = self._get_site_url()

                if wp_username and wp_password and site_url:
                    logger.info("   Trying WordPress REST API...")
                    import requests

                    wp_admin_url = f"{site_url}/wp-admin"
                    flush_url = f"{wp_admin_url}/admin-ajax.php"

                    session = requests.Session()
                    auth = (wp_username, wp_password)

                    # Try to flush rewrite rules via REST API
                    response = session.post(
                        flush_url,
                        data={'action': 'flush_rewrite_rules'},
                        auth=auth,
                        timeout=10
                    )

                    if response.status_code == 200:
                        logger.info("   ✅ Cache flushed via REST API")
                        success_count += 1
                    else:
                        logger.warning(
                            f"   ⚠️  REST API returned status {response.status_code}")
            except ImportError:
                logger.debug(
                    "   ⚠️  requests library not available for REST API flush")
            except Exception as e:
                logger.warning(f"   ⚠️  REST API method failed: {e}")

        if success_count > 0:
            logger.info(
                f"✅ Cache flush complete ({success_count} method(s) succeeded)")
            return True
        else:
            logger.warning("⚠️  All cache flush methods failed")
            logger.info("📋 Manual steps required:")
            site_url = self._get_site_url()
            if site_url:
                logger.info(
                    f"      1. Go to: {site_url}/wp-admin/options-permalink.php")
            logger.info("      2. Click 'Save Changes' (no edits needed)")
            logger.info("      3. Hard refresh homepage (Ctrl+F5)")
            return False

    def _get_site_url(self) -> Optional[str]:
        """Get WordPress site URL from config or credentials."""
        # Try credentials first
        if self.credentials:
            site_url = self.credentials.get(
                "site_url") or self.credentials.get("url")
            if site_url:
                return site_url.rstrip('/')

        # Try config
        if self.config:
            site_url = self.config.get("site_url")
            if site_url:
                return site_url.rstrip('/')

        # Try to infer from site_key
        if self.site_key:
            # Remove common suffixes
            domain = self.site_key.replace(".online", "").replace(
                ".site", "").replace(".com", "")
            # Try common TLDs
            for tld in [".com", ".online", ".site"]:
                potential_url = f"https://{domain}{tld}"
                # Could verify here, but for now just return first guess
                return potential_url

        return None


def main():
    """CLI interface."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Unified WordPress Management Tool")
    parser.add_argument('--site', default='prismblossom', help='Site key')
    parser.add_argument('--port', type=int, help='Override SFTP port')
    parser.add_argument('--username', type=str, help='Override SFTP username')
    parser.add_argument('--remote-base', type=str,
                        help='Override remote theme base path')
    parser.add_argument('--wp-cli-path', type=str,
                        help='Override wp-cli path (e.g., \"php /usr/local/bin/wp-cli-2.12.0.phar\")')
    parser.add_argument('--create-page', type=str, help='Create page')
    parser.add_argument('--deploy', action='store_true',
                        help='Deploy theme files')
    parser.add_argument('--list', action='store_true', help='List pages')
    parser.add_argument('--verify', action='store_true', help='Verify setup')
    parser.add_argument('--add-menu', type=str, help='Add page to menu (slug)')
    parser.add_argument('--replace-theme', type=str,
                        help='Replace theme (path to new theme)')
    parser.add_argument('--activate-theme', type=str,
                        help='Activate theme by name')
    parser.add_argument('--no-browser-fallback', action='store_true',
                        help='Disable browser automation fallback for theme activation')
    parser.add_argument('--auto-login', action='store_true',
                        help='Enable auto-login for browser automation (requires WORDPRESS_USER/PASS in .env)')
    parser.add_argument('--list-themes', action='store_true',
                        help='List all themes')
    parser.add_argument('--deploy-file', type=str,
                        help='Deploy a single file (local path) to remote_base-relative path')
    parser.add_argument('--remote-path', type=str,
                        help='Optional explicit remote path (relative to site root)')
    parser.add_argument('--assign-menu', action='store_true',
                        help='Create/assign primary menu (default name: Main)')
    parser.add_argument('--menu-name', type=str,
                        default='Main', help='Menu name to create/assign')
    parser.add_argument('--add-home-link', type=str, nargs='?', const='https://freerideinvestor.com',
                        help='Add Home link to menu (optional URL, default site home)')
    parser.add_argument('--purge-cache', action='store_true',
                        help='Purge LiteSpeed/WP caches')
    parser.add_argument('--no-auto-flush', action='store_true',
                        help='Disable automatic cache flush after deployment (default: auto-flush enabled)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Dry-run mode: simulate operations without making changes')
    parser.add_argument('--deploy-plugin', type=str,
                        help='Deploy plugin (plugin directory name)')
    parser.add_argument('--deploy-plugin-file', type=str,
                        help='Deploy single plugin file (local path)')
    parser.add_argument('--plugin-name', type=str,
                        help='Plugin name (required with --deploy-plugin-file)')
    parser.add_argument('--update-post-status', type=int,
                        help='Update post status (requires --post-status)')
    parser.add_argument('--post-status', type=str,
                        choices=['publish', 'draft',
                                 'private', 'pending', 'future'],
                        default='publish',
                        help='Post status (used with --update-post-status)')

    args = parser.parse_args()

    try:
        manager = WordPressManager(args.site, dry_run=args.dry_run)

        # Apply overrides
        if args.port:
            manager.override_port = args.port
            manager.credentials["port"] = args.port
        if args.username:
            manager.override_username = args.username
            manager.credentials["username"] = args.username
        if args.remote_base:
            manager.override_remote_base = args.remote_base
            manager.config["remote_base"] = args.remote_base
        if args.wp_cli_path:
            manager.override_wp_cli_path = args.wp_cli_path
            manager.credentials["wp_cli_path"] = args.wp_cli_path

        # Determine auto-flush setting (default: enabled unless --no-auto-flush is set)
        auto_flush = not args.no_auto_flush

        if args.create_page:
            manager.create_page(args.create_page)
        elif args.deploy:
            count = manager.deploy_theme(auto_flush_cache=auto_flush)
            print(f"✅ Deployed {count} files")
        elif args.list:
            pages = manager.list_pages()
            for p in pages:
                print(f"  • {p['file']} - {p['template_name']}")
        elif args.verify:
            results = manager.verify()
            print(f"Theme exists: {results['theme_exists']}")
            print(f"Functions.php: {results['functions_exists']}")
            print(f"Pages: {results['pages']}")
        elif args.add_menu:
            manager.add_to_menu(args.add_menu)
        elif args.replace_theme:
            theme_path = Path(args.replace_theme)
            if manager.replace_theme(theme_path, auto_flush_cache=auto_flush):
                print("✅ Theme replaced successfully")
        elif args.activate_theme:
            use_browser = not args.no_browser_fallback
            auto_login = args.auto_login
            if manager.activate_theme(args.activate_theme, use_browser_fallback=use_browser, auto_login=auto_login):
                print("✅ Theme activated successfully")
            else:
                print("❌ Theme activation failed")
                sys.exit(1)
        elif args.list_themes:
            themes = manager.list_themes()
            for theme in themes:
                status = "✅ ACTIVE" if theme.get(
                    'status') == 'active' else "  "
                print(
                    f"{status} {theme.get('name', 'Unknown')} - {theme.get('version', 'N/A')}")
        elif args.deploy_file:
            local_path = Path(args.deploy_file)
            ok = manager.deploy_file(
                local_path, remote_path=args.remote_path, auto_flush_cache=auto_flush)
            print(
                f"✅ Deployed file: {local_path}" if ok else f"❌ Deploy failed: {local_path}")
        elif args.assign_menu or args.add_home_link:
            home_url = args.add_home_link if args.add_home_link else None
            if manager.assign_primary_menu(menu_name=args.menu_name, add_home=True, home_url=home_url):
                print(f"✅ Menu '{args.menu_name}' assigned to primary")
            else:
                print(f"❌ Failed to assign menu '{args.menu_name}'")
        elif args.purge_cache:
            manager.purge_caches()
            print("✅ Cache purged")
        elif args.deploy_plugin:
            count = manager.deploy_plugin(
                args.deploy_plugin, auto_flush_cache=auto_flush)
            print(f"✅ Deployed {count} plugin files")
        elif args.deploy_plugin_file:
            if not args.plugin_name:
                print("❌ Error: --plugin-name required with --deploy-plugin-file")
                sys.exit(1)
            local_path = Path(args.deploy_plugin_file)
            ok = manager.deploy_plugin_file(
                local_path, args.plugin_name, auto_flush_cache=auto_flush)
            print(
                f"✅ Deployed plugin file: {local_path}" if ok else f"❌ Deploy failed: {local_path}")
        elif args.update_post_status:
            if manager.update_post_status(args.update_post_status, args.post_status):
                print(
                    f"✅ Post {args.update_post_status} updated to '{args.post_status}'")
            else:
                print(f"❌ Failed to update post {args.update_post_status}")
                sys.exit(1)
        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
