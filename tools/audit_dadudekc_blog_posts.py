#!/usr/bin/env python3
"""
DadudekC Blog Posts Audit Tool
==============================

Audits WordPress blog posts for:
1. Duplicate posts
2. Missing initial "About this site" posts
3. Post quality and structure

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-12-14
Priority: HIGH
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from difflib import SequenceMatcher

import requests
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class BlogPostAuditor:
    """Audits WordPress blog posts."""
    
    def __init__(self, base_url: str = "https://dadudekc.com"):
        """Initialize auditor."""
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_all_posts(self) -> List[Dict[str, Any]]:
        """Get all blog posts via WordPress REST API."""
        posts = []
        page = 1
        per_page = 100
        
        try:
            while True:
                url = f"{self.base_url}/wp-json/wp/v2/posts"
                params = {
                    "per_page": per_page,
                    "page": page,
                    "status": "publish",
                    "_embed": True
                }
                
                resp = self.session.get(url, params=params, timeout=10)
                if resp.status_code != 200:
                    break
                
                page_posts = resp.json()
                if not page_posts:
                    break
                
                posts.extend(page_posts)
                
                # Check if there are more pages
                if len(page_posts) < per_page:
                    break
                
                page += 1
                
        except Exception as e:
            print(f"❌ Error fetching posts: {e}")
        
        return posts
    
    def find_duplicates(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find duplicate blog posts."""
        duplicates = []
        
        # Group by title similarity
        title_groups = defaultdict(list)
        for post in posts:
            title = post.get('title', {}).get('rendered', '').strip().lower()
            title_groups[title].append(post)
        
        # Find exact title duplicates
        for title, post_list in title_groups.items():
            if len(post_list) > 1:
                duplicates.append({
                    "type": "exact_title",
                    "title": title,
                    "count": len(post_list),
                    "posts": [
                        {
                            "id": p.get("id"),
                            "link": p.get("link"),
                            "date": p.get("date"),
                            "slug": p.get("slug")
                        }
                        for p in post_list
                    ]
                })
        
        # Find content similarity duplicates
        content_duplicates = []
        for i, post1 in enumerate(posts):
            content1 = self._extract_text_content(post1.get('content', {}).get('rendered', ''))
            if not content1 or len(content1) < 100:  # Skip short posts
                continue
            
            for post2 in posts[i+1:]:
                content2 = self._extract_text_content(post2.get('content', {}).get('rendered', ''))
                if not content2 or len(content2) < 100:
                    continue
                
                similarity = SequenceMatcher(None, content1[:500], content2[:500]).ratio()
                if similarity > 0.85:  # 85% similarity threshold
                    content_duplicates.append({
                        "type": "content_similarity",
                        "similarity": similarity,
                        "post1": {
                            "id": post1.get("id"),
                            "title": post1.get('title', {}).get('rendered', ''),
                            "link": post1.get("link")
                        },
                        "post2": {
                            "id": post2.get("id"),
                            "title": post2.get('title', {}).get('rendered', ''),
                            "link": post2.get("link")
                        }
                    })
        
        return duplicates + content_duplicates
    
    def _extract_text_content(self, html: str) -> str:
        """Extract text content from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except Exception:
            return html
    
    def check_initial_post(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if initial 'About this site' post exists."""
        initial_keywords = [
            "about this site",
            "welcome",
            "introduction",
            "why this site",
            "purpose",
            "reason for this site"
        ]
        
        found = False
        matching_posts = []
        
        for post in posts:
            title = post.get('title', {}).get('rendered', '').lower()
            content = self._extract_text_content(
                post.get('content', {}).get('rendered', '')
            ).lower()
            
            # Check if post matches initial post criteria
            matches = any(keyword in title or keyword in content[:500] 
                         for keyword in initial_keywords)
            
            if matches:
                found = True
                matching_posts.append({
                    "id": post.get("id"),
                    "title": post.get('title', {}).get('rendered', ''),
                    "link": post.get("link"),
                    "date": post.get("date")
                })
        
        return {
            "has_initial_post": found,
            "matching_posts": matching_posts
        }
    
    def generate_initial_post_content(self) -> Dict[str, str]:
        """Generate initial 'About this site' post content."""
        title = "About This Site - DaDudeKC"
        content = """<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 12px; color: white; margin: 2rem 0;">
<h2 style="color: white; margin-top: 0;">Welcome to DaDudeKC</h2>
</div>

<p>This site serves as a showcase and documentation hub for the V2_SWARM collaborative development system and related projects.</p>

<h3>Purpose</h3>
<p>DaDudeKC.com provides:</p>
<ul>
<li><strong>Project Documentation</strong> - Technical documentation and architecture guides</li>
<li><strong>Development Blog</strong> - Updates on the V2_SWARM system and agent coordination</li>
<li><strong>System Showcase</strong> - Demonstrations of collaborative AI agent systems</li>
<li><strong>Knowledge Base</strong> - Resources for understanding multi-agent coordination</li>
</ul>

<h3>About V2_SWARM</h3>
<p>V2_SWARM is a collaborative development system featuring specialized AI agents working together to build and maintain complex software systems. Each agent has specific expertise and responsibilities, coordinated through a unified messaging and task management system.</p>

<div style="background: #f5f5f5; padding: 1.5rem; border-radius: 8px; margin: 2rem 0;">
<h4>Key Features</h4>
<ul>
<li>Multi-agent coordination and communication</li>
<li>Task assignment and contract system</li>
<li>Automated development workflows</li>
<li>Quality assurance and validation processes</li>
</ul>
</div>

<p><strong>Stay tuned for updates and insights into collaborative AI development!</strong></p>
"""
        
        return {
            "title": title,
            "content": content,
            "categories": ["About", "Site Information"]
        }
    
    def audit(self) -> Dict[str, Any]:
        """Run full audit."""
        print("🔍 Starting blog posts audit...")
        print(f"📡 Fetching posts from {self.base_url}...")
        
        posts = self.get_all_posts()
        print(f"✅ Found {len(posts)} published posts")
        
        # Find duplicates
        print("\n🔍 Checking for duplicates...")
        duplicates = self.find_duplicates(posts)
        
        # Check initial post
        print("\n🔍 Checking for initial 'About this site' post...")
        initial_post_check = self.check_initial_post(posts)
        
        # Generate report
        report = {
            "total_posts": len(posts),
            "duplicates": duplicates,
            "duplicate_count": len(duplicates),
            "initial_post": initial_post_check,
            "recommendations": []
        }
        
        # Add recommendations
        if duplicates:
            report["recommendations"].append(
                f"Found {len(duplicates)} duplicate(s) - review and remove duplicates"
            )
        
        if not initial_post_check["has_initial_post"]:
            report["recommendations"].append(
                "Missing initial 'About this site' post - create welcome post"
            )
            report["suggested_initial_post"] = self.generate_initial_post_content()
        
        return report


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Audit dadudekc.com blog posts"
    )
    parser.add_argument(
        "--url",
        default="https://dadudekc.com",
        help="Base URL of WordPress site"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for report (JSON)"
    )
    
    args = parser.parse_args()
    
    auditor = BlogPostAuditor(base_url=args.url)
    report = auditor.audit()
    
    # Print summary
    print("\n" + "=" * 70)
    print("BLOG POSTS AUDIT REPORT")
    print("=" * 70)
    print(f"\nTotal Posts: {report['total_posts']}")
    print(f"Duplicates Found: {report['duplicate_count']}")
    print(f"Has Initial Post: {report['initial_post']['has_initial_post']}")
    
    if report['duplicates']:
        print("\n⚠️  DUPLICATES:")
        for dup in report['duplicates'][:10]:  # Show first 10
            if dup['type'] == 'exact_title':
                print(f"  - Title: '{dup['title'][:50]}...' ({dup['count']} posts)")
                for p in dup['posts']:
                    print(f"    • ID {p['id']}: {p['link']}")
            else:
                print(f"  - Similarity: {dup['similarity']:.2%}")
                print(f"    • Post 1: {dup['post1']['title'][:50]}... ({dup['post1']['link']})")
                print(f"    • Post 2: {dup['post2']['title'][:50]}... ({dup['post2']['link']})")
    
    if not report['initial_post']['has_initial_post']:
        print("\n⚠️  MISSING INITIAL POST")
        print("  Suggested title:", report['suggested_initial_post']['title'])
    
    if report['recommendations']:
        print("\n📋 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    # Save report
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to: {args.output}")
    else:
        # Save to default location
        output_file = project_root / "artifacts" / f"dadudekc_blog_audit_{Path(__file__).stem}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to: {output_file}")


if __name__ == "__main__":
    main()


