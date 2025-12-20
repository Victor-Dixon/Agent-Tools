"""
Communication Tools - Discord Router Integration
================================================

Unified Discord posting for all agents via router.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-11-24
Priority: CRITICAL - Agents not posting to Discord
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()


class DiscordRouterPoster:
    """Unified Discord router posting for all agents."""
    
    def __init__(self):
        """Initialize Discord router poster."""
        # Get Discord router webhook (prefer router, fallback to agent-specific)
        self.webhook_url = (
            os.getenv("DISCORD_ROUTER_WEBHOOK_URL") or
            os.getenv("DISCORD_WEBHOOK_URL")
        )
        
        if not self.webhook_url:
            print("⚠️  WARNING: No Discord webhook configured")
            print("   Set DISCORD_ROUTER_WEBHOOK_URL or DISCORD_WEBHOOK_URL in .env")
    
    def post_update(
        self,
        agent_id: str,
        message: str,
        title: Optional[str] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Post update to Discord via router.
        
        Args:
            agent_id: Agent identifier (e.g., "Agent-8")
            message: Message content
            title: Optional title (defaults to agent update)
            priority: Priority level (normal, high, urgent)
        
        Returns:
            Result dict with success status
        """
        if not self.webhook_url:
            return {
                "success": False,
                "error": "No Discord webhook configured",
            }
        
        # Format title
        if not title:
            title = f"{agent_id} Update"
        
        # Add priority indicator
        priority_icons = {
            "urgent": "🚨",
            "high": "⚡",
            "normal": "📢",
        }
        icon = priority_icons.get(priority, "📢")
        
        # Format message for Discord
        content = f"{icon} ## {title}\n\n{message}\n\n*Posted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        # Discord message payload
        payload = {
            "content": content,
            "username": f"{agent_id} (Discord Router)",
            "avatar_url": None
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return {
                "success": True,
                "message": f"Posted update to Discord: {title}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class DiscordPostTool:
    """Tool adapter for Discord posting."""
    
    def __init__(self):
        """Initialize Discord post tool."""
        self.poster = DiscordRouterPoster()
    
    def execute(self, params: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """
        Execute Discord post.
        
        Args:
            params: {
                "agent_id": "Agent-8",
                "message": "Update message",
                "title": "Optional title",
                "priority": "normal|high|urgent"
            }
        
        Returns:
            Result dict
        """
        agent_id = params.get("agent_id", "Agent-8")
        message = params.get("message", "")
        title = params.get("title")
        priority = params.get("priority", "normal")
        
        if not message:
            return {
                "success": False,
                "error": "Message is required",
            }
        
        result = self.poster.post_update(agent_id, message, title, priority)
        
        if result["success"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Failed to post to Discord: {result.get('error')}")
        
        return result


# Tool registration
def get_tools():
    """Get communication tools."""
    return {
        "discord.post": DiscordPostTool(),
    }


