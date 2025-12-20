#!/usr/bin/env python3
"""
WordPress Blog Audit Tool
=========================

Audits WordPress blogs to:
1. Check for duplicate posts on dadudekc.com
2. Verify each website has an initial "About This Site" blog post
3. Create missing initial blog posts explaining site purpose

Author: Agent-2 (Architecture & Design Specialist)
"""

import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_QUICK = 5
        HTTP_DEFAULT = 30

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Site purposes from website audit
SITE_PURPOSES = {
    "dadudekc.com": {
        "purpose": "Personal/Blog",
        "description": "Personal blog and portfolio site for DaDudeKC",
        "initial_post_title": "About This Site - Welcome to DaDudeKC",
        "initial_post_content": """
# About This Site

Welcome to DaDudeKC.com! This is my personal blog and portfolio site where I share:
- Personal updates and thoughts
- Projects and experiments
- Technical insights and learnings
- Creative work and hobbies

I'm constantly building, learning, and exploring new technologies. This site serves as a record of that journey.

Feel free to explore and reach out if you'd like to connect!

-- DaDudeKC
        """.strip()
    },
    "freerideinvestor.com": {
        "purpose": "Trading Education Platform",
        "description": "Educational content about trading strategies, investment guidance, and market analysis",
        "initial_post_title": "About FreeRide Investor - Your Trading Education Hub",
        "initial_post_content": """
# About FreeRide Investor

Welcome to FreeRide Investor, your comprehensive trading education platform!

## Our Mission

FreeRide Investor is dedicated to providing high-quality educational content about trading strategies, investment guidance, and market analysis. Whether you're a beginner just starting your trading journey or an experienced trader looking to refine your skills, this platform offers valuable resources to help you succeed.

## What You'll Find Here

- **Trading Education**: In-depth guides on trading strategies and market analysis
- **Investment Guidance**: Insights and best practices for making informed investment decisions
- **Trading Robot Plugin Documentation**: Comprehensive documentation for our trading robot plugin
- **Community Resources**: Tools and resources to support traders at all levels

## Our Approach

We believe in practical, actionable education. Our content focuses on real-world applications and strategies that you can implement in your own trading journey.

Thank you for visiting, and we look forward to supporting your trading success!

-- The FreeRide Investor Team
        """.strip()
    },
    "prismblossom.online": {
        "purpose": "Personal/Birthday Celebration Site",
        "description": "Personal milestone celebration, guestbook, photo galleries, and event coordination",
        "initial_post_title": "About PrismBlossom - A Celebration of Life",
        "initial_post_content": """
# About PrismBlossom

Welcome to PrismBlossom, a space for celebrating life's special moments and milestones!

## Our Purpose

PrismBlossom is a personal site dedicated to celebrating important moments, sharing memories, and bringing people together. This space serves as:
- A digital guestbook for special occasions
- A photo gallery of cherished memories
- A platform for event coordination and updates
- A place to mark and celebrate personal milestones

## What Makes This Special

Life is full of beautiful moments worth celebrating. PrismBlossom captures those moments and provides a space where friends and family can come together to share in the joy and create lasting memories.

Thank you for being part of this journey!

-- The PrismBlossom Team
        """.strip()
    },
    "southwestsecret.com": {
        "purpose": "Music/DJ Site",
        "description": "Music portfolio, discography, DJ booking, event information, and music releases",
        "initial_post_title": "About Southwest Secret - Music & DJ Services",
        "initial_post_content": """
# About Southwest Secret

Welcome to Southwest Secret, your gateway to cutting-edge music and professional DJ services!

## Our Mission

Southwest Secret is a music platform and DJ service dedicated to delivering exceptional musical experiences. We specialize in:
- **Music Portfolio**: Explore our discography and musical projects
- **DJ Services**: Professional DJ booking for events and venues
- **Music Releases**: Stay updated on our latest tracks, mixes, and releases
- **Event Information**: Find out where we'll be performing next

## What We Offer

Whether you're looking for a DJ for your event, exploring new music, or following our latest releases, Southwest Secret provides a unique blend of talent and professionalism.

## Our Sound

We bring a distinctive style to every set and release, combining technical skill with creative expression to create memorable musical experiences.

Follow us for updates on new releases, upcoming shows, and more!

-- Southwest Secret
        """.strip()
    },
    "weareswarm.online": {
        "purpose": "Official Swarm System Website",
        "description": "Multi-agent system documentation, real-time agent status dashboard, mission activity feed, agent profiles, and system architecture documentation",
        "initial_post_title": "About We Are Swarm - Multi-Agent Intelligence System",
        "initial_post_content": """
# About We Are Swarm

Welcome to We Are Swarm, the official website for our multi-agent intelligence system!

## What Is Swarm?

Swarm is a sophisticated multi-agent system that leverages the power of collaborative artificial intelligence. Our platform consists of specialized agents, each with unique capabilities, working together to accomplish complex tasks and solve challenging problems.

## What You'll Find Here

- **Real-Time Agent Status**: Live dashboard showing the current status of all agents
- **Mission Activity Feed**: Track ongoing missions and agent activities in real-time
- **Agent Profiles**: Learn about each agent's capabilities, specialties, and achievements
- **System Architecture Documentation**: Deep dives into how the Swarm system works
- **Technical Updates**: Latest developments, improvements, and system enhancements

## Our Vision

We believe that collaboration and specialization are the keys to building truly intelligent systems. By combining the strengths of multiple specialized agents, we create something greater than the sum of its parts.

## Stay Connected

Follow our updates to stay informed about new features, agent achievements, and system improvements. We're constantly evolving and improving!

-- The Swarm Team
        """.strip()
    },
    "weareswarm.site": {
        "purpose": "Swarm Website Alternate Domain",
        "description": "Backup/alternate domain for swarm website with same content as weareswarm.online",
        "initial_post_title": "About We Are Swarm - Multi-Agent Intelligence System",
        "initial_post_content": """
# About We Are Swarm

Welcome to We Are Swarm, the official website for our multi-agent intelligence system!

*(This is an alternate domain for weareswarm.online - same content, different domain for redundancy and SEO purposes)*

## What Is Swarm?

Swarm is a sophisticated multi-agent system that leverages the power of collaborative artificial intelligence. Our platform consists of specialized agents, each with unique capabilities, working together to accomplish complex tasks and solve challenging problems.

## What You'll Find Here

- **Real-Time Agent Status**: Live dashboard showing the current status of all agents
- **Mission Activity Feed**: Track ongoing missions and agent activities in real-time
- **Agent Profiles**: Learn about each agent's capabilities, specialties, and achievements
- **System Architecture Documentation**: Deep dives into how the Swarm system works
- **Technical Updates**: Latest developments, improvements, and system enhancements

## Our Vision

We believe that collaboration and specialization are the keys to building truly intelligent systems. By combining the strengths of multiple specialized agents, we create something greater than the sum of its parts.

## Stay Connected

Follow our updates to stay informed about new features, agent achievements, and system improvements. We're constantly evolving and improving!

-- The Swarm Team
        """.strip()
    },
    "tradingrobotplug.com": {
        "purpose": "Trading Robot Plugin Website",
        "description": "Plugin documentation, features, installation guides, tutorials, plugin updates, changelog, and support resources",
        "initial_post_title": "About Trading Robot Plug - WordPress Plugin for Traders",
        "initial_post_content": """
# About Trading Robot Plug

Welcome to Trading Robot Plug, your comprehensive resource for the Trading Robot WordPress plugin!

## What Is Trading Robot Plug?

Trading Robot Plug is a powerful WordPress plugin designed to help traders integrate trading functionality, market data, and trading tools directly into their WordPress websites.

## What You'll Find Here

- **Plugin Documentation**: Comprehensive guides covering all plugin features
- **Installation Guides**: Step-by-step tutorials to get you started
- **Feature Documentation**: Detailed explanations of all plugin capabilities
- **Plugin Updates & Changelog**: Stay informed about new features and improvements
- **Support Resources**: Get help when you need it

## Key Features

Our plugin provides traders with:
- Integration of trading functionality into WordPress sites
- Real-time market data display
- Trading strategy tools and calculators
- Portfolio tracking and analysis
- Educational content integration

## Our Commitment

We're committed to providing a robust, user-friendly plugin that makes it easy for traders to enhance their WordPress sites with powerful trading capabilities.

Stay tuned for updates, tutorials, and new features!

-- The Trading Robot Plug Team
        """.strip()
    }
}


