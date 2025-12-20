#!/usr/bin/env python3
"""
Fix Dream.OS Article Learn More Links on dadudekc.com
=====================================================

Fixes "Learn More" list so links render as proper hyperlinks instead of raw Markdown/relative file paths.

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


def find_dreamos_post():
    """Find Dream.OS article post."""
    url = f"{API_BASE}/posts"
    params = {"per_page": 100, "search": "Dream"}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        posts = response.json()
        for post in posts:
            title = post.get("title", {}).get("rendered", "")
            slug = post.get("slug", "")
            if "dream" in title.lower() or "dream" in slug.lower():
                return post
    return None


def fix_learnmore_links(content: str) -> str:
    """Fix Learn More links from markdown/relative paths to proper hyperlinks."""
    # Pattern to find "Learn More:" sections with list items
    # Look for patterns like:
    # - [text](relative/path)
    # - text (relative/path)
    # - raw markdown links

    # Fix markdown-style links: [text](path) -> <a href="path">text</a>
    content = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2" style="color: #2a5298; text-decoration: none; font-weight: 500;">\1</a>',
        content
    )

    # Fix relative file paths in Learn More sections
    # Look for patterns like "docs/blog/file.md" or "./file.md"
    learnmore_pattern = r'(<strong>Learn More:</strong>.*?)(<li[^>]*>.*?</li>)'

    def fix_relative_paths(match):
        section = match.group(0)
        # Replace relative paths with proper URLs
        section = re.sub(
            r'(docs/blog/|\./)([^"\s]+\.md)',
            r'https://dadudekc.com/\2',
            section
        )
        return section

    content = re.sub(learnmore_pattern, fix_relative_paths,
                     content, flags=re.DOTALL | re.IGNORECASE)

    # Ensure list items with links are properly formatted
    # Convert raw text links to HTML links in list items
    content = re.sub(
        r'<li[^>]*>([^<]+)(https?://[^\s<]+)([^<]*)</li>',
        r'<li style="margin: 0.5rem 0;"><a href="\2" style="color: #2a5298; text-decoration: none; font-weight: 500;">\1</a>\3</li>',
        content
    )

    return content


def update_post(post_id: int, content: str):
    """Update post content."""
    url = f"{API_BASE}/posts/{post_id}"
    response = requests.post(
        url,
        json={"content": content},
        auth=AUTH,
        timeout=30
    )
    return response.status_code == 200


def main():
    """Main execution."""
    print("🔧 Fixing Dream.OS article Learn More links on dadudekc.com...\n")

    # Find Dream.OS post
    post = find_dreamos_post()
    if not post:
        print("❌ Dream.OS article not found")
        sys.exit(1)

    post_id = post["id"]
    post_title = post.get("title", {}).get("rendered", "")
    print(f"✅ Found post: '{post_title[:60]}...' (ID: {post_id})")

    # Get current content
    content = post.get("content", {}).get("rendered", "")
    original_content = post.get("content", {}).get("raw", content)

    # Check if Learn More section exists
    if "Learn More" not in content and "Learn More" not in original_content:
        print("⏭️  No 'Learn More' section found in post")
        sys.exit(0)

    # Fix links
    print("\n🔧 Fixing Learn More links...")
    fixed_content = fix_learnmore_links(original_content)

    if fixed_content == original_content:
        print("⏭️  No changes needed (links already properly formatted)")
        sys.exit(0)

    # Update post
    if update_post(post_id, fixed_content):
        print(f"✅ Updated post (ID: {post_id})")
        print("✅ Learn More links fixed")
    else:
        print(f"⚠️  Failed to update post (ID: {post_id})")
        sys.exit(1)

    print("\n✅ Dream.OS article Learn More links fix complete!")


if __name__ == "__main__":
    main()




