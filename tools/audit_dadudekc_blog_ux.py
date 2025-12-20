#!/usr/bin/env python3
"""
DaDudeKC Blog Template UX Audit
================================

Comprehensive UX audit of blog post template and user experience.
Analyzes actual page structure, template design, and UX best practices.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-13
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


class BlogTemplateUXAuditor:
    """Comprehensive UX audit of blog template."""

    def __init__(self, base_url: str = "https://dadudekc.com"):
        """Initialize the auditor."""
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def audit_blog_post(self, post_url: str) -> Dict:
        """Comprehensive UX audit of blog post."""
        try:
            resp = self.session.get(post_url, timeout=10)
            if resp.status_code != 200:
                return {"error": f"Failed to fetch post: {resp.status_code}"}
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            audit_results = {
                "url": post_url,
                "ux_issues": [],
                "template_issues": [],
                "accessibility_issues": [],
                "performance_issues": [],
                "recommendations": [],
                "template_structure": {},
                "content_structure": {}
            }
            
            # 1. Template Structure Analysis
            audit_results["template_structure"] = self._analyze_template_structure(soup)
            
            # 2. Content Structure Analysis
            audit_results["content_structure"] = self._analyze_content_structure(soup)
            
            # 3. Typography & Readability
            typography_issues = self._audit_typography(soup)
            audit_results["ux_issues"].extend(typography_issues)
            
            # 4. Layout & Spacing
            layout_issues = self._audit_layout(soup)
            audit_results["ux_issues"].extend(layout_issues)
            
            # 5. Color & Contrast
            contrast_issues = self._audit_contrast(soup)
            audit_results["accessibility_issues"].extend(contrast_issues)
            
            # 6. Navigation & Wayfinding
            nav_issues = self._audit_navigation(soup)
            audit_results["ux_issues"].extend(nav_issues)
            
            # 7. Mobile Responsiveness (check viewport meta)
            mobile_issues = self._audit_mobile(soup)
            audit_results["ux_issues"].extend(mobile_issues)
            
            # 8. Content Hierarchy
            hierarchy_issues = self._audit_hierarchy(soup)
            audit_results["template_issues"].extend(hierarchy_issues)
            
            # 9. Interactive Elements
            interactive_issues = self._audit_interactive_elements(soup)
            audit_results["ux_issues"].extend(interactive_issues)
            
            # 10. Generate Recommendations
            audit_results["recommendations"] = self._generate_recommendations(audit_results)
            
            return audit_results
            
        except Exception as e:
            return {"error": f"Error auditing post: {e}"}

    def _analyze_template_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze blog template structure."""
        structure = {
            "has_header": bool(soup.find('header') or soup.find('.header') or soup.find('#header')),
            "has_footer": bool(soup.find('footer') or soup.find('.footer') or soup.find('#footer')),
            "has_sidebar": bool(soup.find('aside') or soup.find('.sidebar') or soup.find('#sidebar')),
            "has_main_content": bool(soup.find('main') or soup.find('article') or soup.find('.content')),
            "has_breadcrumbs": bool(soup.find('.breadcrumb') or soup.find('nav', {'aria-label': 'breadcrumb'})),
            "has_author_info": bool(soup.find('.author') or soup.find('.post-author')),
            "has_related_posts": bool(soup.find('.related-posts') or soup.find('.related')),
            "has_social_sharing": bool(soup.find('.share') or soup.find('.social-share')),
            "template_classes": [],
            "css_files": []
        }
        
        # Find template classes
        body = soup.find('body')
        if body:
            body_classes = body.get('class', [])
            structure["template_classes"] = body_classes
        
        # Find CSS files
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href:
                structure["css_files"].append(href)
        
        return structure

    def _analyze_content_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze content structure."""
        content = soup.find('article') or soup.find('.post-content') or soup.find('.entry-content') or soup.find('main')
        
        if not content:
            content = soup.find('body')
        
        structure = {
            "paragraphs": len(content.find_all('p')) if content else 0,
            "headings": {
                "h1": len(content.find_all('h1')) if content else 0,
                "h2": len(content.find_all('h2')) if content else 0,
                "h3": len(content.find_all('h3')) if content else 0,
                "h4": len(content.find_all('h4')) if content else 0,
            },
            "lists": len(content.find_all(['ul', 'ol'])) if content else 0,
            "images": len(content.find_all('img')) if content else 0,
            "links": len(content.find_all('a')) if content else 0,
            "code_blocks": len(content.find_all(['pre', 'code'])) if content else 0,
            "has_table_of_contents": bool(content.find('.toc') or content.find('#toc') if content else False),
        }
        
        return structure

    def _audit_typography(self, soup: BeautifulSoup) -> List[Dict]:
        """Audit typography and readability."""
        issues = []
        
        # Check for inline styles that might override template
        body = soup.find('body')
        if body:
            inline_style = body.get('style', '')
            if 'font-size' in inline_style:
                issues.append({
                    "type": "typography",
                    "severity": "high",
                    "message": "Inline font-size styles detected - may override template defaults",
                    "element": "body"
                })
        
        # Check for very small font sizes in inline styles
        for element in soup.find_all(True, style=True):
            style = element.get('style', '')
            font_size_match = re.search(r'font-size:\s*(\d+(?:\.\d+)?)px', style)
            if font_size_match:
                size = float(font_size_match.group(1))
                if size < 14:
                    issues.append({
                        "type": "typography",
                        "severity": "high",
                        "message": f"Very small font size detected: {size}px (recommended: 16-18px minimum)",
                        "element": element.name
                    })
        
        # Check line-height
        for element in soup.find_all(True, style=True):
            style = element.get('style', '')
            line_height_match = re.search(r'line-height:\s*(\d+(?:\.\d+)?)', style)
            if line_height_match:
                lh = float(line_height_match.group(1))
                if lh < 1.4:
                    issues.append({
                        "type": "typography",
                        "severity": "medium",
                        "message": f"Tight line-height detected: {lh} (recommended: 1.5-1.8)",
                        "element": element.name
                    })
        
        return issues

    def _audit_layout(self, soup: BeautifulSoup) -> List[Dict]:
        """Audit layout and spacing."""
        issues = []
        
        # Check for content width constraints
        article = soup.find('article') or soup.find('.post-content') or soup.find('.entry-content')
        if article:
            style = article.get('style', '')
            max_width_match = re.search(r'max-width:\s*(\d+)px', style)
            if max_width_match:
                width = int(max_width_match.group(1))
                if width > 900:
                    issues.append({
                        "type": "layout",
                        "severity": "medium",
                        "message": f"Content width may be too wide: {width}px (recommended: 600-800px for readability)",
                        "element": "article"
                    })
            elif not max_width_match:
                issues.append({
                    "type": "layout",
                    "severity": "low",
                    "message": "No max-width constraint detected - content may be too wide on large screens",
                    "element": "article"
                })
        
        # Check for adequate padding
        if article:
            style = article.get('style', '')
            padding_match = re.search(r'padding:\s*([^;]+)', style)
            if not padding_match:
                issues.append({
                    "type": "layout",
                    "severity": "low",
                    "message": "No padding detected on content area - may feel cramped",
                    "element": "article"
                })
        
        return issues

    def _audit_contrast(self, soup: BeautifulSoup) -> List[Dict]:
        """Audit color contrast and accessibility."""
        issues = []
        
        # Check for low contrast color combinations
        for element in soup.find_all(True, style=True):
            style = element.get('style', '')
            color_match = re.search(r'color:\s*([^;]+)', style)
            bg_match = re.search(r'background(?:-color)?:\s*([^;]+)', style)
            
            if color_match and bg_match:
                # Basic check - light text on light background or dark on dark
                color = color_match.group(1).strip().lower()
                bg = bg_match.group(1).strip().lower()
                
                light_colors = ['white', '#fff', '#ffffff', 'rgb(255', 'rgba(255']
                dark_colors = ['black', '#000', '#000000', 'rgb(0', 'rgba(0']
                
                if any(c in color for c in light_colors) and any(c in bg for c in light_colors):
                    issues.append({
                        "type": "contrast",
                        "severity": "high",
                        "message": "Potential contrast issue: Light text on light background detected",
                        "element": element.name
                    })
                elif any(c in color for c in dark_colors) and any(c in bg for c in dark_colors):
                    issues.append({
                        "type": "contrast",
                        "severity": "high",
                        "message": "Potential contrast issue: Dark text on dark background detected",
                        "element": element.name
                    })
        
        return issues

    def _audit_navigation(self, soup: BeautifulSoup) -> List[Dict]:
        """Audit navigation and wayfinding."""
        issues = []
        
        # Check for breadcrumbs
        has_breadcrumbs = bool(soup.find('.breadcrumb') or soup.find('nav', {'aria-label': 'breadcrumb'}))
        if not has_breadcrumbs:
            issues.append({
                "type": "navigation",
                "severity": "low",
                "message": "No breadcrumbs detected - users may have difficulty understanding location in site hierarchy"
            })
        
        # Check for back to blog link
        has_back_link = bool(soup.find('a', href=re.compile(r'/blog')) or soup.find('a', string=re.compile(r'back|return', re.I)))
        if not has_back_link:
            issues.append({
                "type": "navigation",
                "severity": "low",
                "message": "No clear 'back to blog' navigation link detected"
            })
        
        # Check for table of contents for long posts
        content = soup.find('article') or soup.find('.post-content')
        if content:
            paragraphs = content.find_all('p')
            headings = content.find_all(['h1', 'h2', 'h3'])
            if len(paragraphs) > 20 or len(headings) > 5:
                has_toc = bool(content.find('.toc') or content.find('#toc'))
                if not has_toc:
                    issues.append({
                        "type": "navigation",
                        "severity": "low",
                        "message": "Long post detected but no table of contents - consider adding TOC for better navigation"
                    })
        
        return issues

    def _audit_mobile(self, soup: BeautifulSoup) -> List[Dict]:
        """Audit mobile responsiveness."""
        issues = []
        
        # Check for viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            issues.append({
                "type": "mobile",
                "severity": "high",
                "message": "No viewport meta tag detected - site may not be mobile-responsive"
            })
        else:
            content = viewport.get('content', '')
            if 'width=device-width' not in content:
                issues.append({
                    "type": "mobile",
                    "severity": "medium",
                    "message": "Viewport meta tag may not be properly configured for mobile"
                })
        
        return issues

    def _audit_hierarchy(self, soup: BeautifulSoup) -> List[Dict]:
        """Audit content hierarchy."""
        issues = []
        
        content = soup.find('article') or soup.find('.post-content') or soup.find('.entry-content')
        if content:
            h1_count = len(content.find_all('h1'))
            if h1_count > 1:
                issues.append({
                    "type": "hierarchy",
                    "severity": "medium",
                    "message": f"Multiple h1 tags found ({h1_count}) - should have only one h1 per page for SEO and accessibility"
                })
            
            # Check heading order
            headings = content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            prev_level = 0
            for heading in headings:
                level = int(heading.name[1])
                if prev_level > 0 and level > prev_level + 1:
                    issues.append({
                        "type": "hierarchy",
                        "severity": "low",
                        "message": f"Heading hierarchy skip detected: {heading.name} after h{prev_level} - should maintain sequential order"
                    })
                prev_level = level
        
        return issues

    def _audit_interactive_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """Audit interactive elements."""
        issues = []
        
        # Check for links without clear indication
        links = soup.find_all('a')
        for link in links:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            
            # Check for empty or unclear link text
            if not text or len(text) < 2:
                if 'aria-label' not in link.attrs and 'title' not in link.attrs:
                    issues.append({
                        "type": "interactive",
                        "severity": "medium",
                        "message": "Link with unclear or empty text detected - add aria-label or descriptive text"
                    })
            
            # Check for external links without indication
            if href.startswith('http') and 'dadudekc.com' not in href:
                if 'external' not in link.get('class', []) and 'target="_blank"' not in str(link):
                    issues.append({
                        "type": "interactive",
                        "severity": "low",
                        "message": "External link without clear indication - consider adding icon or target='_blank'"
                    })
        
        return issues

    def _generate_recommendations(self, audit_results: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Template structure recommendations
        structure = audit_results.get("template_structure", {})
        if not structure.get("has_main_content"):
            recommendations.append("Ensure main content area is properly marked with <main> or <article> tag")
        
        if not structure.get("has_breadcrumbs"):
            recommendations.append("Add breadcrumb navigation for better wayfinding")
        
        # Typography recommendations
        typography_issues = [i for i in audit_results.get("ux_issues", []) if i.get("type") == "typography"]
        if typography_issues:
            recommendations.append("Implement consistent typography system: 16-18px base font, 1.5-1.8 line-height")
        
        # Layout recommendations
        layout_issues = [i for i in audit_results.get("ux_issues", []) if i.get("type") == "layout"]
        if layout_issues:
            recommendations.append("Set max-width: 700px on content area for optimal reading line length")
            recommendations.append("Add adequate padding (2rem) to content area")
        
        # Contrast recommendations
        contrast_issues = audit_results.get("accessibility_issues", [])
        if contrast_issues:
            recommendations.append("Audit color contrast ratios - ensure WCAG AA compliance (4.5:1 for text)")
        
        # Mobile recommendations
        mobile_issues = [i for i in audit_results.get("ux_issues", []) if i.get("type") == "mobile"]
        if mobile_issues:
            recommendations.append("Ensure viewport meta tag is properly configured: <meta name='viewport' content='width=device-width, initial-scale=1'>")
        
        # Content structure recommendations
        content = audit_results.get("content_structure", {})
        if content.get("paragraphs", 0) > 20:
            recommendations.append("Consider adding table of contents for long posts")
        
        if not structure.get("has_author_info"):
            recommendations.append("Add author information section for credibility and engagement")
        
        if not structure.get("has_related_posts"):
            recommendations.append("Add related posts section to increase engagement and reduce bounce rate")
        
        if not structure.get("has_social_sharing"):
            recommendations.append("Add social sharing buttons to increase content distribution")
        
        return recommendations


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive UX audit of DaDudeKC blog template"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Specific blog post URL to audit",
        default="https://dadudekc.com/introducing-the-swarm-a-new-paradigm-in-collaborative-development/"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save audit report",
        default=Path("artifacts/2025-12-13_agent-5_dadudekc-blog-ux-audit.md")
    )

    args = parser.parse_args()

    auditor = BlogTemplateUXAuditor()
    
    print(f"🔍 Conducting comprehensive UX audit...")
    print(f"📄 URL: {args.url}")
    
    audit_results = auditor.audit_blog_post(args.url)
    
    if "error" in audit_results:
        print(f"❌ Error: {audit_results['error']}")
        sys.exit(1)
    
    # Generate report
    report_lines = [
        "# DaDudeKC Blog Template UX Audit",
        "",
        f"**Date**: 2025-12-13",
        f"**Agent**: Agent-5 (Business Intelligence Specialist)",
        f"**Post URL**: {args.url}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **UX Issues**: {len(audit_results['ux_issues'])}",
        f"- **Template Issues**: {len(audit_results['template_issues'])}",
        f"- **Accessibility Issues**: {len(audit_results['accessibility_issues'])}",
        f"- **Performance Issues**: {len(audit_results['performance_issues'])}",
        f"- **Total Recommendations**: {len(audit_results['recommendations'])}",
        "",
        "---",
        "",
        "## Template Structure Analysis",
        "",
        "| Feature | Status |",
        "|---------|--------|",
        f"| Header | {'✅' if audit_results['template_structure']['has_header'] else '❌'} |",
        f"| Footer | {'✅' if audit_results['template_structure']['has_footer'] else '❌'} |",
        f"| Sidebar | {'✅' if audit_results['template_structure']['has_sidebar'] else '❌'} |",
        f"| Main Content | {'✅' if audit_results['template_structure']['has_main_content'] else '❌'} |",
        f"| Breadcrumbs | {'✅' if audit_results['template_structure']['has_breadcrumbs'] else '❌'} |",
        f"| Author Info | {'✅' if audit_results['template_structure']['has_author_info'] else '❌'} |",
        f"| Related Posts | {'✅' if audit_results['template_structure']['has_related_posts'] else '❌'} |",
        f"| Social Sharing | {'✅' if audit_results['template_structure']['has_social_sharing'] else '❌'} |",
        "",
        "---",
        "",
        "## Content Structure",
        "",
        f"- **Paragraphs**: {audit_results['content_structure']['paragraphs']}",
        f"- **Headings**: {audit_results['content_structure']['headings']['h1']} h1, {audit_results['content_structure']['headings']['h2']} h2, {audit_results['content_structure']['headings']['h3']} h3",
        f"- **Lists**: {audit_results['content_structure']['lists']}",
        f"- **Images**: {audit_results['content_structure']['images']}",
        f"- **Links**: {audit_results['content_structure']['links']}",
        f"- **Code Blocks**: {audit_results['content_structure']['code_blocks']}",
        "",
        "---",
        "",
        "## UX Issues",
        "",
    ]
    
    if audit_results['ux_issues']:
        for issue in audit_results['ux_issues']:
            severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
            report_lines.extend([
                f"### {severity_emoji} {issue['type'].replace('_', ' ').title()}",
                f"- **Severity**: {issue['severity']}",
                f"- **Message**: {issue['message']}",
                f"- **Element**: {issue.get('element', 'N/A')}",
                ""
            ])
    else:
        report_lines.append("✅ No UX issues found!")
    
    if audit_results['template_issues']:
        report_lines.extend([
            "",
            "## Template Issues",
            ""
        ])
        for issue in audit_results['template_issues']:
            severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
            report_lines.extend([
                f"### {severity_emoji} {issue['type'].replace('_', ' ').title()}",
                f"- **Severity**: {issue['severity']}",
                f"- **Message**: {issue['message']}",
                ""
            ])
    
    if audit_results['accessibility_issues']:
        report_lines.extend([
            "",
            "## Accessibility Issues",
            ""
        ])
        for issue in audit_results['accessibility_issues']:
            severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
            report_lines.extend([
                f"### {severity_emoji} {issue['type'].replace('_', ' ').title()}",
                f"- **Severity**: {issue['severity']}",
                f"- **Message**: {issue['message']}",
                ""
            ])
    
    report_lines.extend([
        "",
        "---",
        "",
        "## Recommendations",
        "",
    ])
    
    for i, rec in enumerate(audit_results['recommendations'], 1):
        report_lines.append(f"{i}. {rec}")
    
    report_lines.extend([
        "",
        "---",
        "",
        "*Audit generated by blog template UX auditor*"
    ])
    
    report = "\n".join(report_lines)
    
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 Audit report saved to: {args.output}")
    
    # Print summary
    print("\n" + "="*60)
    print("AUDIT SUMMARY")
    print("="*60)
    print(f"UX Issues: {len(audit_results['ux_issues'])}")
    print(f"Template Issues: {len(audit_results['template_issues'])}")
    print(f"Accessibility Issues: {len(audit_results['accessibility_issues'])}")
    print(f"Recommendations: {len(audit_results['recommendations'])}")
    print("="*60)


if __name__ == "__main__":
    main()




