#!/usr/bin/env python3
"""
Fetch Blog Post Structure
=========================

Fetches a blog post from dadudekc.com and extracts its structure
for template creation.

Author: Agent-7 (Web Development Specialist)
"""

import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ ERROR: Required packages not installed.")
    print("   Install with: pip install requests beautifulsoup4")
    sys.exit(1)


def find_recent_blog_post(base_url: str = "https://dadudekc.com"):
    """Find a recent blog post URL."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Try WordPress REST API first
    try:
        api_url = f"{base_url}/wp-json/wp/v2/posts?per_page=1"
        resp = session.get(api_url, timeout=10)
        if resp.status_code == 200:
            posts = resp.json()
            if posts:
                return posts[0].get('link', '')
    except Exception:
        pass
    
    # Try fetching main page and finding blog links
    try:
        resp = session.get(base_url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for blog post links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if '/blog/' in href or '/post/' in href or '/article/' in href:
                    if not href.startswith('http'):
                        href = f"{base_url}{href}"
                    return href
    except Exception:
        pass
    
    return None


def extract_structure(post_url: str):
    """Extract the structure of a blog post."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        resp = session.get(post_url, timeout=10)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find the main content area
        content = soup.find('article') or soup.find('main') or soup.find('div', class_=lambda x: x and 'content' in x.lower())
        
        if not content:
            content = soup.find('body')
        
        structure = {
            'url': post_url,
            'title': soup.find('title'),
            'headings': [],
            'sections': [],
            'html_structure': str(content)[:5000] if content else None
        }
        
        # Extract headings
        for heading in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            structure['headings'].append({
                'level': heading.name,
                'text': heading.get_text(strip=True),
                'classes': heading.get('class', [])
            })
        
        # Extract sections
        sections = content.find_all(['div', 'section', 'article'])
        for section in sections[:10]:  # Limit to first 10
            classes = section.get('class', [])
            if classes or section.find(['h1', 'h2', 'h3']):
                structure['sections'].append({
                    'tag': section.name,
                    'classes': classes,
                    'has_heading': bool(section.find(['h1', 'h2', 'h3']))
                })
        
        return structure
        
    except Exception as e:
        print(f"❌ Error fetching post: {e}")
        return None


def main():
    """Main function."""
    print("🔍 Finding recent blog post...")
    post_url = find_recent_blog_post()
    
    if not post_url:
        print("❌ Could not find a blog post URL")
        print("   Please provide the exact blog post URL")
        return 1
    
    print(f"✅ Found blog post: {post_url}")
    print()
    print("📊 Extracting structure...")
    
    structure = extract_structure(post_url)
    
    if not structure:
        print("❌ Could not extract structure")
        return 1
    
    print("✅ Structure extracted!")
    print()
    print("=" * 60)
    print("BLOG POST STRUCTURE")
    print("=" * 60)
    print(f"URL: {structure['url']}")
    print()
    print(f"Headings found: {len(structure['headings'])}")
    for heading in structure['headings'][:10]:
        print(f"  {heading['level'].upper()}: {heading['text'][:60]}")
    print()
    print(f"Sections found: {len(structure['sections'])}")
    print()
    print("HTML Structure (first 2000 chars):")
    print("-" * 60)
    if structure['html_structure']:
        print(structure['html_structure'][:2000])
    
    # Save to file
    output_file = Path("docs/blog/blog_post_structure_analysis.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Blog Post Structure Analysis\n\n")
        f.write(f"**URL**: {structure['url']}\n\n")
        f.write("## Headings\n\n")
        for heading in structure['headings']:
            f.write(f"- **{heading['level'].upper()}**: {heading['text']}\n")
        f.write("\n## HTML Structure\n\n")
        f.write("```html\n")
        if structure['html_structure']:
            f.write(structure['html_structure'][:5000])
        f.write("\n```\n")
    
    print()
    print(f"✅ Structure saved to: {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


