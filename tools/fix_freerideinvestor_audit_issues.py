#!/usr/bin/env python3
"""
Fix FreeRideInvestor.com Audit Issues
=====================================

Implements P0/P1 fixes identified in site audit:
- Create missing pages (Blog, About, Contact)
- Fix broken premium CTA links
- Deduplicate TSLA posts
- Remove email from author byline
- Clean content formatting

Author: Agent-2
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load credentials
creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
with open(creds_file) as f:
    creds_data = json.load(f)

SITE_CONFIG = creds_data["freerideinvestor"]
SITE_URL = SITE_CONFIG["site_url"]
USERNAME = SITE_CONFIG["username"]
APP_PASSWORD = SITE_CONFIG["app_password"]

# WordPress REST API endpoints
API_BASE = f"{SITE_URL}/wp-json/wp/v2"
AUTH = HTTPBasicAuth(USERNAME, APP_PASSWORD.replace(" ", ""))


def create_page(title: str, slug: str, content: str = "") -> Optional[int]:
    """Create WordPress page via REST API."""
    url = f"{API_BASE}/pages"
    data = {
        "title": title,
        "slug": slug,
        "status": "publish",
        "content": content or f"<h1>{title}</h1><p>Content coming soon...</p>"
    }
    response = requests.post(url, json=data, auth=AUTH, timeout=30)
    if response.status_code == 201:
        page_id = response.json().get("id")
        print(f"✅ Created page: {title} (ID: {page_id})")
        return page_id
    else:
        print(
            f"❌ Failed to create page '{title}': {response.status_code} - {response.text}")
        return None


def get_page_by_slug(slug: str) -> Optional[Dict]:
    """Get page by slug."""
    url = f"{API_BASE}/pages"
    params = {"slug": slug, "per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)
    if response.status_code == 200:
        pages = response.json()
        return pages[0] if pages else None
    return None


def get_posts_by_slug_pattern(pattern: str) -> List[Dict]:
    """Get posts matching slug pattern."""
    url = f"{API_BASE}/posts"
    params = {"per_page": 100, "search": pattern}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)
    if response.status_code == 200:
        posts = response.json()
        # Filter by slug pattern
        return [p for p in posts if pattern in p.get("slug", "")]
    return []


def update_post(post_id: int, updates: Dict) -> bool:
    """Update WordPress post via REST API."""
    url = f"{API_BASE}/posts/{post_id}"
    response = requests.post(url, json=updates, auth=AUTH, timeout=30)
    if response.status_code == 200:
        print(f"✅ Updated post {post_id}")
        return True
    else:
        print(
            f"❌ Failed to update post {post_id}: {response.status_code} - {response.text}")
        return False


def fix_premium_cta_link(post_id: int, content: str) -> str:
    """Fix premium CTA link in post content."""
    # Replace /reports/... with /tsla-strategy-report-premium
    fixed = re.sub(
        r'href=["\']/reports/[^"\']+["\']',
        'href="/tsla-strategy-report-premium"',
        content
    )
    # Also fix any relative paths
    fixed = re.sub(
        r'href=["\']\.\.?/reports/[^"\']+["\']',
        'href="/tsla-strategy-report-premium"',
        fixed
    )
    return fixed


def remove_email_from_byline(content: str) -> str:
    """Remove email addresses from author byline."""
    # Remove email patterns in author sections
    fixed = re.sub(
        r'<p[^>]*class=["\'][^"\']*author[^"\']*["\'][^>]*>.*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}).*?</p>',
        lambda m: m.group(0).replace(m.group(1), ""),
        content,
        flags=re.DOTALL
    )
    # Also remove standalone email patterns in author context
    fixed = re.sub(
        r'By\s+[^<]+<[^>]+>([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        lambda m: m.group(0).replace(m.group(1), ""),
        fixed
    )
    return fixed


def clean_markdown_artifacts(content: str) -> str:
    """Remove markdown artifacts and fix formatting."""
    # Fix markdown links that weren't converted
    fixed = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
    # Fix markdown headings
    fixed = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', fixed, flags=re.MULTILINE)
    fixed = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', fixed, flags=re.MULTILINE)
    fixed = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', fixed, flags=re.MULTILINE)
    # Fix markdown lists
    fixed = re.sub(r'^-\s+(.+)$', r'<li>\1</li>', fixed, flags=re.MULTILINE)
    # Fix code blocks
    fixed = re.sub(r'```(\w+)?\n(.*?)```',
                   r'<pre><code>\2</code></pre>', fixed, flags=re.DOTALL)
    return fixed


def main():
    """Main execution."""
    print("🔧 Starting FreeRideInvestor.com audit fixes...\n")

    # 1. Create missing pages
    print("📄 Step 1: Creating missing pages...")
    pages_to_create = [
        ("Blog", "blog", "<h1>Blog</h1><p>Welcome to the FreeRide Investor blog. Check back soon for trading insights and strategy analysis.</p>"),
        ("About", "about", "<h1>About FreeRide Investor</h1><p>FreeRide Investor is dedicated to providing trading education and strategy analysis.</p>"),
        ("Contact", "contact",
         "<h1>Contact Us</h1><p>Get in touch with us through the contact form below.</p>")
    ]

    for title, slug, content in pages_to_create:
        existing = get_page_by_slug(slug)
        if existing:
            print(f"⏭️  Page '{title}' already exists (ID: {existing['id']})")
        else:
            create_page(title, slug, content)

    print()

    # 2. Find and deduplicate TSLA posts
    print("🔍 Step 2: Finding duplicate TSLA posts...")
    tsla_posts = get_posts_by_slug_pattern("tsla")
    duplicate_patterns = ["-4", "-3", "-2", "-base"]
    canonical_slug = None
    duplicates = []

    for post in tsla_posts:
        slug = post.get("slug", "")
        if any(pattern in slug for pattern in duplicate_patterns):
            duplicates.append(post)
        elif "tsla" in slug.lower() and not any(pattern in slug for pattern in duplicate_patterns):
            if not canonical_slug:
                canonical_slug = post.get("slug")
                print(
                    f"✅ Found canonical post: {post.get('title')} (slug: {canonical_slug})")

    print(f"📋 Found {len(duplicates)} duplicate posts to handle")
    for dup in duplicates:
        print(
            f"   - {dup.get('title')} (ID: {dup['id']}, slug: {dup.get('slug')})")

    # For now, mark duplicates as draft (redirects can be handled via .htaccess or redirect plugin)
    if duplicates:
        print("\n📝 Marking duplicates as draft...")
        for dup in duplicates:
            update_post(dup["id"], {"status": "draft"})
            print(f"   ✅ Drafted: {dup.get('title')}")

    print()

    # 3. Fix premium CTA links in posts
    print("🔗 Step 3: Fixing premium CTA links...")
    all_posts = requests.get(
        f"{API_BASE}/posts", params={"per_page": 100}, auth=AUTH, timeout=30).json()
    fixed_count = 0

    for post in all_posts:
        content = post.get("content", {}).get("rendered", "")
        if "/reports/" in content:
            fixed_content = fix_premium_cta_link(post["id"], content)
            if fixed_content != content:
                update_post(post["id"], {"content": fixed_content})
                fixed_count += 1
                print(f"   ✅ Fixed CTA in: {post.get('title')}")

    print(f"✅ Fixed {fixed_count} posts with broken premium links\n")

    # 4. Remove email from author bylines
    print("📧 Step 4: Removing email from author bylines...")
    email_fixed_count = 0

    for post in all_posts:
        content = post.get("content", {}).get("rendered", "")
        if "@" in content and ("author" in content.lower() or "by " in content.lower()):
            fixed_content = remove_email_from_byline(content)
            if fixed_content != content:
                update_post(post["id"], {"content": fixed_content})
                email_fixed_count += 1
                print(f"   ✅ Removed email from: {post.get('title')}")

    print(f"✅ Fixed {email_fixed_count} posts with email in byline\n")

    # 5. Clean markdown artifacts
    print("🧹 Step 5: Cleaning markdown artifacts...")
    cleaned_count = 0

    for post in all_posts:
        content = post.get("content", {}).get("rendered", "")
        # Check for markdown artifacts
        if "[" in content and "]" in content and "(" in content and ")" in content:
            # Likely has markdown links
            fixed_content = clean_markdown_artifacts(content)
            if fixed_content != content:
                update_post(post["id"], {"content": fixed_content})
                cleaned_count += 1
                print(f"   ✅ Cleaned formatting in: {post.get('title')}")

    print(f"✅ Cleaned {cleaned_count} posts with markdown artifacts\n")

    print("✅ All fixes complete!")
    print("\n📋 Next steps:")
    print("   1. Verify pages are accessible: /blog, /about, /contact")
    print("   2. Set up 301 redirects for duplicate TSLA post slugs (via .htaccess or redirect plugin)")
    print("   3. Update navigation menus to point to correct page URLs")
    print("   4. Review premium report content and replace placeholder metrics")


if __name__ == "__main__":
    main()
