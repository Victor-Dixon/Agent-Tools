#!/usr/bin/env python3
"""
Create Initial Blog Post for DadudekC
=====================================

Creates the initial "About this site" post for dadudekc.com.

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-12-14
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import requests

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def create_initial_post(
    base_url: str = "https://dadudekc.com",
    wp_user: Optional[str] = None,
    wp_app_password: Optional[str] = None
) -> Dict[str, Any]:
    """Create initial 'About this site' post."""
    
    # Get credentials from environment or config
    if not wp_user:
        wp_user = os.getenv("WORDPRESS_USER")
    if not wp_app_password:
        wp_app_password = os.getenv("WORDPRESS_APP_PASSWORD")
    
    if not wp_user or not wp_app_password:
        config_path = project_root / "config" / "wordpress_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                wp_user = wp_user or config.get("wp_user")
                wp_app_password = wp_app_password or config.get("wp_app_password")
    
    if not wp_user or not wp_app_password:
        return {
            "ok": False,
            "error": "WordPress credentials not configured. Set WORDPRESS_USER and WORDPRESS_APP_PASSWORD environment variables or config/wordpress_config.json"
        }
    
    # Post content
    title = "About This Site - DaDudeKC"
    content = """<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 12px; color: white; margin: 2rem 0;">
<h2 style="color: white; margin-top: 0;">Welcome to DaDudeKC</h2>
</div>

<p>This site serves as a showcase and documentation hub for the V2_SWARM collaborative development system and related projects.</p>

<h3>Purpose</h3>
<p>DaDudeKC.com provides:</p>
<ul>
<li><strong>Project Documentation</strong> - Technical documentation and architecture guides</li>
<li><strong>Development Blog</strong> - Updates on the V2_SWARM system and agent coordination</li>
<li><strong>System Showcase</strong> - Demonstrations of collaborative AI agent systems</li>
<li><strong>Knowledge Base</strong> - Resources for understanding multi-agent coordination</li>
</ul>

<h3>About V2_SWARM</h3>
<p>V2_SWARM is a collaborative development system featuring specialized AI agents working together to build and maintain complex software systems. Each agent has specific expertise and responsibilities, coordinated through a unified messaging and task management system.</p>

<div style="background: #f5f5f5; padding: 1.5rem; border-radius: 8px; margin: 2rem 0;">
<h4>Key Features</h4>
<ul>
<li>Multi-agent coordination and communication</li>
<li>Task assignment and contract system</li>
<li>Automated development workflows</li>
<li>Quality assurance and validation processes</li>
</ul>
</div>

<p><strong>Stay tuned for updates and insights into collaborative AI development!</strong></p>
"""
    
    # Create post via WordPress REST API
    endpoint = f"{base_url}/wp-json/wp/v2/posts"
    body = {
        "title": title,
        "content": content,
        "status": "publish",
        "categories": ["About", "Site Information"]
    }
    
    try:
        resp = requests.post(
            endpoint,
            auth=(wp_user, wp_app_password),
            json=body,
            timeout=10
        )
        
        if resp.status_code == 201:
            data = resp.json()
            return {
                "ok": True,
                "id": data.get("id"),
                "link": data.get("link"),
                "title": title
            }
        else:
            return {
                "ok": False,
                "status_code": resp.status_code,
                "error": resp.text
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create initial blog post for dadudekc.com"
    )
    parser.add_argument(
        "--url",
        default="https://dadudekc.com",
        help="Base URL of WordPress site"
    )
    parser.add_argument(
        "--user",
        help="WordPress username"
    )
    parser.add_argument(
        "--password",
        help="WordPress app password"
    )
    
    args = parser.parse_args()
    
    print("📝 Creating initial 'About this site' post...")
    result = create_initial_post(
        base_url=args.url,
        wp_user=args.user,
        wp_app_password=args.password
    )
    
    if result.get("ok"):
        print(f"✅ Post created successfully!")
        print(f"   ID: {result.get('id')}")
        print(f"   Link: {result.get('link')}")
        print(f"   Title: {result.get('title')}")
    else:
        print(f"❌ Failed to create post: {result.get('error')}")
        if "credentials" in result.get('error', '').lower():
            print("\n💡 To configure credentials:")
            print("   1. Set environment variables: WORDPRESS_USER and WORDPRESS_APP_PASSWORD")
            print("   2. Or create config/wordpress_config.json with wp_user and wp_app_password")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


