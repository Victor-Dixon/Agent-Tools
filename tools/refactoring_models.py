#!/usr/bin/env python3
"""Refactoring models."""
from dataclasses import dataclass
from typing import List


@dataclass
class CodeEntity:
    name: str
    entity_type: str
    start_line: int
    end_line: int
    line_count: int


@dataclass
class ModuleSuggestion:
    module_name: str
    purpose: str
    estimated_lines: int
    entities: List[CodeEntity]
    priority: int = 3  # Default priority


@dataclass
class RefactoringSuggestion:
    file_path: str
    violation_type: str
    current_lines: int
    target_lines: int
    confidence: float
    reasoning: str
    suggested_modules: List[ModuleSuggestion]
    import_changes: List[str]
    estimated_main_file_lines: int
    estimated_total_lines: int
