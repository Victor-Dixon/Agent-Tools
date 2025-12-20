#!/usr/bin/env python3
"""
SEO Meta Tag Extractor
Extracts and validates meta tags from HTML pages for SEO/UX integration testing.

Usage:
    python tools/seo_meta_tag_extractor.py <url>
    python tools/seo_meta_tag_extractor.py <url> --json
"""

import sys
import json
import argparse
from typing import Dict, List, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


class MetaTagExtractor:
    """Extract and validate meta tags from HTML pages."""
    
    def __init__(self, url: str, timeout: int = 10):
        """
        Initialize extractor with URL.
        
        Args:
            url: URL to extract meta tags from
            timeout: Request timeout in seconds
        """
        self.url = url
        self.timeout = timeout
        self.html = None
        self.soup = None
        
    def fetch_html(self) -> bool:
        """
        Fetch HTML content from URL.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            return True
        except Exception as e:
            print(f"❌ Error fetching HTML: {e}", file=sys.stderr)
            return False
    
    def extract_primary_meta_tags(self) -> Dict[str, Optional[str]]:
        """Extract primary SEO meta tags."""
        tags = {}
        
        # Title tag
        title_tag = self.soup.find('title')
        tags['title'] = title_tag.string.strip() if title_tag else None
        
        # Meta description
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        tags['description'] = meta_desc.get('content') if meta_desc else None
        
        # Meta keywords
        meta_keywords = self.soup.find('meta', attrs={'name': 'keywords'})
        tags['keywords'] = meta_keywords.get('content') if meta_keywords else None
        
        # Meta author
        meta_author = self.soup.find('meta', attrs={'name': 'author'})
        tags['author'] = meta_author.get('content') if meta_author else None
        
        # Meta robots
        meta_robots = self.soup.find('meta', attrs={'name': 'robots'})
        tags['robots'] = meta_robots.get('content') if meta_robots else None
        
        # Canonical URL
        canonical = self.soup.find('link', attrs={'rel': 'canonical'})
        tags['canonical'] = canonical.get('href') if canonical else None
        
        return tags
    
    def extract_open_graph_tags(self) -> Dict[str, Optional[str]]:
        """Extract Open Graph meta tags."""
        og_tags = {}
        
        og_properties = [
            'og:title', 'og:description', 'og:image', 'og:url',
            'og:type', 'og:site_name', 'og:locale'
        ]
        
        for prop in og_properties:
            meta_tag = self.soup.find('meta', attrs={'property': prop})
            og_tags[prop] = meta_tag.get('content') if meta_tag else None
        
        return og_tags
    
    def extract_twitter_card_tags(self) -> Dict[str, Optional[str]]:
        """Extract Twitter Card meta tags."""
        twitter_tags = {}
        
        twitter_properties = [
            'twitter:card', 'twitter:title', 'twitter:description',
            'twitter:image', 'twitter:site', 'twitter:creator'
        ]
        
        for prop in twitter_properties:
            meta_tag = self.soup.find('meta', attrs={'name': prop})
            twitter_tags[prop] = meta_tag.get('content') if meta_tag else None
        
        return twitter_tags
    
    def extract_schema_org_json_ld(self) -> List[Dict]:
        """Extract Schema.org JSON-LD structured data."""
        schema_data = []
        
        json_ld_scripts = self.soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                schema_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return schema_data
    
    def extract_all_meta_tags(self) -> Dict:
        """Extract all meta tags from the page."""
        if not self.soup:
            return {}
        
        return {
            'url': self.url,
            'primary_meta': self.extract_primary_meta_tags(),
            'open_graph': self.extract_open_graph_tags(),
            'twitter_card': self.extract_twitter_card_tags(),
            'schema_org': self.extract_schema_org_json_ld()
        }
    
    def validate_completeness(self) -> Dict[str, bool]:
        """
        Validate meta tag completeness.
        
        Returns:
            Dictionary with validation results for each tag category
        """
        all_tags = self.extract_all_meta_tags()
        validation = {
            'primary_meta_complete': all(
                all_tags['primary_meta'].get(key) 
                for key in ['title', 'description']
            ),
            'open_graph_complete': all(
                all_tags['open_graph'].get(key)
                for key in ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']
            ),
            'twitter_card_complete': all(
                all_tags['twitter_card'].get(key)
                for key in ['twitter:card', 'twitter:title', 'twitter:description']
            ),
            'schema_org_present': len(all_tags['schema_org']) > 0
        }
        
        return validation


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Extract meta tags from HTML pages')
    parser.add_argument('url', help='URL to extract meta tags from')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--validate', action='store_true', help='Validate completeness')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    extractor = MetaTagExtractor(args.url, timeout=args.timeout)
    
    if not extractor.fetch_html():
        sys.exit(1)
    
    if args.validate:
        validation = extractor.validate_completeness()
        if args.json:
            print(json.dumps(validation, indent=2))
        else:
            print("📊 Meta Tag Completeness Validation:")
            print(f"  Primary Meta: {'✅' if validation['primary_meta_complete'] else '❌'}")
            print(f"  Open Graph: {'✅' if validation['open_graph_complete'] else '❌'}")
            print(f"  Twitter Card: {'✅' if validation['twitter_card_complete'] else '❌'}")
            print(f"  Schema.org: {'✅' if validation['schema_org_present'] else '❌'}")
    else:
        all_tags = extractor.extract_all_meta_tags()
        if args.json:
            print(json.dumps(all_tags, indent=2))
        else:
            print(f"📋 Meta Tags for {args.url}:")
            print(f"\n🔹 Primary Meta Tags:")
            for key, value in all_tags['primary_meta'].items():
                print(f"  {key}: {value or '❌ Missing'}")
            
            print(f"\n🔹 Open Graph Tags:")
            for key, value in all_tags['open_graph'].items():
                print(f"  {key}: {value or '❌ Missing'}")
            
            print(f"\n🔹 Twitter Card Tags:")
            for key, value in all_tags['twitter_card'].items():
                print(f"  {key}: {value or '❌ Missing'}")
            
            print(f"\n🔹 Schema.org JSON-LD:")
            print(f"  Found {len(all_tags['schema_org'])} schema(s)")
            for i, schema in enumerate(all_tags['schema_org'], 1):
                print(f"  Schema {i}: {schema.get('@type', 'Unknown')}")


if __name__ == '__main__':
    main()

