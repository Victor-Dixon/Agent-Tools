"""
Toolbelt Core Tests
===================

Tests for ToolbeltCore orchestrator.

V2 Compliance: <200 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools_v2 import ToolbeltCore


class TestToolbeltCore:
    """Tests for ToolbeltCore class."""

    def test_core_initialization(self):
        """Test core initializes successfully."""
        core = ToolbeltCore()
        assert core is not None
        assert core.registry is not None
        assert core.execution_history == []

    def test_list_tools(self):
        """Test listing all available tools."""
        core = ToolbeltCore()
        tools = core.list_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "vector.context" in tools
        assert "msg.send" in tools

    def test_list_categories(self):
        """Test listing tools by category."""
        core = ToolbeltCore()
        categories = core.list_categories()

        assert isinstance(categories, dict)
        assert "vector" in categories
        assert "messaging" in categories
        assert "analysis" in categories

    def test_tool_not_found(self):
        """Test error when tool not found."""
        core = ToolbeltCore()

        result = core.run("nonexistent.tool", {})
        assert result.success is False
        assert result.exit_code == 1

    def test_execution_history_recording(self):
        """Test execution history is recorded."""
        core = ToolbeltCore()
        initial_count = len(core.execution_history)

        # Run a tool (will fail due to missing params, but should record)
        core.run("vector.context", {})

        assert len(core.execution_history) == initial_count + 1

    def test_clear_history(self):
        """Test clearing execution history."""
        core = ToolbeltCore()
        core.run("vector.context", {})
        core.clear_history()

        assert len(core.execution_history) == 0

    def test_get_execution_history(self):
        """Test retrieving execution history."""
        core = ToolbeltCore()
        core.clear_history()

        core.run("vector.context", {})
        history = core.get_execution_history(limit=10)

        assert isinstance(history, list)
        assert len(history) >= 1
