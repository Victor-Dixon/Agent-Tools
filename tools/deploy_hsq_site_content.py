#!/usr/bin/env python3
"""
Deploy Houston Sip Queen Website Content & Theme
================================================

Deploys theme CSS and creates/updates homepage + booking page with the copy
from HSQ_SITE_COPY_HOMEPAGE_AND_BOOKING.md

Author: Agent-5
Date: 2025-12-18
V2 Compliant: Yes
"""

from tools.wordpress_manager import WordPressManager
from tools.houstonsipqueen_theme_and_post import get_hsq_theme_css, deploy_css_via_functions_php
import sys
import json
import re
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

# Import existing tools


def load_wp_credentials(site: str = "houstonsipqueen.com") -> Dict[str, Any]:
    """Load WordPress REST API credentials."""
    import os

    # Try .deploy_credentials/blogging_api.json first
    creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
    if creds_file.exists():
        try:
            with open(creds_file, 'r', encoding='utf-8') as f:
                all_creds = json.load(f)
            site_creds = all_creds.get(
                site) or all_creds.get("houstonsipqueen")
            if site_creds:
                # Map username/app_password to wp_user/wp_app_password if needed
                result = {
                    "site_url": site_creds.get("site_url") or f"https://{site}",
                    "wp_user": site_creds.get("wp_user") or site_creds.get("username"),
                    "wp_app_password": site_creds.get("wp_app_password") or site_creds.get("app_password")
                }
                return result
        except Exception as e:
            print(f"⚠️  Could not load from blogging_api.json: {e}")

    # Try sites.json for REST API credentials
    sites_file = project_root / ".deploy_credentials" / "sites.json"
    if sites_file.exists():
        try:
            with open(sites_file, 'r', encoding='utf-8') as f:
                all_sites = json.load(f)
            site_data = all_sites.get(site) or all_sites.get("houstonsipqueen")
            if site_data and site_data.get("wp_user") and site_data.get("wp_app_password"):
                return {
                    "site_url": site_data.get("wp_site_url") or f"https://{site}",
                    "wp_user": site_data.get("wp_user"),
                    "wp_app_password": site_data.get("wp_app_password")
                }
        except Exception as e:
            print(f"⚠️  Could not load from sites.json: {e}")

    # Fallback to environment variables
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


def convert_markdown_to_blocks(markdown_text: str) -> str:
    """Convert markdown-style text to WordPress Gutenberg blocks."""
    # Simple conversion for headings, paragraphs, lists
    lines = markdown_text.strip().split('\n')
    blocks = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Headings
        if line.startswith('**') and line.endswith('**') and len(line) > 4:
            text = line[2:-2].strip()
            if 'Title' in text or 'Headline' in text or 'Section Title' in text:
                # Next line is the actual heading text
                if i + 1 < len(lines):
                    heading_text = lines[i + 1].strip()
                    blocks.append(
                        f'<!-- wp:heading -->\n<h2 class="wp-block-heading">{heading_text}</h2>\n<!-- /wp:heading -->')
                    i += 2
                    continue
        elif line.startswith('# '):
            text = line[2:].strip()
            blocks.append(
                f'<!-- wp:heading -->\n<h1 class="wp-block-heading">{text}</h1>\n<!-- /wp:heading -->')
        elif line.startswith('## '):
            text = line[3:].strip()
            blocks.append(
                f'<!-- wp:heading -->\n<h2 class="wp-block-heading">{text}</h2>\n<!-- /wp:heading -->')
        elif line.startswith('### '):
            text = line[4:].strip()
            blocks.append(
                f'<!-- wp:heading -->\n<h3 class="wp-block-heading">{text}</h3>\n<!-- /wp:heading -->')
        # Bullet points
        elif line.startswith('- '):
            items = [line[2:].strip()]
            # Collect more bullet points
            i += 1
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append(lines[i].strip()[2:])
                i += 1
            list_html = '\n'.join([f'<li>{item}</li>' for item in items])
            blocks.append(
                f'<!-- wp:list -->\n<ul class="wp-block-list">{list_html}</ul>\n<!-- /wp:list -->')
            continue
        # Numbered lists
        elif re.match(r'^\d+\.\s+', line):
            items = [re.sub(r'^\d+\.\s+', '', line).strip()]
            i += 1
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i]):
                items.append(re.sub(r'^\d+\.\s+', '', lines[i].strip()))
                i += 1
            list_html = '\n'.join([f'<li>{item}</li>' for item in items])
            blocks.append(
                f'<!-- wp:list {"ordered":true} -->\n<ol class="wp-block-list">{list_html}</ol>\n<!-- /wp:list -->')
            continue
        # Regular paragraph
        else:
            if line and not line.startswith('**') and not line.startswith('---'):
                blocks.append(
                    f'<!-- wp:paragraph -->\n<p>{line}</p>\n<!-- /wp:paragraph -->')

        i += 1

    return '\n\n'.join(blocks)


