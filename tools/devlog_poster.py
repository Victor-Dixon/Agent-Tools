#!/usr/bin/env python3
"""
Unified Devlog Poster - SSOT for Discord Devlog Posting
=======================================================

Single comprehensive tool for all devlog posting operations:
- Agents always post to their own devlog channels (#agent-X-devlogs)
- Captain (Agent-4) channel reserved for major updates only
- Automatic Swarm Brain integration
- Smart content chunking
- Mermaid diagram support

Usage:
    # Agent posts to their own channel
    python tools/devlog_poster.py --agent Agent-7 --file devlog.md
    
    # Major update (Captain posts to captain channel, others to their own)
    python tools/devlog_poster.py --agent Agent-4 --file major_update.md --major
    
    # Regular agent update (always goes to agent's channel)
    python tools/devlog_poster.py --agent Agent-1 --file update.md

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <400 lines
"""

import os
import re
import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Add project root to path BEFORE imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import requests
from dotenv import load_dotenv, dotenv_values
from src.core.config.timeout_constants import TimeoutConstants

# Load environment variables
try:
    env_vars = dotenv_values(".env")
    for key, value in env_vars.items():
        if value and key not in os.environ:
            os.environ[key] = value
except Exception:
    load_dotenv()


class DevlogPoster:
    """Unified devlog poster with proper channel routing."""
    
    def __init__(self):
        self.swarm_brain_path = Path("swarm_brain/devlogs")
        self._load_agent_webhooks()
    
    def _load_agent_webhooks(self):
        """Load agent Discord webhook URLs from environment."""
        self.agent_webhooks: Dict[str, Optional[str]] = {}
        
        # Load webhooks for all agents
        for i in range(1, 9):
            agent_lower = f"agent-{i}"
            agent_cap = f"Agent-{i}"
            
            # Try multiple env var formats
            webhook = (
                os.getenv(f"DISCORD_WEBHOOK_AGENT_{i}") or
                os.getenv(f"DISCORD_AGENT{i}_WEBHOOK") or
                (os.getenv("DISCORD_CAPTAIN_WEBHOOK") if i == 4 else None)
            )
            
            self.agent_webhooks[agent_lower] = webhook
            self.agent_webhooks[agent_cap] = webhook
    
    def _normalize_agent(self, agent: str) -> str:
        """Normalize agent ID to lowercase format."""
        agent_lower = agent.lower()
        if agent_lower.startswith("agent-"):
            return agent_lower
        elif agent_lower.startswith("agent"):
            return f"agent-{agent_lower.replace('agent', '')}"
        return agent_lower
    
    def _get_webhook(self, agent: str) -> Optional[str]:
        """Get webhook URL for agent."""
        normalized = self._normalize_agent(agent)
        return self.agent_webhooks.get(agent) or self.agent_webhooks.get(normalized)
    
    def _should_post_to_captain(self, agent: str, is_major: bool) -> bool:
        """
        Determine if post should go to Captain channel.
        Rules:
        - Captain (Agent-4) major updates → Captain channel
        - Other agents → Always their own channel (never Captain)
        """
        normalized = self._normalize_agent(agent)
        is_captain = normalized == "agent-4"
        
        # Only Captain's major updates go to Captain channel
        return is_captain and is_major
    
    def _get_target_channel(self, agent: str, is_major: bool) -> tuple[str, Optional[str]]:
        """
        Get target channel for posting.
        Returns: (channel_name, webhook_url)
        """
        normalized = self._normalize_agent(agent)
        
        # Check if should post to Captain channel
        if self._should_post_to_captain(agent, is_major):
            captain_webhook = self._get_webhook("agent-4")
            if captain_webhook:
                return ("#captain-updates", captain_webhook)
        
        # All other cases: post to agent's own channel
        agent_webhook = self._get_webhook(agent)
        if agent_webhook:
            return (f"#{normalized}-devlogs", agent_webhook)
        
        # Fallback error
        return (f"#{normalized}-devlogs", None)
    
    def categorize_devlog(self, filename: str, content: str) -> str:
        """Auto-categorize devlog based on content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        if 'repo' in filename_lower or 'repository' in content_lower:
            return 'repository_analysis'
        if 'mission' in filename_lower or 'complete' in filename_lower:
            return 'mission_reports'
        if 'session' in filename_lower or 'cycle' in filename_lower:
            return 'agent_sessions'
        if any(word in content_lower for word in ['debate', 'swarm', 'decision', 'vote']):
            return 'system_events'
        
        return 'agent_sessions'
    
    def upload_to_swarm_brain(self, agent: str, file_path: Path, 
                             category: Optional[str] = None) -> Path:
        """Upload devlog to Swarm Brain."""
        content = file_path.read_text(encoding='utf-8')
        
        if not category:
            category = self.categorize_devlog(file_path.name, content)
        
        category_path = self.swarm_brain_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        filename = file_path.name
        normalized = self._normalize_agent(agent)
        if not filename.startswith(normalized.replace('-', '')):
            timestamp = datetime.now().strftime("%Y-%m-%d")
            filename = f"{timestamp}_{normalized}_{filename}"
        
        target_path = category_path / filename
        target_path.write_text(content, encoding='utf-8')
        
        try:
            rel_path = target_path.relative_to(Path.cwd())
            print(f"✅ Uploaded to Swarm Brain: {rel_path}")
        except ValueError:
            print(f"✅ Uploaded to Swarm Brain: {target_path}")
        
        return target_path
    
    def _chunk_content(self, text: str, max_size: int = 1800) -> List[str]:
        """Split content into chunks preserving markdown."""
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        lines = text.split('\n')
        current_chunk = ""
        
        for line in lines:
            test_chunk = current_chunk + line + '\n'
            if len(test_chunk) > max_size and current_chunk:
                chunks.append(current_chunk.rstrip())
                current_chunk = line + '\n'
            else:
                current_chunk = test_chunk
        
        if current_chunk.strip():
            chunks.append(current_chunk.rstrip())
        
        return chunks
    
    def post_to_discord(self, agent: str, file_path: Path, is_major: bool = False) -> bool:
        """Post devlog to appropriate Discord channel."""
        normalized = self._normalize_agent(agent)
        channel_name, webhook_url = self._get_target_channel(agent, is_major)
        
        if not webhook_url:
            print(f"❌ ERROR: No Discord webhook configured for {agent}")
            print(f"   Channel: {channel_name}")
            print(f"   Check environment variables:")
            print(f"   - DISCORD_WEBHOOK_AGENT_X (webhook URL)")
            print(f"   - DISCORD_AGENTX_WEBHOOK (alternative format)")
            return False
        
        content = file_path.read_text(encoding='utf-8')
        
        # Check for Mermaid diagrams
        try:
            import sys
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            try:
                from tools_v2.utils.discord_mermaid_renderer import DiscordMermaidRenderer
            except ImportError:
                from tools.discord_mermaid_renderer import DiscordMermaidRenderer
            
            renderer = DiscordMermaidRenderer()
            if renderer.extract_mermaid_diagrams(content):
                print("🔍 Detected Mermaid diagrams - converting to images...")
                return renderer.post_to_discord_with_mermaid(
                    content, webhook_url,
                    username=f"{agent.upper()} Devlog Bot",
                    temp_dir=Path("temp/discord_images")
                )
        except (ImportError, Exception) as e:
            print(f"⚠️ Mermaid renderer not available: {e}")
        
        # Prepare message
        title = f"{'🚨 MAJOR UPDATE' if is_major else '📋 Devlog'}: {file_path.name}"
        
        # Chunk content if needed
        chunks = self._chunk_content(content)
        preview = chunks[0] + "\n\n*(Continued in next message...)*" if len(chunks) > 1 else chunks[0]
        remaining = chunks[1:] if len(chunks) > 1 else []
        
        # Create embed
        embed = {
            "title": title,
            "description": preview,
            "color": 0xFF0000 if is_major else 0x3498DB,
            "fields": [
                {"name": "Agent", "value": agent.upper(), "inline": True},
                {"name": "Category", "value": self.categorize_devlog(file_path.name, content), "inline": True},
                {"name": "Timestamp", "value": datetime.now().strftime("%Y-%m-%d %H:%M"), "inline": True},
            ],
            "footer": {"text": "Swarm Brain Devlog System"}
        }
        
        payload = {
            "embeds": [embed],
            "username": f"{agent.upper()} Devlog Bot"
        }
        
        # Post embed
        try:
            response = requests.post(webhook_url, json=payload, timeout=TimeoutConstants.HTTP_SHORT)
            if response.status_code == 204:
                print(f"✅ Posted to Discord: {channel_name}")
                self._log_post(agent, file_path, is_major, channel_name, True)
            else:
                print(f"❌ Discord error: {response.status_code}")
                self._log_post(agent, file_path, is_major, channel_name, False)
                return False
        except Exception as e:
            print(f"❌ Failed to post to Discord: {e}")
            self._log_post(agent, file_path, is_major, channel_name, False)
            return False
        
        # Post remaining chunks as beautiful embeds
        if remaining:
            total_parts = len(remaining) + 1
            print(f"📦 Posting {len(remaining)} additional chunks as embeds...")
            for i, chunk in enumerate(remaining, 2):
                # Create beautiful embed for each chunk (consistent with first message)
                chunk_embed = {
                    "title": f"{'🚨 MAJOR UPDATE' if is_major else '📋 Devlog'} (Part {i}/{total_parts})",
                    "description": chunk,
                    "color": 0xFF0000 if is_major else 0x3498DB,
                    "fields": [
                        {"name": "Agent", "value": agent.upper(), "inline": True},
                        {"name": "Part", "value": f"{i}/{total_parts}", "inline": True},
                        {"name": "Category", "value": self.categorize_devlog(file_path.name, content), "inline": True},
                    ],
                    "footer": {"text": "Swarm Brain Devlog System"}
                }
                
                chunk_payload = {
                    "embeds": [chunk_embed],
                    "username": f"{agent.upper()} Devlog Bot"
                }
                
                try:
                    response = requests.post(webhook_url, json=chunk_payload, timeout=TimeoutConstants.HTTP_SHORT)
                    if response.status_code != 204:
                        print(f"❌ Discord error for chunk {i}: {response.status_code}")
                        return False
                    print(f"✅ Posted chunk {i}/{total_parts} as embed")
                    time.sleep(1)  # Rate limit
                except Exception as e:
                    print(f"❌ Failed to post chunk {i}: {e}")
                    return False
        
        return True
    
    def _log_post(self, agent: str, file_path: Path, is_major: bool, 
                 channel: str, success: bool):
        """Log devlog post for tracking."""
        log_file = Path("logs/devlog_posts.json")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        posts = []
        if log_file.exists():
            try:
                posts = json.loads(log_file.read_text(encoding='utf-8'))
            except:
                posts = []
        
        posts.append({
            "agent_id": self._normalize_agent(agent),
            "filename": file_path.name,
            "file_path": str(file_path),
            "timestamp": int(time.time()),
            "is_major": is_major,
            "success": success,
            "channel": channel
        })
        
        if len(posts) > 1000:
            posts = posts[-1000:]
        
        log_file.write_text(json.dumps(posts, indent=2), encoding='utf-8')
    
    def post(self, agent: str, file_path: str, is_major: bool = False,
            category: Optional[str] = None) -> bool:
        """Main post function - uploads to Swarm Brain + posts to Discord."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        normalized = self._normalize_agent(agent)
        channel_name, _ = self._get_target_channel(agent, is_major)
        
        print(f"\n{'='*60}")
        print(f"📤 DEVLOG POSTER - {'MAJOR UPDATE' if is_major else 'Standard Post'}")
        print(f"{'='*60}")
        print(f"Agent: {agent.upper()}")
        print(f"Target Channel: {channel_name}")
        print(f"{'='*60}\n")
        
        # Upload to Swarm Brain
        print("📁 Step 1: Uploading to Swarm Brain...")
        swarm_path = self.upload_to_swarm_brain(agent, file_path, category)
        
        # Post to Discord
        print(f"\n📤 Step 2: Posting to Discord ({channel_name})...")
        discord_success = self.post_to_discord(agent, swarm_path, is_major)
        
        # Summary
        print(f"\n{'='*60}")
        if discord_success:
            print("✅ DEVLOG POSTED SUCCESSFULLY!")
        else:
            print("⚠️ DEVLOG UPLOADED (Discord posting failed)")
        try:
            rel_path = swarm_path.relative_to(Path.cwd())
            print(f"   Swarm Brain: {rel_path}")
        except ValueError:
            print(f"   Swarm Brain: {swarm_path}")
        print(f"   Discord: {channel_name} {'(MAJOR UPDATE)' if is_major else ''}")
        print(f"{'='*60}\n")
        
        return discord_success


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Unified Devlog Poster - SSOT for Discord devlog posting"
    )
    
    parser.add_argument('--agent', '-a', required=True,
                       help='Agent posting the devlog (e.g., Agent-7)')
    parser.add_argument('--file', '-f', required=True,
                       help='Devlog file to post')
    parser.add_argument('--major', action='store_true',
                       help='Mark as MAJOR UPDATE (Captain posts to captain channel)')
    parser.add_argument('--category', '-c',
                       choices=['repository_analysis', 'mission_reports', 
                               'agent_sessions', 'system_events'],
                       help='Devlog category (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    poster = DevlogPoster()
    success = poster.post(args.agent, args.file, args.major, args.category)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

