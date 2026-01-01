#!/usr/bin/env python3
"""
Tool Inventory System
====================

Comprehensive tool discovery, metadata extraction, and inventory generation.

V2 Compliant: Yes (<400 lines)
Author: AI Assistant
Date: 2025-12-29
"""
import ast
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ToolMetadata:
    """Metadata for a single tool."""

    name: str
    path: str
    type: str = "unknown"  # unified, category, domain, specialized
    category: str = "general"  # monitoring, validation, analysis, etc.
    lines_of_code: int = 0
    v2_compliant: bool = False  # ≤400 lines
    dependencies: List[str] = field(default_factory=list)
    cli_flags: List[str] = field(default_factory=list)
    registry: str = "none"  # toolbelt_registry, tool_registry_v2, both
    status: str = "unknown"  # active, deprecated, duplicate, migrate, delete
    migration_target: Optional[str] = None
    migration_priority: Optional[str] = None  # P0, P1, P2
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert metadata to dictionary."""
        return asdict(self)


class ToolInventory:
    """Comprehensive tool inventory system."""

    def __init__(self):
        """Initialize empty inventory."""
        self.tools: Dict[str, ToolMetadata] = {}
        self.categories: Dict[str, Dict] = {}
        self.duplicates: Dict[str, Dict] = {}

    def add_tool(self, tool_id: str, metadata: ToolMetadata):
        """Add a tool to the inventory."""
        self.tools[tool_id] = metadata

        # Update category index
        category = metadata.category
        if category not in self.categories:
            self.categories[category] = {
                "tools": [],
                "target_file": f"tools/categories/{category}_tools.py",
                "existing": False,
            }
        if tool_id not in self.categories[category]["tools"]:
            self.categories[category]["tools"].append(tool_id)

    def to_dict(self) -> Dict:
        """Convert inventory to dictionary."""
        return {
            "tools": {tool_id: tool.to_dict() for tool_id, tool in self.tools.items()},
            "categories": self.categories,
            "duplicates": self.duplicates,
        }

    def save_to_json(self, output_path: str):
        """Save inventory to JSON file."""
        with open(output_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, json_path: str) -> "ToolInventory":
        """Load inventory from JSON file."""
        with open(json_path, "r") as f:
            data = json.load(f)

        inventory = cls()
        for tool_id, tool_data in data.get("tools", {}).items():
            metadata = ToolMetadata(**tool_data)
            inventory.add_tool(tool_id, metadata)

        inventory.categories = data.get("categories", {})
        inventory.duplicates = data.get("duplicates", {})

        return inventory


def discover_tools(directory: str, recursive: bool = True) -> List[Path]:
    """
    Discover all Python tool files in a directory.

    Args:
        directory: Directory to search
        recursive: Whether to search recursively

    Returns:
        List of Path objects to Python files
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []

    tools = []
    pattern = "**/*.py" if recursive else "*.py"

    for py_file in dir_path.glob(pattern):
        # Exclude __pycache__, __init__.py, and test files
        if (
            "__pycache__" in str(py_file)
            or py_file.name == "__init__.py"
            or "test_" in py_file.name
        ):
            continue
        tools.append(py_file)

    return sorted(tools)