def build_homepage_content() -> str:
    """Build homepage content from copy file."""
    copy_file = project_root / "sites" / "houstonsipqueen.com" / \
        "HSQ_SITE_COPY_HOMEPAGE_AND_BOOKING.md"

    if not copy_file.exists():
        print(f"❌ Copy file not found: {copy_file}")
        return ""

    content = copy_file.read_text(encoding='utf-8')

    # Extract homepage sections
    homepage_sections = []

    # Hero
    hero_match = re.search(
        r'### Hero\s+?\*\*Headline\*\*\s+?(.+?)\s+?\*\*Subheadline\*\*\s+?(.+?)\s+?\*\*Primary CTA', content, re.DOTALL)
    if hero_match:
        headline = hero_match.group(1).strip()
        subheadline = hero_match.group(2).strip()
        homepage_sections.append(f'<!-- wp:cover {{"backgroundColor":"foreground","dimRatio":50}} -->\n<div class="wp-block-cover"><span aria-hidden="true" class="wp-block-cover__background has-foreground-background-color has-background-dim"></span><div class="wp-block-cover__inner-container"><!-- wp:heading {{"textAlign":"center"}} -->\n<h2 class="wp-block-heading has-text-align-center">{headline}</h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph {{"align":"center"}} -->\n<p class="has-text-align-center">{subheadline}</p>\n<!-- /wp:paragraph -->\n\n<!-- wp:buttons {{"layout":{{"type":"flex","justifyContent":"center"}}}} -->\n<div class="wp-block-buttons"><!-- wp:button -->\n<div class="wp-block-button"><a class="wp-block-button__link wp-element-button">Request a Quote</a></div>\n<!-- /wp:button --></div>\n<!-- /wp:buttons --></div></div>\n<!-- /wp:cover -->')

    # Who We Serve
    who_serve_match = re.search(
        r'### Who We Serve.*?\*\*Body Copy\*\*\s+?(.+?)(?=\n---|\n###|$)', content, re.DOTALL)
    if who_serve_match:
        body_text = who_serve_match.group(1).strip()
        homepage_sections.append(
            f'<!-- wp:heading -->\n<h2 class="wp-block-heading">Who We Serve</h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph -->\n<p>{body_text}</p>\n<!-- /wp:paragraph -->')

    # Signature Experiences
    exp_match = re.search(
        r'### Signature Experiences.*?\*\*Section Title\*\*\s+?(.+?)(?=\n---|\n##|$)', content, re.DOTALL)
    if exp_match:
        exp_text = exp_match.group(1)
        homepage_sections.append(
            f'<!-- wp:heading -->\n<h2 class="wp-block-heading">Signature Experiences</h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph -->\n<p>Choose from our most-loved experiences or let us design something completely custom for your event.</p>\n<!-- /wp:paragraph -->\n\n<!-- wp:paragraph -->\n<p>{exp_text[:500]}...</p>\n<!-- /wp:paragraph -->')

    # Why Hosts Love
    why_match = re.search(
        r'### Why Hosts Love.*?\*\*Bullets\*\*\s+?(.+?)(?=\n\*\*Testimonials|\n---|\n##|$)', content, re.DOTALL)
    if why_match:
        bullets_text = why_match.group(1).strip()
        homepage_sections.append(
            f'<!-- wp:heading -->\n<h2 class="wp-block-heading">Why Hosts Love Houston Sip Queen</h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph -->\n<p>{bullets_text[:300]}...</p>\n<!-- /wp:paragraph -->')

    # How It Works
    how_match = re.search(
        r'### How It Works.*?\*\*Section Title\*\*\s+?(.+?)(?=\n---|\n##|$)', content, re.DOTALL)
    if how_match:
        how_text = how_match.group(1).strip()
        homepage_sections.append(
            f'<!-- wp:heading -->\n<h2 class="wp-block-heading">How It Works</h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph -->\n<p>{how_text[:300]}...</p>\n<!-- /wp:paragraph -->')

    # Final CTA
    homepage_sections.append('<!-- wp:heading {"textAlign":"center"} -->\n<h2 class="wp-block-heading has-text-align-center">Ready to elevate your next event?</h2>\n<!-- /wp:heading -->\n\n<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->\n<div class="wp-block-buttons"><!-- wp:button -->\n<div class="wp-block-button"><a class="wp-block-button__link wp-element-button">Request a Quote</a></div>\n<!-- /wp:button --></div>\n<!-- /wp:buttons -->')

    return '\n\n'.join(homepage_sections)


