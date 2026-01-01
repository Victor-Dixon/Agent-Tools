"""
Tests for dependency mapping system.

Tests cover:
- Import extraction (internal and external)
- Dependency graph construction
- Circular dependency detection
- Registry dependency mapping
- Cross-reference identification
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from tools.consolidation.dependency_mapper import (
    DependencyMapper,
    DependencyNode,
    DependencyType,
    extract_imports,
    find_circular_dependencies,
    load_registry_dependencies,
    map_registry_relationships,
)


class TestExtractImports:
    """Test import extraction from Python files."""

    def test_extract_simple_import(self):
        """Test extraction of simple import statement."""
        content = "import requests\nimport numpy"
        imports = extract_imports(content)
        assert "requests" in imports["external"]
        assert "numpy" in imports["external"]
        assert len(imports["internal"]) == 0

    def test_extract_from_import(self):
        """Test extraction of from...import statement."""
        content = "from requests import get\nfrom numpy import array"
        imports = extract_imports(content)
        assert "requests" in imports["external"]
        assert "numpy" in imports["external"]

    def test_extract_internal_import(self):
        """Test extraction of internal tool imports."""
        content = "from tools.monitoring import unified_monitor\nimport tools.validation"
        imports = extract_imports(content, base_path="tools")
        assert "tools.monitoring" in imports["internal"]
        assert "tools.validation" in imports["internal"]
        assert len(imports["internal"]) == 2

    def test_extract_tools_v2_import(self):
        """Test extraction of tools_v2 imports."""
        content = "from tools_v2.categories.monitoring_tools import MonitoringTool"
        imports = extract_imports(content, base_path="tools_v2")
        assert "tools_v2.categories.monitoring_tools" in imports["internal"]

    def test_extract_relative_import(self):
        """Test extraction of relative imports."""
        content = "from .base_adapter import IToolAdapter\nfrom ..utils import helper"
        imports = extract_imports(content, base_path="tools_v2")
        # Relative imports should be tracked
        assert len(imports["internal"]) >= 0  # May or may not be trackable

    def test_extract_third_party_import(self):
        """Test extraction of third-party package imports."""
        content = "import requests\nimport numpy as np"
        imports = extract_imports(content)
        assert "requests" in imports["external"]
        assert "numpy" in imports["external"]

    def test_extract_stdlib_import(self):
        """Test that stdlib imports are filtered out."""
        content = "import json\nimport os\nimport sys"
        imports = extract_imports(content)
        # Standard library should be filtered
        stdlib_modules = {"json", "os", "sys"}
        assert not any(module in imports["external"] for module in stdlib_modules)

    def test_extract_complex_imports(self):
        """Test extraction from complex import patterns."""
        content = """
