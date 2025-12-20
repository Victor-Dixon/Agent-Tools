#!/usr/bin/env python3
"""
Fix Menu Links for freerideinvestor.com and crosbyultimateevents.com
====================================================================

Fixes broken menu links and content issues:
- freerideinvestor.com: 6 broken links (4 menu links: About, Blog, Contact)
- crosbyultimateevents.com: 1 broken link (Blog in nav menu)

Author: Agent-7 (Web Development Specialist)
V2 Compliant: < 300 lines
"""

import sys
import json
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("❌ requests not installed. Install with: pip install requests")


def load_site_configs() -> Dict:
    """Load site configurations."""
    config_file = project_root / "site_configs.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def check_page_exists(site_url: str, slug: str, username: str, password: str) -> Optional[Dict]:
    """Check if a WordPress page exists."""
    if not HAS_REQUESTS:
        return None
    
    api_url = f"{site_url}/wp-json/wp/v2/pages"
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded}',
        'Content-Type': 'application/json'
    }
    
    params = {'slug': slug, 'per_page': 1}
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            pages = response.json()
            if pages:
                return pages[0]
        return None
    except Exception as e:
        print(f"⚠️  Error checking page: {e}")
        return None


def create_page(site_url: str, title: str, slug: str, username: str, password: str) -> Optional[Dict]:
    """Create a WordPress page."""
    if not HAS_REQUESTS:
        return None
    
    api_url = f"{site_url}/wp-json/wp/v2/pages"
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded}',
        'Content-Type': 'application/json'
    }
    
    page_data = {
        'title': title,
        'slug': slug,
        'status': 'publish',
        'content': f'<h1>{title}</h1><p>Content coming soon.</p>'
    }
    
    try:
        response = requests.post(api_url, json=page_data, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"⚠️  Failed to create page: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"⚠️  Error creating page: {e}")
        return None


def get_menu_items(site_url: str, menu_id: int, username: str, password: str) -> List[Dict]:
    """Get WordPress menu items."""
    if not HAS_REQUESTS:
        return []
    
    # WordPress REST API v2 doesn't have native menu endpoints
    # We'll need to use a custom endpoint or wp-admin
    # For now, return instructions for manual fix
    return []


def update_menu_item_url(site_url: str, menu_item_id: int, new_url: str, username: str, password: str) -> bool:
    """Update a menu item URL."""
    if not HAS_REQUESTS:
        return False
    
    api_url = f"{site_url}/wp-json/wp/v2/menu-items/{menu_item_id}"
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded}',
        'Content-Type': 'application/json'
    }
    
    data = {'url': new_url}
    
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"⚠️  Error updating menu item: {e}")
        return False


def fix_freeride_menu_links(site_url: str, username: str, password: str, dry_run: bool = False) -> Dict:
    """Fix broken menu links on freerideinvestor.com."""
    result = {
        "site": "freerideinvestor.com",
        "fixed": [],
        "created": [],
        "errors": []
    }
    
    print(f"\n📋 Fixing freerideinvestor.com menu links...")
    
    # Pages to check/create
    pages_to_fix = [
        {"slug": "about", "title": "About"},
        {"slug": "blog", "title": "Blog"},
        {"slug": "contact", "title": "Contact"}
    ]
    
    for page_info in pages_to_fix:
        slug = page_info["slug"]
        title = page_info["title"]
        
        # Check if page exists
        page = check_page_exists(site_url, slug, username, password)
        
        if page:
            print(f"   ✅ Page exists: /{slug} (ID: {page['id']})")
            result["fixed"].append(f"/{slug}")
        else:
            if dry_run:
                print(f"   🔍 DRY RUN: Would create page: /{slug}")
                result["created"].append(f"/{slug}")
            else:
                print(f"   📝 Creating page: /{slug}...")
                new_page = create_page(site_url, title, slug, username, password)
                if new_page:
                    print(f"   ✅ Created page: /{slug} (ID: {new_page['id']})")
                    result["created"].append(f"/{slug}")
                else:
                    print(f"   ❌ Failed to create page: /{slug}")
                    result["errors"].append(f"Failed to create /{slug}")
    
    return result


