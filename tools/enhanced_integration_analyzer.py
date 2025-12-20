#!/usr/bin/env python3
"""
Enhanced Integration Analyzer
==============================

Enhanced analysis for identifying tools that should be converted to:
- Services (src/services/)
- CLI commands (tools_v2/cli/)
- Library utilities (src/core/utils/ or src/utils/)

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-06
"""

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class EnhancedIntegrationAnalyzer:
    """Enhanced integration opportunity analyzer."""
    
    def __init__(self, tools_dir: Path = None):
        """Initialize analyzer."""
        self.tools_dir = tools_dir or project_root / "tools"
        self.integration_opportunities = []
    
    def analyze_tool_imports(self, tool_path: Path) -> Dict[str, Any]:
        """Analyze tool imports to detect service/core/domain usage."""
        try:
            content = tool_path.read_text(encoding='utf-8', errors='ignore')
            
            # Parse imports
            imports = {
                "src_services": [],
                "src_core": [],
                "src_domain": [],
                "src_utils": [],
                "src_web": [],
                "other": []
            }
            
            # Extract import statements
            import_patterns = [
                (r'from\s+(src\.services\.[\w\.]+)\s+import', 'src_services'),
                (r'from\s+(src\.core\.[\w\.]+)\s+import', 'src_core'),
                (r'from\s+(src\.domain\.[\w\.]+)\s+import', 'src_domain'),
                (r'from\s+(src\.utils\.[\w\.]+)\s+import', 'src_utils'),
                (r'from\s+(src\.web\.[\w\.]+)\s+import', 'src_web'),
                (r'import\s+(src\.services\.[\w\.]+)', 'src_services'),
                (r'import\s+(src\.core\.[\w\.]+)', 'src_core'),
                (r'import\s+(src\.domain\.[\w\.]+)', 'src_domain'),
            ]
            
            for pattern, category in import_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    imports[category].extend(matches)
            
            return imports
        except Exception as e:
            return {"error": str(e)}
    
    def detect_service_patterns(self, tool_path: Path) -> Dict[str, Any]:
        """Detect service-like code patterns."""
        try:
            content = tool_path.read_text(encoding='utf-8', errors='ignore')
            
            patterns = {
                "has_service_class": bool(re.search(r'class\s+\w+Service\s*\(', content)),
                "has_manager_class": bool(re.search(r'class\s+\w+Manager\s*\(', content)),
                "has_handler_class": bool(re.search(r'class\s+\w+Handler\s*\(', content)),
                "has_repository_class": bool(re.search(r'class\s+\w+Repository\s*\(', content)),
                "has_async_functions": bool(re.search(r'async\s+def\s+\w+', content)),
                "has_database_operations": bool(re.search(r'(execute|query|fetch|commit|rollback)', content, re.IGNORECASE)),
                "has_api_calls": bool(re.search(r'(requests\.|httpx\.|aiohttp\.|urllib\.)', content)),
                "has_message_queue": bool(re.search(r'(queue|message_queue|rabbitmq|redis)', content, re.IGNORECASE)),
                "has_websocket": bool(re.search(r'(websocket|ws://|wss://)', content, re.IGNORECASE)),
                "has_scheduled_tasks": bool(re.search(r'(schedule|scheduler|cron|periodic)', content, re.IGNORECASE)),
                "function_count": len(re.findall(r'def\s+\w+', content)),
                "class_count": len(re.findall(r'class\s+\w+', content)),
            }
            
            return patterns
        except Exception as e:
            return {"error": str(e)}
    
    def detect_cli_patterns(self, tool_path: Path) -> Dict[str, Any]:
        """Detect CLI-like code patterns."""
        try:
            content = tool_path.read_text(encoding='utf-8', errors='ignore')
            
            patterns = {
                "has_argparse": bool(re.search(r'argparse|ArgumentParser', content)),
                "has_click": bool(re.search(r'import\s+click|@click\.', content)),
                "has_main_function": bool(re.search(r'def\s+main\s*\(|if\s+__name__\s*==\s*["\']__main__["\']', content)),
                "has_command_decorators": bool(re.search(r'@\w+\.command|@click\.command', content)),
                "has_subcommands": bool(re.search(r'add_subparsers|subcommands', content)),
                "prints_to_stdout": bool(re.search(r'print\s*\(', content)),
                "reads_stdin": bool(re.search(r'sys\.stdin|input\s*\(', content)),
            }
            
            return patterns
        except Exception as e:
            return {"error": str(e)}
    
    def detect_library_patterns(self, tool_path: Path) -> Dict[str, Any]:
        """Detect library/utility-like code patterns."""
        try:
            content = tool_path.read_text(encoding='utf-8', errors='ignore')
            
            patterns = {
                "has_utility_functions": bool(re.search(r'def\s+(get_|set_|create_|delete_|update_|find_|search_)', content)),
                "has_helper_functions": bool(re.search(r'def\s+(helper_|util_|format_|parse_|convert_)', content)),
                "has_constants": bool(re.search(r'^[A-Z_]{3,}\s*=', content, re.MULTILINE)),
                "has_data_classes": bool(re.search(r'@dataclass|class\s+\w+.*:\s*$', content, re.MULTILINE)),
                "has_type_hints": bool(re.search(r'->\s*\w+|:\s*\w+\[', content)),
                "no_main_function": not bool(re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', content)),
                "pure_functions": len(re.findall(r'def\s+\w+.*->', content)),
            }
            
            return patterns
        except Exception as e:
            return {"error": str(e)}
    
    def categorize_integration_opportunity(self, tool_data: Dict[str, Any]) -> str:
        """Categorize integration opportunity type."""
        imports = tool_data.get("imports", {})
        service_patterns = tool_data.get("service_patterns", {})
        cli_patterns = tool_data.get("cli_patterns", {})
        library_patterns = tool_data.get("library_patterns", {})
        
        # Service indicators
        service_score = 0
        if imports.get("src_services"):
            service_score += 10
        if service_patterns.get("has_service_class"):
            service_score += 5
        if service_patterns.get("has_manager_class"):
            service_score += 3
        if service_patterns.get("has_async_functions"):
            service_score += 3
        if service_patterns.get("has_database_operations"):
            service_score += 5
        if service_patterns.get("has_message_queue"):
            service_score += 5
        if service_patterns.get("has_api_calls"):
            service_score += 2
        
        # CLI indicators
        cli_score = 0
        if cli_patterns.get("has_argparse"):
            cli_score += 5
        if cli_patterns.get("has_click"):
            cli_score += 5
        if cli_patterns.get("has_main_function"):
            cli_score += 3
        if cli_patterns.get("has_command_decorators"):
            cli_score += 3
        if cli_patterns.get("prints_to_stdout"):
            cli_score += 2
        
        # Library indicators
        library_score = 0
        if library_patterns.get("has_utility_functions"):
            library_score += 3
        if library_patterns.get("has_helper_functions"):
            library_score += 3
        if library_patterns.get("has_constants"):
            library_score += 2
        if library_patterns.get("has_data_classes"):
            library_score += 2
        if library_patterns.get("no_main_function"):
            library_score += 3
        if library_patterns.get("pure_functions", 0) > 3:
            library_score += 3
        
        # Determine category
        if service_score >= 10:
            return "service"
        elif cli_score >= 8:
            return "cli"
        elif library_score >= 8:
            return "library"
        elif service_score > cli_score and service_score > library_score:
            return "service"
        elif cli_score > library_score:
            return "cli"
        else:
            return "library"
    
    def analyze_tool(self, tool_path: Path) -> Dict[str, Any]:
        """Comprehensive tool analysis for integration opportunities."""
        imports = self.analyze_tool_imports(tool_path)
        service_patterns = self.detect_service_patterns(tool_path)
        cli_patterns = self.detect_cli_patterns(tool_path)
        library_patterns = self.detect_library_patterns(tool_path)
        
        # Get basic tool info
        try:
            content = tool_path.read_text(encoding='utf-8', errors='ignore')
            line_count = len(content.splitlines())
            file_size = tool_path.stat().st_size
        except:
            line_count = 0
            file_size = 0
        
        tool_data = {
            "path": str(tool_path.relative_to(self.tools_dir)),
            "name": tool_path.name,
            "imports": imports,
            "service_patterns": service_patterns,
            "cli_patterns": cli_patterns,
            "library_patterns": library_patterns,
            "line_count": line_count,
            "file_size": file_size,
        }
        
        # Categorize integration opportunity
        integration_type = self.categorize_integration_opportunity(tool_data)
        tool_data["integration_type"] = integration_type
        
        # Calculate confidence score
        confidence = self.calculate_confidence(tool_data)
        tool_data["confidence"] = confidence
        
        return tool_data
    
    def calculate_confidence(self, tool_data: Dict[str, Any]) -> float:
        """Calculate confidence score for integration recommendation."""
        score = 0.0
        
        # Import-based confidence
        imports = tool_data.get("imports", {})
        if imports.get("src_services"):
            score += 0.3
        if imports.get("src_core"):
            score += 0.2
        if imports.get("src_domain"):
            score += 0.2
        
        # Pattern-based confidence
        service_patterns = tool_data.get("service_patterns", {})
        if service_patterns.get("has_service_class"):
            score += 0.2
        if service_patterns.get("has_async_functions"):
            score += 0.1
        
        cli_patterns = tool_data.get("cli_patterns", {})
        if cli_patterns.get("has_argparse") or cli_patterns.get("has_click"):
            score += 0.2
        
        library_patterns = tool_data.get("library_patterns", {})
        if library_patterns.get("has_utility_functions") and library_patterns.get("no_main_function"):
            score += 0.2
        
        return min(score, 1.0)
    
    def analyze_all_tools(self) -> List[Dict[str, Any]]:
        """Analyze all tools for integration opportunities."""
        print("🔍 Analyzing tools for integration opportunities...")
        
        tools = []
        python_files = list(self.tools_dir.rglob("*.py"))
        
        for tool_path in python_files:
            # Skip __init__.py and test files
            if tool_path.name == "__init__.py" or tool_path.name.startswith("test_"):
                continue
            
            # Skip unified tools (already consolidated)
            if tool_path.name.startswith("unified_"):
                continue
            
            try:
                tool_data = self.analyze_tool(tool_path)
                
                # Only include tools with integration potential
                if tool_data.get("confidence", 0) > 0.1:
                    tools.append(tool_data)
            except Exception as e:
                print(f"⚠️  Error analyzing {tool_path}: {e}")
        
        # Sort by confidence (highest first)
        tools.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return tools
    
    def generate_report(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate integration opportunities report."""
        # Group by integration type
        by_type = defaultdict(list)
        for tool in tools:
            integration_type = tool.get("integration_type", "unknown")
            by_type[integration_type].append(tool)
        
        # Calculate statistics
        stats = {
            "total_opportunities": len(tools),
            "service_opportunities": len(by_type["service"]),
            "cli_opportunities": len(by_type["cli"]),
            "library_opportunities": len(by_type["library"]),
            "high_confidence": len([t for t in tools if t.get("confidence", 0) >= 0.5]),
            "medium_confidence": len([t for t in tools if 0.3 <= t.get("confidence", 0) < 0.5]),
            "low_confidence": len([t for t in tools if t.get("confidence", 0) < 0.3]),
        }
        
        return {
            "summary": stats,
            "by_type": {
                "service": by_type["service"][:20],  # Top 20
                "cli": by_type["cli"][:20],
                "library": by_type["library"][:20],
            },
            "all_opportunities": tools,
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Integration Analyzer")
    parser.add_argument("--output", type=Path, help="Output JSON file")
    parser.add_argument("--tools-dir", type=Path, help="Tools directory (default: tools/)")
    
    args = parser.parse_args()
    
    tools_dir = args.tools_dir or project_root / "tools"
    analyzer = EnhancedIntegrationAnalyzer(tools_dir)
    
    print("🚀 Starting enhanced integration analysis...")
    tools = analyzer.analyze_all_tools()
    
    print(f"✅ Analyzed {len(tools)} tools with integration potential")
    
    report = analyzer.generate_report(tools)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 INTEGRATION OPPORTUNITIES SUMMARY")
    print("=" * 70)
    print(f"Total Opportunities: {report['summary']['total_opportunities']}")
    print(f"  Service: {report['summary']['service_opportunities']}")
    print(f"  CLI: {report['summary']['cli_opportunities']}")
    print(f"  Library: {report['summary']['library_opportunities']}")
    print(f"\nConfidence Levels:")
    print(f"  High (≥0.5): {report['summary']['high_confidence']}")
    print(f"  Medium (0.3-0.5): {report['summary']['medium_confidence']}")
    print(f"  Low (<0.3): {report['summary']['low_confidence']}")
    
    # Save report
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Report saved to: {args.output}")
    else:
        # Default output
        output_path = project_root / "agent_workspaces" / "Agent-5" / "ENHANCED_INTEGRATION_ANALYSIS_2025-12-06.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Report saved to: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