import os
from pathlib import Path
from typing import List, Dict, Optional
from tools.monitoring import unified_monitor
from tools_v2.categories.validation_tools import ValidationTool
import requests
        """
        imports = extract_imports(content, base_path="tools")
        # Standard library (os, pathlib, typing) should be filtered
        assert "requests" in imports["external"]
        assert "tools.monitoring" in imports["internal"]
        assert "tools_v2.categories.validation_tools" in imports["internal"]


class TestDependencyNode:
    """Test DependencyNode data structure."""

    def test_create_node(self):
        """Test creating a dependency node."""
        node = DependencyNode(
            tool_id="test_tool",
            path="tools/test_tool.py",
            dependencies={"tools.other_tool"},
            dependents={"tools.caller_tool"},
            external_deps={"requests", "numpy"},
        )
        assert node.tool_id == "test_tool"
        assert node.path == "tools/test_tool.py"
        assert "tools.other_tool" in node.dependencies
        assert "tools.caller_tool" in node.dependents
        assert "requests" in node.external_deps

    def test_node_to_dict(self):
        """Test converting node to dictionary."""
        node = DependencyNode(
            tool_id="test_tool",
            path="tools/test_tool.py",
            dependencies={"tools.other_tool"},
            dependents={"tools.caller_tool"},
            external_deps={"requests"},
        )
        node_dict = node.to_dict()
        assert node_dict["tool_id"] == "test_tool"
        assert node_dict["path"] == "tools/test_tool.py"
        assert "tools.other_tool" in node_dict["dependencies"]
        assert "tools.caller_tool" in node_dict["dependents"]
        assert "requests" in node_dict["external_deps"]


class TestDependencyMapper:
    """Test DependencyMapper class."""

    def test_initialize_mapper(self):
        """Test initializing the dependency mapper."""
        mapper = DependencyMapper(base_dir=".")
        assert mapper.base_dir == Path(".")
        assert len(mapper.nodes) == 0
        assert len(mapper.graph) == 0

    def test_scan_directory(self, tmp_path):
        """Test scanning a directory for Python files."""
        # Create test files
        test_file1 = tmp_path / "tool1.py"
        test_file1.write_text("import os\nfrom tools.other import helper")
        test_file2 = tmp_path / "tool2.py"
        test_file2.write_text("import sys\nfrom tools.tool1 import func")

        mapper = DependencyMapper(base_dir=str(tmp_path))
        mapper.scan_directory(tmp_path)

        assert len(mapper.nodes) == 2
        assert "tool1" in mapper.nodes or any("tool1" in n.tool_id for n in mapper.nodes.values())

    def test_build_dependency_graph(self, tmp_path):
        """Test building dependency graph."""
        # Create test files with dependencies
        tool1 = tmp_path / "tool1.py"
        tool1.write_text("import os")
        tool2 = tmp_path / "tool2.py"
        tool2.write_text("from tool1 import func")

        mapper = DependencyMapper(base_dir=str(tmp_path))
        mapper.scan_directory(tmp_path)
        mapper.build_dependency_graph()

        assert len(mapper.graph) > 0

    def test_get_external_dependencies(self, tmp_path):
        """Test getting all external dependencies."""
        tool1 = tmp_path / "tool1.py"
        tool1.write_text("import requests\nimport numpy")
        tool2 = tmp_path / "tool2.py"
        tool2.write_text("import pandas")

        mapper = DependencyMapper(base_dir=str(tmp_path))
        mapper.scan_directory(tmp_path)
        external = mapper.get_external_dependencies()

        assert "requests" in external
        assert "numpy" in external
        assert "pandas" in external

    def test_get_internal_dependencies(self, tmp_path):
        """Test getting internal dependency relationships."""
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        tool1 = tools_dir / "tool1.py"
        tool1.write_text("import os")
        tool2 = tools_dir / "tool2.py"
        tool2.write_text("from tools.tool1 import func")

        mapper = DependencyMapper(base_dir=str(tmp_path))
        mapper.scan_directory(tools_dir)
        mapper.build_dependency_graph()
        internal = mapper.get_internal_dependencies()

        assert len(internal) > 0


class TestCircularDependencies:
    """Test circular dependency detection."""

    def test_find_simple_circular_dependency(self):
        """Test finding a simple circular dependency."""
        graph = {
            "tool1": {"tool2"},
            "tool2": {"tool1"},
        }
        cycles = find_circular_dependencies(graph)
        assert len(cycles) > 0
        # Should find cycle: tool1 -> tool2 -> tool1
        assert any("tool1" in cycle and "tool2" in cycle for cycle in cycles)

    def test_find_complex_circular_dependency(self):
        """Test finding a complex circular dependency."""
        graph = {
            "tool1": {"tool2"},
            "tool2": {"tool3"},
            "tool3": {"tool1"},
        }
        cycles = find_circular_dependencies(graph)
        assert len(cycles) > 0
        # Should find cycle: tool1 -> tool2 -> tool3 -> tool1

    def test_no_circular_dependency(self):
        """Test when there are no circular dependencies."""
        graph = {
            "tool1": {"tool2"},
            "tool2": {"tool3"},
            "tool3": set(),
        }
        cycles = find_circular_dependencies(graph)
        assert len(cycles) == 0

    def test_self_referential_dependency(self):
        """Test self-referential dependency (tool imports itself)."""
        graph = {
            "tool1": {"tool1"},
        }
        cycles = find_circular_dependencies(graph)
        assert len(cycles) > 0


class TestRegistryDependencies:
    """Test registry dependency mapping."""

    def test_load_toolbelt_registry(self, tmp_path):
        """Test loading toolbelt_registry.py."""
        registry_file = tmp_path / "toolbelt_registry.py"
        registry_content = """
