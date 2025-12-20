#!/usr/bin/env python3
"""
Create WordPress Page via REST API
===================================

Creates WordPress pages using the blogging API credentials.

Usage:
    python tools/create_wordpress_page.py --site crosbyultimateevents.com --slug consultation --title "Book Consultation"
    python tools/create_wordpress_page.py --site crosbyultimateevents.com --slug consultation --title "Book Consultation" --template page-consultation.php

Author: Agent-2 (Architecture & Design Specialist)
V2 Compliant: <400 lines
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

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


def create_page(
    site_url: str,
    username: str,
    app_password: str,
    title: str,
    slug: str,
    template: Optional[str] = None,
    content: Optional[str] = None
) -> Dict[str, Any]:
    """Create WordPress page via REST API."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    auth = HTTPBasicAuth(username, app_password)

    # Check if page already exists
    check_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    response = requests.get(
        check_url,
        params={"slug": slug},
        auth=auth,
        timeout=TimeoutConstants.HTTP_DEFAULT
    )

    if response.status_code == 200:
        pages = response.json()
        if pages:
            return {
                "success": True,
                "page_id": pages[0]["id"],
                "link": pages[0]["link"],
                "message": "Page already exists"
            }

    # Create page
    page_data = {
        "title": title,
        "slug": slug,
        "status": "publish",
        "content": content or f"<!-- Page content for {title} -->"
    }

    # Note: WordPress automatically uses page-{slug}.php template if it exists
    # Template assignment via REST API requires meta update after creation

    response = requests.post(
        api_url,
        json=page_data,
        auth=auth,
        timeout=TimeoutConstants.HTTP_DEFAULT
    )

    if response.status_code in (200, 201):
        page = response.json()
        page_id = page.get("id")

        # Set page template via meta if template specified
        if template and page_id:
            meta_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages/{page_id}"
            meta_response = requests.post(
                meta_url,
                json={"meta": {"_wp_page_template": template}},
                auth=auth,
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            # Note: Meta update might not work via REST API, but WordPress will auto-detect page-{slug}.php

        return {
            "success": True,
            "page_id": page_id,
            "link": page.get("link"),
            "edit_link": page.get("_links", {}).get("self", [{}])[0].get("href")
        }
    else:
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text[:200]}"
        }


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create WordPress Page via REST API")
    parser.add_argument("--site", required=True,
                        help="Site ID from blogging_api.json")
    parser.add_argument("--slug", required=True, help="Page slug (URL path)")
    parser.add_argument("--title", required=True, help="Page title")
    parser.add_argument(
        "--template", help="Page template file (e.g., page-consultation.php)")
    parser.add_argument("--content", help="Page content (HTML)")
    parser.add_argument("--config", help="Path to blogging_api.json")

    args = parser.parse_args()

    if not HAS_REQUESTS:
        print("❌ requests library required. Install with: pip install requests")
        return 1

    # Load config
    config_path = Path(args.config) if args.config else Path(
        ".deploy_credentials/blogging_api.json")
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return 1

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if args.site not in config:
        print(f"❌ Site {args.site} not found in config")
        return 1

    site_config = config[args.site]
    site_url = site_config.get("site_url")
    username = site_config.get("username")
    app_password = site_config.get("app_password")

    result = create_page(
        site_url=site_url,
        username=username,
        app_password=app_password,
        title=args.title,
        slug=args.slug,
        template=args.template,
        content=args.content
    )

    if result.get("success"):
        print(f"✅ Page created successfully!")
        print(f"   Page ID: {result.get('page_id')}")
        print(f"   Link: {result.get('link')}")
        if result.get("message"):
            print(f"   Note: {result.get('message')}")
        return 0
    else:
        print(f"❌ Failed to create page: {result.get('error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
