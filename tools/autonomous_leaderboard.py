#!/usr/bin/env python3
"""
Autonomous Development Leaderboard
==================================

CLI tool to view and manage the autonomous development competition system.

Encourages proactive agent behavior through gamification while maintaining
cooperative swarm intelligence.

Author: Captain Agent-4
Usage: python tools/autonomous_leaderboard.py [--award] [--show]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse

from src.core.gamification.autonomous_competition_system import (
    AchievementType,
    get_competition_system,
)


def show_leaderboard(top_n: int = 8):
    """Display current leaderboard."""
    system = get_competition_system()
    leaderboard = system.get_leaderboard(top_n)

    print("\n" + "=" * 80)
    print("🎯 AUTONOMOUS DEVELOPMENT LEADERBOARD")
    print("   (Competition drives proactive excellence!)")
    print("=" * 80)
    print()

    if not leaderboard:
        print("📊 No scores yet. Start earning achievements!")
        print("    Proactive work = 1.5x points multiplier!")
        print()
        return

    medals = ["🥇", "🥈", "🥉", "⭐", "⭐", "⭐", "⭐", "⭐"]

    for i, score in enumerate(leaderboard):
        medal = medals[i] if i < len(medals) else "•"

        print(f"{medal} #{score.rank:2d} {score.agent_name:40s}")
        print(
            f"       Points: {score.total_points:,} | "
            f"Proactive: {score.proactive_count} | "
            f"Achievements: {len(score.achievements)}"
        )

        # Show recent achievements
        if score.achievements:
            recent = score.achievements[-3:]  # Last 3
            for ach in recent:
                print(f"         └─ {ach.title} (+{ach.points} pts)")
        print()

    print("=" * 80)
    print("💡 Proactive initiatives earn 1.5x points!")
    print("🎯 Quality work earns multipliers up to 2.0x!")
    print("🐝 WE ARE SWARM - Competition makes us stronger!")
    print("=" * 80)
    print()


def award_achievement_cli():
    """Interactive achievement award."""
    system = get_competition_system()

    print("\n🏆 AWARD ACHIEVEMENT")
    print("=" * 80)

    # Get inputs
    agent_id = input("Agent ID (e.g., Agent-5): ").strip()
    agent_name = input("Agent Name: ").strip()

    print("\nAchievement Types:")
    for i, atype in enumerate(AchievementType, 1):
        print(f"  {i}. {atype.value}")

    type_choice = int(input("Select type (1-8): ")) - 1
    achievement_type = list(AchievementType)[type_choice]

    title = input("Achievement Title: ").strip()
    description = input("Description: ").strip()
    points = int(input("Base Points: "))

    is_proactive = input("Is this proactive work? (y/n): ").lower() == "y"
    if is_proactive:
        points = system.calculate_proactive_bonus(points)
        print(f"  💡 Proactive bonus applied! {points} points total")

    mission_ref = input("Mission/Cycle reference (optional): ").strip() or None

    # Award achievement
    achievement = system.award_achievement(
        agent_id=agent_id,
        agent_name=agent_name,
        achievement_type=achievement_type,
        title=title,
        description=description,
        points=points,
        mission_ref=mission_ref,
    )

    print("\n✅ Achievement awarded!")
    print(f"   Agent: {agent_name}")
    print(f"   Points: {points}")
    print(f"   Total: {system.scores[agent_id].total_points:,} pts")
    print(f"   Rank: #{system.scores[agent_id].rank}")
    print()


def show_agent_details(agent_id: str):
    """Show detailed stats for specific agent."""
    system = get_competition_system()
    score = system.get_agent_score(agent_id)

    if not score:
        print(f"❌ Agent {agent_id} not found in leaderboard")
        return

    print("\n" + "=" * 80)
    print(f"🤖 {score.agent_name} (#{score.rank})")
    print("=" * 80)
    print()
    print(f"Total Points:     {score.total_points:,}")
    print(f"Achievements:     {len(score.achievements)}")
    print(f"Proactive Count:  {score.proactive_count}")
    print(f"Quality Score:    {score.quality_score:.2f}")
    print(f"Velocity Score:   {score.velocity_score:.2f}")
    print(f"Collaboration:    {score.collaboration_score:.2f}")
    print()

    if score.achievements:
        print("🏆 Recent Achievements:")
        for ach in score.achievements[-10:]:
            print(f"   • {ach.title} (+{ach.points} pts) - {ach.timestamp[:10]}")
            if ach.mission_ref:
                print(f"     Mission: {ach.mission_ref}")

    print("\n" + "=" * 80)
    print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Development Leaderboard - Encourage proactive excellence!"
    )
    parser.add_argument("--show", action="store_true", help="Show leaderboard")
    parser.add_argument("--award", action="store_true", help="Award achievement")
    parser.add_argument("--agent", help="Show specific agent details")
    parser.add_argument("--top", type=int, default=8, help="Number of top agents to show")

    args = parser.parse_args()

    if args.award:
        award_achievement_cli()
    elif args.agent:
        show_agent_details(args.agent)
    else:
        show_leaderboard(args.top)


if __name__ == "__main__":
    main()
