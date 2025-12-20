#!/usr/bin/env python3
"""
Upload File to Discord via Webhook
===================================

Uploads a file to Discord using a webhook URL.

Author: Agent-3 (Infrastructure & DevOps Specialist)
"""

import os
import sys
import requests
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def upload_file_to_discord(
    file_path: Path,
    webhook_url: str,
    content: str = "",
    username: str = "Agent-3"
) -> bool:
    """
    Upload a file to Discord via webhook.
    
    Args:
        file_path: Path to file to upload
        webhook_url: Discord webhook URL
        content: Optional message content
        username: Optional username for webhook
    
    Returns:
        True if successful
    """
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    if not webhook_url:
        print("❌ Discord webhook URL not provided")
        return False
    
    print(f"📤 Uploading {file_path.name} to Discord...")
    print(f"   Size: {file_path.stat().st_size:,} bytes")
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/zip")}
            data = {
                "content": content,
                "username": username
            }
            
            response = requests.post(
                webhook_url,
                files=files,
                data=data,
                timeout=TimeoutConstants.HTTP_MEDIUM
            )
            
            if response.status_code == 200 or response.status_code == 204:
                print(f"✅ Successfully uploaded {file_path.name} to Discord!")
                return True
            else:
                print(f"❌ Discord error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to upload file: {e}")
        return False


def main():
    """CLI interface."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(description="Upload file to Discord via webhook")
    parser.add_argument("file", type=Path, help="File to upload")
    parser.add_argument("--webhook", type=str, help="Discord webhook URL (or set DISCORD_WEBHOOK_URL env var)")
    parser.add_argument("--content", type=str, default="", help="Message content")
    parser.add_argument("--username", type=str, default="Agent-3", help="Webhook username")
    
    args = parser.parse_args()
    
    webhook_url = args.webhook or os.getenv("DISCORD_WEBHOOK_URL") or os.getenv("DISCORD_AGENT3_WEBHOOK")
    
    if not webhook_url:
        print("❌ Error: Discord webhook URL required")
        print("   Set --webhook argument or DISCORD_WEBHOOK_URL environment variable")
        sys.exit(1)
    
    success = upload_file_to_discord(
        file_path=args.file,
        webhook_url=webhook_url,
        content=args.content,
        username=args.username
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()





