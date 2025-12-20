#!/usr/bin/env python3
"""
Meta Tag Completeness Checker
Comprehensive checker for meta tag completeness across multiple sites.

Usage:
    python tools/meta_tag_completeness_checker.py <url1> <url2> ...
    python tools/meta_tag_completeness_checker.py --file urls.txt
"""

import sys
import json
import argparse
from typing import Dict, List, Set
from pathlib import Path

# Add tools directory to path for imports
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from seo_meta_tag_extractor import MetaTagExtractor


class MetaTagCompletenessChecker:
    """Check meta tag completeness across multiple sites."""
    
    REQUIRED_PRIMARY_TAGS = {'title', 'description'}
    REQUIRED_OG_TAGS = {'og:title', 'og:description', 'og:image', 'og:url', 'og:type'}
    REQUIRED_TWITTER_TAGS = {'twitter:card', 'twitter:title', 'twitter:description'}
    
    def __init__(self, urls: List[str], timeout: int = 10):
        """
        Initialize checker with URLs.
        
        Args:
            urls: List of URLs to check
            timeout: Request timeout in seconds
        """
        self.urls = urls
        self.timeout = timeout
        self.results = []
        
    def check_site(self, url: str) -> Dict:
        """
        Check meta tag completeness for a single site.
        
        Args:
            url: URL to check
            
        Returns:
            Completeness check result
        """
        extractor = MetaTagExtractor(url, timeout=self.timeout)
        
        if not extractor.fetch_html():
            return {
                'url': url,
                'status': 'error',
                'error': 'Failed to fetch HTML'
            }
        
        all_tags = extractor.extract_all_meta_tags()
        validation = extractor.validate_completeness()
        
        # Detailed completeness check
        primary_tags = all_tags['primary_meta']
        og_tags = all_tags['open_graph']
        twitter_tags = all_tags['twitter_card']
        
        missing_primary = [
            tag for tag in self.REQUIRED_PRIMARY_TAGS 
            if not primary_tags.get(tag.replace(':', '_').replace('-', '_'))
        ]
        
        missing_og = [
            tag for tag in self.REQUIRED_OG_TAGS 
            if not og_tags.get(tag)
        ]
        
        missing_twitter = [
            tag for tag in self.REQUIRED_TWITTER_TAGS 
            if not twitter_tags.get(tag)
        ]
        
        has_schema = len(all_tags['schema_org']) > 0
        
        completeness_score = self._calculate_score(
            missing_primary, missing_og, missing_twitter, has_schema
        )
        
        return {
            'url': url,
            'status': 'success',
            'completeness_score': completeness_score,
            'primary_meta': {
                'complete': len(missing_primary) == 0,
                'missing': missing_primary,
                'present': {k: v is not None for k, v in primary_tags.items()}
            },
            'open_graph': {
                'complete': len(missing_og) == 0,
                'missing': missing_og,
                'present': {k: v is not None for k, v in og_tags.items()}
            },
            'twitter_card': {
                'complete': len(missing_twitter) == 0,
                'missing': missing_twitter,
                'present': {k: v is not None for k, v in twitter_tags.items()}
            },
            'schema_org': {
                'present': has_schema,
                'count': len(all_tags['schema_org'])
            }
        }
    
    def _calculate_score(self, missing_primary: List, missing_og: List, 
                        missing_twitter: List, has_schema: bool) -> float:
        """
        Calculate completeness score (0-100).
        
        Args:
            missing_primary: List of missing primary tags
            missing_og: List of missing OG tags
            missing_twitter: List of missing Twitter tags
            has_schema: Whether Schema.org is present
            
        Returns:
            Completeness score (0-100)
        """
        score = 0.0
        
        # Primary tags: 30 points
        primary_weight = 30.0 / len(self.REQUIRED_PRIMARY_TAGS)
        score += (len(self.REQUIRED_PRIMARY_TAGS) - len(missing_primary)) * primary_weight
        
        # Open Graph: 30 points
        og_weight = 30.0 / len(self.REQUIRED_OG_TAGS)
        score += (len(self.REQUIRED_OG_TAGS) - len(missing_og)) * og_weight
        
        # Twitter Card: 20 points
        twitter_weight = 20.0 / len(self.REQUIRED_TWITTER_TAGS)
        score += (len(self.REQUIRED_TWITTER_TAGS) - len(missing_twitter)) * twitter_weight
        
        # Schema.org: 20 points
        if has_schema:
            score += 20.0
        
        return round(score, 1)
    
    def check_all_sites(self) -> List[Dict]:
        """Check all sites and return results."""
        results = []
        
        for url in self.urls:
            print(f"🔍 Checking {url}...", file=sys.stderr)
            result = self.check_site(url)
            results.append(result)
            self.results.append(result)
        
        return results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive report."""
        successful_checks = [r for r in self.results if r.get('status') == 'success']
        
        if not successful_checks:
            return {
                'total_sites': len(self.urls),
                'successful_checks': 0,
                'error': 'No successful checks'
            }
        
        avg_score = sum(r['completeness_score'] for r in successful_checks) / len(successful_checks)
        
        # Consistency check
        all_primary_complete = all(r['primary_meta']['complete'] for r in successful_checks)
        all_og_complete = all(r['open_graph']['complete'] for r in successful_checks)
        all_twitter_complete = all(r['twitter_card']['complete'] for r in successful_checks)
        all_have_schema = all(r['schema_org']['present'] for r in successful_checks)
        
        return {
            'total_sites': len(self.urls),
            'successful_checks': len(successful_checks),
            'average_completeness_score': round(avg_score, 1),
            'consistency': {
                'all_primary_complete': all_primary_complete,
                'all_og_complete': all_og_complete,
                'all_twitter_complete': all_twitter_complete,
                'all_have_schema': all_have_schema
            },
            'site_results': self.results
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Check meta tag completeness')
    parser.add_argument('urls', nargs='*', help='URLs to check')
    parser.add_argument('--file', help='File containing URLs (one per line)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    urls = args.urls
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                urls.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"❌ File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    
    if not urls:
        print("❌ No URLs provided", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    checker = MetaTagCompletenessChecker(urls, timeout=args.timeout)
    checker.check_all_sites()
    report = checker.generate_report()
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n📊 Meta Tag Completeness Report")
        print(f"=" * 60)
        print(f"Total Sites: {report['total_sites']}")
        print(f"Successful Checks: {report['successful_checks']}")
        print(f"Average Completeness Score: {report['average_completeness_score']}/100")
        
        print(f"\n🔹 Consistency Across Sites:")
        print(f"  Primary Meta Complete: {'✅' if report['consistency']['all_primary_complete'] else '❌'}")
        print(f"  Open Graph Complete: {'✅' if report['consistency']['all_og_complete'] else '❌'}")
        print(f"  Twitter Card Complete: {'✅' if report['consistency']['all_twitter_complete'] else '❌'}")
        print(f"  Schema.org Present: {'✅' if report['consistency']['all_have_schema'] else '❌'}")
        
        print(f"\n🔹 Site-by-Site Results:")
        for result in report['site_results']:
            if result['status'] == 'success':
                print(f"\n  {result['url']}:")
                print(f"    Score: {result['completeness_score']}/100")
                print(f"    Primary Meta: {'✅' if result['primary_meta']['complete'] else '❌'}")
                if result['primary_meta']['missing']:
                    print(f"      Missing: {', '.join(result['primary_meta']['missing'])}")
                print(f"    Open Graph: {'✅' if result['open_graph']['complete'] else '❌'}")
                if result['open_graph']['missing']:
                    print(f"      Missing: {', '.join(result['open_graph']['missing'])}")
                print(f"    Twitter Card: {'✅' if result['twitter_card']['complete'] else '❌'}")
                if result['twitter_card']['missing']:
                    print(f"      Missing: {', '.join(result['twitter_card']['missing'])}")
                print(f"    Schema.org: {'✅' if result['schema_org']['present'] else '❌'} ({result['schema_org']['count']} schema(s))")
            else:
                print(f"\n  {result['url']}: ❌ {result.get('error', 'Unknown error')}")


if __name__ == '__main__':
    main()

