#!/usr/bin/env python3
"""
Implement Unified Positioning Line on dadudekc.com
=================================================

Implements "I build automation systems that save teams hours every week." 
site-wide across key pages (Home, About, Services) as per ad-readiness audit.

Author: Agent-2
V2 Compliant: <300 lines
"""

import json
import sys
import re
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load credentials
creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
with open(creds_file) as f:
    creds_data = json.load(f)

SITE_CONFIG = creds_data["dadudekc.com"]
SITE_URL = SITE_CONFIG["site_url"]
USERNAME = SITE_CONFIG["username"]
APP_PASSWORD = SITE_CONFIG["app_password"]

API_BASE = f"{SITE_URL}/wp-json/wp/v2"
AUTH = HTTPBasicAuth(USERNAME, APP_PASSWORD.replace(" ", ""))

POSITIONING_LINE = "I build automation systems that save teams hours every week."
POSITIONING_TAGLINE = "Automation systems that save teams hours every week."


def find_page_by_slug(slug: str):
    """Find page by slug."""
    url = f"{API_BASE}/pages"
    params = {"slug": slug, "per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        pages = response.json()
        return pages[0] if pages else None
    return None


def add_positioning_to_content(content: str, placement: str = "top") -> str:
    """Add positioning line to content."""
    positioning_html = f'<p class="positioning-line" style="font-size: 1.25rem; font-weight: 600; color: #2a5298; margin-bottom: 1.5rem;"><strong>{POSITIONING_LINE}</strong></p>'

    if placement == "top":
        # Add at the beginning of content
        if positioning_html not in content:
            # Find first paragraph or heading
            first_p = re.search(r'<p[^>]*>', content)
            if first_p:
                return content[:first_p.start()] + positioning_html + content[first_p.start():]
            else:
                return positioning_html + content
    elif placement == "hero":
        # Replace existing hero/manifesto content
        # Look for common hero patterns
        hero_patterns = [
            r'<h1[^>]*>.*?</h1>',
            r'<h2[^>]*>.*?</h2>',
        ]
        for pattern in hero_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                # Insert positioning after heading
                pos = match.end()
                if positioning_html not in content[:pos+100]:
                    return content[:pos] + positioning_html + content[pos:]

    return content


def create_page(slug: str, title: str, content: str):
    """Create a new page."""
    url = f"{API_BASE}/pages"
    data = {
        "title": title,
        "slug": slug,
        "content": content,
        "status": "publish"
    }
    response = requests.post(url, json=data, auth=AUTH, timeout=30)
    if response.status_code == 201:
        return response.json()
    return None


def update_page(page_id: int, content: str, title: str = None):
    """Update page content."""
    url = f"{API_BASE}/pages/{page_id}"
    data = {"content": content}
    if title:
        data["title"] = title

    response = requests.post(url, json=data, auth=AUTH, timeout=30)
    return response.status_code == 200


def update_homepage():
    """Update homepage with positioning line."""
    print("🏠 Updating homepage...")

    # Try multiple possible homepage slugs
    page = None
    for slug in ["home", "developer-tools"]:
        page = find_page_by_slug(slug)
        if page:
            break

    if not page:
        # Try front page (first page by menu order)
        url = f"{API_BASE}/pages"
        params = {"per_page": 1, "orderby": "menu_order", "order": "asc"}
        response = requests.get(url, params=params, auth=AUTH, timeout=30)
        if response.status_code == 200:
            pages = response.json()
            page = pages[0] if pages else None

    if not page:
        print("  ⚠️  Homepage not found")
        return False

    page_id = page["id"]
    current_content = page.get("content", {}).get("raw", "")

    # Check if positioning already exists
    if POSITIONING_LINE in current_content:
        print(f"  ⏭️  Positioning line already present (Page ID: {page_id})")
        return True

    # Add positioning to hero section
    updated_content = add_positioning_to_content(
        current_content, placement="hero")

    if update_page(page_id, updated_content):
        print(f"  ✅ Updated homepage (ID: {page_id})")
        return True
    else:
        print(f"  ⚠️  Failed to update homepage (ID: {page_id})")
        return False


def update_about_page():
    """Update About page with positioning line."""
    print("👤 Updating About page...")

    page = find_page_by_slug("about")

    # Create page if it doesn't exist
    if not page:
        print("  📝 Creating About page...")
        initial_content = f'<p class="positioning-line" style="font-size: 1.25rem; font-weight: 600; color: #2a5298; margin-bottom: 1.5rem;"><strong>{POSITIONING_LINE}</strong></p><h2>About</h2><p>I help teams automate their workflows to save hours every week.</p>'
        page = create_page("about", "About", initial_content)
        if page:
            page_id = page.get("id")
            print(f"  ✅ Created About page (ID: {page_id})")
            return True
        else:
            print("  ⚠️  Failed to create About page")
            return False

    page_id = page["id"]
    current_content = page.get("content", {}).get("raw", "")

    # Check if positioning already exists
    if POSITIONING_LINE in current_content:
        print(f"  ⏭️  Positioning line already present (Page ID: {page_id})")
        return True

    # Add positioning at top
    updated_content = add_positioning_to_content(
        current_content, placement="top")

    if update_page(page_id, updated_content):
        print(f"  ✅ Updated About page (ID: {page_id})")
        return True
    else:
        print(f"  ⚠️  Failed to update About page (ID: {page_id})")
        return False


def update_services_page():
    """Update Services page with positioning line."""
    print("🛠️  Updating Services page...")

    page = find_page_by_slug("services")

    # Create page if it doesn't exist
    if not page:
        print("  📝 Creating Services page...")
        initial_content = f'<p class="positioning-line" style="font-size: 1.25rem; font-weight: 600; color: #2a5298; margin-bottom: 1.5rem;"><strong>{POSITIONING_LINE}</strong></p><h2>Services</h2><p>I offer automation consulting and custom development services to help teams save time and reduce manual work.</p>'
        page = create_page("services", "Services", initial_content)
        if page:
            page_id = page.get("id")
            print(f"  ✅ Created Services page (ID: {page_id})")
            return True
        else:
            print("  ⚠️  Failed to create Services page")
            return False

    page_id = page["id"]
    current_content = page.get("content", {}).get("raw", "")

    # Check if positioning already exists
    if POSITIONING_LINE in current_content:
        print(f"  ⏭️  Positioning line already present (Page ID: {page_id})")
        return True

    # Add positioning at top
    updated_content = add_positioning_to_content(
        current_content, placement="top")

    if update_page(page_id, updated_content):
        print(f"  ✅ Updated Services page (ID: {page_id})")
        return True
    else:
        print(f"  ⚠️  Failed to update Services page (ID: {page_id})")
        return False


def main():
    """Main execution."""
    print("🔧 Implementing unified positioning line on dadudekc.com...\n")
    print(f"Positioning line: \"{POSITIONING_LINE}\"\n")

    results = []

    # Update key pages
    results.append(("Homepage", update_homepage()))
    results.append(("About", update_about_page()))
    results.append(("Services", update_services_page()))

    # Summary
    print("\n📊 Summary:")
    updated_count = sum(1 for _, success in results if success)
    for name, success in results:
        status = "✅" if success else "⚠️"
        print(f"  {status} {name}")

    if updated_count > 0:
        print(
            f"\n✅ Positioning unification complete! ({updated_count} page(s) updated)")
    else:
        print("\n⏭️  No pages needed updates (positioning may already be present)")


if __name__ == "__main__":
    main()




