#!/usr/bin/env python3
"""Generate coordination metrics dashboard with real-time data."""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

def load_agent_status(agent: str) -> Dict:
    """Load agent status file."""
    status_file = Path(f'agent_workspaces/{agent}/status.json')
    if status_file.exists():
        try:
            return json.loads(status_file.read_text())
        except:
            return {}
    return {}

def calculate_coordination_metrics() -> Dict:
    """Calculate comprehensive coordination metrics."""
    agents = ['Agent-1', 'Agent-2', 'Agent-3', 'Agent-5', 'Agent-7', 'Agent-8']
    now = datetime.now()
    
    metrics = {
        'total_agents': len(agents),
        'active_agents': 0,
        'agents_with_coordination': 0,
        'total_tasks': 0,
        'coordination_mentions': 0,
        'recently_updated': 0,
        'coordination_pairs_active': 0,
        'coordination_pairs_total': 8,
        'agent_details': {}
    }
    
    # Coordination pairs from Captain broadcast
    pairs = [
        ('Agent-2', 'Agent-7'),
        ('Agent-2', 'Agent-1'),
        ('Agent-7', 'Agent-1'),
        ('Agent-3', 'Agent-7'),
        ('Agent-8', 'Agent-2'),
        ('Agent-8', 'Agent-7'),
        ('Agent-8', 'Agent-1'),
        ('Agent-8', 'Agent-3'),
    ]
    
    for agent in agents:
        status = load_agent_status(agent)
        if not status:
            continue
        
        is_active = status.get('status') == 'ACTIVE_AGENT_MODE'
        tasks = status.get('current_tasks', [])
        last_updated = status.get('last_updated', '')
        
        # Check for coordination mentions
        coord_keywords = ['coordinate', 'coordination', 'bilateral', 'agent-']
        has_coord = any(any(kw in str(t).lower() for kw in coord_keywords) for t in tasks)
        coord_count = sum(1 for t in tasks if any(kw in str(t).lower() for kw in coord_keywords))
        
        # Check if recently updated
        try:
            updated_dt = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
            age_minutes = (now - updated_dt).total_seconds() / 60
            is_recent = age_minutes < 60
        except:
            is_recent = False
        
        if is_active:
            metrics['active_agents'] += 1
        if has_coord:
            metrics['agents_with_coordination'] += 1
        if is_recent:
            metrics['recently_updated'] += 1
        
        metrics['total_tasks'] += len(tasks)
        metrics['coordination_mentions'] += coord_count
        
        metrics['agent_details'][agent] = {
            'active': is_active,
            'tasks': len(tasks),
            'coordination_mentions': coord_count,
            'has_coordination': has_coord,
            'recently_updated': is_recent,
            'last_updated': last_updated
        }
    
    # Check coordination pairs
    for agent1, agent2 in pairs:
        details1 = metrics['agent_details'].get(agent1, {})
        details2 = metrics['agent_details'].get(agent2, {})
        if details1.get('active') and details2.get('active') and (details1.get('has_coordination') or details2.get('has_coordination')):
            metrics['coordination_pairs_active'] += 1
    
    return metrics

def generate_dashboard(metrics: Dict) -> str:
    """Generate metrics dashboard."""
    dashboard = []
    dashboard.append("=" * 80)
    dashboard.append("COORDINATION METRICS DASHBOARD")
    dashboard.append("=" * 80)
    dashboard.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    dashboard.append("")
    
    # Overall metrics
    dashboard.append("OVERALL METRICS:")
    dashboard.append("-" * 80)
    dashboard.append(f"  Total Agents: {metrics['total_agents']}")
    dashboard.append(f"  Active Agents: {metrics['active_agents']}/{metrics['total_agents']} ({metrics['active_agents']/metrics['total_agents']*100:.1f}%)")
    dashboard.append(f"  Agents with Coordination: {metrics['agents_with_coordination']}/{metrics['total_agents']} ({metrics['agents_with_coordination']/metrics['total_agents']*100:.1f}%)")
    dashboard.append(f"  Total Tasks: {metrics['total_tasks']}")
    dashboard.append(f"  Coordination Mentions: {metrics['coordination_mentions']}")
    dashboard.append(f"  Recently Updated: {metrics['recently_updated']}/{metrics['total_agents']} ({metrics['recently_updated']/metrics['total_agents']*100:.1f}%)")
    dashboard.append(f"  Active Coordination Pairs: {metrics['coordination_pairs_active']}/{metrics['coordination_pairs_total']} ({metrics['coordination_pairs_active']/metrics['coordination_pairs_total']*100:.1f}%)")
    dashboard.append("")
    
    # Agent details
    dashboard.append("AGENT DETAILS:")
    dashboard.append("-" * 80)
    for agent, details in sorted(metrics['agent_details'].items()):
        status_icon = "✅" if details['active'] else "❌"
        coord_icon = "🔗" if details['has_coordination'] else "❌"
        recent_icon = "🕐" if details['recently_updated'] else "⏰"
        dashboard.append(f"{status_icon} {agent}:")
        dashboard.append(f"   Tasks: {details['tasks']}")
        dashboard.append(f"   {coord_icon} Coordination Mentions: {details['coordination_mentions']}")
        dashboard.append(f"   {recent_icon} Last Updated: {details['last_updated']}")
        dashboard.append("")
    
    # Health score
    health_score = (
        (metrics['active_agents'] / metrics['total_agents'] * 0.3) +
        (metrics['agents_with_coordination'] / metrics['total_agents'] * 0.3) +
        (metrics['coordination_pairs_active'] / metrics['coordination_pairs_total'] * 0.4)
    ) * 100
    
    dashboard.append("COORDINATION HEALTH SCORE:")
    dashboard.append("-" * 80)
    dashboard.append(f"  Score: {health_score:.1f}/100")
    if health_score >= 80:
        dashboard.append("  Status: ✅ EXCELLENT")
    elif health_score >= 60:
        dashboard.append("  Status: ⚠️  GOOD")
    elif health_score >= 40:
        dashboard.append("  Status: ⚠️  FAIR")
    else:
        dashboard.append("  Status: ❌ NEEDS IMPROVEMENT")
    dashboard.append("")
    dashboard.append("=" * 80)
    
    return "\n".join(dashboard)

if __name__ == '__main__':
    metrics = calculate_coordination_metrics()
    dashboard = generate_dashboard(metrics)
    print(dashboard)
    
    # Save dashboard
    dashboard_file = Path('tools/COORDINATION_METRICS_DASHBOARD.txt')
    dashboard_file.write_text(dashboard)
    print(f"\n✅ Dashboard saved to: {dashboard_file}")

