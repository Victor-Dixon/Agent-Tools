#!/usr/bin/env python3
"""
Monitoring Dashboard Generator
==============================

Generates a simple HTML dashboard for infrastructure health monitoring.

Usage:
    python tools/generate_monitoring_dashboard.py [--output dashboard.html]

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def generate_dashboard(
    output_path: Path,
    alert_dir: Optional[Path] = None
) -> None:
    """
    Generate monitoring dashboard HTML.
    
    Args:
        output_path: Output HTML file path
        alert_dir: Directory containing alert history
    """
    alert_dir = alert_dir or project_root / "alerts"
    
    # Load recent alerts
    alerts = []
    history_file = alert_dir / "alert_history.jsonl"
    if history_file.exists():
        with history_file.open("r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-50:]:  # Last 50 alerts
                try:
                    alerts.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    
    # Count alerts by level
    alert_counts = {"info": 0, "warning": 0, "critical": 0}
    for alert in alerts:
        level = alert.get("level", "info")
        if level in alert_counts:
            alert_counts[level] += 1
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infrastructure Monitoring Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        .timestamp {{
            opacity: 0.9;
            font-size: 0.9rem;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        .stat-card .value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .stat-card.info .value {{ color: #3498db; }}
        .stat-card.warning .value {{ color: #f39c12; }}
        .stat-card.critical .value {{ color: #e74c3c; }}
        .alerts {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .alerts h2 {{
            margin-bottom: 1rem;
            color: #333;
        }}
        .alert-item {{
            padding: 1rem;
            border-left: 4px solid #ddd;
            margin-bottom: 1rem;
            border-radius: 4px;
            background: #f9f9f9;
        }}
        .alert-item.info {{
            border-left-color: #3498db;
        }}
        .alert-item.warning {{
            border-left-color: #f39c12;
        }}
        .alert-item.critical {{
            border-left-color: #e74c3c;
            background: #fee;
        }}
        .alert-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        .alert-title {{
            font-weight: bold;
            color: #333;
        }}
        .alert-time {{
            color: #666;
            font-size: 0.85rem;
        }}
        .alert-message {{
            color: #555;
            margin-bottom: 0.5rem;
        }}
        .alert-source {{
            color: #999;
            font-size: 0.85rem;
        }}
        .refresh-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            margin-top: 1rem;
        }}
        .refresh-btn:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏥 Infrastructure Monitoring Dashboard</h1>
            <div class="timestamp">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </header>
        
        <div class="stats">
            <div class="stat-card info">
                <h3>Info Alerts</h3>
                <div class="value">{alert_counts['info']}</div>
            </div>
            <div class="stat-card warning">
                <h3>Warning Alerts</h3>
                <div class="value">{alert_counts['warning']}</div>
            </div>
            <div class="stat-card critical">
                <h3>Critical Alerts</h3>
                <div class="value">{alert_counts['critical']}</div>
            </div>
            <div class="stat-card">
                <h3>Total Alerts</h3>
                <div class="value">{len(alerts)}</div>
            </div>
        </div>
        
        <div class="alerts">
            <h2>Recent Alerts</h2>
            {generate_alert_list(alerts)}
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        </div>
    </div>
</body>
</html>"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Dashboard generated: {output_path}")


def generate_alert_list(alerts: List[Dict]) -> str:
    """Generate HTML for alert list."""
    if not alerts:
        return "<p>No alerts found.</p>"
    
    html_items = []
    for alert in reversed(alerts[-20:]):  # Show last 20, most recent first
        level = alert.get("level", "info")
        title = alert.get("title", "Alert")
        message = alert.get("message", "")
        source = alert.get("source", "unknown")
        timestamp = alert.get("timestamp", "")
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = timestamp
        
        html_items.append(f"""
            <div class="alert-item {level}">
                <div class="alert-header">
                    <div class="alert-title">{title}</div>
                    <div class="alert-time">{time_str}</div>
                </div>
                <div class="alert-message">{message}</div>
                <div class="alert-source">Source: {source}</div>
            </div>
        """)
    
    return "".join(html_items)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate infrastructure monitoring dashboard"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=project_root / "docs" / "monitoring_dashboard.html",
        help='Output HTML file path'
    )
    parser.add_argument(
        '--alert-dir',
        type=Path,
        default=project_root / "alerts",
        help='Alert history directory'
    )
    
    args = parser.parse_args()
    
    generate_dashboard(args.output, args.alert_dir)


if __name__ == '__main__':
    main()

