#!/usr/bin/env python3
"""Delete Hello World default WordPress post."""

import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("❌ requests library not available")
    sys.exit(1)

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30


def load_config():
    config_path = project_root / ".deploy_credentials" / "blogging_api.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def delete_post(site_url, username, app_password, post_id):
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts/{post_id}"
    auth = HTTPBasicAuth(username, app_password)
    
    response = requests.delete(
        api_url,
        auth=auth,
        params={"force": True},
        timeout=TimeoutConstants.HTTP_DEFAULT
    )
    return response.status_code == 200


def main():
    config = load_config()
    site_config = config["dadudekc.com"]
    
    if delete_post(site_config["site_url"], site_config["username"], site_config["app_password"], 1):
        print("✅ Deleted Hello World post")
        return 0
    else:
        print("❌ Failed to delete Hello World post")
        return 1


if __name__ == "__main__":
    sys.exit(main())





