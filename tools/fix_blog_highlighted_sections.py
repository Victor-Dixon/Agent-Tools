#!/usr/bin/env python3
"""
Fix Blog Post Highlighted Sections - Text Color Issue
======================================================

Fixes white-on-white text issue in highlighted sections of blog posts.
Updates published posts on dadudekc.com to add proper text color.

Author: Agent-4 (Captain)
Date: 2025-12-14
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def fix_highlighted_section_html(html_content: str) -> str:
    """Fix highlighted sections by adding text color to paragraph elements."""
    
    def fix_paragraph(match):
        """Fix a paragraph style attribute."""
        full_tag = match.group(0)
        style_attr = match.group(1)
        
        # If color is already present, return as is
        if 'color:' in style_attr:
            return full_tag
        
        # Add color before closing quote
        # Handle both cases: with semicolon and without
        if style_attr.rstrip().endswith(';'):
            new_style = f'{style_attr.rstrip()} color: #2d3748"'
        else:
            new_style = f'{style_attr}; color: #2d3748"'
        
        return f'<p style="{new_style}>'
    
    def fix_plain_paragraph(match):
        """Fix a plain <p> tag (no style) by adding style with color."""
        # Check if this is inside a white background card or highlighted section
        # We'll add color to plain <p> tags in cards
        return '<p style="color: #2d3748;">'
    
    # Pattern 1: Fix paragraphs with style attributes that don't have color
    # Highlighted sections with font-size: 1.1em
    pattern = r'<p style="([^"]*font-size:\s*1\.1em[^"]*?)"'
    fixed = re.sub(pattern, fix_paragraph, html_content)
    
    # Pattern 2: Fix paragraphs with margin-bottom (highlighted sections)
    pattern2 = r'<p style="([^"]*margin-bottom[^"]*?)"'
    fixed = re.sub(pattern2, fix_paragraph, fixed)
    
    # Pattern 3: Fix plain <p> tags that are in white background cards
    # These are in divs with background: #fff or #ffffff
    # We need to be careful - only fix <p> tags that are inside specific card divs
    # Look for <p> tags after card div opening (background: #fff)
    def fix_card_paragraphs(content):
        """Fix plain <p> tags inside white background cards."""
        # Pattern: card div opening, then plain <p> (no style)
        # Match: <div ... background: #fff ...> ... <p> or <div ... background: #ffffff ...>
        card_pattern = r'(<div[^>]*background:\s*#fff[^>]*>.*?)(<p)(?!\s+style)'
        
        def replace_card_p(m):
            prefix = m.group(1)
            p_tag = m.group(2)
            # Find where this <p> ends (at the next >)
            # We need to insert style attribute
            return f'{prefix}{p_tag} style="color: #2d3748"'
        
        content = re.sub(card_pattern, replace_card_p, content, flags=re.DOTALL)
        return content
    
    # Fix plain <p> tags in cards
    fixed = fix_card_paragraphs(fixed)
    
    # Pattern 4: Also fix plain <p> tags that might be in highlighted sections
    # Look for <p> without style that comes after highlighted section div
    highlighted_pattern = r'(<div[^>]*background:\s*#f8f9fa[^>]*>.*?)(<p)(?!\s+style)'
    def replace_highlighted_p(m):
        prefix = m.group(1)
        p_tag = m.group(2)
        return f'{prefix}{p_tag} style="color: #2d3748"'
    
    fixed = re.sub(highlighted_pattern, replace_highlighted_p, fixed, flags=re.DOTALL)
    
    return fixed


def update_published_post(post_id: int, updated_content: str) -> Dict[str, Any]:
    """Update a published WordPress post."""
    automation = UnifiedBloggingAutomation()
    
    if not automation.clients:
        return {"success": False, "error": "No WordPress sites configured"}
    
    site_id = "dadudekc.com"
    if site_id not in automation.clients:
        return {"success": False, "error": f"Site '{site_id}' not found"}
    
    client = automation.clients[site_id]
    
    try:
        # Update the post
        result = client.posts().update(
            post_id=post_id,
            content=updated_content
        )
        
        return {
            "success": True,
            "post_id": post_id,
            "link": result.get("link"),
            "title": result.get("title", {}).get("rendered", "N/A")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Fix highlighted sections in published blog posts."""
    print("=" * 60)
    print("FIXING BLOG POST HIGHLIGHTED SECTIONS - TEXT COLOR")
    print("=" * 60)
    print()
    
    site_id = "dadudekc.com"
    
    # Get WordPress credentials from config
    config_path = project_root / ".deploy_credentials" / "blogging_api.json"
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        print(f"   Expected at: {config_path}")
        return 1
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Try different config structures
    sites = config.get("sites", {})
    if not sites:
        # Try direct site config
        site_config = config.get(site_id, {})
    else:
        site_config = sites.get(site_id, {})
    
    if not site_config:
        print(f"❌ Site '{site_id}' not found in config")
        print(f"   Available keys: {list(config.keys())[:5]}...")
        return 1
    
    import requests
    from requests.auth import HTTPBasicAuth
    
    site_url = site_config.get("url") or site_config.get("base_url") or f"https://{site_id}"
    username = site_config.get("username") or site_config.get("wp_user")
    app_password = site_config.get("app_password") or site_config.get("wp_app_password")
    
    if not username or not app_password:
        print(f"❌ Missing credentials for {site_id}")
        return 1
    
    auth = HTTPBasicAuth(username, app_password)
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
    
    try:
        # Get recent posts
        response = requests.get(
            api_url,
            auth=auth,
            params={"per_page": 10, "status": "publish"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch posts: {response.status_code}")
            return 1
        
        posts = response.json()
        print(f"📋 Found {len(posts)} recent posts")
        print()
        
        fixed_count = 0
        
        for post in posts:
            post_id = post["id"]
            title = post.get("title", {}).get("rendered", "Unknown")
            content = post.get("content", {}).get("rendered", "")
            
            # Check if content has highlighted sections that need fixing
            if 'background: #f8f9fa' in content and 'border-left: 5px solid #2a5298' in content:
                # Check if any paragraph in highlighted section lacks color
                needs_fix = False
                # Look for highlighted section paragraphs without color
                highlighted_pattern = r'<div[^>]*background:\s*#f8f9fa[^>]*>.*?<p style="([^"]*font-size:\s*1\.1em[^"]*?)"'
                matches = re.finditer(highlighted_pattern, content, re.DOTALL)
                for match in matches:
                    styles = match.group(1)
                    if 'color:' not in styles:
                        needs_fix = True
                        break
                
                if needs_fix:
                    print(f"🔧 Fixing post #{post_id}: {title[:60]}...")
                    fixed_content = fix_highlighted_section_html(content)
                    
                    # Get raw content or use rendered
                    raw_content = post.get("content", {}).get("raw", fixed_content)
                    
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
                        print(f"   ✅ Fixed: {result.get('link', 'N/A')}")
                        fixed_count += 1
                    else:
                        print(f"   ❌ Failed: {update_response.status_code} - {update_response.text[:200]}")
        
        print()
        print("=" * 60)
        print(f"✅ Fixed {fixed_count} post(s)")
        
        return 0 if fixed_count > 0 else 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

