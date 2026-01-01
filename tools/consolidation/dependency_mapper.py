"""
Dependency Mapping System for Tools Consolidation.

This module provides comprehensive dependency analysis for tools in the
tools/ and tools_v2/ directories, including:
- Import extraction (internal and external)
- Dependency graph construction
- Circular dependency detection
- Registry dependency mapping
- Cross-reference identification

V2 Compliance: <400 lines
Author: Consolidation Tools
"""

import ast
import json
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Standard library modules to filter out
STDLIB_MODULES = {
    "sys", "os", "json", "pathlib", "typing", "dataclasses", "abc",
    "collections", "itertools", "functools", "logging", "re", "ast",
    "unittest", "pytest", "tempfile", "io", "contextlib", "datetime",
    "time", "asyncio", "argparse", "subprocess", "shutil", "hashlib",
    "base64", "urllib", "http", "email", "html", "xml", "csv", "sqlite3",
    "threading", "multiprocessing", "queue", "socket", "ssl", "zipfile",
    "tarfile", "gzip", "pickle", "copy", "enum", "warnings", "traceback",
}


class DependencyType(Enum):
    """Types of dependencies."""

    INTERNAL = "internal"
    EXTERNAL = "external"
    REGISTRY = "registry"


@dataclass
class DependencyNode:
    """Represents a tool and its dependencies."""

    tool_id: str
    path: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    external_deps: Set[str] = field(default_factory=set)
    registry: str = "none"

    def to_dict(self) -> Dict:
        """Convert node to dictionary."""
        return {
            "tool_id": self.tool_id,
            "path": self.path,
            "dependencies": sorted(list(self.dependencies)),
            "dependents": sorted(list(self.dependents)),
            "external_deps": sorted(list(self.external_deps)),
            "registry": self.registry,
        }


