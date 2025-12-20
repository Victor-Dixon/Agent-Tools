#!/usr/bin/env python3
"""
Map dadudekc.com Consulting CTA to Smoke Session
================================================

Updates CTAs across dadudekc.com to route to Smoke Session booking.
Smoke Session is a $25 consulting offer that should be the primary CTA.

Author: Agent-2
V2 Compliant: <300 lines
"""

import json
import re
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

# Smoke Session details
SMOKE_SESSION_URL = "/contact"  # Route to contact form for now
SMOKE_SESSION_TEXT = "Book $25 Smoke Session"
SMOKE_SESSION_DESCRIPTION = "A focused session to discuss your automation needs and explore solutions."


def find_page_by_slug(slug):
    """Find a page by slug."""
    url = f"{API_BASE}/pages"
    params = {"slug": slug, "per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        pages = response.json()
        return pages[0] if pages else None
    return None


def get_page_content(page_id):
    """Get page content."""
    url = f"{API_BASE}/pages/{page_id}"
    response = requests.get(url, auth=AUTH, timeout=30)

    if response.status_code == 200:
        return response.json()
    return None


def update_page_content(page_id, content, title=None):
    """Update page content."""
    url = f"{API_BASE}/pages/{page_id}"
    data = {"content": content}
    if title:
        data["title"] = title

    response = requests.post(url, json=data, auth=AUTH, timeout=30)
    return response.status_code in [200, 201]


def update_homepage_cta():
    """Update homepage CTA to reference Smoke Session."""
    print("🏠 Updating homepage CTA...")

    page = find_page_by_slug("developer-tools") or find_page_by_slug("home")
    if not page:
        print("  ❌ Homepage not found")
        return False

    page_id = page.get("id")
    current_content = page.get("content", {}).get("raw", "")

    # Check if CTA already mentions Smoke Session
    if "smoke session" in current_content.lower():
        print("  ⏭️  Homepage CTA already references Smoke Session")
        return True

    # Update CTA text to include Smoke Session
    # Look for existing CTA patterns
    cta_patterns = [
        (r'(Work with Me|Book a call|Get started|Contact me)', SMOKE_SESSION_TEXT),
        (r'(href=["\']/contact["\'])([^>]*>)([^<]+)',
         rf'\1\2{SMOKE_SESSION_TEXT}'),
    ]

    updated_content = current_content
    for pattern, replacement in cta_patterns:
        if re.search(pattern, updated_content, re.IGNORECASE):
            updated_content = re.sub(
                pattern, replacement, updated_content, flags=re.IGNORECASE)
            break

    # If no CTA found, add one
    if "smoke session" not in updated_content.lower():
        smoke_session_cta = f'''
<!-- wp:group -->
<div class="wp-block-group">
    <div class="wp-block-group__inner-container">
        <h2>Ready to Automate Your Workflow?</h2>
        <p>{SMOKE_SESSION_DESCRIPTION}</p>
        <p><a href="{SMOKE_SESSION_URL}" class="wp-block-button__link">Book $25 Smoke Session</a></p>
    </div>
</div>
<!-- /wp:group -->
'''
        # Insert before closing body or at end
        if "</body>" in updated_content:
            updated_content = updated_content.replace(
                "</body>", smoke_session_cta + "</body>")
        else:
            updated_content += smoke_session_cta

    if update_page_content(page_id, updated_content):
        print(
            f"  ✅ Homepage CTA updated to reference Smoke Session (ID: {page_id})")
        return True
    else:
        print(f"  ❌ Failed to update homepage CTA")
        return False


def update_contact_page_smoke_session():
    """Update contact page to mention Smoke Session."""
    print("📧 Updating contact page...")

    page = find_page_by_slug("contact")
    if not page:
        print("  ⏭️  Contact page not found, skipping")
        return False

    page_id = page.get("id")
    current_content = page.get("content", {}).get("raw", "")

    # Check if already mentions Smoke Session
    if "smoke session" in current_content.lower():
        print("  ⏭️  Contact page already mentions Smoke Session")
        return True

    # Add Smoke Session description to contact page
    smoke_session_intro = f'''
<!-- wp:paragraph -->
<p><strong>Book Your $25 Smoke Session</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>{SMOKE_SESSION_DESCRIPTION} Fill out the form below to get started.</p>
<!-- /wp:paragraph -->
'''

    # Insert after positioning line or at beginning
    if "positioning-line" in current_content:
        updated_content = current_content.replace(
            '</p>',
            '</p>' + smoke_session_intro,
            1
        )
    else:
        updated_content = smoke_session_intro + current_content

    if update_page_content(page_id, updated_content):
        print(
            f"  ✅ Contact page updated with Smoke Session info (ID: {page_id})")
        return True
    else:
        print(f"  ❌ Failed to update contact page")
        return False


def update_about_page_cta():
    """Update About page CTA to reference Smoke Session."""
    print("ℹ️  Updating About page CTA...")

    page = find_page_by_slug("about")
    if not page:
        print("  ⏭️  About page not found, skipping")
        return False

    page_id = page.get("id")
    current_content = page.get("content", {}).get("raw", "")

    # Check if already mentions Smoke Session
    if "smoke session" in current_content.lower():
        print("  ⏭️  About page CTA already references Smoke Session")
        return True

    # Update CTA links to mention Smoke Session
    updated_content = re.sub(
        r'(<a[^>]*href=["\']/contact["\'][^>]*>)([^<]+)(</a>)',
        rf'\1{SMOKE_SESSION_TEXT}\3',
        current_content,
        flags=re.IGNORECASE
    )

    if updated_content != current_content:
        if update_page_content(page_id, updated_content):
            print(f"  ✅ About page CTA updated (ID: {page_id})")
            return True

    print("  ⏭️  No CTA found to update on About page")
    return False


def main():
    """Main execution."""
    print("🔗 Mapping dadudekc.com consulting CTAs to Smoke Session...\n")

    results = []
    results.append(("Homepage", update_homepage_cta()))
    results.append(("Contact Page", update_contact_page_smoke_session()))
    results.append(("About Page", update_about_page_cta()))

    print("\n📊 Summary:")
    print("=" * 60)
    for page_name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {page_name}")

    successful = sum(1 for _, success in results if success)
    print(f"\n✅ Updated {successful}/{len(results)} pages")

    if successful > 0:
        print("\n💡 Next steps:")
        print("  1. Verify CTAs route correctly to Smoke Session booking")
        print("  2. Consider creating dedicated /smoke-session page if needed")
        print("  3. Update thank-you page to mention Smoke Session confirmation")


if __name__ == "__main__":
    main()




