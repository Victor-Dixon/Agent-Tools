#!/usr/bin/env python3
"""
Observability Tools
===================

Tools for metrics, monitoring, and system health.

Author: Agent-7 - Repository Cloning Specialist
Created: 2025-10-13
"""

import logging
from typing import Any

from ..adapters.base_adapter import IToolAdapter

logger = logging.getLogger(__name__)


class MetricsSnapshotTool(IToolAdapter):
    """Get current metrics snapshot."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute metrics snapshot."""
        try:
            from src.obs.metrics import snapshot

            metrics = snapshot()

            return {"success": True, "metrics": metrics, "count": len(metrics)}

        except Exception as e:
            return {"success": False, "error": str(e)}


class MetricsTool(IToolAdapter):
    """Get specific metric value."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute metric retrieval."""
        try:
            from src.obs.metrics import get

            key = params.get("key")
            if not key:
                return {"success": False, "error": "key required"}

            value = get(key)

            return {"success": True, "key": key, "value": value}

        except Exception as e:
            return {"success": False, "error": str(e)}


class SystemHealthTool(IToolAdapter):
    """Check system health status."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute health check."""
        try:
            from src.obs.metrics import get

            # Check key metrics
            health = {
                "messaging": {
                    "sent": get("messaging.sent", 0),
                    "failed": get("messaging.failed", 0),
                },
                "msg_task": {
                    "ingest_ok": get("msg_task.ingest.ok", 0),
                    "ingest_fail": get("msg_task.ingest.fail", 0),
                    "duplicates": get("msg_task.dedupe.duplicate", 0),
                },
                "oss": {
                    "clone_ok": get("oss.clone.ok", 0),
                    "clone_fail": get("oss.clone.fail", 0),
                },
            }

            # Calculate success rates
            msg_total = health["messaging"]["sent"] + health["messaging"]["failed"]
            ingest_total = health["msg_task"]["ingest_ok"] + health["msg_task"]["ingest_fail"]

            health["messaging"]["success_rate"] = (
                (health["messaging"]["sent"] / msg_total * 100) if msg_total > 0 else 100
            )
            health["msg_task"]["success_rate"] = (
                (health["msg_task"]["ingest_ok"] / ingest_total * 100) if ingest_total > 0 else 100
            )

            return {"success": True, "health": health, "status": "operational"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class SLOCheckTool(IToolAdapter):
    """Check SLO compliance."""

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute SLO check."""
        try:
            from src.obs.metrics import get

            slos = {}

            # Message-Task SLOs
            ingest_ok = get("msg_task.ingest.ok", 0)
            ingest_fail = get("msg_task.ingest.fail", 0)
            ingest_total = ingest_ok + ingest_fail

            if ingest_total > 0:
                ingest_rate = (ingest_ok / ingest_total) * 100
                slos["msg_task_ingest"] = {
                    "current": ingest_rate,
                    "target": 99.0,
                    "passing": ingest_rate >= 99.0,
                }

            # Messaging SLOs
            msg_sent = get("messaging.sent", 0)
            msg_failed = get("messaging.failed", 0)
            msg_total = msg_sent + msg_failed

            if msg_total > 0:
                msg_rate = (msg_sent / msg_total) * 100
                slos["messaging_delivery"] = {
                    "current": msg_rate,
                    "target": 100.0,
                    "passing": msg_rate == 100.0,
                }

            passing = all(slo.get("passing", True) for slo in slos.values())

            return {
                "success": True,
                "slos": slos,
                "all_passing": passing,
                "checked": len(slos),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
