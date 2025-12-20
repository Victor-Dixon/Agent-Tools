#!/usr/bin/env python3
"""
Project Scanner - REFACTORED FOR V2 COMPLIANCE
==============================================

⚠️ REFACTORED: This file was 1,153 lines (3x V2 limit!).
Split into 6 V2-compliant modules:
  - projectscanner_language_analyzer.py (317 lines) - Language parsing
  - projectscanner_workers.py (223 lines) - Threading & file processing
  - projectscanner_modular_reports.py (263 lines) - Modular reports
  - projectscanner_legacy_reports.py (190 lines) - Legacy reports
  - projectscanner_core.py (236 lines) - Main orchestrator
  - projectscanner.py (100 lines) - CLI facade

This file now serves as the CLI entry point and facade.

REFACTORED BY: Agent-1 (Integration & Core Systems Specialist)
DATE: 2025-10-11
REASON: V2 Compliance - BIGGEST violation (1,153 lines)
"""

import argparse
import json
import logging
from pathlib import Path

from projectscanner_core import ProjectScanner

logger = logging.getLogger(__name__)


# ---------------------------------
# CLI Usage
# ---------------------------------
def main():
    """CLI entry point for project scanner."""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(
        description="Project scanner with agent categorization and incremental caching."
    )
    parser.add_argument("--project-root", default=".", help="Root directory to scan.")
    parser.add_argument("--ignore", nargs="*", default=[], help="Additional directories to ignore.")
    parser.add_argument(
        "--categorize-agents",
        action="store_true",
        help="Categorize Python classes into maturity level and agent type.",
    )
    parser.add_argument(
        "--no-chatgpt-context", action="store_true", help="Skip exporting ChatGPT context."
    )
    parser.add_argument(
        "--generate-init", action="store_true", help="Enable auto-generating __init__.py files."
    )
    args = parser.parse_args()

    scanner = ProjectScanner(project_root=args.project_root)
    scanner.additional_ignore_dirs = set(args.ignore)

    scanner.scan_project()

    if args.generate_init:
        scanner.generate_init_files(overwrite=True)

    if args.categorize_agents:
        scanner.categorize_agents()
        scanner.report_generator.save_report()
        logging.info("✅ Agent categorization complete. Updated project_analysis.json.")

    if not args.no_chatgpt_context:
        scanner.export_chatgpt_context()
        logging.info("✅ ChatGPT context exported by default.")

        # Output merged ChatGPT context to stdout
        context_path = Path(args.project_root) / "chatgpt_project_context.json"
        if context_path.exists():
            try:
                with context_path.open("r", encoding="utf-8") as f:
                    chatgpt_context = json.load(f)
            except Exception as e:
                logger.error(f"❌ Error reading exported ChatGPT context: {e}")


if __name__ == "__main__":
    main()
