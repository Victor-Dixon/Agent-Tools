#!/usr/bin/env python3
"""
Test Blog Post Template
=======================

Quick test to verify the blog post template is working correctly.
"""

from strategy_blog_automation import (
    load_blog_template,
    generate_strategy_analysis,
    generate_blog_post_content
)
import sys
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "tools"))


def test_template():
    """Test the blog post template."""
    print("🧪 Testing Blog Post Template\n")

    # Load template
    print("1. Loading template...")
    template = load_blog_template()
    print(f"   ✅ Template loaded ({len(template)} characters)")

    # Find all template variables
    template_vars = set(re.findall(r'\{(\w+)\}', template))
    print(f"   📋 Found {len(template_vars)} template variables")

    # Generate analysis
    print("\n2. Generating strategy analysis...")
    analysis = generate_strategy_analysis()
    print(f"   ✅ Analysis generated for {analysis['strategy_name']}")

    # Generate content
    print("\n3. Generating blog post content...")
    try:
        content = generate_blog_post_content(analysis)
        print(f"   ✅ Content generated ({len(content)} characters)")

        # Check for unfilled variables
        remaining_vars = set(re.findall(r'\{(\w+)\}', content))
        if remaining_vars:
            print(
                f"   ⚠️  Warning: {len(remaining_vars)} variables not filled: {remaining_vars}")
        else:
            print("   ✅ All template variables filled successfully")

        # Check for key sections
        sections = [
            "Strategy Analysis:",
            "Overview",
            "Strategy Configuration",
            "Entry Logic",
            "Exit Strategy",
            "Risk Management",
            "Key Features",
            "Performance Considerations",
            "Want the Complete Analysis?"
        ]

        print("\n4. Checking template sections...")
        for section in sections:
            if section in content:
                print(f"   ✅ Section found: {section}")
            else:
                print(f"   ❌ Section missing: {section}")

        print("\n✅ Template test completed successfully!")
        return True

    except KeyError as e:
        print(f"   ❌ Error: Missing variable {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_template()
    sys.exit(0 if success else 1)