def extract_metadata(tool_path: str, base_dir: str) -> ToolMetadata:
    """
    Extract metadata from a tool file.

    Args:
        tool_path: Path to the tool file
        base_dir: Base directory for relative path calculation

    Returns:
        ToolMetadata object
    """
    file_path = Path(tool_path)
    if not file_path.exists():
        return ToolMetadata(name="unknown", path=tool_path)

    # Read file content
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        line_count = len(lines)
    except Exception:
        lines = []
        line_count = 0

    # Determine tool name
    name = file_path.stem

    # Determine tool type
    tool_type = "unknown"
    path_str = str(file_path)
    parent_str = str(file_path.parent)
    if "unified_" in name:
        tool_type = "unified"
    elif "tools_v2/categories" in path_str or "categories" in parent_str or "/categories/" in path_str:
        tool_type = "category"
    elif "domain" in parent_str:
        tool_type = "domain"
    else:
        tool_type = "specialized"

    # Determine category from path or name
    category = "general"
    path_str = str(file_path)
    if "monitoring" in path_str or "monitor" in name.lower():
        category = "monitoring"
    elif "validation" in path_str or "validator" in name.lower():
        category = "validation"
    elif "analysis" in path_str or "analyzer" in name.lower():
        category = "analysis"
    elif "security" in path_str or "security" in name.lower():
        category = "security"
    elif "debug" in path_str or "debugger" in name.lower():
        category = "debug"
    elif "agent" in path_str or "agent" in name.lower():
        category = "agent_ops"
    elif "captain" in path_str or "captain" in name.lower():
        category = "captain"
    elif "github" in path_str or "github" in name.lower():
        category = "github"
    elif "discord" in path_str or "discord" in name.lower():
        category = "discord"
    elif "wordpress" in path_str or "wordpress" in name.lower():
        category = "web"
    elif "devops" in path_str or "environment" in name.lower():
        category = "infrastructure"
    elif "testing" in path_str or "test" in name.lower():
        category = "testing"

    # Check V2 compliance (≤400 lines)
    v2_compliant = line_count <= 400

    # Extract dependencies
    dependencies = _extract_dependencies(content)

    # Extract CLI flags (look for argparse, click, etc.)
    cli_flags = _extract_cli_flags(content)

    # Determine registry
    registry = "none"
    if "toolbelt_registry" in content:
        registry = "toolbelt_registry"
    if "tool_registry" in content or "IToolAdapter" in content:
        if registry == "toolbelt_registry":
            registry = "both"
        else:
            registry = "tool_registry_v2"

    # Determine status
    status = "active"
    if "deprecated" in path_str.lower() or "deprecated" in content.lower():
        status = "deprecated"
    if "TODO" in content or "FIXME" in content:
        status = "needs_attention"

    # Calculate relative path
    try:
        base_path = Path(base_dir)
        if base_path.exists() and file_path.is_relative_to(base_path):
            rel_path = str(file_path.relative_to(base_path))
        elif base_path.exists() and file_path.is_relative_to(base_path.parent):
            rel_path = str(file_path.relative_to(base_path.parent))
        else:
            rel_path = str(file_path)
    except (ValueError, AttributeError):
        # Fallback to absolute path if relative calculation fails
        rel_path = str(file_path)

    return ToolMetadata(
        name=name,
        path=rel_path,
        type=tool_type,
        category=category,
        lines_of_code=line_count,
        v2_compliant=v2_compliant,
        dependencies=dependencies,
        cli_flags=cli_flags,
        registry=registry,
        status=status,
    )


def _extract_dependencies(content: str) -> List[str]:
    """Extract import dependencies from file content."""
    dependencies = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Keep full module path for better tracking
                    dep = alias.name
                    # Also add first part for compatibility
                    first_part = dep.split(".")[0]
                    if first_part not in dependencies:
                        dependencies.append(first_part)
                    if dep != first_part and dep not in dependencies:
                        dependencies.append(dep)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Keep full module path
                    dep = node.module
                    first_part = dep.split(".")[0]
                    if first_part not in dependencies:
                        dependencies.append(first_part)
                    if dep != first_part and dep not in dependencies:
                        dependencies.append(dep)
    except SyntaxError:
        # If parsing fails, use regex fallback
        import_pattern = r"^(?:from|import)\s+([a-zA-Z0-9_.]+)"
        for line in content.splitlines():
            match = re.match(import_pattern, line.strip())
            if match:
                dep = match.group(1)
                dependencies.append(dep)
                # Also add first part
                first_part = dep.split(".")[0]
                if first_part != dep and first_part not in dependencies:
                    dependencies.append(first_part)

    # Remove duplicates and standard library modules
    stdlib = {
        "sys", "os", "json", "pathlib", "typing", "dataclasses", "abc",
        "collections", "itertools", "functools", "logging", "re", "ast",
        "unittest", "pytest", "tempfile", "io", "contextlib",
    }
    filtered = [d for d in dependencies if d.split(".")[0] not in stdlib]
    return sorted(set(filtered))


