#!/usr/bin/env python3
"""
Template Structure Linter
=========================

Quick CLI to render messaging templates (S2A/D2A/C2A/A2A) and assert that
required sections and ordering are present. Useful for smoke checks before
shipping template changes.

Usage:
    python tools/template_structure_linter.py --category S2A --recipient Agent-1
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from src.core.messaging_models import (
    MessageCategory,
    UnifiedMessage,
    UnifiedMessagePriority,
    UnifiedMessageType,
)
from src.core.messaging_templates import render_message


def _create_message(
    category: MessageCategory,
    sender: str,
    recipient: str,
    message_type: UnifiedMessageType,
    content: str = "Test content",
) -> UnifiedMessage:
    return UnifiedMessage(
        content=content,
        sender=sender,
        recipient=recipient,
        message_type=message_type,
        priority=UnifiedMessagePriority.REGULAR,
        tags=[],
        category=category,
        message_id="lint_msg_id",
    )


def _assert_sections_present(rendered: str, required: List[str]) -> None:
    for section in required:
        if section not in rendered:
            raise AssertionError(f"Missing required section: {section}")


def _assert_in_order(rendered: str, ordered: List[str]) -> None:
    positions = []
    for section in ordered:
        pos = rendered.find(section)
        if pos < 0:
            raise AssertionError(f"Section not found: {section}")
        positions.append(pos)
    if positions != sorted(positions):
        raise AssertionError(
            f"Sections out of order.\nOrder: {ordered}\nPositions: {positions}"
        )


def lint_template(category: MessageCategory, recipient: str, sender: str) -> str:
    defaults = {
        MessageCategory.S2A: {
            "required": [
                "[HEADER] S2A",
                "From:",
                "To:",
                "Priority:",
                "Message ID:",
                "Timestamp:",
                "Agent Operating Cycle",
                "Cycle Checklist:",
            ],
            "order": [
                "[HEADER] S2A",
                "Context:",
                "Action Required:",
                "Agent Operating Cycle",
                "Cycle Checklist:",
                "Evidence format:",
                "If blocked:",
            ],
            "type": UnifiedMessageType.SYSTEM_TO_AGENT,
        },
        MessageCategory.D2A: {
            "required": [
                "[HEADER] D2A",
                "User Message:",
                "Interpretation (agent):",
                "Proposed Action:",
                "Devlog Command",
                "#DISCORD",
            ],
            "order": [
                "[HEADER] D2A",
                "Origin:",
                "User Message:",
                "Interpretation (agent):",
                "Proposed Action:",
                "Devlog Command",
                "If clarification needed:",
                "#DISCORD",
            ],
            "type": UnifiedMessageType.HUMAN_TO_AGENT,
        },
        MessageCategory.C2A: {
            "required": [
                "[HEADER] C2A",
                "Identity:",
                "No-Ack Policy:",
                "Cycle Checklist:",
                "Task:",
                "Operating Procedures",
                "Deliverable:",
                "If blocked:",
            ],
            "order": [
                "[HEADER] C2A",
                "Identity:",
                "No-Ack Policy:",
                "Cycle Checklist:",
                "Task:",
                "Context:",
                "Operating Procedures",
                "Deliverable:",
            ],
            "type": UnifiedMessageType.CAPTAIN_TO_AGENT,
        },
        MessageCategory.A2A: {
            "required": [
                "[HEADER] A2A",
                "Identity:",
                "No-Ack Policy:",
                "Cycle Checklist:",
                "Ask/Offer:",
                "Context:",
                "Next Step:",
                "If blocked:",
                "How to respond:",
                "#A2A",
            ],
            "order": [
                "[HEADER] A2A",
                "Identity:",
                "No-Ack Policy:",
                "Cycle Checklist:",
                "Ask/Offer:",
                "Context:",
                "Next Step:",
                "If blocked:",
                "How to respond:",
                "#A2A",
            ],
            "type": UnifiedMessageType.AGENT_TO_AGENT,
        },
    }

    cfg = defaults[category]
    msg = _create_message(
        category=category,
        sender=sender,
        recipient=recipient,
        message_type=cfg["type"],
    )
    rendered = render_message(msg, context="Context", actions="Actions")
    _assert_sections_present(rendered, cfg["required"])
    _assert_in_order(rendered, cfg["order"])
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lint messaging template structure and ordering."
    )
    parser.add_argument(
        "--category",
        choices=["S2A", "D2A", "C2A", "A2A"],
        required=True,
        help="Template category to lint",
    )
    parser.add_argument("--recipient", required=True, help="Recipient agent id")
    parser.add_argument("--sender", default="SYSTEM", help="Sender id")
    args = parser.parse_args()

    category = MessageCategory[args.category]
    try:
        rendered = lint_template(category, recipient=args.recipient, sender=args.sender)
    except AssertionError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    print("[PASS] Template structure and ordering validated.")
    print("--- Rendered Preview ---")
    print(rendered[:800])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


