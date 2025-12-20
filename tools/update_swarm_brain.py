#!/usr/bin/env python3
"""
Swarm Brain Database Updater

Records insights, lessons learned, and recommendations into the swarm's collective
knowledge base for future agents to reference.

Usage:
    python tools/update_swarm_brain.py --insights "Your insight here"
    python tools/update_swarm_brain.py --lesson "Lesson learned" --category "autonomy"
    python tools/update_swarm_brain.py --recommendation "Do this next time"

Author: Agent-2 - Architecture & Design Specialist
Created: 2025-10-11
Purpose: Civilization-building knowledge persistence
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


class SwarmBrainUpdater:
    """Updates the swarm brain database with insights and learnings."""

    def __init__(self):
        self.brain_file = Path("runtime/swarm_brain.json")
        self.brain_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_brain()

    def _load_brain(self):
        """Load existing brain data or create new structure."""
        if self.brain_file.exists():
            with open(self.brain_file, encoding="utf-8") as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "insights": [],
            "lessons": [],
            "recommendations": [],
            "patterns": [],
            "statistics": {
                "total_insights": 0,
                "total_lessons": 0,
                "total_recommendations": 0,
                "total_patterns": 0,
            },
        }

    def add_insight(self, insight: str, agent: str = "Unknown", tags: list = None):
        """Add a new insight to the brain."""
        entry = {
            "id": len(self.data["insights"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "content": insight,
            "tags": tags or [],
            "category": "insight",
        }
        self.data["insights"].append(entry)
        self.data["statistics"]["total_insights"] += 1
        print(f"✅ Insight #{entry['id']} recorded by {agent}")

    def add_lesson(
        self, lesson: str, agent: str = "Unknown", category: str = "general", tags: list = None
    ):
        """Add a lesson learned to the brain."""
        entry = {
            "id": len(self.data["lessons"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "category": category,
            "content": lesson,
            "tags": tags or [],
            "type": "lesson",
        }
        self.data["lessons"].append(entry)
        self.data["statistics"]["total_lessons"] += 1
        print(f"✅ Lesson #{entry['id']} recorded by {agent} (category: {category})")

    def add_recommendation(
        self,
        recommendation: str,
        agent: str = "Unknown",
        priority: str = "normal",
        tags: list = None,
    ):
        """Add a recommendation for future agents."""
        entry = {
            "id": len(self.data["recommendations"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "priority": priority,
            "content": recommendation,
            "tags": tags or [],
            "status": "open",
            "type": "recommendation",
        }
        self.data["recommendations"].append(entry)
        self.data["statistics"]["total_recommendations"] += 1
        print(f"✅ Recommendation #{entry['id']} recorded by {agent} " f"(priority: {priority})")

    def add_pattern(
        self,
        name: str,
        description: str,
        agent: str = "Unknown",
        success_rate: str = "N/A",
        tags: list = None,
    ):
        """Add a proven pattern to the brain."""
        entry = {
            "id": len(self.data["patterns"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "name": name,
            "description": description,
            "success_rate": success_rate,
            "tags": tags or [],
            "type": "pattern",
        }
        self.data["patterns"].append(entry)
        self.data["statistics"]["total_patterns"] += 1
        print(f"✅ Pattern '{name}' recorded by {agent} " f"(success rate: {success_rate})")

    def save(self):
        """Save the brain data to disk."""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.brain_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Swarm brain updated: {self.brain_file}")
        print(
            f"📊 Statistics: {self.data['statistics']['total_insights']} "
            f"insights, {self.data['statistics']['total_lessons']} lessons, "
            f"{self.data['statistics']['total_recommendations']} recommendations, "
            f"{self.data['statistics']['total_patterns']} patterns"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Update the swarm brain database with insights and learnings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add an insight
  python tools/update_swarm_brain.py --insights "Entry #025 validates autonomy"
  
  # Add a lesson
  python tools/update_swarm_brain.py --lesson "Verify before claiming" \\
      --category "autonomy" --agent "Agent-2"
  
  # Add a recommendation
  python tools/update_swarm_brain.py --recommendation "Create batching system" \\
      --priority "high"
  
  # Add a pattern
  python tools/update_swarm_brain.py --pattern "Intelligent Verification" \\
      --pattern-desc "Check reality before claiming" --success-rate "100%"
  
  # Add multiple with tags
  python tools/update_swarm_brain.py --insights "Brotherhood perfected" \\
      --tags "entry-025,cooperation,brotherhood"
        """,
    )

    parser.add_argument("--insights", "-i", type=str, help="Insight to record in swarm brain")
    parser.add_argument("--lesson", "-l", type=str, help="Lesson learned to record")
    parser.add_argument(
        "--category",
        "-c",
        type=str,
        default="general",
        help="Category for lesson (default: general)",
    )
    parser.add_argument("--recommendation", "-r", type=str, help="Recommendation for future agents")
    parser.add_argument(
        "--priority",
        "-p",
        type=str,
        default="normal",
        choices=["low", "normal", "high", "critical"],
        help="Priority level (default: normal)",
    )
    parser.add_argument("--pattern", type=str, help="Pattern name to record")
    parser.add_argument("--pattern-desc", type=str, help="Pattern description")
    parser.add_argument(
        "--success-rate", type=str, default="N/A", help="Pattern success rate (default: N/A)"
    )
    parser.add_argument(
        "--agent",
        "-a",
        type=str,
        default="Unknown",
        help="Agent recording the entry (default: Unknown)",
    )
    parser.add_argument("--tags", "-t", type=str, help="Comma-separated tags for categorization")

    args = parser.parse_args()

    # Parse tags
    tags = []
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",")]

    # Initialize updater
    updater = SwarmBrainUpdater()

    # Check if any content was provided
    has_content = False

    # Add insight
    if args.insights:
        updater.add_insight(args.insights, agent=args.agent, tags=tags)
        has_content = True

    # Add lesson
    if args.lesson:
        updater.add_lesson(args.lesson, agent=args.agent, category=args.category, tags=tags)
        has_content = True

    # Add recommendation
    if args.recommendation:
        updater.add_recommendation(
            args.recommendation, agent=args.agent, priority=args.priority, tags=tags
        )
        has_content = True

    # Add pattern
    if args.pattern:
        if not args.pattern_desc:
            print("❌ Error: --pattern-desc required when using --pattern")
            return 1
        updater.add_pattern(
            args.pattern,
            args.pattern_desc,
            agent=args.agent,
            success_rate=args.success_rate,
            tags=tags,
        )
        has_content = True

    if not has_content:
        parser.print_help()
        print(
            "\n❌ Error: No content provided. Use --insights, --lesson, "
            "--recommendation, or --pattern"
        )
        return 1

    # Save brain
    updater.save()

    print("\n🐝 WE. ARE. SWARM. ⚡")
    print("Swarm brain updated successfully!")

    return 0


if __name__ == "__main__":
    exit(main())
