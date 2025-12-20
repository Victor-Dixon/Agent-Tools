#!/usr/bin/env python3
"""
Create Vibe-Coded Work Review Blog Post
========================================

Creates and publishes a professional blog post reviewing the coding work.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.unified_blogging_automation import UnifiedBloggingAutomation


def main():
    """Create and publish the vibe-coded work review blog post."""
    
    # Read the blog post content
    blog_content_path = project_root / "docs" / "blog" / "vibe_coded_work_review.md"
    
    if not blog_content_path.exists():
        print(f"❌ Blog content file not found: {blog_content_path}")
        return 1
    
    with open(blog_content_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Initialize blogging automation
    automation = UnifiedBloggingAutomation()
    
    if not automation.clients:
        print("❌ No WordPress sites configured")
        print("   Configure sites in .deploy_credentials/blogging_api.json")
        return 1
    
    # Blog post metadata
    title = "A Professional Review of My Vibe-Coded Work: Building with Intuition and Structure"
    excerpt = "An honest review of my coding approach, examining what works, what could be improved, and how this style has shaped the projects I've built."
    
    print("=" * 60)
    print("BLOG POST: Vibe-Coded Work Review")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"Content length: {len(content)} characters")
    print(f"Available sites: {', '.join(automation.clients.keys())}")
    print()
    
    # Ask which site to publish to
    print("Available WordPress sites:")
    for i, site_id in enumerate(automation.clients.keys(), 1):
        print(f"  {i}. {site_id}")
    
    print()
    choice = input("Select site number (or 'all' for all sites, 'draft' for draft preview): ").strip().lower()
    
    if choice == 'draft':
        # Preview mode
        print("\n📝 DRAFT PREVIEW:")
        print("=" * 60)
        print(f"Title: {title}")
        print(f"\nExcerpt: {excerpt}")
        print(f"\nContent preview (first 500 chars):\n{content[:500]}...")
        print("\n✅ This is a preview. Use a site number to publish.")
        return 0
    
    # Determine sites to publish to
    if choice == 'all':
        sites_to_publish = list(automation.clients.keys())
    else:
        try:
            site_index = int(choice) - 1
            sites_to_publish = [list(automation.clients.keys())[site_index]]
        except (ValueError, IndexError):
            print(f"❌ Invalid choice: {choice}")
            return 1
    
    # Ask for status
    print()
    status_choice = input("Publish as 'draft' or 'publish'? (default: draft): ").strip().lower()
    status = "publish" if status_choice == "publish" else "draft"
    
    # Ask for site purposes (optional)
    print()
    print("Site purposes (optional, press Enter to skip):")
    site_purpose_map = {}
    for site_id in sites_to_publish:
        purpose = input(f"  {site_id} purpose (swarm_system/personal/trading_education/etc): ").strip()
        if purpose:
            site_purpose_map[site_id] = purpose
    
    # Publish to selected sites
    print()
    print("🚀 Publishing blog post...")
    print()
    
    results = {}
    for site_id in sites_to_publish:
        site_purpose = site_purpose_map.get(site_id)
        
        result = automation.publish_to_site(
            site_id=site_id,
            title=title,
            content=content,
            site_purpose=site_purpose,
            excerpt=excerpt,
            status=status
        )
        
        results[site_id] = result
        
        if result.get("success"):
            post_id = result.get("post_id")
            post_url = result.get("post_url", "N/A")
            print(f"✅ {site_id}: Published successfully!")
            print(f"   Post ID: {post_id}")
            print(f"   URL: {post_url}")
        else:
            error = result.get("error", "Unknown error")
            print(f"❌ {site_id}: Failed - {error}")
        print()
    
    # Summary
    print("=" * 60)
    print("PUBLICATION SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results.values() if r.get("success"))
    total = len(results)
    print(f"Successfully published: {successful}/{total}")
    
    if successful > 0:
        print("\n✅ Blog post published successfully!")
    else:
        print("\n❌ Failed to publish to any sites")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

