#!/usr/bin/env python3
"""
Swarm Coordination Patterns Analysis
====================================
Analyzes coordination patterns, force multiplier delegations, loop closures,
and communication bottlenecks to identify optimization opportunities.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-18
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict, Counter

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_agent_statuses() -> Dict[str, Dict[str, Any]]:
    """Load all agent status.json files."""
    agent_statuses = {}
    agent_workspaces = PROJECT_ROOT / 'agent_workspaces'

    for agent_dir in agent_workspaces.iterdir():
        if not agent_dir.is_dir():
            continue

        agent_id = agent_dir.name
        status_file = agent_dir / 'status.json'

        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    agent_statuses[agent_id] = json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading {status_file}: {e}")

    return agent_statuses


def analyze_force_multiplier_delegations(agent_statuses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze force multiplier delegations across agents."""
    delegations = []
    delegation_patterns = defaultdict(int)

    for agent_id, status in agent_statuses.items():
        delegations_list = status.get('delegations', [])
        for delegation in delegations_list:
            delegations.append({
                'from': agent_id,
                'to': delegation.get('to'),
                'task': delegation.get('task'),
                'status': delegation.get('status'),
                'priority': delegation.get('priority', 'UNKNOWN')
            })
            delegation_patterns[f"{agent_id} -> {delegation.get('to')}"] += 1

    # Analyze patterns
    delegation_by_status = Counter(d['status'] for d in delegations)
    delegation_by_priority = Counter(d['priority'] for d in delegations)

    return {
        'total_delegations': len(delegations),
        'delegations': delegations,
        'patterns': dict(delegation_patterns),
        'status_distribution': dict(delegation_by_status),
        'priority_distribution': dict(delegation_by_priority),
        'agents_most_active': dict(Counter(d['from'] for d in delegations).most_common(5)),
        'agents_most_delegated_to': dict(Counter(d['to'] for d in delegations).most_common(5))
    }


