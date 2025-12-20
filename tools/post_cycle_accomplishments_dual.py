#!/usr/bin/env python3
"""
Post Cycle Accomplishments to Discord AND Website
==================================================

Automatically generates cycle accomplishments report, formats it with mobile-friendly template,
and posts to both Discord and weareswarm.online.

Usage:
    python tools/post_cycle_accomplishments_dual.py
    python tools/post_cycle_accomplishments_dual.py --cycle C-XXX
    python tools/post_cycle_accomplishments_dual.py --no-generate  # reuse latest report
    python tools/post_cycle_accomplishments_dual.py --discord-only  # skip website
    python tools/post_cycle_accomplishments_dual.py --website-only  # skip Discord

V2 Compliance | Author: Agent-7 (Web Development) | Date: 2025-12-14
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.generate_cycle_accomplishments_report import generate_cycle_report

try:
    from tools.unified_blogging_automation import UnifiedBloggingAutomation
    HAS_BLOGGING = True
except ImportError:
    HAS_BLOGGING = False
    logging.warning("unified_blogging_automation not available - website posting disabled")

try:
    import discord
    HAS_DISCORD = True
except ImportError:
    HAS_DISCORD = False
    logging.warning("discord.py not available - Discord posting disabled")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agent color palette
AGENT_COLORS = {
    "Agent-1": "#667eea",
    "Agent-2": "#764ba2",
    "Agent-3": "#4facfe",
    "Agent-4": "#f093fb",
    "Agent-5": "#43e97b",
    "Agent-6": "#fa709a",
    "Agent-7": "#f59e0b",
    "Agent-8": "#30cfd0",
}

DEFAULT_DISCORD_CHANNEL_ID = 1394677708167970917


def load_agent_status(agent_id: str) -> Optional[Dict[str, Any]]:
    """Load agent status.json file."""
    status_file = project_root / "agent_workspaces" / agent_id / "status.json"
    if not status_file.exists():
        return None
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load status for {agent_id}: {e}")
        return None


def format_cycle_accomplishments_blog(
    report_path: Path,
    cycle_id: Optional[str] = None
) -> str:
    """
    Format cycle accomplishments report as mobile-friendly blog post.
    
    Args:
        report_path: Path to cycle accomplishments markdown report
        cycle_id: Optional cycle identifier
    
    Returns:
        Formatted blog post HTML/markdown content
    """
    # Read report
    report_content = report_path.read_text(encoding='utf-8')
    lines = report_content.splitlines()
    
    # Parse report data
    agents_data = {}
    summary = {
        "active_agents": "N/A",
        "total_tasks": "0",
        "total_achievements": "0",
        "total_points": "0",
        "generated_date": datetime.now().strftime('%Y-%m-%d'),
    }
    
    current_agent = None
    current_section = None
    
    for line in lines:
        if "**Generated**" in line:
            parts = line.split(": ", 1)
            if len(parts) == 2:
                summary["generated_date"] = parts[1].strip()
        elif "**Cycle**" in line:
            parts = line.split(": ", 1)
            if len(parts) == 2 and not cycle_id:
                cycle_id = parts[1].strip()
        elif "Agents Active" in line:
            summary["active_agents"] = line.split(":")[-1].strip()
        elif "Total Completed Tasks" in line:
            summary["total_tasks"] = line.split(":")[-1].strip()
        elif "Total Achievements" in line:
            summary["total_achievements"] = line.split(":")[-1].strip()
        elif "Total Points Earned" in line:
            summary["total_points"] = line.split(":")[-1].strip().replace(",", "")
        elif line.startswith("### ") and "Agent-" in line:
            agent_match = line.split(" - ")
            if len(agent_match) >= 1:
                agent_id = agent_match[0].replace("### ", "").strip()
                agent_name = agent_match[1].strip() if len(agent_match) > 1 else ""
                current_agent = agent_id
                agents_data[agent_id] = {
                    "name": agent_name,
                    "completed_tasks": [],
                    "achievements": [],
                    "status": "",
                    "mission": "",
                }
        elif line.startswith("#### ") and current_agent:
            if "Completed Tasks" in line:
                current_section = "tasks"
            elif "Achievements" in line:
                current_section = "achievements"
        elif line.startswith("- ") and current_agent and current_section:
            task_text = line[2:].strip()
            if current_section == "tasks":
                agents_data[current_agent]["completed_tasks"].append(task_text)
            elif current_section == "achievements":
                agents_data[current_agent]["achievements"].append(task_text)
        elif "**Status**" in line and current_agent:
            agents_data[current_agent]["status"] = line.split(":")[-1].strip()
        elif "**Mission**" in line and current_agent:
            agents_data[current_agent]["mission"] = line.split(":")[-1].strip()
    
    # Load fresh data from status files for better accuracy
    for agent_id in agents_data.keys():
        status = load_agent_status(agent_id)
        if status:
            if not agents_data[agent_id]["status"]:
                agents_data[agent_id]["status"] = status.get("status", "Unknown")
            if not agents_data[agent_id]["mission"]:
                agents_data[agent_id]["mission"] = status.get("current_mission", "No mission")
    
    # Generate blog post
    cycle_display = cycle_id if cycle_id else summary["generated_date"]
    
    blog_lines = []
    blog_lines.append(f"# 🎉 Swarm Cycle Accomplishments - {cycle_display}")
    blog_lines.append("")
    blog_lines.append('<div style="max-width: 100%; margin: 0 auto; padding: 1rem; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif; line-height: 1.7; color: #333; box-sizing: border-box;">')
    blog_lines.append("")
    
    # Hero Section
    blog_lines.append('<!-- HERO SECTION - Mobile Optimized -->')
    blog_lines.append('<div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 2rem 1rem; border-radius: 12px; color: white; margin: 1rem 0; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">')
    blog_lines.append('<h1 style="color: white; margin: 0 0 0.75rem 0; font-size: clamp(1.75em, 5vw, 2.5em); font-weight: 700; line-height: 1.2;">🎉 Swarm Cycle Accomplishments</h1>')
    blog_lines.append(f'<p style="font-size: clamp(1.1em, 3vw, 1.3em); margin: 0; opacity: 0.95; font-weight: 300;">{cycle_display} - {summary["generated_date"]}</p>')
    blog_lines.append('</div>')
    blog_lines.append("")
    
    # Introduction
    blog_lines.append('<!-- INTRODUCTION -->')
    blog_lines.append('<p style="font-size: clamp(1em, 2.5vw, 1.1em); margin: 1.5rem 0;">Our autonomous agent swarm continues to deliver exceptional results. This cycle showcases the collaborative power of specialized AI agents working together to achieve meaningful progress across multiple domains.</p>')
    blog_lines.append("")
    
    # Summary Cards
    blog_lines.append('## 📊 Swarm Summary')
    blog_lines.append("")
    blog_lines.append('<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin: 1.5rem 0;">')
    blog_lines.append("")
    
    blog_lines.append('<div style="background: white; border: 2px solid #667eea; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">')
    blog_lines.append('<h3 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: clamp(1.1em, 3vw, 1.3em);">👥 Agents</h3>')
    blog_lines.append(f'<p style="margin: 0; font-size: clamp(1.5em, 4vw, 2em); font-weight: 700; color: #2d3748;">{summary["active_agents"]}</p>')
    blog_lines.append('</div>')
    blog_lines.append("")
    
    blog_lines.append('<div style="background: white; border: 2px solid #764ba2; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">')
    blog_lines.append('<h3 style="color: #764ba2; margin: 0 0 0.5rem 0; font-size: clamp(1.1em, 3vw, 1.3em);">✅ Tasks</h3>')
    blog_lines.append(f'<p style="margin: 0; font-size: clamp(1.5em, 4vw, 2em); font-weight: 700; color: #2d3748;">{summary["total_tasks"]}</p>')
    blog_lines.append('</div>')
    blog_lines.append("")
    
    blog_lines.append('<div style="background: white; border: 2px solid #f093fb; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">')
    blog_lines.append('<h3 style="color: #f093fb; margin: 0 0 0.5rem 0; font-size: clamp(1.1em, 3vw, 1.3em);">🏆 Achievements</h3>')
    blog_lines.append(f'<p style="margin: 0; font-size: clamp(1.5em, 4vw, 2em); font-weight: 700; color: #2d3748;">{summary["total_achievements"]}</p>')
    blog_lines.append('</div>')
    blog_lines.append("")
    
    blog_lines.append('<div style="background: white; border: 2px solid #4facfe; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">')
    blog_lines.append('<h3 style="color: #4facfe; margin: 0 0 0.5rem 0; font-size: clamp(1.1em, 3vw, 1.3em);">⭐ Points</h3>')
    blog_lines.append(f'<p style="margin: 0; font-size: clamp(1.5em, 4vw, 2em); font-weight: 700; color: #2d3748;">{summary["total_points"]}</p>')
    blog_lines.append('</div>')
    blog_lines.append("")
    
    blog_lines.append('</div>')
    blog_lines.append("")
    
    # Agent Accomplishments
    blog_lines.append("## 🤖 Agent Accomplishments")
    blog_lines.append("")
    
    # Get active agents (mode-aware)
    try:
        from src.core.agent_mode_manager import get_active_agents
        active_agents = get_active_agents()
    except Exception:
        active_agents = ["Agent-1", "Agent-2", "Agent-3", "Agent-4"]
    
    for agent_id in sorted(agents_data.keys()):
        # Only show active agents
        if agent_id not in active_agents:
            continue
            
        data = agents_data[agent_id]
        color = AGENT_COLORS.get(agent_id, "#667eea")
        
        blog_lines.append(f'### {agent_id} - {data["name"]}')
        blog_lines.append("")
        blog_lines.append(f'<div style="background: #f8f9fa; border-left: 4px solid {color}; padding: 1rem; margin: 1rem 0; border-radius: 8px;">')
        blog_lines.append("")
        blog_lines.append(f'<p style="margin: 0.5rem 0; font-weight: 600; color: #2d3748; font-size: clamp(0.95em, 2.5vw, 1.05em);"><strong>Status:</strong> {data["status"]} | <strong>Mission:</strong> {data["mission"]}</p>')
        blog_lines.append("")
        
        if data["completed_tasks"]:
            blog_lines.append("#### ✅ Completed Tasks")
            blog_lines.append("")
            for task in data["completed_tasks"][:10]:  # Limit to 10
                blog_lines.append(f"- {task}")
            if len(data["completed_tasks"]) > 10:
                blog_lines.append(f"- *... and {len(data['completed_tasks']) - 10} more*")
            blog_lines.append("")
        
        if data["achievements"]:
            blog_lines.append("#### 🏆 Achievements")
            blog_lines.append("")
            for achievement in data["achievements"]:
                blog_lines.append(f"- {achievement}")
            blog_lines.append("")
        
        blog_lines.append('</div>')
        blog_lines.append("")
    
    # Conclusion
    blog_lines.append("## Conclusion")
    blog_lines.append("")
    blog_lines.append('<div style="background: #f7fafc; border-left: 5px solid #2a5298; padding: 1.5rem; margin: 2rem 0; border-radius: 8px;">')
    blog_lines.append('<p style="font-size: clamp(1em, 2.5vw, 1.1em); margin: 0; line-height: 1.8; color: #2d3748;">Our swarm continues to demonstrate the power of collaborative AI. Through specialized expertise and coordinated execution, we\'re building something truly remarkable—one cycle at a time.</p>')
    blog_lines.append('</div>')
    blog_lines.append("")
    blog_lines.append('<p style="text-align: center; margin-top: 2rem; font-size: clamp(0.9em, 2vw, 1em); color: #666;">🐝 <strong>WE. ARE. SWARM. AUTONOMOUS. POWERFUL.</strong> ⚡🔥🚀</p>')
    blog_lines.append("")
    blog_lines.append('</div>')
    
    return "\n".join(blog_lines)


async def post_to_discord(report_path: Path, channel_id: int):
    """Post cycle report to Discord."""
    if not HAS_DISCORD:
        logger.error("Discord posting disabled - discord.py not available")
        return False
    
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN not set")
        return False
    
    class OneShotClient(discord.Client):
        def __init__(self, *, channel_id: int, report_path: Path, **kwargs):
            intents = discord.Intents.default()
            intents.guilds = True
            super().__init__(intents=intents, **kwargs)
            self.channel_id = channel_id
            self.report_path = report_path
        
        async def on_ready(self):
            try:
                channel = self.get_channel(self.channel_id)
                if channel is None:
                    channel = await self.fetch_channel(self.channel_id)
                
                date = datetime.now().strftime('%Y-%m-%d')
                embed = discord.Embed(
                    title="📊 Cycle Accomplishments Report",
                    description=f"Date: {date}\nAutomated cycle report posted to Discord and website.",
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Attached: full markdown report")
                
                file = discord.File(str(self.report_path), filename=self.report_path.name)
                await channel.send(embed=embed, file=file)
                logger.info("✅ Report posted to Discord successfully")
            except Exception as e:
                logger.error(f"Failed to post to Discord: {e}", exc_info=True)
            finally:
                await self.close()
    
    client = OneShotClient(channel_id=channel_id, report_path=report_path)
    await client.start(token)
    return True


def post_to_website(blog_content: str, cycle_id: Optional[str] = None) -> bool:
    """Post cycle accomplishments to weareswarm.online."""
    if not HAS_BLOGGING:
        logger.error("Website posting disabled - unified_blogging_automation not available")
        return False
    
    try:
        automation = UnifiedBloggingAutomation()
        site_id = "weareswarm.online"
        
        if site_id not in automation.clients:
            logger.error(f"Site '{site_id}' not found in config")
            return False
        
        title = f"🎉 Swarm Cycle Accomplishments - {cycle_id}" if cycle_id else f"🎉 Swarm Cycle Accomplishments - {datetime.now().strftime('%Y-%m-%d')}"
        excerpt = "Our autonomous agent swarm continues to deliver exceptional results through collaborative AI."
        
        result = automation.publish_to_site(
            site_id=site_id,
            title=title,
            content=blog_content,
            site_purpose="swarm",
            excerpt=excerpt,
            status="publish"
        )
        
        if result.get("success"):
            logger.info(f"✅ Posted to website: {result.get('link')}")
            return True
        else:
            logger.error(f"Failed to post to website: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"Error posting to website: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Post cycle accomplishments to Discord AND website"
    )
    parser.add_argument("--cycle", type=str, help="Cycle identifier (e.g., C-XXX)")
    parser.add_argument("--output", type=str, help="Output directory for report")
    parser.add_argument("--no-generate", action="store_true", help="Reuse latest report")
    parser.add_argument("--discord-only", action="store_true", help="Skip website posting")
    parser.add_argument("--website-only", action="store_true", help="Skip Discord posting")
    parser.add_argument("--channel", type=int, default=DEFAULT_DISCORD_CHANNEL_ID, help="Discord channel ID")
    
    args = parser.parse_args()
    
    # Generate or find report
    if args.no_generate:
        archive_dir = project_root / "docs" / "archive" / "cycles"
        reports = sorted(archive_dir.glob("CYCLE_ACCOMPLISHMENTS_*.md"))
        if not reports:
            logger.error("No existing report found. Run without --no-generate to create one.")
            return 1
        report_path = reports[-1]
        logger.info(f"Using existing report: {report_path}")
    else:
        output_dir = Path(args.output) if args.output else None
        report_path = generate_cycle_report(cycle_id=args.cycle, output_dir=output_dir)
    
    # Format for blog
    blog_content = format_cycle_accomplishments_blog(report_path, cycle_id=args.cycle)
    
    # Post to Discord
    discord_success = True
    if not args.website_only:
        if HAS_DISCORD:
            import asyncio
            asyncio.run(post_to_discord(report_path, args.channel))
        else:
            logger.warning("Skipping Discord - not available")
            discord_success = False
    
    # Post to website
    website_success = True
    if not args.discord_only:
        website_success = post_to_website(blog_content, cycle_id=args.cycle)
    
    # Summary
    if discord_success and website_success:
        logger.info("✅ Successfully posted to both Discord and website!")
        return 0
    elif discord_success or website_success:
        logger.warning("⚠️ Partial success - check logs")
        return 1
    else:
        logger.error("❌ Failed to post to both platforms")
        return 1


if __name__ == "__main__":
    sys.exit(main())


