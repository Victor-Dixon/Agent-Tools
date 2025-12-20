#!/usr/bin/env python3
"""
Set up 301 Redirects for FreeRideInvestor.com Duplicate TSLA Posts
==================================================================

Creates 301 redirects for duplicate TSLA post slugs to canonical version.
Uses WP-CLI with redirect plugin or .htaccess fallback.

Author: Agent-2
"""

from tools.wordpress_manager import WordPressManager
import json
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Load credentials
creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
with open(creds_file) as f:
    creds_data = json.load(f)

SITE_CONFIG = creds_data["freerideinvestor"]
SITE_URL = SITE_CONFIG["site_url"]
USERNAME = SITE_CONFIG["username"]
APP_PASSWORD = SITE_CONFIG["app_password"]

API_BASE = f"{SITE_URL}/wp-json/wp/v2"
AUTH = HTTPBasicAuth(USERNAME, APP_PASSWORD.replace(" ", ""))


def get_canonical_tsla_post():
    """Get the canonical TSLA post."""
    url = f"{API_BASE}/posts"
    # Get all posts (search may not work reliably)
    params = {"per_page": 100, "status": "any"}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)
    if response.status_code == 200:
        posts = response.json()
        # Debug: print all TSLA-related posts
        tsla_posts = [p for p in posts if "tsla" in p.get("slug", "").lower()]
        if tsla_posts:
            print(f"🔍 Found {len(tsla_posts)} TSLA-related posts")
        # Find canonical (not ending in -4, -3, -2, -base)
        for post in posts:
            slug = post.get("slug", "")
            if "tsla" in slug.lower():
                # Check if it's canonical (doesn't end with duplicate pattern)
                is_duplicate = any(slug.endswith(
                    f"-{i}") for i in [2, 3, 4]) or slug.endswith("-base")
                if not is_duplicate:
                    # Publish it if it's draft
                    if post.get("status") == "draft":
                        print(
                            f"📝 Publishing canonical post (ID: {post['id']}, slug: {slug})...")
                        update_url = f"{API_BASE}/posts/{post['id']}"
                        update_response = requests.post(
                            update_url, json={"status": "publish"}, auth=AUTH, timeout=30)
                        if update_response.status_code == 200:
                            print(f"✅ Published canonical post")
                            # Refresh post data
                            post_response = requests.get(
                                update_url, auth=AUTH, timeout=30)
                            if post_response.status_code == 200:
                                post = post_response.json()
                    return post
    return None


def get_duplicate_tsla_posts():
    """Get duplicate TSLA posts."""
    url = f"{API_BASE}/posts"
    params = {"per_page": 100, "search": "tsla", "status": "draft"}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)
    if response.status_code == 200:
        posts = response.json()
        duplicates = []
        for post in posts:
            slug = post.get("slug", "")
            if any(pattern in slug for pattern in ["-4", "-3", "-2", "-base"]):
                duplicates.append(post)
        return duplicates
    return []


def setup_redirects_via_wp_cli(manager: WordPressManager, duplicates: list, canonical: dict):
    """Set up redirects using WP-CLI redirect plugin."""
    canonical_slug = canonical.get("slug")
    canonical_url = canonical.get("link", "").replace(SITE_URL, "")

    print(f"📋 Setting up redirects to canonical: {canonical_slug}\n")

    # Try Redirection plugin first
    for dup in duplicates:
        dup_slug = dup.get("slug")
        dup_url = f"/{dup_slug}/"
        redirect_url = canonical_url if canonical_url.startswith(
            "/") else f"/{canonical_slug}/"

        # Try Redirection plugin
        stdout, stderr, code = manager.wp_cli(
            f'redirection add "{dup_url}" "{redirect_url}" 301'
        )
        if code == 0:
            print(f"✅ Redirect created: {dup_slug} → {canonical_slug}")
        else:
            # Try redirect plugin (different command format)
            stdout2, stderr2, code2 = manager.wp_cli(
                f'redirect add "{dup_url}" "{redirect_url}" 301'
            )
            if code2 == 0:
                print(f"✅ Redirect created: {dup_slug} → {canonical_slug}")
            else:
                print(f"⚠️  Could not create redirect via plugin: {dup_slug}")
                return False

    return True