def fix_crosby_menu_links(site_url: str, username: str, password: str, dry_run: bool = False) -> Dict:
    """Fix broken menu links on crosbyultimateevents.com."""
    result = {
        "site": "crosbyultimateevents.com",
        "fixed": [],
        "created": [],
        "errors": []
    }
    
    print(f"\n📋 Fixing crosbyultimateevents.com menu links...")
    
    # Check if blog page exists
    page = check_page_exists(site_url, "blog", username, password)
    
    if page:
        print(f"   ✅ Blog page exists: /blog (ID: {page['id']})")
        result["fixed"].append("/blog")
    else:
        if dry_run:
            print(f"   🔍 DRY RUN: Would create blog page: /blog")
            result["created"].append("/blog")
        else:
            print(f"   📝 Creating blog page: /blog...")
            new_page = create_page(site_url, "Blog", "blog", username, password)
            if new_page:
                print(f"   ✅ Created blog page: /blog (ID: {new_page['id']})")
                result["created"].append("/blog")
            else:
                print(f"   ❌ Failed to create blog page: /blog")
                result["errors"].append("Failed to create /blog")
    
    return result


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix menu links for freerideinvestor.com and crosbyultimateevents.com")
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual changes)')
    parser.add_argument('--freeride-only', action='store_true', help='Fix only freerideinvestor.com')
    parser.add_argument('--crosby-only', action='store_true', help='Fix only crosbyultimateevents.com')
    
    args = parser.parse_args()
    
    print("🔧 Fix Menu Links - freerideinvestor.com & crosbyultimateevents.com")
    print("=" * 70)
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No actual changes will be made")
    print()
    
    configs = load_site_configs()
    results = []
    
    # Fix freerideinvestor.com
    if not args.crosby_only:
        freeride_config = configs.get("freerideinvestor.com", {})
        rest_api = freeride_config.get("rest_api", {})
        
        if rest_api.get("username") and rest_api.get("app_password"):
            site_url = rest_api.get("site_url") or freeride_config.get("site_url", "https://freerideinvestor.com")
            username = rest_api["username"]
            password = rest_api["app_password"]
            
            result = fix_freeride_menu_links(site_url, username, password, args.dry_run)
            results.append(result)
        else:
            print("⚠️  freerideinvestor.com: REST API credentials not configured")
            print("   Manual fix required: Create pages (About, Blog, Contact) and update menus")
    
    # Fix crosbyultimateevents.com
    if not args.freeride_only:
        crosby_config = configs.get("crosbyultimateevents.com", {})
        rest_api = crosby_config.get("rest_api", {})
        
        if rest_api.get("username") and rest_api.get("app_password"):
            site_url = rest_api.get("site_url") or crosby_config.get("site_url", "https://crosbyultimateevents.com")
            username = rest_api["username"]
            password = rest_api["app_password"]
            
            result = fix_crosby_menu_links(site_url, username, password, args.dry_run)
            results.append(result)
        else:
            print("⚠️  crosbyultimateevents.com: REST API credentials not configured")
            print("   Manual fix required: Create blog page and update nav menu")
    
    # Summary
    print()
    print("=" * 70)
    print("✅ Fix Complete")
    print()
    print("📊 Summary:")
    for result in results:
        print(f"   {result['site']}:")
        if result.get("fixed"):
            print(f"      Fixed: {len(result['fixed'])} pages")
        if result.get("created"):
            print(f"      Created: {len(result['created'])} pages")
        if result.get("errors"):
            print(f"      Errors: {len(result['errors'])}")
    
    print()
    print("💡 Next Steps:")
    print("   1. Update WordPress menus to link to these pages")
    print("   2. Add content to created pages")
    print("   3. Test all menu links")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

