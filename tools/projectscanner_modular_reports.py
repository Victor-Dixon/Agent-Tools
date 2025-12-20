#!/usr/bin/env python3
"""
Project Scanner - Modular Report Generator
==========================================

Creates agent-digestible analysis files instead of one massive JSON.
Reports are optimized for 15k character chunking for agent consumption.

V2 Compliance: Extracted from projectscanner.py (1,153 lines → modular)
Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-10-11
License: MIT
"""

import json
import logging
from pathlib import Path
from collections import defaultdict

# Import chunking utility from SSOT
try:
    import sys
    from pathlib import Path
    # Add tools directory to path for import
    tools_dir = Path(__file__).parent
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    from chunk_reports import chunk_json_report, CHUNK_SIZE
except ImportError:
    # Fallback if chunk_reports not available
    CHUNK_SIZE = 15000
    chunk_json_report = None

logger = logging.getLogger(__name__)


class ModularReportGenerator:
    """Creates modular, agent-digestible analysis files optimized for chunking."""

    def __init__(self, project_root: Path, analysis: dict[str, dict]):
        self.project_root = project_root
        self.analysis = analysis

    def generate_modular_reports(self):
        """Generate multiple smaller, focused analysis files."""
        logger.info("🔄 Generating modular analysis reports...")

        # Create analysis directory
        analysis_dir = self.project_root / "analysis"
        analysis_dir.mkdir(exist_ok=True)

        # Generate different types of analysis
        self._generate_agent_analysis(analysis_dir)
        self._generate_module_analysis(analysis_dir)
        self._generate_file_type_analysis(analysis_dir)
        self._generate_complexity_analysis(analysis_dir)
        self._generate_dependency_analysis(analysis_dir)
        self._generate_architecture_overview(analysis_dir)

        logger.info("✅ Modular analysis reports generated successfully!")

    def _generate_agent_analysis(self, analysis_dir: Path):
        """Generate agent-specific analysis files."""
        agent_analysis = defaultdict(lambda: {
            "agent_id": "",
            "files": [],
            "total_functions": 0,
            "total_classes": 0,
            "total_complexity": 0,
            "key_files": [],
        })

        for file_path, file_data in self.analysis.items():
            # Check if file is in agent workspace (handle both formats)
            agent_id = None
            if "agent_workspaces" in file_path or "Agent-" in file_path:
                parts = file_path.replace("\\", "/").split("/")
                for i, part in enumerate(parts):
                    if part.startswith("Agent-"):
                        agent_id = part
                        break

            if agent_id:
                agent_analysis[agent_id]["agent_id"] = agent_id
                file_info = {
                    "path": file_path,
                    "functions": file_data.get("functions", []),
                    "function_count": len(file_data.get("functions", [])),
                    "classes": list(file_data.get("classes", {}).keys()) if isinstance(file_data.get("classes"), dict) else [],
                    "class_count": len(file_data.get("classes", {})) if isinstance(file_data.get("classes"), dict) else 0,
                    "complexity": file_data.get("complexity", 0),
                    "language": file_data.get("language", "unknown"),
                }
                agent_analysis[agent_id]["files"].append(file_info)
                agent_analysis[agent_id]["total_functions"] += file_info["function_count"]
                agent_analysis[agent_id]["total_classes"] += file_info["class_count"]
                agent_analysis[agent_id]["total_complexity"] += file_info["complexity"]

                # Track key files (high complexity or many functions/classes)
                if file_info["complexity"] > 10 or file_info["function_count"] > 5 or file_info["class_count"] > 2:
                    agent_analysis[agent_id]["key_files"].append({
                        "path": file_path,
                        "reason": self._get_key_file_reason(file_info),
                    })

        # Convert defaultdict to dict and sort by agent_id
        result = {k: dict(v) for k, v in sorted(agent_analysis.items())}

        # Save agent analysis
        output_path = analysis_dir / "agent_analysis.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        logger.info(
            f"📊 Agent analysis saved to {output_path} ({len(result)} agents)")

    def _get_key_file_reason(self, file_info: dict) -> str:
        """Generate reason why file is considered key."""
        reasons = []
        if file_info["complexity"] > 10:
            reasons.append(f"high complexity ({file_info['complexity']})")
        if file_info["function_count"] > 5:
            reasons.append(f"many functions ({file_info['function_count']})")
        if file_info["class_count"] > 2:
            reasons.append(f"many classes ({file_info['class_count']})")
        return ", ".join(reasons) if reasons else "significant code"

    def _generate_module_analysis(self, analysis_dir: Path):
        """Generate module/component-specific analysis."""
        module_analysis = defaultdict(lambda: {
            "module": "",
            "files": [],
            "total_functions": 0,
            "total_classes": 0,
            "languages": set(),
            "total_complexity": 0,
            "file_count": 0,
        })

        for file_path, file_data in self.analysis.items():
            # Extract module name (first directory or top-level)
            normalized_path = file_path.replace("\\", "/")
            parts = normalized_path.split("/")

            # Skip agent workspaces and cache
            if parts[0] in ["agent_workspaces", "__pycache__", ".git"]:
                continue

            module = parts[0] if len(parts) > 1 else "root"

            module_analysis[module]["module"] = module
            file_info = {
                "path": file_path,
                "language": file_data.get("language", "unknown"),
                "functions": file_data.get("functions", []),
                "function_count": len(file_data.get("functions", [])),
                "classes": list(file_data.get("classes", {}).keys()) if isinstance(file_data.get("classes"), dict) else [],
                "class_count": len(file_data.get("classes", {})) if isinstance(file_data.get("classes"), dict) else 0,
                "complexity": file_data.get("complexity", 0),
            }
            module_analysis[module]["files"].append(file_info)
            module_analysis[module]["total_functions"] += file_info["function_count"]
            module_analysis[module]["total_classes"] += file_info["class_count"]
            module_analysis[module]["languages"].add(
                file_data.get("language", "unknown"))
            module_analysis[module]["total_complexity"] += file_info["complexity"]
            module_analysis[module]["file_count"] += 1

        # Convert sets to lists and sort
        result = {}
        for module, data in sorted(module_analysis.items()):
            data["languages"] = sorted(list(data["languages"]))
            # Sort files by complexity (most complex first)
            data["files"].sort(key=lambda x: x["complexity"], reverse=True)
            result[module] = dict(data)

        # Save module analysis
        output_path = analysis_dir / "module_analysis.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        logger.info(
            f"📊 Module analysis saved to {output_path} ({len(result)} modules)")

    def _generate_file_type_analysis(self, analysis_dir: Path):
        """Generate analysis grouped by file type."""
        file_type_analysis = defaultdict(lambda: {
            "file_type": "",
            "files": [],
            "total_functions": 0,
            "total_classes": 0,
            "total_complexity": 0,
            "file_count": 0,
            "avg_complexity": 0,
        })

        for file_path, file_data in self.analysis.items():
            file_type = file_data.get("language", "unknown")
            file_type_analysis[file_type]["file_type"] = file_type

            file_info = {
                "path": file_path,
                "functions": file_data.get("functions", []),
                "function_count": len(file_data.get("functions", [])),
                "classes": list(file_data.get("classes", {}).keys()) if isinstance(file_data.get("classes"), dict) else [],
                "class_count": len(file_data.get("classes", {})) if isinstance(file_data.get("classes"), dict) else 0,
                "complexity": file_data.get("complexity", 0),
            }
            file_type_analysis[file_type]["files"].append(file_info)
            file_type_analysis[file_type]["total_functions"] += file_info["function_count"]
            file_type_analysis[file_type]["total_classes"] += file_info["class_count"]
            file_type_analysis[file_type]["total_complexity"] += file_info["complexity"]
            file_type_analysis[file_type]["file_count"] += 1

        # Calculate averages and sort
        result = {}
        for file_type, data in sorted(file_type_analysis.items()):
            if data["file_count"] > 0:
                data["avg_complexity"] = round(
                    data["total_complexity"] / data["file_count"], 2)
            # Sort files by complexity
            data["files"].sort(key=lambda x: x["complexity"], reverse=True)
            result[file_type] = dict(data)

        # Save file type analysis
        output_path = analysis_dir / "file_type_analysis.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        logger.info(
            f"📊 File type analysis saved to {output_path} ({len(result)} types)")

    def _generate_complexity_analysis(self, analysis_dir: Path):
        """Generate complexity-focused analysis."""
        complexity_analysis = {
            "complexity_distribution": {},
            "high_complexity_files": [],
            "low_complexity_files": [],
            "average_complexity": 0,
            "total_files": 0,
            "complexity_ranges": {
                "simple": [],  # complexity 1-5
                "moderate": [],  # complexity 6-15
                "complex": [],  # complexity 16-30
                "very_complex": [],  # complexity > 30
            },
        }

        total_complexity = 0
        file_count = 0
        complexity_counts = defaultdict(int)

        for file_path, file_data in self.analysis.items():
            complexity = file_data.get("complexity", 0)
            total_complexity += complexity
            file_count += 1
            complexity_counts[complexity] += 1

            file_info = {
                "path": file_path,
                "complexity": complexity,
                "functions": len(file_data.get("functions", [])),
                "classes": len(file_data.get("classes", {})) if isinstance(file_data.get("classes"), dict) else 0,
                "language": file_data.get("language", "unknown"),
            }

            # Categorize by complexity ranges
            if complexity <= 5:
                complexity_analysis["complexity_ranges"]["simple"].append(
                    file_info)
            elif complexity <= 15:
                complexity_analysis["complexity_ranges"]["moderate"].append(
                    file_info)
            elif complexity <= 30:
                complexity_analysis["complexity_ranges"]["complex"].append(
                    file_info)
            else:
                complexity_analysis["complexity_ranges"]["very_complex"].append(
                    file_info)

            # Track high and low complexity files
            if complexity >= 20:
                complexity_analysis["high_complexity_files"].append(file_info)
            elif complexity <= 3 and complexity > 0:
                complexity_analysis["low_complexity_files"].append(file_info)

        if file_count > 0:
            complexity_analysis["average_complexity"] = round(
                total_complexity / file_count, 2)
        complexity_analysis["total_files"] = file_count
        complexity_analysis["complexity_distribution"] = dict(
            sorted(complexity_counts.items()))

        # Sort high complexity files by complexity (most complex first)
        complexity_analysis["high_complexity_files"].sort(
            key=lambda x: x["complexity"], reverse=True)
        # Top 100
        complexity_analysis["high_complexity_files"] = complexity_analysis["high_complexity_files"][:100]

        # Save complexity analysis
        output_path = analysis_dir / "complexity_analysis.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(complexity_analysis, f, indent=2)
        logger.info(f"📊 Complexity analysis saved to {output_path}")

    def _generate_dependency_analysis(self, analysis_dir: Path):
        """Generate dependency/import analysis."""
        dependency_analysis = {
            "imports_by_module": {},
            "most_imported_modules": {},
            "circular_dependencies": [],
            "external_dependencies": set(),
            "internal_dependencies": {},
            "module_summary": {},
        }

        # Analyze internal structure
        for file_path, file_data in self.analysis.items():
            if file_path.endswith((".py", ".ts", ".js")):
                normalized_path = file_path.replace("\\", "/")
                module_name = normalized_path.replace(
                    "/", ".").rsplit(".", 1)[0]

                dependency_analysis["internal_dependencies"][module_name] = {
                    "file_path": file_path,
                    "function_count": len(file_data.get("functions", [])),
                    "class_count": len(file_data.get("classes", {})) if isinstance(file_data.get("classes"), dict) else 0,
                    "complexity": file_data.get("complexity", 0),
                    "language": file_data.get("language", "unknown"),
                }

        # Convert set to list for JSON
        dependency_analysis["external_dependencies"] = sorted(
            list(dependency_analysis["external_dependencies"]))

        # Save dependency analysis
        output_path = analysis_dir / "dependency_analysis.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(dependency_analysis, f, indent=2)
        logger.info(f"📊 Dependency analysis saved to {output_path}")

    def _generate_architecture_overview(self, analysis_dir: Path):
        """Generate high-level architecture overview."""
        architecture_overview = {
            "project_structure": {},
            "key_components": [],
            "architecture_patterns": [],
            "code_metrics": {
                "total_files": len(self.analysis),
                "total_functions": 0,
                "total_classes": 0,
                "total_complexity": 0,
                "languages_used": set(),
            },
            "recommendations": [],
        }

        # Calculate metrics
        top_level_dirs = defaultdict(
            lambda: {"files": [], "functions": 0, "classes": 0, "complexity": 0})

        for file_path, file_data in self.analysis.items():
            normalized_path = file_path.replace("\\", "/")
            parts = normalized_path.split("/")
            top_level = parts[0] if len(parts) > 1 else "root"

            # Skip cache and git
            if top_level in ["__pycache__", ".git", "node_modules"]:
                continue

            top_level_dirs[top_level]["files"].append(file_path)
            top_level_dirs[top_level]["functions"] += len(
                file_data.get("functions", []))
            top_level_dirs[top_level]["classes"] += len(file_data.get(
                "classes", {})) if isinstance(file_data.get("classes"), dict) else 0
            top_level_dirs[top_level]["complexity"] += file_data.get(
                "complexity", 0)

            architecture_overview["code_metrics"]["total_functions"] += len(
                file_data.get("functions", []))
            architecture_overview["code_metrics"]["total_classes"] += len(file_data.get(
                "classes", {})) if isinstance(file_data.get("classes"), dict) else 0
            architecture_overview["code_metrics"]["total_complexity"] += file_data.get(
                "complexity", 0)
            architecture_overview["code_metrics"]["languages_used"].add(
                file_data.get("language", "unknown"))

        # Convert set to list
        architecture_overview["code_metrics"]["languages_used"] = sorted(
            list(architecture_overview["code_metrics"]["languages_used"]))
        architecture_overview["project_structure"] = {k: {
            "file_count": len(v["files"]),
            "functions": v["functions"],
            "classes": v["classes"],
            "complexity": v["complexity"],
        } for k, v in sorted(top_level_dirs.items())}

        # Identify key components (high complexity or many files)
        for top_level, data in top_level_dirs.items():
            if data["complexity"] > 100 or len(data["files"]) > 50:
                architecture_overview["key_components"].append({
                    "name": top_level,
                    "file_count": len(data["files"]),
                    "complexity": data["complexity"],
                    "functions": data["functions"],
                    "classes": data["classes"],
                })

        # Sort key components by complexity
        architecture_overview["key_components"].sort(
            key=lambda x: x["complexity"], reverse=True)

        # Save architecture overview
        output_path = analysis_dir / "architecture_overview.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(architecture_overview, f, indent=2)
        logger.info(f"📊 Architecture overview saved to {output_path}")

    @staticmethod
    def chunk_report(report_path: Path, chunk_size: int = CHUNK_SIZE) -> list[str]:
        """
        Chunk a JSON report into 15k character pieces for agent consumption.
        Returns list of JSON strings, each under chunk_size characters.

        DEPRECATED: Use chunk_json_report from chunk_reports.py (SSOT) instead.
        This method is kept for backward compatibility but delegates to SSOT.
        """
        if chunk_json_report is None:
            logger.warning(
                "chunk_reports.py not available, falling back to simple chunking"
            )
            # Fallback implementation
            with report_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            json_str = json.dumps(data, indent=2)
            if len(json_str) <= chunk_size:
                return [json_str]
            return [json_str[i:i+chunk_size] for i in range(0, len(json_str), chunk_size)]

        # Use SSOT implementation
        return chunk_json_report(report_path, chunk_size)