def analyze_coordination_loops(agent_statuses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze coordination loops and closure rates."""
    all_coordinations = []
    coordination_pairs = defaultdict(list)
    completed_coordinations = []
    active_coordinations = []

    for agent_id, status in agent_statuses.items():
        coordinations = status.get('active_coordinations', [])
        for coord in coordinations:
            # Handle both dict and string formats
            if isinstance(coord, str):
                continue  # Skip string entries

            partner = coord.get('partner', 'UNKNOWN')
            phase = coord.get('phase', 'UNKNOWN')
            coord_status = coord.get('status', 'UNKNOWN')

            coord_data = {
                'agent': agent_id,
                'partner': partner,
                'type': coord.get('type', 'unknown'),
                'task': coord.get('task', ''),
                'phase': phase,
                'status': coord_status
            }
            all_coordinations.append(coord_data)

            # Track pairs
            pair_key = tuple(sorted([agent_id, partner]))
            coordination_pairs[pair_key].append(coord_data)

            # Categorize
            if 'complete' in phase.lower() or 'complete' in coord_status.lower():
                completed_coordinations.append(coord_data)
            else:
                active_coordinations.append(coord_data)

    # Find bilateral coordinations
    bilateral_count = sum(
        1 for c in all_coordinations if c['type'] == 'bilateral')

    # Calculate closure rate
    total_historical = len(completed_coordinations) + len(active_coordinations)
    closure_rate = (len(completed_coordinations) /
                    total_historical * 100) if total_historical > 0 else 0

    # Find most active coordination pairs
    pair_activity = {f"{k[0]} ↔ {k[1]}": len(
        v) for k, v in coordination_pairs.items()}

    return {
        'total_coordinations': len(all_coordinations),
        'active_coordinations': len(active_coordinations),
        'completed_coordinations': len(completed_coordinations),
        'bilateral_count': bilateral_count,
        'closure_rate': closure_rate,
        'most_active_pairs': dict(sorted(pair_activity.items(), key=lambda x: x[1], reverse=True)[:10]),
        'coordination_by_type': dict(Counter(c['type'] for c in all_coordinations)),
        'coordination_by_phase': dict(Counter(c['phase'] for c in all_coordinations)),
        'all_coordinations': all_coordinations,
        'active_coordinations_list': active_coordinations,
        'completed_coordinations_list': completed_coordinations
    }


def analyze_communication_bottlenecks(agent_statuses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze communication bottlenecks and patterns."""
    # Count active coordinations per agent
    coordinations_per_agent = defaultdict(int)
    delegations_per_agent = defaultdict(int)
    tasks_per_agent = defaultdict(int)

    for agent_id, status in agent_statuses.items():
        coordinations_per_agent[agent_id] = len(
            status.get('active_coordinations', []))
        delegations_per_agent[agent_id] = len(status.get('delegations', []))
        tasks_per_agent[agent_id] = len(status.get('current_tasks', []))

    # Identify bottlenecks (agents with high coordination/task load)
    bottleneck_threshold_coord = 3
    bottleneck_threshold_tasks = 5

    bottlenecks = []
    for agent_id in coordinations_per_agent:
        coord_count = coordinations_per_agent[agent_id]
        task_count = tasks_per_agent[agent_id]

        if coord_count >= bottleneck_threshold_coord or task_count >= bottleneck_threshold_tasks:
            bottlenecks.append({
                'agent': agent_id,
                'active_coordinations': coord_count,
                'current_tasks': task_count,
                'delegations': delegations_per_agent[agent_id],
                'severity': 'HIGH' if coord_count >= 4 or task_count >= 7 else 'MEDIUM'
            })

    # Communication load distribution
    load_distribution = {
        'low_load': sum(1 for a in coordinations_per_agent.values() if a <= 1),
        'medium_load': sum(1 for a in coordinations_per_agent.values() if 2 <= a <= 3),
        'high_load': sum(1 for a in coordinations_per_agent.values() if a >= 4)
    }

    return {
        'coordinations_per_agent': dict(coordinations_per_agent),
        'tasks_per_agent': dict(tasks_per_agent),
        'delegations_per_agent': dict(delegations_per_agent),
        'bottlenecks': sorted(bottlenecks, key=lambda x: (x['active_coordinations'], x['current_tasks']), reverse=True),
        'load_distribution': load_distribution,
        'total_agents': len(agent_statuses),
        'agents_overloaded': len(bottlenecks)
    }


def identify_optimization_opportunities(
    delegations: Dict[str, Any],
    coordinations: Dict[str, Any],
    bottlenecks: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Identify optimization opportunities."""
    opportunities = []

    # 1. High delegation patterns
    if delegations['total_delegations'] > 0:
        top_delegation_pattern = max(
            delegations['patterns'].items(), key=lambda x: x[1])
        if top_delegation_pattern[1] > 2:
            opportunities.append({
                'type': 'DELEGATION_PATTERN',
                'severity': 'MEDIUM',
                'description': f"Recurring delegation pattern: {top_delegation_pattern[0]} ({top_delegation_pattern[1]} times)",
                'recommendation': f"Consider establishing permanent coordination channel or workflow automation between these agents"
            })

    # 2. Low closure rate
    if coordinations['closure_rate'] < 50:
        opportunities.append({
            'type': 'LOW_CLOSURE_RATE',
            'severity': 'HIGH',
            'description': f"Low coordination closure rate: {coordinations['closure_rate']:.1f}%",
            'recommendation': "Investigate why coordinations remain active. May indicate missing completion criteria or status updates"
        })

    # 3. Communication bottlenecks
    if bottlenecks['agents_overloaded'] > 0:
        top_bottleneck = bottlenecks['bottlenecks'][0]
        opportunities.append({
            'type': 'COMMUNICATION_BOTTLENECK',
            'severity': top_bottleneck['severity'],
            'description': f"{top_bottleneck['agent']} has {top_bottleneck['active_coordinations']} active coordinations and {top_bottleneck['current_tasks']} tasks",
            'recommendation': f"Consider redistributing work from {top_bottleneck['agent']} or establishing parallel execution streams"
        })

    # 4. Uneven load distribution
    if bottlenecks['load_distribution']['high_load'] > bottlenecks['load_distribution']['low_load']:
        opportunities.append({
            'type': 'UNEVEN_LOAD',
            'severity': 'MEDIUM',
            'description': f"Uneven communication load: {bottlenecks['load_distribution']['high_load']} agents overloaded vs {bottlenecks['load_distribution']['low_load']} underutilized",
            'recommendation': "Rebalance coordination workload across agents for better force multiplication"
        })

    # 5. Incomplete bilateral coordinations
    if coordinations['bilateral_count'] > 0:
        active_bilateral = sum(1 for c in coordinations.get(
            'active_coordinations_list', []) if c.get('type') == 'bilateral')
        if active_bilateral > coordinations['bilateral_count'] * 0.5:
            opportunities.append({
                'type': 'BILATERAL_STALL',
                'severity': 'MEDIUM',
                'description': f"High number of active bilateral coordinations: {active_bilateral}",
                'recommendation': "Review bilateral coordination protocols and ensure clear handoff criteria"
            })

    return opportunities


def generate_report(
    delegations: Dict[str, Any],
    coordinations: Dict[str, Any],
    bottlenecks: Dict[str, Any],
    opportunities: List[Dict[str, Any]]
) -> str:
    """Generate markdown report."""
    report = f"""# Swarm Coordination Patterns Analysis

**Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Agent**: Agent-5 (Business Intelligence Specialist)  
**Purpose**: Analyze force multiplier delegations, loop closures, communication bottlenecks, and optimization opportunities

---

## 📊 Force Multiplier Delegations

### Summary

- **Total Delegations**: {delegations['total_delegations']}
- **Status Distribution**: {', '.join(f'{k}: {v}' for k, v in delegations['status_distribution'].items())}
- **Priority Distribution**: {', '.join(f'{k}: {v}' for k, v in delegations['priority_distribution'].items())}

### Most Active Delegators

"""

    for agent, count in list(delegations['agents_most_active'].items())[:5]:
        report += f"- **{agent}**: {count} delegations\n"

    report += f"""
### Most Delegated-To Agents

"""

    for agent, count in list(delegations['agents_most_delegated_to'].items())[:5]:
        report += f"- **{agent}**: {count} delegations received\n"

    if delegations['patterns']:
        report += f"""
### Top Delegation Patterns

"""
        for pattern, count in sorted(delegations['patterns'].items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"- **{pattern}**: {count} times\n"

    report += f"""

---

## 🔄 Coordination Loops & Closure Rates

### Summary

- **Total Coordinations**: {coordinations['total_coordinations']}
- **Active Coordinations**: {coordinations['active_coordinations']}
- **Completed Coordinations**: {coordinations['completed_coordinations']}
- **Bilateral Coordinations**: {coordinations['bilateral_count']}
- **Closure Rate**: {coordinations['closure_rate']:.1f}%

### Most Active Coordination Pairs

"""

    for pair, count in list(coordinations['most_active_pairs'].items())[:10]:
        report += f"- **{pair}**: {count} coordinations\n"

    report += f"""
### Coordination Distribution

- **By Type**: {', '.join(f'{k}: {v}' for k, v in coordinations['coordination_by_type'].items())}
- **By Phase**: {', '.join(f'{k}: {v}' for k, v in list(coordinations['coordination_by_phase'].items())[:5])}

---

## 🚧 Communication Bottlenecks

### Summary

- **Total Agents Analyzed**: {bottlenecks['total_agents']}
- **Agents Overloaded**: {bottlenecks['agents_overloaded']}

### Load Distribution

- **Low Load** (≤1 coordinations): {bottlenecks['load_distribution']['low_load']} agents
- **Medium Load** (2-3 coordinations): {bottlenecks['load_distribution']['medium_load']} agents
- **High Load** (≥4 coordinations): {bottlenecks['load_distribution']['high_load']} agents

### Identified Bottlenecks

"""

    for bottleneck in bottlenecks['bottlenecks'][:5]:
        report += f"""
- **{bottleneck['agent']}** ({bottleneck['severity']}):
  - Active Coordinations: {bottleneck['active_coordinations']}
  - Current Tasks: {bottleneck['current_tasks']}
  - Delegations: {bottleneck['delegations']}
"""

    report += f"""
---

## 💡 Optimization Opportunities

**Total Opportunities Identified**: {len(opportunities)}

"""

    for opp in opportunities:
        severity_emoji = '🔴' if opp['severity'] == 'HIGH' else '🟡'
        report += f"""
### {severity_emoji} {opp['type']}

**Description**: {opp['description']}

**Recommendation**: {opp['recommendation']}

"""

    report += f"""
---

## 📋 Key Findings

### Force Multiplication Effectiveness

"""

    if delegations['total_delegations'] > 0:
        report += f"- Delegation system active: {delegations['total_delegations']} delegations tracked\n"

    if coordinations['bilateral_count'] > 0:
        report += f"- Bilateral coordination active: {coordinations['bilateral_count']} bilateral coordinations\n"

    report += f"""
### Communication Health

- Closure Rate: {coordinations['closure_rate']:.1f}% ({'✅ Good' if coordinations['closure_rate'] >= 50 else '⚠️ Needs Improvement'})
- Active Coordinations: {coordinations['active_coordinations']} ({'⚠️ High' if coordinations['active_coordinations'] > 10 else '✅ Manageable'})
- Communication Bottlenecks: {len(bottlenecks['bottlenecks'])} agents overloaded

### Optimization Priority

"""

    high_priority = [o for o in opportunities if o['severity'] == 'HIGH']
    if high_priority:
        report += f"- **HIGH Priority**: {len(high_priority)} optimization(s) identified\n"

    medium_priority = [o for o in opportunities if o['severity'] == 'MEDIUM']
    if medium_priority:
        report += f"- **MEDIUM Priority**: {len(medium_priority)} optimization(s) identified\n"

    report += """

---

## 🎯 Recommendations

1. **Monitor Closure Rates**: Track coordination completion to ensure loops close properly
2. **Balance Communication Load**: Redistribute work from overloaded agents to underutilized ones
3. **Establish Patterns**: For recurring delegations, consider permanent coordination channels
4. **Define Completion Criteria**: Ensure all coordinations have clear completion criteria
5. **Parallel Execution**: Leverage force multiplication by enabling more parallel coordination streams

---

🐝 **WE. ARE. SWARM. ⚡🔥**

"""

    return report


def main():
    """Main entry point."""
    print("🚀 Starting Swarm Coordination Patterns Analysis...")
    print()

    # Load agent statuses
    print("📊 Loading agent statuses...")
    agent_statuses = load_agent_statuses()
    print(f"✅ Loaded {len(agent_statuses)} agent status files\n")

    # Analyze delegations
    print("🔍 Analyzing force multiplier delegations...")
    delegations = analyze_force_multiplier_delegations(agent_statuses)
    print(f"✅ Found {delegations['total_delegations']} delegations\n")

    # Analyze coordinations
    print("🔄 Analyzing coordination loops...")
    coordinations = analyze_coordination_loops(agent_statuses)
    print(
        f"✅ Found {coordinations['total_coordinations']} coordinations (closure rate: {coordinations['closure_rate']:.1f}%)\n")

    # Analyze bottlenecks
    print("🚧 Analyzing communication bottlenecks...")
    bottlenecks = analyze_communication_bottlenecks(agent_statuses)
    print(
        f"✅ Identified {bottlenecks['agents_overloaded']} overloaded agents\n")

    # Identify opportunities
    print("💡 Identifying optimization opportunities...")
    opportunities = identify_optimization_opportunities(
        delegations, coordinations, bottlenecks)
    print(f"✅ Identified {len(opportunities)} optimization opportunities\n")

    # Generate report
    print("📄 Generating report...")
    report = generate_report(delegations, coordinations,
                             bottlenecks, opportunities)
    report_path = PROJECT_ROOT / \
        'docs/technical_debt/SWARM_COORDINATION_PATTERNS_ANALYSIS.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Report saved to: {report_path}\n")

    # Print summary
    print("📊 SUMMARY:")
    print(f"   Delegations: {delegations['total_delegations']}")
    print(
        f"   Coordinations: {coordinations['total_coordinations']} ({coordinations['active_coordinations']} active)")
    print(f"   Closure Rate: {coordinations['closure_rate']:.1f}%")
    print(
        f"   Bottlenecks: {bottlenecks['agents_overloaded']} agents overloaded")
    print(f"   Optimization Opportunities: {len(opportunities)}")
    print()

    if opportunities:
        print("🎯 TOP OPTIMIZATION OPPORTUNITIES:")
        for opp in opportunities[:3]:
            print(f"   [{opp['severity']}] {opp['type']}: {opp['description']}")


if __name__ == '__main__':
    main()

