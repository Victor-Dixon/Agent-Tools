#!/usr/bin/env python3
"""
Post Completion Report to Discord
==================================

Posts a completion report to Discord via webhook.

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-12-04
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants

def post_to_discord(content: str, title: str = "Completion Report") -> bool:
    """Post content to Discord via webhook."""
    # Try multiple webhook environment variables
    webhook_url = (
        os.getenv("DISCORD_ROUTER_WEBHOOK_URL") or
        os.getenv("DISCORD_WEBHOOK_URL") or
        os.getenv("DISCORD_WEBHOOK_AGENT_4")
    )
    
    if not webhook_url:
        print("❌ Discord webhook not configured")
        print("   Set one of these in .env:")
        print("   - DISCORD_ROUTER_WEBHOOK_URL")
        print("   - DISCORD_WEBHOOK_URL")
        print("   - DISCORD_WEBHOOK_AGENT_4")
        return False
    
    # Discord has a 2000 character limit per message
    # Split into chunks if needed
    max_length = 1900
    chunks = []
    
    if len(content) <= max_length:
        chunks = [content]
    else:
        # Split by sections (## headers)
        lines = content.split('\n')
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk) + len(line) + 1 < max_length:
                current_chunk += line + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
    
    # Post all chunks
    for i, chunk in enumerate(chunks):
        # Create embed for first chunk, plain text for continuation
        if i == 0:
            embed = {
                "title": title,
                "description": chunk,
                "color": 0x2ecc71,  # Green
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "Agent-4 (Captain) - Completion Report"
                }
            }
            payload = {
                "embeds": [embed],
                "username": "Agent-4"
            }
        else:
            payload = {
                "content": f"*(continued {i+1}/{len(chunks)})*\n```\n{chunk}\n```",
                "username": "Agent-4"
            }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=TimeoutConstants.HTTP_SHORT)
            
            if response.status_code in [200, 204]:
                print(f"✅ Posted chunk {i+1}/{len(chunks)} to Discord")
            else:
                print(f"❌ Error posting chunk {i+1}: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"❌ Error posting chunk {i+1}: {e}")
            return False
        
        # Rate limit between chunks
        if i < len(chunks) - 1:
            import time
            time.sleep(1)
    
    return True

def main():
    """Post yesterday's completion report to Discord."""
    project_root = Path(__file__).resolve().parent.parent
    report_path = project_root / "agent_workspaces" / "Agent-4" / "YESTERDAY_COMPLETION_REPORT_2025-12-03.md"
    
    if not report_path.exists():
        print(f"❌ Report not found: {report_path}")
        return 1
    
    # Read the report
    report_content = report_path.read_text(encoding='utf-8')
    
    # Post to Discord
    success = post_to_discord(
        content=report_content,
        title="📊 Yesterday's Completion Report - December 3, 2025"
    )
    
    if success:
        print("\n✅ Successfully posted yesterday's completion report to Discord!")
        print("🐝 WE. ARE. SWARM. ⚡🔥")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
