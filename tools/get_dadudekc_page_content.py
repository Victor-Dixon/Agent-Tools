#!/usr/bin/env python3
"""Get dadudekc.com page content for review."""

import json
import sys
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
with open(creds_file) as f:
    creds_data = json.load(f)

config = creds_data["dadudekc.com"]
api = f"{config['site_url']}/wp-json/wp/v2"
auth = HTTPBasicAuth(config["username"],
                     config["app_password"].replace(" ", ""))

page_id = 76  # About page
response = requests.get(f"{api}/pages/{page_id}", auth=auth, timeout=30)

if response.status_code == 200:
    page = response.json()
    print(f"Title: {page.get('title', {}).get('rendered', 'N/A')}")
    print(
        f"\nContent (raw):\n{page.get('content', {}).get('raw', 'N/A')[:500]}")
    print(
        f"\nContent (rendered):\n{page.get('content', {}).get('rendered', 'N/A')[:500]}")
else:
    print(f"Error: {response.status_code}")




