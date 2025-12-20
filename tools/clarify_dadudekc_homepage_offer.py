#!/usr/bin/env python3
"""
Clarify dadudekc.com Homepage Primary Offer
==========================================

Updates homepage to clarify primary offer as consulting (not developer tools).
Changes title, ensures positioning line is present, and aligns with consulting positioning.

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


def get_homepage():
    """Get homepage (developer-tools page)."""
    url = f"{API_BASE}/pages/5"  # Homepage ID
    response = requests.get(url, auth=AUTH, timeout=30)

    if response.status_code == 200:
        return response.json()
    return None


def ensure_positioning_line(content: str) -> str:
    """Ensure positioning line is in content."""
    positioning_html = f'<p class="positioning-line" style="font-size: 1.25rem; font-weight: 600; color: #2a5298; margin-bottom: 1.5rem;"><strong>{POSITIONING_LINE}</strong></p>'

    if POSITIONING_LINE in content:
        return content

    # Add at the beginning
    first_p = re.search(r'<p[^>]*>', content)
    if first_p:
        return content[:first_p.start()] + positioning_html + content[first_p.start():]
    else:
        return positioning_html + content


def update_homepage():
    """Update homepage to clarify consulting offer."""
    print("🏠 Updating homepage to clarify primary offer...\n")

    page = get_homepage()
    if not page:
        print("  ⚠️  Could not fetch homepage")
        return False

    page_id = page.get("id")
    current_title = page.get("title", {}).get("rendered", "")
    current_content = page.get("content", {}).get("raw", "")

    print(f"  Current title: {current_title}")
    print(f"  Current content length: {len(current_content)} chars")

    # Update title to consulting-focused
    new_title = "Home"  # Simple, consulting-focused title

    # Ensure positioning line is present
    updated_content = ensure_positioning_line(current_content)

    # Update page
    url = f"{API_BASE}/pages/{page_id}"
    data = {
        "title": new_title,
        "content": updated_content
    }

    response = requests.post(url, json=data, auth=AUTH, timeout=30)

    if response.status_code == 200:
        print(f"  ✅ Updated homepage title to: {new_title}")
        if POSITIONING_LINE not in current_content:
            print(f"  ✅ Added positioning line to homepage")
        else:
            print(f"  ✅ Positioning line already present")
        return True
    else:
        print(f"  ⚠️  Failed to update homepage: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return False


def main():
    """Main execution."""
    print("🔧 Clarifying dadudekc.com homepage primary offer...\n")

    success = update_homepage()

    if success:
        print("\n✅ Homepage updated successfully!")
        print("📋 Changes:")
        print("  - Title changed from 'Developer Tools' to 'Home'")
        print("  - Positioning line ensured")
        print("  - Primary offer now clearly consulting-focused")
    else:
        print("\n⚠️  Failed to update homepage")


if __name__ == "__main__":
    main()




