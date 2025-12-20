#!/usr/bin/env python3
"""Quick script to check TSLA posts."""
import json
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

creds_file = Path(".deploy_credentials/blogging_api.json")
creds = json.load(open(creds_file))
config = creds["freerideinvestor"]
auth = HTTPBasicAuth(config["username"],
                     config["app_password"].replace(" ", ""))

url = f"{config['site_url']}/wp-json/wp/v2/posts"
r = requests.get(url, params={
                 "per_page": 100, "search": "tsla", "status": "any"}, auth=auth, timeout=30)
posts = r.json()

print("TSLA Posts:")
for p in posts:
    if "tsla" in p.get("slug", "").lower():
        print(f"  ID: {p['id']}, Slug: {p.get('slug')}, Status: {p.get('status')}, Title: {p.get('title', {}).get('rendered', 'N/A')[:50]}")
