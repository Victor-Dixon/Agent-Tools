#!/usr/bin/env python3
"""
Update Blog Posts with Fixed Links
===================================

Updates existing WordPress blog posts with fixed links using WordPress REST API.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-12-14
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.unified_blogging_automation import UnifiedBloggingAutomation
except ImportError:
    print("❌ Could not import UnifiedBloggingAutomation")
    sys.exit(1)


def get_post_by_slug(automation: UnifiedBloggingAutomation, site_id: str, slug: str) -> Optional[Dict[str, Any]]:
    """Get WordPress post by slug."""
    if site_id not in automation.clients:
        return None

    client = automation.clients[site_id]
    endpoint = f"{client.api_url}/posts"

    try:
        params = {"slug": slug}
        response = client.session.get(endpoint, params=params)
        if response.status_code == 200:
            posts = response.json()
            if posts:
                return posts[0]
    except Exception as e:
        print(f"❌ Error getting post: {e}")

    return None


def update_post(automation: UnifiedBloggingAutomation, site_id: str, post_id: int, content: str, title: str) -> bool:
    """Update WordPress post."""
    if site_id not in automation.clients:
        return False

    client = automation.clients[site_id]
    endpoint = f"{client.api_url}/posts/{post_id}"

    try:
        # Convert markdown to HTML if needed
        html_content = client.convert_markdown_to_html(content)

        data = {
            "content": html_content,
            "title": title,
        }

        response = client.session.post(endpoint, json=data)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error updating post: {e}")
        return False


def main():
    """Update blog posts with fixed links."""
    print("🔍 Updating blog posts with fixed links...\n")

    # Initialize automation
    automation = UnifiedBloggingAutomation()

    if not automation.clients:
        print("❌ No WordPress sites configured")
        print("   Configure .deploy_credentials/blogging_api.json")
        return 1

    if "dadudekc.com" not in automation.clients:
        print("❌ dadudekc.com not configured")
        return 1

    site_id = "dadudekc.com"

    # Posts to update
    posts_to_update = [
        {
            "file": "docs/blog/the_swarm_core_philosophy_2025-12-13.md",
            "slug": "%f0%9f%8e%af-the-core-philosophy-building-software-through-collaborative-agent-teams-2",
        },
        {
            "file": "docs/blog/4_agent_mode_optimization_2025-12-13.md",
            "slug": "%f0%9f%9a%80-optimizing-multi-agent-systems-introducing-4-agent-mode-2",
        },
        {
            "file": "docs/blog/dream_os_operating_cycle_interview_2025-12-14.md",
            "slug": "%f0%9f%9a%80-dream-os-operating-cycle-an-inside-look-at-weareswarm-ai",
        },
        {
            "file": "docs/blog/what_comes_next_2025-12-14.md",
            "slug": "%f0%9f%94%ae-what-comes-next-the-roadmap-for-weareswarm-ai",
        },
        {
            "file": "docs/blog/dream_os_review_styled.md",
            "slug": "%f0%9f%9a%80-a-professional-review-of-my-vibe-coded-project-dream-os",
        }
    ]

    updated_count = 0

    for post_info in posts_to_update:
        file_path = project_root / post_info["file"]

        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        print(f"📝 Processing: {file_path.name}")

        # Get existing post
        post = get_post_by_slug(automation, site_id, post_info["slug"])
        if not post:
            print(f"   ⚠️  Post not found with slug: {post_info['slug']}")
            continue

        post_id = post["id"]
        print(f"   Found post ID: {post_id}")

        # Read updated content
        content = file_path.read_text(encoding="utf-8")

        # Extract title from first h1
        first_line = content.split('\n')[0]
        if first_line.startswith('# '):
            title = first_line[2:].strip()
        else:
            title = post.get("title", {}).get("rendered", file_path.stem)

        # Update post
        if update_post(automation, site_id, post_id, content, title):
            print(f"   ✅ Updated successfully")
            print(f"   Link: {post.get('link', 'N/A')}")
            updated_count += 1
        else:
            print(f"   ❌ Failed to update")

    print(f"\n✅ Updated {updated_count}/{len(posts_to_update)} posts")
    return 0 if updated_count == len(posts_to_update) else 1


if __name__ == "__main__":
    sys.exit(main())
