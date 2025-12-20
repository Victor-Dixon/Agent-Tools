#!/usr/bin/env python3
"""
Create Thank-You Page for dadudekc.com CTA Submissions
======================================================

Creates a dedicated thank-you page for CTA form submissions as part of
ad-readiness improvements.

Author: Agent-2
V2 Compliant: <300 lines
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


def find_page_by_slug(slug: str):
    """Find page by slug."""
    url = f"{API_BASE}/pages"
    params = {"slug": slug, "per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        pages = response.json()
        return pages[0] if pages else None
    return None


def create_thank_you_page():
    """Create thank-you page for CTA submissions."""
    print("📝 Creating thank-you page for CTA submissions...")

    # Check if page already exists
    page = find_page_by_slug("thank-you")
    if page:
        print(f"  ⏭️  Thank-you page already exists (ID: {page['id']})")
        return page

    # Create thank-you page content
    content = """
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"6rem","bottom":"6rem"},"margin":{"top":"0","bottom":"0"}}},"layout":{"type":"constrained"}} -->
<div class="wp-block-group alignfull" style="margin-top:0;margin-bottom:0;padding-top:6rem;padding-bottom:6rem">
    <!-- wp:columns {"align":"wide"} -->
    <div class="wp-block-columns alignwide">
        <!-- wp:column {"width":"100%"} -->
        <div class="wp-block-column" style="flex-basis:100%">
            <!-- wp:heading {"textAlign":"center","level":1,"style":{"typography":{"fontSize":"3rem"},"spacing":{"margin":{"bottom":"1rem"}}}} -->
            <h1 class="wp-block-heading has-text-align-center" style="margin-bottom:1rem;font-size:3rem">Thank You!</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph {"align":"center","style":{"typography":{"fontSize":"1.25rem"},"spacing":{"margin":{"bottom":"2rem"}}}} -->
            <p class="has-text-align-center" style="margin-bottom:2rem;font-size:1.25rem">I've received your message and will get back to you soon.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:paragraph {"align":"center","style":{"spacing":{"margin":{"bottom":"2rem"}}}} -->
            <p class="has-text-align-center" style="margin-bottom:2rem">I build automation systems that save teams hours every week. I'm excited to discuss how I can help streamline your operations.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:spacer {"height":"2rem"} -->
            <div style="height:2rem" aria-hidden="true" class="wp-block-spacer"></div>
            <!-- /wp:spacer -->
            
            <!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
            <div class="wp-block-buttons">
                <!-- wp:button {"backgroundColor":"primary","textColor":"secondary","width":100,"style":{"border":{"radius":"0.5rem"},"spacing":{"padding":{"top":"1rem","bottom":"1rem","left":"2rem","right":"2rem"}}}} -->
                <div class="wp-block-button has-custom-width wp-block-button__width-100" style="width:100%">
                    <a class="wp-block-button__link has-secondary-color has-primary-background-color has-text-color has-background wp-element-button" href="/" style="border-radius:0.5rem;padding-top:1rem;padding-bottom:1rem;padding-left:2rem;padding-right:2rem">Return to Home</a>
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

    # Create page via REST API
    url = f"{API_BASE}/pages"
    data = {
        "title": "Thank You",
        "slug": "thank-you",
        "content": content.strip(),
        "status": "publish"
    }
    response = requests.post(url, json=data, auth=AUTH, timeout=30)

    if response.status_code == 201:
        page = response.json()
        page_id = page.get("id")
        print(f"  ✅ Created thank-you page (ID: {page_id})")
        print(f"  📋 URL: {SITE_URL}/thank-you")
        return page
    else:
        print(f"  ⚠️  Failed to create thank-you page: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None


def main():
    """Main execution."""
    print("🔧 Creating thank-you page for dadudekc.com CTA submissions...\n")

    page = create_thank_you_page()

    if page:
        print("\n✅ Thank-you page created successfully!")
        print(f"📋 View at: {SITE_URL}/thank-you")
        print("\n💡 Next step: Update CTA form to redirect to /thank-you after submission")
    else:
        print("\n⚠️  Failed to create thank-you page")


if __name__ == "__main__":
    main()




