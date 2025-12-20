#!/usr/bin/env python3
"""
Integrate Auto Learning with Message System
===========================================

Integrates automatic preference learning into the message reading/response flow.
When Agent-8 reads and responds to messages, this automatically learns from the interaction.

<!-- SSOT Domain: qa -->

Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import time


def learn_from_message_response(
    message_file: Path,
    response: str,
    response_quality: str = "good",
    feedback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Automatically learn from a message response interaction.
    
    Args:
        message_file: Path to the message file (ARIA_MESSAGE_*.md or CARMYN_MESSAGE_*.md)
        response: Agent-8's response
        response_quality: "excellent", "good", "poor", "failed"
        feedback: User feedback if available
    
    Returns:
        Dictionary of insights learned
    """
    # Determine user from filename
    filename = message_file.name
    if filename.startswith("ARIA_MESSAGE_"):
        user = "aria"
    elif filename.startswith("CARMYN_MESSAGE_"):
        user = "carmyn"
    else:
        return {"error": "Unknown message type"}
    
    # Read original message
    try:
        message_content = message_file.read_text(encoding='utf-8')
        # Extract user's message (between "**Aria's Message:**" or "**Carmyn's Message:**" and next section)
        user_message_match = re.search(
            rf"\*\*{user.capitalize()}'s Message:\*\*\s*\n(.*?)\n\n\*\*",
            message_content,
            re.DOTALL
        )
        if not user_message_match:
            # Try alternative pattern
            user_message_match = re.search(
                rf"Message:\*\*\s*\n(.*?)\n\n\*\*",
                message_content,
                re.DOTALL
            )
        
        user_message = user_message_match.group(1).strip() if user_message_match else message_content[:500]
    except Exception as e:
        return {"error": f"Failed to read message: {e}"}
    
    # Calculate response time (if message has timestamp)
    response_time = None
    try:
        timestamp_match = re.search(r"\*\*Timestamp\*\*:\s*(.+)", message_content)
        if timestamp_match:
            message_time = datetime.fromisoformat(timestamp_match.group(1).strip())
            response_time = (datetime.now() - message_time).total_seconds()
    except:
        pass
    
    # Learn from interaction
    from .auto_learn_preferences import AutomaticPreferenceLearner
    
    learner = AutomaticPreferenceLearner(user=user)
    insights = learner.learn_from_interaction(
        message=user_message,
        response=response,
        response_quality=response_quality,
        feedback=feedback,
        response_time_seconds=response_time
    )
    
    return {
        "user": user,
        "insights": insights,
        "preferences_updated": True,
        "summary": learner.get_learned_preferences_summary()
    }


def auto_learn_from_inbox_message(message_file: Path) -> Dict[str, Any]:
    """
    Automatically learn from an inbox message (when Agent-8 reads it).
    This is called automatically when Agent-8 reads a message.
    """
    # Just reading the message is a positive interaction
    return learn_from_message_response(
        message_file=message_file,
        response="Message read",
        response_quality="good"
    )


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrate Auto Learning")
    parser.add_argument("message_file", type=Path,
                       help="Path to message file")
    parser.add_argument("--response", type=str, default=None,
                       help="Agent-8's response")
    parser.add_argument("--quality", type=str, default="good",
                       choices=["excellent", "good", "poor", "failed"],
                       help="Response quality")
    
    args = parser.parse_args()
    
    result = learn_from_message_response(
        message_file=args.message_file,
        response=args.response or "Message processed",
        response_quality=args.quality
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    
    print(f"✅ Learned from {result['user']}'s message")
    print(f"   Insights: {len(result['insights'].get('effective_approaches', []))} effective approaches")
    print(f"   Patterns: {len(result['insights'].get('communication_patterns', []))} patterns learned")

