#!/usr/bin/env python3
"""
Houston Sip Queen Theme & Announcement Post
===========================================

Creates luxury mobile bartender theme styling and publishes launch announcement post.

Author: Agent-5
Date: 2025-12-17
V2 Compliant: Yes
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

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


def get_hsq_theme_css() -> str:
    """Generate Houston Sip Queen luxury theme CSS."""
    return """
/* Houston Sip Queen - Luxury Mobile Bartender Theme */
/* Brand: Luxury Nightlife + Southern Glam */
/* Applied: 2025-12-17 */

/* Color Palette */
:root {
    --hsq-onyx: #0B0B0F;
    --hsq-champagne: #F5E6C8;
    --hsq-rosegold: #C9A26A;
    --hsq-berry: #7A1E3A;
    --hsq-white: #FFFFFF;
}

/* Typography */
body, 
body * {
    font-family: 'Inter', 'Montserrat', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

h1, h2, h3, h4, h5, h6,
.wp-block-heading,
h1.wp-block-heading,
h2.wp-block-heading,
h3.wp-block-heading,
h4.wp-block-heading,
h5.wp-block-heading,
h6.wp-block-heading {
    font-family: 'Playfair Display', 'Cinzel', Georgia, serif !important;
    font-weight: 700;
    color: var(--hsq-onyx);
}

/* Buttons - Pill radius, RoseGold fill, Onyx text */
.wp-block-button__link,
.wp-element-button,
button,
input[type="submit"],
a.button {
    border-radius: 50px !important;
    background-color: var(--hsq-rosegold) !important;
    color: var(--hsq-onyx) !important;
    padding: 12px 32px !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

.wp-block-button__link:hover,
.wp-element-button:hover,
button:hover,
input[type="submit"]:hover,
a.button:hover {
    background-color: var(--hsq-berry) !important;
    color: var(--hsq-white) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(122, 30, 58, 0.3);
}

/* Hero Section */
.wp-block-cover,
.hero-section {
    background: linear-gradient(135deg, var(--hsq-onyx) 0%, #1a1a24 100%) !important;
    color: var(--hsq-champagne) !important;
    min-height: 60vh !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Section Styling */
.wp-block-group,
section {
    padding: 60px 20px !important;
}

/* High Contrast for Readability */
body {
    background-color: var(--hsq-white) !important;
    color: var(--hsq-onyx) !important;
}

p, li, span {
    color: var(--hsq-onyx) !important;
    line-height: 1.7 !important;
}

/* Links */
a {
    color: var(--hsq-rosegold) !important;
    text-decoration: none !important;
    transition: color 0.3s ease !important;
}

a:hover {
    color: var(--hsq-berry) !important;
}

/* Mobile-First Responsive */
@media (max-width: 768px) {
    .wp-block-cover,
    .hero-section {
        min-height: 50vh !important;
        padding: 40px 20px !important;
    }
    
    h1 {
        font-size: 2rem !important;
    }
    
    h2 {
        font-size: 1.75rem !important;
    }
}

/* Navigation */
.wp-block-navigation,
nav {
    background-color: rgba(11, 11, 15, 0.95) !important;
    backdrop-filter: blur(10px);
}

.wp-block-navigation-item__content,
nav a {
    color: var(--hsq-champagne) !important;
}

.wp-block-navigation-item__content:hover,
nav a:hover {
    color: var(--hsq-rosegold) !important;
}

/* Footer */
footer,
.wp-block-template-part[data-area="footer"] {
    background-color: var(--hsq-onyx) !important;
    color: var(--hsq-champagne) !important;
    padding: 40px 20px !important;
}

footer a,
footer .wp-block-navigation-item__content {
    color: var(--hsq-rosegold) !important;
}

footer a:hover {
    color: var(--hsq-champagne) !important;
}
"""


def load_wp_credentials(site: str = "houstonsipqueen.com") -> Dict[str, Any]:
    """Load WordPress REST API credentials."""
    # Try .deploy_credentials/blogging_api.json first
    creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
    if creds_file.exists():
        try:
            with open(creds_file, 'r', encoding='utf-8') as f:
                all_creds = json.load(f)
            site_creds = all_creds.get(
                site) or all_creds.get("houstonsipqueen")
            if site_creds:
                return site_creds
        except Exception as e:
            print(f"⚠️  Could not load from blogging_api.json: {e}")

    # Fallback to environment variables
    import os
    wp_user = os.getenv("WP_ADMIN_USERNAME") or os.getenv("WORDPRESS_USER")
    wp_pass = os.getenv("WP_ADMIN_PASSWORD") or os.getenv(
        "WORDPRESS_PASS") or os.getenv("WP_APP_PASSWORD")
    site_url = os.getenv("WP_SITE_URL") or f"https://{site}"

    if wp_user and wp_pass:
        return {
            "site_url": site_url,
            "wp_user": wp_user,
            "wp_app_password": wp_pass
        }

    return {}


def deploy_css_via_functions_php(site_key: str = "houstonsipqueen.com") -> bool:
    """Deploy CSS theme as standalone PHP file using WordPress Manager."""
    try:
        from tools.wordpress_manager import WordPressManager

        print(f"🎨 Deploying Houston Sip Queen theme CSS...")
        manager = WordPressManager(site_key)

        if not manager.connect():
            print("❌ Failed to connect to WordPress server")
            return False

        # Create PHP file with CSS injection
        css_content = get_hsq_theme_css()
        php_code = f"""<?php
/**
 * Houston Sip Queen Luxury Theme CSS
 * Applied: 2025-12-17
 */

if (!defined('ABSPATH')) {{
    exit;
}}

function hsq_luxury_theme_css() {{
    ?>
    <style id="hsq-luxury-theme">
    {css_content}
    </style>
    <?php
}}
add_action('wp_head', 'hsq_luxury_theme_css', 999);
"""

        # Write temporary PHP file
        temp_php = project_root / "temp_hsq_theme.php"
        temp_php.write_text(php_code, encoding='utf-8')

        # Deploy to theme (WordPress Manager handles directory creation)
        success = manager.deploy_file(
            temp_php, remote_path="hsq_theme_css.php", auto_flush_cache=True)

        # Clean up
        if temp_php.exists():
            temp_php.unlink()

        if success:
            print("✅ Theme CSS file deployed successfully!")
            print("   File: hsq_theme_css.php")
            print("   Note: Add 'require_once get_template_directory() . \\'/hsq_theme_css.php\\';' to functions.php")
            print(
                "   Or use WordPress Admin → Appearance → Additional CSS to add the CSS directly")
            return True
        else:
            print("❌ Failed to deploy theme CSS")
            return False

    except Exception as e:
        print(f"❌ Error deploying CSS: {e}")
        import traceback
        traceback.print_exc()
        return False


def publish_announcement_post(site: str = "houstonsipqueen.com") -> Optional[Dict[str, Any]]:
    """Publish Houston Sip Queen launch announcement post."""
    creds = load_wp_credentials(site)

    if not creds.get("wp_user") or not creds.get("wp_app_password"):
        print("⚠️  WordPress credentials not found")
        print("   Please configure in .deploy_credentials/blogging_api.json or .env")
        return None

    site_url = creds.get("site_url", f"https://{site}")
    wp_user = creds.get("wp_user")
    wp_pass = creds.get("wp_app_password")

    # Post content
    post_title = "Houston Sip Queen is Live — Luxury Mobile Bartending for Your Event"
    post_content = """<!-- wp:paragraph -->
<p>Bringing the bar to you. Weddings, birthdays, corporate events, girls' night, and private dinners.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Choose a package, pick your vibe, and we'll handle the setup + service.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Now booking — request a quote today.</strong></p>
<!-- /wp:paragraph -->

<!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link">Request a Quote</a></div>
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
        print(f"📝 Publishing announcement post to {site}...")
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
            print(f"✅ Post published successfully!")
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
        description="Create Houston Sip Queen theme and publish announcement post"
    )
    parser.add_argument(
        '--site',
        default='houstonsipqueen.com',
        help='Site key for WordPress'
    )
    parser.add_argument(
        '--css-only',
        action='store_true',
        help='Only deploy CSS theme (skip post)'
    )
    parser.add_argument(
        '--post-only',
        action='store_true',
        help='Only publish post (skip CSS)'
    )

    args = parser.parse_args()

    print("🍸 Houston Sip Queen Theme & Announcement Post")
    print("=" * 60)

    css_deployed = False
    post_published = False

    # Deploy CSS
    if not args.post_only:
        css_deployed = deploy_css_via_functions_php(args.site)
    else:
        print("⏭️  Skipping CSS deployment (--post-only)")

    # Publish post
    if not args.css_only:
        result = publish_announcement_post(args.site)
        if result and result.get("ok"):
            post_published = True
    else:
        print("⏭️  Skipping post publication (--css-only)")

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  CSS Theme: {'✅ Deployed' if css_deployed else '❌ Failed'}")
    print(
        f"  Announcement Post: {'✅ Published' if post_published else '❌ Failed'}")

    if css_deployed and post_published:
        print("\n✅ All tasks complete!")
        return 0
    elif css_deployed or post_published:
        print("\n🟡 Partial completion - check errors above")
        return 1
    else:
        print("\n❌ All tasks failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())

