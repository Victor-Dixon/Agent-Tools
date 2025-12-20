#!/usr/bin/env python3
"""
Refactoring CLI - Command Line Interface
=========================================

CLI interface for refactoring suggestion engine.
Extracted from refactoring_suggestion_engine.py for V2 compliance.

Author: Agent-6 (VSCode Forking & Quality Gates Specialist)
License: MIT
"""

import argparse
from pathlib import Path

try:
    from .refactoring_models import RefactoringSuggestion
    from .refactoring_suggestion_engine import (
        RefactoringSuggestionEngine,
        RefactoringSuggestionService,
    )
except ImportError:
    from refactoring_models import RefactoringSuggestion
    from refactoring_suggestion_engine import (
        RefactoringSuggestionEngine,
        RefactoringSuggestionService,
    )


def format_suggestion(
    engine: RefactoringSuggestionEngine, suggestion: RefactoringSuggestion, detailed: bool = True
) -> str:
    """Format refactoring suggestion as readable text."""
    lines = []
    lines.append("=" * 80)
    lines.append(f"REFACTORING SUGGESTION: {Path(suggestion.file_path).name}")
    lines.append("=" * 80)
    lines.append(f"Violation: {suggestion.violation_type}")
    lines.append(
        f"Current: {suggestion.current_lines} lines → Target: ≤{suggestion.target_lines} lines"
    )
    lines.append(f"Confidence: {suggestion.confidence * 100:.0f}%")
    lines.append("")
    lines.append("REASONING:")
    lines.append(suggestion.reasoning)
    lines.append("")

    if detailed and suggestion.suggested_modules:
        lines.append("SUGGESTED IMPLEMENTATION:")
        lines.append("")

        for i, module in enumerate(suggestion.suggested_modules, 1):
            lines.append(f"{i}. CREATE: {module.module_name}")
            lines.append(f"   Purpose: {module.purpose}")
            lines.append(f"   Estimated size: {module.estimated_lines} lines")
            lines.append(f"   Entities to extract ({len(module.entities)}):")

            for entity in module.entities:
                lines.append(
                    f"      - {entity.entity_type.title()} '{entity.name}' "
                    f"({entity.line_count} lines, lines {entity.start_line}-{entity.end_line})"
                )

            lines.append("")

        lines.append("IMPORT CHANGES:")
        lines.append("Add to main file:")
        for import_stmt in suggestion.import_changes:
            lines.append(f"  {import_stmt}")
        lines.append("")

        lines.append("ESTIMATED RESULT:")
        lines.append(f"  - Main file: {suggestion.estimated_main_file_lines} lines")
        lines.append(f"  - Total (all modules): {suggestion.estimated_total_lines} lines")
        lines.append(
            f"  - V2 Compliant: "
            f"{'✅ YES' if suggestion.estimated_main_file_lines <= suggestion.target_lines else '⚠️  NO (needs more refactoring)'}"
        )

    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Refactoring Suggestion Engine - Intelligent Quality Automation"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="File or directory to analyze (default: current directory)",
    )
    parser.add_argument("--pattern", default="**/*.py", help="File pattern for directory scan")
    parser.add_argument("--detailed", "-d", action="store_true", help="Show detailed suggestions")
    parser.add_argument(
        "--limit", "-l", type=int, default=10, help="Limit number of suggestions shown"
    )

    args = parser.parse_args()

    service = RefactoringSuggestionService()
    engine = service.engine
    path = Path(args.path)

    if path.is_file():
        # Analyze single file
        suggestion = service.analyze_and_suggest(str(path))
        if suggestion:
            print(format_suggestion(engine, suggestion, args.detailed))
        else:
            print(f"✅ {path.name} is V2 compliant or couldn't be analyzed")

    elif path.is_dir():
        # Analyze directory
        suggestions = service.analyze_directory(str(path), args.pattern)

        if not suggestions:
            print(f"✅ All files in {path} are V2 compliant!")
        else:
            print(f"\nFound {len(suggestions)} files requiring refactoring:")
            print("")

            for i, suggestion in enumerate(suggestions[: args.limit], 1):
                print(f"\n{'=' * 80}")
                print(f"#{i}: {Path(suggestion.file_path).name}")
                print(f"{'=' * 80}")
                print(format_suggestion(engine, suggestion, args.detailed))

            if len(suggestions) > args.limit:
                print(f"\n... and {len(suggestions) - args.limit} more files")

    else:
        print(f"❌ Path not found: {path}")


if __name__ == "__main__":
    main()
