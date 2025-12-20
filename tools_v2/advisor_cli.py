#!/usr/bin/env python3
"""
Intelligent Mission Advisor CLI - The Masterpiece Tool
======================================================

Command-line interface for the Intelligent Mission Advisor.
Every agent's personal AI copilot for mission intelligence.

Usage:
    # Get mission recommendation
    python tools_v2/advisor_cli.py --agent Agent-5 --recommend

    # Validate Captain's order
    python tools_v2/advisor_cli.py --agent Agent-5 --validate inbox/ORDER.md

    # Analyze swarm state
    python tools_v2/advisor_cli.py --agent Agent-5 --swarm

    # Get real-time guidance
    python tools_v2/advisor_cli.py --agent Agent-5 --guide refactoring

Author: Agent-5 (Business Intelligence & Team Beta Leader)
License: MIT
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools_v2.categories.intelligent_mission_advisor import get_mission_advisor


def main():
    parser = argparse.ArgumentParser(
        description="🧠 Intelligent Mission Advisor - Your AI Copilot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🧠 INTELLIGENT MISSION ADVISOR - THE MASTERPIECE TOOL
====================================================

Your personal AI copilot providing intelligent mission guidance.

EXAMPLES:
--------
# Get mission recommendation (what should I work on?)
python tools_v2/advisor_cli.py --agent Agent-5 --recommend

# Validate Captain's order (Pattern #1: verify before claiming!)
python tools_v2/advisor_cli.py --agent Agent-5 --validate inbox/EXECUTION_ORDER.md

# Analyze swarm state (what's everyone doing?)
python tools_v2/advisor_cli.py --agent Agent-5 --swarm

# Get real-time guidance during execution
python tools_v2/advisor_cli.py --agent Agent-5 --guide refactoring

# Get recommendation with specific context
python tools_v2/advisor_cli.py --agent Agent-5 --recommend --context analytics

LIKE THE MESSAGING SYSTEM REVOLUTIONIZED COMMUNICATION,
THIS TOOL REVOLUTIONIZES DECISION-MAKING! 🚀
""",
    )

    parser.add_argument("--agent", required=True, help="Agent ID (e.g., Agent-5)")

    # Main actions (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--recommend", action="store_true", help="Get mission recommendation")
    action_group.add_argument("--validate", metavar="ORDER_FILE", help="Validate Captain's order")
    action_group.add_argument("--swarm", action="store_true", help="Analyze swarm state")
    action_group.add_argument("--guide", metavar="STEP", help="Get real-time guidance")

    # Optional flags
    parser.add_argument(
        "--context", help="Task context filter (e.g., 'analytics', 'error handling')"
    )
    parser.add_argument("--no-roi", action="store_true", help="Don't prefer high-ROI tasks")
    parser.add_argument("--allow-duplication", action="store_true", help="Allow duplicate work")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        advisor = get_mission_advisor(args.agent)

        # Execute requested action
        if args.recommend:
            result = advisor.get_mission_recommendation(
                context=args.context,
                prefer_high_roi=not args.no_roi,
                avoid_duplication=not args.allow_duplication,
            )

            if args.json:
                print(json.dumps(result, indent=2))
            else:
                _print_recommendation(result)

        elif args.validate:
            result = advisor.validate_captain_order(args.validate)

            if args.json:
                print(json.dumps(result, indent=2))
            else:
                _print_validation(result)

        elif args.swarm:
            result = advisor.analyze_swarm_state()

            if args.json:
                print(json.dumps(result, indent=2))
            else:
                _print_swarm_analysis(result)

        elif args.guide:
            result = advisor.get_realtime_guidance(args.guide, {})

            if args.json:
                print(json.dumps({"guidance": result, "step": args.guide}, indent=2))
            else:
                print(f"\n💡 GUIDANCE FOR {args.guide.upper()}:")
                print(f"   {result}\n")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}\n", file=sys.stderr)
        return 1


