#!/usr/bin/env python3
"""
Houston Sip Queen Auto_Blogger Setup
====================================

1. Deletes "Hello world!" post
2. Creates Auto_Blogger template with mock YAML
3. Creates company introduction post

Author: Agent-7
V2 Compliant: Yes
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

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


def load_wp_credentials(site: str = "houstonsipqueen.com") -> Dict[str, Any]:
    """Load WordPress REST API credentials."""
    creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
    if creds_file.exists():
        try:
            with open(creds_file, 'r', encoding='utf-8') as f:
                all_creds = json.load(f)
            site_creds = all_creds.get(site) or all_creds.get("houstonsipqueen")
            if site_creds:
                # Map to expected field names
                return {
                    "site_url": site_creds.get("site_url"),
                    "wp_user": site_creds.get("username"),
                    "wp_app_password": site_creds.get("app_password")
                }
        except Exception as e:
            print(f"⚠️  Could not load from blogging_api.json: {e}")

    import os
    wp_user = os.getenv("WP_ADMIN_USERNAME") or os.getenv("WORDPRESS_USER")
    wp_pass = os.getenv("WP_ADMIN_PASSWORD") or os.getenv("WORDPRESS_PASS") or os.getenv("WP_APP_PASSWORD")
    site_url = os.getenv("WP_SITE_URL") or f"https://{site}"

    if wp_user and wp_pass:
        return {
            "site_url": site_url,
            "wp_user": wp_user,
            "wp_app_password": wp_pass
        }

    return {}


def delete_hello_world_post(site: str = "houstonsipqueen.com") -> bool:
    """Delete the 'Hello world!' post from WordPress."""
    creds = load_wp_credentials(site)
    
    if not creds.get("wp_user") or not creds.get("wp_app_password"):
        print("⚠️  WordPress credentials not found")
        return False

    site_url = creds.get("site_url", f"https://{site}")
    wp_user = creds.get("wp_user")
    wp_pass = creds.get("wp_app_password")
    
    endpoint = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
    auth = HTTPBasicAuth(wp_user, wp_pass)

    try:
        print("🔍 Searching for 'Hello world!' post...")
        resp = requests.get(
            endpoint,
            auth=auth,
            params={"search": "Hello world!", "per_page": 10},
            timeout=TimeoutConstants.HTTP_DEFAULT
        )

        if resp.status_code != 200:
            print(f"❌ Failed to search posts: {resp.status_code}")
            return False

        posts = resp.json()
        hello_world_post = None
        
        for post in posts:
            title = post.get("title", {}).get("rendered", "")
            if "Hello world" in title or "hello world" in title.lower():
                hello_world_post = post
                break

        if not hello_world_post:
            print("ℹ️  'Hello world!' post not found (may already be deleted)")
            return True

        post_id = hello_world_post.get("id")
        delete_endpoint = f"{endpoint}/{post_id}"
        
        print(f"🗑️  Deleting post ID {post_id}...")
        delete_resp = requests.delete(
            delete_endpoint,
            auth=auth,
            params={"force": True},
            timeout=TimeoutConstants.HTTP_DEFAULT
        )

        if delete_resp.status_code == 200:
            print(f"✅ Successfully deleted 'Hello world!' post (ID: {post_id})")
            return True
        else:
            print(f"❌ Failed to delete post: {delete_resp.status_code}")
            print(f"   Response: {delete_resp.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error deleting post: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_autoblogger_template() -> bool:
    """Create Auto_Blogger template for Houston Sip Queen with mock YAML."""
    autoblogger_dir = project_root / "temp_repos" / "Auto_Blogger"
    templates_dir = autoblogger_dir / "autoblogger" / "templates"
    resources_dir = autoblogger_dir / "autoblogger" / "resources"
    
    # Create directories if they don't exist
    templates_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)
    
    # Create voice template directory
    voice_dir = resources_dir / "voice_templates"
    voice_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock YAML template for Quiana's voice (to be replaced with actual voice structure)
    mock_voice_yaml = {
        "author": {
            "name": "Quiana",
            "business": "Houston Sip Queen",
            "role": "Owner & Lead Bartender",
            "location": "Houston, TX"
        },
        "voice": {
            "tone": "luxury, warm, professional, approachable",
            "style": "conversational, elegant, Southern hospitality",
            "personality": [
                "Passionate about craft cocktails",
                "Detail-oriented service provider",
                "Luxury experience focused",
                "Warm and welcoming",
                "Professional yet personable"
            ],
            "writing_style": {
                "sentence_length": "varied (short punchy statements + longer descriptive)",
                "vocabulary": "sophisticated but accessible",
                "use_contractions": True,
                "use_exclamation": "moderate (for excitement)",
                "formality": "professional but friendly"
            }
        },
        "content_themes": [
            "Luxury mobile bartending",
            "Craft cocktails",
            "Event planning tips",
            "Houston event scene",
            "Southern hospitality",
            "Wedding bartending",
            "Corporate events",
            "Private parties"
        ],
        "content_guidelines": {
            "topics": [
                "Event planning advice",
                "Cocktail recipes",
                "Event trends",
                "Client testimonials",
                "Behind-the-scenes",
                "Seasonal drink ideas"
            ],
            "avoid": [
                "Overly technical jargon",
                "Negative reviews",
                "Competitor comparisons",
                "Pricing specifics (use 'request a quote' instead)"
            ],
            "cta": "Request a quote for your event",
            "branding": {
                "company_name": "Houston Sip Queen",
                "tagline": "Bringing the bar to you",
                "values": [
                    "Luxury service",
                    "Attention to detail",
                    "Southern hospitality",
                    "Professional excellence"
                ]
            }
        },
        "seo": {
            "target_keywords": [
                "luxury mobile bartending Houston",
                "wedding bartender Houston",
                "corporate event bartending",
                "mobile bar service Houston",
                "craft cocktails Houston"
            ],
            "local_focus": "Houston, Texas area events"
        }
    }
    
    # Write YAML file
    yaml_path = voice_dir / "houstonsipqueen_voice_template.yaml"
    try:
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(mock_voice_yaml, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"✅ Created Auto_Blogger voice template: {yaml_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating YAML template: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_company_intro_post(site: str = "houstonsipqueen.com") -> Optional[Dict[str, Any]]:
    """Create company introduction post for Houston Sip Queen."""
    creds = load_wp_credentials(site)

    if not creds.get("wp_user") or not creds.get("wp_app_password"):
        print("⚠️  WordPress credentials not found")
        return None

    site_url = creds.get("site_url", f"https://{site}")
    wp_user = creds.get("wp_user")
    wp_pass = creds.get("wp_app_password")

    post_title = "Welcome to Houston Sip Queen — Luxury Mobile Bartending for Your Event"
    post_content = """<!-- wp:paragraph -->
