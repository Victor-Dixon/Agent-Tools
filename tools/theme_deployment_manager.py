#!/usr/bin/env python3
"""
Theme Deployment Manager - Multi-Site Theme Deployment
======================================================

Deploys entire WordPress themes to multiple sites with verification.
Ensures all sites have the correct theme deployed.

<!-- SSOT Domain: infrastructure -->

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <400 lines
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import FTP deployer
sys.path.insert(0, str(Path(__file__).parent))
from ftp_deployer import FTPDeployer, load_site_configs, detect_site_from_path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ThemeDeploymentManager:
    """Manages theme deployment across multiple WordPress sites."""
    
    def __init__(self):
        """Initialize theme deployment manager."""
        self.site_configs = load_site_configs()
    
    def find_theme_directory(self, site: str) -> Optional[Path]:
        """Find theme directory for a site."""
        config = self.site_configs.get(site)
        if not config:
            return None
        
        local_path = Path(config.get("local_path", ""))
        theme_name = config.get("theme_name")
        
        if not local_path.exists():
            return None
        
        # Check multiple possible locations
        possible_paths = []
        
        if theme_name:
            possible_paths.extend([
                local_path / "wordpress-theme" / theme_name,
                local_path / "wp-content" / "themes" / theme_name,
            ])
        
        # For FreeRideInvestor where theme is in root
        possible_paths.append(local_path)
        
        for path in possible_paths:
            if path.exists():
                # Check for WordPress theme indicators
                has_style_css = (path / "style.css").exists()
                has_functions_php = (path / "functions.php").exists()
                has_index_php = (path / "index.php").exists()
                has_page_templates = len(list(path.glob("page-*.php"))) > 0
                
                # WordPress theme must have:
                # - style.css (standard), OR
                # - functions.php + (index.php OR page templates)
                if has_style_css or (has_functions_php and (has_index_php or has_page_templates)):
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
                    ".pyc", ".log", ".zip", ".backup"
                ]
                if any(pattern in str(file_path) for pattern in skip_patterns):
                    continue
                files.append(file_path)
        return files
    
    def deploy_theme(self, site: str, dry_run: bool = False) -> Tuple[bool, int, List[str]]:
        """
        Deploy entire theme to a site.
        
        Returns:
            (success, files_deployed, errors)
        """
        config = self.site_configs.get(site)
        if not config:
            return False, 0, [f"Unknown site: {site}"]
        
        theme_path = self.find_theme_directory(site)
        if not theme_path:
            return False, 0, [f"Theme directory not found for {site}"]
        
        theme_files = self.get_theme_files(theme_path)
        if not theme_files:
            return False, 0, [f"No theme files found in {theme_path}"]
        
        logger.info(f"📦 Found {len(theme_files)} files in theme: {theme_path}")
        
        if dry_run:
            logger.info("🔍 DRY RUN - Would deploy:")
            for f in theme_files[:10]:  # Show first 10
                rel_path = f.relative_to(theme_path)
                remote_path = f"{config['remote_base']}/{rel_path}".replace("\\", "/")
                logger.info(f"  • {rel_path} → {remote_path}")
            if len(theme_files) > 10:
                logger.info(f"  ... and {len(theme_files) - 10} more files")
            return True, len(theme_files), []
        
        # Deploy files
        deployer = FTPDeployer(site=site)
        if not deployer.connect():
            return False, 0, ["Failed to connect to FTP server"]
        
        errors = []
        files_deployed = 0
        
        try:
            for file_path in theme_files:
                rel_path = file_path.relative_to(theme_path)
                remote_path = f"{config['remote_base']}/{rel_path}".replace("\\", "/")
                
                if deployer.upload_file(file_path, remote_path):
                    files_deployed += 1
                    if files_deployed % 10 == 0:
                        logger.info(f"  Deployed {files_deployed}/{len(theme_files)} files...")
                else:
                    errors.append(f"Failed to deploy: {rel_path}")
        
        finally:
            deployer.disconnect()
        
        success = files_deployed > 0 and len(errors) == 0
        return success, files_deployed, errors
    
    def audit_all_sites(self) -> Dict[str, Dict]:
        """Audit all sites for theme deployment status."""
        audit_results = {}
        
        for site_key in sorted(self.site_configs.keys()):
            config = self.site_configs[site_key]
            theme_path = self.find_theme_directory(site_key)
            
            status = {
                "site": site_key,
                "theme_name": config.get("theme_name"),
                "local_path": config.get("local_path"),
                "remote_base": config.get("remote_base"),
                "theme_found": theme_path is not None,
                "theme_path": str(theme_path) if theme_path else None,
                "file_count": 0,
            }
            
            if theme_path:
                theme_files = self.get_theme_files(theme_path)
                status["file_count"] = len(theme_files)
                status["total_size_mb"] = sum(f.stat().st_size for f in theme_files) / (1024 * 1024)
            
            audit_results[site_key] = status
        
        return audit_results
    
    def deploy_all_themes(self, dry_run: bool = False) -> Dict[str, Tuple[bool, int, List[str]]]:
        """Deploy themes to all sites."""
        results = {}
        
        for site_key in sorted(self.site_configs.keys()):
            logger.info(f"\n{'='*60}")
            logger.info(f"Deploying theme to: {site_key}")
            logger.info(f"{'='*60}")
            
            success, count, errors = self.deploy_theme(site_key, dry_run=dry_run)
            results[site_key] = (success, count, errors)
            
            if success:
                logger.info(f"✅ {site_key}: {count} files deployed")
            else:
                logger.error(f"❌ {site_key}: Failed - {errors}")
        
        return results


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Theme Deployment Manager for WordPress Sites"
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Audit all sites for theme deployment status"
    )
    parser.add_argument(
        "--deploy",
        type=str,
        metavar="SITE",
        help="Deploy theme to specific site"
    )
    parser.add_argument(
        "--deploy-all",
        action="store_true",
        help="Deploy themes to all sites"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deployed without making changes"
    )
    parser.add_argument(
        "--list-sites",
        action="store_true",
        help="List all sites with theme information"
    )
    
    args = parser.parse_args()
    
    manager = ThemeDeploymentManager()
    
    if args.audit:
        print("\n🔍 Theme Deployment Audit")
        print("=" * 80)
        results = manager.audit_all_sites()
        
        for site_key, status in results.items():
            print(f"\n📋 {site_key}")
            print(f"   Theme: {status['theme_name']}")
            print(f"   Local Path: {status['local_path']}")
            print(f"   Remote Base: {status['remote_base']}")
            print(f"   Theme Found: {'✅' if status['theme_found'] else '❌'}")
            if status['theme_found']:
                print(f"   Theme Path: {status['theme_path']}")
                print(f"   Files: {status['file_count']}")
                print(f"   Size: {status.get('total_size_mb', 0):.2f} MB")
            else:
                print(f"   ⚠️  Theme directory not found!")
    
    elif args.list_sites:
        print("\n📋 Available Sites for Theme Deployment")
        print("=" * 80)
        for site_key in sorted(manager.site_configs.keys()):
            config = manager.site_configs[site_key]
            theme_path = manager.find_theme_directory(site_key)
            status = "✅" if theme_path else "❌"
            print(f"{status} {site_key}")
            print(f"   Theme: {config.get('theme_name', 'N/A')}")
            print(f"   Local: {config.get('local_path', 'N/A')}")
            if theme_path:
                files = manager.get_theme_files(theme_path)
                print(f"   Files: {len(files)}")
    
    elif args.deploy:
        success, count, errors = manager.deploy_theme(args.deploy, dry_run=args.dry_run)
        if success:
            print(f"\n✅ Successfully deployed {count} files to {args.deploy}")
            sys.exit(0)
        else:
            print(f"\n❌ Deployment failed: {errors}")
            sys.exit(1)
    
    elif args.deploy_all:
        results = manager.deploy_all_themes(dry_run=args.dry_run)
        
        print("\n" + "=" * 80)
        print("📊 Deployment Summary")
        print("=" * 80)
        
        success_count = sum(1 for success, _, _ in results.values() if success)
        total_count = len(results)
        
        for site_key, (success, count, errors) in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {site_key}: {count} files")
            if errors:
                for error in errors[:3]:  # Show first 3 errors
                    print(f"     ⚠️  {error}")
        
        print(f"\n✅ Successful: {success_count}/{total_count}")
        if success_count < total_count:
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

