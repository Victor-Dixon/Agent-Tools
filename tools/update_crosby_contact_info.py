#!/usr/bin/env python3
"""
Update Crosby Ultimate Events Contact Information
=================================================

Updates placeholder phone number and service area in WordPress theme files.

Task: Crosby Ultimate Events site hardening - Cycle 1 HIGH priority
- Replace placeholder phone (123) 456-7890 with real business phone
- Update generic service area with specific cities/region

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <300 lines
"""

import re
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def update_contact_page(
    file_path: Path,
    new_phone: str,
    new_phone_tel: str,
    new_service_area: str
) -> bool:
    """
    Update contact page template with real phone and service area.
    
    Args:
        file_path: Path to page-contact.php
        new_phone: New phone number in format (XXX) XXX-XXXX
        new_phone_tel: Tel link format (e.g., tel:+1XXXXXXXXXX)
        new_service_area: Specific service area text
    
    Returns:
        True if updates successful, False otherwise
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Replace phone number in display
        content = re.sub(
            r'\(123\)\s*456-7890',
            new_phone,
            content
        )
        
        # Replace tel: link
        content = re.sub(
            r'tel:\+1234567890',
            f'tel:{new_phone_tel}',
            content
        )
        
        # Replace service area
        content = re.sub(
            r'Serving the greater metropolitan area',
            new_service_area,
            content
        )
        
        # Write updated content
        file_path.write_text(content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def find_all_phone_instances(directory: Path) -> list:
    """Find all files containing placeholder phone number."""
    instances = []
    pattern = re.compile(r'123.*456.*7890|\(123\)', re.IGNORECASE)
    
    for file_path in directory.rglob('*.php'):
        try:
            content = file_path.read_text(encoding='utf-8')
            if pattern.search(content):
                instances.append(file_path)
        except Exception:
            continue
    
    return instances


def main():
    """Main execution."""
    print("🔧 Update Crosby Ultimate Events Contact Information")
    print()
    
    # Get new values from command line or prompt
    if len(sys.argv) >= 4:
        new_phone = sys.argv[1]
        new_phone_tel = sys.argv[2]
        new_service_area = sys.argv[3]
    else:
        print("Usage: python update_crosby_contact_info.py <phone> <tel_link> <service_area>")
        print()
        print("Example:")
        print('  python update_crosby_contact_info.py "(713) 555-1234" "+17135551234" "Serving Houston, TX and surrounding areas"')
        print()
        print("⚠️  Real phone number and service area required from business owner/Agent-4")
        return 1
    
    # Find contact page
    contact_page = project_root / "temp_repos" / "crosbyultimateevents.com" / "wordpress-theme" / "crosbyultimateevents" / "page-contact.php"
    
    if not contact_page.exists():
        print(f"❌ Contact page not found: {contact_page}")
        return 1
    
    # Find all instances
    theme_dir = contact_page.parent
    all_instances = find_all_phone_instances(theme_dir)
    
    print(f"📋 Found {len(all_instances)} file(s) with placeholder phone:")
    for instance in all_instances:
        print(f"   - {instance.relative_to(project_root)}")
    print()
    
    # Update contact page
    print(f"📝 Updating contact page...")
    if update_contact_page(contact_page, new_phone, new_phone_tel, new_service_area):
        print(f"✅ Contact page updated successfully")
    else:
        print(f"❌ Failed to update contact page")
        return 1
    
    # Update other instances if found
    for instance in all_instances:
        if instance != contact_page:
            print(f"📝 Updating {instance.name}...")
            if update_contact_page(instance, new_phone, new_phone_tel, new_service_area):
                print(f"✅ {instance.name} updated successfully")
            else:
                print(f"⚠️  Failed to update {instance.name}")
    
    print()
    print("✅ Contact information update complete!")
    print()
    print("📋 Next steps:")
    print("   1. Review updated files")
    print("   2. Deploy updated theme files to WordPress")
    print("   3. Clear cache and verify on live site")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

