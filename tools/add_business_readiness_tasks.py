#!/usr/bin/env python3
"""
Add Business Readiness Tasks to Website Grade Cards
==================================================

Adds business readiness tasks to website grade cards for websites that need them.

Author: Agent-2
V2 Compliant: <300 lines
"""

import sys
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def add_business_readiness_tasks(website: str, grade_card_path: Path):
    """Add business readiness tasks to grade card."""
    content = grade_card_path.read_text(encoding='utf-8')

    # Business readiness tasks template
    business_tasks = {
        "tradingrobotplug.com": [
            "Implement contact form for plugin inquiries and support requests",
            "Add clear call-to-action buttons (Get Plugin, View Pricing, Contact Support) on key pages",
            "Ensure contact information (email, support channels) is prominently displayed",
            "Create privacy policy and terms of service pages",
            "Enhance about page with plugin information, features, and use cases",
            "Add testimonials or user reviews section",
            "Create pricing/comparison table for plugins",
            "Add FAQ page for common plugin questions",
            "Implement newsletter signup with plugin updates",
            "Integrate social media links and sharing buttons"
        ],
        "weareswarm.online": [
            "Implement contact form for swarm system inquiries",
            "Add clear call-to-action buttons (Learn More, Get Started, Contact) on key pages",
            "Ensure contact information is prominently displayed",
            "Create privacy policy and terms of service pages",
            "Enhance about page with swarm system information and architecture",
            "Add case studies or success stories section",
            "Create documentation access page with clear navigation",
            "Add FAQ page for common swarm system questions",
            "Implement newsletter signup for swarm updates",
            "Integrate social media links and sharing buttons",
            "Add demo request form",
            "Create resource library or documentation hub"
        ],
        "weareswarm.site": [
            "Implement contact form for demo inquiries",
            "Add clear call-to-action buttons (Request Demo, View Gallery, Contact) on key pages",
            "Ensure contact information is prominently displayed",
            "Create privacy policy and terms of service pages",
            "Enhance about page with demo information and capabilities",
            "Add demo gallery with screenshots/videos",
            "Create demo request/booking page",
            "Add FAQ page for common demo questions",
            "Implement newsletter signup for demo updates",
            "Integrate social media links and sharing buttons",
            "Add demo walkthrough scheduling",
            "Create resource library for demo materials"
        ]
    }

    tasks = business_tasks.get(website, [])

    if not tasks:
        print(f"  ⚠️  No business readiness tasks template for {website}")
        return False

    # Find the HIGH Priority Tasks section
    high_priority_pattern = r'(### \*\*HIGH Priority Tasks:\*\*.*?)(?=### \*\*MEDIUM Priority Tasks:\*\*|$)'
    match = re.search(high_priority_pattern, content, re.DOTALL)

    if match:
        high_priority_section = match.group(1)

        # Check if tasks already added
        if "Add business readiness tasks" in high_priority_section and "[x]" in high_priority_section:
            print(f"  ℹ️  Business readiness tasks already added to {website}")
            return True

        # Add tasks
        new_tasks = "\n".join([f"- [ ] {task}" for task in tasks])
        new_section = high_priority_section.rstrip() + "\n" + new_tasks + "\n"

        content = content.replace(high_priority_section, new_section)

        # Update Issues Found section
        issues_pattern = r'(### \*\*5\. Business Readiness\*\*.*?Issues Found:.*?\n)'
        issues_match = re.search(issues_pattern, content, re.DOTALL)

        if issues_match:
            issues_section = issues_match.group(1)
            new_issues = issues_section + "- " + "\n- ".join(tasks[:5]) + "\n"
            content = content.replace(issues_section, new_issues)

        # Update Recommendations section
        rec_pattern = r'(### \*\*5\. Business Readiness\*\*.*?Recommendations:.*?\n)'
        rec_match = re.search(rec_pattern, content, re.DOTALL)

        if rec_match:
            rec_section = rec_match.group(1)
            new_recs = rec_section + "- " + "\n- ".join([task.replace("Implement ", "").replace("Add ", "").replace(
                "Create ", "").replace("Ensure ", "").replace("Enhance ", "") for task in tasks[:5]]) + "\n"
            content = content.replace(rec_section, new_recs)

        # Write updated content
        grade_card_path.write_text(content, encoding='utf-8')
        print(f"  ✅ Added {len(tasks)} business readiness tasks to {website}")
        return True
    else:
        print(
            f"  ⚠️  Could not find HIGH Priority Tasks section in {website} grade card")
        return False


def main():
    """Main execution."""
    websites = [
        "tradingrobotplug.com",
        "weareswarm.online",
        "weareswarm.site"
    ]

    print("📋 Adding business readiness tasks to website grade cards\n")

    for website in websites:
        print(f"Processing: {website}")
        grade_card_path = project_root / "docs" / "website_grade_cards" / \
            f"{website.replace('.', '_')}_grade_card.md"

        if grade_card_path.exists():
            add_business_readiness_tasks(website, grade_card_path)
        else:
            print(f"  ⚠️  Grade card not found: {grade_card_path}")
        print()

    print("✅ Business readiness tasks added to grade cards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
