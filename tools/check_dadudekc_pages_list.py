#!/usr/bin/env python3
"""Check dadudekc.com pages list."""

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

pages = requests.get(
    f"{api}/pages", params={"per_page": 20}, auth=auth, timeout=30).json()

print("Pages on dadudekc.com:")
for p in pages:
    print(
        f"  - {p.get('slug')} (ID: {p.get('id')}): {p.get('title', {}).get('rendered', 'N/A')[:60]}")




