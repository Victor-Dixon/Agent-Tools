"""
Captain Snapshot Tool - Multi-Agent Status Overview
==================================================

Provides aggregated view of all agent statuses with staleness detection.
Reads from runtime/agents_index.json and presents a concise table.

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use 'python -m tools_v2.toolbelt health.snapshot' instead.
This file will be removed in future version.

Migrated to: tools_v2/categories/health_tools.py → SnapshotTool
Registry: health.snapshot

Author: Agent-4 - Strategic Oversight & Emergency Intervention Manager
Deprecated: 2025-01-27 (Agent-8 - V2 Tools Flattening)
"""

import warnings
import logging

warnings.warn(
    "⚠️ DEPRECATED: This tool has been migrated to tools_v2. "
    "Use 'python -m tools_v2.toolbelt health.snapshot' instead. "
    "This file will be removed in future version.",
    DeprecationWarning,
    stacklevel=2
)

logger = logging.getLogger(__name__)
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from src.utils.unified_utilities import get_logger, read_json
ROOT = Path(__file__).resolve().parents[1]
INDEX_FILE = ROOT / 'runtime' / 'agents_index.json'


def load_agents_index() ->dict[str, Any]:
    """Load the current agents index."""
    if not INDEX_FILE.exists():
        return {}
    try:
        with open(INDEX_FILE, encoding='utf-8') as f:
            return read_json(f)
    except Exception as e:
        get_logger(__name__).info(f'❌ Error loading agents index: {e}')
        return {}


def calculate_staleness(last_updated: str) ->tuple[int, str]:
    """Calculate staleness in minutes and return status."""
    try:
        if last_updated.endswith('Z'):
            last_updated = last_updated[:-1] + '+00:00'
        last_time = datetime.fromisoformat(last_updated)
        now = datetime.now(UTC)
        diff = now - last_time
        minutes = int(diff.total_seconds() / 60)
        if minutes > 15:
            return minutes, '🟠 STALE'
        elif minutes > 5:
            return minutes, '🟡 RECENT'
        else:
            return minutes, '🟢 FRESH'
    except Exception:
        return 999, '❌ INVALID'


def get_status_priority(status: str) ->int:
    """Get priority for sorting (lower number = higher priority)."""
    status_priority = {'CRITICAL': 1, 'BLOCKED': 2, 'ACTIVE': 3, 'PENDING':
        4, 'COMPLETE': 5, 'INACTIVE': 6}
    return status_priority.get(status.upper(), 7)


def format_agent_row(agent_id: str, agent_data: dict[str, Any]) ->str:
    """Format a single agent row for display."""
    status = agent_data.get('status', 'UNKNOWN')
    current_phase = agent_data.get('current_phase', 'UNKNOWN')
    next_milestone = agent_data.get('next_milestone', 'N/A')
    last_updated = agent_data.get('last_updated', 'N/A')
    staleness_min, staleness_status = calculate_staleness(last_updated)
    if len(current_phase) > 25:
        current_phase = current_phase[:22] + '...'
    if len(next_milestone) > 30:
        next_milestone = next_milestone[:27] + '...'
    return (
        f'{agent_id:<10} {status:<12} {staleness_status:<12} {current_phase:<25} {next_milestone:<30} {staleness_min:>3}m'
        )


def main():
    """Main function to display agent status snapshot."""
    agents = load_agents_index()
    if not agents:
        logger.info('❌ No agent data available')
        return
    logger.info('📊 AGENT STATUS SNAPSHOT')
    logger.info('=' * 120)
    logger.info(
        f"{'Agent ID':<10} {'Status':<12} {'Staleness':<12} {'Current Phase':<25} {'Next Milestone':<30} {'Age':>3}"
        )
    logger.info('-' * 120)
    for agent_id, data in agents.items():
        logger.info(format_agent_row(agent_id, data))
    logger.info('=' * 120)
    logger.info(f'Total agents: {len(agents)}')


if __name__ == '__main__':
    main()
