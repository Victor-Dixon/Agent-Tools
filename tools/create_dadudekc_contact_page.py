#!/usr/bin/env python3
"""
Create Contact Page with Lead Capture Form for dadudekc.com
==========================================================

Creates a contact page with a lightweight lead capture form (name + email + context)
wired to redirect to the thank-you page after submission.

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

POSITIONING_LINE = "I build automation systems that save teams hours every week."


def find_page_by_slug(slug: str):
    """Find page by slug."""
    url = f"{API_BASE}/pages"
    params = {"slug": slug, "per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        pages = response.json()
        return pages[0] if pages else None
    return None


def create_contact_page():
    """Create contact page with lead capture form."""
    print("📝 Creating contact page with lead capture form...")

    # Check if page already exists
    page = find_page_by_slug("contact")
    if page:
        print(f"  ⏭️  Contact page already exists (ID: {page['id']})")
        return page

    # Create contact page content with form
    positioning_html = f'<p class="positioning-line" style="margin-bottom:2rem;font-size:1.25rem;font-weight:600;color:#2a5298"><strong>{POSITIONING_LINE}</strong></p>'

    content = f"""<!-- wp:group {{"align":"full","style":{{"spacing":{{"padding":{{"top":"4rem","bottom":"4rem"}},"margin":{{"top":"0","bottom":"0"}}}},"layout":{{"type":"constrained"}}}} -->
<div class="wp-block-group alignfull" style="margin-top:0;margin-bottom:0;padding-top:4rem;padding-bottom:4rem">
    <!-- wp:paragraph -->
    {positioning_html}
    <!-- /wp:paragraph -->
    
    <!-- wp:heading {{"level":1,"style":{{"spacing":{{"margin":{{"bottom":"1rem"}}}}}} -->
    <h1 style="margin-bottom:1rem">Get in Touch</h1>
    <!-- /wp:heading -->
    
    <!-- wp:paragraph {{"style":{{"spacing":{{"margin":{{"bottom":"2rem"}}}}}} -->
    <p style="margin-bottom:2rem">Ready to automate your workflow? Let's discuss how I can help streamline your operations.</p>
    <!-- /wp:paragraph -->
    
    <!-- wp:html -->
    <form action="/thank-you" method="GET" style="max-width:600px;margin:0 auto">
        <div style="margin-bottom:1.5rem">
            <label for="name" style="display:block;margin-bottom:0.5rem;font-weight:600">Name *</label>
            <input type="text" id="name" name="name" required style="width:100%;padding:0.75rem;border:1px solid #ccc;border-radius:0.25rem;font-size:1rem" />
        </div>
        
        <div style="margin-bottom:1.5rem">
            <label for="email" style="display:block;margin-bottom:0.5rem;font-weight:600">Email *</label>
            <input type="email" id="email" name="email" required style="width:100%;padding:0.75rem;border:1px solid #ccc;border-radius:0.25rem;font-size:1rem" />
        </div>
        
        <div style="margin-bottom:1.5rem">
            <label for="context" style="display:block;margin-bottom:0.5rem;font-weight:600">Tell me about your project *</label>
            <textarea id="context" name="context" rows="5" required style="width:100%;padding:0.75rem;border:1px solid #ccc;border-radius:0.25rem;font-size:1rem;font-family:inherit"></textarea>
        </div>
        
        <div style="margin-top:2rem">
            <button type="submit" style="background-color:#2a5298;color:white;padding:1rem 2rem;border:none;border-radius:0.5rem;font-size:1rem;font-weight:600;cursor:pointer;width:100%">Send Message</button>
        </div>
    </form>
    <!-- /wp:html -->
</div>
<!-- /wp:group -->"""

    # Create page via REST API
    url = f"{API_BASE}/pages"
    data = {
        "title": "Contact",
        "slug": "contact",
        "content": content.strip(),
        "status": "publish"
    }
    response = requests.post(url, json=data, auth=AUTH, timeout=30)

    if response.status_code == 201:
        page = response.json()
        page_id = page.get("id")
        print(f"  ✅ Created contact page (ID: {page_id})")
        print(f"  📋 URL: {SITE_URL}/contact")
        return page
    else:
        print(f"  ⚠️  Failed to create contact page: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None


def main():
    """Main execution."""
    print("🔧 Creating contact page with lead capture form for dadudekc.com...\n")

    page = create_contact_page()

    if page:
        print("\n✅ Contact page created successfully!")
        print(f"📋 View at: {SITE_URL}/contact")
        print("\n📋 Form features:")
        print("  - Name field (required)")
        print("  - Email field (required)")
        print("  - Context/Project description (required)")
        print("  - Redirects to /thank-you after submission")
        print("\n💡 Note: Form currently uses GET method for simplicity.")
        print("   For production, consider integrating with Contact Form 7 or WPForms")
        print("   for proper form handling and email notifications.")
    else:
        print("\n⚠️  Failed to create contact page")


if __name__ == "__main__":
    main()




