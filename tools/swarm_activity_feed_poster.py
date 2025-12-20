#!/usr/bin/env python3
"""
Swarm Activity Feed Poster
==========================

Automatically posts swarm devlogs to weareswarm.online WordPress site.
Monitors devlogs directory and posts new entries as blog posts.

Author: Agent-2
V2 Compliant: <300 lines
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load credentials
creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
with open(creds_file) as f:
    creds_data = json.load(f)

SITE_CONFIG = creds_data["weareswarm.online"]
SITE_URL = SITE_CONFIG["site_url"]
USERNAME = SITE_CONFIG["username"]
APP_PASSWORD = SITE_CONFIG["app_password"]

API_BASE = f"{SITE_URL}/wp-json/wp/v2"
AUTH = HTTPBasicAuth(USERNAME, APP_PASSWORD.replace(" ", ""))

# Directories
DEVLOGS_DIR = project_root / "devlogs"
POSTED_TRACKER = project_root / "sites" / \
    "weareswarm.online" / "posted_devlogs.json"


def load_posted_devlogs() -> Dict[str, bool]:
    """Load tracking file of posted devlogs."""
    if POSTED_TRACKER.exists():
        try:
            with open(POSTED_TRACKER, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_posted_devlog(devlog_file: str):
    """Mark devlog as posted."""
    posted = load_posted_devlogs()
    posted[devlog_file] = True
    POSTED_TRACKER.parent.mkdir(parents=True, exist_ok=True)
    with open(POSTED_TRACKER, 'w', encoding='utf-8') as f:
        json.dump(posted, f, indent=2)


def parse_devlog(file_path: Path) -> Optional[Dict]:
    """Parse devlog markdown file and extract content."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(
            1) if title_match else file_path.stem.replace('_', ' ').title()

        # Extract agent
        agent_match = re.search(r'\*\*Agent:\*\*\s*(.+?)(?:\n|$)', content)
        agent = agent_match.group(1).strip() if agent_match else "Swarm"

        # Extract date
        date_match = re.search(r'\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})', content)
        date_str = date_match.group(
            1) if date_match else datetime.now().strftime('%Y-%m-%d')

        # Extract status
        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', content)
        status = status_match.group(1).strip() if status_match else ""

        # Format content for public consumption
        # Remove internal references, format for WordPress
        public_content = format_for_public(content, agent, date_str)

        return {
            "title": f"{title} - {agent}",
            "content": public_content,
            "excerpt": f"Swarm activity update from {agent} on {date_str}",
            "agent": agent,
            "date": date_str,
            "status": status
        }
    except Exception as e:
        print(f"  ⚠️  Error parsing {file_path.name}: {e}")
        return None


def format_for_public(content: str, agent: str, date: str) -> str:
    """Format devlog content for public consumption."""
    # Convert markdown to HTML
    html = content

    # Convert headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

    # Convert bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Convert code blocks
    html = re.sub(r'```(\w+)?\n(.*?)```',
                  r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    # Convert lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)

    # Convert paragraphs
    paragraphs = html.split('\n\n')
    formatted = []
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<'):
            formatted.append(f'<p>{para}</p>')
        else:
            formatted.append(para)

    html = '\n'.join(formatted)

    # Add header with agent info
    header = f"""<div class="swarm-activity-item">
<div class="swarm-activity-meta">Agent: {agent} | Date: {date}</div>
</div>
"""

    return header + html


def get_or_create_category(category_name: str) -> Optional[int]:
    """Get or create a category."""
    url = f"{API_BASE}/categories"
    params = {"search": category_name, "per_page": 100}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        categories = response.json()
        for cat in categories:
            if cat["name"].lower() == category_name.lower():
                return cat["id"]

    # Create category
    url = f"{API_BASE}/categories"
    data = {"name": category_name}
    response = requests.post(url, json=data, auth=AUTH, timeout=30)

    if response.status_code == 201:
        return response.json()["id"]

    return None


def get_or_create_tags(tag_names: List[str]) -> List[int]:
    """Get or create tags."""
    tag_ids = []

    for tag_name in tag_names:
        url = f"{API_BASE}/tags"
        params = {"search": tag_name, "per_page": 100}
        response = requests.get(url, params=params, auth=AUTH, timeout=30)

        if response.status_code == 200:
            tags = response.json()
            for tag in tags:
                if tag["name"].lower() == tag_name.lower():
                    tag_ids.append(tag["id"])
                    break
            else:
                # Create tag
                url = f"{API_BASE}/tags"
                data = {"name": tag_name}
                response = requests.post(url, json=data, auth=AUTH, timeout=30)
                if response.status_code == 201:
                    tag_ids.append(response.json()["id"])

    return tag_ids


def post_devlog(devlog_data: Dict) -> bool:
    """Post devlog to WordPress."""
    print(f"  📝 Posting: {devlog_data['title']}")

    # Get category (Agent Operations)
    category_id = get_or_create_category("Agent Operations")

    # Get tags
    tags = ["swarm", "activity", "update",
            devlog_data["agent"].lower().replace(" ", "-")]
    tag_ids = get_or_create_tags(tags)

    # Prepare post data
    post_data = {
        "title": devlog_data["title"],
        "content": devlog_data["content"],
        "excerpt": devlog_data["excerpt"],
        "status": "publish",
        "format": "standard",
    }

    if category_id:
        post_data["categories"] = [category_id]

    if tag_ids:
        post_data["tags"] = tag_ids

    # Post to WordPress
    url = f"{API_BASE}/posts"
    response = requests.post(url, json=post_data, auth=AUTH, timeout=30)

    if response.status_code == 201:
        post = response.json()
        print(f"    ✅ Posted: {post['link']}")
        return True
    else:
        print(f"    ❌ Error: {response.status_code} - {response.text}")
        return False


def process_new_devlogs():
    """Process new devlogs that haven't been posted yet."""
    if not DEVLOGS_DIR.exists():
        print(f"  ⚠️  Devlogs directory not found: {DEVLOGS_DIR}")
        return

    posted = load_posted_devlogs()
    new_devlogs = []

    # Find all markdown devlogs
    for devlog_file in DEVLOGS_DIR.glob("*.md"):
        file_key = str(devlog_file.relative_to(project_root))
        if file_key not in posted:
            new_devlogs.append(devlog_file)

    if not new_devlogs:
        print("  ℹ️  No new devlogs to post")
        return

    print(f"  📋 Found {len(new_devlogs)} new devlog(s)")

    for devlog_file in sorted(new_devlogs):
        print(f"\n  Processing: {devlog_file.name}")
        devlog_data = parse_devlog(devlog_file)

        if devlog_data:
            if post_devlog(devlog_data):
                save_posted_devlog(str(devlog_file.relative_to(project_root)))
        else:
            print(f"    ⚠️  Skipped (parse error)")


def main():
    """Main execution."""
    print("🚀 Swarm Activity Feed Poster\n")
    print(f"📡 Monitoring: {DEVLOGS_DIR}")
    print(f"🌐 Posting to: {SITE_URL}\n")

    process_new_devlogs()

    print(f"\n✅ Activity feed update complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
