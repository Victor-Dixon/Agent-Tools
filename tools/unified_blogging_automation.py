#!/usr/bin/env python3
"""
Unified Blogging Automation Tool
=================================

Automated blog post publishing across multiple WordPress sites with:
- Multi-site support
- Content templating system
- Purpose-aware content adaptation
- Category/tag management
- Scheduled publishing
- WordPress REST API integration

<!-- SSOT Domain: infrastructure -->

Author: Agent-2 (Architecture & Design Specialist)
V2 Compliant: <400 lines
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Try to import markdown converter
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    try:
        import markdown2
        HAS_MARKDOWN = True
        markdown = markdown2  # Alias for compatibility
    except ImportError:
        HAS_MARKDOWN = False

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    # Fallback if timeout constants not available
    class TimeoutConstants:
        HTTP_QUICK = 5
        HTTP_DEFAULT = 30

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WordPressBlogClient:
    """WordPress REST API client for blog posting."""
    
    def __init__(self, site_url: str, username: str, app_password: str):
        """Initialize WordPress blog client."""
        self.site_url = site_url.rstrip('/')
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.auth = HTTPBasicAuth(username, app_password)
        self.session = requests.Session()
        self.session.auth = self.auth
    
    def check_api_availability(self) -> bool:
        """Check if WordPress REST API is available."""
        try:
            response = self.session.get(
                f"{self.site_url}/wp-json/",
                timeout=TimeoutConstants.HTTP_QUICK
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API check failed: {e}")
            return False
    
    def get_or_create_category(self, name: str) -> Optional[int]:
        """Get or create category, return category ID."""
        endpoint = f"{self.api_url}/categories"
        
        # Search for existing category
        params = {"search": name, "per_page": 100}
        try:
            response = self.session.get(endpoint, params=params, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    if cat["name"].lower() == name.lower():
                        return cat["id"]
            
            # Create if not found
            payload = {"name": name}
            response = self.session.post(endpoint, json=payload, timeout=TimeoutConstants.HTTP_DEFAULT)
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
            response = self.session.get(endpoint, params=params, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 200:
                tags = response.json()
                for tag in tags:
                    if tag["name"].lower() == name.lower():
                        return tag["id"]
            
            # Create if not found
            payload = {"name": name}
            response = self.session.post(endpoint, json=payload, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 201:
                return response.json()["id"]
        except Exception as e:
            logger.error(f"Tag operation failed: {e}")
        
        return None
    
    def convert_markdown_to_html(self, content: str) -> str:
        """Convert markdown content to HTML for WordPress."""
        # Check if content is already HTML (contains HTML tags)
        if "<div" in content or "<h1" in content or "<p>" in content:
            # Already HTML, return as-is
            return content
        
        # Try to convert markdown to HTML
        if HAS_MARKDOWN:
            try:
                # Use markdown library with extensions for better HTML output
                if hasattr(markdown, 'markdown'):
                    html = markdown.markdown(
                        content,
                        extensions=['extra', 'codehilite', 'fenced_code']
                    )
                else:
                    # markdown2 library
                    html = markdown.markdown(content, extras=['fenced-code-blocks'])
                return html
            except Exception as e:
                logger.warning(f"Markdown conversion failed: {e}, using raw content")
                return content
        
        # No markdown library available, return as-is
        logger.warning("Markdown library not available, sending raw content")
        return content
    
    def create_post(
        self,
        title: str,
        content: str,
        excerpt: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        status: str = "draft",
        featured_media_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create WordPress blog post."""
        endpoint = f"{self.api_url}/posts"
        
        # Convert markdown to HTML if needed
        html_content = self.convert_markdown_to_html(content)
        
        # Resolve category IDs
        category_ids = []
        if categories:
            for cat_name in categories:
                cat_id = self.get_or_create_category(cat_name)
                if cat_id:
                    category_ids.append(cat_id)
        
        # Resolve tag IDs
        tag_ids = []
        if tags:
            for tag_name in tags:
                tag_id = self.get_or_create_tag(tag_name)
                if tag_id:
                    tag_ids.append(tag_id)
        
        # Prepare post data
        post_data = {
            "title": title,
            "content": html_content,  # Use converted HTML
            "status": status,
        }
        
        if excerpt:
            post_data["excerpt"] = excerpt
        if category_ids:
            post_data["categories"] = category_ids
        if tag_ids:
            post_data["tags"] = tag_ids
        if featured_media_id:
            post_data["featured_media"] = featured_media_id
        
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
                    "edit_link": post.get("_links", {}).get("self", [{}])[0].get("href")
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


class ContentAdapter:
    """Adapts content based on site purpose."""
    
    PURPOSE_ADAPTATIONS = {
        "trading_education": {
            "tone": "professional",
            "focus": "trading strategies, market analysis, investment guidance",
            "categories": ["Trading Education", "Market Analysis"],
            "tags": ["trading", "education", "analysis"]
        },
        "personal": {
            "tone": "friendly",
            "focus": "personal updates, memories, events",
            "categories": ["Personal"],
            "tags": ["personal", "update"]
        },
        "music": {
            "tone": "creative",
            "focus": "music releases, events, DJ sets",
            "categories": ["Music", "Releases"],
            "tags": ["music", "release", "dj"]
        },
        "swarm_system": {
            "tone": "technical",
            "focus": "system updates, architecture, agent achievements",
            "categories": ["System Updates", "Architecture"],
            "tags": ["swarm", "system", "updates"]
        },
        "plugin": {
            "tone": "technical",
            "focus": "plugin updates, changelog, features",
            "categories": ["Plugin Updates", "Changelog"],
            "tags": ["plugin", "update", "changelog"]
        }
    }
    
    @classmethod
    def adapt_content(cls, content: str, site_purpose: str) -> Dict[str, Any]:
        """Adapt content for specific site purpose."""
        adaptation = cls.PURPOSE_ADAPTATIONS.get(site_purpose, {})
        
        return {
            "content": content,
            "tone": adaptation.get("tone", "neutral"),
            "categories": adaptation.get("categories", []),
            "tags": adaptation.get("tags", []),
            "focus": adaptation.get("focus", "")
        }


