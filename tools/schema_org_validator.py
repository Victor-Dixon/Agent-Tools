#!/usr/bin/env python3
"""
Schema.org JSON-LD Validator
Validates Schema.org structured data for SEO/UX integration testing.

Usage:
    python tools/schema_org_validator.py <url>
    python tools/schema_org_validator.py <url> --validate-types
"""

import sys
import json
import argparse
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup


class SchemaOrgValidator:
    """Validate Schema.org JSON-LD structured data."""
    
    # Common Schema.org types
    VALID_TYPES = {
        'Organization', 'LocalBusiness', 'WebSite', 'WebPage',
        'Person', 'Article', 'BlogPosting', 'Product', 'Service',
        'BreadcrumbList', 'FAQPage', 'Review', 'Rating'
    }
    
    def __init__(self, url: str, timeout: int = 10):
        """
        Initialize validator with URL.
        
        Args:
            url: URL to validate Schema.org data from
            timeout: Request timeout in seconds
        """
        self.url = url
        self.timeout = timeout
        self.soup = None
        self.schemas = []
        
    def fetch_html(self) -> bool:
        """Fetch HTML content from URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'html.parser')
            return True
        except Exception as e:
            print(f"❌ Error fetching HTML: {e}", file=sys.stderr)
            return False
    
    def extract_json_ld(self) -> List[Dict]:
        """Extract all JSON-LD scripts from HTML."""
        schemas = []
        
        if not self.soup:
            return schemas
        
        json_ld_scripts = self.soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                # Handle both single objects and arrays
                if isinstance(data, list):
                    schemas.extend(data)
                else:
                    schemas.append(data)
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"⚠️  Invalid JSON-LD: {e}", file=sys.stderr)
                continue
        
        self.schemas = schemas
        return schemas
    
    def validate_schema_structure(self, schema: Dict) -> Dict[str, any]:
        """
        Validate basic Schema.org structure.
        
        Args:
            schema: Schema.org JSON-LD object
            
        Returns:
            Validation result dictionary
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check for @context
        if '@context' not in schema:
            result['valid'] = False
            result['errors'].append('Missing @context')
        elif schema['@context'] != 'https://schema.org':
            result['warnings'].append(f"Unexpected @context: {schema['@context']}")
        
        # Check for @type
        if '@type' not in schema:
            result['valid'] = False
            result['errors'].append('Missing @type')
        else:
            schema_type = schema['@type']
            if schema_type not in self.VALID_TYPES:
                result['warnings'].append(f"Unknown schema type: {schema_type}")
        
        return result
    
    def validate_required_properties(self, schema: Dict) -> Dict[str, any]:
        """
        Validate required properties based on schema type.
        
        Args:
            schema: Schema.org JSON-LD object
            
        Returns:
            Validation result dictionary
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        schema_type = schema.get('@type', '')
        
        # Define required properties by type
        required_props = {
            'Organization': ['name'],
            'LocalBusiness': ['name', 'address'],
            'WebSite': ['name', 'url'],
            'WebPage': ['name'],
            'Person': ['name'],
            'Article': ['headline', 'datePublished'],
            'BreadcrumbList': ['itemListElement']
        }
        
        if schema_type in required_props:
            for prop in required_props[schema_type]:
                if prop not in schema:
                    result['valid'] = False
                    result['errors'].append(f"Missing required property: {prop}")
        
        return result
    
    def validate_all_schemas(self) -> List[Dict]:
        """
        Validate all extracted schemas.
        
        Returns:
            List of validation results
        """
        if not self.schemas:
            self.extract_json_ld()
        
        results = []
        
        for i, schema in enumerate(self.schemas):
            validation = {
                'index': i,
                'schema_type': schema.get('@type', 'Unknown'),
                'structure_valid': True,
                'properties_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Validate structure
            structure_result = self.validate_schema_structure(schema)
            validation['structure_valid'] = structure_result['valid']
            validation['errors'].extend(structure_result['errors'])
            validation['warnings'].extend(structure_result['warnings'])
            
            # Validate required properties
            properties_result = self.validate_required_properties(schema)
            validation['properties_valid'] = properties_result['valid']
            validation['errors'].extend(properties_result['errors'])
            validation['warnings'].extend(properties_result['warnings'])
            
            validation['overall_valid'] = (
                validation['structure_valid'] and 
                validation['properties_valid']
            )
            
            results.append(validation)
        
        return results
    
    def check_google_rich_results_compatibility(self) -> Dict[str, any]:
        """
        Check compatibility with Google Rich Results requirements.
        
        Returns:
            Compatibility check results
        """
        results = {
            'compatible': True,
            'issues': []
        }
        
        for schema in self.schemas:
            schema_type = schema.get('@type', '')
            
            # Google Rich Results requirements
            if schema_type == 'LocalBusiness':
                if 'address' not in schema:
                    results['compatible'] = False
                    results['issues'].append('LocalBusiness missing address')
                if 'telephone' not in schema:
                    results['issues'].append('LocalBusiness missing telephone (recommended)')
            
            elif schema_type == 'Article':
                if 'datePublished' not in schema:
                    results['compatible'] = False
                    results['issues'].append('Article missing datePublished')
                if 'author' not in schema:
                    results['issues'].append('Article missing author (recommended)')
        
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Validate Schema.org JSON-LD')
    parser.add_argument('url', help='URL to validate Schema.org data from')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--validate-types', action='store_true', help='Validate schema types')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    validator = SchemaOrgValidator(args.url, timeout=args.timeout)
    
    if not validator.fetch_html():
        sys.exit(1)
    
    schemas = validator.extract_json_ld()
    
    if not schemas:
        print("❌ No Schema.org JSON-LD found", file=sys.stderr)
        sys.exit(1)
    
    validation_results = validator.validate_all_schemas()
    google_compat = validator.check_google_rich_results_compatibility()
    
    if args.json:
        output = {
            'url': args.url,
            'schemas_found': len(schemas),
            'validation_results': validation_results,
            'google_rich_results_compatible': google_compat['compatible'],
            'google_issues': google_compat['issues']
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"📊 Schema.org Validation for {args.url}:")
        print(f"\n🔹 Found {len(schemas)} schema(s)\n")
        
        for result in validation_results:
            status = '✅' if result['overall_valid'] else '❌'
            print(f"{status} Schema {result['index'] + 1}: {result['schema_type']}")
            
            if result['errors']:
                for error in result['errors']:
                    print(f"   ❌ Error: {error}")
            
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"   ⚠️  Warning: {warning}")
        
        print(f"\n🔹 Google Rich Results Compatibility:")
        if google_compat['compatible']:
            print("  ✅ Compatible")
        else:
            print("  ❌ Not compatible")
        
        if google_compat['issues']:
            for issue in google_compat['issues']:
                print(f"   ⚠️  {issue}")


if __name__ == '__main__':
    main()

