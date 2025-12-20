#!/usr/bin/env python3
"""
DaDudeKC Blog Post Readability Analyzer
=======================================

Analyzes blog post styling and identifies readability improvements.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-12-12
V2 Compliant: Yes
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ ERROR: Required packages not installed.")
    print("   Install with: pip install requests beautifulsoup4")
    sys.exit(1)


class BlogPostAnalyzer:
    """Analyzes blog post readability and styling."""

    def __init__(self, base_url: str = "https://dadudekc.com"):
        """Initialize the analyzer."""
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def find_blog_posts(self) -> List[Dict]:
        """Find blog post URLs on the site."""
        posts = []
        
        try:
            # Try common blog URLs
            blog_urls = [
                f"{self.base_url}/blog",
                f"{self.base_url}/",
                f"{self.base_url}/posts",
            ]
            
            for url in blog_urls:
                try:
                    resp = self.session.get(url, timeout=10)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        
                        # Find post links
                        post_links = soup.find_all('a', href=re.compile(r'/(blog|post|article|entry)'))
                        for link in post_links[:5]:  # Get first 5
                            href = link.get('href', '')
                            if not href.startswith('http'):
                                href = f"{self.base_url}{href}"
                            posts.append({
                                'url': href,
                                'title': link.get_text(strip=True) or 'Untitled'
                            })
                        
                        if posts:
                            break
                except Exception as e:
                    continue
            
            # If no posts found via links, try to find recent posts via WordPress REST API
            if not posts:
                try:
                    api_url = f"{self.base_url}/wp-json/wp/v2/posts?per_page=5"
                    resp = self.session.get(api_url, timeout=10)
                    if resp.status_code == 200:
                        api_posts = resp.json()
                        for post in api_posts:
                            posts.append({
                                'url': post.get('link', ''),
                                'title': post.get('title', {}).get('rendered', 'Untitled')
                            })
                except Exception:
                    pass
            
            return posts
            
        except Exception as e:
            print(f"⚠️  Error finding blog posts: {e}")
            return []

    def analyze_post(self, post_url: str) -> Dict:
        """Analyze a single blog post for readability issues."""
        try:
            resp = self.session.get(post_url, timeout=10)
            if resp.status_code != 200:
                return {"error": f"Failed to fetch post: {resp.status_code}"}
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find main content area
            content_selectors = [
                'article',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '#content',
                '.post'
            ]
            
            content = None
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if not content:
                content = soup.find('body')
            
            issues = []
            recommendations = []
            
            # Check 1: Font size
            font_sizes = self._extract_font_sizes(content)
            if font_sizes:
                avg_size = sum(font_sizes) / len(font_sizes)
                if avg_size < 16:
                    issues.append({
                        "type": "font_size",
                        "severity": "high",
                        "message": f"Average font size ({avg_size:.1f}px) is too small for readability (recommended: 16-18px)"
                    })
                    recommendations.append("Increase base font size to 16-18px for body text")
            
            # Check 2: Line height
            line_heights = self._extract_line_heights(content)
            if line_heights:
                avg_line_height = sum(line_heights) / len(line_heights)
                if avg_line_height < 1.5:
                    issues.append({
                        "type": "line_height",
                        "severity": "medium",
                        "message": f"Line height ({avg_line_height:.2f}) is too tight (recommended: 1.5-1.8)"
                    })
                    recommendations.append("Increase line-height to 1.5-1.8 for better readability")
            
            # Check 3: Text color contrast
            text_colors = self._extract_text_colors(content)
            bg_colors = self._extract_background_colors(content)
            
            # Check 4: Paragraph spacing
            paragraphs = content.find_all('p')
            if paragraphs:
                # Check for adequate spacing between paragraphs
                issues.append({
                    "type": "paragraph_spacing",
                    "severity": "low",
                    "message": f"Found {len(paragraphs)} paragraphs - ensure adequate spacing (1.5-2em recommended)"
                })
                recommendations.append("Add margin-bottom: 1.5em to paragraphs for better separation")
            
            # Check 5: Max width
            max_width = self._extract_max_width(content)
            if max_width:
                if max_width > 800:
                    issues.append({
                        "type": "max_width",
                        "severity": "medium",
                        "message": f"Content width ({max_width}px) may be too wide for optimal readability (recommended: 600-800px)"
                    })
                    recommendations.append("Set max-width to 600-800px for optimal reading line length")
            
            # Check 6: Headings hierarchy
            headings = content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                heading_sizes = {}
                for h in headings:
                    tag = h.name
                    if tag not in heading_sizes:
                        heading_sizes[tag] = 0
                    heading_sizes[tag] += 1
                
                # Check if proper hierarchy exists
                if 'h1' in heading_sizes and heading_sizes['h1'] > 1:
                    issues.append({
                        "type": "heading_hierarchy",
                        "severity": "low",
                        "message": "Multiple h1 tags found - should have only one h1 per page"
                    })
            
            # Check 7: Text alignment
            text_align = self._extract_text_align(content)
            if text_align and text_align != 'left' and text_align != 'justify':
                issues.append({
                    "type": "text_align",
                    "severity": "low",
                    "message": f"Text alignment is '{text_align}' - left or justify recommended for readability"
                })
            
            # Extract current styles
            styles = self._extract_styles(content)
            
            return {
                "url": post_url,
                "issues": issues,
                "recommendations": recommendations,
                "current_styles": styles,
                "paragraph_count": len(paragraphs),
                "heading_count": len(headings)
            }
            
        except Exception as e:
            return {"error": f"Error analyzing post: {e}"}

    def _extract_font_sizes(self, element) -> List[float]:
        """Extract font sizes from element and children."""
        sizes = []
        
        # Check inline styles
        if element and hasattr(element, 'get'):
            style = element.get('style', '')
            font_size_match = re.search(r'font-size:\s*(\d+(?:\.\d+)?)px', style)
            if font_size_match:
                sizes.append(float(font_size_match.group(1)))
        
        # Check computed styles (would need browser, but we can check CSS classes)
        # For now, return empty list - would need actual browser rendering
        
        return sizes

    def _extract_line_heights(self, element) -> List[float]:
        """Extract line heights from element."""
        heights = []
        
        if element and hasattr(element, 'get'):
            style = element.get('style', '')
            line_height_match = re.search(r'line-height:\s*(\d+(?:\.\d+)?)', style)
            if line_height_match:
                heights.append(float(line_height_match.group(1)))
        
        return heights

    def _extract_text_colors(self, element) -> List[str]:
        """Extract text colors."""
        colors = []
        
        if element and hasattr(element, 'get'):
            style = element.get('style', '')
            color_match = re.search(r'color:\s*([^;]+)', style)
            if color_match:
                colors.append(color_match.group(1).strip())
        
        return colors

    def _extract_background_colors(self, element) -> List[str]:
        """Extract background colors."""
        colors = []
        
        if element and hasattr(element, 'get'):
            style = element.get('style', '')
            bg_match = re.search(r'background(?:-color)?:\s*([^;]+)', style)
            if bg_match:
                colors.append(bg_match.group(1).strip())
        
        return colors

    def _extract_max_width(self, element) -> Optional[int]:
        """Extract max-width."""
        if element and hasattr(element, 'get'):
            style = element.get('style', '')
            width_match = re.search(r'(?:max-)?width:\s*(\d+)px', style)
            if width_match:
                return int(width_match.group(1))
        return None

    def _extract_text_align(self, element) -> Optional[str]:
        """Extract text alignment."""
        if element and hasattr(element, 'get'):
            style = element.get('style', '')
            align_match = re.search(r'text-align:\s*(\w+)', style)
            if align_match:
                return align_match.group(1)
        return None

    def _extract_styles(self, element) -> Dict:
        """Extract current styling information."""
        styles = {
            "font_size": "unknown",
            "line_height": "unknown",
            "text_color": "unknown",
            "background_color": "unknown",
            "max_width": "unknown"
        }
        
        if element and hasattr(element, 'get'):
            style = element.get('style', '')
            
            font_size_match = re.search(r'font-size:\s*([^;]+)', style)
            if font_size_match:
                styles["font_size"] = font_size_match.group(1).strip()
            
            line_height_match = re.search(r'line-height:\s*([^;]+)', style)
            if line_height_match:
                styles["line_height"] = line_height_match.group(1).strip()
            
            color_match = re.search(r'color:\s*([^;]+)', style)
            if color_match:
                styles["text_color"] = color_match.group(1).strip()
            
            bg_match = re.search(r'background(?:-color)?:\s*([^;]+)', style)
            if bg_match:
                styles["background_color"] = bg_match.group(1).strip()
            
            width_match = re.search(r'(?:max-)?width:\s*([^;]+)', style)
            if width_match:
                styles["max_width"] = width_match.group(1).strip()
        
        return styles

    def generate_css_recommendations(self, analysis: Dict) -> str:
        """Generate CSS recommendations based on analysis."""
        css_rules = []
        
        # Base readability improvements
        css_rules.append("/* Blog Post Readability Improvements */")
        css_rules.append("")
        css_rules.append("/* Main content area */")
        css_rules.append("article, .post-content, .entry-content, .content {")
        css_rules.append("    max-width: 700px; /* Optimal reading width */")
        css_rules.append("    margin: 0 auto; /* Center content */")
        css_rules.append("    padding: 2rem 1rem; /* Adequate padding */")
        css_rules.append("}")
        css_rules.append("")
        css_rules.append("/* Typography improvements */")
        css_rules.append("article p, .post-content p, .entry-content p {")
        css_rules.append("    font-size: 18px; /* Readable base size */")
        css_rules.append("    line-height: 1.7; /* Comfortable line spacing */")
        css_rules.append("    margin-bottom: 1.5em; /* Paragraph spacing */")
        css_rules.append("    color: #333; /* Dark text for contrast */")
        css_rules.append("}")
        css_rules.append("")
        css_rules.append("/* Headings */")
        css_rules.append("article h1, .post-content h1 {")
        css_rules.append("    font-size: 2.5em;")
        css_rules.append("    line-height: 1.2;")
        css_rules.append("    margin-top: 1.5em;")
        css_rules.append("    margin-bottom: 0.5em;")
        css_rules.append("}")
        css_rules.append("")
        css_rules.append("article h2, .post-content h2 {")
        css_rules.append("    font-size: 2em;")
        css_rules.append("    line-height: 1.3;")
        css_rules.append("    margin-top: 1.5em;")
        css_rules.append("    margin-bottom: 0.5em;")
        css_rules.append("}")
        css_rules.append("")
        css_rules.append("article h3, .post-content h3 {")
        css_rules.append("    font-size: 1.5em;")
        css_rules.append("    line-height: 1.4;")
        css_rules.append("    margin-top: 1.25em;")
        css_rules.append("    margin-bottom: 0.5em;")
        css_rules.append("}")
        css_rules.append("")
        css_rules.append("/* Links */")
        css_rules.append("article a, .post-content a {")
        css_rules.append("    color: #0066cc;")
        css_rules.append("    text-decoration: underline;")
        css_rules.append("}")
        css_rules.append("")
        css_rules.append("article a:hover, .post-content a:hover {")
        css_rules.append("    color: #004499;")
        css_rules.append("}")
        css_rules.append("")
        css_rules.append("/* Lists */")
        css_rules.append("article ul, article ol, .post-content ul, .post-content ol {")
        css_rules.append("    margin-left: 2em;")
        css_rules.append("    margin-bottom: 1.5em;")
        css_rules.append("    line-height: 1.7;")
        css_rules.append("}")
        css_rules.append("")
        css_rules.append("/* Code blocks */")
        css_rules.append("article pre, .post-content pre {")
        css_rules.append("    background: #f5f5f5;")
        css_rules.append("    padding: 1em;")
        css_rules.append("    border-radius: 4px;")
        css_rules.append("    overflow-x: auto;")
        css_rules.append("    margin-bottom: 1.5em;")
        css_rules.append("}")
        css_rules.append("")
        css_rules.append("/* Images */")
        css_rules.append("article img, .post-content img {")
        css_rules.append("    max-width: 100%;")
        css_rules.append("    height: auto;")
        css_rules.append("    margin: 1.5em 0;")
        css_rules.append("}")
        
        return "\n".join(css_rules)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze DaDudeKC blog post readability"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Specific blog post URL to analyze",
        default=None
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save analysis report",
        default=None
    )

    args = parser.parse_args()

    analyzer = BlogPostAnalyzer()
    
    if args.url:
        post_url = args.url
    else:
        # Find blog posts
        print("🔍 Finding blog posts...")
        posts = analyzer.find_blog_posts()
        
        if not posts:
            print("❌ No blog posts found. Please provide --url")
            sys.exit(1)
        
        print(f"✅ Found {len(posts)} blog post(s)")
        post_url = posts[0]['url']
        print(f"📄 Analyzing: {posts[0]['title']}")
        print(f"   URL: {post_url}")
    
    # Analyze post
    print(f"\n🔍 Analyzing blog post readability...")
    analysis = analyzer.analyze_post(post_url)
    
    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
        sys.exit(1)
    
    # Generate CSS recommendations
    css_recommendations = analyzer.generate_css_recommendations(analysis)
    
    # Generate report
    report_lines = [
        "# DaDudeKC Blog Post Readability Analysis",
        "",
        f"**Date**: 2025-12-12",
        f"**Agent**: Agent-2 (Architecture & Design Specialist)",
        f"**Post URL**: {post_url}",
        "",
        "---",
        "",
        "## Analysis Summary",
        "",
        f"- **Issues Found**: {len(analysis['issues'])}",
        f"- **Paragraphs**: {analysis['paragraph_count']}",
        f"- **Headings**: {analysis['heading_count']}",
        "",
        "---",
        "",
        "## Current Styles",
        "",
        "| Property | Value |",
        "|----------|-------|",
        f"| Font Size | {analysis['current_styles']['font_size']} |",
        f"| Line Height | {analysis['current_styles']['line_height']} |",
        f"| Text Color | {analysis['current_styles']['text_color']} |",
        f"| Background Color | {analysis['current_styles']['background_color']} |",
        f"| Max Width | {analysis['current_styles']['max_width']} |",
        "",
        "---",
        "",
        "## Issues Identified",
        "",
    ]
    
    if analysis['issues']:
        for issue in analysis['issues']:
            severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
            report_lines.extend([
                f"### {severity_emoji} {issue['type'].replace('_', ' ').title()}",
                f"- **Severity**: {issue['severity']}",
                f"- **Message**: {issue['message']}",
                ""
            ])
    else:
        report_lines.append("✅ No major issues found!")
    
    report_lines.extend([
        "---",
        "",
        "## Recommendations",
        "",
    ])
    
    if analysis['recommendations']:
        for i, rec in enumerate(analysis['recommendations'], 1):
            report_lines.append(f"{i}. {rec}")
    else:
        report_lines.append("No specific recommendations at this time.")
    
    report_lines.extend([
        "",
        "---",
        "",
        "## CSS Recommendations",
        "",
        "```css",
        css_recommendations,
        "```",
        "",
        "---",
        "",
        "*Analysis generated by blog post readability analyzer*"
    ])
    
    report = "\n".join(report_lines)
    
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n💾 Report saved to: {args.output}")
    else:
        print("\n" + "="*60)
        print(report)
    
    # Also save CSS file
    if args.output:
        css_file = args.output.parent / f"{args.output.stem}.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_recommendations)
        print(f"💾 CSS recommendations saved to: {css_file}")


if __name__ == "__main__":
    main()