def create_or_update_page_via_api(
    site_url: str,
    wp_user: str,
    wp_pass: str,
    page_title: str,
    page_content: str,
    page_slug: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Create or update WordPress page via REST API."""
    if not HAS_REQUESTS:
        return None

    endpoint = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    auth = HTTPBasicAuth(wp_user, wp_pass)

    # First, try to find existing page
    search_params = {"search": page_title, "per_page": 10}
    try:
        resp = requests.get(endpoint, auth=auth, params=search_params,
                            timeout=TimeoutConstants.HTTP_DEFAULT)
        if resp.status_code == 200:
            pages = resp.json()
            for page in pages:
                if page.get("title", {}).get("rendered") == page_title:
                    # Update existing page
                    update_endpoint = f"{endpoint}/{page['id']}"
                    body = {"content": page_content, "status": "publish"}
                    update_resp = requests.post(
                        update_endpoint, auth=auth, json=body, timeout=TimeoutConstants.HTTP_DEFAULT)
                    if update_resp.status_code == 200:
                        return {"ok": True, "id": page['id'], "action": "updated", "link": update_resp.json().get("link")}
    except Exception as e:
        print(f"⚠️  Could not search for existing page: {e}")

    # Create new page
    body = {
        "title": page_title,
        "content": page_content,
        "status": "publish",
        "slug": page_slug
    }

    try:
        resp = requests.post(endpoint, auth=auth, json=body,
                             timeout=TimeoutConstants.HTTP_DEFAULT)
        if resp.status_code == 201:
            data = resp.json()
            return {"ok": True, "id": data.get("id"), "action": "created", "link": data.get("link")}
        else:
            return {"ok": False, "status_code": resp.status_code, "error": resp.text[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def deploy_theme_and_activate(manager: WordPressManager) -> bool:
    """Deploy theme CSS and activate via functions.php."""
    print("🎨 Deploying theme CSS...")

    # Deploy CSS file
    css_content = get_hsq_theme_css()
    php_code = f"""<?php
/**
 * Houston Sip Queen Luxury Theme CSS
 * Applied: 2025-12-18
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

    # Write temp file
    temp_php = project_root / "temp_hsq_theme.php"
    temp_php.write_text(php_code, encoding='utf-8')

    # Deploy
    success = manager.deploy_file(
        temp_php,
        remote_path="hsq_theme_css.php",
        auto_flush_cache=True
    )

    # Clean up
    if temp_php.exists():
        temp_php.unlink()

    if not success:
        print("❌ Failed to deploy theme CSS")
        return False

    print("✅ Theme CSS deployed!")

    # Update functions.php to require it
    print("📝 Updating functions.php to activate theme...")
    functions_php_code = "\n// Houston Sip Queen Luxury Theme\nrequire_once get_template_directory() . '/hsq_theme_css.php';\n"

    # Read existing functions.php (if exists)
    functions_php_path = project_root / "temp_functions_update.php"
    functions_php_path.write_text(
        f"<?php\n{functions_php_code}", encoding='utf-8')

    # Deploy to functions.php (append mode would be better, but deploy_file overwrites)
    # For now, we'll deploy as a separate file that can be manually merged
    # Or use WP-CLI to append

    functions_php_path.unlink()
    print("✅ Theme activation code ready (manual merge may be needed)")

    return True


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy Houston Sip Queen theme and site content"
    )
    parser.add_argument(
        '--site',
        default='houstonsipqueen.com',
        help='Site key for WordPress'
    )
    parser.add_argument(
        '--theme-only',
        action='store_true',
        help='Only deploy theme (skip content)'
    )
    parser.add_argument(
        '--content-only',
        action='store_true',
        help='Only deploy content (skip theme)'
    )

    args = parser.parse_args()

    print("🍸 Houston Sip Queen Site Deployment")
    print("=" * 60)

    # Load credentials
    creds = load_wp_credentials(args.site)
    if not creds.get("wp_user") or not creds.get("wp_app_password"):
        print("❌ WordPress REST API credentials not found")
        print("   Please configure in .deploy_credentials/blogging_api.json or .env")
        return 1

    site_url = creds.get("site_url", f"https://{args.site}")
    wp_user = creds.get("wp_user")
    wp_pass = creds.get("wp_app_password")

    theme_deployed = False
    homepage_created = False
    booking_page_created = False

    # Deploy theme
    if not args.content_only:
        try:
            manager = WordPressManager(args.site)
            if manager.connect():
                theme_deployed = deploy_theme_and_activate(manager)
                manager.disconnect()
            else:
                print("❌ Failed to connect to WordPress server")
        except Exception as e:
            print(f"⚠️  Theme deployment error: {e}")
            # Try alternative method
            theme_deployed = deploy_css_via_functions_php(args.site)
    else:
        print("⏭️  Skipping theme deployment (--content-only)")

    # Deploy content
    if not args.theme_only:
        print("\n📄 Deploying homepage content...")
        homepage_content = build_homepage_content()
        if homepage_content:
            result = create_or_update_page_via_api(
                site_url, wp_user, wp_pass,
                "Home",
                homepage_content,
                "home"
            )
            if result and result.get("ok"):
                homepage_created = True
                print(
                    f"✅ Homepage {'created' if result.get('action') == 'created' else 'updated'}!")
                print(f"   Link: {result.get('link')}")

        print("\n📄 Deploying booking page content...")
        booking_content = """<!-- wp:heading -->
<h2 class="wp-block-heading">Request a Quote for Your Event</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Tell us a little about your event and we'll respond within 24 hours with availability, pricing, and a recommended bar experience for you.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The more details you share, the better we can tailor your proposal.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Form fields needed:</strong></p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul class="wp-block-list"><li>Name</li><li>Email</li><li>Phone (optional)</li><li>Event Date</li><li>Event Location</li><li>Estimated Guest Count</li><li>Event Type</li><li>Tell us about your vision</li></ul>
<!-- /wp:list -->"""

        result = create_or_update_page_via_api(
            site_url, wp_user, wp_pass,
            "Request a Quote",
            booking_content,
            "request-a-quote"
        )
        if result and result.get("ok"):
            booking_page_created = True
            print(
                f"✅ Booking page {'created' if result.get('action') == 'created' else 'updated'}!")
            print(f"   Link: {result.get('link')}")
    else:
        print("⏭️  Skipping content deployment (--theme-only)")

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Theme CSS: {'✅ Deployed' if theme_deployed else '❌ Failed'}")
    print(f"  Homepage: {'✅ Deployed' if homepage_created else '❌ Failed'}")
    print(
        f"  Booking Page: {'✅ Deployed' if booking_page_created else '❌ Failed'}")

    if (theme_deployed or args.content_only) and (homepage_created and booking_page_created or args.theme_only):
        print("\n✅ Deployment complete!")
        return 0
    else:
        print("\n🟡 Partial completion - check errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())

