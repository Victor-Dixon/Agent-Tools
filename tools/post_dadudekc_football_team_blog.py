#!/usr/bin/env python3
"""
Post Football Team Company Blog to dadudekc.com
==============================================

Posts the "Building Your Company Like a Football Team" blog post.

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

# Blog content
TITLE = "Building Your Company Like a Football Team"

# Read content from template file
template_file = project_root / "docs" / "blog" / \
    "dadudekc_company_football_team_template.md"
with open(template_file, 'r', encoding='utf-8') as f:
    template_content = f.read()

# Extract the HTML content (everything after the first line)
lines = template_content.split('\n')
# Skip the first markdown header line and get the HTML content
CONTENT = '\n'.join(lines[2:])  # Skip "# Building..." and empty line

EXCERPT = "Every role matters. Every position has a purpose. Here's how to think about your team structure using a football team framework."

TAGS = ["business", "leadership", "team-building",
        "startups", "management", "strategy"]
CATEGORY = "Development"


def get_or_create_category(category_name: str):
    """Get or create a category."""
    url = f"{API_BASE}/categories"
    params = {"search": category_name, "per_page": 100}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        categories = response.json()
        for cat in categories:
            if cat["name"].lower() == category_name.lower():
                return cat["id"]

    # Create category if not found
    url = f"{API_BASE}/categories"
    data = {"name": category_name}
    response = requests.post(url, json=data, auth=AUTH, timeout=30)

    if response.status_code == 201:
        return response.json()["id"]

    return None


def get_or_create_tags(tag_names: list):
    """Get or create tags, return list of tag IDs."""
    tag_ids = []

    for tag_name in tag_names:
        # Try to get existing tag
        url = f"{API_BASE}/tags"
        params = {"search": tag_name, "per_page": 100}
        response = requests.get(url, params=params, auth=AUTH, timeout=30)

        if response.status_code == 200:
            tags = response.json()
            for tag in tags:
                if tag["name"].lower() == tag_name.lower():
                    tag_ids.append(tag["id"])
                    break
            else:
                # Create tag if not found
                url = f"{API_BASE}/tags"
                data = {"name": tag_name}
                response = requests.post(url, json=data, auth=AUTH, timeout=30)
                if response.status_code == 201:
                    tag_ids.append(response.json()["id"])

    return tag_ids


def check_existing_post(title: str):
    """Check if post with this title already exists."""
    url = f"{API_BASE}/posts"
    params = {"search": title, "per_page": 10}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        posts = response.json()
        for post in posts:
            if post["title"]["rendered"] == title:
                return post
    return None


def create_post():
    """Create the blog post."""
    print(f"📝 Posting blog to {SITE_URL}...")

    # Check if post already exists
    existing = check_existing_post(TITLE)
    if existing:
        print(f"  ⚠️  Post already exists: {existing['link']}")
        return existing

    # Get or create category
    print(f"  📂 Getting category: {CATEGORY}")
    category_id = get_or_create_category(CATEGORY)
    if not category_id:
        print(f"  ⚠️  Could not get/create category, continuing anyway...")

    # Get or create tags
    print(f"  🏷️  Getting/creating tags: {', '.join(TAGS)}")
    tag_ids = get_or_create_tags(TAGS)

    # Prepare post data
    post_data = {
        "title": TITLE,
        "content": CONTENT,
        "excerpt": EXCERPT,
        "status": "publish",
        "format": "standard",
    }

    if category_id:
        post_data["categories"] = [category_id]

    if tag_ids:
        post_data["tags"] = tag_ids

    # Create post
    print(f"  ✍️  Creating post: {TITLE}")
    url = f"{API_BASE}/posts"
    response = requests.post(url, json=post_data, auth=AUTH, timeout=30)

    if response.status_code == 201:
        post = response.json()
        print(f"  ✅ Post created successfully!")
        print(f"     Post ID: {post['id']}")
        print(f"     URL: {post['link']}")
        print(f"     Status: {post['status']}")
        return post
    else:
        print(f"  ❌ Error creating post: {response.status_code}")
        print(f"     Response: {response.text}")
        return None


def main():
    """Main execution."""
    print("🚀 Posting football team company blog to dadudekc.com\n")

    post = create_post()

    if post:
        print(f"\n✅ Blog post published successfully!")
        print(f"   View at: {post['link']}")
    else:
        print(f"\n❌ Failed to publish blog post")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
