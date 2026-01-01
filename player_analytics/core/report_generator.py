#!/usr/bin/env python3
"""
Report Generator
================

Generates formatted reports from analytics data.
Supports multiple output formats and scheduling.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .analytics_engine import AnalyticsEngine
from .player_database import PlayerDatabase

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates analytics reports.
    
    Features:
    - Daily/weekly/monthly reports
    - Multiple formats (dict, markdown, discord embed)
    - Scheduled report generation
    - Report history
    """
    
    def __init__(
        self,
        analytics: Optional[AnalyticsEngine] = None,
        reports_path: Optional[Path] = None,
    ):
        self.analytics = analytics or AnalyticsEngine()
        self.reports_path = reports_path or Path.home() / ".player_analytics" / "reports"
        self.reports_path.mkdir(parents=True, exist_ok=True)
    
    def generate_daily_report(
        self,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a daily analytics report.
        
        Args:
            date: Date for report (default: yesterday)
            
        Returns:
            Daily report data
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        engagement = self.analytics.get_engagement_metrics(days=1)
        peak_hours = self.analytics.get_peak_hours(days=1)
        leaderboard = self.analytics.get_leaderboard(metric="playtime", limit=5)
        
        report = {
            "report_type": "daily",
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "unique_players": engagement.get("unique_players", 0),
                "total_sessions": engagement.get("total_sessions", 0),
                "total_playtime_hours": engagement.get("total_playtime_hours", 0),
                "avg_session_minutes": engagement.get("avg_session_minutes", 0),
            },
            "peak_hour": peak_hours.get("peak_hour", {}),
            "top_players": leaderboard,
        }
        
        # Save report
        self._save_report(report, f"daily_{date}")
        
        return report
    
    def generate_weekly_report(
        self,
        week_start: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a weekly analytics report.
        
        Args:
            week_start: Start date of week (default: last week)
            
        Returns:
            Weekly report data
        """
        if week_start is None:
            # Last week Monday
            today = datetime.now()
            week_start = (today - timedelta(days=today.weekday() + 7)).strftime("%Y-%m-%d")
        
        engagement = self.analytics.get_engagement_metrics(days=7)
        retention = self.analytics.get_retention_metrics()
        peak_hours = self.analytics.get_peak_hours(days=7)
        segments = self.analytics.get_player_segments()
        leaderboard = self.analytics.get_leaderboard(metric="playtime", limit=10)
        servers = self.analytics.get_server_comparison(days=7)
        
        report = {
            "report_type": "weekly",
            "week_start": week_start,
            "generated_at": datetime.now().isoformat(),
            "engagement": engagement,
            "retention": retention,
            "peak_times": peak_hours,
            "player_segments": segments,
            "leaderboard": leaderboard,
            "server_comparison": servers,
        }
        
        # Save report
        self._save_report(report, f"weekly_{week_start}")
        
        return report
    
    def generate_monthly_report(
        self,
        month: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a monthly analytics report.
        
        Args:
            month: Month in YYYY-MM format (default: last month)
            
        Returns:
            Monthly report data
        """
        if month is None:
            today = datetime.now()
            first_of_month = today.replace(day=1)
            last_month = first_of_month - timedelta(days=1)
            month = last_month.strftime("%Y-%m")
        
        engagement = self.analytics.get_engagement_metrics(days=30)
        retention = self.analytics.get_retention_metrics()
        segments = self.analytics.get_player_segments()
        leaderboard = self.analytics.get_leaderboard(metric="playtime", limit=20)
        
        report = {
            "report_type": "monthly",
            "month": month,
            "generated_at": datetime.now().isoformat(),
            "engagement": engagement,
            "retention": retention,
            "player_segments": segments,
            "leaderboard": leaderboard,
            "highlights": self._generate_highlights(engagement, retention),
        }
        
        # Save report
        self._save_report(report, f"monthly_{month}")
        
        return report
    
    def _generate_highlights(
        self,
        engagement: Dict,
        retention: Dict,
    ) -> List[str]:
        """Generate report highlights."""
        highlights = []
        
        # Engagement highlights
        if engagement.get("unique_players", 0) > 0:
            highlights.append(
                f"📊 {engagement['unique_players']} unique players this period"
            )
        
        if engagement.get("total_playtime_hours", 0) > 0:
            highlights.append(
                f"⏱️ {engagement['total_playtime_hours']} total hours played"
            )
        
        avg_session = engagement.get("avg_session_minutes", 0)
        if avg_session > 30:
            highlights.append(
                f"🎮 Average session: {avg_session:.0f} minutes (healthy engagement!)"
            )
        
        # Retention highlights
        if retention.get("retention"):
            day7 = retention["retention"].get("day_7", {}).get("rate", 0)
            if day7 > 40:
                highlights.append(f"📈 Strong 7-day retention: {day7}%")
            elif day7 < 20:
                highlights.append(f"⚠️ Low 7-day retention: {day7}% (needs attention)")
        
        return highlights
    
    def _save_report(self, report: Dict, filename: str) -> Path:
        """Save report to file."""
        filepath = self.reports_path / f"{filename}.json"
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        return filepath
    
    def format_as_markdown(self, report: Dict) -> str:
        """Format report as markdown."""
        report_type = report.get("report_type", "unknown")
        
        md = []
        md.append(f"# 📊 {report_type.title()} Analytics Report")
        md.append(f"*Generated: {report.get('generated_at', 'Unknown')}*\n")
        
        # Summary
        if "summary" in report:
            summary = report["summary"]
            md.append("## Summary")
            md.append(f"- **Unique Players:** {summary.get('unique_players', 0)}")
            md.append(f"- **Total Sessions:** {summary.get('total_sessions', 0)}")
            md.append(f"- **Playtime:** {summary.get('total_playtime_hours', 0)} hours")
            md.append(f"- **Avg Session:** {summary.get('avg_session_minutes', 0)} minutes")
            md.append("")
        
        # Engagement
        if "engagement" in report:
            engagement = report["engagement"]
            md.append("## Engagement Metrics")
            md.append(f"- **Unique Players:** {engagement.get('unique_players', 0)}")
            md.append(f"- **Total Sessions:** {engagement.get('total_sessions', 0)}")
            md.append(f"- **Sessions per Player:** {engagement.get('sessions_per_player', 0)}")
            
            dau = engagement.get("dau", {})
            md.append(f"- **Avg Daily Active:** {dau.get('average', 0)}")
            md.append(f"- **Peak DAU:** {dau.get('max', 0)}")
            md.append("")
        
        # Leaderboard
        if "leaderboard" in report or "top_players" in report:
            leaders = report.get("leaderboard") or report.get("top_players", [])
            if leaders:
                md.append("## 🏆 Top Players")
                for entry in leaders[:10]:
                    md.append(
                        f"{entry.get('rank', '')}. **{entry.get('username', 'Unknown')}** "
                        f"— {entry.get('value', 0)} {entry.get('label', '')}"
                    )
                md.append("")
        
        # Highlights
        if "highlights" in report:
            md.append("## ✨ Highlights")
            for highlight in report["highlights"]:
                md.append(f"- {highlight}")
            md.append("")
        
        return "\n".join(md)
    
    def format_as_discord_embed(self, report: Dict) -> Dict[str, Any]:
        """Format report as Discord embed structure."""
        report_type = report.get("report_type", "unknown")
        
        fields = []
        
        # Add summary fields
        if "summary" in report:
            summary = report["summary"]
            fields.append({
                "name": "👥 Players",
                "value": str(summary.get("unique_players", 0)),
                "inline": True,
            })
            fields.append({
                "name": "🎮 Sessions",
                "value": str(summary.get("total_sessions", 0)),
                "inline": True,
            })
            fields.append({
                "name": "⏱️ Playtime",
                "value": f"{summary.get('total_playtime_hours', 0)}h",
                "inline": True,
            })
        
        if "engagement" in report:
            engagement = report["engagement"]
            dau = engagement.get("dau", {})
            fields.append({
                "name": "📊 Daily Active",
                "value": f"Avg: {dau.get('average', 0):.0f} | Peak: {dau.get('max', 0)}",
                "inline": False,
            })
        
        # Top players
        if "leaderboard" in report or "top_players" in report:
            leaders = report.get("leaderboard") or report.get("top_players", [])
            if leaders:
                leaderboard_text = "\n".join(
                    f"{'🥇🥈🥉'[i] if i < 3 else f'{i+1}.'} {e.get('username', '?')} — {e.get('value', 0)}{e.get('label', 'h')[:1]}"
                    for i, e in enumerate(leaders[:5])
                )
                fields.append({
                    "name": "🏆 Top Players",
                    "value": leaderboard_text,
                    "inline": False,
                })
        
        return {
            "title": f"📊 {report_type.title()} Report",
            "color": 0x00d9ff,
            "fields": fields,
            "footer": {"text": f"Generated {report.get('generated_at', '')[:10]}"},
        }
    
    def list_reports(
        self,
        report_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List available reports."""
        reports = []
        
        for filepath in sorted(self.reports_path.glob("*.json"), reverse=True):
            if report_type and not filepath.stem.startswith(report_type):
                continue
            
            try:
                with open(filepath) as f:
                    data = json.load(f)
                reports.append({
                    "filename": filepath.name,
                    "report_type": data.get("report_type"),
                    "generated_at": data.get("generated_at"),
                })
            except:
                pass
            
            if len(reports) >= limit:
                break
        
        return reports
    
    def get_report(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get a specific report by filename."""
        filepath = self.reports_path / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath) as f:
                return json.load(f)
        except:
            return None
