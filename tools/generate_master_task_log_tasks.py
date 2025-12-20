#!/usr/bin/env python3
"""
Generate Master Task Log Tasks from Site Audit Data
====================================================

Generates task list entries for MASTER_TASK_LOG.md from site audit data.

Usage:
    python tools/generate_master_task_log_tasks.py
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import List, Dict

project_root = Path(__file__).resolve().parent.parent
broken_links_path = project_root / "docs" / "site_audit" / "broken_links.json"


def generate_task_id(site_domain: str, url: str, source: str) -> str:
    """Generate unique task ID."""
    site_short = site_domain.replace(".com", "").replace(".", "").upper()[:12]
    url_slug = url.split("/")[-1] or "home"
    hash_suffix = hashlib.md5(f"{url}{source}".encode()).hexdigest()[:8].upper()
    return f"{site_short}-{source.upper()}-{hash_suffix}"


def generate_tasks_from_broken_links() -> List[str]:
    """Generate tasks from broken_links.json."""
    if not broken_links_path.exists():
        print(f"❌ File not found: {broken_links_path}")
        return []
    
    with open(broken_links_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tasks = []
    
    for site_domain, site_data in data.get("sites", {}).items():
        broken_links = site_data.get("broken_links", [])
        
        for link in broken_links:
            # Skip if already fixed (pages that have been created)
            # This is a simple check - you may need to update this based on completed tasks
            url = link.get("url", "")
            source = link.get("source", "unknown")
            text = link.get("text", "")
            severity = link.get("severity", "MEDIUM")
            
            # Format task
            task_id = generate_task_id(site_domain, url, source)
            priority = "HIGH" if severity == "HIGH" else "MEDIUM"
            
            # Format description
            if source == "nav":
                description = f"{site_domain}: nav link '{text}' -> 404 ({url})"
            elif source == "footer":
                description = f"{site_domain}: footer link '{text}' -> 404 ({url})"
            elif source == "cta":
                description = f"{site_domain}: CTA link '{text}' -> 404 ({url})"
            else:
                description = f"{site_domain}: {source} link '{text}' -> 404 ({url})"
            
            task = f"- [ ] [SITE_AUDIT][{priority}][SA-{task_id}] {description}"
            tasks.append(task)
    
    return tasks


def main():
    """Main execution."""
    print("🔧 Generating tasks from site audit data...\n")
    
    tasks = generate_tasks_from_broken_links()
    
    if not tasks:
        print("❌ No tasks generated")
        return 1
    
    print(f"📋 Generated {len(tasks)} tasks:\n")
    for task in tasks:
        print(task)
    
    print(f"\n✅ Task generation complete")
    print(f"\n💡 Copy the tasks above and add them to MASTER_TASK_LOG.md")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





