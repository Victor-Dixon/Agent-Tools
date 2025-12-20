#!/usr/bin/env python3
"""
Claim and Fix Master Task Log Task
===================================

Automates the workflow of claiming and fixing tasks from MASTER_TASK_LOG.md.
This tool identifies the next available task, allows claiming it, and provides
a template for creating fix scripts based on task type.

This is the tool Agent-5 wished they had during the session!

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-17
V2 Compliant: <300 lines
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def parse_master_task_log() -> List[Dict[str, str]]:
    """Parse MASTER_TASK_LOG.md and extract unclaimed tasks."""
    log_path = project_root / "MASTER_TASK_LOG.md"
    if not log_path.exists():
        print(f"❌ MASTER_TASK_LOG.md not found at {log_path}")
        return []
    
    tasks = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Match task lines: - [ ] [CATEGORY][PRIORITY][TASK-ID] description
            match = re.match(r'^- \[ \] \[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\] (.+)', line)
            if match:
                category, priority, task_id, description = match.groups()
                tasks.append({
                    "line_num": line_num,
                    "category": category,
                    "priority": priority,
                    "task_id": task_id,
                    "description": description.strip(),
                    "raw_line": line.strip()
                })
    
    return tasks


def identify_task_type(task: Dict[str, str]) -> str:
    """Identify the type of task based on description and category."""
    desc = task["description"].lower()
    cat = task["category"].lower()
    
    if "404" in desc or "nav link" in desc or "footer link" in desc:
        return "wordpress_page_404"
    elif "copy glitch" in desc or "rendering" in desc:
        return "frontend_fix"
    elif "seo" in desc or "unpublish" in desc:
        return "content_management"
    elif "nav" in desc or "ia" in desc or "structure" in desc:
        return "navigation_ia"
    elif "cta" in desc:
        return "cta_enhancement"
    else:
        return "unknown"


def claim_task(task: Dict[str, str], agent_id: str) -> bool:
    """Claim a task by updating MASTER_TASK_LOG.md."""
    log_path = project_root / "MASTER_TASK_LOG.md"
    
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update the specific line to add [CLAIMED BY Agent-X]
    line_idx = task["line_num"] - 1
    if line_idx < len(lines):
        line = lines[line_idx]
        if "[CLAIMED BY" not in line:
            lines[line_idx] = line.rstrip() + f" [CLAIMED BY {agent_id}]\n"
            
            with open(log_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
    
    return False


def generate_fix_template(task: Dict[str, str], task_type: str, agent_id: str) -> str:
    """Generate a fix script template based on task type."""
    
    if task_type == "wordpress_page_404":
        # Extract site and page info from description
        desc = task["description"]
        site_match = re.search(r'([a-z0-9.-]+\.(com|site|online))', desc)
        page_match = re.search(r"'(.*?)'", desc)
        
        site = site_match.group(1) if site_match else "example.com"
        page_name = page_match.group(1) if page_match else "page"
        page_slug = page_name.lower().replace(" ", "-")
        
        template = f'''#!/usr/bin/env python3
"""
Fix {site} {page_name} Page 404
================================

Task: {task["task_id"]}
Issue: {task["description"]}

Author: {agent_id}
V2 Compliant: <300 lines
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("❌ requests library required. Install with: pip install requests")
    sys.exit(1)

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30


