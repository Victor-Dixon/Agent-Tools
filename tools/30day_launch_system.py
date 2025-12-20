#!/usr/bin/env python3
"""
30-Day Launch System Tracker & Automation
==========================================

Tracks and automates the "DaDudeKC 30-Day Launch System" program:
- Daily task tracking
- Progress monitoring
- Blog post automation
- DM script templates
- Weekly target tracking

Author: Agent-2 (Architecture & Design Specialist)
V2 Compliant: <400 lines
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.unified_blogging_automation import UnifiedBloggingAutomation
    HAS_BLOGGING = True
except ImportError:
    HAS_BLOGGING = False

# Program structure
PROGRAM_CONFIG = {
    "program": "DaDudeKC 30-Day Launch System",
    "goal": "Get first paying clients + repeatable lead flow",
    "start_date": None,  # Will be set on initialization
    "current_day": 0,
    "week_1_foundation": {
        "day_1": ["Pick niche + target buyer", "Write 1-sentence promise", "List 3 competitors"],
        "day_2": ["Create 3 packages", "Set pricing", "Write guarantee/benefit bullets"],
        "day_3": ["Build landing page copy", "Create intake form", "Create booking link"],
        "day_4": ["Website goes live", "Google Business Profile (if local)", "Set up email capture"],
        "day_5": ["Create 10 FAQ answers", "Turn into 5 posts + 5 short videos"],
        "day_6": ["Post 1 reel + 1 marketplace post", "DM 20 leads with script"],
        "day_7": ["Make 5 calls", "Book 2 consults", "Collect 1 deposit target"]
    },
    "week_2_leads": {
        "daily": ["1 short video", "10 DMs", "1 post", "1 follow-up block"],
        "day_8": ["Publish blog post #1", "Create 'Start Here' page"],
        "day_9": ["Offer audit for 3 people (public)", "Ask for referrals"],
        "day_10": ["Local outreach: 10 businesses", "Pitch collaboration"],
        "day_11": ["Publish blog post #2", "Create testimonial request template"],
        "day_12": ["Consult day", "Close 1 deal target"],
        "day_13": ["Deliver quick win for new client", "Get proof screenshot"],
        "day_14": ["Weekly review + adjust scripts + pricing if needed"]
    },
    "week_3_systemize": {
        "day_15": ["Create SOP: how to post blog", "How to respond to leads", "How to invoice"],
        "day_16": ["Create 3 email follow-ups", "Create 3 SMS follow-ups"],
        "day_17": ["Add FAQ section to site", "Add portfolio/proof section"],
        "day_18": ["Publish blog post #3", "Repurpose into 3 shorts"],
        "day_19": ["Cold outreach sprint: 50 DMs", "Book 5 calls target"],
        "day_20": ["Consult day", "Close 1 deal target"],
        "day_21": ["Weekly review + proof collection"]
    },
    "week_4_scale": {
        "day_22": ["Create a simple ad (optional)", "Or referral incentive"],
        "day_23": ["Publish blog post #4", "Add lead magnet download"],
        "day_24": ["Partner outreach: 10", "Set 2 collabs"],
        "day_25": ["Batch content: 7 posts + 7 shorts"],
        "day_26": ["Consult day", "Close 1 deal target"],
        "day_27": ["Client delivery day + testimonial capture"],
        "day_28": ["Optimize site CTA + headline"],
        "day_29": ["Pipeline cleanup + follow-ups"],
        "day_30": ["Results recap + next 30-day goals"]
    },
    "dm_script": {
        "opener": "Yo quick question—what do you do + how are you currently getting customers?",
        "diagnose": "What have you tried? What's working even a little?",
        "pitch": "I can package this into 3 tiers + build your site + give you a 30-day play to get your first paying clients.",
        "close": "Want me to draft your packages today? I'll send a quick blueprint."
    },
    "tracking": {
        "targets_weekly": {"dms": 70, "calls": 10, "consults": 5, "deposits": 2},
        "actuals": {
            "dms": 0,
            "calls": 0,
            "consults": 0,
            "deposits": 0
        },
        "blog_posts": {
            "day_8": {"published": False, "title": None, "content": None},
            "day_11": {"published": False, "title": None, "content": None},
            "day_18": {"published": False, "title": None, "content": None},
            "day_23": {"published": False, "title": None, "content": None}
        }
    }
}


class LaunchSystemTracker:
    """Tracks and manages the 30-day launch system."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize tracker."""
        self.config_path = config_path or Path(
            ".deploy_credentials/30day_launch_tracker.json")
        self.config = self.load_config()
        self.blogging = UnifiedBloggingAutomation() if HAS_BLOGGING else None

    def load_config(self) -> Dict[str, Any]:
        """Load or create program configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Initialize if not properly set
                    if not config.get("start_date") or config.get("current_day", 0) == 0:
                        config["start_date"] = datetime.now().isoformat()
                        config["current_day"] = 1
                        self.save_config(config)
                    return config
            except Exception as e:
                print(f"⚠️  Error loading config: {e}, creating new one")

        # Initialize new program
        config = PROGRAM_CONFIG.copy()
        config["start_date"] = datetime.now().isoformat()
        config["current_day"] = 1
        self.save_config(config)
        return config

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration."""
        config = config or self.config
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving config: {e}")

    def get_current_day_tasks(self) -> List[str]:
        """Get tasks for current day."""
        day = self.config.get("current_day", 1)

        if day <= 7:
            return self.config["week_1_foundation"].get(f"day_{day}", [])
        elif day <= 14:
            tasks = self.config["week_2_leads"]["daily"].copy()
            tasks.extend(self.config["week_2_leads"].get(f"day_{day}", []))
            return tasks
        elif day <= 21:
            return self.config["week_3_systemize"].get(f"day_{day}", [])
        elif day <= 30:
            return self.config["week_4_scale"].get(f"day_{day}", [])

        return []

    def get_dm_script(self) -> Dict[str, str]:
        """Get DM script templates."""
        return self.config.get("dm_script", {})

    def update_progress(self, metric: str, value: int) -> None:
        """Update tracking metrics."""
        if metric in self.config["tracking"]["actuals"]:
            self.config["tracking"]["actuals"][metric] += value
            self.save_config()

    def get_progress_report(self) -> Dict[str, Any]:
        """Get progress report."""
        day = self.config.get("current_day", 1)
        week = ((day - 1) // 7) + 1
        targets = self.config["tracking"]["targets_weekly"]
        actuals = self.config["tracking"]["actuals"]

        return {
            "day": day,
            "week": week,
            "targets": targets,
            "actuals": actuals,
            "progress": {
                "dms": f"{actuals['dms']}/{targets['dms'] * week}",
                "calls": f"{actuals['calls']}/{targets['calls'] * week}",
                "consults": f"{actuals['consults']}/{targets['consults'] * week}",
                "deposits": f"{actuals['deposits']}/{targets['deposits'] * week}"
            }
        }

    def publish_blog_post(self, day: int, title: str, content: str, site_id: str = "crosbyultimateevents.com") -> Dict[str, Any]:
        """Publish blog post for scheduled day."""
        if not self.blogging:
            return {"success": False, "error": "Blogging automation not available"}

        blog_key = f"day_{day}"
        if blog_key not in self.config["tracking"]["blog_posts"]:
            return {"success": False, "error": f"Day {day} is not a scheduled blog post day"}

        result = self.blogging.publish_to_site(
            site_id=site_id,
            title=title,
            content=content,
            status="publish"
        )

        if result.get("success"):
            self.config["tracking"]["blog_posts"][blog_key] = {
                "published": True,
                "title": title,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "post_id": result.get("post_id"),
                "link": result.get("link"),
                "published_at": datetime.now().isoformat()
            }
            self.save_config()

        return result

    def advance_day(self) -> None:
        """Advance to next day."""
        current = self.config.get("current_day", 1)
        if current < 30:
            self.config["current_day"] = current + 1
            self.save_config()

    def print_daily_tasks(self) -> None:
        """Print current day tasks."""
        day = self.config.get("current_day", 1)
        tasks = self.get_current_day_tasks()

        print(f"\n{'='*60}")
        print(f"📅 DAY {day} TASKS")
        print(f"{'='*60}\n")

        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task}")

        print()

    def print_progress(self) -> None:
        """Print progress report."""
        report = self.get_progress_report()

        print(f"\n{'='*60}")
        print(f"📊 WEEK {report['week']} PROGRESS (Day {report['day']})")
        print(f"{'='*60}\n")

        print("Targets vs Actuals:")
        for metric in ["dms", "calls", "consults", "deposits"]:
            target = report["targets"][metric] * report["week"]
            actual = report["actuals"][metric]
            status = "✅" if actual >= target else "⚠️"
            print(
                f"  {status} {metric.upper()}: {actual}/{target} ({report['progress'][metric]})")

        print()


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="30-Day Launch System Tracker")
    parser.add_argument("--init", action="store_true",
                        help="Initialize new program")
    parser.add_argument("--tasks", action="store_true",
                        help="Show today's tasks")
    parser.add_argument("--progress", action="store_true",
                        help="Show progress report")
    parser.add_argument("--dm-script", action="store_true",
                        help="Show DM script")
    parser.add_argument("--advance", action="store_true",
                        help="Advance to next day")
    parser.add_argument(
        "--update", help="Update metric (format: metric:value, e.g., dms:10)")
    parser.add_argument("--publish-blog", nargs=3, metavar=("DAY", "TITLE", "CONTENT_FILE"),
                        help="Publish blog post for scheduled day")
    parser.add_argument(
        "--site", default="crosbyultimateevents.com", help="Site ID for blog posts")

    args = parser.parse_args()

    tracker = LaunchSystemTracker()

    if args.init:
        print("✅ Program initialized!")
        print(f"   Start date: {tracker.config.get('start_date')}")
        print(f"   Current day: {tracker.config.get('current_day')}")
        return 0

    if args.tasks:
        tracker.print_daily_tasks()
        return 0

    if args.progress:
        tracker.print_progress()
        return 0

    if args.dm_script:
        script = tracker.get_dm_script()
        print("\n" + "="*60)
        print("💬 DM SCRIPT TEMPLATE")
        print("="*60 + "\n")
        print(f"Opener: {script.get('opener')}\n")
        print(f"Diagnose: {script.get('diagnose')}\n")
        print(f"Pitch: {script.get('pitch')}\n")
        print(f"Close: {script.get('close')}\n")
        return 0

    if args.advance:
        tracker.advance_day()
        print(f"✅ Advanced to day {tracker.config.get('current_day')}")
        return 0

    if args.update:
        try:
            metric, value = args.update.split(":")
            tracker.update_progress(metric, int(value))
            print(f"✅ Updated {metric} by {value}")
        except ValueError:
            print("❌ Invalid format. Use: --update metric:value")
            return 1

    if args.publish_blog:
        day, title, content_file = args.publish_blog
        try:
            day_num = int(day)
            content_path = Path(content_file)
            if not content_path.exists():
                print(f"❌ Content file not found: {content_file}")
                return 1

            content = content_path.read_text(encoding='utf-8')
            result = tracker.publish_blog_post(
                day_num, title, content, args.site)

            if result.get("success"):
                print(f"✅ Blog post published!")
                print(f"   Post ID: {result.get('post_id')}")
                print(f"   Link: {result.get('link')}")
            else:
                print(f"❌ Failed: {result.get('error')}")
                return 1
        except ValueError:
            print("❌ Invalid day number")
            return 1

    # Default: show tasks and progress
    if len(sys.argv) == 1:
        tracker.print_daily_tasks()
        tracker.print_progress()

    return 0


if __name__ == "__main__":
    sys.exit(main())
