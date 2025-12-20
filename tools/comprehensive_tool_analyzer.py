#!/usr/bin/env python3
"""
Comprehensive Tool Analyzer
===========================

Analyzes all tools in the tools/ directory to:
1. Create complete inventory
2. Categorize all tools
3. Identify consolidation opportunities
4. Identify deletion candidates
5. Identify integration opportunities

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-06
"""

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class ToolAnalyzer:
    """Comprehensive tool analysis system."""
    
    # Category patterns
    CATEGORY_PATTERNS = {
        "captain": ["captain_", "captain-"],
        "github": ["github_", "gh_", "pr_", "merge_"],
        "agent": ["agent_", "agent-"],
        "discord": ["discord_", "discord-"],
        "wordpress": ["wordpress_", "wp_", "theme_", "deploy_"],
        "archive": ["archive_", "delete_", "cleanup_"],
        "verify": ["verify_", "check_", "validate_"],
        "analyze": ["analyze_", "analysis_", "analyzer"],
        "consolidation": ["consolidation_", "consolidate_", "merge_"],
        "repository": ["repo_", "repository_", "git_"],
        "monitoring": ["monitor_", "check_", "status_"],
        "queue": ["queue_", "message_", "messaging_"],
        "deployment": ["deploy_", "deployment_", "ftp_", "sftp_"],
        "documentation": ["doc_", "documentation_", "readme_"],
        "testing": ["test_", "testing_", "pytest_"],
        "cli": ["cli_", "command_", "toolbelt_"],
        "data": ["data_", "metrics_", "dashboard_", "report_"],
        "automation": ["auto_", "automation_", "scheduler_"],
        "integration": ["integration_", "integrate_"],
        "workflow": ["workflow_", "execute_", "run_"],
    }
    
    # Known unified tools
    UNIFIED_TOOLS = {
        "unified_validator.py",
        "unified_analyzer.py",
        "unified_monitor.py",
        "unified_agent_status_monitor.py",
    }
    
    # Known deprecated directories
    DEPRECATED_DIRS = {"deprecated", "__pycache__", "examples", "test"}
    
    def __init__(self):
        self.tools_dir = project_root / "tools"
        self.tools = []
        self.categories = defaultdict(list)
        self.imports = defaultdict(set)
        self.consolidation_opportunities = []
        self.deletion_candidates = []
        self.integration_opportunities = []
        
    def get_all_tools(self) -> List[Path]:
        """Get all Python tools, excluding deprecated/test files."""
        tools = []
        for tool_path in self.tools_dir.rglob("*.py"):
            # Skip deprecated, test, and cache directories
            if any(dep in tool_path.parts for dep in self.DEPRECATED_DIRS):
                continue
            # Skip __init__.py and __main__.py
            if tool_path.name in ("__init__.py", "__main__.py"):
                continue
            tools.append(tool_path)
        return sorted(tools)
    
    def categorize_tool(self, tool_path: Path) -> List[str]:
        """Categorize a tool based on filename patterns."""
        name = tool_path.stem.lower()
        categories = []
        
        for category, patterns in self.CATEGORY_PATTERNS.items():
            if any(pattern in name for pattern in patterns):
                categories.append(category)
        
        # Special cases
        if "unified_" in name:
            categories.append("unified")
        if "test_" in name or "_test" in name:
            categories.append("testing")
        if not categories:
            categories.append("miscellaneous")
        
        return categories
    
    def analyze_imports(self, tool_path: Path) -> Set[str]:
        """Analyze imports in a tool file."""
        imports = set()
        try:
            content = tool_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(tool_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except Exception as e:
            # Skip files that can't be parsed
            pass
        
        return imports
    
    def check_if_unified_tool_exists(self, category: str) -> bool:
        """Check if a unified tool exists for this category."""
        unified_names = {
            "captain": "unified_captain.py",
            "github": "unified_github.py",
            "agent": "unified_agent.py",
            "discord": "unified_discord.py",
            "wordpress": "unified_wordpress.py",
            "archive": "unified_cleanup.py",
            "verify": "unified_verifier.py",
            "analyze": "unified_analyzer.py",
            "monitoring": "unified_monitor.py",
        }
        
        if category in unified_names:
            return (self.tools_dir / unified_names[category]).exists()
        return False
    
    def analyze_tool(self, tool_path: Path) -> Dict:
        """Analyze a single tool."""
        rel_path = tool_path.relative_to(self.tools_dir)
        categories = self.categorize_tool(tool_path)
        imports = self.analyze_imports(tool_path)
        
        # Check if registered in toolbelt
        is_registered = self.check_toolbelt_registration(tool_path)
        
        # Check for main function
        has_main = self.check_has_main(tool_path)
        
        # Check file size
        file_size = tool_path.stat().st_size
        line_count = len(tool_path.read_text(encoding='utf-8').splitlines())
        
        return {
            "path": str(rel_path),
            "name": tool_path.name,
            "categories": categories,
            "imports": list(imports),
            "is_registered": is_registered,
            "has_main": has_main,
            "file_size": file_size,
            "line_count": line_count,
            "primary_category": categories[0] if categories else "miscellaneous",
        }
    
    def check_toolbelt_registration(self, tool_path: Path) -> bool:
        """Check if tool is registered in toolbelt registry."""
        try:
            registry_content = (self.tools_dir / "toolbelt_registry.py").read_text(encoding='utf-8')
            tool_name = tool_path.stem
            # Check if tool name appears in registry
            return f'"{tool_name}"' in registry_content or f"'{tool_name}'" in registry_content
        except:
            return False
    
    def check_has_main(self, tool_path: Path) -> bool:
        """Check if tool has main function or __main__ block."""
        try:
            content = tool_path.read_text(encoding='utf-8')
            return 'if __name__ == "__main__"' in content or 'def main(' in content
        except:
            return False
    
    def identify_consolidation_opportunities(self):
        """Identify tools that could be consolidated."""
        # Group by category
        by_category = defaultdict(list)
        for tool in self.tools:
            for cat in tool["categories"]:
                by_category[cat].append(tool)
        
        # Find categories with multiple tools
        for category, tools in by_category.items():
            if len(tools) > 3 and category not in ["unified", "miscellaneous"]:
                # Check if unified tool exists
                if not self.check_if_unified_tool_exists(category):
                    self.consolidation_opportunities.append({
                        "category": category,
                        "tools": tools,
                        "count": len(tools),
                        "recommendation": f"Create unified_{category}.py",
                    })
    
    def identify_deletion_candidates(self):
        """Identify tools that could be deleted."""
        for tool in self.tools:
            # Check if tool is very small (might be stub/empty)
            if tool["line_count"] < 20:
                self.deletion_candidates.append({
                    "tool": tool,
                    "reason": "Very small file (< 20 lines)",
                })
            
            # Check if tool is not registered and has no main
            if not tool["is_registered"] and not tool["has_main"]:
                self.deletion_candidates.append({
                    "tool": tool,
                    "reason": "Not registered and no main function",
                })
    
    def identify_integration_opportunities(self):
        """Identify tools that should be integrated into systems."""
        # Use enhanced integration analyzer for better detection
        try:
            from tools.enhanced_integration_analyzer import EnhancedIntegrationAnalyzer
            
            enhanced_analyzer = EnhancedIntegrationAnalyzer(self.tools_dir)
            enhanced_tools = enhanced_analyzer.analyze_all_tools()
            
            # Convert enhanced analysis to our format
            for enhanced_tool in enhanced_tools:
                # Find matching tool in our tools list
                matching_tool = None
                for tool in self.tools:
                    if tool["path"] == enhanced_tool["path"]:
                        matching_tool = tool
                        break
                
                if matching_tool:
                    integration_type = enhanced_tool.get("integration_type", "unknown")
                    confidence = enhanced_tool.get("confidence", 0.0)
                    
                    # Only include medium+ confidence opportunities
                    if confidence >= 0.3:
                        self.integration_opportunities.append({
                            "tool": matching_tool,
                            "integration_type": integration_type,
                            "confidence": confidence,
                            "recommendation": f"Convert to {integration_type}",
                            "reason": f"Uses core services/patterns (confidence: {confidence:.2f})",
                            "imports": enhanced_tool.get("imports", {}),
                            "patterns": {
                                "service": enhanced_tool.get("service_patterns", {}),
                                "cli": enhanced_tool.get("cli_patterns", {}),
                                "library": enhanced_tool.get("library_patterns", {}),
                            }
                        })
        except Exception as e:
            # Fallback to simple detection if enhanced analyzer fails
            print(f"⚠️  Enhanced integration analyzer failed: {e}, using fallback")
            for tool in self.tools:
                core_imports = {"src.services", "src.core", "src.domain"}
                if any(imp.startswith(tuple(core_imports)) for imp in tool["imports"]):
                    if tool["primary_category"] in ["monitoring", "queue", "agent"]:
                        self.integration_opportunities.append({
                            "tool": tool,
                            "recommendation": "Convert to service or CLI command",
                            "reason": "Uses core services extensively",
                        })
    
    def analyze(self) -> Dict:
        """Run complete analysis."""
        print("🔍 Analyzing all tools...")
        
        # Get all tools
        tool_paths = self.get_all_tools()
        print(f"📊 Found {len(tool_paths)} tools")
        
        # Analyze each tool
        for tool_path in tool_paths:
            tool_data = self.analyze_tool(tool_path)
            self.tools.append(tool_data)
            
            # Categorize
            for cat in tool_data["categories"]:
                self.categories[cat].append(tool_data)
        
        print(f"✅ Analyzed {len(self.tools)} tools")
        print(f"📁 Found {len(self.categories)} categories")
        
        # Identify opportunities
        print("🔍 Identifying consolidation opportunities...")
        self.identify_consolidation_opportunities()
        
        print("🔍 Identifying deletion candidates...")
        self.identify_deletion_candidates()
        
        print("🔍 Identifying integration opportunities...")
        self.identify_integration_opportunities()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate comprehensive report."""
        return {
            "summary": {
                "total_tools": len(self.tools),
                "total_categories": len(self.categories),
                "registered_tools": sum(1 for t in self.tools if t["is_registered"]),
                "unregistered_tools": sum(1 for t in self.tools if not t["is_registered"]),
                "consolidation_opportunities": len(self.consolidation_opportunities),
                "deletion_candidates": len(self.deletion_candidates),
                "integration_opportunities": len(self.integration_opportunities),
            },
            "categories": {
                cat: {
                    "count": len(tools),
                    "tools": [t["name"] for t in tools[:10]],  # First 10
                }
                for cat, tools in self.categories.items()
            },
            "consolidation_opportunities": self.consolidation_opportunities,
            "deletion_candidates": self.deletion_candidates[:50],  # Top 50
            "integration_opportunities": self.integration_opportunities,
            "all_tools": self.tools,
        }


def main():
    """Main function."""
    analyzer = ToolAnalyzer()
    report = analyzer.analyze()
    
    # Save report
    report_file = project_root / "agent_workspaces" / "Agent-5" / "COMPREHENSIVE_TOOLS_ANALYSIS_2025-12-06.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Summary:")
    print(f"   Total tools: {report['summary']['total_tools']}")
    print(f"   Categories: {report['summary']['total_categories']}")
    print(f"   Registered: {report['summary']['registered_tools']}")
    print(f"   Unregistered: {report['summary']['unregistered_tools']}")
    print(f"   Consolidation opportunities: {report['summary']['consolidation_opportunities']}")
    print(f"   Deletion candidates: {report['summary']['deletion_candidates']}")
    print(f"   Integration opportunities: {report['summary']['integration_opportunities']}")
    print(f"\n📄 Report saved: {report_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

