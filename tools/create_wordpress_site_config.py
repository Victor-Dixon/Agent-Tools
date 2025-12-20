#!/usr/bin/env python3
"""
WordPress Site Configuration Helper
====================================

Creates site_configs.json for batch WordPress SEO/UX deployment.
Supports both REST API and SFTP deployment methods.

Author: Agent-7
V2 Compliant: Yes
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def load_existing_credentials() -> Dict[str, Any]:
    """Load existing WordPress credentials from .deploy_credentials/blogging_api.json."""
    creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
    if creds_file.exists():
        try:
            with open(creds_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load existing credentials: {e}")
    return {}


def create_site_config_template() -> Dict[str, Any]:
    """Create site configuration template for 9 WordPress sites."""
    sites = [
        "ariajet.site",
        "crosbyultimateevents.com",
        "digitaldreamscape.site",
        "freerideinvestor.com",
        "prismblossom.online",
        "southwestsecret.com",
        "tradingrobotplug.com",
        "weareswarm.online",
        "weareswarm.site"
    ]
    
    existing_creds = load_existing_credentials()
    config = {}
    
    for site in sites:
        # Check if credentials exist for this site
        site_creds = existing_creds.get(site) or existing_creds.get(site.replace(".", "_"))
        
        if site_creds:
            # Use existing credentials
            config[site] = {
                "site_url": site_creds.get("site_url", f"https://{site}"),
                "deployment_method": "rest_api",  # or "sftp"
                "rest_api": {
                    "username": site_creds.get("username"),
                    "app_password": site_creds.get("app_password"),
                    "site_url": site_creds.get("site_url", f"https://{site}")
                },
                "sftp": {
                    "host": site_creds.get("sftp_host"),
                    "username": site_creds.get("sftp_username"),
                    "password": site_creds.get("sftp_password"),
                    "remote_path": site_creds.get("remote_path", f"domains/{site}/public_html")
                },
                "seo_deployment": {
                    "method": "functions.php",  # or "plugin"
                    "target_file": "wp-content/themes/{active_theme}/functions.php"
                },
                "ux_deployment": {
                    "method": "additional_css",  # or "theme"
                    "target_file": "wp-content/themes/{active_theme}/style.css"  # if theme method
                }
            }
        else:
            # Create template entry (needs manual configuration)
            config[site] = {
                "site_url": f"https://{site}",
                "deployment_method": "rest_api",  # or "sftp"
                "rest_api": {
                    "username": "",  # TODO: Fill in
                    "app_password": "",  # TODO: Fill in
                    "site_url": f"https://{site}"
                },
                "sftp": {
                    "host": "",  # TODO: Fill in
                    "username": "",  # TODO: Fill in
                    "password": "",  # TODO: Fill in
                    "remote_path": f"domains/{site}/public_html"
                },
                "seo_deployment": {
                    "method": "functions.php",
                    "target_file": "wp-content/themes/{active_theme}/functions.php"
                },
                "ux_deployment": {
                    "method": "additional_css",
                    "target_file": "wp-content/themes/{active_theme}/style.css"
                }
            }
    
    return config


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create WordPress site configuration for batch deployment"
    )
    parser.add_argument(
        '--output',
        default='site_configs.json',
        help='Output file path (default: site_configs.json)'
    )
    parser.add_argument(
        '--check-existing',
        action='store_true',
        help='Check for existing credentials and populate automatically'
    )

    args = parser.parse_args()

    print("🔧 WordPress Site Configuration Helper")
    print("=" * 60)
    print()

    config = create_site_config_template()
    
    # Count configured vs template sites
    configured = sum(1 for site, cfg in config.items() 
                   if cfg.get("rest_api", {}).get("username") or 
                      cfg.get("sftp", {}).get("username"))
    total = len(config)
    
    print(f"📋 Site Configuration Summary:")
    print(f"   Total sites: {total}")
    print(f"   Configured: {configured}")
    print(f"   Needs configuration: {total - configured}")
    print()

    # Write configuration file
    output_path = project_root / args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration file created: {output_path}")
    print()
    
    if configured < total:
        print("⚠️  Some sites need manual configuration:")
        for site, cfg in config.items():
            if not (cfg.get("rest_api", {}).get("username") or 
                   cfg.get("sftp", {}).get("username")):
                print(f"   - {site}: Missing credentials")
        print()
        print("📝 Next steps:")
        print("   1. Edit site_configs.json and fill in missing credentials")
        print("   2. Or add credentials to .deploy_credentials/blogging_api.json")
        print("   3. Run batch_wordpress_seo_ux_deploy.py with --dry-run to test")
        print()
    else:
        print("✅ All sites have credentials configured!")
        print("   Ready for deployment.")
        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())

