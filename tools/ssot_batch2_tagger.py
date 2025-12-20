#!/usr/bin/env python3
"""
SSOT Batch 2 Tagger
===================

Tool to add SSOT tags to core infrastructure files in src/core/.
Batch 2: Core infrastructure files (50-70 files).

Author: Agent-3
Date: 2025-12-14
"""

import re
from pathlib import Path
from typing import List, Tuple

# Priority files for Batch 2 tagging
BATCH2_PRIORITY_FILES = [
    # Core agent management
    "src/core/agent_activity_tracker.py",
    "src/core/agent_context_manager.py",
    "src/core/agent_documentation_service.py",
    "src/core/agent_lifecycle.py",
    "src/core/agent_mode_manager.py",
    "src/core/agent_self_healing_system.py",

    # Core services
    "src/core/activity_emitter.py",
    "src/core/daily_cycle_tracker.py",
    "src/core/enhanced_activity_status_checker.py",
    "src/core/optimized_stall_resume_prompt.py",
    "src/core/stall_resumer_guard.py",
    "src/core/resume_cycle_planner_integration.py",

    # Configuration
    "src/core/config_browser.py",
    "src/core/config_thresholds.py",
    "src/core/unified_config.py",
    "src/core/pydantic_config.py",

    # Coordination
    "src/core/coordinate_loader.py",
    "src/core/coordinator_interfaces.py",
    "src/core/coordinator_models.py",
    "src/core/coordinator_registry.py",

    # Message queue core
    "src/core/message_queue.py",
    "src/core/message_queue_processor.py",
    "src/core/message_queue_persistence.py",
    "src/core/message_queue_statistics.py",
    "src/core/message_queue_error_monitor.py",
    "src/core/message_queue_performance_metrics.py",
    "src/core/message_queue_helpers.py",
    "src/core/message_queue_interfaces.py",
    "src/core/message_formatters.py",
    "src/core/in_memory_message_queue.py",

    # Messaging core
    "src/core/messaging_core.py",
    "src/core/messaging_models_core.py",
    "src/core/messaging_process_lock.py",
    "src/core/messaging_protocol_models.py",
    "src/core/messaging_pyautogui.py",
    "src/core/messaging_templates.py",
    "src/core/mock_unified_messaging_core.py",

    # Multi-agent
    "src/core/multi_agent_request_validator.py",
    "src/core/multi_agent_responder.py",

    # Utilities
    "src/core/shared_utilities.py",
    "src/core/command_execution_wrapper.py",
    "src/core/deferred_push_queue.py",
    "src/core/end_of_cycle_push.py",
    "src/core/merge_conflict_resolver.py",
    "src/core/local_repo_layer.py",
    "src/core/keyboard_control_lock.py",

    # Engines
    "src/core/engines/base_engine.py",
    "src/core/engines/engine_lifecycle.py",
    "src/core/engines/engine_state.py",
    "src/core/engines/engine_monitoring.py",

    # Performance
    "src/core/performance/performance_monitoring_system.py",
    "src/core/performance/performance_collector.py",
    "src/core/performance/coordination_performance_monitor.py",

    # Error handling core
    "src/core/error_handling/error_handling_core.py",
    "src/core/error_handling/error_models_core.py",
    "src/core/error_handling/error_exceptions_core.py",
    "src/core/error_handling/error_reporting_core.py",

    # File locking
    "src/core/file_locking/file_locking_models.py",

    # Metrics
    "src/core/metrics.py",

    # Onboarding
    "src/core/onboarding_service.py",
]

SSOT_DOMAIN = "infrastructure"
SSOT_TAG = f"<!-- SSOT Domain: {SSOT_DOMAIN} -->"


def has_ssot_tag(content: str) -> bool:
    """Check if file already has SSOT tag."""
    return "SSOT Domain:" in content


def add_ssot_tag(content: str) -> str:
    """Add SSOT tag to file content after docstring title."""
    lines = content.split('\n')
    new_lines = []
    i = 0

    # Skip shebang if present
    if lines and lines[0].startswith('#!'):
        new_lines.append(lines[0])
        i = 1

    # Find docstring start
    if i < len(lines) and (lines[i].startswith('"""') or lines[i].startswith("'''")):
        quote = lines[i][:3]
        new_lines.append(lines[i])
        i += 1

        # Add title line
        if i < len(lines):
            new_lines.append(lines[i])
            i += 1

        # Add blank line if needed
        if i < len(lines) and lines[i].strip():
            # Check if next line is blank
            if lines[i].strip() == "":
                new_lines.append(lines[i])
                i += 1
            else:
                # Insert blank line before content
                new_lines.append("")

        # Add SSOT tag
        new_lines.append(SSOT_TAG)
        new_lines.append("")  # Blank line after tag

    # Add remaining lines
    new_lines.extend(lines[i:])
    return '\n'.join(new_lines)


def process_file(file_path: Path) -> Tuple[bool, str]:
    """Process a single file to add SSOT tag."""
    try:
        content = file_path.read_text(encoding='utf-8')

        if has_ssot_tag(content):
            return False, "Already tagged"

        new_content = add_ssot_tag(content)
        file_path.write_text(new_content, encoding='utf-8')
        return True, "Tagged"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Main execution."""
    workspace_root = Path(__file__).parent.parent
    tagged_count = 0
    skipped_count = 0
    error_count = 0

    print(f"SSOT Batch 2 Tagging - Core Infrastructure Files")
    print(f"=" * 60)
    print()

    for file_rel_path in BATCH2_PRIORITY_FILES:
        file_path = workspace_root / file_rel_path

        if not file_path.exists():
            print(f"⚠️  Not found: {file_rel_path}")
            continue

        success, message = process_file(file_path)

        if success:
            tagged_count += 1
            print(f"✅ {file_rel_path}")
        elif "Already tagged" in message:
            skipped_count += 1
            print(f"⏭️  {file_rel_path} (already tagged)")
        else:
            error_count += 1
            print(f"❌ {file_rel_path}: {message}")

    print()
    print(f"=" * 60)
    print(f"Summary:")
    print(f"  Tagged: {tagged_count}")
    print(f"  Already tagged: {skipped_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total processed: {tagged_count + skipped_count + error_count}")


if __name__ == "__main__":
    main()
