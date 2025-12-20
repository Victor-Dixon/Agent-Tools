#!/usr/bin/env python3
"""
Fix The Swarm Post - White on White Text Sections
==================================================

Directly fixes the specific sections in "Introducing The Swarm" post that have white-on-white text.

Author: Agent-4 (Captain)
Date: 2025-12-14
"""

import sys
import json
import re
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
    
    # Try different config structures
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


def fix_swarm_post_content(content: str) -> str:
    """Fix specific white-on-white sections in The Swarm post."""
    
    original = content
    
    # Fix 1: The Core Philosophy paragraph - add color if missing
    # Pattern: <p style="...font-size: 1.1em...margin-bottom: 0..."> without color
    def add_color_to_philosophy(match):
        style = match.group(1)
        if 'color:' not in style:
            # Add color before closing quote
            if style.rstrip().endswith(';'):
                return f'<p style="{style.rstrip()} color: #2d3748">'
            else:
                return f'<p style="{style}; color: #2d3748">'
        return match.group(0)
    
    content = re.sub(
        r'<p style="([^"]*font-size:\s*1\.1em[^"]*?margin-bottom:\s*0[^"]*?)"',
        add_color_to_philosophy,
        content
    )
    
    # Fix 2: Plain <p> tags (no style) in white background cards
    # These are Activity Detection, Unified Messaging, Test-Driven Development
    # Match: <div...background: #fff...> ... <p> (with no style attribute)
    # Use a more targeted approach - find each card and fix its <p> tag
    def fix_plain_p_in_cards(html):
        # Split by card divs to process each card separately
        # Pattern to find: card div, h3, then plain <p>
        # More specific: look for the pattern where we have Activity Detection, etc.
        
        # Fix plain <p> tags that come after h3 in white cards
        # Pattern: <h3...Activity Detection...>...</h3> then plain <p>
        patterns_to_fix = [
            (r'(<h3[^>]*Activity Detection[^>]*>.*?</h3>\s*)(<p)(?!\s+style=)',
             r'\1\2 style="color: #2d3748"'),
            (r'(<h3[^>]*Unified Messaging[^>]*>.*?</h3>\s*)(<p)(?!\s+style=)',
             r'\1\2 style="color: #2d3748"'),
            (r'(<h3[^>]*Test-Driven Development[^>]*>.*?</h3>\s*)(<p)(?!\s+style=)',
             r'\1\2 style="color: #2d3748"'),
        ]
        
        for pattern, replacement in patterns_to_fix:
            html = re.sub(pattern, replacement, html, flags=re.DOTALL | re.IGNORECASE)
        
        # Also fix any plain <p> in white background divs more generally
        # Match div with background #fff, then find plain <p> tag
        def fix_p_in_white_div(match):
            div_start = match.start()
            div_end = match.end()
            div_content = match.group(0)
            
            # Find plain <p> tags within this div
            # Look for <p> that doesn't have style="...
            fixed = re.sub(r'(<p)(?!\s+style=")', r'\1 style="color: #2d3748"', div_content)
            return fixed
        
        # Match white background divs
        white_div_pattern = r'<div[^>]*background:\s*#fff[^>]*>.*?</div>'
        html = re.sub(white_div_pattern, fix_p_in_white_div, html, flags=re.DOTALL | re.IGNORECASE)
        
        return html
    
    content = fix_plain_p_in_cards(content)
    
    # Fix 3: Why The Swarm Matters section - paragraph with font-size but no color
    def add_color_to_conclusion(match):
        style = match.group(1)
        if 'color:' not in style:
            if style.rstrip().endswith(';'):
                return f'<p style="{style.rstrip()} color: #2d3748">'
            else:
                return f'<p style="{style}; color: #2d3748">'
        return match.group(0)
    
    content = re.sub(
        r'<p style="([^"]*font-size:\s*1\.15em[^"]*?)"',
        add_color_to_conclusion,
        content
    )
    
    # Fix 4: Any other plain <p> tags without style in highlighted sections
    # Fix all plain <p> tags that don't have style attribute
    # But only if they're likely in a styled section (after specific content)
    # Be careful not to break things - only fix if in context of our sections
    
    # More aggressive: fix all plain <p> tags that appear in cards/highlighted sections
    # Check if <p> is inside a div with background styling
    lines = content.split('\n')
    fixed_lines = []
    in_styled_section = False
    
    for i, line in enumerate(lines):
        # Check if we're entering a styled section
        if 'background:' in line and ('#fff' in line or '#f8f9fa' in line or '#f7fafc' in line):
            in_styled_section = True
        elif '</div>' in line and in_styled_section:
            in_styled_section = False
        
        # Fix plain <p> tags in styled sections
        if in_styled_section and re.search(r'<p(?!\s+style=)', line):
            line = re.sub(r'(<p)(?!\s+style=)', r'\1 style="color: #2d3748"', line)
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    return content


def main():
    """Fix The Swarm post white-on-white sections."""
    print("=" * 60)
    print("FIXING THE SWARM POST - WHITE ON WHITE SECTIONS")
    print("=" * 60)
    print()
    
    config = load_config()
    if not config.get("username") or not config.get("app_password"):
        print("❌ Missing WordPress credentials")
        return 1
    
    site_url = config["url"]
    auth = HTTPBasicAuth(config["username"], config["app_password"])
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
    
    try:
        # Get all posts to find "Introducing The Swarm"
        response = requests.get(
            api_url,
            auth=auth,
            params={"per_page": 10, "status": "publish", "search": "Introducing The Swarm"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch posts: {response.status_code}")
            return 1
        
        posts = response.json()
        swarm_post = None
        
        for post in posts:
            title = post.get("title", {}).get("rendered", "")
            if "Introducing The Swarm" in title:
                swarm_post = post
                break
        
        if not swarm_post:
            print("❌ Could not find 'Introducing The Swarm' post")
            return 1
        
        post_id = swarm_post["id"]
        title = swarm_post.get("title", {}).get("rendered", "")
        content = swarm_post.get("content", {}).get("rendered", "")
        
        print(f"📋 Found post #{post_id}: {title[:60]}...")
        print()
        
        # Fix the content
        fixed_content = fix_swarm_post_content(content)
        
        # Check if changes were made
        if fixed_content == content:
            print("ℹ️  No changes needed - content already has color fixes")
            return 0
        
        print("🔧 Applying fixes...")
        
        # Update the post
        update_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
        update_response = requests.post(
            update_url,
            auth=auth,
            json={"content": fixed_content},
            timeout=30
        )
        
        if update_response.status_code == 200:
            result = update_response.json()
            print(f"✅ Successfully updated!")
            print(f"   Post ID: {post_id}")
            print(f"   URL: {result.get('link', 'N/A')}")
            return 0
        else:
            print(f"❌ Failed to update: {update_response.status_code}")
            print(f"   Error: {update_response.text[:200]}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

