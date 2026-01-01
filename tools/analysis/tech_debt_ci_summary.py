#!/usr/bin/env python3
"""
Technical Debt CI Summary Generator
===================================

Runs the consolidated TechnicalDebtAnalyzer plus targeted V2 size checks using
the v2_compliance_server, then writes a compact markdown dashboard and a
devlog-style summary for CI consumers.

This is designed for use in GitHub Actions but can also be run locally.
"""

from __future__ import annotations
from .technical_debt_analyzer import TechnicalDebtAnalyzer
from mcp_servers import v2_compliance_server as vc

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Ensure project root is importable so `mcp_servers` and related modules resolve
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_technical_debt_analysis() -> Dict[str, Any]:
    """Run TechnicalDebtAnalyzer over the repo and persist canonical outputs."""
    analyzer = TechnicalDebtAnalyzer(project_root=str(PROJECT_ROOT))
    results = analyzer.analyze_codebase()

    analysis_json = PROJECT_ROOT / "docs" / \
        "technical_debt" / "TECHNICAL_DEBT_ANALYSIS.json"
    analysis_report = (
        PROJECT_ROOT / "docs" / "technical_debt" / "TECHNICAL_DEBT_ANALYSIS_REPORT.md"
    )
    analyzer.save_results(results, analysis_json)
    analyzer.generate_report(results, analysis_report)
    return results


