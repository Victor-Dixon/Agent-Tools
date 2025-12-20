#!/usr/bin/env python3
"""
CI Workflow Consolidation Tool
==============================

Analyzes and recommends consolidation of duplicate CI/CD workflows.

Usage:
    python tools/consolidate_ci_workflows.py [--dry-run] [--backup]

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class CIWorkflowAnalyzer:
    """Analyzes CI/CD workflows for consolidation opportunities."""
    
    def __init__(self, workflows_dir: Path):
        """Initialize analyzer."""
        self.workflows_dir = workflows_dir
        self.workflows: Dict[str, Dict] = {}
        
    def analyze_workflows(self) -> Dict:
        """Analyze all workflow files."""
        if not self.workflows_dir.exists():
            return {"error": "Workflows directory not found"}
        
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        
        results = {
            "total_workflows": len(workflow_files),
            "workflows": {},
            "duplicates": [],
            "recommendations": []
        }
        
        for workflow_file in workflow_files:
            try:
                content = workflow_file.read_text(encoding='utf-8')
                # Simple analysis - check for key patterns
                has_testing = "pytest" in content or "test" in content.lower()
                has_linting = "ruff" in content or "black" in content or "lint" in content.lower()
                has_deployment = "deploy" in content.lower() or "release" in content.lower()
                has_v2 = "v2" in content.lower() or "V2" in content
                
                results["workflows"][workflow_file.name] = {
                    "path": str(workflow_file.relative_to(project_root)),
                    "size": len(content),
                    "has_testing": has_testing,
                    "has_linting": has_linting,
                    "has_deployment": has_deployment,
                    "has_v2": has_v2,
                }
            except Exception as e:
                results["workflows"][workflow_file.name] = {"error": str(e)}
        
        # Identify duplicates (same patterns)
        workflow_patterns = {}
        for name, info in results["workflows"].items():
            if "error" in info:
                continue
            pattern = (
                info["has_testing"],
                info["has_linting"],
                info["has_deployment"],
                info["has_v2"]
            )
            if pattern not in workflow_patterns:
                workflow_patterns[pattern] = []
            workflow_patterns[pattern].append(name)
        
        # Find duplicates
        for pattern, files in workflow_patterns.items():
            if len(files) > 1:
                results["duplicates"].append({
                    "pattern": pattern,
                    "files": files
                })
        
        # Generate recommendations
        if results["duplicates"]:
            results["recommendations"].append(
                f"Found {len(results['duplicates'])} duplicate patterns - consolidate workflows"
            )
        
        if results["total_workflows"] > 5:
            results["recommendations"].append(
                f"Too many workflows ({results['total_workflows']}) - recommend consolidation to 3-4 workflows"
            )
        
        return results
    
    def print_report(self, results: Dict):
        """Print analysis report."""
        print("\n" + "="*60)
        print("📋 CI WORKFLOW CONSOLIDATION ANALYSIS")
        print("="*60)
        print(f"Total Workflows: {results['total_workflows']}")
        print(f"Duplicate Patterns: {len(results['duplicates'])}")
        print()
        
        if results['duplicates']:
            print("🔄 DUPLICATE PATTERNS:")
            for dup in results['duplicates']:
                print(f"  Pattern: {dup['pattern']}")
                print(f"  Files: {', '.join(dup['files'])}")
                print()
        
        print("📊 WORKFLOW SUMMARY:")
        for name, info in sorted(results['workflows'].items()):
            if "error" in info:
                print(f"  ❌ {name}: Error - {info['error']}")
            else:
                features = []
                if info['has_testing']:
                    features.append("testing")
                if info['has_linting']:
                    features.append("linting")
                if info['has_deployment']:
                    features.append("deployment")
                if info['has_v2']:
                    features.append("V2")
                print(f"  • {name}: {', '.join(features) if features else 'basic'} ({info['size']} bytes)")
        print()
        
        if results['recommendations']:
            print("💡 RECOMMENDATIONS:")
            for rec in results['recommendations']:
                print(f"  • {rec}")
            print()
        
        print("="*60 + "\n")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze CI/CD workflows for consolidation opportunities"
    )
    parser.add_argument(
        '--workflows-dir',
        type=Path,
        default=project_root / ".github" / "workflows",
        help='Path to workflows directory'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Save analysis results to JSON file'
    )
    
    args = parser.parse_args()
    
    analyzer = CIWorkflowAnalyzer(args.workflows_dir)
    results = analyzer.analyze_workflows()
    analyzer.print_report(results)
    
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2), encoding='utf-8')
        print(f"✅ Analysis saved to: {args.output}")
    
    sys.exit(0)


if __name__ == '__main__':
    main()

