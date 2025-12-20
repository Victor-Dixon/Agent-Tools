#!/usr/bin/env python3
"""
Analyze Blog Post Styling Issues
=================================

Analyzes the published blog post on dadudekc.com for styling and readability issues.

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


def analyze_styling_issues(post_url: str):
    """Analyze styling issues in the published blog post."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        resp = session.get(post_url, timeout=10)
        if resp.status_code != 200:
            print(f"❌ Failed to fetch post: {resp.status_code}")
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find main content area
        content = soup.find('article') or soup.find('main') or soup.find('div', class_=lambda x: x and 'content' in str(x).lower())
        
        if not content:
            content = soup.find('body')
        
        issues = []
        
        # Check for common styling issues
        # 1. Text color contrast
        elements_with_color = content.find_all(style=True)
        for elem in elements_with_color:
            style = elem.get('style', '')
            # Check for white text on light background or dark text on dark background
            if 'color: white' in style or 'color:#fff' in style or 'color:#ffffff' in style:
                bg_color = ''
                if 'background' in style:
                    # Extract background color
                    bg_parts = style.split('background')
                    if len(bg_parts) > 1:
                        bg_part = bg_parts[1].split(';')[0]
                        if 'gradient' in bg_part:
                            bg_color = 'gradient'
                        elif '#' in bg_part:
                            bg_color = bg_part.split('#')[1].split()[0][:6]
                
                if bg_color and bg_color != 'gradient':
                    # Check if background is light
                    if bg_color and len(bg_color) == 6:
                        try:
                            r, g, b = int(bg_color[0:2], 16), int(bg_color[2:4], 16), int(bg_color[4:6], 16)
                            brightness = (r * 299 + g * 587 + b * 114) / 1000
                            if brightness > 200:  # Light background
                                issues.append({
                                    'type': 'contrast',
                                    'severity': 'high',
                                    'element': elem.name,
                                    'text': elem.get_text(strip=True)[:50],
                                    'issue': f'White text on light background (brightness: {brightness:.0f})'
                                })
                        except:
                            pass
        
        # 2. Small font sizes
        for elem in content.find_all(style=True):
            style = elem.get('style', '')
            if 'font-size' in style:
                # Extract font size
                size_part = style.split('font-size')[1].split(';')[0].strip()
                if 'em' in size_part:
                    try:
                        size = float(size_part.replace('em', '').strip())
                        if size < 0.9:  # Less than 14.4px (0.9em * 16px)
                            text = elem.get_text(strip=True)[:50]
                            if text:
                                issues.append({
                                    'type': 'font_size',
                                    'severity': 'medium',
                                    'element': elem.name,
                                    'text': text,
                                    'issue': f'Font size too small: {size_part}'
                                })
                    except:
                        pass
        
        # 3. Low contrast text colors
        for elem in content.find_all(style=True):
            style = elem.get('style', '')
            if 'color:' in style and 'white' not in style.lower():
                # Extract color
                color_part = style.split('color:')[1].split(';')[0].strip()
                if '#' in color_part:
                    color_hex = color_part.split('#')[1].split()[0][:6]
                    if len(color_hex) == 6:
                        try:
                            r, g, b = int(color_hex[0:2], 16), int(color_hex[2:4], 16), int(color_hex[4:6], 16)
                            brightness = (r * 299 + g * 587 + b * 114) / 1000
                            # Check if text is on white/light background
                            if brightness < 100:  # Dark text - should be readable
                                pass  # Dark text is usually fine
                            elif brightness > 200:  # Very light text
                                issues.append({
                                    'type': 'contrast',
                                    'severity': 'high',
                                    'element': elem.name,
                                    'text': elem.get_text(strip=True)[:50],
                                    'issue': f'Light text color may have low contrast: #{color_hex}'
                                })
                        except:
                            pass
        
        # 4. Check for missing closing divs or malformed HTML
        html_str = str(content)
        open_divs = html_str.count('<div')
        close_divs = html_str.count('</div>')
        if open_divs != close_divs:
            issues.append({
                'type': 'html_structure',
                'severity': 'medium',
                'element': 'div',
                'text': '',
                'issue': f'Mismatched div tags: {open_divs} open, {close_divs} closed'
            })
        
        return {
            'url': post_url,
            'issues': issues,
            'total_issues': len(issues)
        }
        
    except Exception as e:
        print(f"❌ Error analyzing post: {e}")
        return None


def main():
    """Main function."""
    post_url = "https://dadudekc.com/introducing-the-swarm-a-new-paradigm-in-collaborative-development/"
    
    print("🔍 Analyzing blog post styling issues...")
    print(f"URL: {post_url}")
    print()
    
    result = analyze_styling_issues(post_url)
    
    if not result:
        print("❌ Could not analyze blog post")
        return 1
    
    print(f"✅ Analysis complete! Found {result['total_issues']} potential issues")
    print()
    
    if result['issues']:
        print("=" * 60)
        print("STYLING ISSUES FOUND")
        print("=" * 60)
        
        for i, issue in enumerate(result['issues'], 1):
            print(f"\n{i}. [{issue['severity'].upper()}] {issue['type']}")
            print(f"   Element: {issue['element']}")
            print(f"   Issue: {issue['issue']}")
            if issue['text']:
                print(f"   Text: {issue['text']}...")
    else:
        print("✅ No obvious styling issues detected!")
        print("   (Note: Manual visual inspection may reveal additional issues)")
    
    # Save report
    output_file = Path("docs/blog/blog_styling_issues_report.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Blog Post Styling Issues Report\n\n")
        f.write(f"**URL**: {result['url']}\n\n")
        f.write(f"**Total Issues Found**: {result['total_issues']}\n\n")
        
        if result['issues']:
            f.write("## Issues\n\n")
            for i, issue in enumerate(result['issues'], 1):
                f.write(f"### Issue {i}: {issue['type']} ({issue['severity']})\n\n")
                f.write(f"- **Element**: `{issue['element']}`\n")
                f.write(f"- **Issue**: {issue['issue']}\n")
                if issue['text']:
                    f.write(f"- **Text**: {issue['text']}\n")
                f.write("\n")
        else:
            f.write("## Status\n\n")
            f.write("✅ No obvious styling issues detected.\n")
            f.write("\nNote: Manual visual inspection may reveal additional issues.\n")
    
    print()
    print(f"✅ Report saved to: {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


