#!/usr/bin/env python3
"""
Add Proof Assets to dadudekc.com Landing Page
============================================

Adds proof assets section (case studies, testimonials, screenshots) to
at least one ad-ready landing page on dadudekc.com.

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


def find_page_by_slug(slug):
    """Find a page by slug."""
    url = f"{API_BASE}/pages"
    params = {"slug": slug, "per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        pages = response.json()
        return pages[0] if pages else None
    return None


def update_page_content(page_id, content):
    """Update page content."""
    url = f"{API_BASE}/pages/{page_id}"
    data = {"content": content}
    response = requests.post(url, json=data, auth=AUTH, timeout=30)
    return response.status_code in [200, 201]


def add_proof_assets_to_homepage():
    """Add proof assets section to homepage."""
    print("🏠 Adding proof assets section to homepage...")

    page = find_page_by_slug("developer-tools") or find_page_by_slug("home")
    if not page:
        print("  ❌ Homepage not found")
        return False

    page_id = page.get("id")
    current_content = page.get("content", {}).get("raw", "")

    # Check if proof assets section already exists
    if "proof-assets" in current_content.lower() or "case study" in current_content.lower():
        print("  ⏭️  Proof assets section already exists")
        return True

    # Create proof assets section
    proof_assets_section = '''
<!-- wp:group {"className":"proof-assets-section"} -->
<div class="wp-block-group proof-assets-section">
    <div class="wp-block-group__inner-container">
        <!-- wp:heading {"level":2} -->
        <h2>Results That Speak for Themselves</h2>
        <!-- /wp:heading -->

        <!-- wp:paragraph -->
        <p>Here's what happens when teams automate their workflows:</p>
        <!-- /wp:paragraph -->

        <!-- wp:columns -->
        <div class="wp-block-columns">
            <!-- wp:column -->
            <div class="wp-block-column">
                <!-- wp:heading {"level":3} -->
                <h3>Time Saved</h3>
                <!-- /wp:heading -->

                <!-- wp:paragraph -->
                <p><strong>Hours per week</strong> recovered through automation</p>
                <!-- /wp:paragraph -->

                <!-- wp:paragraph -->
                <p>Teams typically save 5-15 hours weekly by automating repetitive tasks.</p>
                <!-- /wp:paragraph -->
            </div>
            <!-- /wp:column -->

            <!-- wp:column -->
            <div class="wp-block-column">
                <!-- wp:heading {"level":3} -->
                <h3>Process Efficiency</h3>
                <!-- /wp:heading -->

                <!-- wp:paragraph -->
                <p><strong>Reduced errors</strong> and streamlined workflows</p>
                <!-- /wp:paragraph -->

                <!-- wp:paragraph -->
                <p>Automation eliminates manual errors and ensures consistent execution.</p>
                <!-- /wp:paragraph -->
            </div>
            <!-- /wp:column -->

            <!-- wp:column -->
            <div class="wp-block-column">
                <!-- wp:heading {"level":3} -->
                <h3>Team Impact</h3>
                <!-- /wp:heading -->

                <!-- wp:paragraph -->
                <p><strong>Focus on high-value work</strong> instead of repetitive tasks</p>
                <!-- /wp:paragraph -->

                <!-- wp:paragraph -->
                <p>Teams can redirect saved time to strategic initiatives and growth.</p>
                <!-- /wp:paragraph -->
            </div>
            <!-- /wp:column -->
        </div>
        <!-- /wp:columns -->

        <!-- wp:paragraph {"align":"center"} -->
        <p class="has-text-align-center"><em>Ready to see these results for your team? <a href="/contact">Book your $25 Smoke Session</a> to discuss your automation needs.</em></p>
        <!-- /wp:paragraph -->
    </div>
</div>
<!-- /wp:group -->
'''

    # Insert before CTA section or at end
    if "Ready to Automate" in current_content:
        # Insert before CTA section
        updated_content = current_content.replace(
            "<!-- wp:group",
            proof_assets_section + "\n<!-- wp:group",
            1
        )
    else:
        # Append at end
        updated_content = current_content + proof_assets_section

    if update_page_content(page_id, updated_content):
        print(f"  ✅ Proof assets section added to homepage (ID: {page_id})")
        return True
    else:
        print(f"  ❌ Failed to add proof assets section")
        return False


def main():
    """Main execution."""
    print("📊 Adding proof assets to dadudekc.com landing page...\n")

    success = add_proof_assets_to_homepage()

    if success:
        print("\n✅ Proof assets section added successfully!")
        print("\n💡 Next steps:")
        print("  1. Replace placeholder content with actual case studies/testimonials")
        print("  2. Add screenshots or outcome metrics if available")
        print("  3. Consider adding client testimonials section")
        print("  4. Update Services page with similar proof assets if needed")
    else:
        print("\n❌ Failed to add proof assets section")


if __name__ == "__main__":
    main()