def extract_imports(content: str, base_path: str = "") -> Dict[str, Set[str]]:
    """
    Extract import statements from Python file content.

    Args:
        content: Python file content
        base_path: Base path for determining internal vs external imports

    Returns:
        Dictionary with 'internal' and 'external' import sets
    """
    internal = set()
    external = set()

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    if _is_internal_module(module, base_path):
                        internal.add(module)
                    elif not _is_stdlib(module):
                        external.add(module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module
                    if _is_internal_module(module, base_path):
                        internal.add(module)
                    elif not _is_stdlib(module):
                        external.add(module)
    except SyntaxError:
        # Fallback to regex parsing
        import_pattern = r"^(?:from|import)\s+([a-zA-Z0-9_.]+)"
        for line in content.splitlines():
            match = re.match(import_pattern, line.strip())
            if match:
                module = match.group(1)
                if _is_internal_module(module, base_path):
                    internal.add(module)
                elif not _is_stdlib(module):
                    external.add(module)

    return {"internal": internal, "external": external}


def _is_internal_module(module: str, base_path: str) -> bool:
    """Check if module is internal (tools/ or tools_v2/)."""
    if not base_path:
        return module.startswith(("tools.", "tools_v2."))
    return module.startswith(("tools.", "tools_v2."))


def _is_stdlib(module: str) -> bool:
    """Check if module is part of standard library."""
    first_part = module.split(".")[0]
    return first_part in STDLIB_MODULES


def find_circular_dependencies(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """
    Find circular dependencies in a dependency graph.

    Uses DFS to detect cycles.

    Args:
        graph: Dictionary mapping tool_id to set of dependencies

    Returns:
        List of cycles, where each cycle is a list of tool_ids
    """
    cycles = []
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node: str) -> None:
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return

        if node in visited:
            return

        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            dfs(neighbor)

        rec_stack.remove(node)
        path.pop()

    for node in graph:
        if node not in visited:
            dfs(node)

    return cycles


def load_registry_dependencies(registry_path: str) -> Set[str]:
    """
    Load dependencies from registry files.

    Supports:
    - toolbelt_registry.py (Python dict)
    - tool_registry.lock.json (JSON)

    Args:
        registry_path: Path to registry file

    Returns:
        Set of module paths from registry
    """
    deps = set()
    path = Path(registry_path)

    if not path.exists():
        return deps

    if path.suffix == ".json":
        # Load JSON registry
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if "tools" in data:
                    for tool_info in data["tools"].values():
                        if isinstance(tool_info, list) and len(tool_info) > 0:
                            deps.add(tool_info[0])  # Module path
        except (json.JSONDecodeError, KeyError):
            pass
    elif path.name == "toolbelt_registry.py":
        # Parse Python registry
        try:
            content = path.read_text()
            # Extract module paths - handle both single and multi-line formats
            module_pattern = r'"module"\s*:\s*"([^"]+)"'
            modules = re.findall(module_pattern, content)
            deps.update(modules)
        except Exception:
            pass

    return deps


def map_registry_relationships(
    toolbelt_registry: str = "tools/toolbelt_registry.py",
    tool_registry_lock: str = "tools_v2/tool_registry.lock.json",
) -> Dict[str, Set[str]]:
    """
    Map relationships between registries.

    Args:
        toolbelt_registry: Path to toolbelt_registry.py
        tool_registry_lock: Path to tool_registry.lock.json

    Returns:
        Dictionary mapping registry names to sets of module paths
    """
    relationships = {
        "toolbelt_registry": set(),
        "tool_registry_lock": set(),
    }

    if Path(toolbelt_registry).exists():
        relationships["toolbelt_registry"] = load_registry_dependencies(toolbelt_registry)

    if Path(tool_registry_lock).exists():
        relationships["tool_registry_lock"] = load_registry_dependencies(tool_registry_lock)

    return relationships


class DependencyMapper:
    """Comprehensive dependency mapper for tools."""

    def __init__(self, base_dir: str = "."):
        """
        Initialize dependency mapper.

        Args:
            base_dir: Base directory for the project
        """
        self.base_dir = Path(base_dir)
        self.nodes: Dict[str, DependencyNode] = {}
        self.graph: Dict[str, Set[str]] = {}

    def scan_directory(self, directory: Path) -> None:
        """
        Scan directory for Python files and extract dependencies.

        Args:
            directory: Directory to scan
        """
        if isinstance(directory, str):
            directory = Path(directory)

        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("__") or "test" in py_file.name.lower():
                continue

            tool_id = self._get_tool_id(py_file)
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            imports = extract_imports(content, base_path=str(self.base_dir))

            # Determine if this is tools/ or tools_v2/
            is_tools_v2 = "tools_v2" in str(py_file)

            node = DependencyNode(
                tool_id=tool_id,
                path=str(py_file.relative_to(self.base_dir)),
                external_deps=imports["external"],
            )

            # Track internal dependencies
            for internal_dep in imports["internal"]:
                node.dependencies.add(internal_dep)

            # Determine registry
            if is_tools_v2:
                node.registry = "tool_registry_v2"
            else:
                node.registry = "toolbelt_registry"

            self.nodes[tool_id] = node

    def _get_tool_id(self, file_path: Path) -> str:
        """Generate tool ID from file path."""
        rel_path = file_path.relative_to(self.base_dir)
        # Remove extension and convert to tool_id
        parts = rel_path.parts
        if len(parts) > 1:
            # Include directory structure
            tool_id = ".".join(parts[:-1]) + "." + parts[-1].replace(".py", "")
        else:
            tool_id = parts[0].replace(".py", "")
        return tool_id

    def build_dependency_graph(self) -> None:
        """Build dependency graph from nodes."""
        self.graph = {}

        for tool_id, node in self.nodes.items():
            self.graph[tool_id] = set()

            # Map internal dependencies to tool_ids
            for dep in node.dependencies:
                # Try to find matching tool_id
                matching_tool = self._find_tool_by_module(dep)
                if matching_tool:
                    self.graph[tool_id].add(matching_tool)
                    # Update dependents
                    if matching_tool in self.nodes:
                        self.nodes[matching_tool].dependents.add(tool_id)

    def _find_tool_by_module(self, module: str) -> str:
        """Find tool_id that matches a module path."""
        # Try exact match first
        for tool_id, node in self.nodes.items():
            if module in node.path or node.path.replace("/", ".").replace(".py", "") == module:
                return tool_id

        # Try partial match
        module_parts = module.split(".")
        for tool_id, node in self.nodes.items():
            node_parts = node.path.replace("/", ".").replace(".py", "").split(".")
            if any(part in node_parts for part in module_parts):
                return tool_id

        return ""

    def get_external_dependencies(self) -> Set[str]:
        """Get all external (third-party) dependencies."""
        external = set()
        for node in self.nodes.values():
            external.update(node.external_deps)
        return external

    def get_internal_dependencies(self) -> Dict[str, Set[str]]:
        """Get internal dependency relationships."""
        return {tool_id: deps for tool_id, deps in self.graph.items() if deps}

    def get_circular_dependencies(self) -> List[List[str]]:
        """Get circular dependencies in the graph."""
        return find_circular_dependencies(self.graph)

    def export_to_json(self, output_path: str) -> None:
        """
        Export dependency map to JSON.

        Args:
            output_path: Path to output JSON file
        """
        registry_rels = map_registry_relationships()
        # Convert sets to lists for JSON serialization
        registry_rels_serializable = {
            key: sorted(list(value)) for key, value in registry_rels.items()
        }

        data = {
            "nodes": {tool_id: node.to_dict() for tool_id, node in self.nodes.items()},
            "graph": {tool_id: sorted(list(deps)) for tool_id, deps in self.graph.items()},
            "external_dependencies": sorted(list(self.get_external_dependencies())),
            "circular_dependencies": self.get_circular_dependencies(),
            "registry_relationships": registry_rels_serializable,
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

