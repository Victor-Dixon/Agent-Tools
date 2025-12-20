#!/usr/bin/env python3
"""
Template Customizer Tool

Customizes Discord bot templates with agent-specific values and sends to agents.
Makes it easy to use template library programmatically.

Usage:
    python tools/template_customizer.py --template "Autonomous Execution - With Progress" --agent Agent-3 --progress "29.5% test coverage"
    python tools/template_customizer.py --list-templates
    python tools/template_customizer.py --template "Autonomous Execution - Standard" --agent Agent-7 --send

Author: Agent-3 (Infrastructure & DevOps Specialist)
Created: 2025-01-27
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.discord_commander.discord_template_collection import (
        get_template_by_name,
        get_templates_by_mode,
    )
    from src.services.messaging_infrastructure import ConsolidatedMessagingService
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Make sure you're running from project root")
    sys.exit(1)


class TemplateCustomizer:
    """Customizes and sends Discord bot templates to agents."""

    # Agent specializations mapping
    AGENT_SPECIALIZATIONS = {
        "Agent-1": "Integration & Core Systems Specialist",
        "Agent-2": "Architecture & Design Specialist",
        "Agent-3": "Infrastructure & DevOps Specialist",
        "Agent-4": "Strategic Oversight & Emergency Intervention",
        "Agent-5": "Business Intelligence Specialist",
        "Agent-6": "Coordination & Communication Specialist",
        "Agent-7": "Web Development Specialist",
        "Agent-8": "SSOT & System Integration Specialist",
    }

    def __init__(self):
        """Initialize template customizer."""
        self.messaging_service = ConsolidatedMessagingService()

    def list_templates(self, mode: str = "agent_commands") -> None:
        """List available templates for a mode."""
        templates = get_templates_by_mode(mode)
        if not templates:
            print(f"❌ No templates found for mode: {mode}")
            return

        print(f"\n📋 Templates for mode: {mode}\n")
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template['emoji']} {template['name']}")
            print(f"   Priority: {template['priority']}")
            if "placeholders" in template:
                placeholders = template["placeholders"].get("placeholders", {})
                if placeholders:
                    print(f"   Placeholders: {', '.join(placeholders.keys())}")
                else:
                    print("   Placeholders: None")
            print()

    def customize_template(
        self,
        template_name: str,
        mode: str = "agent_commands",
        agent_id: str = None,
        progress: str = None,
        milestone: str = None,
        context: str = None,
        achievements: str = None,
        work_type: str = None,
        target: str = None,
        work_unit: str = None,
        specific_actions: str = None,
    ) -> str:
        """Customize template with provided values."""
        template = get_template_by_name(template_name, mode)
        if not template:
            print(f"❌ Template not found: {template_name} (mode: {mode})")
            return None

        message = template["message"]

        # Auto-fill specialization if agent_id provided
        specialization = self.AGENT_SPECIALIZATIONS.get(agent_id, "Specialist")

        # Build replacement dict
        replacements = {
            "{SPECIALIZATION}": specialization,
            "{CURRENT_PROGRESS}": progress or "progress tracking",
            "{NEXT_MILESTONE}": milestone or "next milestone",
            "{CURRENT_CONTEXT}": context or "current work",
            "{ACHIEVEMENTS}": achievements or "achievements",
            "{WORK_TYPE}": work_type or "work",
            "{TARGET}": target or "excellence",
            "{WORK_UNIT}": work_unit or "unit",
            "{SPECIFIC_ACTIONS}": specific_actions or "Execute. Create. Verify.",
        }

        # Replace placeholders
        for placeholder, value in replacements.items():
            message = message.replace(placeholder, value)

        return message

    def send_template(
        self,
        template_name: str,
        agent_id: str,
        mode: str = "agent_commands",
        priority: str = "NORMAL",
        **kwargs,
    ) -> bool:
        """Customize and send template to agent."""
        # Customize template
        message = self.customize_template(
            template_name, mode=mode, agent_id=agent_id, **kwargs
        )

        if not message:
            return False

        # Send message
        try:
            result = self.messaging_service.send_message(
                agent=agent_id, message=message, priority=priority
            )
            if result:
                print(f"✅ Template '{template_name}' sent to {agent_id}")
                return True
            else:
                print(f"❌ Failed to send template to {agent_id}")
                return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False

    def preview_template(
        self,
        template_name: str,
        mode: str = "agent_commands",
        agent_id: str = None,
        **kwargs,
    ) -> None:
        """Preview customized template without sending."""
        message = self.customize_template(
            template_name, mode=mode, agent_id=agent_id, **kwargs
        )

        if not message:
            return

        print(f"\n📋 Preview of '{template_name}' for {agent_id or 'agent'}:\n")
        print("=" * 80)
        print(message)
        print("=" * 80)
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Customize and send Discord bot templates to agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all agent command templates
  python tools/template_customizer.py --list-templates

  # Preview customized template
  python tools/template_customizer.py --template "Autonomous Execution - With Progress" \\
    --agent Agent-3 --progress "29.5% test coverage" --milestone "30% coverage"

  # Send template to agent
  python tools/template_customizer.py --template "Autonomous Execution - Standard" \\
    --agent Agent-7 --send

  # Customize with all values
  python tools/template_customizer.py --template "Autonomous Execution - Full Jet Fuel" \\
    --agent Agent-3 --progress "29.5% test coverage" --achievements "222 tests" \\
    --milestone "30% coverage" --context "test coverage" --send
        """,
    )

    parser.add_argument(
        "--template",
        "-t",
        help="Template name to use",
    )
    parser.add_argument(
        "--mode",
        "-m",
        default="agent_commands",
        help="Template mode (default: agent_commands)",
    )
    parser.add_argument(
        "--agent",
        "-a",
        help="Target agent ID (e.g., Agent-3)",
    )
    parser.add_argument(
        "--list-templates",
        "-l",
        action="store_true",
        help="List available templates",
    )
    parser.add_argument(
        "--send",
        "-s",
        action="store_true",
        help="Send template to agent (otherwise just preview)",
    )
    parser.add_argument(
        "--priority",
        "-p",
        default="NORMAL",
        choices=["NORMAL", "HIGH", "CRITICAL"],
        help="Message priority (default: NORMAL)",
    )

    # Template customization options
    parser.add_argument("--progress", help="Current progress/metric")
    parser.add_argument("--milestone", help="Next milestone")
    parser.add_argument("--context", help="Current work context")
    parser.add_argument("--achievements", help="Recent achievements")
    parser.add_argument("--work-type", help="Type of work (files, tests, etc.)")
    parser.add_argument("--target", help="Ultimate target")
    parser.add_argument("--work-unit", help="Unit of work (test file, commit, etc.)")
    parser.add_argument("--specific-actions", help="Specific action verbs")

    args = parser.parse_args()

    customizer = TemplateCustomizer()

    # List templates
    if args.list_templates:
        customizer.list_templates(args.mode)
        return

    # Require template name
    if not args.template:
        print("❌ Error: --template required (use --list-templates to see options)")
        parser.print_help()
        sys.exit(1)

    # Build kwargs for customization
    kwargs = {}
    if args.progress:
        kwargs["progress"] = args.progress
    if args.milestone:
        kwargs["milestone"] = args.milestone
    if args.context:
        kwargs["context"] = args.context
    if args.achievements:
        kwargs["achievements"] = args.achievements
    if args.work_type:
        kwargs["work_type"] = args.work_type
    if args.target:
        kwargs["target"] = args.target
    if args.work_unit:
        kwargs["work_unit"] = args.work_unit
    if args.specific_actions:
        kwargs["specific_actions"] = args.specific_actions

    # Send or preview
    if args.send:
        if not args.agent:
            print("❌ Error: --agent required when using --send")
            sys.exit(1)
        customizer.send_template(
            args.template,
            args.agent,
            mode=args.mode,
            priority=args.priority,
            **kwargs,
        )
    else:
        customizer.preview_template(
            args.template, mode=args.mode, agent_id=args.agent, **kwargs
        )


if __name__ == "__main__":
    main()

