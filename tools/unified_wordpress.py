#!/usr/bin/env python3
"""
Unified WordPress - Consolidated WordPress Operations Tool
=========================================================

<!-- SSOT Domain: infrastructure -->

Consolidates all WordPress operations into a single unified tool.
Replaces 16+ individual WordPress tools with modular WordPress system.

WordPress Categories:
- deploy - Deployment operations
- theme - Theme management
- debug - Debugging operations
- admin - Admin operations

Author: Agent-5 (Business Intelligence Specialist) - Executing Agent-8's Consolidation Plan
Date: 2025-12-06
V2 Compliant: Yes
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedWordPress:
    """Unified WordPress operations system consolidating all WordPress capabilities."""
    
    def __init__(self):
        """Initialize unified WordPress."""
        self.project_root = project_root
    
    def deploy_admin(self, site_url: str, file_path: str, target_path: str = None) -> Dict[str, Any]:
        """Deploy file via WordPress admin."""
        try:
            from tools.deploy_via_wordpress_admin import deploy_file
            
            result = deploy_file(site_url, file_path, target_path)
            return {
                "category": "deploy",
                "action": "admin",
                "site_url": site_url,
                "file_path": file_path,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"WordPress admin deployment failed: {e}")
            return {
                "category": "deploy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def deploy_rest_api(self, site_url: str, file_path: str, target_path: str = None) -> Dict[str, Any]:
        """Deploy file via WordPress REST API."""
        try:
            from tools.deploy_via_wordpress_rest_api import deploy_file_via_rest_api
            
            result = deploy_file_via_rest_api(site_url, file_path, target_path)
            return {
                "category": "deploy",
                "action": "rest_api",
                "site_url": site_url,
                "file_path": file_path,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"WordPress REST API deployment failed: {e}")
            return {
                "category": "deploy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def deploy_sftp(self, site_url: str, file_path: str, target_path: str = None) -> Dict[str, Any]:
        """Deploy file via SFTP."""
        try:
            from tools.deploy_via_sftp import deploy_file_via_sftp
            
            result = deploy_file_via_sftp(site_url, file_path, target_path)
            return {
                "category": "deploy",
                "action": "sftp",
                "site_url": site_url,
                "file_path": file_path,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"WordPress SFTP deployment failed: {e}")
            return {
                "category": "deploy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def theme_activate(self, site_url: str, theme_name: str, auto_login: bool = False) -> Dict[str, Any]:
        """Activate WordPress theme."""
        try:
            from tools.activate_wordpress_theme import activate_theme
            
            result = activate_theme(site_url, theme_name, auto_login)
            return {
                "category": "theme",
                "action": "activate",
                "site_url": site_url,
                "theme_name": theme_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Theme activation failed: {e}")
            return {
                "category": "theme",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def theme_check_syntax(self, theme_path: str) -> Dict[str, Any]:
        """Check theme syntax."""
        try:
            from tools.check_theme_syntax import check_syntax
            
            result = check_syntax(theme_path)
            return {
                "category": "theme",
                "action": "check_syntax",
                "theme_path": theme_path,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Theme syntax check failed: {e}")
            return {
                "category": "theme",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def debug_enable(self, site_url: str) -> Dict[str, Any]:
        """Enable WordPress debug mode."""
        try:
            from tools.enable_wordpress_debug import enable_debug
            
            result = enable_debug(site_url)
            return {
                "category": "debug",
                "action": "enable",
                "site_url": site_url,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Debug enable failed: {e}")
            return {
                "category": "debug",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def debug_deployer(self, site_url: str) -> Dict[str, Any]:
        """Debug WordPress deployer."""
        try:
            from tools.debug_wordpress_deployer import debug_deployer
            
            result = debug_deployer(site_url)
            return {
                "category": "debug",
                "action": "deployer",
                "site_url": site_url,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Deployer debug failed: {e}")
            return {
                "category": "debug",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def admin_clear_transients(self, site_url: str) -> Dict[str, Any]:
        """Clear WordPress transients."""
        try:
            from tools.clear_wordpress_transients import clear_transients
            
            result = clear_transients(site_url)
            return {
                "category": "admin",
                "action": "clear_transients",
                "site_url": site_url,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Clear transients failed: {e}")
            return {
                "category": "admin",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def admin_diagnose_path(self, site_url: str) -> Dict[str, Any]:
        """Diagnose WordPress path issues."""
        try:
            from tools.diagnose_ariajet_wordpress_path import diagnose_path
            
            result = diagnose_path(site_url)
            return {
                "category": "admin",
                "action": "diagnose_path",
                "site_url": site_url,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Path diagnosis failed: {e}")
            return {
                "category": "admin",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """CLI entry point for unified WordPress tool."""
    parser = argparse.ArgumentParser(
        description="Unified WordPress Operations Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tools.unified_wordpress deploy admin --site https://example.com --file path/to/file.php
  python -m tools.unified_wordpress deploy rest-api --site https://example.com --file path/to/file.php
  python -m tools.unified_wordpress deploy sftp --site https://example.com --file path/to/file.php
  python -m tools.unified_wordpress theme activate --site https://example.com --theme ariajet
  python -m tools.unified_wordpress theme check-syntax --theme path/to/theme
  python -m tools.unified_wordpress debug enable --site https://example.com
  python -m tools.unified_wordpress debug deployer --site https://example.com
  python -m tools.unified_wordpress admin clear-transients --site https://example.com
  python -m tools.unified_wordpress admin diagnose-path --site https://example.com
        """
    )
    
    parser.add_argument(
        "category",
        choices=["deploy", "theme", "debug", "admin"],
        help="WordPress operation category"
    )
    
    parser.add_argument(
        "action",
        help="Action to perform within category"
    )
    
    parser.add_argument("--site", help="WordPress site URL")
    parser.add_argument("--file", help="File path for deployment")
    parser.add_argument("--target", help="Target path on server")
    parser.add_argument("--theme", help="Theme name or path")
    parser.add_argument("--auto-login", action="store_true", help="Auto-login for admin operations")
    
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    wp = UnifiedWordPress()
    results = {}
    
    # Route to appropriate category method
    if args.category == "deploy":
        if args.action == "admin" and args.site and args.file:
            results = wp.deploy_admin(args.site, args.file, args.target)
        elif args.action == "rest-api" and args.site and args.file:
            results = wp.deploy_rest_api(args.site, args.file, args.target)
        elif args.action == "sftp" and args.site and args.file:
            results = wp.deploy_sftp(args.site, args.file, args.target)
        else:
            results = {"error": "Site URL and file path required for deployment"}
    
    elif args.category == "theme":
        if args.action == "activate" and args.site and args.theme:
            results = wp.theme_activate(args.site, args.theme, args.auto_login)
        elif args.action == "check-syntax" and args.theme:
            results = wp.theme_check_syntax(args.theme)
        else:
            results = {"error": f"Invalid theme action or missing parameters: {args.action}"}
    
    elif args.category == "debug":
        if args.action == "enable" and args.site:
            results = wp.debug_enable(args.site)
        elif args.action == "deployer" and args.site:
            results = wp.debug_deployer(args.site)
        else:
            results = {"error": f"Invalid debug action or missing site URL: {args.action}"}
    
    elif args.category == "admin":
        if args.action == "clear-transients" and args.site:
            results = wp.admin_clear_transients(args.site)
        elif args.action == "diagnose-path" and args.site:
            results = wp.admin_diagnose_path(args.site)
        else:
            results = {"error": f"Invalid admin action or missing site URL: {args.action}"}
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        if "error" in results:
            print(f"❌ Error: {results['error']}")
        else:
            print(json.dumps(results, indent=2, default=str))
    
    return 0 if "error" not in results else 1


if __name__ == "__main__":
    sys.exit(main())

