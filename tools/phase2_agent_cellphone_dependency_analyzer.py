#!/usr/bin/env python3
"""
Phase 2 Agent_Cellphone Dependency Analyzer
===========================================

Enhanced dependency analysis for Phase 2 config migration.
Scans for all config-related imports and usage patterns.

Created: 2025-01-28
Agent: Agent-1 (Integration & Core Systems Specialist)
"""

import ast
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config import patterns to search for
CONFIG_IMPORT_PATTERNS = [
    r'from\s+core\.config_manager\s+import',
    r'from\s+config_manager\s+import',
    r'from\s+config\s+import',
    r'from\s+core\.config\s+import',
    r'import\s+config_manager',
    r'import\s+config',
    r'from\s+src\.core\.config_manager\s+import',
    r'from\s+src\.core\.config\s+import',
]

# Config usage patterns
CONFIG_USAGE_PATTERNS = [
    r'ConfigManager\(',
    r'ConfigValidationLevel\.',
    r'ConfigReloadMode\.',
    r'get_repos_root\(',
    r'get_owner_path\(',
    r'get_communications_root\(',
    r'SystemPaths\(',
]


def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in directory."""
    python_files = []
    excluded = {'.git', '__pycache__', 'venv', 'env', 'node_modules', '.venv', 'temp_repos'}
    
    for py_file in root_dir.rglob('*.py'):
        if not any(excluded_dir in py_file.parts for excluded_dir in excluded):
            python_files.append(py_file)
    
    return python_files


def analyze_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single file for config dependencies."""
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        analysis = {
            "file": str(file_path.relative_to(file_path.parts[0])),
            "imports": [],
            "usage": [],
            "line_numbers": {}
        }
        
        # Find imports
        for i, line in enumerate(lines, 1):
            for pattern in CONFIG_IMPORT_PATTERNS:
                if re.search(pattern, line):
                    analysis["imports"].append({
                        "line": i,
                        "statement": line.strip(),
                        "pattern": pattern
                    })
                    if "imports" not in analysis["line_numbers"]:
                        analysis["line_numbers"]["imports"] = []
                    analysis["line_numbers"]["imports"].append(i)
        
        # Find usage patterns
        for i, line in enumerate(lines, 1):
            for pattern in CONFIG_USAGE_PATTERNS:
                if re.search(pattern, line):
                    analysis["usage"].append({
                        "line": i,
                        "code": line.strip(),
                        "pattern": pattern
                    })
                    if "usage" not in analysis["line_numbers"]:
                        analysis["line_numbers"]["usage"] = []
                    analysis["line_numbers"]["usage"].append(i)
        
        # Try AST parsing for more accurate import detection
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if any(keyword in module.lower() for keyword in ['config', 'config_manager']):
                        names = [alias.name for alias in node.names]
                        analysis["imports"].append({
                            "line": node.lineno if hasattr(node, 'lineno') else 0,
                            "statement": f"from {module} import {', '.join(names)}",
                            "ast_detected": True
                        })
        except SyntaxError:
            pass
        
        return analysis if analysis["imports"] or analysis["usage"] else None
    
    except Exception as e:
        logger.warning(f"Error analyzing {file_path}: {e}")
        return None


def generate_dependency_report(analyses: List[Dict[str, Any]], output_path: Path):
    """Generate comprehensive dependency report."""
    # Filter out None results
    analyses = [a for a in analyses if a is not None]
    
    # Group by import type
    config_manager_files = []
    config_files = []
    other_config_files = []
    
    for analysis in analyses:
        has_config_manager = any('config_manager' in imp['statement'].lower() for imp in analysis['imports'])
        has_config = any('from config import' in imp['statement'].lower() or 'import config' in imp['statement'].lower() for imp in analysis['imports'])
        
        if has_config_manager:
            config_manager_files.append(analysis)
        elif has_config:
            config_files.append(analysis)
        else:
            other_config_files.append(analysis)
    
    report = {
        "summary": {
            "total_files_with_config_dependencies": len(analyses),
            "config_manager_files": len(config_manager_files),
            "config_files": len(config_files),
            "other_config_files": len(other_config_files),
            "total_imports": sum(len(a['imports']) for a in analyses),
            "total_usage_patterns": sum(len(a['usage']) for a in analyses)
        },
        "config_manager_dependencies": config_manager_files,
        "config_dependencies": config_files,
        "other_config_dependencies": other_config_files,
        "all_dependencies": analyses
    }
    
    # Save JSON report
    output_path.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
    logger.info(f"✅ Dependency report saved to: {output_path}")
    
    return report


def main():
    """Main execution function."""
    logger.info("🔍 Phase 2 Agent_Cellphone Dependency Analyzer")
    logger.info("=" * 60)
    
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "docs" / "organization"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Analyze all Python files
    logger.info("📂 Scanning Python files...")
    python_files = find_python_files(project_root)
    logger.info(f"   Found {len(python_files)} Python files")
    
    # Analyze each file
    logger.info("🔍 Analyzing config dependencies...")
    analyses = []
    for py_file in python_files:
        analysis = analyze_file(py_file)
        if analysis:
            analyses.append(analysis)
    
    logger.info(f"   Found {len(analyses)} files with config dependencies")
    
    # Generate report
    output_path = output_dir / "PHASE2_AGENT_CELLPHONE_DEPENDENCY_MAP.json"
    report = generate_dependency_report(analyses, output_path)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 DEPENDENCY ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"\nTotal files with config dependencies: {report['summary']['total_files_with_config_dependencies']}")
    print(f"Config Manager imports: {report['summary']['config_manager_files']} files")
    print(f"Config imports: {report['summary']['config_files']} files")
    print(f"Other config dependencies: {report['summary']['other_config_files']} files")
    print(f"Total imports found: {report['summary']['total_imports']}")
    print(f"Total usage patterns: {report['summary']['total_usage_patterns']}")
    
    print("\n📁 Files requiring migration:")
    for analysis in analyses[:10]:  # Show first 10
        print(f"  - {analysis['file']} ({len(analysis['imports'])} imports)")
    
    if len(analyses) > 10:
        print(f"  ... and {len(analyses) - 10} more files")
    
    print(f"\n✅ Full report: {output_path}")


if __name__ == "__main__":
    main()