def get_credentials() -> Optional[Dict[str, str]]:
    """Get WordPress credentials from config file."""
    config_paths = [
        Path(".deploy_credentials/blogging_api.json"),
        Path("config/blogging_api.json"),
        Path(project_root / ".deploy_credentials/blogging_api.json"),
        Path(project_root / "config/blogging_api.json"),
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    site_key = "{site}".replace(".", "_").replace("-", "_")
                    site_config = config.get(site_key) or config.get("{site}")
                    if site_config:
                        return {{
                            "username": site_config.get("username"),
                            "app_password": site_config.get("app_password"),
                            "site_url": site_config.get("site_url", "https://{site}")
                        }}
            except Exception as e:
                print(f"⚠️  Could not read config from {{config_path}}: {{e}}")
                continue
    
    return None


def check_page_exists(site_url: str, slug: str, auth) -> Optional[Dict[str, Any]]:
    """Check if a WordPress page with the given slug exists."""
    api_url = f"{{site_url.rstrip('/')}}/wp-json/wp/v2/pages"
    try:
        response = requests.get(
            api_url,
            params={{"slug": slug}},
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            pages = response.json()
            if pages:
                return {{
                    "exists": True,
                    "page_id": pages[0]["id"],
                    "link": pages[0]["link"],
                    "status": pages[0].get("status", "unknown")
                }}
        return {{"exists": False}}
    except Exception as e:
        print(f"⚠️  Error checking page existence: {{e}}")
        return None


def create_page(site_url: str, username: str, app_password: str) -> Dict[str, Any]:
    """Create the {page_name} page for {site}."""
    api_url = f"{{site_url.rstrip('/')}}/wp-json/wp/v2/pages"
    auth = HTTPBasicAuth(username, app_password.replace(" ", ""))
    
    slug = "{page_slug}"
    
    # Check if page already exists
    existing = check_page_exists(site_url, slug, auth)
    if existing and existing.get("exists"):
        status = existing.get("status")
        if status == "publish":
            return {{
                "success": True,
                "page_id": existing.get("page_id"),
                "link": existing.get("link"),
                "message": "Page already exists and is published",
                "action": "skipped"
            }}
    
    # Create new page
    page_content = f"""<!-- wp:paragraph -->
<p>Welcome to the {page_name} page.</p>
<!-- /wp:paragraph -->"""
    
    page_data = {{
        "title": "{page_name}",
        "slug": slug,
        "status": "publish",
        "content": page_content
    }}
    
    try:
        response = requests.post(
            api_url,
            json=page_data,
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code in (200, 201):
            page = response.json()
            return {{
                "success": True,
                "page_id": page.get("id"),
                "link": page.get("link"),
                "message": "Page created successfully",
                "action": "created"
            }}
        else:
            return {{
                "success": False,
                "error": f"HTTP {{response.status_code}}: {{response.text[:200]}}"
            }}
    except Exception as e:
        return {{
            "success": False,
            "error": str(e)
        }}


def main():
    """Main execution."""
    site_url = "https://{site}"
    
    print(f"🔧 Fixing {site} {page_name} Page 404")
    print(f"   Site: {{site_url}}")
    print(f"   Target: /{page_slug}")
    print()
    
    credentials = get_credentials()
    if not credentials:
        print("❌ WordPress credentials not found!")
        print("Please create .deploy_credentials/blogging_api.json")
        return 1
    
    result = create_page(
        site_url=credentials["site_url"],
        username=credentials["username"],
        app_password=credentials["app_password"]
    )
    
    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"   {{result.get('message')}}")
        print(f"   Page ID: {{result.get('page_id')}}")
        print(f"   Link: {{result.get('link')}}")
        return 0
    else:
        print("❌ FAILED!")
        print(f"   Error: {{result.get('error')}}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
    else:
        template = f'''#!/usr/bin/env python3
"""
Fix Task: {task["task_id"]}
===========================

Task: {task["task_id"]}
Issue: {task["description"]}

Author: {agent_id}
V2 Compliant: <300 lines
"""

# TODO: Implement fix for {task["description"]}
# Task Type: {task_type}
# Category: {task["category"]}
# Priority: {task["priority"]}

def main():
    """Main execution."""
    print(f"🔧 Fixing: {task["description"]}")
    print("TODO: Implement fix")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
'''
    
    return template


def main():
    """Main execution."""
    agent_id = "Agent-5"  # Could be passed as argument
    
    print("🎯 Claim and Fix Master Task Log Task")
    print()
    
    # Parse tasks
    tasks = parse_master_task_log()
    if not tasks:
        print("❌ No unclaimed tasks found")
        return 1
    
    # Filter by priority (show HIGH first)
    high_priority = [t for t in tasks if t["priority"] == "HIGH"]
    medium_priority = [t for t in tasks if t["priority"] == "MEDIUM"]
    other_tasks = [t for t in tasks if t["priority"] not in ["HIGH", "MEDIUM"]]
    
    print(f"📋 Available Tasks:")
    print(f"   HIGH: {len(high_priority)}")
    print(f"   MEDIUM: {len(medium_priority)}")
    print(f"   OTHER: {len(other_tasks)}")
    print()
    
    # Show first HIGH priority task
    if high_priority:
        task = high_priority[0]
        print(f"🎯 Next HIGH Priority Task:")
        print(f"   ID: {task['task_id']}")
        print(f"   Category: {task['category']}")
        print(f"   Description: {task['description']}")
        print()
        
        # Identify task type
        task_type = identify_task_type(task)
        print(f"   Task Type: {task_type}")
        print()
        
        # Claim task
        if claim_task(task, agent_id):
            print(f"✅ Task claimed by {agent_id}")
            
            # Generate fix template
            if task_type == "wordpress_page_404":
                script_name = f"tools/fix_{task['task_id'].lower().replace('-', '_')}.py"
                template = generate_fix_template(task, task_type, agent_id)
                
                script_path = project_root / script_name
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(template)
                
                print(f"📝 Fix script template created: {script_name}")
                print(f"   Next: Edit script, add appropriate content, and execute")
        else:
            print("⚠️  Could not claim task (may already be claimed)")
    else:
        print("ℹ️  No HIGH priority tasks available")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())



