#!/usr/bin/env python3
"""
Document SSOT Registry - Single Source of Truth Registry
========================================================

Scans codebase for SSOT tags and creates comprehensive SSOT registry.
Documents designated SSOT files for each domain.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import re
import json
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent


def find_ssot_files(directory: Path) -> Dict[str, Dict]:
    """Find all files with SSOT domain tags."""
    ssot_files = {}
    
    # Pattern to match SSOT tags
    patterns = [
        r'# SSOT Domain:\s*(\w+)',  # Python comment
        r'<!-- SSOT Domain:\s*(\w+)\s*-->',  # HTML/XML comment
        r'// SSOT Domain:\s*(\w+)',  # JavaScript comment
    ]
    
    for py_file in directory.rglob("*"):
        # Skip certain directories
        if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'node_modules', 'venv', 'htmlcov']):
            continue
        
        if not py_file.is_file():
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for SSOT tags
            domain = None
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    domain = match.group(1).strip()
                    break
            
            if domain:
                relative_path = str(py_file.relative_to(PROJECT_ROOT))
                ssot_files[relative_path] = {
                    'domain': domain,
                    'file_path': relative_path,
                    'file_type': py_file.suffix
                }
        
        except Exception:
            # Skip files that can't be read
            continue
    
    return ssot_files


def organize_by_domain(ssot_files: Dict[str, Dict]) -> Dict[str, List[str]]:
    """Organize SSOT files by domain."""
    by_domain = defaultdict(list)
    
    for file_path, info in ssot_files.items():
        domain = info['domain']
        by_domain[domain].append(file_path)
    
    return dict(by_domain)


def generate_ssot_registry(ssot_files: Dict[str, Dict], by_domain: Dict[str, List[str]]) -> Dict:
    """Generate comprehensive SSOT registry."""
    registry = {
        'total_ssot_files': len(ssot_files),
        'domains': {},
        'domain_summary': {domain: len(files) for domain, files in by_domain.items()},
        'recommendations': {}
    }
    
    # Organize by domain
    for domain, files in sorted(by_domain.items()):
        registry['domains'][domain] = {
            'count': len(files),
            'files': sorted(files),
            'primary_ssot': files[0] if files else None  # First file as primary
        }
    
    # Generate recommendations
    for domain, files in by_domain.items():
        if len(files) > 1:
            registry['recommendations'][domain] = {
                'issue': f"Multiple SSOT files for domain '{domain}' ({len(files)} files)",
                'action': f"Review and designate single SSOT for {domain} domain",
                'files': files
            }
    
    return registry


def main():
    """Scan for SSOT files and generate registry."""
    print("🔍 Scanning for SSOT domain tags...")
    print()
    
    # Find SSOT files
    ssot_files = find_ssot_files(PROJECT_ROOT / "src")
    ssot_files.update(find_ssot_files(PROJECT_ROOT / "tools"))
    
    print(f"📊 Found {len(ssot_files)} SSOT-tagged files")
    print()
    
    # Organize by domain
    by_domain = organize_by_domain(ssot_files)
    
    print("📋 SSOT Files by Domain:")
    for domain, files in sorted(by_domain.items()):
        print(f"   {domain}: {len(files)} files")
        for file_path in sorted(files)[:3]:  # Show first 3
            print(f"      - {file_path}")
        if len(files) > 3:
            print(f"      ... and {len(files) - 3} more")
    print()
    
    # Generate registry
    registry = generate_ssot_registry(ssot_files, by_domain)
    
    # Check for multiple SSOTs per domain
    multiple_ssots = {domain: files for domain, files in by_domain.items() if len(files) > 1}
    if multiple_ssots:
        print("⚠️  Domains with Multiple SSOT Files:")
        for domain, files in sorted(multiple_ssots.items()):
            print(f"   {domain}: {len(files)} files (needs consolidation)")
            for file_path in files:
                print(f"      - {file_path}")
        print()
    
    # Save registry
    registry_file = PROJECT_ROOT / "docs" / "archive" / "consolidation" / "ssot_registry.json"
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    print(f"✅ SSOT registry saved to: {registry_file}")
    print()
    print("🎯 Summary:")
    print(f"   • Total SSOT files: {registry['total_ssot_files']}")
    print(f"   • Unique domains: {len(by_domain)}")
    print(f"   • Domains needing consolidation: {len(multiple_ssots)}")


if __name__ == "__main__":
    main()

