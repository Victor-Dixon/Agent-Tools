#!/usr/bin/env python3
"""
Soft Onboarding CLI Tool
========================

Command-line interface for soft onboarding agents with session cleanup protocol.

Usage:
    python tools/soft_onboard_cli.py --agent Agent-1 --message "Your onboarding message"
    python tools/soft_onboard_cli.py --agent Agent-1 --role "Integration Specialist" --file onboarding.txt
    python tools/soft_onboard_cli.py --agents Agent-1,Agent-2,Agent-3 --message "Team mission"
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.soft_onboarding_service import (
    SoftOnboardingService,
    soft_onboard_agent,
    soft_onboard_multiple_agents,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Soft Onboarding CLI - Session cleanup and agent onboarding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Agent selection
    parser.add_argument("--agent", type=str, help="Single agent ID (e.g., Agent-1)")
    parser.add_argument(
        "--agents",
        type=str,
        help="Multiple agent IDs, comma-separated (e.g., Agent-1,Agent-2,Agent-3)",
    )

    # Message options
    parser.add_argument("--message", type=str, help="Onboarding message content")
    parser.add_argument("--file", type=str, help="File containing onboarding message content")
    parser.add_argument("--role", type=str, help="Role assignment for agent(s)")

    # Custom cleanup message
    parser.add_argument(
        "--cleanup-message",
        type=str,
        help="Custom session cleanup message (optional, uses template if not provided)",
    )

    # Step-by-step mode
    parser.add_argument(
        "--step",
        type=int,
        choices=[1, 2, 3],
        help="Execute single step only (1=cleanup, 2=new chat, 3=onboarding)",
    )

    # Testing
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without executing"
    )
    
    # Cycle report
    parser.add_argument(
        "--generate-cycle-report",
        action="store_true",
        default=True,
        help="Generate cycle accomplishments report after onboarding (default: True)"
    )
    parser.add_argument(
        "--no-cycle-report",
        dest="generate_cycle_report",
        action="store_false",
        help="Skip cycle accomplishments report generation"
    )
    parser.add_argument(
        "--cycle-id",
        type=str,
        help="Cycle identifier for report (e.g., C-XXX)"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.agent and not args.agents:
        parser.error("Must specify --agent or --agents")

    if not args.message and not args.file and not args.step:
        parser.error("Must specify --message or --file (unless using --step)")

    # Load message from file if specified
    if args.file:
        try:
            message_file = Path(args.file)
            if not message_file.exists():
                logger.error(f"❌ Message file not found: {args.file}")
                return 1
            args.message = message_file.read_text(encoding="utf-8")
            logger.info(f"📄 Loaded message from {args.file}")
        except Exception as e:
            logger.error(f"❌ Failed to read message file: {e}")
            return 1

    # Handle step-by-step mode
    if args.step:
        return execute_single_step(args)

    # Handle dry run
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE - No actions will be executed")
        if args.agent:
            logger.info(f"Would soft onboard: {args.agent}")
        elif args.agents:
            agent_list = [a.strip() for a in args.agents.split(",")]
            logger.info(f"Would soft onboard: {', '.join(agent_list)}")
        logger.info(f"Message: {args.message[:100]}...")
        if args.role:
            logger.info(f"Role: {args.role}")
        return 0

    # Execute soft onboarding
    try:
        if args.agent:
            # Single agent
            logger.info(f"🚀 Soft onboarding {args.agent}")
            success = soft_onboard_agent(args.agent, args.message, role=args.role)
            if success:
                logger.info(f"✅ Soft onboarding complete for {args.agent}!")
                return 0
            else:
                logger.error(f"❌ Soft onboarding failed for {args.agent}")
                return 1

        elif args.agents:
            # Multiple agents
            agent_list = [a.strip() for a in args.agents.split(",")]
            logger.info(f"🚀 Soft onboarding {len(agent_list)} agents")

            # Create list of (agent_id, message) tuples
            agents_with_messages = [(agent_id, args.message) for agent_id in agent_list]

            results = soft_onboard_multiple_agents(
                agents_with_messages,
                args.role,
                generate_cycle_report=args.generate_cycle_report
            )

            # Report results
            successful = [aid for aid, success in results.items() if success]
            failed = [aid for aid, success in results.items() if not success]

            logger.info(f"📊 Results: {len(successful)}/{len(agent_list)} successful")
            if successful:
                logger.info(f"✅ Success: {', '.join(successful)}")
            if failed:
                logger.error(f"❌ Failed: {', '.join(failed)}")
            
            # Generate cycle report if requested (and not already generated)
            if args.generate_cycle_report:
                try:
                    from src.services.soft_onboarding_service import generate_cycle_accomplishments_report
                    report_path = generate_cycle_accomplishments_report(cycle_id=args.cycle_id)
                    if report_path:
                        logger.info(f"📊 Cycle report available at: {report_path}")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to generate cycle report: {e}")

            return 0 if len(failed) == 0 else 1

    except Exception as e:
        logger.error(f"❌ Soft onboarding error: {e}")
        return 1


def execute_single_step(args):
    """Execute a single step of soft onboarding protocol."""
    if not args.agent:
        logger.error("❌ --step mode requires --agent (single agent only)")
        return 1

    try:
        service = SoftOnboardingService()

        if args.step == 1:
            # Step 1: Session cleanup message
            logger.info(f"📝 Step 1: Sending session cleanup message to {args.agent}")
            success = service.send_session_cleanup_message(args.agent, args.cleanup_message)
            if success:
                logger.info("✅ Session cleanup message sent!")
                logger.info(
                    "⏳ Agent should complete: passdown.json, devlog, Discord post, swarm brain update, tool creation"
                )
                return 0
            else:
                logger.error("❌ Failed to send session cleanup message")
                return 1

        elif args.step == 2:
            # Step 2: New chat
            logger.info("🆕 Step 2: Starting new chat (Ctrl+T)")
            success = service.start_new_chat()
            if success:
                logger.info("✅ New chat started!")
                return 0
            else:
                logger.error("❌ Failed to start new chat")
                return 1

        elif args.step == 3:
            # Step 3: Onboarding message
            if not args.message:
                logger.error("❌ Step 3 requires --message")
                return 1
            logger.info(f"🎯 Step 3: Sending onboarding message to {args.agent}")
            success = service.send_onboarding_message(args.agent, args.message, args.role)
            if success:
                logger.info("✅ Onboarding message sent!")
                return 0
            else:
                logger.error("❌ Failed to send onboarding message")
                return 1

    except Exception as e:
        logger.error(f"❌ Step execution error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