<p>Welcome to Houston Sip Queen, where we bring the bar to you. Whether you're planning a wedding, birthday celebration, corporate event, girls' night, or private dinner, we're here to elevate your gathering with luxury mobile bartending services.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>What We Do</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Houston Sip Queen specializes in bringing professional, elegant bartending services directly to your event location. We handle everything from setup to service, ensuring your guests enjoy expertly crafted cocktails in a sophisticated atmosphere.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Our Services</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul><!-- wp:list-item -->
<li><strong>Weddings:</strong> Make your special day unforgettable with our luxury bar service</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><strong>Corporate Events:</strong> Professional bartending for your business gatherings</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><strong>Private Parties:</strong> Birthdays, anniversaries, and special celebrations</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><strong>Girls' Night:</strong> Elevate your gathering with craft cocktails</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><strong>Private Dinners:</strong> Intimate events with personalized service</li>
<!-- /wp:list-item --></ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Why Choose Houston Sip Queen?</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>We combine Southern hospitality with professional excellence, bringing you a luxury experience that's both elegant and approachable. Our attention to detail and commitment to quality ensures your event is nothing short of exceptional.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Ready to bring the bar to your event? Request a quote today and let's make your gathering unforgettable.</strong></p>
<!-- /wp:paragraph -->

<!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/request-a-quote">Request a Quote</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons -->"""

    endpoint = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
    auth = HTTPBasicAuth(wp_user, wp_pass)

    body = {
        "title": post_title,
        "content": post_content,
        "status": "publish",
        "format": "standard"
    }

    try:
        print(f"📝 Creating company introduction post...")
        resp = requests.post(
            endpoint,
            auth=auth,
            json=body,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )

        if resp.status_code == 201:
            data = resp.json()
            post_id = data.get("id")
            post_link = data.get("link")
            print(f"✅ Company introduction post published!")
            print(f"   Post ID: {post_id}")
            print(f"   Link: {post_link}")
            return {"ok": True, "id": post_id, "link": post_link}
        else:
            print(f"❌ Failed to publish post: {resp.status_code}")
            print(f"   Response: {resp.text[:200]}")
            return {"ok": False, "status_code": resp.status_code, "error": resp.text}

    except Exception as e:
        print(f"❌ Error publishing post: {e}")
        import traceback
        traceback.print_exc()
        return {"ok": False, "error": str(e)}


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup Houston Sip Queen Auto_Blogger template and content"
    )
    parser.add_argument(
        '--site',
        default='houstonsipqueen.com',
        help='Site key for WordPress'
    )
    parser.add_argument(
        '--skip-delete',
        action='store_true',
        help='Skip deleting Hello World post'
    )
    parser.add_argument(
        '--skip-template',
        action='store_true',
        help='Skip creating Auto_Blogger template'
    )
    parser.add_argument(
        '--skip-intro',
        action='store_true',
        help='Skip creating introduction post'
    )

    args = parser.parse_args()

    print("🍸 Houston Sip Queen Auto_Blogger Setup")
    print("=" * 60)

    results = {
        "delete_post": False,
        "create_template": False,
        "create_intro": False
    }

    # Delete Hello World post
    if not args.skip_delete:
        results["delete_post"] = delete_hello_world_post(args.site)
    else:
        print("⏭️  Skipping Hello World post deletion")

    # Create Auto_Blogger template
    if not args.skip_template:
        results["create_template"] = create_autoblogger_template()
    else:
        print("⏭️  Skipping Auto_Blogger template creation")

    # Create introduction post
    if not args.skip_intro:
        result = create_company_intro_post(args.site)
        results["create_intro"] = result and result.get("ok", False)
    else:
        print("⏭️  Skipping introduction post creation")

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Delete Hello World Post: {'✅ Success' if results['delete_post'] else '❌ Failed'}")
    print(f"  Create Auto_Blogger Template: {'✅ Success' if results['create_template'] else '❌ Failed'}")
    print(f"  Create Introduction Post: {'✅ Success' if results['create_intro'] else '❌ Failed'}")

    if all(results.values()):
        print("\n✅ All tasks complete!")
        return 0
    elif any(results.values()):
        print("\n🟡 Partial completion - check errors above")
        return 1
    else:
        print("\n❌ All tasks failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())

