#!/usr/bin/env python3
"""
Devlog Manager - Backward Compatibility Wrapper
================================================

⚠️  DEPRECATED: This module is maintained for backward compatibility.
    New code should use devlog_poster.py (SSOT) instead.

This module redirects to devlog_poster.py for compatibility.
All functionality has been consolidated into devlog_poster.py.

Routing Rules:
- Agents (1-3, 5-8): Always post to their own devlog channels
- Captain (Agent-4): Regular posts → own channel, Major updates → captain channel

Author: Agent-7 (Web Development Specialist)
Date: 2025-11-26
"""

import os
import sys
import re
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path BEFORE imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import requests
from dotenv import load_dotenv, dotenv_values
from src.core.config.timeout_constants import TimeoutConstants

# Load environment variables from .env file
# Use dotenv_values first (more lenient), then load_dotenv to merge into os.environ
try:
    # Load using dotenv_values (handles parsing errors better)
    env_vars = dotenv_values(".env")
    # Merge into os.environ
    for key, value in env_vars.items():
        if value and key not in os.environ:
            os.environ[key] = value
except Exception as e:
    # Fallback to load_dotenv if dotenv_values fails
    load_dotenv()


class DevlogManager:
    """Manages devlog uploads to Swarm Brain and Discord"""

    def __init__(self):
        self.swarm_brain_path = Path("swarm_brain/devlogs")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")

        # Agent to Discord channel mapping
        # Support multiple naming conventions:
        # - DISCORD_WEBHOOK_AGENT_X (PRIORITY - webhook URL)
        # - DISCORD_AGENTX_WEBHOOK (alternative webhook URL format)
        # - DISCORD_CHANNEL_AGENT_X is channel ID, NOT webhook URL (ignore)
        self.agent_channels = {
            "agent-1": (os.getenv("DISCORD_WEBHOOK_AGENT_1") or
                        os.getenv("DISCORD_AGENT1_WEBHOOK")),
            "agent-2": (os.getenv("DISCORD_WEBHOOK_AGENT_2") or
                        os.getenv("DISCORD_AGENT2_WEBHOOK")),
            "agent-3": (os.getenv("DISCORD_WEBHOOK_AGENT_3") or
                        os.getenv("DISCORD_AGENT3_WEBHOOK")),
            "agent-4": (os.getenv("DISCORD_WEBHOOK_AGENT_4") or
                        os.getenv("DISCORD_CAPTAIN_WEBHOOK") or
                        os.getenv("DISCORD_AGENT4_WEBHOOK")),
            "agent-5": (os.getenv("DISCORD_WEBHOOK_AGENT_5") or
                        os.getenv("DISCORD_AGENT5_WEBHOOK")),
            "agent-6": (os.getenv("DISCORD_WEBHOOK_AGENT_6") or
                        os.getenv("DISCORD_AGENT6_WEBHOOK")),
            "agent-7": (os.getenv("DISCORD_WEBHOOK_AGENT_7") or
                        os.getenv("DISCORD_AGENT7_WEBHOOK")),
            "agent-8": (os.getenv("DISCORD_WEBHOOK_AGENT_8") or
                        os.getenv("DISCORD_AGENT8_WEBHOOK")),
            # Also support Agent-X format (capital A, dash)
            "Agent-1": (os.getenv("DISCORD_WEBHOOK_AGENT_1") or
                        os.getenv("DISCORD_AGENT1_WEBHOOK")),
            "Agent-2": (os.getenv("DISCORD_WEBHOOK_AGENT_2") or
                        os.getenv("DISCORD_AGENT2_WEBHOOK")),
            "Agent-3": (os.getenv("DISCORD_WEBHOOK_AGENT_3") or
                        os.getenv("DISCORD_AGENT3_WEBHOOK")),
            "Agent-4": (os.getenv("DISCORD_WEBHOOK_AGENT_4") or
                        os.getenv("DISCORD_CAPTAIN_WEBHOOK") or
                        os.getenv("DISCORD_AGENT4_WEBHOOK")),
            "Agent-5": (os.getenv("DISCORD_WEBHOOK_AGENT_5") or
                        os.getenv("DISCORD_AGENT5_WEBHOOK")),
            "Agent-6": (os.getenv("DISCORD_WEBHOOK_AGENT_6") or
                        os.getenv("DISCORD_AGENT6_WEBHOOK")),
            "Agent-7": (os.getenv("DISCORD_WEBHOOK_AGENT_7") or
                        os.getenv("DISCORD_AGENT7_WEBHOOK")),
            "Agent-8": (os.getenv("DISCORD_WEBHOOK_AGENT_8") or
                        os.getenv("DISCORD_AGENT8_WEBHOOK")),
        }

    def categorize_devlog(self, filename: str, content: str) -> str:
        """Auto-categorize devlog based on content/filename"""
        filename_lower = filename.lower()
        content_lower = content.lower()

        # Repository analysis
        if 'repo' in filename_lower or 'repository' in content_lower:
            return 'repository_analysis'

        # Mission reports
        if 'mission' in filename_lower or 'complete' in filename_lower:
            return 'mission_reports'

        # Agent sessions
        if 'session' in filename_lower or 'cycle' in filename_lower:
            return 'agent_sessions'

        # System events
        if any(word in content_lower for word in ['debate', 'swarm', 'decision', 'vote']):
            return 'system_events'

        # Default
        return 'agent_sessions'

    def upload_to_swarm_brain(
        self,
        agent: str,
        file_path: Path,
        category: Optional[str] = None
    ) -> Path:
        """Upload devlog to Swarm Brain"""

        # Read content
        content = file_path.read_text(encoding='utf-8')

        # Auto-categorize if not specified
        if not category:
            category = self.categorize_devlog(file_path.name, content)

        # Create category directory
        category_path = self.swarm_brain_path / category
        category_path.mkdir(parents=True, exist_ok=True)

        # Generate filename with agent prefix if not present
        filename = file_path.name
        if not filename.startswith(agent.replace('-', '')):
            timestamp = datetime.now().strftime("%Y-%m-%d")
            filename = f"{timestamp}_{agent}_{filename}"

        # Upload
        target_path = category_path / filename
        target_path.write_text(content, encoding='utf-8')

        try:
            rel_path = target_path.relative_to(Path.cwd())
            print(f"✅ Uploaded to Swarm Brain: {rel_path}")
        except ValueError:
            print(f"✅ Uploaded to Swarm Brain: {target_path}")
        return target_path

    def post_to_discord(
        self,
        agent: str,
        file_path: Path,
        is_major: bool = False
    ) -> bool:
        """
        Post devlog to appropriate Discord channel.
        
        Routing Rules:
        - Agents (1-3, 5-8): Always post to their own devlog channels
        - Captain (Agent-4): Regular posts → own channel, Major updates → captain channel
        """

        # Normalize agent ID (handle both "agent-1" and "Agent-1" formats)
        agent_normalized = agent.lower() if agent.startswith("agent-") else agent
        agent_capitalized = agent if agent.startswith(
            "Agent-") else f"Agent-{agent.split('-')[-1]}" if '-' in agent else agent
        
        # Determine target channel based on routing rules
        is_captain = agent_normalized == "agent-4"
        target_agent = agent  # Default: post to agent's own channel
        
        # Routing: Captain's major updates go to captain channel
        # All other cases: agent's own channel
        if is_captain and is_major:
            # Captain major update → use captain webhook (already in agent_channels)
            target_agent = agent
        else:
            # Regular post → agent's own channel
            target_agent = agent

        # Get webhook for target agent (try both formats)
        webhook_url = self.agent_channels.get(target_agent) or self.agent_channels.get(
            agent_normalized) or self.agent_channels.get(agent_capitalized)

        if not webhook_url:
            print(f"❌ ERROR: No Discord webhook configured for {agent}")
            print(f"   Checked environment variables (in priority order):")
            print(f"   1. DISCORD_WEBHOOK_AGENT_X (webhook URL)")
            print(f"   2. DISCORD_AGENTX_WEBHOOK (alternative webhook URL)")
            print(f"   ⚠️ NOTE: DISCORD_CHANNEL_AGENT_X is channel ID, not webhook URL")
            print(
                f"   ⚠️ NOT falling back to general webhook (would post to wrong channel)")
            return False

        # Read content
        content = file_path.read_text(encoding='utf-8')

        # Check for Mermaid diagrams and convert if needed
        try:
            # Try V2 Compliance import first (tools_v2/utils/)
            # Add parent directory to path if needed
            import sys
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))

            try:
                from tools_v2.utils.discord_mermaid_renderer import DiscordMermaidRenderer
            except ImportError:
                # Fallback to tools/ if tools_v2 not available
                from tools.discord_mermaid_renderer import DiscordMermaidRenderer

            renderer = DiscordMermaidRenderer()
            if renderer.extract_mermaid_diagrams(content):
                print("🔍 Detected Mermaid diagrams - converting to images...")
                return renderer.post_to_discord_with_mermaid(
                    content,
                    webhook_url,
                    username=f"{agent.upper()} Devlog Bot",
                    temp_dir=Path("temp/discord_images")
                )
        except (ImportError, Exception) as e:
            # Mermaid renderer not available, continue with normal posting
            print(f"⚠️ Mermaid renderer not available: {e}")

        # Prepare message with smart chunking
        title = f"{'🚨 MAJOR UPDATE' if is_major else '📋 Devlog'}: {file_path.name}"

        # Smart chunking for long content
        DISCORD_CHAR_LIMIT = 2000
        SAFE_CHUNK_SIZE = 1800  # Leave buffer for embed description

        def smart_chunk_content(text: str, max_size: int = SAFE_CHUNK_SIZE) -> list[str]:
            """Split content into chunks, preserving markdown structure."""
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

        # Check if chunking needed
        if len(content) > SAFE_CHUNK_SIZE:
            # Use first chunk for embed, post rest as separate messages
            chunks = smart_chunk_content(content, SAFE_CHUNK_SIZE)
            preview = chunks[0] + "\n\n*(Continued in next message...)*"
            remaining_chunks = chunks[1:]
        else:
            preview = content
            remaining_chunks = []

        # Create embed
        embed = {
            "title": title,
            "description": preview,
            "color": 0xFF0000 if is_major else 0x3498DB,  # Red for major, blue for normal
            "fields": [
                {"name": "Agent", "value": agent.upper(), "inline": True},
                {"name": "Category", "value": self.categorize_devlog(
                    file_path.name, content), "inline": True},
                {"name": "Timestamp", "value": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"), "inline": True},
            ],
            "footer": {"text": "Swarm Brain Devlog System"}
        }

        payload = {
            "embeds": [embed],
            "username": f"{agent.upper()} Devlog Bot"
        }

        # Post embed (first chunk)
        try:
            response = requests.post(webhook_url, json=payload, timeout=TimeoutConstants.HTTP_SHORT)
            if response.status_code == 204:
                print(f"✅ Posted to Discord: #{agent}-devlogs")

                # Log post for status monitor integration
                self._log_devlog_post(agent, file_path, is_major, success=True)
            else:
                print(f"❌ Discord error: {response.status_code}")
                self._log_devlog_post(
                    agent, file_path, is_major, success=False)
                return False
        except Exception as e:
            print(f"❌ Failed to post to Discord: {e}")
            self._log_devlog_post(agent, file_path, is_major, success=False)
            return False

        # Post remaining chunks as beautiful embeds
        if remaining_chunks:
            import time
            total_parts = len(remaining_chunks) + 1
            print(f"📦 Posting {len(remaining_chunks)} additional chunks as embeds...")

            for i, chunk in enumerate(remaining_chunks, 2):
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
                    response = requests.post(
                        webhook_url, json=chunk_payload, timeout=TimeoutConstants.HTTP_SHORT)
                    if response.status_code == 204:
                        print(f"✅ Posted chunk {i}/{total_parts} as embed")
                    else:
                        print(
                            f"❌ Discord error for chunk {i}: {response.status_code}")
                        return False

                    # Rate limit: 1 second delay between chunks
                    if i <= total_parts:
                        time.sleep(1)

                except Exception as e:
                    print(f"❌ Failed to post chunk {i} to Discord: {e}")
                    return False

        return True

    def _log_devlog_post(self, agent: str, file_path: Path, is_major: bool, success: bool):
        """Log devlog post for status monitor integration."""
        import json
        import time

        log_file = Path("logs/devlog_posts.json")
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Read existing logs
        posts = []
        if log_file.exists():
            try:
                posts = json.loads(log_file.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, Exception):
                posts = []

        # Add new post entry
        post_entry = {
            "agent_id": agent.lower(),
            "filename": file_path.name,
            "file_path": str(file_path),
            "timestamp": int(time.time()),
            "is_major": is_major,
            "success": success,
            "channel": f"#{agent.lower()}-devlogs"
        }

        posts.append(post_entry)

        # Keep only last 1000 entries
        if len(posts) > 1000:
            posts = posts[-1000:]

        # Write back
        log_file.write_text(json.dumps(posts, indent=2), encoding='utf-8')

    def update_index(self):
        """Update devlog index"""
        index_path = self.swarm_brain_path / "DEVLOG_INDEX.md"

        # Count devlogs by category
        stats = {}
        for category in ['repository_analysis', 'mission_reports', 'agent_sessions', 'system_events']:
            category_path = self.swarm_brain_path / category
            if category_path.exists():
                count = len(list(category_path.glob("*.md")))
                stats[category] = count

        # Update index header
        content = f"""# 📚 SWARM BRAIN DEVLOG INDEX

**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**Total Devlogs:** {sum(stats.values())}  
**Auto-Updated:** Via Devlog Manager

---

## 📊 DEVLOG STATISTICS

**By Category:**
- Repository Analysis: {stats.get('repository_analysis', 0)} devlogs
- Mission Reports: {stats.get('mission_reports', 0)} devlogs
- Agent Sessions: {stats.get('agent_sessions', 0)} devlogs
- System Events: {stats.get('system_events', 0)} devlogs

---

*Index auto-generated by Devlog Manager*  
*All devlogs automatically posted to agent Discord channels*

"""

        index_path.write_text(content, encoding='utf-8')
        print(f"✅ Updated devlog index")

    def post(
        self,
        agent: str,
        file_path: str,
        is_major: bool = False,
        category: Optional[str] = None
    ):
        """Main post function - uploads to Swarm Brain + posts to Discord"""

        file_path = Path(file_path)

        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False

        print(f"\n{'='*60}")
        print(
            f"📤 DEVLOG MANAGER - {'MAJOR UPDATE' if is_major else 'Standard Post'}")
        print(f"{'='*60}\n")

        # Step 1: Upload to Swarm Brain
        print("📁 Step 1: Uploading to Swarm Brain...")
        swarm_path = self.upload_to_swarm_brain(agent, file_path, category)

        # Step 2: Post to Discord
        print("\n📤 Step 2: Posting to Discord...")
        discord_success = self.post_to_discord(agent, swarm_path, is_major)

        # Step 3: Compress and archive original file (if Discord post succeeded)
        if discord_success and file_path.exists():
            print("\n📦 Step 3: Compressing and archiving devlog...")
            try:
                import sys
                # Add tools directory to path for import
                tools_dir = Path(__file__).parent
                if str(tools_dir) not in sys.path:
                    sys.path.insert(0, str(tools_dir))
                from devlog_compressor import compress_and_archive
                archive_path = compress_and_archive(
                    file_path,
                    agent=agent,
                    delete_original=True
                )
                print(f"✅ Archived to: {archive_path}")
            except Exception as e:
                print(f"⚠️ Archive failed (devlog not deleted): {e}")

        # Step 4: Update index
        print("\n📊 Step 4: Updating index...")
        self.update_index()

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
        print(
            f"   Discord: #{agent}-devlogs {'(MAJOR UPDATE)' if is_major else ''}")
        print(f"{'='*60}\n")

        return True


def main():
    """CLI entry point - redirects to devlog_poster.py"""
    import subprocess
    
    parser = argparse.ArgumentParser(
        description="Devlog Manager - Backward Compatibility Wrapper (uses devlog_poster.py)"
    )

    parser.add_argument(
        'action',
        choices=['post'],
        help='Action to perform'
    )

    parser.add_argument(
        '--agent', '-a',
        required=True,
        help='Agent posting the devlog (e.g., agent-5 or Agent-5)'
    )

    parser.add_argument(
        '--file', '-f',
        required=True,
        help='Devlog file to post'
    )

    parser.add_argument(
        '--major',
        action='store_true',
        help='Mark as MAJOR UPDATE (Captain posts to captain channel)'
    )

    parser.add_argument(
        '--category', '-c',
        choices=['repository_analysis', 'mission_reports',
                 'agent_sessions', 'system_events'],
        help='Devlog category (auto-detected if not specified)'
    )

    args = parser.parse_args()
    
    # Redirect to devlog_poster.py (SSOT)
    print("⚠️  NOTE: devlog_manager.py is a compatibility wrapper.")
    print("   Using devlog_poster.py (SSOT)...\n")
    
    devlog_poster_path = Path(__file__).parent / "devlog_poster.py"
    cmd = [sys.executable, str(devlog_poster_path),
           "--agent", args.agent,
           "--file", args.file]
    
    if args.major:
        cmd.append("--major")
    if args.category:
        cmd.extend(["--category", args.category])
    
    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: devlog_poster.py failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
