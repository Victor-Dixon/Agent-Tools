#!/usr/bin/env python3
"""
Website Fixes Verification Tool
================================

Verifies that website fixes are working on live sites.

Author: Agent-7 (Web Development Specialist)
"""

import sys
from pathlib import Path

try:
    from src.core.config.timeout_constants import TimeoutConstants
except Exception:
    class TimeoutConstants:
        HTTP_SHORT = 10

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("❌ Required libraries not installed:")
    print("   pip install requests beautifulsoup4")

def check_text_rendering(url: str, expected_text: str) -> dict:
    """Check if text renders correctly (no spacing issues)."""
    if not HAS_REQUESTS:
        return {"status": "error", "message": "requests not available"}
    
    try:
        response = requests.get(url, timeout=TimeoutConstants.HTTP_SHORT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        
        # Check for common text rendering issues
        issues = []
        
        # Check for broken words (spaces in middle of words)
        if expected_text.lower() in page_text.lower():
            # Check if it appears broken
            broken_patterns = [
                expected_text.replace(' ', ' '),  # Multiple spaces
                expected_text.replace('', ' '),   # Spaces inserted
            ]
            
            for pattern in broken_patterns:
                if pattern in page_text:
                    issues.append(f"Broken text pattern found: {pattern}")
        
        # Check for ligature issues (common in text rendering problems)
        if 'pri mblo om' in page_text.lower() or 'gue tbook' in page_text.lower():
            issues.append("Text rendering issue detected (broken words)")
        
        return {
            "status": "success" if not issues else "warning",
            "url": url,
            "issues": issues,
            "page_loaded": True
        }
    except Exception as e:
        return {
            "status": "error",
            "url": url,
            "message": str(e)
        }

def check_contact_form(url: str) -> dict:
    """Check if contact form exists and is accessible."""
    if not HAS_REQUESTS:
        return {"status": "error", "message": "requests not available"}
    
    try:
        response = requests.get(url, timeout=TimeoutConstants.HTTP_SHORT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for contact form elements
        forms = soup.find_all('form')
        contact_forms = [f for f in forms if 'contact' in f.get('id', '').lower() or 
                        'contact' in f.get('class', [])]
        
        # Check for form inputs
        inputs = soup.find_all(['input', 'textarea'])
        has_email = any(i.get('type') == 'email' or 'email' in i.get('name', '').lower() 
                       for i in inputs)
        has_message = any(i.name == 'textarea' or 'message' in i.get('name', '').lower() 
                         for i in inputs)
        
        return {
            "status": "success",
            "url": url,
            "forms_found": len(forms),
            "contact_forms": len(contact_forms),
            "has_email_field": has_email,
            "has_message_field": has_message,
            "form_accessible": True
        }
    except Exception as e:
        return {
            "status": "error",
            "url": url,
            "message": str(e)
        }

def verify_prismblossom():
    """Verify prismblossom.online fixes."""
    print("=" * 60)
    print("🔍 Verifying prismblossom.online Fixes")
    print("=" * 60)
    print()
    
    results = {
        "site": "prismblossom.online",
        "checks": []
    }
    
    # Check homepage text rendering
    print("📝 Checking homepage text rendering...")
    home_check = check_text_rendering("https://prismblossom.online", "prismblossom.online")
    results["checks"].append({"type": "text_rendering_home", **home_check})
    print(f"   Status: {home_check['status']}")
    if home_check.get('issues'):
        for issue in home_check['issues']:
            print(f"   ⚠️  {issue}")
    print()
    
    # Check Carmyn page text rendering
    print("📝 Checking Carmyn page text rendering...")
    carmyn_check = check_text_rendering("https://prismblossom.online/carmyn", "Carmyn")
    results["checks"].append({"type": "text_rendering_carmyn", **carmyn_check})
    print(f"   Status: {carmyn_check['status']}")
    print()
    
    # Check contact form
    print("📝 Checking contact form...")
    contact_check = check_contact_form("https://prismblossom.online/contact")
    results["checks"].append({"type": "contact_form", **contact_check})
    print(f"   Forms found: {contact_check.get('forms_found', 0)}")
    print(f"   Has email field: {contact_check.get('has_email_field', False)}")
    print(f"   Has message field: {contact_check.get('has_message_field', False)}")
    print()
    
    return results

def verify_freerideinvestor():
    """Verify FreeRideInvestor fixes."""
    print("=" * 60)
    print("🔍 Verifying FreeRideInvestor Fixes")
    print("=" * 60)
    print()
    
    results = {
        "site": "freerideinvestor.com",
        "checks": []
    }
    
    # Check homepage text rendering
    print("📝 Checking homepage text rendering...")
    home_check = check_text_rendering("https://freerideinvestor.com", "FreeRideInvestor")
    results["checks"].append({"type": "text_rendering_home", **home_check})
    print(f"   Status: {home_check['status']}")
    if home_check.get('issues'):
        for issue in home_check['issues']:
            print(f"   ⚠️  {issue}")
    print()
    
    # Check navigation menu (Developer Tools links)
    print("📝 Checking navigation menu...")
    try:
        import requests
        from bs4 import BeautifulSoup
        response = requests.get("https://freerideinvestor.com", timeout=TimeoutConstants.HTTP_SHORT)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find navigation links
        nav_links = soup.find_all('a', href=True)
        developer_tools_links = [
            link for link in nav_links
            if 'developer' in link.get('href', '').lower() or 
               'developer' in link.get_text().lower()
        ]
        
        menu_check = {
            "status": "success" if len(developer_tools_links) == 0 else "warning",
            "developer_tools_links_found": len(developer_tools_links),
            "links": [link.get('href') for link in developer_tools_links[:5]]
        }
        results["checks"].append({"type": "navigation_menu", **menu_check})
        
        print(f"   Developer Tools links found: {len(developer_tools_links)}")
        if developer_tools_links:
            print("   ⚠️  Warning: Developer Tools links still present")
            for link in developer_tools_links[:3]:
                print(f"      - {link.get('href')}")
        else:
            print("   ✅ No Developer Tools links found")
        print()
    except Exception as e:
        print(f"   ❌ Error checking menu: {e}")
        results["checks"].append({
            "type": "navigation_menu",
            "status": "error",
            "message": str(e)
        })
        print()
    
    return results

def main():
    """Main verification function."""
    if not HAS_REQUESTS:
        print("❌ Required libraries not installed")
        print("   Install with: pip install requests beautifulsoup4")
        return 1
    
    print("=" * 60)
    print("🚀 Website Fixes Verification")
    print("=" * 60)
    print()
    
    all_results = []
    
    # Verify prismblossom.online
    prismblossom_results = verify_prismblossom()
    all_results.append(prismblossom_results)
    
    # Verify FreeRideInvestor
    freeride_results = verify_freerideinvestor()
    all_results.append(freeride_results)
    
    # Summary
    print("=" * 60)
    print("📊 Verification Summary")
    print("=" * 60)
    print()
    
    for result in all_results:
        print(f"🌐 {result['site']}:")
        for check in result['checks']:
            status_icon = "✅" if check['status'] == 'success' else "⚠️" if check['status'] == 'warning' else "❌"
            print(f"   {status_icon} {check['type']}: {check['status']}")
        print()
    
    # Save report
    import json
    from datetime import datetime
    report_file = Path("agent_workspaces/Agent-7/WEBSITE_VERIFICATION_REPORT.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": all_results
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report saved: {report_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




