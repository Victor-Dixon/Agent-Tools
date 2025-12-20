#!/usr/bin/env python3
"""
Audit DadudeKC.com WordPress Site
===================================

Lists all posts and pages to identify what should stay vs what should be removed.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

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


def get_all_posts(site_url: str, username: str, app_password: str) -> List[Dict]:
    """Get all posts from WordPress site."""
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
                params={"per_page": per_page, "page": page, "status": "any"},
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if response.status_code != 200:
                print(f"❌ Error fetching posts: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                break
            
            posts = response.json()
            if not posts:
                break
            
            all_posts.extend(posts)
            
            # Check if there are more pages
            if len(posts) < per_page:
                break
            
            page += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    return all_posts


def get_all_pages(site_url: str, username: str, app_password: str) -> List[Dict]:
    """Get all pages from WordPress site."""
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    auth = HTTPBasicAuth(username, app_password)
    
    all_pages = []
    page = 1
    per_page = 100
    
    while True:
        try:
            response = requests.get(
                api_url,
                auth=auth,
                params={"per_page": per_page, "page": page, "status": "any"},
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if response.status_code != 200:
                print(f"❌ Error fetching pages: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                break
            
            pages = response.json()
            if not pages:
                break
            
            all_pages.extend(pages)
            
            # Check if there are more pages
            if len(pages) < per_page:
                break
            
            page += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    return all_pages


def categorize_content(items: List[Dict], item_type: str) -> Dict[str, List[Dict]]:
    """Categorize content by keywords."""
    categories = {
        "developer_tools": [],
        "interactive_games": [],
        "code_reviews": [],
        "projects": [],
        "other": []
    }
    
    keywords = {
        "developer_tools": ["tool", "developer", "dev", "utility", "helper", "generator"],
        "interactive_games": ["game", "interactive", "play", "gaming", "playable"],
        "code_reviews": ["review", "code review", "vibe coded", "dream.os"],
        "projects": ["project", "portfolio", "showcase"]
    }
    
    for item in items:
        title = item.get("title", {}).get("rendered", "").lower()
        content = item.get("content", {}).get("rendered", "").lower()
        excerpt = item.get("excerpt", {}).get("rendered", "").lower()
        
        text = f"{title} {content} {excerpt}"
        
        categorized = False
        for cat, keywords_list in keywords.items():
            if any(keyword in text for keyword in keywords_list):
                categories[cat].append(item)
                categorized = True
                break
        
        if not categorized:
            categories["other"].append(item)
    
    return categories


def main():
    """Main audit function."""
    print("=" * 60)
    print("DADUDEKC.COM SITE AUDIT")
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
    
    print(f"🔍 Auditing: {site_url}")
    print(f"   Username: {username}")
    print()
    
    # Get all posts and pages
    print("📥 Fetching posts and pages...")
    posts = get_all_posts(site_url, username, app_password)
    pages = get_all_pages(site_url, username, app_password)
    
    print(f"   Found {len(posts)} posts")
    print(f"   Found {len(pages)} pages")
    print()
    
    # Categorize content
    print("📊 Categorizing content...")
    post_categories = categorize_content(posts, "posts")
    page_categories = categorize_content(pages, "pages")
    
    # Print summary
    print()
    print("=" * 60)
    print("AUDIT RESULTS")
    print("=" * 60)
    print()
    
    print("📝 POSTS:")
    print(f"   Developer Tools: {len(post_categories['developer_tools'])}")
    print(f"   Interactive Games: {len(post_categories['interactive_games'])}")
    print(f"   Code Reviews: {len(post_categories['code_reviews'])}")
    print(f"   Projects: {len(post_categories['projects'])}")
    print(f"   Other: {len(post_categories['other'])}")
    print()
    
    print("📄 PAGES:")
    print(f"   Developer Tools: {len(page_categories['developer_tools'])}")
    print(f"   Interactive Games: {len(page_categories['interactive_games'])}")
    print(f"   Code Reviews: {len(page_categories['code_reviews'])}")
    print(f"   Projects: {len(page_categories['projects'])}")
    print(f"   Other: {len(page_categories['other'])}")
    print()
    
    # Detailed listings
    print("=" * 60)
    print("DETAILED LISTINGS")
    print("=" * 60)
    print()
    
    # Developer Tools
    all_dev_tools = post_categories['developer_tools'] + page_categories['developer_tools']
    if all_dev_tools:
        print("🔧 DEVELOPER TOOLS:")
        for item in all_dev_tools:
            title = item.get("title", {}).get("rendered", "No title")
            item_type = "POST" if item in posts else "PAGE"
            item_id = item.get("id")
            status = item.get("status", "unknown")
            link = item.get("link", "N/A")
            print(f"   [{item_type}] ID: {item_id} | Status: {status}")
            print(f"      Title: {title}")
            print(f"      URL: {link}")
            print()
    
    # Interactive Games
    all_games = post_categories['interactive_games'] + page_categories['interactive_games']
    if all_games:
        print("🎮 INTERACTIVE GAMES:")
        for item in all_games:
            title = item.get("title", {}).get("rendered", "No title")
            item_type = "POST" if item in posts else "PAGE"
            item_id = item.get("id")
            status = item.get("status", "unknown")
            link = item.get("link", "N/A")
            print(f"   [{item_type}] ID: {item_id} | Status: {status}")
            print(f"      Title: {title}")
            print(f"      URL: {link}")
            print()
    
    # Code Reviews
    all_reviews = post_categories['code_reviews'] + page_categories['code_reviews']
    if all_reviews:
        print("📝 CODE REVIEWS:")
        for item in all_reviews:
            title = item.get("title", {}).get("rendered", "No title")
            item_type = "POST" if item in posts else "PAGE"
            item_id = item.get("id")
            status = item.get("status", "unknown")
            link = item.get("link", "N/A")
            print(f"   [{item_type}] ID: {item_id} | Status: {status}")
            print(f"      Title: {title}")
            print(f"      URL: {link}")
            print()
    
    # Summary recommendations
    print("=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    print()
    
    total_dev_tools = len(all_dev_tools)
    total_games = len(all_games)
    
    if total_dev_tools > 0:
        print(f"⚠️  Found {total_dev_tools} developer tool(s)")
        print("   Consider: Moving to a dedicated developer tools site or portfolio")
        print()
    
    if total_games > 0:
        print(f"⚠️  Found {total_games} interactive game(s)")
        print("   Consider: Moving to a gaming/entertainment site or portfolio")
        print()
    
    if total_dev_tools == 0 and total_games == 0:
        print("✅ No developer tools or games found - site content looks appropriate")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





