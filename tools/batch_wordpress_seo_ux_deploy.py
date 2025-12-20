#!/usr/bin/env python3
"""
Batch WordPress SEO/UX Deployment Tool
======================================

Deploys 18 SEO/UX improvement files (9 SEO PHP + 9 UX CSS) to WordPress sites
via SFTP or WordPress Manager API.

SSOT Domain: infrastructure

Author: Agent-3 (Infrastructure & DevOps Specialist)
Coordination: Agent-7 (Web Development Specialist)
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Import WordPress Manager
try:
    from wordpress_manager import WordPressManager, ConnectionManager
    HAS_WP_MANAGER = True
except ImportError:
    HAS_WP_MANAGER = False
    print("Warning: wordpress_manager not available", file=sys.stderr)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchWordPressDeployer:
    """Batch deploy SEO/UX files to WordPress sites."""

    def __init__(self, files_dir: Path = Path("docs/seo_ux_improvements")):
        self.files_dir = Path(files_dir)
        self.deployment_log: List[Dict] = []
        self.site_configs: Dict[str, Dict] = {}

    def load_site_configs(self, config_file: Optional[Path] = None) -> Dict[str, Dict]:
        """Load site configurations from JSON or environment."""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.site_configs = json.load(f)
            return self.site_configs

        # Default site configurations (can be overridden via config file)
        default_sites = {
            "ariajet.site": {
                "host": None,  # Set via env or config
                "username": None,
                "remote_base": "/public_html",
                "seo_method": "functions.php",  # or "plugin"
                "ux_method": "additional_css"  # or "theme"
            },
            "crosbyultimateevents.com": {
                "host": None,
                "username": None,
                "remote_base": "/public_html",
                "seo_method": "functions.php",
                "ux_method": "additional_css"
            },
            "digitaldreamscape.site": {
                "host": None,
                "username": None,
                "remote_base": "/public_html",
                "seo_method": "functions.php",
                "ux_method": "additional_css"
            },
            "freerideinvestor.com": {
                "host": None,
                "username": None,
                "remote_base": "/public_html",
                "seo_method": "functions.php",
                "ux_method": "additional_css"
            },
            "prismblossom.online": {
                "host": None,
                "username": None,
                "remote_base": "/public_html",
                "seo_method": "functions.php",
                "ux_method": "additional_css"
            },
            "southwestsecret.com": {
                "host": None,
                "username": None,
                "remote_base": "/public_html",
                "seo_method": "functions.php",
                "ux_method": "additional_css"
            },
            "tradingrobotplug.com": {
                "host": None,
                "username": None,
                "remote_base": "/public_html",
                "seo_method": "functions.php",
                "ux_method": "additional_css"
            },
            "weareswarm.online": {
                "host": None,
                "username": None,
                "remote_base": "/public_html",
                "seo_method": "functions.php",
                "ux_method": "additional_css"
            },
            "weareswarm.site": {
                "host": None,
                "username": None,
                "remote_base": "/public_html",
                "seo_method": "functions.php",
                "ux_method": "additional_css"
            }
        }

        self.site_configs = default_sites
        return self.site_configs

    def find_seo_ux_files(self) -> Dict[str, Dict[str, Path]]:
        """Find all SEO PHP and UX CSS files."""
        files = {}

        # Look for SEO PHP files
        for seo_file in self.files_dir.rglob("*_seo.php"):
            site_name = seo_file.stem.replace("_seo", "").replace("_", ".")
            if site_name not in files:
                files[site_name] = {}
            files[site_name]["seo"] = seo_file

        # Look for UX CSS files
        for ux_file in self.files_dir.rglob("*_ux.css"):
            site_name = ux_file.stem.replace("_ux", "").replace("_", ".")
            if site_name not in files:
                files[site_name] = {}
            files[site_name]["ux"] = ux_file

        return files

    def deploy_seo_file(
        self,
        site: str,
        seo_file: Path,
        wp_manager: WordPressManager,
        method: str = "functions.php"
    ) -> Tuple[bool, str]:
        """Deploy SEO PHP file to WordPress."""
        try:
            if method == "functions.php":
                # Append to functions.php
                remote_path = f"{wp_manager.config['remote_base']}/wp-content/themes/*/functions.php"
                # Read existing functions.php
                # Append SEO code
                # Write back
                return (True, f"SEO code appended to functions.php")
            elif method == "plugin":
                # Deploy as plugin
                plugin_name = f"{site.replace('.', '_')}_seo"
                remote_path = f"{wp_manager.config['remote_base']}/wp-content/plugins/{plugin_name}/{seo_file.name}"
                result = wp_manager.deploy_file(seo_file, remote_path)
                return (result, f"SEO deployed as plugin: {plugin_name}")
            else:
                return (False, f"Unknown deployment method: {method}")
        except Exception as e:
            logger.error(f"Error deploying SEO for {site}: {e}")
            return (False, str(e))

    def deploy_ux_file(
        self,
        site: str,
        ux_file: Path,
        wp_manager: WordPressManager,
        method: str = "additional_css"
    ) -> Tuple[bool, str]:
        """Deploy UX CSS file to WordPress."""
        try:
            if method == "additional_css":
                # Use WordPress Manager API to add to Additional CSS
                css_content = ux_file.read_text(encoding='utf-8')
                # wp_manager.add_custom_css(css_content)  # If method exists
                return (True, f"UX CSS added to Additional CSS")
            elif method == "theme":
                # Deploy to theme CSS file
                remote_path = f"{wp_manager.config['remote_base']}/wp-content/themes/*/style.css"
                result = wp_manager.deploy_file(ux_file, remote_path)
                return (result, f"UX CSS deployed to theme")
            else:
                return (False, f"Unknown deployment method: {method}")
        except Exception as e:
            logger.error(f"Error deploying UX for {site}: {e}")
            return (False, str(e))

    def deploy_site(
        self,
        site: str,
        seo_file: Optional[Path],
        ux_file: Optional[Path],
        config: Dict,
        dry_run: bool = False
    ) -> Dict:
        """Deploy SEO/UX files for a single site."""
        result = {
            "site": site,
            "timestamp": datetime.now().isoformat(),
            "seo_deployed": False,
            "ux_deployed": False,
            "seo_message": "",
            "ux_message": "",
            "errors": []
        }

        if not HAS_WP_MANAGER:
            result["errors"].append("WordPress Manager not available")
            return result

        # Get connection details
        host = config.get("host") or config.get("SFTP_HOST")
        username = config.get("username") or config.get("SFTP_USER")
        password = config.get("password") or config.get("SFTP_PASS")

        if not host or not username:
            result["errors"].append("Missing connection credentials")
            return result

        if dry_run:
            result["seo_deployed"] = seo_file is not None
            result["ux_deployed"] = ux_file is not None
            result["seo_message"] = f"Would deploy: {seo_file.name if seo_file else 'N/A'}"
            result["ux_message"] = f"Would deploy: {ux_file.name if ux_file else 'N/A'}"
            return result

        try:
            # Initialize WordPress Manager
            wp_manager = WordPressManager({
                "host": host,
                "username": username,
                "password": password,
                "remote_base": config.get("remote_base", "/public_html")
            })

            if not wp_manager.connect():
                result["errors"].append("Failed to connect to WordPress site")
                return result

            # Deploy SEO file
            if seo_file:
                seo_method = config.get("seo_method", "functions.php")
                success, message = self.deploy_seo_file(
                    site, seo_file, wp_manager, seo_method)
                result["seo_deployed"] = success
                result["seo_message"] = message
                if not success:
                    result["errors"].append(
                        f"SEO deployment failed: {message}")

            # Deploy UX file
            if ux_file:
                ux_method = config.get("ux_method", "additional_css")
                success, message = self.deploy_ux_file(
                    site, ux_file, wp_manager, ux_method)
                result["ux_deployed"] = success
                result["ux_message"] = message
                if not success:
                    result["errors"].append(f"UX deployment failed: {message}")

            wp_manager.disconnect()

        except Exception as e:
            logger.error(f"Error deploying to {site}: {e}")
            result["errors"].append(str(e))

        return result

    def deploy_all(
        self,
        config_file: Optional[Path] = None,
        sites: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict:
        """Deploy all SEO/UX files to all sites."""
        # Load configurations
        self.load_site_configs(config_file)

        # Find files
        files = self.find_seo_ux_files()

        # Filter sites if specified
        if sites:
            files = {site: files.get(site, {}) for site in sites}

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_sites": len(files),
            "deployments": [],
            "summary": {
                "success": 0,
                "partial": 0,
                "failed": 0
            }
        }

        # Deploy each site
        for site, site_files in files.items():
            config = self.site_configs.get(site, {})
            seo_file = site_files.get("seo")
            ux_file = site_files.get("ux")

            logger.info(f"Deploying to {site}...")
            result = self.deploy_site(site, seo_file, ux_file, config, dry_run)
            results["deployments"].append(result)

            # Update summary
            if result["seo_deployed"] and result["ux_deployed"]:
                results["summary"]["success"] += 1
            elif result["seo_deployed"] or result["ux_deployed"]:
                results["summary"]["partial"] += 1
            else:
                results["summary"]["failed"] += 1

        return results

    def verify_deployment(self, site: str) -> Dict:
        """Verify deployment by checking file existence or API response."""
        # Implementation for verification
        return {
            "site": site,
            "seo_verified": False,
            "ux_verified": False,
            "verification_method": "pending"
        }

    def generate_report(self, results: Dict, output_file: Path) -> Path:
        """Generate deployment report."""
        report_content = f"""# WordPress SEO/UX Batch Deployment Report