def _extract_cli_flags(content: str) -> List[str]:
    """Extract CLI flags from argparse/click definitions."""
    flags = []
    # Look for argparse add_argument patterns
    arg_pattern = r'add_argument\(["\']([^"\']+)["\']'
    for match in re.finditer(arg_pattern, content):
        flag = match.group(1)
        if flag.startswith("-"):
            flags.append(flag)

    # Look for click.option patterns
    option_pattern = r'option\(["\']([^"\']+)["\']'
    for match in re.finditer(option_pattern, content):
        flag = match.group(1)
        if flag.startswith("-"):
            flags.append(flag)

    return sorted(set(flags))


def generate_inventory(
    tools_dir: str = "tools",
    tools_v2_dir: str = "tools_v2",
    output_path: Optional[str] = None,
) -> ToolInventory:
    """
    Generate comprehensive tool inventory from directories.

    Args:
        tools_dir: Path to tools/ directory
        tools_v2_dir: Path to tools_v2/ directory
        output_path: Optional path to save JSON inventory

    Returns:
        ToolInventory object
    """
    inventory = ToolInventory()

    # Discover tools in both directories
    tools_files = discover_tools(tools_dir, recursive=True)
    tools_v2_files = discover_tools(tools_v2_dir, recursive=True) if Path(tools_v2_dir).exists() else []

    # Extract metadata from tools/
    for tool_file in tools_files:
        try:
            metadata = extract_metadata(str(tool_file), tools_dir)
            # Use just the name as tool_id for simpler lookup
            tool_id = metadata.name
            # Check for duplicates before adding
            if tool_id in inventory.tools:
                # Mark as duplicate
                dup_key = f"duplicate_{tool_id}"
                if dup_key not in inventory.duplicates:
                    inventory.duplicates[dup_key] = {
                        "tools": [tool_id],
                        "keep": tool_id,
                        "delete": [],
                        "reason": "Duplicate name found",
                    }
            inventory.add_tool(tool_id, metadata)
        except Exception as e:
            # Log error but continue
            print(f"Warning: Failed to extract metadata from {tool_file}: {e}")

    # Extract metadata from tools_v2/
    for tool_file in tools_v2_files:
        try:
            metadata = extract_metadata(str(tool_file), tools_v2_dir)
            # Use just the name as tool_id
            tool_id = metadata.name
            # Check for duplicates
            if tool_id in inventory.tools:
                # Mark as duplicate
                dup_key = f"duplicate_{tool_id}"
                if dup_key not in inventory.duplicates:
                    inventory.duplicates[dup_key] = {
                        "tools": [tool_id],
                        "keep": tool_id,
                        "delete": [],
                        "reason": "Duplicate name found between tools/ and tools_v2/",
                    }
            inventory.add_tool(tool_id, metadata)
        except Exception as e:
            print(f"Warning: Failed to extract metadata from {tool_file}: {e}")

    # Save to JSON if output path provided
    if output_path:
        inventory.save_to_json(output_path)

    return inventory


if __name__ == "__main__":
    # CLI interface
    import argparse

    parser = argparse.ArgumentParser(description="Generate tool inventory")
    parser.add_argument("--tools-dir", default="tools", help="Path to tools/ directory")
    parser.add_argument("--tools-v2-dir", default="tools_v2", help="Path to tools_v2/ directory")
    parser.add_argument("--output", default="tools_inventory.json", help="Output JSON file path")
    args = parser.parse_args()

    print("🔍 Discovering tools...")
    inventory = generate_inventory(
        tools_dir=args.tools_dir,
        tools_v2_dir=args.tools_v2_dir,
        output_path=args.output,
    )

    print(f"✅ Inventory generated: {len(inventory.tools)} tools found")
    print(f"📁 Categories: {len(inventory.categories)}")
    print(f"🔄 Duplicates: {len(inventory.duplicates)}")
    print(f"💾 Saved to: {args.output}")

