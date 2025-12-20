#!/usr/bin/env python3
"""
Post Dream.os Review Blog
==========================

Posts the "A Professional Review of My Vibe-Coded Project: Dream.os" blog to dadudekc.com.

Author: Agent-4 (Captain)
Date: 2025-12-14
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import requests
from requests.auth import HTTPBasicAuth


def load_config() -> Dict[str, Any]:
    """Load WordPress configuration."""
    config_path = project_root / ".deploy_credentials" / "blogging_api.json"
    
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    sites = config.get("sites", {})
    if not sites:
        site_config = config.get("dadudekc.com", {})
    else:
        site_config = sites.get("dadudekc.com", {})
    
    return {
        "url": site_config.get("url") or site_config.get("site_url") or "https://dadudekc.com",
        "username": site_config.get("username") or site_config.get("wp_user"),
        "app_password": site_config.get("app_password") or site_config.get("wp_app_password")
    }


def main() -> int:
    """Post the Dream.os review blog to dadudekc.com."""

    # Read the blog post content
    blog_content_path = project_root / "docs" / "blog" / "dream_os_review_styled.md"

    if not blog_content_path.exists():
        print(f"❌ Blog content file not found: {blog_content_path}")
        return 1

    with open(blog_content_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Load config
    config = load_config()
    if not config.get("username") or not config.get("app_password"):
        print("❌ Missing WordPress credentials")
        return 1

    # Blog post metadata
    title = "🚀 A Professional Review of My Vibe-Coded Project: Dream.os"
    excerpt = "Building Dreams with Code - A multi-agent system that balances intuitive problem-solving with professional structure"

    site_url = config["url"]
    auth = HTTPBasicAuth(config["username"], config["app_password"])
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"

    print("=" * 60)
    print("POSTING DREAM.OS REVIEW BLOG")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"Site: dadudekc.com")
    print(f"Content length: {len(content)} characters")
    print()

    try:
        # Publish
        print(f"🚀 Publishing to dadudekc.com...")
        print()

        payload = {
            "title": title,
            "content": content,
            "status": "publish",
            "excerpt": excerpt
        }

        response = requests.post(
            api_url,
            auth=auth,
            json=payload,
            timeout=30
        )

        if response.status_code == 201:
            result = response.json()
            post_id = result.get("id")
            post_url = result.get("link", "N/A")
            print(f"✅ Published successfully!")
            print(f"   Post ID: {post_id}")
            print(f"   URL: {post_url}")
            return 0
        else:
            error_msg = response.text
            print(f"❌ Failed: HTTP {response.status_code}")
            print(f"   Error: {error_msg[:500]}")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


