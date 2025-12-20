"""
Tool Registry Tests
===================

Tests for tool registry and resolution.

V2 Compliance: <150 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest

from tools_v2 import ToolRegistry, get_tool_registry
from tools_v2.adapters import IToolAdapter
from tools_v2.adapters.error_types import ToolNotFoundError


class TestToolRegistry:
    """Tests for ToolRegistry class."""

    def test_registry_initialization(self):
        """Test registry initializes successfully."""
        registry = ToolRegistry()
        assert registry is not None
        assert registry._cache == {}

    def test_singleton_pattern(self):
        """Test registry singleton returns same instance."""
        registry1 = get_tool_registry()
        registry2 = get_tool_registry()

        assert registry1 is registry2

    def test_list_tools(self):
        """Test listing all tools."""
        registry = ToolRegistry()
        tools = registry.list_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert tools == sorted(tools)  # Should be sorted

    def test_list_by_category(self):
        """Test listing tools by category."""
        registry = ToolRegistry()
        categories = registry.list_by_category()

        assert isinstance(categories, dict)
        assert "vector" in categories
        assert "msg" in categories  # msg.send -> "msg" category

    def test_resolve_valid_tool(self):
        """Test resolving a valid tool."""
        registry = ToolRegistry()
        adapter_class = registry.resolve("vector.context")

        assert adapter_class is not None
        assert issubclass(adapter_class, IToolAdapter)

    def test_resolve_invalid_tool(self):
        """Test error when resolving invalid tool."""
        registry = ToolRegistry()

        with pytest.raises(ToolNotFoundError):
            registry.resolve("invalid.tool")

    def test_caching(self):
        """Test tool resolution is cached."""
        registry = ToolRegistry()

        # First resolution
        adapter1 = registry.resolve("vector.context")

        # Second resolution (should be from cache)
        adapter2 = registry.resolve("vector.context")

        assert adapter1 is adapter2
        assert "vector.context" in registry._cache

    def test_export_lock(self, tmp_path):
        """Test exporting registry lock file."""
        registry = ToolRegistry()
        lock_file = tmp_path / "test_registry.lock.json"

        registry.export_lock(str(lock_file))

        assert lock_file.exists()

        import json

        lock_data = json.loads(lock_file.read_text())
        assert "version" in lock_data
        assert "tools" in lock_data
        assert "count" in lock_data