def summarize_markers(results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract high-level TODO/FIXME/BUG stats from analyzer results."""
    markers = results.get("markers", {})
    by_type = markers.get("by_type", {})
    by_priority = markers.get("by_priority", {})
    summary = results.get("summary", {})

    return {
        "files_analyzed": summary.get("files_analyzed", 0),
        "total_markers": summary.get("total_markers", 0),
        "todo": by_type.get("TODO", 0),
        "fixme": by_type.get("FIXME", 0),
        "bug": by_type.get("BUG", 0),
        "by_priority": by_priority,
    }


def summarize_duplicates(results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract duplicate-file stats from analyzer results."""
    summary = results.get("summary", {})
    duplicates = results.get("duplicates", {})
    same_name = duplicates.get("same_name", {})

    return {
        "exact_duplicate_groups": summary.get("exact_duplicate_groups", 0),
        "same_name_groups": len(same_name),
        "consolidation_opportunities": summary.get("consolidation_opportunities", 0),
    }


def summarize_v2_size() -> Dict[str, Any]:
    """Run v2_compliance_server size checks across src/ for CI metrics."""
    src_dir = PROJECT_ROOT / "src"
    py_files = list(src_dir.rglob("*.py")) if src_dir.exists() else []

    files_scanned = len(py_files)
    violating_files = 0
    total_violations = 0

    for path in py_files:
        result = vc.check_v2_compliance(str(path))
        if not result.get("success"):
            # Best-effort only; skip errors so CI remains resilient.
            continue

        if result.get("is_exception"):
            continue

        if not result.get("is_compliant"):
            violating_files += 1
            total_violations += int(result.get("violations_count", 0))

    return {
        "files_scanned": files_scanned,
        "violating_files": violating_files,
        "total_violations": total_violations,
    }


def render_dashboard_markdown(
    markers: Dict[str, Any],
    duplicates: Dict[str, Any],
    v2_size: Dict[str, Any],
) -> str:
    """Render a compact technical-debt dashboard markdown string."""
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    lines = [
        "# 🧹 Technical Debt CI Dashboard",
        "",
        f"**Last Run (UTC):** {ts}  ",
        "**Source:** `tools/tech_debt_ci_summary.py` (Tech Debt CI job)",
        "",
        "---",
        "",
        "## 📊 High-Level Summary",
        "",
        f"- **Files analyzed (technical debt):** {markers['files_analyzed']}",
        f"- **Total markers (all types):** {markers['total_markers']}",
        f"- **TODO markers:** {markers['todo']}  ",
        f"- **FIXME markers:** {markers['fixme']}  ",
        f"- **BUG markers:** {markers['bug']}  ",
        "",
        f"- **Exact duplicate groups:** {duplicates['exact_duplicate_groups']}",
        f"- **Same-name duplicate groups:** {duplicates['same_name_groups']}",
        f"- **Consolidation opportunities:** {duplicates['consolidation_opportunities']}",
        "",
        f"- **V2 size – files scanned:** {v2_size['files_scanned']}",
        f"- **V2 size – violating files (non-exception):** {v2_size['violating_files']}",
        f"- **V2 size – total violations:** {v2_size['total_violations']}",
        "",
        "---",
        "",
        "## 🧷 Markers by Priority",
        "",
    ]

    for priority, count in sorted(
        markers["by_priority"].items(), key=lambda kv: kv[0]
    ):
        lines.append(f"- **{priority}**: {count}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "🐝 **WE. ARE. SWARM.** – Tech Debt CI snapshot only (no auto-fix).")
    lines.append("")

    return "\n".join(lines)


def render_devlog_markdown(
    markers: Dict[str, Any],
    duplicates: Dict[str, Any],
    v2_size: Dict[str, Any],
) -> str:
    """Render a short devlog-style summary for the Tech Debt CI run."""
    today = datetime.utcnow().date().isoformat()

    lines = [
        f"# Agent-A2A: Technical Debt CI Summary - {today}",
        "",
        "**Agent:** Agent-A2A - CI & Infrastructure Specialist",
        f"**Date:** {today}",
        "**Mission:** Tech-debt CI sweep (duplicates, V2 size, TODO/FIXME)",
        "",
        "---",
        "",
        "## 🎯 Mission Summary",
        "",
        "- Ran consolidated technical-debt analyzer across the repo.",
        "- Captured duplicate-file and consolidation metrics.",
        "- Ran V2 size checks via `v2_compliance_server` over `src/`.",
        "",
        "---",
        "",
        "## 📊 Detailed Results",
        "",
        "### Technical Debt Markers",
        f"- **Files analyzed:** {markers['files_analyzed']}",
        f"- **Total markers:** {markers['total_markers']}",
        f"- **TODO markers:** {markers['todo']}",
        f"- **FIXME markers:** {markers['fixme']}",
        f"- **BUG markers:** {markers['bug']}",
        "",
        "### Duplicate Files",
        f"- **Exact duplicate groups:** {duplicates['exact_duplicate_groups']}",
        f"- **Same-name groups:** {duplicates['same_name_groups']}",
        f"- **Consolidation opportunities:** {duplicates['consolidation_opportunities']}",
        "",
        "### V2 Size (via v2_compliance_server)",
        f"- **Files scanned:** {v2_size['files_scanned']}",
        f"- **Violating files (non-exception):** {v2_size['violating_files']}",
        f"- **Total violations:** {v2_size['total_violations']}",
        "",
        "---",
        "",
        "## 💡 Key Learnings",
        "",
        "- Technical-debt scanners are now wired into CI, giving fast feedback on markers,",
        "  duplicates, and V2 size drift.",
        "- Future cycles can pull concrete refactor targets directly from the analysis ",
        "  outputs instead of ad-hoc scans.",
        "",
        "---",
        "",
        "## 🏆 Achievements",
        "",
        "- ✅ Automated technical-debt analysis for every qualifying CI run.",
        "- ✅ Integrated v2_compliance_server into CI for size tracking.",
        "- ✅ Generated dashboard + devlog artifacts for downstream review.",
        "",
        "---",
        "",
        "## 🐝 WE ARE SWARM",
        "",
        "Continuous, automated visibility into technical debt keeps the codebase honest",
        "and lets refactor work stay focused on the highest-impact targets.",
        "",
        "---",
        "",
        "**Agent-A2A | CI & Infrastructure Specialist**",
        "",
        "🐝 **WE ARE SWARM** ⚡",
        "",
    ]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate technical-debt CI dashboard + devlog summary."
    )
    parser.add_argument(
        "--dashboard",
        type=Path,
        default=PROJECT_ROOT
        / "docs"
        / "technical_debt"
        / "TECHNICAL_DEBT_DASHBOARD.md",
        help="Path to write the markdown dashboard summary.",
    )
    parser.add_argument(
        "--devlog-dir",
        type=Path,
        default=PROJECT_ROOT / "devlogs",
        help="Directory where the devlog summary file should be written.",
    )
    args = parser.parse_args()

    results = run_technical_debt_analysis()
    markers = summarize_markers(results)
    duplicates = summarize_duplicates(results)
    v2_size = summarize_v2_size()

    # Write dashboard markdown
    dashboard_md = render_dashboard_markdown(markers, duplicates, v2_size)
    dashboard_path: Path = args.dashboard
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(dashboard_md, encoding="utf-8")
    print(f"✅ Wrote technical-debt dashboard to {dashboard_path}")

    # Write devlog markdown (for devlogs/ + Discord tooling)
    devlog_dir: Path = args.devlog_dir
    devlog_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.utcnow().date().isoformat()
    devlog_name = f"{today}_agent-a2a_technical_debt_ci_summary.md"
    devlog_path = devlog_dir / devlog_name
    devlog_md = render_devlog_markdown(markers, duplicates, v2_size)
    devlog_path.write_text(devlog_md, encoding="utf-8")
    print(f"✅ Wrote technical-debt CI devlog to {devlog_path}")


if __name__ == "__main__":
    main()

