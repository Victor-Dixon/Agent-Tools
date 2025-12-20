#!/usr/bin/env python3
"""
Fix DadudeKC Blog Post Readability
===================================

Updates blog posts on dadudekc.com with CSS fixes for readability.
Can update existing posts or delete and recreate them.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-13
V2 Compliant: Yes
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("❌ requests library not available")
    sys.exit(1)

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30


def load_blogging_config() -> Dict[str, Any]:
    """Load blogging API configuration."""
    config_path = project_root / ".deploy_credentials" / "blogging_api.json"
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_css_fix() -> str:
    """Load the CSS readability fix."""
    css_path = project_root / "docs" / "DADUDEKC_BLOG_READABILITY_FIX.css"
    
    if not css_path.exists():
        print(f"⚠️  CSS fix file not found: {css_path}")
        return ""
    
    return css_path.read_text(encoding='utf-8')


def get_post(site_url: str, username: str, app_password: str, post_id: int) -> Optional[Dict]:
    """Get a single post from WordPress."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
    auth = HTTPBasicAuth(username, app_password)
    
    try:
        response = requests.get(
            api_url,
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def get_all_posts(site_url: str, username: str, app_password: str) -> List[Dict]:
    """Get all published posts from WordPress."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
    auth = HTTPBasicAuth(username, app_password)
    
    all_posts = []
    page = 1
    per_page = 100
    
    while True:
        try:
            response = requests.get(
                api_url,
                auth=auth,
                params={"per_page": per_page, "page": page, "status": "publish"},
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if response.status_code != 200:
                break
            
            posts = response.json()
            if not posts:
                break
            
            all_posts.extend(posts)
            
            if len(posts) < per_page:
                break
            
            page += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    return all_posts


def update_post_with_css(
    site_url: str,
    username: str,
    app_password: str,
    post_id: int,
    css_fix: str
) -> bool:
    """Update a post with CSS fix embedded in the content."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
    auth = HTTPBasicAuth(username, app_password)
    
    # Get current post
    post = get_post(site_url, username, app_password, post_id)
    if not post:
        return False
    
    # Get current content
    current_content = post.get("content", {}).get("rendered", "")
    
    # Check if CSS is already embedded
    if "<style>" in current_content and "Blog Post Readability Fix" in current_content:
        print(f"   ℹ️  CSS fix already embedded in post {post_id}")
        return True
    
    # Create style tag with CSS
    style_tag = f"""<style>
/* DaDudeKC Blog Post Readability Fix - Embedded */
{css_fix}
</style>
"""
    
    # Get raw content (not rendered)
    raw_content = post.get("content", {}).get("raw", "")
    if not raw_content:
        # If no raw content, use rendered and strip HTML
        raw_content = current_content
    
    # Prepend CSS to content
    updated_content = style_tag + raw_content
    
    # Update post
    try:
        response = requests.post(
            api_url,
            auth=auth,
            json={"content": updated_content},
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def delete_post(site_url: str, username: str, app_password: str, post_id: int) -> bool:
    """Delete a post from WordPress."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
    auth = HTTPBasicAuth(username, app_password)
    
    try:
        response = requests.delete(
            api_url,
            auth=auth,
            params={"force": True},
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def create_post_with_css(
    site_url: str,
    username: str,
    app_password: str,
    title: str,
    content: str,
    css_fix: str,
    categories: Optional[List[int]] = None
) -> Optional[Dict]:
    """Create a new post with CSS fix embedded."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
    auth = HTTPBasicAuth(username, app_password)
    
    # Create style tag with CSS
    style_tag = f"""<style>
/* DaDudeKC Blog Post Readability Fix - Embedded */
{css_fix}
</style>
"""
    
    # Prepend CSS to content
    full_content = style_tag + content
    
    body = {
        "title": title,
        "content": full_content,
        "status": "publish"
    }
    
    if categories:
        body["categories"] = categories
    
    try:
        response = requests.post(
            api_url,
            auth=auth,
            json=body,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix dadudekc.com blog post readability"
    )
    parser.add_argument(
        "--post-id",
        type=int,
        help="Specific post ID to fix (if not provided, lists all posts)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Fix all blog posts"
    )
    parser.add_argument(
        "--delete-and-recreate",
        action="store_true",
        help="Delete post and recreate with CSS fix (use with --post-id)"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing post with CSS fix (default action)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("DADUDEKC BLOG POST READABILITY FIX")
    print("=" * 60)
    print()
    
    # Load config
    config = load_blogging_config()
    
    if "dadudekc.com" not in config:
        print("❌ dadudekc.com not found in blogging config")
        return 1
    
    site_config = config["dadudekc.com"]
    site_url = site_config["site_url"]
    username = site_config["username"]
    app_password = site_config["app_password"]
    
    # Load CSS fix
    css_fix = load_css_fix()
    if not css_fix:
        print("❌ Could not load CSS fix file")
        return 1
    
    print(f"🔍 Site: {site_url}")
    print(f"   Username: {username}")
    print()
    
    # If no post ID, list all posts
    if not args.post_id and not args.all:
        print("📝 Available blog posts:")
        print()
        posts = get_all_posts(site_url, username, app_password)
        
        if not posts:
            print("   No posts found")
            return 0
        
        for post in posts:
            post_id = post.get("id")
            title = post.get("title", {}).get("rendered", "No title")
            link = post.get("link", "N/A")
            print(f"   ID {post_id}: {title}")
            print(f"      URL: {link}")
            print()
        
        print("💡 Usage:")
        print("   python tools/fix_dadudekc_blog_post.py --post-id <ID> --update")
        print("   python tools/fix_dadudekc_blog_post.py --post-id <ID> --delete-and-recreate")
        print("   python tools/fix_dadudekc_blog_post.py --all")
        return 0
    
    # Fix specific post
    if args.post_id:
        post = get_post(site_url, username, app_password, args.post_id)
        if not post:
            print(f"❌ Post {args.post_id} not found")
            return 1
        
        title = post.get("title", {}).get("rendered", "No title")
        print(f"📄 Fixing post: {title} (ID: {args.post_id})")
        print()
        
        if args.delete_and_recreate:
            print("🗑️  Deleting post...")
            if delete_post(site_url, username, app_password, args.post_id):
                print("   ✅ Deleted")
                print()
                print("📝 Recreating with CSS fix...")
                content = post.get("content", {}).get("raw", post.get("content", {}).get("rendered", ""))
                categories = post.get("categories", [])
                new_post = create_post_with_css(
                    site_url, username, app_password, title, content, css_fix, categories
                )
                if new_post:
                    print(f"   ✅ Created new post ID: {new_post.get('id')}")
                    print(f"   🔗 URL: {new_post.get('link')}")
                    return 0
                else:
                    print("   ❌ Failed to create new post")
                    return 1
            else:
                print("   ❌ Failed to delete post")
                return 1
        else:
            # Default: update existing post
            print("🔄 Updating post with CSS fix...")
            if update_post_with_css(site_url, username, app_password, args.post_id, css_fix):
                print("   ✅ Updated successfully")
                print(f"   🔗 URL: {post.get('link')}")
                return 0
            else:
                print("   ❌ Failed to update post")
                return 1
    
    # Fix all posts
    if args.all:
        posts = get_all_posts(site_url, username, app_password)
        if not posts:
            print("❌ No posts found")
            return 1
        
        print(f"🔄 Updating {len(posts)} post(s) with CSS fix...")
        print()
        
        updated = 0
        for post in posts:
            post_id = post.get("id")
            title = post.get("title", {}).get("rendered", "No title")
            print(f"   Updating ID {post_id}: {title}...")
            
            if update_post_with_css(site_url, username, app_password, post_id, css_fix):
                print(f"      ✅ Updated")
                updated += 1
            else:
                print(f"      ❌ Failed")
            print()
        
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"✅ Updated {updated} of {len(posts)} post(s)")
        return 0 if updated == len(posts) else 1


if __name__ == "__main__":
    sys.exit(main())




