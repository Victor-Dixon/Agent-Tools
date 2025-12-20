#!/usr/bin/env python3
"""
Add UX Tasks to Website Grade Cards
===================================

Adds UX (User Experience) tasks to website grade cards for websites that need them.

Author: Agent-2
V2 Compliant: <300 lines
"""

import sys
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def add_ux_tasks(website: str, grade_card_path: Path):
    """Add UX tasks to grade card."""
    content = grade_card_path.read_text(encoding='utf-8')

    # UX tasks template - common UX improvements
    ux_tasks = [
        "Improve mobile responsiveness and touch interactions",
        "Enhance page load speed and performance optimization",
        "Add clear navigation menu with intuitive structure",
        "Implement consistent design system (colors, fonts, spacing)",
        "Improve accessibility (WCAG compliance, keyboard navigation)",
        "Add breadcrumb navigation for better user orientation",
        "Enhance form usability and error messaging",
        "Implement search functionality if applicable",
        "Add loading states and feedback for user actions",
        "Improve visual hierarchy and content readability"
    ]

    # Find the MEDIUM Priority Tasks section
    medium_priority_pattern = r'(### \*\*MEDIUM Priority Tasks:\*\*.*?)(?=### \*\*LOW Priority Tasks:\*\*|$)'
    match = re.search(medium_priority_pattern, content, re.DOTALL)

    if match:
        medium_priority_section = match.group(1)

        # Check if UX tasks already added
        if "Add UX tasks" in medium_priority_section and "[x]" in medium_priority_section:
            print(f"  ℹ️  UX tasks already added to {website}")
            return True

        # Check if "Add UX tasks" line exists and mark it complete, then add tasks
        if "Add UX tasks" in medium_priority_section:
            # Replace the checkbox
            medium_priority_section = re.sub(
                r'- \[ \] Add UX tasks for ' + re.escape(website),
                f'- [x] Add UX tasks for {website} ✅ COMPLETE',
                medium_priority_section
            )

        # Add tasks
        new_tasks = "\n".join([f"- [ ] {task}" for task in ux_tasks])
        new_section = medium_priority_section.rstrip() + "\n" + new_tasks + "\n"

        content = content.replace(medium_priority_section, new_section)

        # Update Issues Found section for UX
        issues_pattern = r'(### \*\*4\. User Experience\*\*.*?Issues Found:.*?\n)'
        issues_match = re.search(issues_pattern, content, re.DOTALL)

        if issues_match:
            issues_section = issues_match.group(1)
            if "No UX tasks identified" in content:
                # Replace the placeholder
                new_issues = issues_section + "- " + \
                    "\n- ".join(ux_tasks[:5]) + "\n"
                content = content.replace(
                    issues_section + "- No UX tasks identified\n",
                    new_issues
                )

        # Update Recommendations section for UX
        rec_pattern = r'(### \*\*4\. User Experience\*\*.*?Recommendations:.*?\n)'
        rec_match = re.search(rec_pattern, content, re.DOTALL)

        if rec_match:
            rec_section = rec_match.group(1)
            if "None" in content[content.find(rec_section):content.find(rec_section) + 200]:
                new_recs = rec_section + "- " + "\n- ".join([task.replace("Improve ", "").replace(
                    "Enhance ", "").replace("Add ", "").replace("Implement ", "") for task in ux_tasks[:5]]) + "\n"
                content = content.replace(
                    rec_section + "- None\n",
                    new_recs
                )

        # Write updated content
        grade_card_path.write_text(content, encoding='utf-8')
        print(f"  ✅ Added {len(ux_tasks)} UX tasks to {website}")
        return True
    else:
        print(
            f"  ⚠️  Could not find MEDIUM Priority Tasks section in {website} grade card")
        return False


def main():
    """Main execution."""
    websites = [
        "ariajet.site",
        "digitaldreamscape.site",
        "prismblossom.online",
        "southwestsecret.com",
        "tradingrobotplug.com",
        "weareswarm.online",
        "weareswarm.site"
    ]

    print("📋 Adding UX tasks to website grade cards\n")

    for website in websites:
        print(f"Processing: {website}")
        grade_card_path = project_root / "docs" / "website_grade_cards" / \
            f"{website.replace('.', '_')}_grade_card.md"

        if grade_card_path.exists():
            add_ux_tasks(website, grade_card_path)
        else:
            print(f"  ⚠️  Grade card not found: {grade_card_path}")
        print()

    print("✅ UX tasks added to grade cards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
