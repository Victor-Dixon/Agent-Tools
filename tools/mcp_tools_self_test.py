#!/usr/bin/env python3
"""Self-test harness for MCP server tools.

Runs each MCP-exposed function once with safe test inputs and reports
success/error status and brief results.
"""

from mcp_servers import v2_compliance_server as vc
from mcp_servers import git_operations_server as go
from mcp_servers import swarm_brain_server as sb
from mcp_servers import website_manager_server as wm
from mcp_servers import task_manager_server as tm
import json
import traceback
from pathlib import Path
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


report: dict = {}


def safe_call(section_name: str, tool_name: str, func, *args, **kwargs) -> None:
    """Call a tool function and capture success/error without raising."""
    entry: dict = {"ok": False}
    try:
        res = func(*args, **kwargs)
        entry["ok"] = True
        entry["result"] = res
    except Exception as e:  # noqa: BLE001
        entry["error"] = f"{type(e).__name__}: {e}"
        entry["traceback"] = traceback.format_exc()
    report.setdefault(section_name, {})[tool_name] = entry


def run_task_manager_tests() -> None:
    section = "task-manager"
    # Get all sections
    safe_call(section, "get_tasks_all", tm.get_tasks)
    # Add and move a clearly-marked diagnostic task
    task_desc = "MCP SELF-TEST TASK (safe to delete)"
    safe_call(section, "add_task_to_inbox", tm.add_to_inbox,
              task_desc, agent_id="Agent-MCP")
    safe_call(
        section,
        "move_to_waiting_on",
        tm.move_to_waiting_on,
        task_desc,
        "diagnostic test",
        "Agent-MCP",
    )
    # Attempt to mark it complete in INBOX (may legitimately report not found)
    safe_call(section, "mark_task_complete_inbox",
              tm.mark_task_complete, task_desc, section="INBOX")


def run_website_manager_tests() -> None:
    section = "website-manager"
    # Use freerideinvestor as safe default site_key
    site_key = "freerideinvestor"

    # List pages
    safe_call(section, "list_wordpress_pages",
              wm.list_wordpress_pages, site_key)

    # Create a simple test page (uses WordPressManager.create_page which only
    # touches theme files + functions.php locally; actual WordPress page is
    # created on next theme switch).
    safe_call(
        section,
        "create_wordpress_page",
        wm.create_wordpress_page,
        site_key,
        "MCP Test Page",
        "mcp-test-page",
    )

    # Deploy file with missing local path (exercise error path only)
    safe_call(
        section,
        "deploy_file_missing",
        wm.deploy_file_to_wordpress,
        site_key,
        "NON_EXISTENT_LOCAL_FILE",
        "dummy_remote_path",
    )

    # Add test page slug to menu (idempotent)
    safe_call(
        section,
        "add_page_to_menu",
        wm.add_page_to_menu,
        site_key,
        "mcp-test-page",
        "MCP Test Page",
    )

    # Create TSLA strategy blog post for freerideinvestor
    safe_call(
        section,
        "create_blog_post_for_site",
        wm.create_blog_post_for_site,
        "freerideinvestor",
    )

    # Create TSLA report page (free)
    safe_call(
        section,
        "create_report_page_for_site",
        wm.create_report_page_for_site,
        "freerideinvestor",
        strategy_name=None,
        premium=False,
    )

    # Generate image prompts (local files only)
    safe_call(section, "generate_image_prompts", wm.generate_image_prompts)

    # Purge WordPress cache (via WP-CLI / REST)
    safe_call(section, "purge_wordpress_cache",
              wm.purge_wordpress_cache, site_key)


def run_swarm_brain_tests() -> None:
    section = "swarm-brain"
    agent_id = "Agent-MCP"

    # Share learning
    safe_call(
        section,
        "share_learning",
        sb.share_learning,
        agent_id,
        "MCP diagnostics",
        "Testing Swarm Brain MCP tools",
        ["mcp", "diagnostic"],
    )

    # Record decision
    safe_call(
        section,
        "record_decision",
        sb.record_decision,
        agent_id,
        "Use MCP for infra ops",
        "MCP tools verified across servers",
        ["Agent-MCP"],
    )

    # Search knowledge
    safe_call(section, "search_swarm_knowledge",
              sb.search_swarm_knowledge, agent_id, "MCP", 5)

    # Take a note
    safe_call(section, "take_note", sb.take_note,
              agent_id, "MCP self-test note", "important")

    # Get notes for this agent
    safe_call(section, "get_agent_notes", sb.get_agent_notes, agent_id)


def run_git_operations_tests() -> None:
    section = "git-operations"

    safe_call(section, "get_recent_commits",
              go.get_recent_commits, None, 24, None)
    safe_call(
        section,
        "verify_git_work",
        go.verify_git_work,
        "Agent-MCP",
        "MASTER_TASK_LOG.md",
        "Updated tasks via MCP self-test",
        48,
    )
    safe_call(section, "check_file_history",
              go.check_file_history, "MASTER_TASK_LOG.md", 14)
    safe_call(section, "validate_commit_HEAD", go.validate_commit, "HEAD")
    safe_call(
        section,
        "verify_work_exists_mcp",
        go.verify_work_exists_mcp,
        ["mcp_servers/*.py"],
        "Agent-MCP",
    )


def run_v2_compliance_tests() -> None:
    section = "v2-compliance"

    safe_call(section, "validate_file_size_MASTER_TASK_LOG",
              vc.validate_file_size, "MASTER_TASK_LOG.md")
    safe_call(section, "check_v2_compliance_MASTER_TASK_LOG",
              vc.check_v2_compliance, "MASTER_TASK_LOG.md")
    safe_call(
        section,
        "check_function_size_task_manager_server",
        vc.check_function_size,
        "mcp_servers/task_manager_server.py",
        None,
        30,
    )
    safe_call(section, "get_v2_exceptions", vc.get_v2_exceptions)


if __name__ == "__main__":
    run_task_manager_tests()
    run_website_manager_tests()
    run_swarm_brain_tests()
    run_git_operations_tests()
    run_v2_compliance_tests()

    print(json.dumps(report, indent=2, default=str))
