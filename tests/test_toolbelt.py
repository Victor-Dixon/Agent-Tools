import sys
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.toolbelt_registry import ToolRegistry
from tools.cli import main

class TestToolbelt:
    def test_registry_loading(self):
        """Test that registry loads and contains expected tools."""
        registry = ToolRegistry()
        assert "monitor" in registry.tools
        assert "validator" in registry.tools
        assert "analyzer" in registry.tools
        
        # Check flags mapping
        assert registry.get_tool_for_flag("--monitor")["id"] == "monitor"
        assert registry.get_tool_for_flag("-m")["id"] == "monitor"

    def test_registry_paths_exist(self):
        """Test that all registered tool modules actually exist."""
        registry = ToolRegistry()
        workspace_root = Path(__file__).parent.parent
        
        for tool_id, config in registry.tools.items():
            module_path = config["module"].replace(".", "/") + ".py"
            full_path = workspace_root / module_path
            assert full_path.exists(), f"Tool {tool_id} module missing: {module_path}"

    def test_help_generation(self):
        """Test that help generation runs without error."""
        with patch("sys.argv", ["tools/cli.py", "--help"]):
            # argparse --help calls sys.exit(0), so we catch SystemExit
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_list_tools(self):
        """Test that tool listing runs without error."""
        with patch("sys.argv", ["tools/cli.py", "--list"]):
            assert main() == 0
