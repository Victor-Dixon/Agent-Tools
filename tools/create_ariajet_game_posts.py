#!/usr/bin/env python3
"""
Create AriaJet Game Posts
=========================

Creates WordPress game posts for Aria's games using WordPress REST API.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-02
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("❌ requests library not installed. Install with: pip install requests")

try:
    from dotenv import load_dotenv
from src.core.config.timeout_constants import TimeoutConstants
    load_dotenv()
except ImportError:
    pass


def get_wordpress_credentials() -> Dict[str, str]:
    """Get WordPress REST API credentials from environment."""
    site_url = os.getenv("ARIAJET_SITE_URL", "https://ariajet.site")
    username = os.getenv("ARIAJET_WP_USERNAME")
    app_password = os.getenv("ARIAJET_WP_APP_PASSWORD")
    
    if not username or not app_password:
        print("⚠️  WordPress credentials not found in .env")
        print("   Add these to .env file:")
        print("   ARIAJET_SITE_URL=https://ariajet.site")
        print("   ARIAJET_WP_USERNAME=your_username")
        print("   ARIAJET_WP_APP_PASSWORD=your_app_password")
        print("\n   To create app password:")
        print("   1. Go to WordPress admin → Users → Your Profile")
        print("   2. Scroll to 'Application Passwords'")
        print("   3. Create new app password")
        return {}
    
    return {
        "site_url": site_url,
        "username": username,
        "password": app_password
    }


def create_game_post(creds: Dict, game_data: Dict) -> bool:
    """Create a WordPress game post."""
    if not REQUESTS_AVAILABLE:
        print("❌ requests library not available")
        return False
    
    url = f"{creds['site_url']}/wp-json/wp/v2/game"
    
    # Basic auth for WordPress REST API
    auth = (creds['username'], creds['password'])
    
    # Prepare post data
    post_data = {
        "title": game_data["title"],
        "content": game_data["content"],
        "status": "publish",
        "game_url": game_data["game_url"],
        "game_type": game_data.get("game_type", "2d"),
        "featured_media": game_data.get("featured_image_id", 0),
    }
    
    try:
        response = requests.post(url, json=post_data, auth=auth, timeout=TimeoutConstants.HTTP_DEFAULT)
        
        if response.status_code == 201:
            post = response.json()
            print(f"✅ Created game post: {game_data['title']}")
            print(f"   URL: {post.get('link', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to create post: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating post: {e}")
        return False


def main():
    """Main execution."""
    print("🎮 AriaJet Game Posts Creator")
    print("=" * 60)
    
    # Get credentials
    creds = get_wordpress_credentials()
    if not creds:
        return 1
    
    # Game data
    games = [
        {
            "title": "Aria's Wild World",
            "game_url": "https://ariajet.site/games/arias-wild-world.html",
            "game_type": "2d",
            "content": """<h2>Wildlife Survival Game</h2>
<p>Experience the wild in this exciting survival game. Navigate through diverse ecosystems, encounter wildlife, and survive the challenges of nature.</p>
<p><a href="https://ariajet.site/games/arias-wild-world.html" class="button">Play Game</a></p>""",
        },
        {
            "title": "Wildlife Adventure",
            "game_url": "https://ariajet.site/games/wildlife-adventure.html",
            "game_type": "2d",
            "content": """<h2>Adventure Game</h2>
<p>Embark on an epic adventure through the wilderness. Explore, discover, and survive in this immersive 2D adventure game.</p>
<p><a href="https://ariajet.site/games/wildlife-adventure.html" class="button">Play Game</a></p>""",
        }
    ]
    
    print(f"\n📋 Found {len(games)} games to create\n")
    
    # Create posts
    success_count = 0
    for game in games:
        print(f"📝 Creating: {game['title']}...")
        if create_game_post(creds, game):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"✅ Created {success_count}/{len(games)} game posts")
    
    if success_count < len(games):
        print("\n💡 Note: Make sure:")
        print("   1. WordPress REST API is enabled")
        print("   2. 'game' custom post type is registered")
        print("   3. Application password is correct")
        print("   4. User has permission to create posts")
    
    return 0 if success_count == len(games) else 1


if __name__ == "__main__":
    sys.exit(main())


