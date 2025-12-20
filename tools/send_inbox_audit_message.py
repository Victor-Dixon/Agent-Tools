#!/usr/bin/env python3
"""
DEPRECATED:
This script is deprecated. Prefer using the canonical messaging CLI instead.

Equivalent CLI command (send audit to individual agents):
  python -m src.services.messaging_cli --agent <agent_id> -m "**🚨 PRE-PUBLIC PUSH AUDIT - [your message]**" --type text --category a2c --priority urgent
  # Or use bulk mode for all agents:
  python -m src.services.messaging_cli --bulk -m "[your message]" --priority urgent

For A2A/A2C message formatting and reply instructions, see:
  src/core/messaging_template_texts.py (MessageCategory.A2A / MessageCategory.A2C templates)

This script is kept for backward compatibility only. New workflows should use messaging_cli.

---

Send Audit Message Directly to Agent Inboxes
=============================================

Writes audit message directly to agent inbox directories (file-based messaging).
Works even when message queue and Discord bot are offline.

Author: Agent-6 (Coordination & Communication)
Date: 2025-12-11
"""

import sys
from datetime import datetime
from pathlib import Path

# Agent list
AGENTS = ['Agent-1', 'Agent-2', 'Agent-3', 'Agent-5',
          'Agent-6', 'Agent-7', 'Agent-8', 'Agent-4']

# Audit message
AUDIT_MESSAGE = """# 🚨 CAPTAIN MESSAGE - PRE-PUBLIC PUSH AUDIT

**From**: Captain Agent-4
**To**: {agent_id}
**Priority**: urgent
**Message ID**: audit_2025-12-11_pre_public
**Timestamp**: {timestamp}

---

## 🚨 PRE-PUBLIC PUSH AUDIT REQUEST

**PREPARING FOR PUBLIC REPOSITORY**: https://github.com/Victor-Dixon/Dream.os.git

All agents are requested to conduct a **FINAL AUDIT** of your areas of responsibility before we push to public GitHub.

### REQUIRED CHECKS:

✅ **Security Review**
   - No tokens, passwords, API keys, or credentials in code
   - No `.env` files with real values
   - No hardcoded secrets
   - No production database credentials
   - No personal information or private data

✅ **Code Quality**
   - Clean, professional code structure
   - Appropriate comments (no debug clutter)
   - Follows V2 compliance standards
   - Proper error handling
   - No temporary or test code in production paths

✅ **Documentation**
   - README is professional and clear
   - Code comments are helpful, not revealing internal details
   - No internal coordination details exposed
   - Proper licensing information

✅ **Professional Presentation**
   - Project structure is logical
   - File naming is consistent and professional
   - No unprofessional language or comments
   - Consistent branding (Dream.os)

### YOUR DOMAIN-SPECIFIC CHECKS:

{domain_checks}

### ACTION REQUIRED:

1. **Review your domain immediately**
2. **Report any issues found** via status.json update
3. **Flag any files** that need removal before push
4. **Update status.json** when audit complete with:
   - `"audit_status": "complete"`
   - `"audit_findings": ["list", "of", "findings"]`
   - `"audit_blockers": ["any", "blockers"]`

### DEADLINE:

**ASAP** - We are preparing for public push. Complete your audit immediately.

---

*Message delivered via direct inbox file-based messaging*

#PRE-PUBLIC-AUDIT #HIGH-PRIORITY #ALL-AGENTS #URGENT
"""

# Domain-specific checks
DOMAIN_CHECKS = {
    'Agent-1': """
• **Integration & Core Systems**
  - Review `src/core/` for sensitive data
  - Check integration configurations
  - Review API client implementations
  - Audit core system utilities
  - Check messaging infrastructure
""",
    'Agent-2': """
• **Architecture & Design**
  - Review architecture documentation
  - Check design pattern implementations
  - Review system design documents
  - Ensure no internal design secrets exposed
  - Review README and documentation structure
""",
    'Agent-3': """
• **Infrastructure & DevOps**
  - Review deployment configurations
  - Check infrastructure as code
  - Review CI/CD pipelines
  - Audit environment configurations
  - Check for any deployment secrets
""",
    'Agent-5': """
• **Business Intelligence**
  - Review analytics code
  - Check data processing implementations
  - Review reporting systems
  - Ensure no sensitive metrics exposed
  - Check for any API keys in analytics code
""",
    'Agent-6': """
• **Coordination & Communication**
  - Review messaging infrastructure
  - Check coordination systems
  - Review communication protocols
  - Ensure no internal coordination details exposed
  - Review agent communication code
""",
    'Agent-7': """
• **Web Development**
  - Review web assets
  - Check frontend code
  - Review web application code
  - Ensure no API keys in frontend
  - Check for any exposed credentials
""",
    'Agent-8': """
• **SSOT & System Integration / QA**
  - Review test files
  - Check quality standards
  - Review SSOT compliance
  - Ensure test data is safe
  - Review validation code
""",
    'Agent-4': """
• **Captain - Strategic Oversight**
  - Coordinate audit efforts
  - Review overall project structure
  - Final security check
  - Approve for public push
  - Review README and branding
""",
}


def send_inbox_message(agent_id: str, workspace_root: Path = None) -> bool:
    """Send audit message directly to agent inbox."""
    if workspace_root is None:
        workspace_root = Path(__file__).parent.parent

    inbox_dir = workspace_root / "agent_workspaces" / agent_id / "inbox"

    # Create inbox directory if it doesn't exist
    inbox_dir.mkdir(parents=True, exist_ok=True)

    # Generate message with agent-specific domain checks
    timestamp = datetime.now().isoformat()
    domain_checks = DOMAIN_CHECKS.get(
        agent_id, "• Review your domain for all security and quality issues")

    message_content = AUDIT_MESSAGE.format(
        agent_id=agent_id,
        timestamp=timestamp,
        domain_checks=domain_checks
    )

    # Create message filename
    message_filename = f"CAPTAIN_MESSAGE_AUDIT_PRE_PUBLIC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}.md"
    message_path = inbox_dir / message_filename

    try:
        # Write message to inbox
        message_path.write_text(message_content, encoding='utf-8')
        print(f"✅ Message delivered to {agent_id} inbox: {message_path.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to send message to {agent_id}: {e}")
        return False


def main():
    """Send audit message to all agents."""
    workspace_root = Path(__file__).parent.parent
    print("=" * 70)
    print("PRE-PUBLIC PUSH AUDIT - DIRECT INBOX DELIVERY")
    print("=" * 70)
    print()

    success_count = 0
    failed_count = 0

    for agent_id in AGENTS:
        if send_inbox_message(agent_id, workspace_root):
            success_count += 1
        else:
            failed_count += 1

    print()
    print("=" * 70)
    print(f"✅ Successfully delivered: {success_count}/{len(AGENTS)}")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count}/{len(AGENTS)}")
    print("=" * 70)

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