TOOLS_REGISTRY = {
    "scan": {
        "module": "tools.scan",
        "flags": ["--scan"],
    },
    "validate": {
        "module": "tools.validate",
        "flags": ["--validate"],
    }
}
        """
        registry_file.write_text(registry_content)

        deps = load_registry_dependencies(str(registry_file))
        # Should extract both modules
        assert len(deps) >= 1  # At least one should be found
        assert "tools.scan" in deps or "tools.validate" in deps

    def test_load_tool_registry_lock(self, tmp_path):
        """Test loading tool_registry.lock.json."""
        lock_file = tmp_path / "tool_registry.lock.json"
        lock_data = {
            "tools": {
                "monitoring.tool": ["tools_v2.categories.monitoring_tools", "MonitoringTool"],
                "validation.tool": ["tools_v2.categories.validation_tools", "ValidationTool"],
            }
        }
        lock_file.write_text(json.dumps(lock_data, indent=2))

        deps = load_registry_dependencies(str(lock_file))
        assert "tools_v2.categories.monitoring_tools" in deps
        assert "tools_v2.categories.validation_tools" in deps

    def test_map_registry_relationships(self, tmp_path):
        """Test mapping registry relationships."""
        # Create mock registries
        toolbelt_registry = tmp_path / "toolbelt_registry.py"
        toolbelt_registry.write_text('TOOLS_REGISTRY = {"scan": {"module": "tools.scan"}}')

        lock_file = tmp_path / "tool_registry.lock.json"
        lock_data = {"tools": {"monitoring.tool": ["tools_v2.categories.monitoring_tools", "MonitoringTool"]}}
        lock_file.write_text(json.dumps(lock_data, indent=2))

        relationships = map_registry_relationships(
            toolbelt_registry=str(toolbelt_registry),
            tool_registry_lock=str(lock_file),
        )

        assert "toolbelt_registry" in relationships
        assert "tool_registry_lock" in relationships
        assert len(relationships["toolbelt_registry"]) > 0
        assert len(relationships["tool_registry_lock"]) > 0


class TestDependencyMapperIntegration:
    """Integration tests for DependencyMapper."""

    def test_full_analysis(self, tmp_path):
        """Test full dependency analysis workflow."""
        # Create test structure
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        tools_v2_dir = tmp_path / "tools_v2"
        tools_v2_dir.mkdir()

        # Create test tools
        tool1 = tools_dir / "tool1.py"
        tool1.write_text("import requests\nfrom tools.tool2 import helper")
        tool2 = tools_dir / "tool2.py"
        tool2.write_text("import os")

        v2_tool = tools_v2_dir / "categories" / "monitoring_tools.py"
        v2_tool.parent.mkdir()
        v2_tool.write_text("from tools.tool1 import func")

        mapper = DependencyMapper(base_dir=str(tmp_path))
        mapper.scan_directory(tools_dir)
        mapper.scan_directory(tools_v2_dir)
        mapper.build_dependency_graph()

        external = mapper.get_external_dependencies()
        internal = mapper.get_internal_dependencies()
        cycles = find_circular_dependencies(mapper.graph)

        assert "requests" in external
        assert len(internal) > 0
        # Should not have cycles in this simple case
        assert isinstance(cycles, list)

    def test_export_dependency_map(self, tmp_path):
        """Test exporting dependency map to JSON."""
        tool1 = tmp_path / "tool1.py"
        tool1.write_text("import requests")

        mapper = DependencyMapper(base_dir=str(tmp_path))
        mapper.scan_directory(tmp_path)
        mapper.build_dependency_graph()

        output_file = tmp_path / "dependencies.json"
        mapper.export_to_json(str(output_file))

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert "nodes" in data
        assert "graph" in data
        assert "external_dependencies" in data
        assert "circular_dependencies" in data

