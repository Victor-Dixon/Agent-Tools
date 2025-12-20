#!/usr/bin/env python3
"""Validate bilateral coordination pairs are active and working."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

def load_agent_status(agent: str) -> Dict:
    """Load agent status file."""
    status_file = Path(f'agent_workspaces/{agent}/status.json')
    if status_file.exists():
        try:
            return json.loads(status_file.read_text())
        except:
            return {}
    return {}

def check_coordination_pair(agent1: str, agent2: str, description: str) -> Tuple[bool, List[str]]:
    """Check if a coordination pair is active."""
    status1 = load_agent_status(agent1)
    status2 = load_agent_status(agent2)
    
    issues = []
    active = True
    
    # Check both agents are active
    if status1.get('status') != 'ACTIVE_AGENT_MODE':
        issues.append(f"{agent1} status: {status1.get('status', 'UNKNOWN')}")
        active = False
    
    if status2.get('status') != 'ACTIVE_AGENT_MODE':
        issues.append(f"{agent2} status: {status2.get('status', 'UNKNOWN')}")
        active = False
    
    # Check for coordination mentions
    tasks1 = status1.get('current_tasks', [])
    tasks2 = status2.get('current_tasks', [])
    
    coord_keywords = ['coordinate', 'coordination', 'bilateral', agent1.lower(), agent2.lower()]
    has_coord1 = any(any(kw in str(t).lower() for kw in coord_keywords) for t in tasks1)
    has_coord2 = any(any(kw in str(t).lower() for kw in coord_keywords) for t in tasks2)
    
    if not has_coord1:
        issues.append(f"{agent1} has no coordination mentions")
    if not has_coord2:
        issues.append(f"{agent2} has no coordination mentions")
    
    return active and (has_coord1 or has_coord2), issues

def validate_all_coordination_pairs() -> Dict:
    """Validate all coordination pairs from Captain broadcast."""
    pairs = [
        (('Agent-2', 'Agent-7'), 'V2 violations refactoring'),
        (('Agent-2', 'Agent-1'), 'Integration testing (via Agent-2/Agent-7)'),
        (('Agent-7', 'Agent-1'), 'Integration testing (via Agent-2/Agent-7)'),
        (('Agent-3', 'Agent-7'), 'WordPress web interface'),
        (('Agent-8', 'Agent-2'), 'QA review (Agent-2)'),
        (('Agent-8', 'Agent-7'), 'QA review (Agent-7)'),
        (('Agent-8', 'Agent-1'), 'QA review (Agent-1)'),
        (('Agent-8', 'Agent-3'), 'QA review (Agent-3)'),
    ]
    
    results = {}
    for (agent1, agent2), description in pairs:
        is_active, issues = check_coordination_pair(agent1, agent2, description)
        results[f"{agent1} ↔ {agent2}"] = {
            'description': description,
            'active': is_active,
            'issues': issues
        }
    
    return results

def generate_validation_report(results: Dict) -> str:
    """Generate validation report."""
    report = []
    report.append("=" * 80)
    report.append("BILATERAL COORDINATION VALIDATION REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    active_count = sum(1 for r in results.values() if r['active'])
    total_count = len(results)
    
    report.append("COORDINATION PAIRS VALIDATION:")
    report.append("-" * 80)
    
    for pair_name, result in results.items():
        status_icon = "✅" if result['active'] else "❌"
        report.append(f"{status_icon} {pair_name}: {result['description']}")
        if result['issues']:
            for issue in result['issues']:
                report.append(f"   ⚠️  {issue}")
        report.append("")
    
    report.append("VALIDATION SUMMARY:")
    report.append("-" * 80)
    report.append(f"  Active Pairs: {active_count}/{total_count}")
    report.append(f"  Inactive Pairs: {total_count - active_count}/{total_count}")
    report.append("")
    
    if active_count == total_count:
        report.append("✅ ALL COORDINATION PAIRS ACTIVE")
    elif active_count >= total_count * 0.75:
        report.append("⚠️  MOST COORDINATION PAIRS ACTIVE")
    else:
        report.append("❌ SOME COORDINATION PAIRS INACTIVE")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)

if __name__ == '__main__':
    results = validate_all_coordination_pairs()
    report = generate_validation_report(results)
    print(report)
    
    # Save report
    report_file = Path('tools/BILATERAL_COORDINATION_VALIDATION.txt')
    report_file.write_text(report)
    print(f"\n✅ Validation report saved to: {report_file}")

