#!/usr/bin/env python3
"""
Fix dadudekc.com CSS Duplicate Issue
=====================================

Removes embedded CSS from blog posts and documents how to add it to theme.
"""

import json
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("❌ Install required packages: pip install requests beautifulsoup4")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30

# Load credentials
config_path = project_root / ".deploy_credentials" / "blogging_api.json"
if not config_path.exists():
    print(f"❌ Config file not found: {config_path}")
    sys.exit(1)

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

site_config = config.get("dadudekc.com")
if not site_config:
    print("❌ dadudekc.com not found in config")
    sys.exit(1)

site_url = site_config["site_url"]
username = site_config["username"]
app_password = site_config["app_password"]
api_url = f"{site_url}/wp-json/wp/v2"

session = requests.Session()
session.auth = HTTPBasicAuth(username, app_password)

print("🔍 Fetching posts from dadudekc.com...\n")

# Fetch posts
response = session.get(
    f"{api_url}/posts", params={"per_page": 100}, timeout=TimeoutConstants.HTTP_DEFAULT)
if response.status_code != 200:
    print(f"❌ Failed to fetch posts: HTTP {response.status_code}")
    sys.exit(1)

posts = response.json()
print(f"✅ Found {len(posts)} post(s)\n")

# Extract CSS from first post
css_content = None
posts_to_fix = []

for post in posts:
    post_id = post.get('id')
    title = post.get('title', {}).get('rendered', '')
    content = post.get('content', {}).get('rendered', '')

    soup = BeautifulSoup(content, 'html.parser')
    style_tags = soup.find_all('style')

    if style_tags:
        # Extract CSS
        post_css = '\n'.join([tag.get_text() for tag in style_tags])

        if not css_content:
            css_content = post_css
            print(f"📝 Extracted CSS from post ID {post_id}: '{title}'")
            print(f"   CSS length: {len(css_content)} chars\n")

        # Remove style tags
        for tag in style_tags:
            tag.decompose()

        # Get clean content
        clean_content = str(soup)

        posts_to_fix.append({
            'id': post_id,
            'title': title,
            'original_content': content,
            'clean_content': clean_content,
            'has_css': len(style_tags) > 0
        })

        print(f"✅ Prepared fix for post ID {post_id}: '{title}'")

if not css_content:
    print("✅ No embedded CSS found - issue may already be fixed!")
    sys.exit(0)

# Save CSS for theme
css_output = Path("docs/blog/dadudekc_blog_css_for_theme.css")
css_output.parent.mkdir(parents=True, exist_ok=True)
css_output.write_text(css_content, encoding='utf-8')
print(f"\n✅ CSS saved to: {css_output}")
print(f"   This CSS should be added to your WordPress theme's style.css\n")

# Update posts (remove embedded CSS)
print("\n🔧 Removing embedded CSS from posts...\n")

for post_info in posts_to_fix:
    if not post_info['has_css']:
        continue

    update_url = f"{api_url}/posts/{post_info['id']}"

    update_data = {
        "content": post_info['clean_content']
    }

    try:
        update_response = session.post(
            update_url,
            json=update_data,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )

        if update_response.status_code in (200, 201):
            print(f"✅ Post ID {post_info['id']}: Removed embedded CSS")
        else:
            print(
                f"❌ Post ID {post_info['id']}: Failed - HTTP {update_response.status_code}")
            print(f"   Error: {update_response.text[:200]}")
    except Exception as e:
        print(f"❌ Post ID {post_info['id']}: Error - {e}")

print("\n" + "="*70)
print("📋 NEXT STEPS")
print("="*70)
print("\n1. Add CSS to WordPress Theme:")
print("   • Via WordPress Customizer: Appearance > Customize > Additional CSS")
print("   • Or add to theme's style.css file")
print(f"   • CSS file: {css_output}")
print("\n2. Verify posts display correctly after CSS removal")
print("3. Check that styling still works on both posts\n")

print("✅ CSS extraction and post cleanup complete!")
