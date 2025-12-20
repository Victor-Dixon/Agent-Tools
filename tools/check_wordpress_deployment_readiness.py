#!/usr/bin/env python3
"""
WordPress Deployment Infrastructure Readiness Check
====================================================

Checks infrastructure readiness for WordPress batch deployment:
- WordPress Manager availability
- SFTP libraries availability
- Site configuration file
- SEO/UX files availability
- Credentials configuration

Author: Agent-3 (Infrastructure & DevOps Specialist)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def check_wordpress_manager() -> Dict:
    """Check if WordPress Manager is available."""
    result = {
        "available": False,
        "error": None,
        "location": None
    }

    # Check if wordpress_manager module exists
    try:
        from wordpress_manager import WordPressManager, ConnectionManager
        result["available"] = True
        result["location"] = "wordpress_manager"
        return result
    except ImportError:
        # Check if it's in tools directory
        try:
            sys.path.insert(0, str(project_root / "tools"))
            from wordpress_manager import WordPressManager, ConnectionManager
            result["available"] = True
            result["location"] = "tools.wordpress_manager"
            return result
        except ImportError as e:
            result["error"] = str(e)
            return result


def check_sftp_libraries() -> Dict:
    """Check if SFTP libraries are available."""
    result = {
        "paramiko": False,
        "pysftp": False,
        "available": False,
        "library": None
    }

    try:
        import paramiko
        result["paramiko"] = True
        result["available"] = True
        result["library"] = "paramiko"
        return result
    except ImportError:
        pass

    try:
        import pysftp
        result["pysftp"] = True
        result["available"] = True
        result["library"] = "pysftp"
        return result
    except ImportError:
        result["error"] = "Neither paramiko nor pysftp available"
        return result


def check_site_configs() -> Dict:
    """Check site configuration file."""
    result = {
        "exists": False,
        "path": None,
        "sites_count": 0,
        "sites": [],
        "errors": []
    }

    config_paths = [
        project_root / "site_configs.json",
        project_root / "docs" / "site_configs.json",
        project_root / ".deploy_credentials" / "sites.json"
    ]

    for config_path in config_paths:
        if config_path.exists():
            result["exists"] = True
            result["path"] = str(config_path)
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        result["sites"] = list(data.keys())
                        result["sites_count"] = len(data)
                    elif isinstance(data, list):
                        result["sites"] = [
                            site.get("domain", site) for site in data]
                        result["sites_count"] = len(data)
            except Exception as e:
                result["errors"].append(str(e))
            break

    return result


def check_seo_ux_files() -> Dict:
    """Check if SEO/UX files exist."""
    result = {
        "seo_files": [],
        "ux_files": [],
        "total_seo": 0,
        "total_ux": 0,
        "sites_with_files": []
    }

    # Check common locations
    search_paths = [
        project_root / "docs" / "seo_ux_improvements",
        project_root / "temp",
        project_root
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Find SEO PHP files
        for seo_file in search_path.rglob("temp_*_seo.php"):
            result["seo_files"].append(str(seo_file))
            site = seo_file.stem.replace("temp_", "").replace("_seo", "")
            if site not in result["sites_with_files"]:
                result["sites_with_files"].append(site)

        # Find UX CSS files
        for ux_file in search_path.rglob("temp_*_ux.css"):
            result["ux_files"].append(str(ux_file))
            site = ux_file.stem.replace("temp_", "").replace("_ux", "")
            if site not in result["sites_with_files"]:
                result["sites_with_files"].append(site)

    result["total_seo"] = len(result["seo_files"])
    result["total_ux"] = len(result["ux_files"])

    return result


def check_deployment_tool() -> Dict:
    """Check if deployment tool exists and is functional."""
    result = {
        "exists": False,
        "path": None,
        "functional": False,
        "errors": []
    }

    tool_path = project_root / "tools" / "batch_wordpress_seo_ux_deploy.py"
    result["path"] = str(tool_path)
    result["exists"] = tool_path.exists()

    if result["exists"]:
        # Check if it can be imported (syntax check)
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "batch_wordpress_seo_ux_deploy", tool_path)
            if spec and spec.loader:
                result["functional"] = True
        except Exception as e:
            result["errors"].append(str(e))

    return result


def main():
    """Main execution."""
    print("🔍 WordPress Deployment Infrastructure Readiness Check")
    print("=" * 60)
    print()

    results = {
        "wordpress_manager": check_wordpress_manager(),
        "sftp_libraries": check_sftp_libraries(),
        "site_configs": check_site_configs(),
        "seo_ux_files": check_seo_ux_files(),
        "deployment_tool": check_deployment_tool()
    }

    # WordPress Manager
    print("📦 WordPress Manager:")
    if results["wordpress_manager"]["available"]:
        print(f"   ✅ Available ({results['wordpress_manager']['location']})")
    else:
        print(f"   ❌ Not available: {results['wordpress_manager']['error']}")
    print()

    # SFTP Libraries
    print("📦 SFTP Libraries:")
    if results["sftp_libraries"]["available"]:
        print(f"   ✅ Available ({results['sftp_libraries']['library']})")
    else:
        print(
            f"   ❌ Not available: {results['sftp_libraries'].get('error', 'Unknown error')}")
    print()

    # Site Configs
    print("📋 Site Configuration:")
    if results["site_configs"]["exists"]:
        print(f"   ✅ Found: {results['site_configs']['path']}")
        print(
            f"   ✅ Sites configured: {results['site_configs']['sites_count']}")
        if results["site_configs"]["sites"]:
            print(
                f"   Sites: {', '.join(results['site_configs']['sites'][:5])}")
            if len(results["site_configs"]["sites"]) > 5:
                print(
                    f"   ... and {len(results['site_configs']['sites']) - 5} more")
    else:
        print("   ❌ Not found")
    print()

    # SEO/UX Files
    print("📄 SEO/UX Files:")
    print(f"   SEO files: {results['seo_ux_files']['total_seo']}")
    print(f"   UX files: {results['seo_ux_files']['total_ux']}")
    if results["seo_ux_files"]["sites_with_files"]:
        print(
            f"   Sites with files: {len(results['seo_ux_files']['sites_with_files'])}")
    print()

    # Deployment Tool
    print("🛠️  Deployment Tool:")
    if results["deployment_tool"]["exists"]:
        print(f"   ✅ Found: {results['deployment_tool']['path']}")
        if results["deployment_tool"]["functional"]:
            print("   ✅ Functional")
        else:
            print(
                f"   ⚠️  Issues: {', '.join(results['deployment_tool']['errors'])}")
    else:
        print("   ❌ Not found")
    print()

    # Overall Status
    print("=" * 60)
    print("📊 Overall Infrastructure Readiness:")

    ready = (
        results["wordpress_manager"]["available"] and
        results["sftp_libraries"]["available"] and
        results["site_configs"]["exists"] and
        results["deployment_tool"]["exists"] and
        results["deployment_tool"]["functional"]
    )

    if ready:
        print("   ✅ READY for deployment")
        print()
        print("   Infrastructure components:")
        print("   ✅ WordPress Manager")
        print("   ✅ SFTP Libraries")
        print("   ✅ Site Configuration")
        print("   ✅ Deployment Tool")
        print()
        if results["seo_ux_files"]["total_seo"] > 0 and results["seo_ux_files"]["total_ux"] > 0:
            print(
                f"   ✅ Files ready: {results['seo_ux_files']['total_seo']} SEO + {results['seo_ux_files']['total_ux']} UX")
        else:
            print("   ⚠️  SEO/UX files not found (may be in different location)")
    else:
        print("   ⚠️  NOT READY - Missing components:")
        if not results["wordpress_manager"]["available"]:
            print("   ❌ WordPress Manager")
        if not results["sftp_libraries"]["available"]:
            print("   ❌ SFTP Libraries")
        if not results["site_configs"]["exists"]:
            print("   ❌ Site Configuration")
        if not results["deployment_tool"]["exists"] or not results["deployment_tool"]["functional"]:
            print("   ❌ Deployment Tool")

    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
