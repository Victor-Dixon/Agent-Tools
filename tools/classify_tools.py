#!/usr/bin/env python3
"""
Tool Classification Script
===========================

Classifies tools in the tools/ directory as Signal (working) or Noise (experimental/broken).

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-11-24
Priority: HIGH
"""

import json
import ast
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class ToolClassifier:
    """Classify tools as Signal or Noise."""

    def __init__(self, tools_dir: Path = None):
        """Initialize classifier."""
        self.tools_dir = tools_dir or Path(__file__).parent
        self.classification = {
            "signal": [],
            "noise": [],
            "unknown": []
        }
        self.toolbelt_registry_path = self.tools_dir / "toolbelt_registry.py"

    def load_toolbelt_registry(self) -> Dict[str, Any]:
        """Load registered tools from toolbelt registry."""
        registered = {}
        if self.toolbelt_registry_path.exists():
            try:
                with open(self.toolbelt_registry_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract TOOLS_REGISTRY dict
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name) and target.id == "TOOLS_REGISTRY":
                                    # Try to evaluate the dict
                                    try:
                                        registered = eval(compile(ast.Expression(node.value), '<string>', 'eval'))
                                    except:
                                        pass
            except Exception as e:
                print(f"⚠️ Could not load toolbelt registry: {e}")
        return registered

    def analyze_tool_file(self, tool_path: Path) -> Dict[str, Any]:
        """Analyze a tool file for classification."""
        analysis = {
            "file": str(tool_path.relative_to(self.tools_dir)),
            "name": tool_path.stem,
            "size": tool_path.stat().st_size,
            "has_main": False,
            "has_docstring": False,
            "imports": [],
            "functions": [],
            "classes": [],
            "errors": [],
            "is_registered": False
        }

        try:
            with open(tool_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            # Check for main function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                    if node.name == "main":
                        analysis["has_main"] = True

                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(node.module)

            # Check for docstring
            if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Str):
                analysis["has_docstring"] = True

        except SyntaxError as e:
            analysis["errors"].append(f"Syntax error: {e}")
        except Exception as e:
            analysis["errors"].append(f"Error: {e}")

        return analysis

    def classify_tool(self, analysis: Dict[str, Any], registered_tools: Dict[str, Any]) -> str:
        """Classify tool as Signal, Noise, or Unknown."""
        # Check if registered in toolbelt
        for tool_id, tool_config in registered_tools.items():
            module = tool_config.get("module", "")
            if analysis["name"] in module or analysis["file"].replace("/", ".").replace(".py", "") in module:
                analysis["is_registered"] = True
                return "signal"

        # Signal indicators
        signal_score = 0
        if analysis["has_main"]:
            signal_score += 2
        if analysis["has_docstring"]:
            signal_score += 1
        if len(analysis["functions"]) > 0:
            signal_score += 1
        if len(analysis["errors"]) == 0:
            signal_score += 1

        # Noise indicators
        noise_score = 0
        if len(analysis["errors"]) > 0:
            noise_score += 3
        if analysis["size"] < 100:  # Very small file
            noise_score += 1
        if "test" in analysis["name"].lower() or "check" in analysis["name"].lower():
            noise_score += 1
        if "backup" in analysis["name"].lower() or "old" in analysis["name"].lower():
            noise_score += 2

        # Classification
        if signal_score >= 3 and noise_score == 0:
            return "signal"
        elif noise_score >= 2:
            return "noise"
        else:
            return "unknown"

    def classify_all_tools(self) -> Dict[str, Any]:
        """Classify all tools in tools directory."""
        registered_tools = self.load_toolbelt_registry()
        tool_files = list(self.tools_dir.glob("*.py"))
        tool_files = [f for f in tool_files if f.name != "__init__.py" and f.name != "__main__.py"]

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tools": len(tool_files),
            "signal": [],
            "noise": [],
            "unknown": []
        }

        for tool_file in tool_files:
            analysis = self.analyze_tool_file(tool_file)
            classification = self.classify_tool(analysis, registered_tools)
            analysis["classification"] = classification
            results[classification].append(analysis)

        return results

    def generate_report(self, results: Dict[str, Any], output_path: Path = None) -> str:
        """Generate classification report."""
        output_path = output_path or self.tools_dir / "TOOLS_CLASSIFICATION_REPORT.md"

        report = f"""# 🛠️ Tools Classification Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Tools**: {results['total_tools']}  
**Signal**: {len(results['signal'])}  
**Noise**: {len(results['noise'])}  
**Unknown**: {len(results['unknown'])}

---

## ✅ SIGNAL TOOLS ({len(results['signal'])})

**Status**: Working, useful tools - Add to Tool Belt

"""
        for tool in sorted(results['signal'], key=lambda x: x['name']):
            report += f"- **{tool['name']}** (`{tool['file']}`)\n"
            if tool['is_registered']:
                report += f"  - ✅ Registered in toolbelt\n"
            if tool['has_main']:
                report += f"  - ✅ Has main function\n"
            if tool['errors']:
                report += f"  - ⚠️ Errors: {', '.join(tool['errors'])}\n"
            report += "\n"

        report += f"""
---

## ⚠️ NOISE TOOLS ({len(results['noise'])})

**Status**: Experimental, broken, or unused - Review for improvement, free product, or showcase

"""
        for tool in sorted(results['noise'], key=lambda x: x['name']):
            report += f"- **{tool['name']}** (`{tool['file']}`)\n"
            if tool['errors']:
                report += f"  - ❌ Errors: {', '.join(tool['errors'])}\n"
            if 'backup' in tool['name'].lower() or 'old' in tool['name'].lower():
                report += f"  - 🗑️ Backup/old file - Consider removing\n"
            report += "\n"

        report += f"""
---

## ❓ UNKNOWN TOOLS ({len(results['unknown'])})

**Status**: Needs manual review

"""
        for tool in sorted(results['unknown'], key=lambda x: x['name']):
            report += f"- **{tool['name']}** (`{tool['file']}`)\n"
            report += "\n"

        report += """
---

## 🎯 NEXT STEPS

1. **Review Signal Tools**: Add to toolbelt if not already registered
2. **Review Noise Tools**: 
   - Fix and improve to Signal
   - Package as free product
   - Showcase on DaDudekC website
   - Archive or remove deprecated tools
3. **Review Unknown Tools**: Manual classification needed

---

*Generated by tools/classify_tools.py*
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return str(output_path)


def main():
    """Main entry point."""
    classifier = ToolClassifier()
    print("🔍 Classifying tools...")
    results = classifier.classify_all_tools()
    
    print(f"✅ Classified {results['total_tools']} tools:")
    print(f"   - Signal: {len(results['signal'])}")
    print(f"   - Noise: {len(results['noise'])}")
    print(f"   - Unknown: {len(results['unknown'])}")
    
    report_path = classifier.generate_report(results)
    print(f"📊 Report generated: {report_path}")
    
    # Save JSON results
    json_path = classifier.tools_dir / "TOOLS_CLASSIFICATION.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"📁 JSON results saved: {json_path}")


if __name__ == "__main__":
    main()


