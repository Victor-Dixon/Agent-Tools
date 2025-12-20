#!/usr/bin/env python3
"""
Analyze and fix duplicate content issue on dadudekc.com.

The issue: Both blog posts have identical CSS embedded in their content,
making them appear as duplicates even though they should have different content.
"""

import json
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Install required packages: pip install requests beautifulsoup4")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

site_url = "https://dadudekc.com"
api_url = f"{site_url}/wp-json/wp/v2/posts"

print("🔍 Fetching posts from dadudekc.com...\n")

try:
    response = requests.get(api_url, params={"per_page": 100}, timeout=10)
    if response.status_code != 200:
        print(f"❌ Failed to fetch posts: HTTP {response.status_code}")
        sys.exit(1)

    posts = response.json()
    print(f"✅ Found {len(posts)} post(s)\n")

    analysis = {
        "total_posts": len(posts),
        "posts": [],
        "duplicate_css_issue": False,
        "recommendations": []
    }

    for post in posts:
        post_id = post.get('id')
        title = post.get('title', {}).get('rendered', 'N/A')
        content = post.get('content', {}).get('rendered', '')
        date = post.get('date', 'N/A')
        link = post.get('link', 'N/A')

        # Parse HTML to extract actual content vs CSS
        soup = BeautifulSoup(content, 'html.parser')

        # Find style tags
        style_tags = soup.find_all('style')
        css_content = '\n'.join([tag.get_text() for tag in style_tags])

        # Remove style tags to get actual content
        for tag in style_tags:
            tag.decompose()

        actual_content = soup.get_text().strip()

        post_analysis = {
            "id": post_id,
            "title": title,
            "date": date,
            "link": link,
            "has_css": len(style_tags) > 0,
            "css_length": len(css_content),
            "content_length": len(actual_content),
            "content_preview": actual_content[:200] if actual_content else "No content"
        }

        analysis["posts"].append(post_analysis)

        print(f"📝 Post ID {post_id}: '{title}'")
        print(f"   Date: {date}")
        print(f"   Link: {link}")
        print(
            f"   Has embedded CSS: {'✅' if post_analysis['has_css'] else '❌'}")
        if post_analysis['has_css']:
            print(f"   CSS length: {post_analysis['css_length']} chars")
        print(f"   Content length: {post_analysis['content_length']} chars")
        print(
            f"   Content preview: {post_analysis['content_preview'][:100]}...")
        print()

    # Check if CSS is identical across posts
    if len(posts) >= 2:
        css_list = []
        for post in analysis["posts"]:
            if post["has_css"]:
                # Get CSS from original post
                post_idx = analysis["posts"].index(post)
                original_content = posts[post_idx].get(
                    'content', {}).get('rendered', '')
                soup = BeautifulSoup(original_content, 'html.parser')
                css = '\n'.join([tag.get_text()
                                for tag in soup.find_all('style')])
                css_list.append((post["id"], css))

        if len(css_list) >= 2:
            # Compare CSS
            css_1 = css_list[0][1]
            css_2 = css_list[1][1]

            if css_1 == css_2:
                analysis["duplicate_css_issue"] = True
                analysis["recommendations"].append(
                    "Both posts have identical embedded CSS. The CSS should be moved to the theme's "
                    "style.css or added via WordPress Customizer instead of embedding in each post."
                )
                print("⚠️  ISSUE FOUND: Both posts have identical embedded CSS!")
                print("   This makes the posts appear as duplicates.")
                print(
                    "   Recommendation: Move CSS to theme stylesheet, not embedded in posts.\n")
            else:
                print("✅ CSS is different between posts (not a duplicate issue)\n")

    # Check if actual content is different
    if len(analysis["posts"]) >= 2:
        content_1 = analysis["posts"][0]["content_preview"]
        content_2 = analysis["posts"][1]["content_preview"]

        if content_1 == content_2 or not content_1 or not content_2:
            analysis["recommendations"].append(
                "Posts may have duplicate or empty content. Verify that each post has unique content."
            )
            print("⚠️  WARNING: Posts may have duplicate or missing content!")
        else:
            print("✅ Posts have different content (not duplicates)\n")

    # Save analysis
    output_file = Path("docs/blog/dadudekc_duplicate_analysis.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)

    print(f"✅ Analysis saved to: {output_file}\n")

    # Generate recommendations report
    if analysis["recommendations"]:
        print("📋 RECOMMENDATIONS:")
        for i, rec in enumerate(analysis["recommendations"], 1):
            print(f"   {i}. {rec}")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total posts: {analysis['total_posts']}")
    print(
        f"Duplicate CSS issue: {'Yes' if analysis['duplicate_css_issue'] else 'No'}")
    print(f"Recommendations: {len(analysis['recommendations'])}")
    print("\n✅ Analysis complete!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