def setup_redirects_via_htaccess(manager: WordPressManager, duplicates: list, canonical: dict):
    """Set up redirects via .htaccess file."""
    canonical_slug = canonical.get("slug")

    print(f"📝 Creating .htaccess redirects...\n")

    # Get WordPress root
    remote_base = manager.config.get("remote_base", "")
    if "/wp-content/themes/" in remote_base:
        wp_root = remote_base.split("/wp-content/themes/")[0]
    else:
        wp_root = "domains/freerideinvestor.com/public_html"

    # Build redirect rules
    redirect_rules = []
    for dup in duplicates:
        dup_slug = dup.get("slug")
        redirect_rules.append(
            f'RewriteRule ^{dup_slug}/?$ /{canonical_slug}/ [R=301,L]'
        )

    if not redirect_rules:
        print("⚠️  No redirects to create")
        return False

    # Read existing .htaccess
    htaccess_path = f"{wp_root}/.htaccess"
    stdout, stderr, code = manager.conn_manager.execute_command(
        f"cat {htaccess_path} 2>/dev/null || echo ''"
    )
    existing_content = stdout if code == 0 else ""

    # Check if redirects already exist
    marker = "# FreeRideInvestor TSLA redirects - Auto-generated"
    if marker in existing_content:
        print("⏭️  Redirects already exist in .htaccess")
        return True

    # Add redirect rules
    new_rules = f"""
{marker}
# Redirect duplicate TSLA post slugs to canonical
"""
    for rule in redirect_rules:
        new_rules += f"{rule}\n"

    # Insert after RewriteEngine On if present, otherwise append
    if "RewriteEngine On" in existing_content:
        new_content = existing_content.replace(
            "RewriteEngine On",
            f"RewriteEngine On\n{new_rules}"
        )
    else:
        new_content = existing_content + "\n" + new_rules

    # Write back to .htaccess
    # Use echo to write (safer than SFTP for .htaccess)
    temp_file = f"{wp_root}/.htaccess.tmp"
    manager.conn_manager.execute_command(
        f'echo "{new_content.replace(chr(34), chr(92)+chr(34))}" > {temp_file}'
    )
    manager.conn_manager.execute_command(f"mv {temp_file} {htaccess_path}")

    print(f"✅ Added {len(redirect_rules)} redirect rules to .htaccess")
    return True


def main():
    """Main execution."""
    print("🔧 Setting up 301 redirects for duplicate TSLA posts...\n")

    # Get posts via REST API
    canonical = get_canonical_tsla_post()
    if not canonical:
        print("❌ Could not find canonical TSLA post")
        sys.exit(1)

    duplicates = get_duplicate_tsla_posts()
    if not duplicates:
        print("⏭️  No duplicate TSLA posts found (may have been deleted)")
        sys.exit(0)

    print(
        f"✅ Found canonical post: {canonical.get('title')} (slug: {canonical.get('slug')})")
    print(f"📋 Found {len(duplicates)} duplicate posts to redirect\n")

    # Connect via WP-CLI
    manager = WordPressManager("freerideinvestor")
    if not manager.connect():
        print("❌ Failed to connect to server")
        sys.exit(1)

    # Try WP-CLI redirect plugin first
    success = setup_redirects_via_wp_cli(manager, duplicates, canonical)

    # Fallback to .htaccess if plugin method failed
    if not success:
        print("\n🔄 Falling back to .htaccess method...")
        success = setup_redirects_via_htaccess(manager, duplicates, canonical)

    if success:
        # Flush cache
        manager.purge_caches()
        print("\n✅ Redirects set up successfully!")
        print("\n📋 Redirects created:")
        for dup in duplicates:
            print(f"   /{dup.get('slug')}/ → /{canonical.get('slug')}/")
    else:
        print("\n⚠️  Could not set up redirects automatically")
        print("💡 Manual steps:")
        print("   1. Install a redirect plugin (e.g., Redirection)")
        print("   2. Or add redirect rules to .htaccess manually")

    manager.disconnect()


if __name__ == "__main__":
    main()
