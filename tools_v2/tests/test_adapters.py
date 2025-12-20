"""
Adapter Interface Tests
=======================

Tests for adapter base classes and interfaces.

V2 Compliance: <180 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools_v2.adapters import ToolResult, ToolSpec
from tools_v2.categories.messaging_tools import SendMessageTool
from tools_v2.categories.vector_tools import TaskContextTool


class TestToolSpec:
    """Tests for ToolSpec dataclass."""

    def test_spec_creation(self):
        """Test creating tool specification."""
        spec = ToolSpec(
            name="test.tool",
            version="1.0.0",
            category="test",
            summary="Test tool",
            required_params=["param1"],
            optional_params={"param2": "default"},
        )

        assert spec.name == "test.tool"
        assert spec.version == "1.0.0"
        assert "param1" in spec.required_params

    def test_validate_params_success(self):
        """Test parameter validation success."""
        spec = ToolSpec(
            name="test.tool",
            version="1.0.0",
            category="test",
            summary="Test",
            required_params=["param1"],
            optional_params={},
        )

        is_valid, missing = spec.validate_params({"param1": "value"})
        assert is_valid is True
        assert len(missing) == 0

    def test_validate_params_failure(self):
        """Test parameter validation failure."""
        spec = ToolSpec(
            name="test.tool",
            version="1.0.0",
            category="test",
            summary="Test",
            required_params=["param1", "param2"],
            optional_params={},
        )

        is_valid, missing = spec.validate_params({"param1": "value"})
        assert is_valid is False
        assert "param2" in missing


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_result_creation(self):
        """Test creating tool result."""
        result = ToolResult(success=True, output="test output", exit_code=0)

        assert result.success is True
        assert result.output == "test output"
        assert result.exit_code == 0

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = ToolResult(success=False, output=None, exit_code=1, error_message="Test error")

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["success"] is False
        assert result_dict["exit_code"] == 1


class TestIToolAdapter:
    """Tests for IToolAdapter interface implementation."""

    def test_adapter_implements_interface(self):
        """Test adapters implement required interface methods."""
        adapter = TaskContextTool()

        # Should have all required methods
        assert hasattr(adapter, "get_spec")
        assert hasattr(adapter, "validate")
        assert hasattr(adapter, "execute")
        assert hasattr(adapter, "get_help")

    def test_adapter_get_spec(self):
        """Test adapter returns valid spec."""
        adapter = TaskContextTool()
        spec = adapter.get_spec()

        assert isinstance(spec, ToolSpec)
        assert spec.name == "vector.context"
        assert len(spec.required_params) > 0

    def test_adapter_validate(self):
        """Test adapter validates parameters."""
        adapter = SendMessageTool()

        # Valid params
        is_valid, _ = adapter.validate({"agent_id": "Agent-1", "message": "test"})
        assert is_valid is True

        # Invalid params (missing required)
        is_valid, missing = adapter.validate({"message": "test"})
        assert is_valid is False
        assert "agent_id" in missing

    def test_adapter_get_help(self):
        """Test adapter returns help text."""
        adapter = TaskContextTool()
        help_text = adapter.get_help()

        assert isinstance(help_text, str)
        assert "vector.context" in help_text
        assert "Required parameters" in help_text
