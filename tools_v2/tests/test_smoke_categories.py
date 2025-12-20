"""
Category Smoke Tests
====================

Smoke tests for all tool category modules.

V2 Compliance: <200 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest

from tools_v2.adapters import IToolAdapter


class TestCategoryImports:
    """Test all category modules can be imported."""

    def test_import_vector_tools(self):
        """Test vector_tools module imports."""
        from tools_v2.categories import vector_tools

        assert hasattr(vector_tools, "TaskContextTool")
        assert hasattr(vector_tools, "VectorSearchTool")
        assert hasattr(vector_tools, "IndexWorkTool")

    def test_import_messaging_tools(self):
        """Test messaging_tools module imports."""
        from tools_v2.categories import messaging_tools

        assert hasattr(messaging_tools, "SendMessageTool")
        assert hasattr(messaging_tools, "BroadcastTool")
        assert hasattr(messaging_tools, "InboxCheckTool")

    def test_import_analysis_tools(self):
        """Test analysis_tools module imports."""
        from tools_v2.categories import analysis_tools

        assert hasattr(analysis_tools, "ProjectScanTool")
        assert hasattr(analysis_tools, "ComplexityTool")
        assert hasattr(analysis_tools, "DuplicationTool")

    def test_import_v2_tools(self):
        """Test v2_tools module imports."""
        from tools_v2.categories import v2_tools

        assert hasattr(v2_tools, "V2CheckTool")
        assert hasattr(v2_tools, "V2ReportTool")

    def test_import_agent_ops_tools(self):
        """Test agent_ops_tools module imports."""
        from tools_v2.categories import agent_ops_tools

        assert hasattr(agent_ops_tools, "AgentStatusTool")
        assert hasattr(agent_ops_tools, "ClaimTaskTool")

    def test_import_testing_tools(self):
        """Test testing_tools module imports."""
        from tools_v2.categories import testing_tools

        assert hasattr(testing_tools, "CoverageReportTool")
        assert hasattr(testing_tools, "MutationGateTool")

    def test_import_compliance_tools(self):
        """Test compliance_tools module imports."""
        from tools_v2.categories import compliance_tools

        assert hasattr(compliance_tools, "ComplianceHistoryTool")
        assert hasattr(compliance_tools, "PolicyCheckTool")

    def test_import_onboarding_tools(self):
        """Test onboarding_tools module imports."""
        from tools_v2.categories import onboarding_tools

        assert hasattr(onboarding_tools, "SoftOnboardTool")
        assert hasattr(onboarding_tools, "HardOnboardTool")

    def test_import_docs_tools(self):
        """Test docs_tools module imports."""
        from tools_v2.categories import docs_tools

        assert hasattr(docs_tools, "DocsSearchTool")
        assert hasattr(docs_tools, "DocsExportTool")

    def test_import_health_tools(self):
        """Test health_tools module imports."""
        from tools_v2.categories import health_tools

        assert hasattr(health_tools, "HealthPingTool")
        assert hasattr(health_tools, "SnapshotTool")


class TestAdapterInterface:
    """Test all adapters implement IToolAdapter correctly."""

    @pytest.mark.parametrize(
        "tool_class_path",
        [
            ("tools_v2.categories.vector_tools", "TaskContextTool"),
            ("tools_v2.categories.messaging_tools", "SendMessageTool"),
            ("tools_v2.categories.analysis_tools", "ProjectScanTool"),
            ("tools_v2.categories.v2_tools", "V2CheckTool"),
            ("tools_v2.categories.agent_ops_tools", "AgentStatusTool"),
            ("tools_v2.categories.testing_tools", "CoverageReportTool"),
            ("tools_v2.categories.compliance_tools", "ComplianceHistoryTool"),
            ("tools_v2.categories.onboarding_tools", "SoftOnboardTool"),
            ("tools_v2.categories.docs_tools", "DocsSearchTool"),
            ("tools_v2.categories.health_tools", "HealthPingTool"),
        ],
    )
    def test_adapter_implements_interface(self, tool_class_path):
        """Test adapter implements IToolAdapter interface."""
        module_path, class_name = tool_class_path

        import importlib

        module = importlib.import_module(module_path)
        tool_class = getattr(module, class_name)

        assert issubclass(tool_class, IToolAdapter)

        # Test instantiation
        adapter = tool_class()
        assert adapter is not None

        # Test required methods exist
        assert callable(adapter.get_spec)
        assert callable(adapter.validate)
        assert callable(adapter.execute)
        assert callable(adapter.get_help)

        # Test spec is valid
        spec = adapter.get_spec()
        assert spec.name is not None
        assert spec.version is not None
        assert spec.category is not None