def _print_recommendation(result: dict):
    """Print mission recommendation in human-readable format."""
    print("\n" + "=" * 70)
    print("🧠 INTELLIGENT MISSION RECOMMENDATION")
    print("=" * 70)

    if result.get("recommended_task"):
        task = result["recommended_task"]
        print("\n📋 RECOMMENDED TASK:")
        print(f"   File: {task.get('file', 'Unknown')}")
        print(f"   Type: {task.get('type', 'Unknown')}")
        print(f"   ROI: {task.get('roi', 0):.2f}")
        print(f"   Points: {task.get('points', 0)}")
        print(f"   Complexity: {task.get('complexity', 0):.1f}")
        print(f"   Specialty Match: {task.get('specialty_match', 0):.0%}")

        print("\n✅ VERIFICATION:")
        print(f"   Status: {result.get('verification_status', 'Unknown')}")
        if result.get("verification_details"):
            for check in result["verification_details"].get("checks_performed", []):
                print(f"   - {check}")

        print("\n🎯 INTELLIGENT BRIEFING:")
        print(result.get("intelligent_briefing", ""))

        if result.get("relevant_patterns"):
            print("\n📚 RELEVANT PATTERNS:")
            for pattern in result["relevant_patterns"]:
                print(f"   - {pattern}")

        if result.get("execution_guidance"):
            print("\n🚀 EXECUTION GUIDANCE:")
            for step in result["execution_guidance"]:
                print(f"   {step}")

        print("\n📊 METRICS:")
        print(f"   Success Probability: {result.get('success_probability', 0):.0%}")
        print(f"   Estimated Points: {result.get('estimated_points', 0)}")

        if result.get("risk_factors"):
            print("\n⚠️ RISK FACTORS:")
            for risk in result["risk_factors"]:
                print(f"   - {risk}")
    else:
        print("\n❌ NO SUITABLE TASKS FOUND")
        if result.get("suggestions"):
            print("\n💡 SUGGESTIONS:")
            for suggestion in result["suggestions"]:
                print(f"   - {suggestion}")

    print("\n" + "=" * 70 + "\n")


def _print_validation(result: dict):
    """Print order validation in human-readable format."""
    print("\n" + "=" * 70)
    print("🛡️ CAPTAIN ORDER VALIDATION")
    print("=" * 70)

    if result.get("validated"):
        print("\n✅ ORDER VALIDATED - SAFE TO EXECUTE!")
        print(f"   Recommendation: {result.get('recommendation', 'EXECUTE')}")
        print(f"   Message: {result.get('message', '')}")
    else:
        print("\n⚠️ ORDER VALIDATION FAILED!")
        print(f"   Issue: {result.get('issue', 'Unknown')}")
        print(f"   Recommendation: {result.get('recommendation', 'REVIEW')}")

    print("\n📋 CHECKS:")
    print(f"   Order exists: {result.get('order_exists', False)}")
    print(f"   Task file exists: {result.get('task_file_exists', False)}")
    print(f"   Task available: {result.get('task_available', False)}")

    if result.get("conflicts"):
        print("\n⚠️ CONFLICTS DETECTED:")
        for conflict in result["conflicts"]:
            print(f"   - {conflict}")

    print("\n" + "=" * 70 + "\n")


def _print_swarm_analysis(result: dict):
    """Print swarm analysis in human-readable format."""
    print("\n" + "=" * 70)
    print("📊 SWARM STATE ANALYSIS")
    print("=" * 70)

    print("\n🐝 SWARM OVERVIEW:")
    print(f"   Total agents: {result.get('total_agents', 0)}")
    print(f"   Active agents: {result.get('agents_active', 0)}")
    print(f"   Your position: {result.get('your_position', 'Unknown')}")
    print(f"   Patterns available: {result.get('swarm_patterns_available', 0)}")

    if result.get("opportunities"):
        print("\n💡 OPPORTUNITIES FOR YOU:")
        for opp in result["opportunities"]:
            print(f"   - {opp}")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    sys.exit(main())
