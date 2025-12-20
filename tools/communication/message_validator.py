#!/usr/bin/env python3
"""
Unified Message Validator
=========================

Consolidates Discord message validation and protocol compliance validation.
Combines functionality from discord_message_validator.py and protocol_validator.py.

Features:
- Discord message limits validation
- Protocol compliance validation
- Message structure validation
- Format validation

V2 Compliance: ≤300 lines, ≤200 lines/class, ≤30 lines/function
Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Task: Phase 2 Tools Consolidation - Communication Validation
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.utils.validation_utils import print_validation_report

# Discord limits
MAX_MESSAGE_LENGTH = 2000
MAX_EMBED_DESCRIPTION = 4096
MAX_FIELD_VALUE = 1024
MAX_FIELD_NAME = 256
MAX_EMBED_TOTAL = 6000
MAX_MODAL_LABEL = 45
MAX_FIELDS_PER_EMBED = 25


class MessageValidator:
    """Unified message validation (Discord limits + protocol compliance)."""

    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_discord_message(self, content: str) -> bool:
        """Validate Discord message content against limits."""
        if len(content) > MAX_MESSAGE_LENGTH:
            self.errors.append(
                f"Message exceeds limit: {len(content)}/{MAX_MESSAGE_LENGTH} chars"
            )
            return False
        return True

    def validate_discord_embed(self, embed_data: Dict[str, Any]) -> bool:
        """Validate Discord embed structure and content."""
        valid = True
        total_length = 0

        description = embed_data.get("description", "")
        if description:
            desc_len = len(description)
            total_length += desc_len
            if desc_len > MAX_EMBED_DESCRIPTION:
                self.errors.append(
                    f"Embed description exceeds limit: {desc_len}/{MAX_EMBED_DESCRIPTION}"
                )
                valid = False

        fields = embed_data.get("fields", [])
        if len(fields) > MAX_FIELDS_PER_EMBED:
            self.errors.append(
                f"Too many fields: {len(fields)}/{MAX_FIELDS_PER_EMBED}"
            )
            valid = False

        for i, field in enumerate(fields):
            if not self._validate_field(field, i):
                valid = False
            field_name = field.get("name", "")
            field_value = field.get("value", "")
            total_length += len(field_name) + len(field_value)

        if total_length > MAX_EMBED_TOTAL:
            self.warnings.append(
                f"Embed total length high: {total_length}/{MAX_EMBED_TOTAL}"
            )

        return valid

    def _validate_field(self, field: Dict[str, Any], index: int) -> bool:
        """Validate embed field."""
        valid = True
        name = field.get("name", "")
        if len(name) > MAX_FIELD_NAME:
            self.errors.append(
                f"Field {index} name exceeds limit: {len(name)}/{MAX_FIELD_NAME}"
            )
            valid = False

        value = field.get("value", "")
        if len(value) > MAX_FIELD_VALUE:
            self.errors.append(
                f"Field {index} value exceeds limit: {len(value)}/{MAX_FIELD_VALUE}"
            )
            valid = False

        return valid

    def validate_protocol(self, protocol_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate protocol data structure."""
        errors = []
        required_fields = ["version", "type"]
        for field in required_fields:
            if field not in protocol_data:
                errors.append(f"Missing required field: {field}")

        if "version" in protocol_data:
            version = protocol_data["version"]
            if not isinstance(version, (int, str)):
                errors.append("Version must be int or string")
            elif isinstance(version, str) and not version.isdigit():
                errors.append("Version string must be numeric")

        return len(errors) == 0, errors

    def validate_message_structure(self, message: Dict[str, Any]) -> bool:
        """Validate message structure (content, sender, recipient)."""
        valid = True
        if not message.get("content"):
            self.errors.append("Message content is required")
            valid = False
        if not message.get("sender"):
            self.errors.append("Message sender is required")
            valid = False
        if not message.get("recipient"):
            self.errors.append("Message recipient is required")
            valid = False
        return valid

    def validate_file(self, file_path: Path) -> bool:
        """Validate message/embed from JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            valid = True
            if "content" in data:
                if not self.validate_discord_message(data["content"]):
                    valid = False
            if "embed" in data:
                if not self.validate_discord_embed(data["embed"]):
                    valid = False
            if "modal_labels" in data:
                for label in data["modal_labels"]:
                    if len(label) > MAX_MODAL_LABEL:
                        self.errors.append(
                            f"Modal label exceeds limit: {len(label)}/{MAX_MODAL_LABEL}"
                        )
                        valid = False

            return valid
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def print_report(self) -> None:
        """Print validation report using SSOT utility."""
        print_validation_report(
            errors=self.errors,
            warnings=self.warnings,
        )


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified message validator (Discord + protocol)"
    )
    parser.add_argument("content", nargs="?", help="Message content to validate")
    parser.add_argument("--file", type=Path, help="JSON file with message data")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    validator = MessageValidator()

    if args.file:
        valid = validator.validate_file(args.file)
    elif args.content:
        valid = validator.validate_discord_message(args.content)
    else:
        parser.print_help()
        return 1

    if args.json:
        summary = validator.get_summary()
        print(json.dumps(summary, indent=2))
        return 0 if summary["valid"] else 1
    else:
        validator.print_report()
        return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())


