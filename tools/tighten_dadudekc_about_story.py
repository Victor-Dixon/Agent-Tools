#!/usr/bin/env python3
"""
Tighten dadudekc.com About Story
================================

Updates About page to connect engineering background → consulting offers,
making the transition from technical expertise to business value clear.

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


def get_about_page():
    """Get About page."""
    url = f"{API_BASE}/pages/76"  # About page ID
    response = requests.get(url, auth=AUTH, timeout=30)

    if response.status_code == 200:
        return response.json()
    return None


def update_about_story():
    """Update About page with engineering → consulting story."""
    print("📝 Tightening About story to connect engineering → consulting...\n")

    page = get_about_page()
    if not page:
        print("  ⚠️  Could not fetch About page")
        return False

    # Create enhanced About content connecting engineering to consulting
    positioning_html = f'<p class="positioning-line" style="font-size: 1.25rem; font-weight: 600; color: #2a5298; margin-bottom: 1.5rem;"><strong>{POSITIONING_LINE}</strong></p>'

    content = f"""{positioning_html}
<!-- wp:heading {{"level":2}} -->
<h2>From Engineering to Business Impact</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>I'm an engineer who builds automation systems that save teams hours every week. After years of developing tools and systems, I've learned that the real value isn't in the code—it's in the time and stress you eliminate for your team.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level":3}} -->
<h3>Why I Consult</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Most teams have repetitive tasks that eat up hours every week. Manual processes, data entry, report generation, workflow coordination—these are the bottlenecks that slow down growth and burn out your team.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>I help teams identify these bottlenecks and build automation systems that eliminate them. The result? Your team gets time back to focus on high-value work, and you get measurable ROI from reduced manual effort.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level":3}} -->
<h3>What You Get</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>When you work with me, you get:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>Clear automation strategy</strong> - We identify the highest-impact automation opportunities in your workflow</li>
<li><strong>Custom-built solutions</strong> - Systems designed specifically for your team's needs, not generic tools</li>
<li><strong>Measurable results</strong> - Time saved, errors reduced, processes streamlined</li>
<li><strong>Ongoing support</strong> - Your automation systems evolve as your needs change</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>Ready to automate your workflow? <a href="/contact">Let's discuss how I can help</a>.</p>
<!-- /wp:paragraph -->
"""

    # Update page
    url = f"{API_BASE}/pages/76"
    data = {
        "content": content.strip()
    }

    response = requests.post(url, json=data, auth=AUTH, timeout=30)

    if response.status_code == 200:
        print("  ✅ Updated About page with engineering → consulting story")
        return True
    else:
        print(f"  ⚠️  Failed to update About page: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return False


def main():
    """Main execution."""
    print("🔧 Tightening dadudekc.com About story...\n")

    success = update_about_story()

    if success:
        print("\n✅ About story updated successfully!")
        print("📋 Changes:")
        print("  - Added engineering background context")
        print("  - Connected technical expertise to business value")
        print("  - Clear transition: Engineering → Consulting")
        print("  - Added value proposition and CTA")
    else:
        print("\n⚠️  Failed to update About story")


if __name__ == "__main__":
    main()




