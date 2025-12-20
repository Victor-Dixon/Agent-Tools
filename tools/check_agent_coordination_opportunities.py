#!/usr/bin/env python3
"""Check agent statuses and identify coordination opportunities."""
import json
from pathlib import Path
from datetime import datetime

agents = ['Agent-1', 'Agent-2', 'Agent-3', 'Agent-5', 'Agent-7', 'Agent-8']
statuses = {}

for agent in agents:
    status_file = Path(f'agent_workspaces/{agent}/status.json')
    if status_file.exists():
        try:
            data = json.loads(status_file.read_text())
            statuses[agent] = {
                'status': data.get('status', 'UNKNOWN'),
                'mission': data.get('current_mission', 'N/A')[:80],
                'last_updated': data.get('last_updated', 'N/A'),
                'tasks': len(data.get('current_tasks', []))
            }
        except Exception as e:
            statuses[agent] = {'error': str(e)}
    else:
        statuses[agent] = {'error': 'No status file'}

print("Agent Status Summary:")
print("=" * 80)
for agent, info in statuses.items():
    if 'error' in info:
        print(f"{agent}: {info['error']}")
    else:
        print(f"{agent}: {info['status']}")
        print(f"  Mission: {info['mission']}")
        print(f"  Last Updated: {info['last_updated']}")
        print(f"  Active Tasks: {info['tasks']}")
        print()

