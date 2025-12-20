#!/usr/bin/env python3
"""
Post Cycle Accomplishments report to Discord.

Generates the latest cycle accomplishments report and posts it to a Discord channel.
Intended to be run on a scheduler (e.g., Task Scheduler) or manually.

Usage:
    python tools/post_cycle_report_to_discord.py
    python tools/post_cycle_report_to_discord.py --channel 1394677708167970917
    python tools/post_cycle_report_to_discord.py --no-generate  # reuse latest report

Requirements:
    - DISCORD_BOT_TOKEN set in environment or .env
    - discord.py and python-dotenv installed
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Tuple, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

try:
    import discord
except ImportError:
    print("❌ discord.py not installed. Run: pip install discord.py")
    sys.exit(1)

try:
    from tools.generate_cycle_accomplishments_report import (
        generate_cycle_report,
    )
except Exception as exc:  # pragma: no cover - defensive import
    print(f"❌ Failed to import report generator: {exc}")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("cycle_report_poster")

DEFAULT_CHANNEL_ID = 1394677708167970917


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and post cycle accomplishments report to Discord."
    )
    parser.add_argument(
        "--channel",
        type=int,
        default=DEFAULT_CHANNEL_ID,
        help=f"Discord channel ID to post to (default: {DEFAULT_CHANNEL_ID})",
    )
    parser.add_argument(
        "--no-generate",
        action="store_true",
        help="Do not generate a new report; post the most recent file in docs/archive/cycles/",
    )
    return parser.parse_args()


def find_latest_report() -> Path | None:
    archive_dir = project_root / "docs" / "archive" / "cycles"
    if not archive_dir.exists():
        return None
    reports = sorted(archive_dir.glob("CYCLE_ACCOMPLISHMENTS_*.md"))
    return reports[-1] if reports else None


def find_today_report() -> Path | None:
    """Find a report generated today (by date prefix)."""
    archive_dir = project_root / "docs" / "archive" / "cycles"
    if not archive_dir.exists():
        return None
    today_prefix = Path(
        f"CYCLE_ACCOMPLISHMENTS_{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}"
    )
    candidates = sorted(archive_dir.glob(f"{today_prefix}*.md"))
    return candidates[-1] if candidates else None


def get_report_path(skip_generate: bool) -> Path:
    if skip_generate:
        latest = find_latest_report()
        if not latest:
            raise FileNotFoundError("No existing report found to post.")
        logger.info(f"Using latest existing report: {latest}")
        return latest

    # Date guard: if today's report already exists, reuse it
    today = find_today_report()
    if today:
        logger.info(f"Today's report already exists, reusing: {today}")
        return today

    logger.info("Generating fresh cycle accomplishments report...")
    path = generate_cycle_report()
    logger.info(f"Report generated at: {path}")
    return path


def parse_summary(report_path: Path) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Extract date and summary stats from the markdown report."""
    date = None
    agents = None
    tasks = None
    achievements = None
    points = None

    # Derive date from filename if present
    stem = report_path.stem
    if "CYCLE_ACCOMPLISHMENTS_" in stem:
        date = stem.replace("CYCLE_ACCOMPLISHMENTS_", "").split("_")[0]

    try:
        lines = report_path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if "**Generated**" in line and not date:
                # e.g., **Generated**: 2025-12-08 16:56:45
                parts = line.split(": ", 1)
                if len(parts) == 2:
                    date = parts[1].strip()
            if "Agents Active" in line:
                agents = line.split(":")[-1].strip()
            if "Total Completed Tasks" in line:
                tasks = line.split(":")[-1].strip()
            if "Total Achievements" in line:
                achievements = line.split(":")[-1].strip()
            if "Total Points Earned" in line:
                points = line.split(":")[-1].strip()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(f"Failed to parse summary from report: {exc}")

    return date, agents, tasks, achievements or points


class OneShotClient(discord.Client):
    """Minimal client to post one report then exit."""

    def __init__(self, *, channel_id: int, report_path: Path, **kwargs):
        # Need guilds intent to resolve channel by ID
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(intents=intents, **kwargs)
        self.channel_id = channel_id
        self.report_path = report_path
        self.logger = logging.getLogger("cycle_report_poster.client")

    async def close(self):
        """Ensure aiohttp connector closes cleanly."""
        try:
            await super().close()
        finally:
            if self.http and self.http._HTTPClient__session and not self.http._HTTPClient__session.closed:
                await self.http._HTTPClient__session.close()

    async def on_ready(self):
        try:
            channel = self.get_channel(self.channel_id)
            # If not cached, attempt to fetch
            if channel is None:
                try:
                    channel = await self.fetch_channel(self.channel_id)
                except Exception as exc:
                    self.logger.error(
                        f"Channel {self.channel_id} not found or not accessible (fetch failed): {exc}"
                    )
                    await self.close()
                    return

            date, agents, tasks, achievements = parse_summary(self.report_path)
            title = "📊 Cycle Accomplishments Report"
            desc_lines = []
            if date:
                desc_lines.append(f"Date: {date}")
            if agents:
                desc_lines.append(f"Agents: {agents}")
            if tasks:
                desc_lines.append(f"Completed Tasks: {tasks}")
            if achievements:
                desc_lines.append(f"Achievements: {achievements}")
            desc = "\n".join(desc_lines) if desc_lines else "Automated cycle report."

            embed = discord.Embed(title=title, description=desc, color=discord.Color.blue())
            embed.set_footer(text="Attached: full markdown report")

            file = discord.File(str(self.report_path), filename=self.report_path.name)
            await channel.send(embed=embed, file=file)
            self.logger.info("✅ Report posted successfully.")
        except Exception as exc:  # pragma: no cover - runtime safety
            self.logger.error(f"Failed to post report: {exc}", exc_info=True)
        finally:
            await self.close()


def main():
    args = parse_args()
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN not set in environment or .env")
        sys.exit(1)

    try:
        report_path = get_report_path(skip_generate=args.no_generate)
    except Exception as exc:
        logger.error(f"Failed to prepare report: {exc}")
        sys.exit(1)

    client = OneShotClient(channel_id=args.channel, report_path=report_path)
    asyncio.run(client.start(token))


if __name__ == "__main__":
    main()

