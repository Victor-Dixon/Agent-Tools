#!/usr/bin/env python3
"""
Functionality Signature Generator
=================================

Generates comprehensive functionality signatures for verification.

Author: Agent-1 (Integration & Core Systems Specialist)
V2 Compliant: <300 lines
"""

import ast
import json
from pathlib import Path
from typing import Any, Dict


class SignatureGenerator:
    """Generate functionality signatures from codebase."""

    def __init__(self, project_root: Path):
        """Initialize signature generator."""
        self.project_root = project_root

    def generate_signature(self) -> Dict[str, Any]:
        """Generate comprehensive functionality signature."""
        signature = {
            "functions": [],
            "classes": [],
            "files": [],
            "imports": [],
            "timestamp": None,
        }

        # Scan Python files in tools directory
        tools_dir = self.project_root / "tools"
        if tools_dir.exists():
            for py_file in tools_dir.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        tree = ast.parse(content, filename=str(py_file))

                    rel_path = str(py_file.relative_to(self.project_root))

                    # Extract functions and classes
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            signature["functions"].append({
                                "name": node.name,
                                "file": rel_path,
                                "line": node.lineno,
                            })
                        elif isinstance(node, ast.ClassDef):
                            signature["classes"].append({
                                "name": node.name,
                                "file": rel_path,
                                "line": node.lineno,
                            })

                    # Extract imports
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                signature["imports"].append({
                                    "module": alias.name,
                                    "file": rel_path,
                                })
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                signature["imports"].append({
                                    "module": node.module,
                                    "file": rel_path,
                                })

                    signature["files"].append(rel_path)

                except Exception:
                    # Skip files that can't be parsed
                    continue

        from datetime import datetime
        signature["timestamp"] = datetime.now().isoformat()

        return signature

