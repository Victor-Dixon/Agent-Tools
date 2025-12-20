#!/usr/bin/env python3
"""
Deploy WordPress Theme via Blogging API
========================================

Deploys WordPress theme files using the same credentials as the blogging API.
Integrates with the unified blogging automation system.

Usage:
    python tools/deploy_theme_via_blogging_api.py --site crosbyultimateevents.com
    python tools/deploy_theme_via_blogging_api.py --site crosbyultimateevents.com --dry-run

Author: Agent-2 (Architecture & Design Specialist)
V2 Compliant: <400 lines
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_QUICK = 5
        HTTP_DEFAULT = 30


class ThemeDeployer:
    """Deploy WordPress theme using blogging API credentials."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize theme deployer."""
        self.config_path = config_path or Path(
            ".deploy_credentials/blogging_api.json")
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load blogging API configuration."""
        if not self.config_path.exists():
            print(f"❌ Config file not found: {self.config_path}")
            print("   Create it with: python tools/test_blogging_api_connectivity.py")
            sys.exit(1)

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            sys.exit(1)

    def find_theme_directory(self, site_id: str) -> Optional[Path]:
        """Find theme directory for site."""
        # Check multiple possible locations
        possible_paths = [
            project_root / "temp_repos" / site_id / "wordpress-theme" /
            site_id.replace(".com", "").replace(".", ""),
            project_root / "temp_repos" / site_id / "wordpress-theme" / site_id,
            project_root / "websites" / site_id / "wordpress-theme" /
            site_id.replace(".com", "").replace(".", ""),
        ]

        # Try to get theme name from sites.json
        sites_json = Path(".deploy_credentials/sites.json")
        if sites_json.exists():
            try:
                with open(sites_json, 'r') as f:
                    sites_data = json.load(f)
                    site_data = sites_data.get(site_id, {})
                    if site_data.get("local_path") and site_data.get("theme_name"):
                        local_path = Path(site_data["local_path"])
                        theme_name = site_data["theme_name"]
                        theme_path = local_path / "wordpress-theme" / theme_name
                        if theme_path.exists():
                            return theme_path
            except Exception:
                pass

        # Try possible paths
        for path in possible_paths:
            if path.exists() and (path / "style.css").exists():
                return path

        return None

    def get_theme_files(self, theme_path: Path) -> List[Path]:
        """Get all theme files to deploy."""
        files = []
        for file_path in theme_path.rglob("*"):
            if file_path.is_file():
                # Skip common non-theme files
                skip_patterns = [
                    ".git", ".svn", ".DS_Store", "__pycache__",
                    ".pyc", ".log", ".zip", ".backup", ".md"
                ]
                if any(pattern in str(file_path) for pattern in skip_patterns):
                    continue
                files.append(file_path)
        return files

    def deploy_theme_file_via_ftp(
        self,
        site_id: str,
        local_file: Path,
        remote_path: str
    ) -> bool:
        """Deploy single file via FTP using sites.json credentials."""
        try:
            from tools.ftp_deployer import deploy_wordpress_file
            return deploy_wordpress_file(site_id, local_file, remote_path)
        except Exception as e:
            print(f"❌ FTP deployment failed: {e}")
            return False

    def deploy_theme(
        self,
        site_id: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Deploy theme to site."""
        if site_id not in self.config:
            return {
                "success": False,
                "error": f"Site {site_id} not found in blogging_api.json"
            }

        site_config = self.config[site_id]
        site_url = site_config.get("site_url")

        # Find theme directory
        theme_path = self.find_theme_directory(site_id)
        if not theme_path:
            return {
                "success": False,
                "error": f"Theme directory not found for {site_id}"
            }

        theme_files = self.get_theme_files(theme_path)
        if not theme_files:
            return {
                "success": False,
                "error": f"No theme files found in {theme_path}"
            }

        print(f"\n📦 Found {len(theme_files)} theme files")
        print(f"   Theme path: {theme_path}")
        print(f"   Site: {site_id} ({site_url})")

        if dry_run:
            print("\n🔍 DRY RUN - Would deploy:")
            for f in theme_files[:10]:
                rel_path = f.relative_to(theme_path)
                print(f"   • {rel_path}")
            if len(theme_files) > 10:
                print(f"   ... and {len(theme_files) - 10} more files")
            return {
                "success": True,
                "files_count": len(theme_files),
                "dry_run": True
            }

        # Deploy via FTP (using sites.json credentials)
        print(f"\n📤 Deploying theme files...")

        # Get remote base path from sites.json
        sites_json = Path(".deploy_credentials/sites.json")
        remote_base = None
        if sites_json.exists():
            try:
                with open(sites_json, 'r') as f:
                    sites_data = json.load(f)
                    site_data = sites_data.get(site_id, {})
                    remote_base = site_data.get("remote_path", "")
            except Exception:
                pass

        if not remote_base:
            # Default remote path
            theme_name = theme_path.name
            remote_base = f"domains/{site_id}/public_html/wp-content/themes/{theme_name}"

        deployed = 0
        errors = []

        for file_path in theme_files:
            rel_path = file_path.relative_to(theme_path)
            remote_path = f"{remote_base}/{rel_path}".replace("\\", "/")

            if self.deploy_theme_file_via_ftp(site_id, file_path, remote_path):
                deployed += 1
                if deployed % 5 == 0:
                    print(
                        f"   ✅ Deployed {deployed}/{len(theme_files)} files...")
            else:
                errors.append(str(rel_path))

        success = deployed > 0 and len(errors) == 0

        return {
            "success": success,
            "files_deployed": deployed,
            "files_total": len(theme_files),
            "errors": errors
        }


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy WordPress Theme via Blogging API"
    )
    parser.add_argument(
        "--site",
        required=True,
        help="Site ID from blogging_api.json (e.g., crosbyultimateevents.com)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deployed without making changes"
    )
    parser.add_argument(
        "--config",
        help="Path to blogging_api.json (default: .deploy_credentials/blogging_api.json)"
    )

    args = parser.parse_args()

    if not HAS_REQUESTS:
        print("❌ requests library required. Install with: pip install requests")
        return 1

    config_path = Path(args.config) if args.config else None
    deployer = ThemeDeployer(config_path=config_path)

    result = deployer.deploy_theme(args.site, dry_run=args.dry_run)

    if result.get("success"):
        if result.get("dry_run"):
            print(
                f"\n✅ Dry run completed: {result.get('files_count')} files would be deployed")
        else:
            print(f"\n✅ Theme deployment completed!")
            print(
                f"   Files deployed: {result.get('files_deployed')}/{result.get('files_total')}")
            if result.get("errors"):
                print(
                    f"   ⚠️  Errors: {len(result.get('errors', []))} files failed")
                for error in result.get("errors", [])[:5]:
                    print(f"      • {error}")
        return 0
    else:
        print(f"\n❌ Deployment failed: {result.get('error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
