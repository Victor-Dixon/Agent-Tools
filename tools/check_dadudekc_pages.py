#!/usr/bin/env python3
import json
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

creds_file = Path(".deploy_credentials/blogging_api.json")
creds = json.load(open(creds_file))
config = creds["dadudekc.com"]
auth = HTTPBasicAuth(config["username"],
                     config["app_password"].replace(" ", ""))

url = f"{config['site_url']}/wp-json/wp/v2/pages"
r = requests.get(url, params={"per_page": 20}, auth=auth, timeout=30)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}")

if r.status_code == 200:
    try:
        pages = r.json()
        print(f"\nPages: {len(pages)}")
        for p in pages[:10]:
            title = p.get('title', {}).get('rendered', 'N/A')[:60]
            print(f"  ID: {p['id']}, Slug: {p.get('slug')}, Title: {title}")
    except:
        print("Failed to parse JSON")
