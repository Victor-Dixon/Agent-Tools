#!/usr/bin/env python3
"""
Audit dadudekc.com Blog Content
==============================

Lists all blog posts on dadudekc.com to identify which content should be
featured vs archived for ad-readiness.

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


def get_all_posts():
    """Get all blog posts."""
    url = f"{API_BASE}/posts"
    params = {"per_page": 100, "status": "any"}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        return response.json()
    return []


def analyze_blog_content():
    """Analyze blog posts for feature/archive recommendations."""
    print("📝 Auditing dadudekc.com blog content...\n")

    posts = get_all_posts()

    if not posts:
        print("  ℹ️  No blog posts found")
        return []

    print(f"  Found {len(posts)} blog post(s)\n")

    recommendations = []

    for post in posts:
        post_id = post.get("id")
        title = post.get("title", {}).get("rendered", "N/A")
        slug = post.get("slug", "N/A")
        status = post.get("status", "N/A")
        date = post.get("date", "N/A")
        excerpt = post.get("excerpt", {}).get("rendered", "")[:100]
        content_length = len(post.get("content", {}).get("raw", ""))

        # Analyze for ad-readiness
        title_lower = title.lower()
        content_raw = post.get("content", {}).get("raw", "").lower()

        # Keywords for featuring
        consulting_keywords = [
            "automation", "workflow", "consulting", "save time", "efficiency",
            "process", "streamline", "automate"
        ]
        keyword_matches = sum(
            1 for kw in consulting_keywords if kw in (title_lower + content_raw))

        # Recommendation logic
        if status == "publish" and keyword_matches > 0:
            recommendation = "FEATURE"
        elif status == "publish":
            recommendation = "REVIEW"
        else:
            recommendation = "ARCHIVE"

        recommendations.append({
            "id": post_id,
            "title": title,
            "slug": slug,
            "status": status,
            "date": date,
            "content_length": content_length,
            "keyword_matches": keyword_matches,
            "recommendation": recommendation
        })

        print(f"  Post ID {post_id}: {title[:60]}")
        print(f"    Slug: {slug}")
        print(f"    Status: {status}")
        print(f"    Date: {date}")
        print(f"    Content: {content_length} chars")
        print(f"    Consulting keywords: {keyword_matches}")
        print(f"    Recommendation: {recommendation}")
        print()

    # Summary
    featured = [r for r in recommendations if r["recommendation"] == "FEATURE"]
    review = [r for r in recommendations if r["recommendation"] == "REVIEW"]
    archive = [r for r in recommendations if r["recommendation"] == "ARCHIVE"]

    print("📊 Summary:")
    print("=" * 60)
    print(f"  Total posts: {len(posts)}")
    print(f"  FEATURE: {len(featured)} posts")
    print(f"  REVIEW: {len(review)} posts")
    print(f"  ARCHIVE: {len(archive)} posts")

    if featured:
        print("\n✅ Posts to FEATURE (consulting-focused):")
        for r in featured:
            print(
                f"  - {r['title'][:60]} (ID: {r['id']}, {r['keyword_matches']} keywords)")

    if review:
        print("\n⚠️  Posts to REVIEW (may need updates):")
        for r in review:
            print(f"  - {r['title'][:60]} (ID: {r['id']})")

    if archive:
        print("\n📦 Posts to ARCHIVE (draft/private/off-topic):")
        for r in archive:
            print(
                f"  - {r['title'][:60]} (ID: {r['id']}, status: {r['status']})")

    return recommendations


def main():
    """Main execution."""
    print("🔍 Auditing dadudekc.com blog content for feature/archive recommendations...\n")

    recommendations = analyze_blog_content()

    if recommendations:
        print("\n✅ Blog content audit complete!")
        print("\n💡 Next steps:")
        print("  1. Review FEATURE recommendations")
        print("  2. Update REVIEW posts to align with consulting positioning")
        print("  3. Archive or update ARCHIVE posts as needed")
    else:
        print("\nℹ️  No blog posts found to audit")


if __name__ == "__main__":
    main()




