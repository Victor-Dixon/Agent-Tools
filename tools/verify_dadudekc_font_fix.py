#!/usr/bin/env python3
"""Quick script to verify dadudekc.com font fix."""

import requests
from bs4 import BeautifulSoup

url = "https://dadudekc.com"
print(f"Checking {url} for font rendering fix...")

r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
text = soup.get_text()

# Test words that should now have 's' characters
test_words = {
    'Professional': 'Professional',
    'Services': 'Services',
    'WordPress': 'WordPress',
    'systems': 'systems',
    'Business': 'Business',
    'About Us': 'About Us'
}

print("\nChecking for words with 's' characters:")
print("-" * 50)

all_good = True
for search, display in test_words.items():
    found = search in text
    status = "✓ Found" if found else "✗ Missing"
    print(f"{display:20} {status}")
    if not found:
        all_good = False

# Check for the problematic versions (without 's')
problematic = {
    'Profe ional': 'Professional (missing s)',
    'Service ': 'Services (missing s)',
    'WordPre ': 'WordPress (missing s)',
    'About U': 'About Us (missing s)',
}

print("\nChecking for problematic versions (should NOT be found):")
print("-" * 50)

for search, description in problematic.items():
    found = search in text
    status = "✗ FOUND (BAD)" if found else "✓ Not found (good)"
    print(f"{description:30} {status}")
    if found:
        all_good = False

print("\n" + "=" * 50)
if all_good:
    print("✅ Font fix appears to be working correctly!")
else:
    print("⚠️  Some issues detected - may need cache clear or time for fix to propagate")
print("=" * 50)

