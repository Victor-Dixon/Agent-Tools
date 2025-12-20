#!/usr/bin/env python3
"""
Direct Fix for The Swarm Post - Force Update All Sections
==========================================================

Directly updates the specific sections that need color fixes, regardless of current state.

Author: Agent-4 (Captain)
Date: 2025-12-14
"""

import sys
import json
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import requests
from requests.auth import HTTPBasicAuth


def load_config():
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


def force_fix_content(content: str) -> str:
    """Force fix all sections - replace with corrected versions."""
    
    # Fix 1: The Core Philosophy section - ensure paragraph has color
    # Replace the paragraph regardless of current state
    philosophy_pattern = r'(<h2[^>]*Core Philosophy[^>]*>.*?</h2>\s*<p style=")([^"]*?)(">)'
    def fix_philosophy(match):
        tag_start = match.group(1)
        styles = match.group(2)
        tag_end = match.group(3)
        
        # Remove any existing color first
        styles = re.sub(r'color:\s*[^;]+;?\s*', '', styles)
        
        # Add color
        if not styles.rstrip().endswith(';'):
            styles = styles.rstrip() + '; '
        styles += 'color: #2d3748'
        
        return f'{tag_start}{styles}{tag_end}'
    
    content = re.sub(philosophy_pattern, fix_philosophy, content, flags=re.DOTALL | re.IGNORECASE)
    
    # Fix 2: Activity Detection, Unified Messaging, TDD cards
    # Find each card and fix its <p> tag
    card_fixes = [
        "Activity Detection",
        "Unified Messaging", 
        "Test-Driven Development"
    ]
    
    for heading_text in card_fixes:
        # Pattern: <h3>heading</h3> ... <p> or <p style="...">
        pattern = f'(<h3[^>]*{re.escape(heading_text)}[^>]*>.*?</h3>.*?)(<p)([^>]*?>)'
        
        def fix_card_p(match):
            before = match.group(1)
            p_tag = match.group(2)
            p_attrs = match.group(3)
            
            # If p_attrs has style, add color to it
            if 'style=' in p_attrs:
                # Extract style attribute
                style_match = re.search(r'style="([^"]*)"', p_attrs)
                if style_match:
                    styles = style_match.group(1)
                    # Remove existing color
                    styles = re.sub(r'color:\s*[^;]+;?\s*', '', styles)
                    # Add color
                    if not styles.rstrip().endswith(';'):
                        styles = styles.rstrip() + '; '
                    styles += 'color: #2d3748'
                    # Replace style in attributes
                    p_attrs = re.sub(r'style="[^"]*"', f'style="{styles}"', p_attrs)
                else:
                    p_attrs = p_attrs.replace('>', ' style="color: #2d3748">')
            else:
                # No style attribute, add one
                p_attrs = p_attrs.replace('>', ' style="color: #2d3748">')
            
            return f'{before}{p_tag}{p_attrs}'
        
        content = re.sub(pattern, fix_card_p, content, flags=re.DOTALL | re.IGNORECASE)
    
    # Fix 3: Why The Swarm Matters conclusion section
    conclusion_pattern = r'(<p style=")([^"]*font-size:\s*1\.15em[^"]*?)(">)'
    def fix_conclusion(match):
        tag_start = match.group(1)
        styles = match.group(2)
        tag_end = match.group(3)
        
        # Remove existing color
        styles = re.sub(r'color:\s*[^;]+;?\s*', '', styles)
        
        # Add color
        if not styles.rstrip().endswith(';'):
            styles = styles.rstrip() + '; '
        styles += 'color: #2d3748'
        
        return f'{tag_start}{styles}{tag_end}'
    
    content = re.sub(conclusion_pattern, fix_conclusion, content, flags=re.DOTALL | re.IGNORECASE)
    
    return content


def main():
    """Force fix The Swarm post."""
    print("=" * 60)
    print("FORCE FIXING THE SWARM POST - WHITE ON WHITE SECTIONS")
    print("=" * 60)
    print()
    
    config = load_config()
    if not config.get("username") or not config.get("app_password"):
        print("❌ Missing WordPress credentials")
        return 1
    
    site_url = config["url"]
    auth = HTTPBasicAuth(config["username"], config["app_password"])
    
    try:
        # Get the post
        response = requests.get(
            f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/46",
            auth=auth,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch post: {response.status_code}")
            return 1
        
        post = response.json()
        post_id = post["id"]
        title = post.get("title", {}).get("rendered", "")
        content = post.get("content", {}).get("rendered", "")
        
        print(f"📋 Found post #{post_id}: {title[:60]}...")
        print()
        
        # Force fix the content
        print("🔧 Force applying color fixes...")
        fixed_content = force_fix_content(content)
        
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
            print()
            print("💡 Please refresh the page to see the changes")
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


