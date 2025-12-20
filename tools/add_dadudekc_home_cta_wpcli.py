#!/usr/bin/env python3
"""
Add Primary CTA Section to dadudekc.com Homepage (WP-CLI Method)
==================================================================

Adds a clear primary CTA section using WP-CLI.

Author: Agent-2
"""

from tools.wordpress_manager import WordPressManager
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def generate_cta_section() -> str:
    """Generate primary CTA section HTML."""
    cta_html = """
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"4rem","bottom":"4rem"},"margin":{"top":"0","bottom":"0"}}},"backgroundColor":"primary","layout":{"type":"constrained"}} -->
<div class="wp-block-group alignfull has-primary-background-color has-background" style="margin-top:0;margin-bottom:0;padding-top:4rem;padding-bottom:4rem">
    <!-- wp:columns {"align":"wide"} -->
    <div class="wp-block-columns alignwide">
        <!-- wp:column {"width":"100%"} -->
        <div class="wp-block-column" style="flex-basis:100%">
            <!-- wp:heading {"textAlign":"center","level":2,"style":{"typography":{"fontSize":"2.5rem"},"spacing":{"margin":{"bottom":"1rem"}}}} -->
            <h2 class="wp-block-heading has-text-align-center" style="margin-bottom:1rem;font-size:2.5rem">Ready to Automate Your Workflow?</h2>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph {"align":"center","style":{"spacing":{"margin":{"bottom":"2rem"}}}} -->
            <p class="has-text-align-center" style="margin-bottom:2rem">I build automation systems that save teams hours every week. Let's discuss how I can help streamline your operations.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
            <div class="wp-block-buttons">
                <!-- wp:button {"backgroundColor":"secondary","textColor":"primary","width":100,"style":{"border":{"radius":"0.5rem"},"spacing":{"padding":{"top":"1rem","bottom":"1rem","left":"2rem","right":"2rem"}}}} -->
                <div class="wp-block-button has-custom-width wp-block-button__width-100" style="width:100%">
                    <a class="wp-block-button__link has-primary-color has-secondary-background-color has-text-color has-background wp-element-button" href="/contact" style="border-radius:0.5rem;padding-top:1rem;padding-bottom:1rem;padding-left:2rem;padding-right:2rem">Work with Me</a>
                </div>
                <!-- /wp:button -->
            </div>
            <!-- /wp:buttons -->
        </div>
        <!-- /wp:column -->
    </div>
    <!-- /wp:columns -->
</div>
<!-- /wp:group -->
"""
    return cta_html


def main():
    """Main execution."""
    print("🔧 Adding primary CTA section to dadudekc.com homepage...\n")

    manager = WordPressManager("dadudekc.com")
    if not manager.connect():
        print("❌ Failed to connect to server")
        sys.exit(1)

    # Get homepage - try to find front page
    pages_json, stderr, code = manager.wp_cli(
        "post list --post_type=page --format=json --fields=ID,post_name,post_title")
    print(f"WP-CLI return code: {code}")
    print(f"WP-CLI stderr: {stderr[:200] if stderr else 'None'}")
    print(f"WP-CLI stdout length: {len(pages_json) if pages_json else 0}")

    if pages_json and pages_json.strip():
        try:
            pages = json.loads(pages_json)
            print(f"✅ Found {len(pages)} pages")
            for p in pages[:5]:
                print(
                    f"  ID: {p.get('ID')}, Slug: {p.get('post_name')}, Title: {p.get('post_title', 'N/A')[:50]}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response: {pages_json[:200]}")
            pages = []
    else:
        pages = []

    homepage = None
    for page in pages:
        slug = page.get("post_name", "")
        if slug in ["home", "front-page", ""] or page.get("ID") == 1:
            homepage = page
            break

    if not homepage and pages:
        # Get first page by menu order or ID
        homepage = pages[0]

    if not homepage:
        print("❌ Could not find homepage")
        print("💡 May need to create homepage or check WordPress reading settings")
        sys.exit(1)

    page_id = homepage.get("ID")
    content = homepage.get("post_content", "")

    print(
        f"✅ Found homepage (ID: {page_id}, slug: {homepage.get('post_name', 'N/A')})")

    # Check if CTA already exists
    if "Ready to Automate Your Workflow" in content or "Work with Me" in content:
        print("⏭️  CTA section already exists on homepage")
        manager.disconnect()
        return

    # Add CTA section
    cta_section = generate_cta_section()
    new_content = content + "\n" + cta_section

    # Update page via WP-CLI
    # Escape content for shell
    import shlex
    escaped_content = shlex.quote(new_content)
    stdout, stderr, code = manager.wp_cli(
        f"post update {page_id} --post_content={escaped_content}"
    )

    if code == 0:
        print("✅ Added CTA section to homepage")
        manager.purge_caches()
    else:
        print(f"❌ Failed to update homepage: {stderr}")
        # Try alternative method - update via file
        print("💡 Alternative: Update homepage content manually in WordPress admin")

    manager.disconnect()

    if code == 0:
        print("\n✅ Primary CTA section added to homepage!")
        print(f"📋 View at: https://dadudekc.com")


if __name__ == "__main__":
    main()
