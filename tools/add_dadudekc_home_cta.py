#!/usr/bin/env python3
"""
Add Primary CTA Section to dadudekc.com Homepage
==================================================

Adds a clear primary CTA section with "Work with me" action button.

Author: Agent-2
"""

import json
import sys
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


def get_homepage():
    """Get homepage (front page)."""
    # Get all pages and find the one used as front page
    url = f"{API_BASE}/pages"
    params = {"per_page": 100}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)
    if response.status_code == 200:
        pages = response.json()

        # Check common homepage slugs
        for page in pages:
            slug = page.get("slug", "")
            if slug in ["home", "front-page", ""] or page.get("id") == 1:
                return page

        # If no specific homepage found, get the first page or check menu order
        if pages:
            # Sort by menu_order, then by ID
            pages_sorted = sorted(pages, key=lambda p: (
                p.get("menu_order", 999), p.get("id", 999)))
            return pages_sorted[0]

    # Also try posts endpoint (some sites use posts as homepage)
    url = f"{API_BASE}/posts"
    params = {"per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)
    if response.status_code == 200:
        posts = response.json()
        if posts:
            # Check if this is actually a page masquerading as post
            return posts[0]

    return None


def generate_cta_section() -> str:
    """Generate primary CTA section HTML."""
    cta_html = """
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"4rem","bottom":"4rem"},"margin":{"top":"0","bottom":"0"}}},"backgroundColor":"primary","layout":{"type":"constrained"}} -->
<div class="wp-block-group alignfull has-primary-background-color has-background" style="margin-top:0;margin-bottom:0;padding-top:4rem;padding-bottom:4rem">
    <!-- wp:columns {"align":"wide"} -->
    <div class="wp-block-columns alignwide">
        <!-- wp:column {"width":"100%"} -->
        <div class="wp-block-column" style="flex-basis:100%">
            <!-- wp:heading {"textAlign":"center","level":2,"style":{"typography":{"fontSize":"2.5rem"},"spacing":{"margin":{"bottom":"1rem"}}}} -->
            <h2 class="wp-block-heading has-text-align-center" style="margin-bottom:1rem;font-size:2.5rem">Ready to Automate Your Workflow?</h2>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph {"align":"center","style":{"spacing":{"margin":{"bottom":"2rem"}}}} -->
            <p class="has-text-align-center" style="margin-bottom:2rem">I build automation systems that save teams hours every week. Let's discuss how I can help streamline your operations.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
            <div class="wp-block-buttons">
                <!-- wp:button {"backgroundColor":"secondary","textColor":"primary","width":100,"style":{"border":{"radius":"0.5rem"},"spacing":{"padding":{"top":"1rem","bottom":"1rem","left":"2rem","right":"2rem"}}}} -->
                <div class="wp-block-button has-custom-width wp-block-button__width-100" style="width:100%">
                    <a class="wp-block-button__link has-primary-color has-secondary-background-color has-text-color has-background wp-element-button" href="/contact" style="border-radius:0.5rem;padding-top:1rem;padding-bottom:1rem;padding-left:2rem;padding-right:2rem">Work with Me</a>
                </div>
                <!-- /wp:button -->
            </div>
            <!-- /wp:buttons -->
        </div>
        <!-- /wp:column -->
    </div>
    <!-- /wp:columns -->
</div>
<!-- /wp:group -->
"""
    return cta_html


def update_homepage_with_cta(page_id: int, content: str) -> bool:
    """Update homepage with CTA section."""
    # Check if CTA section already exists
    if "Ready to Automate Your Workflow" in content or "Work with Me" in content:
        print("⏭️  CTA section already exists on homepage")
        return True

    # Add CTA section - insert before closing content or at end
    cta_section = generate_cta_section()

    # Try to insert before closing tags, or append at end
    if "</div>" in content and content.count("</div>") > 5:
        # Insert before last few closing divs
        parts = content.rsplit("</div>", 3)
        if len(parts) >= 2:
            content = parts[0] + cta_section + "</div>".join(parts[1:])
        else:
            content += cta_section
    else:
        content += cta_section

    # Update page
    url = f"{API_BASE}/pages/{page_id}"
    data = {"content": content}
    response = requests.post(url, json=data, auth=AUTH, timeout=30)

    if response.status_code == 200:
        print(f"✅ Updated homepage (ID: {page_id}) with CTA section")
        return True
    else:
        print(
            f"❌ Failed to update page: {response.status_code} - {response.text}")
        return False


def main():
    """Main execution."""
    print("🔧 Adding primary CTA section to dadudekc.com homepage...\n")

    # Get homepage
    homepage = get_homepage()
    if not homepage:
        print("❌ Could not find homepage")
        print("💡 Trying to get front page...")
        # Try posts endpoint for front page
        url = f"{API_BASE}/posts"
        params = {"per_page": 1}
        response = requests.get(url, params=params, auth=AUTH, timeout=30)
        if response.status_code == 200:
            posts = response.json()
            if posts:
                homepage = posts[0]
                print(f"✅ Found front page post (ID: {homepage['id']})")

    if not homepage:
        print("❌ Could not locate homepage to update")
        sys.exit(1)

    page_id = homepage["id"]
    content = homepage.get("content", {}).get("rendered", "")

    print(f"✅ Found homepage (ID: {page_id})")

    # Update with CTA
    success = update_homepage_with_cta(page_id, content)

    if success:
        print("\n✅ Primary CTA section added to homepage!")
        print(f"📋 View at: {SITE_URL}")
        print("💡 CTA button links to /contact - ensure Contact page exists")
    else:
        print("\n⚠️  Could not add CTA section automatically")
        print("💡 Manual steps:")
        print("   1. Go to WordPress admin → Pages → Home")
        print("   2. Add CTA section with 'Work with Me' button")
        print("   3. Link button to /contact page")


if __name__ == "__main__":
    main()
