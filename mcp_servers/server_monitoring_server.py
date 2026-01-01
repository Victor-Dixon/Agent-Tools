#!/usr/bin/env python3
"""
MCP Server for Game Server Performance Monitoring
==================================================

Exposes server monitoring operations via Model Context Protocol.
Enables AI agents to monitor and optimize game server performance.

Tools:
- collect_metrics: Collect current server metrics
- analyze_performance: Analyze metrics and get recommendations
- check_alerts: Check for active alerts
- configure_alerts: Configure alert channels
- get_weekly_report: Generate weekly performance report
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "server_monitoring"))

try:
    from core.metrics_collector import MetricsCollector, ServerMetrics
    from core.performance_analyzer import PerformanceAnalyzer
    from core.alert_manager import AlertManager, AlertConfig, AlertChannel
    HAS_MONITORING = True
except ImportError as e:
    HAS_MONITORING = False
    import_error = str(e)


def collect_metrics(
    game_path: str,
    process_name: str = "",
) -> Dict[str, Any]:
    """Collect current server performance metrics."""
    if not HAS_MONITORING:
        return {"success": False, "error": f"Monitoring not available: {import_error}"}
    
    try:
        collector = MetricsCollector(
            game_path=Path(game_path),
            process_name=process_name,
        )
        metrics = collector.collect()
        return {"success": True, "metrics": metrics.to_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_performance(
    game_path: str,
    process_name: str = "",
    history_minutes: int = 60,
) -> Dict[str, Any]:
    """Analyze server performance and get recommendations."""
    if not HAS_MONITORING:
        return {"success": False, "error": "Monitoring not available"}
    
    try:
        collector = MetricsCollector(
            game_path=Path(game_path),
            process_name=process_name,
        )
        
        # Collect current metrics
        current = collector.collect()
        history = collector.get_history(history_minutes)
        
        # Analyze
        analyzer = PerformanceAnalyzer()
        report = analyzer.analyze(current, history)
        
        return {"success": True, "report": report.to_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_alerts() -> Dict[str, Any]:
    """Check for active/unacknowledged alerts."""
    if not HAS_MONITORING:
        return {"success": False, "error": "Monitoring not available"}
    
    try:
        manager = AlertManager()
        active = manager.get_active_alerts()
        summary = manager.get_alert_summary()
        
        return {
            "success": True,
            "active_alerts": [a.to_dict() for a in active],
            "summary": summary,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def acknowledge_alert(alert_id: str) -> Dict[str, Any]:
    """Acknowledge an alert."""
    if not HAS_MONITORING:
        return {"success": False, "error": "Monitoring not available"}
    
    try:
        manager = AlertManager()
        success = manager.acknowledge_alert(alert_id)
        return {"success": success, "alert_id": alert_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


def configure_discord_alerts(
    webhook_url: str,
    min_severity: str = "warning",
    cooldown_minutes: int = 15,
) -> Dict[str, Any]:
    """Configure Discord alert channel."""
    if not HAS_MONITORING:
        return {"success": False, "error": "Monitoring not available"}
    
    try:
        from core.alert_manager import AlertConfig, AlertChannel, IssueSeverity
        
        manager = AlertManager()
        
        # Remove existing Discord config
        manager.remove_channel(AlertChannel.DISCORD)
        
        # Add new config
        config = AlertConfig(
            channel=AlertChannel.DISCORD,
            url=webhook_url,
            min_severity=IssueSeverity(min_severity),
            cooldown_minutes=cooldown_minutes,
        )
        manager.add_channel(config)
        
        return {"success": True, "configured": "discord"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_metric_history(
    game_path: str,
    process_name: str = "",
    minutes: int = 60,
) -> Dict[str, Any]:
    """Get metrics history for the specified duration."""
    if not HAS_MONITORING:
        return {"success": False, "error": "Monitoring not available"}
    
    try:
        collector = MetricsCollector(
            game_path=Path(game_path),
            process_name=process_name,
        )
        
        history = collector.get_history(minutes)
        averages = collector.get_averages(minutes)
        
        return {
            "success": True,
            "history_count": len(history),
            "averages": averages,
            "history": [m.to_dict() for m in history[-20:]],  # Last 20 samples
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_weekly_report(
    game_path: str,
    process_name: str = "",
) -> Dict[str, Any]:
    """Generate weekly performance report."""
    if not HAS_MONITORING:
        return {"success": False, "error": "Monitoring not available"}
    
    try:
        collector = MetricsCollector(
            game_path=Path(game_path),
            process_name=process_name,
        )
        
        # Get week of history (would need persistent storage in production)
        history = collector.get_history(minutes=60*24*7)
        
        analyzer = PerformanceAnalyzer()
        report = analyzer.generate_weekly_report(history)
        
        return {"success": True, "report": report}
    except Exception as e:
        return {"success": False, "error": str(e)}


# MCP Server Protocol
def main():
    """MCP server main loop."""
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "collect_metrics": {
                                "description": "Collect current server performance metrics (CPU, RAM, tick rate, players)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string", "description": "Path to game server"},
                                        "process_name": {"type": "string", "description": "Server process name"},
                                    },
                                    "required": ["game_path"],
                                },
                            },
                            "analyze_performance": {
                                "description": "Analyze server performance and get optimization recommendations",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string"},
                                        "process_name": {"type": "string"},
                                        "history_minutes": {"type": "integer", "default": 60},
                                    },
                                    "required": ["game_path"],
                                },
                            },
                            "check_alerts": {
                                "description": "Check for active performance alerts",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            "acknowledge_alert": {
                                "description": "Acknowledge a performance alert",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "alert_id": {"type": "string"},
                                    },
                                    "required": ["alert_id"],
                                },
                            },
                            "configure_discord_alerts": {
                                "description": "Configure Discord webhook for alerts",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "webhook_url": {"type": "string"},
                                        "min_severity": {"type": "string", "enum": ["info", "warning", "critical"]},
                                        "cooldown_minutes": {"type": "integer", "default": 15},
                                    },
                                    "required": ["webhook_url"],
                                },
                            },
                            "get_metric_history": {
                                "description": "Get historical metrics and averages",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string"},
                                        "process_name": {"type": "string"},
                                        "minutes": {"type": "integer", "default": 60},
                                    },
                                    "required": ["game_path"],
                                },
                            },
                            "get_weekly_report": {
                                "description": "Generate weekly performance summary report",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "game_path": {"type": "string"},
                                        "process_name": {"type": "string"},
                                    },
                                    "required": ["game_path"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "server-monitoring", "version": "1.0.0"},
                },
            }
        )
    )

    # Handle tool calls
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "collect_metrics":
                    result = collect_metrics(**arguments)
                elif tool_name == "analyze_performance":
                    result = analyze_performance(**arguments)
                elif tool_name == "check_alerts":
                    result = check_alerts()
                elif tool_name == "acknowledge_alert":
                    result = acknowledge_alert(**arguments)
                elif tool_name == "configure_discord_alerts":
                    result = configure_discord_alerts(**arguments)
                elif tool_name == "get_metric_history":
                    result = get_metric_history(**arguments)
                elif tool_name == "get_weekly_report":
                    result = get_weekly_report(**arguments)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
                        }
                    )
                )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if 'request' in dir() else None,
                        "error": {"code": -32603, "message": str(e)},
                    }
                )
            )


if __name__ == "__main__":
    main()