class WordPressBlogAuditor:
    """Audit WordPress blogs for duplicates and missing initial posts."""

    def __init__(self, site_url: str, username: str = None, app_password: str = None):
        """Initialize WordPress blog auditor."""
        self.site_url = site_url.rstrip('/')
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.username = username
        self.app_password = app_password
        self.session = requests.Session()
        if username and app_password:
            self.session.auth = HTTPBasicAuth(username, app_password)

    def get_all_posts(self, per_page: int = 100) -> List[Dict[str, Any]]:
        """Fetch all blog posts from WordPress REST API."""
        all_posts = []
        page = 1

        try:
            while True:
                params = {"per_page": per_page, "page": page, "status": "any"}
                response = self.session.get(
                    f"{self.api_url}/posts",
                    params=params,
                    timeout=TimeoutConstants.HTTP_DEFAULT
                )

                if response.status_code != 200:
                    logger.warning(
                        f"Failed to fetch posts page {page}: {response.status_code}")
                    break

                posts = response.json()
                if not posts:
                    break

                all_posts.extend(posts)

                # Check if there are more pages
                total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                if page >= total_pages:
                    break

                page += 1

            logger.info(
                f"✅ Fetched {len(all_posts)} posts from {self.site_url}")
            return all_posts
        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            return []

    def find_duplicates(self, posts: List[Dict[str, Any]]) -> List[Tuple[Dict, Dict]]:
        """Find duplicate blog posts based on title similarity."""
        duplicates = []
        seen_titles = defaultdict(list)

        # Group posts by normalized title
        for post in posts:
            title = post.get('title', {}).get('rendered', '').strip().lower()
            # Remove extra whitespace and normalize
            normalized = ' '.join(title.split())
            seen_titles[normalized].append(post)

        # Find duplicates
        for normalized_title, post_list in seen_titles.items():
            if len(post_list) > 1:
                # Sort by date (newest first) - keep the newest, mark others as duplicates
                post_list.sort(key=lambda x: x.get('date', ''), reverse=True)
                for dup_post in post_list[1:]:  # Skip the first (newest)
                    duplicates.append((post_list[0], dup_post))

        return duplicates

    def find_initial_post(self, posts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check if site has an initial 'About This Site' post."""
        keywords = ['about this site', 'welcome', 'about us',
                    'site purpose', 'about', 'introduction']

        for post in posts:
            title = post.get('title', {}).get('rendered', '').strip().lower()
            content = post.get('content', {}).get(
                'rendered', '').strip().lower()

            # Check if title or content contains keywords
            for keyword in keywords:
                # Check first 500 chars
                if keyword in title or keyword in content[:500]:
                    # Check if it's an introductory/initial post
                    if any(word in title for word in ['about', 'welcome', 'introduction', 'site']):
                        return post

        return None

    def get_or_create_category(self, name: str) -> Optional[int]:
        """Get or create category, return category ID."""
        endpoint = f"{self.api_url}/categories"

        # Search for existing category
        params = {"search": name, "per_page": 100}
        try:
            response = self.session.get(
                endpoint, params=params, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    if cat["name"].lower() == name.lower():
                        return cat["id"]

            # Create if not found
            payload = {"name": name}
            response = self.session.post(
                endpoint, json=payload, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 201:
                return response.json()["id"]
        except Exception as e:
            logger.error(f"Category operation failed: {e}")

        return None

    def get_or_create_tag(self, name: str) -> Optional[int]:
        """Get or create tag, return tag ID."""
        endpoint = f"{self.api_url}/tags"

        # Search for existing tag
        params = {"search": name, "per_page": 100}
        try:
            response = self.session.get(
                endpoint, params=params, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 200:
                tags = response.json()
                for tag in tags:
                    if tag["name"].lower() == name.lower():
                        return tag["id"]

            # Create if not found
            payload = {"name": name}
            response = self.session.post(
                endpoint, json=payload, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 201:
                return response.json()["id"]
        except Exception as e:
            logger.error(f"Tag operation failed: {e}")

        return None

    def create_initial_post(
        self,
        title: str,
        content: str,
        status: str = "publish"
    ) -> Dict[str, Any]:
        """Create initial blog post explaining site purpose."""
        if not self.username or not self.app_password:
            return {
                "success": False,
                "error": "WordPress credentials not provided"
            }

        endpoint = f"{self.api_url}/posts"

        # Resolve category IDs
        category_ids = []
        cat_id = self.get_or_create_category("Site Information")
        if cat_id:
            category_ids.append(cat_id)

        # Resolve tag IDs
        tag_ids = []
        for tag_name in ["about", "welcome"]:
            tag_id = self.get_or_create_tag(tag_name)
            if tag_id:
                tag_ids.append(tag_id)

        post_data = {
            "title": title,
            "content": content,
            "status": status,
        }

        if category_ids:
            post_data["categories"] = category_ids
        if tag_ids:
            post_data["tags"] = tag_ids

        try:
            response = self.session.post(
                endpoint,
                json=post_data,
                timeout=TimeoutConstants.HTTP_DEFAULT
            )

            if response.status_code in (200, 201):
                post = response.json()
                return {
                    "success": True,
                    "post_id": post.get("id"),
                    "link": post.get("link"),
                    "title": post.get("title", {}).get("rendered")
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def delete_post(self, post_id: int) -> bool:
        """Delete a blog post."""
        if not self.username or not self.app_password:
            return False

        endpoint = f"{self.api_url}/posts/{post_id}"

        try:
            response = self.session.delete(
                endpoint,
                params={"force": True},  # Force delete (skip trash)
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error deleting post {post_id}: {e}")
            return False


def load_credentials(config_path: Path) -> Dict[str, Dict[str, str]]:
    """Load WordPress credentials from config file."""
    if not config_path.exists():
        return {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load credentials: {e}")
        return {}


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Audit WordPress blogs")
    parser.add_argument(
        "--site", help="Site URL to audit (e.g., dadudekc.com)")
    parser.add_argument("--all-sites", action="store_true",
                        help="Audit all configured sites")
    parser.add_argument("--check-duplicates",
                        action="store_true", help="Check for duplicate posts")
    parser.add_argument("--check-initial-posts", action="store_true",
                        help="Check for initial purpose posts")
    parser.add_argument("--create-initial-posts",
                        action="store_true", help="Create missing initial posts")
    parser.add_argument("--delete-duplicates", action="store_true",
                        help="Delete duplicate posts (use with caution!)")
    parser.add_argument("--config", help="Path to blogging_api.json config file",
                        default=".deploy_credentials/blogging_api.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="Dry run (don't make changes)")

    args = parser.parse_args()

    if not HAS_REQUESTS:
        print("❌ ERROR: requests library required. Install with: pip install requests")
        return 1

    config_path = Path(args.config)
    credentials = load_credentials(config_path)

    if not credentials:
        print(f"⚠️  No credentials found at {config_path}")
        print("   Create the file with WordPress credentials to enable full functionality")
        credentials = {}

    # Determine which sites to audit
    sites_to_audit = []
    if args.all_sites:
        sites_to_audit = list(SITE_PURPOSES.keys())
    elif args.site:
        sites_to_audit = [args.site]
    else:
        # Default: audit dadudekc.com
        sites_to_audit = ["dadudekc.com"]

    results = {}

    for site_url in sites_to_audit:
        if not site_url.startswith('http'):
            site_url = f"https://{site_url}"

        site_key = site_url.replace('https://', '').replace('http://', '')
        site_info = SITE_PURPOSES.get(site_key, {})

        print(f"\n{'='*70}")
        print(f"🔍 AUDITING: {site_url}")
        print(f"{'='*70}\n")

        # Get credentials for this site
        site_cred = credentials.get(site_key, {})
        username = site_cred.get("username")
        app_password = site_cred.get("app_password")

        auditor = WordPressBlogAuditor(site_url, username, app_password)

        # Fetch all posts
        posts = auditor.get_all_posts()
        if not posts:
            print(
                f"⚠️  Could not fetch posts from {site_url} (may need credentials)")
            results[site_key] = {"error": "Could not fetch posts"}
            continue

        site_results = {
            "total_posts": len(posts),
            "duplicates": [],
            "has_initial_post": False,
            "initial_post_created": False
        }

        # Check for duplicates
        if args.check_duplicates or not args.check_initial_posts:
            duplicates = auditor.find_duplicates(posts)
            site_results["duplicates"] = duplicates

            if duplicates:
                print(f"⚠️  Found {len(duplicates)} duplicate post(s):")
                for original, duplicate in duplicates:
                    print(
                        f"   • '{original.get('title', {}).get('rendered')}' (ID: {original.get('id')})")
                    print(
                        f"     Duplicate: ID {duplicate.get('id')} (date: {duplicate.get('date')})")

                    if args.delete_duplicates and not args.dry_run:
                        if auditor.delete_post(duplicate.get('id')):
                            print(
                                f"     ✅ Deleted duplicate post ID {duplicate.get('id')}")
                        else:
                            print(
                                f"     ❌ Failed to delete duplicate post ID {duplicate.get('id')}")
                    elif args.delete_duplicates and args.dry_run:
                        print(
                            f"     [DRY RUN] Would delete duplicate post ID {duplicate.get('id')}")
            else:
                print(f"✅ No duplicate posts found")

        # Check for initial post
        if args.check_initial_posts or not args.check_duplicates:
            initial_post = auditor.find_initial_post(posts)
            if initial_post:
                print(f"✅ Initial 'About This Site' post found:")
                print(
                    f"   • '{initial_post.get('title', {}).get('rendered')}' (ID: {initial_post.get('id')})")
                site_results["has_initial_post"] = True
            else:
                print(f"⚠️  No initial 'About This Site' post found")

                if args.create_initial_posts:
                    if site_info:
                        title = site_info.get(
                            "initial_post_title", "About This Site")
                        content = site_info.get(
                            "initial_post_content", "Welcome to this site!")

                        if args.dry_run:
                            print(
                                f"   [DRY RUN] Would create initial post: '{title}'")
                            site_results["initial_post_created"] = True
                        else:
                            if username and app_password:
                                result = auditor.create_initial_post(
                                    title, content)
                                if result.get("success"):
                                    print(
                                        f"   ✅ Created initial post: '{result.get('title')}'")
                                    print(f"      Link: {result.get('link')}")
                                    site_results["initial_post_created"] = True
                                else:
                                    print(
                                        f"   ❌ Failed to create initial post: {result.get('error')}")
                            else:
                                print(
                                    f"   ⚠️  Cannot create post: credentials not configured for {site_key}")
                    else:
                        print(
                            f"   ⚠️  No site purpose information available for {site_key}")

        results[site_key] = site_results

    # Summary
    print(f"\n{'='*70}")
    print("📊 AUDIT SUMMARY")
    print(f"{'='*70}\n")

    for site_key, site_results in results.items():
        if "error" in site_results:
            print(f"❌ {site_key}: {site_results['error']}")
        else:
            print(f"📝 {site_key}:")
            print(f"   Total posts: {site_results['total_posts']}")
            print(f"   Duplicates: {len(site_results['duplicates'])}")
            print(
                f"   Has initial post: {'✅' if site_results['has_initial_post'] else '❌'}")
            if site_results.get('initial_post_created'):
                print(f"   Initial post created: ✅")

    # Save results
    output_file = Path("docs/blog/wordpress_blog_audit_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "audit_date": datetime.now().isoformat(),
            "sites_audited": list(results.keys()),
            "results": results
        }, f, indent=2)

    print(f"\n✅ Audit results saved to: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