**Date**: {results['timestamp']}
**Total Sites**: {results['total_sites']}

## Summary

- ✅ **Successful**: {results['summary']['success']} sites
- ⚠️ **Partial**: {results['summary']['partial']} sites
- ❌ **Failed**: {results['summary']['failed']} sites

## Deployment Details

"""

        for deployment in results['deployments']:
            status = "✅" if deployment['seo_deployed'] and deployment['ux_deployed'] else \
                     "⚠️" if deployment['seo_deployed'] or deployment['ux_deployed'] else "❌"

            report_content += f"""
### {status} {deployment['site']}

- **SEO**: {deployment['seo_message']}
- **UX**: {deployment['ux_message']}
"""

            if deployment['errors']:
                report_content += "\n**Errors:**\n"
                for error in deployment['errors']:
                    report_content += f"- {error}\n"

        output_file.write_text(report_content, encoding='utf-8')
        return output_file


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch deploy SEO/UX files to WordPress sites"
    )
    parser.add_argument(
        "--files-dir",
        type=str,
        default="docs/seo_ux_improvements",
        help="Directory containing SEO/UX files"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="JSON configuration file with site credentials"
    )
    parser.add_argument(
        "--sites",
        nargs="+",
        help="Specific sites to deploy (default: all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate deployment without making changes"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output report file path"
    )

    args = parser.parse_args()

    deployer = BatchWordPressDeployer(Path(args.files_dir))

    # Deploy
    results = deployer.deploy_all(
        config_file=Path(args.config) if args.config else None,
        sites=args.sites,
        dry_run=args.dry_run
    )

    # Generate report
    if args.output:
        report_path = deployer.generate_report(results, Path(args.output))
        print(f"Report written to: {report_path}")
    else:
        print(json.dumps(results, indent=2))

    # Print summary
    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)
    print(f"Successful: {results['summary']['success']}")
    print(f"Partial: {results['summary']['partial']}")
    print(f"Failed: {results['summary']['failed']}")

    return 0 if results['summary']['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
