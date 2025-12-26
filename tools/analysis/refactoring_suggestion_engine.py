#!/usr/bin/env python3
"""
Refactoring Suggestion Engine - Intelligent Quality Automation
===============================================================

AST-based analyzer that suggests split points and refactoring strategies
for V2 compliance violations. Provides actionable recommendations with
code snippets and impact estimates.

Features:
- AST analysis to identify logical split points
- Intelligent module extraction suggestions
- Class/function grouping recommendations
- Import statement generation
- Impact estimation and preview

Author: Agent-6 (VSCode Forking & Quality Gates Specialist)
License: MIT
"""

from pathlib import Path

try:
    from .refactoring_ast_analyzer import ASTAnalyzer
    from .refactoring_models import CodeEntity, ModuleSuggestion, RefactoringSuggestion
except ImportError:
    # Fallback for direct execution
    from tools.analysis.refactoring_ast_analyzer import ASTAnalyzer
    from tools.analysis.refactoring_models import CodeEntity, ModuleSuggestion, RefactoringSuggestion


class RefactoringSuggestionEngine:
    """Generates intelligent refactoring suggestions."""

    def __init__(self):
        """Initialize suggestion engine."""
        self.analyzer = ASTAnalyzer()

    def suggest_refactoring(
        self, file_path: str, current_lines: int, target_lines: int = 400
    ) -> RefactoringSuggestion | None:
        """Generate refactoring suggestions for a file."""
        path = Path(file_path)
        if not path.exists():
            return None

        # Analyze file structure
        entities = self.analyzer.analyze_file(path)
        if not entities:
            return None

        # Group entities by category
        grouped = self._group_entities_by_category(entities)

        # Generate module suggestions
        suggested_modules = self._generate_module_suggestions(
            file_path, grouped, current_lines, target_lines
        )

        # Calculate estimates
        estimated_main = self._estimate_main_file_size(
            entities, suggested_modules)
        estimated_total = estimated_main + \
            sum(m.estimated_lines for m in suggested_modules)

        # Generate import changes
        import_changes = self._generate_import_changes(
            file_path, suggested_modules)

        # Calculate confidence
        confidence = self._calculate_confidence(
            current_lines, estimated_main, target_lines)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            current_lines, estimated_main, suggested_modules, target_lines
        )

        return RefactoringSuggestion(
            file_path=file_path,
            violation_type="FILE_SIZE",
            current_lines=current_lines,
            target_lines=target_lines,
            suggested_modules=suggested_modules,
            import_changes=import_changes,
            estimated_main_file_lines=estimated_main,
            estimated_total_lines=estimated_total,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _group_entities_by_category(
        self, entities: list[CodeEntity]
    ) -> dict[str, list[CodeEntity]]:
        """Group entities by their category."""
        grouped: dict[str, list[CodeEntity]] = {}

        for entity in entities:
            if entity.category not in grouped:
                grouped[entity.category] = []
            grouped[entity.category].append(entity)

        return grouped

    def _generate_module_suggestions(
        self,
        file_path: str,
        grouped: dict[str, list[CodeEntity]],
        current_lines: int,
        target_lines: int,
    ) -> list[ModuleSuggestion]:
        """Generate module extraction suggestions."""
        suggestions = []
        base_name = Path(file_path).stem

        # Priority order for extraction
        extraction_priority = [
            ("model", "models", "Data models and entities", 1),
            ("config", "config", "Configuration classes", 1),
            ("enum", "enums", "Enumeration definitions", 2),
            ("repository", "repository", "Repository operations", 1),
            ("operations", "operations", "Operation handlers", 2),
            ("utility", "utils", "Utility functions", 2),
            ("factory", "factories", "Factory functions", 3),
            ("validation", "validators", "Validation logic", 2),
            ("formatting", "formatters", "Formatting functions", 3),
            ("validation_helper", "validation_helpers",
             "Validation helper methods", 2),
            ("formatting_helper", "formatting_helpers",
             "Formatting helper methods", 2),
            ("processing_helper", "processing_helpers",
             "Processing helper methods", 2),
            ("factory_helper", "factory_helpers", "Factory helper methods", 3),
            ("helper", "helpers", "Helper methods", 3),
        ]

        for category, suffix, purpose, priority in extraction_priority:
            if category in grouped and grouped[category]:
                entities = grouped[category]
                total_lines = sum(e.line_count for e in entities)

                # Only suggest extraction if it's meaningful
                if total_lines >= 30:  # Minimum size to justify extraction
                    module_name = f"{base_name}_{suffix}.py"

                    suggestion = ModuleSuggestion(
                        module_name=module_name,
                        purpose=purpose,
                        entities=entities,
                        estimated_lines=total_lines + 20,  # Add overhead for imports/docs
                        priority=priority,
                    )

                    suggestions.append(suggestion)

        # Sort by priority
        suggestions.sort(key=lambda x: x.priority)

        return suggestions

    def _estimate_main_file_size(
        self, all_entities: list[CodeEntity], suggested_modules: list[ModuleSuggestion]
    ) -> int:
        """Estimate main file size after extraction."""
        extracted_entities = set()
        extracted_lines = 0

        for module in suggested_modules:
            for entity in module.entities:
                extracted_entities.add(entity.name)
                extracted_lines += entity.line_count

        # Get total current lines (including non-entity lines like comments, docstrings)
        # Estimate non-entity lines as ~20% of file
        entity_lines = sum(
            e.line_count for e in all_entities if e.entity_type != "import")

        # Calculate total file lines from largest entity end line
        max_line = max((e.end_line for e in all_entities), default=0)
        total_file_lines = max_line

        # Remaining = total - extracted + import overhead
        import_overhead = 20 + (len(suggested_modules) * 2)  # Header + imports
        remaining_lines = total_file_lines - extracted_lines + import_overhead

        return max(remaining_lines, 50)  # Minimum 50 lines for basic structure

    def _generate_import_changes(
        self, file_path: str, modules: list[ModuleSuggestion]
    ) -> list[str]:
        """Generate import statements for suggested modules."""
        imports = []
        base_dir = Path(file_path).parent.name

        for module in modules:
            # Generate relative import
            module_base = module.module_name.replace(".py", "")
            # First 5 entities
            entity_names = [e.name for e in module.entities[:5]]

            if len(entity_names) <= 3:
                import_stmt = f"from .{module_base} import {', '.join(entity_names)}"
            else:
                import_stmt = f"from .{module_base} import ("
                for name in entity_names:
                    import_stmt += f"\n    {name},"
                import_stmt += "\n)"

            imports.append(import_stmt)

        return imports

    def _calculate_confidence(self, current: int, estimated_main: int, target: int) -> float:
        """Calculate confidence score for suggestion."""
        if estimated_main <= target:
            # Will achieve compliance
            margin = target - estimated_main
            confidence = min(1.0, 0.7 + (margin / target) * 0.3)
        else:
            # Won't fully achieve compliance
            improvement = current - estimated_main
            confidence = max(0.3, (improvement / current) * 0.7)

        return round(confidence, 2)

    def _generate_reasoning(
        self,
        current: int,
        estimated_main: int,
        modules: list[ModuleSuggestion],
        target: int,
    ) -> str:
        """Generate human-readable reasoning for suggestions."""
        lines = []

        reduction = current - estimated_main
        reduction_pct = (reduction / current * 100) if current > 0 else 0

        lines.append(
            f"Current file: {current} lines (target: ≤{target} lines)")
        lines.append(
            f"Suggested extraction: {len(modules)} modules ({reduction} lines, {reduction_pct:.0f}% reduction)"
        )
        lines.append(f"Estimated main file: {estimated_main} lines")

        if estimated_main <= target:
            lines.append(
                f"✅ Result: V2 COMPLIANT (within {target - estimated_main} lines of limit)"
            )
        else:
            lines.append(
                f"⚠️ Result: Still {estimated_main - target} lines over (may need additional refactoring)"
            )

        lines.append("\nSuggested modules:")
        for i, module in enumerate(modules, 1):
            entity_count = len(module.entities)
            lines.append(
                f"{i}. {module.module_name} ({module.estimated_lines} lines, {entity_count} entities)"
            )
            lines.append(f"   Purpose: {module.purpose}")
            entity_preview = ", ".join([e.name for e in module.entities[:3]])
            if len(module.entities) > 3:
                entity_preview += f", ... (+{len(module.entities) - 3} more)"
            lines.append(f"   Contains: {entity_preview}")

        return "\n".join(lines)


class RefactoringSuggestionService:
    """Main service for refactoring suggestions."""

    def __init__(self):
        """Initialize refactoring suggestion service."""
        self.engine = RefactoringSuggestionEngine()

    def analyze_and_suggest(self, file_path: str) -> RefactoringSuggestion | None:
        """Analyze file and generate suggestions."""
        path = Path(file_path)

        # Check file size
        if not path.exists():
            return None

        content = path.read_text(encoding="utf-8")
        current_lines = len(content.split("\n"))

        # Only suggest if violation exists
        if current_lines <= 400:
            return None

        # Generate suggestions
        return self.engine.suggest_refactoring(file_path, current_lines)

    def analyze_directory(
        self, directory: str, pattern: str = "**/*.py"
    ) -> list[RefactoringSuggestion]:
        """Analyze directory and generate suggestions for all violations."""
        suggestions = []
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if self._should_skip_file(file_path):
                continue

            suggestion = self.analyze_and_suggest(str(file_path))
            if suggestion:
                suggestions.append(suggestion)

        # Sort by current line count (worst first)
        suggestions.sort(key=lambda x: x.current_lines, reverse=True)

        return suggestions

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".venv",
            "venv",
            "env",
            ".git",
            "migrations",
            ".pytest_cache",
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)


# CLI entry point moved to refactoring_cli.py for V2 compliance
def main():
    """Main entry point for toolbelt registry compatibility."""
    from .refactoring_cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