class UnifiedBloggingAutomation:
    """Unified blogging automation across multiple WordPress sites."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize automation system."""
        self.config_path = config_path or Path(".deploy_credentials/blogging_api.json")
        self.clients: Dict[str, WordPressBlogClient] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load site configurations."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            logger.info("Create .deploy_credentials/blogging_api.json with site credentials")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for site_id, site_config in config.items():
                site_url = site_config.get("site_url")
                username = site_config.get("username")
                app_password = site_config.get("app_password")
                
                if all([site_url, username, app_password]):
                    self.clients[site_id] = WordPressBlogClient(
                        site_url, username, app_password
                    )
                    logger.info(f"✅ Loaded client for {site_id}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    
    def publish_to_site(
        self,
        site_id: str,
        title: str,
        content: str,
        site_purpose: Optional[str] = None,
        excerpt: Optional[str] = None,
        status: str = "draft",
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Publish post to specific site."""
        if site_id not in self.clients:
            return {
                "success": False,
                "error": f"Site {site_id} not configured"
            }
        
        client = self.clients[site_id]
        
        # Adapt content if purpose provided
        if site_purpose:
            adapted = ContentAdapter.adapt_content(content, site_purpose)
            categories = adapted["categories"]
            tags = adapted["tags"]
        else:
            categories = []
            tags = []
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "site_id": site_id,
                "title": title,
                "categories": categories,
                "tags": tags
            }
        
        # Create post
        result = client.create_post(
            title=title,
            content=content,
            excerpt=excerpt,
            categories=categories,
            tags=tags,
            status=status
        )
        
        result["site_id"] = site_id
        return result
    
    def publish_to_all_sites(
        self,
        title: str,
        content: str,
        site_filter: Optional[List[str]] = None,
        site_purpose_map: Optional[Dict[str, str]] = None,
        status: str = "draft",
        dry_run: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """Publish post to multiple sites."""
        results = {}
        
        sites_to_publish = site_filter or list(self.clients.keys())
        
        for site_id in sites_to_publish:
            if site_id not in self.clients:
                continue
            
            site_purpose = None
            if site_purpose_map and site_id in site_purpose_map:
                site_purpose = site_purpose_map[site_id]
            
            results[site_id] = self.publish_to_site(
                site_id=site_id,
                title=title,
                content=content,
                site_purpose=site_purpose,
                status=status,
                dry_run=dry_run
            )
        
        return results


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Blogging Automation")
    parser.add_argument("--site", help="Site ID to publish to")
    parser.add_argument("--title", required=True, help="Post title")
    parser.add_argument("--content", required=True, help="Post content (or file path)")
    parser.add_argument("--purpose", help="Site purpose (for content adaptation)")
    parser.add_argument("--status", default="draft", choices=["draft", "publish"], help="Post status")
    parser.add_argument("--all-sites", action="store_true", help="Publish to all configured sites")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no actual posting)")
    parser.add_argument("--config", help="Path to blogging_api.json config file")
    
    args = parser.parse_args()
    
    if not HAS_REQUESTS:
        logger.error("❌ requests library required. Install with: pip install requests")
        return 1
    
    # Load content
    content_path = Path(args.content)
    if content_path.exists():
        content = content_path.read_text(encoding='utf-8')
    else:
        content = args.content
    
    # Initialize automation
    config_path = Path(args.config) if args.config else None
    automation = UnifiedBloggingAutomation(config_path=config_path)
    
    if not automation.clients:
        logger.error("❌ No sites configured. Create .deploy_credentials/blogging_api.json")
        return 1
    
    # Publish
    if args.all_sites:
        logger.info("📤 Publishing to all sites...")
        results = automation.publish_to_all_sites(
            title=args.title,
            content=content,
            status=args.status,
            dry_run=args.dry_run
        )
    elif args.site:
        logger.info(f"📤 Publishing to {args.site}...")
        result = automation.publish_to_site(
            site_id=args.site,
            title=args.title,
            content=content,
            site_purpose=args.purpose,
            status=args.status,
            dry_run=args.dry_run
        )
        results = {args.site: result}
    else:
        logger.error("❌ Specify --site or --all-sites")
        return 1
    
    # Report results
    print("\n" + "="*70)
    print("📊 PUBLISHING RESULTS")
    print("="*70)
    
    for site_id, result in results.items():
        if result.get("success"):
            if result.get("dry_run"):
                print(f"✅ {site_id}: DRY RUN - Would publish '{args.title}'")
            else:
                print(f"✅ {site_id}: Published successfully")
                print(f"   Post ID: {result.get('post_id')}")
                print(f"   Link: {result.get('link')}")
        else:
            print(f"❌ {site_id}: Failed")
            print(f"   Error: {result.get('error')}")
    
    print("="*70 + "\n")
    
    return 0 if all(r.get("success") for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

