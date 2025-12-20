#!/usr/bin/env python3
"""
Analyze dadudekc.com Pages for Primary Offer Clarity
====================================================

Analyzes current page content to identify consulting vs developer tools
positioning conflicts and recommends clarifications.

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


def get_page_content(page_id: int):
    """Get page content by ID."""
    url = f"{API_BASE}/pages/{page_id}"
    response = requests.get(url, auth=AUTH, timeout=30)

    if response.status_code == 200:
        return response.json()
    return None


def analyze_offer_conflicts():
    """Analyze pages for offer conflicts."""
    print("🔍 Analyzing dadudekc.com pages for primary offer clarity...\n")

    # Key pages to analyze
    pages_to_check = [
        (5, "developer-tools", "Homepage"),
        (76, "about", "About"),
        (77, "services", "Services"),
    ]

    findings = []

    for page_id, slug, name in pages_to_check:
        print(f"📄 Analyzing {name} (ID: {page_id}, slug: {slug})...")
        page = get_page_content(page_id)

        if not page:
            print(f"  ⚠️  Could not fetch page")
            continue

        title = page.get("title", {}).get("rendered", "")
        content = page.get("content", {}).get("rendered", "")
        content_raw = page.get("content", {}).get("raw", "")

        # Analyze for consulting vs developer tools mentions
        consulting_keywords = [
            "consulting", "automation", "workflow", "save time", "streamline",
            "smoke session", "book a call", "work with me"
        ]
        dev_tools_keywords = [
            "developer tools", "tools", "software", "product", "store",
            "purchase", "buy", "download"
        ]

        consulting_count = sum(
            1 for kw in consulting_keywords if kw.lower() in (title + content).lower())
        dev_tools_count = sum(
            1 for kw in dev_tools_keywords if kw.lower() in (title + content).lower())

        # Check for positioning line
        has_positioning = "I build automation systems that save teams hours every week" in content

        findings.append({
            "page_id": page_id,
            "slug": slug,
            "name": name,
            "title": title,
            "consulting_mentions": consulting_count,
            "dev_tools_mentions": dev_tools_count,
            "has_positioning": has_positioning,
            "primary_offer": "consulting" if consulting_count > dev_tools_count else ("dev_tools" if dev_tools_count > 0 else "unclear"),
            "conflict": consulting_count > 0 and dev_tools_count > 0
        })

        print(f"  Title: {title[:60]}")
        print(f"  Consulting mentions: {consulting_count}")
        print(f"  Developer tools mentions: {dev_tools_count}")
        print(f"  Has positioning line: {has_positioning}")
        print(f"  Primary offer: {findings[-1]['primary_offer']}")
        print(f"  Conflict detected: {findings[-1]['conflict']}")
        print()

    # Summary
    print("📊 Analysis Summary:")
    print("=" * 60)

    conflicts = [f for f in findings if f["conflict"]]
    if conflicts:
        print(f"\n⚠️  {len(conflicts)} page(s) with offer conflicts:")
        for f in conflicts:
            print(
                f"  - {f['name']} ({f['slug']}): Mixes consulting and developer tools")
    else:
        print("\n✅ No conflicts detected")

    unclear = [f for f in findings if f["primary_offer"] == "unclear"]
    if unclear:
        print(f"\n⚠️  {len(unclear)} page(s) with unclear primary offer:")
        for f in unclear:
            print(f"  - {f['name']} ({f['slug']}): Needs clearer positioning")

    # Recommendations
    print("\n💡 Recommendations:")
    print("=" * 60)

    homepage = next(
        (f for f in findings if f["slug"] == "developer-tools"), None)
    if homepage and homepage["slug"] == "developer-tools":
        print("1. Homepage slug 'developer-tools' conflicts with consulting positioning")
        print("   → Consider renaming homepage slug to 'home' or updating title")

    if conflicts:
        print("2. Pages with conflicts should be split or clarified:")
        for f in conflicts:
            print(
                f"   - {f['name']}: Choose ONE primary offer (consulting OR developer tools)")

    if unclear:
        print("3. Pages with unclear offers need stronger positioning:")
        for f in unclear:
            print(f"   - {f['name']}: Add clear value proposition and CTA")

    return findings


def main():
    """Main execution."""
    findings = analyze_offer_conflicts()

    print("\n✅ Analysis complete!")
    print("\n📋 Next steps:")
    print("  1. Review findings above")
    print("  2. Create implementation plan for offer clarification")
    print("  3. Update pages to have single, clear primary offer")


if __name__ == "__main__":
    main()




