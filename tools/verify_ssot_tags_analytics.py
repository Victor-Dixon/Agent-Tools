#!/usr/bin/env python3
"""
SSOT Tagging Verification Tool
==============================

Verifies SSOT tags in analytics domain files for pre-public audit.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-13
V2 Compliant: Yes
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

def verify_ssot_tag(file_path: Path) -> Tuple[bool, str, str]:
    """
    Verify SSOT tag in a file.
    
    Returns:
        (has_tag, tag_domain, status_message)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Look for SSOT tag in various formats
        ssot_patterns = [
            r'<!--\s*SSOT\s+Domain:\s*(\w+)\s*-->',
            r'#\s*SSOT\s+Domain:\s*(\w+)',
            r'SSOT\s+Domain:\s*(\w+)',
        ]
        
        tag_domain = None
        for pattern in ssot_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                tag_domain = match.group(1).lower()
                break
        
        if tag_domain:
            # Verify domain matches expected
            expected_domain = "analytics"
            if "analytics" in str(file_path).lower():
                if tag_domain == expected_domain:
                    return (True, tag_domain, "✅ Correct SSOT tag")
                else:
                    return (True, tag_domain, f"⚠️ Incorrect domain: {tag_domain} (expected: {expected_domain})")
            else:
                return (True, tag_domain, f"✅ SSOT tag present: {tag_domain}")
        else:
            return (False, None, "❌ No SSOT tag found")
            
    except Exception as e:
        return (False, None, f"❌ Error reading file: {e}")


def scan_analytics_domain() -> List[Dict]:
    """Scan analytics domain files for SSOT tags."""
    analytics_dir = Path("src/core/analytics")
    
    if not analytics_dir.exists():
        return []
    
    results = []
    
    # Find all Python files
    for py_file in analytics_dir.rglob("*.py"):
        # Skip __init__.py files (usually don't need SSOT tags)
        if py_file.name == "__init__.py":
            continue
            
        has_tag, domain, status = verify_ssot_tag(py_file)
        
        results.append({
            "file": str(py_file),
            "has_tag": has_tag,
            "domain": domain,
            "status": status,
            "needs_fix": not has_tag or (domain and domain != "analytics" and "analytics" in str(py_file).lower())
        })
    
    return results


def generate_report(results: List[Dict]) -> str:
    """Generate SSOT verification report."""
    total_files = len(results)
    files_with_tags = sum(1 for r in results if r["has_tag"])
    files_needing_fix = sum(1 for r in results if r["needs_fix"])
    
    report_lines = [
        "# SSOT Tagging Verification Report - Analytics Domain",
        "",
        f"**Date**: 2025-12-13",
        f"**Agent**: Agent-5 (Business Intelligence Specialist)",
        f"**Total Files Scanned**: {total_files}",
        f"**Files with SSOT Tags**: {files_with_tags}",
        f"**Files Needing Fix**: {files_needing_fix}",
        "",
        "---",
        "",
        "## File-by-File Verification",
        "",
        "| File | Has Tag | Domain | Status |",
        "|------|---------|--------|--------|",
    ]
    
    for result in sorted(results, key=lambda x: x["file"]):
        file_name = result["file"].replace("src/core/analytics/", "")
        has_tag = "✅" if result["has_tag"] else "❌"
        domain = result["domain"] or "N/A"
        status = result["status"]
        
        report_lines.append(f"| `{file_name}` | {has_tag} | {domain} | {status} |")
    
    report_lines.extend([
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Total Files**: {total_files}",
        f"- **Files with Tags**: {files_with_tags} ({files_with_tags/total_files*100:.1f}%)",
        f"- **Files Needing Fix**: {files_needing_fix}",
        "",
        "## Recommendations",
        "",
    ])
    
    if files_needing_fix > 0:
        report_lines.append(f"1. Fix SSOT tags in {files_needing_fix} file(s)")
        report_lines.append("2. Ensure all analytics domain files have `<!-- SSOT Domain: analytics -->`")
    else:
        report_lines.append("✅ All files have correct SSOT tags!")
    
    return "\n".join(report_lines)


def main():
    """Main entry point."""
    print("🔍 Scanning analytics domain for SSOT tags...")
    
    results = scan_analytics_domain()
    
    if not results:
        print("❌ No analytics domain files found")
        return
    
    print(f"✅ Scanned {len(results)} files")
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    report_path = Path("artifacts/2025-12-13_agent-5_ssot-verification-analytics-domain.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    
    print(f"💾 Report saved to: {report_path}")
    
    # Print summary
    files_with_tags = sum(1 for r in results if r["has_tag"])
    files_needing_fix = sum(1 for r in results if r["needs_fix"])
    
    print(f"\n📊 Summary:")
    print(f"   Total files: {len(results)}")
    print(f"   Files with tags: {files_with_tags}")
    print(f"   Files needing fix: {files_needing_fix}")


if __name__ == "__main__":
    main()




