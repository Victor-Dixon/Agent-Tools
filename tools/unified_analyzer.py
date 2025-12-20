#!/usr/bin/env python3
"""
Unified Analyzer - Consolidated Analysis Tool
==============================================

<!-- SSOT Domain: analytics -->

Consolidates all analysis capabilities into a single unified tool.
Replaces multiple individual analysis tools with modular analysis system.

Analysis Categories:
- Repository Analysis
- Project Structure Analysis
- Code Analysis
- Consolidation Detection
- Overlap Detection
- File Analysis

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<400 lines)
"""

import argparse
import ast
import json
import os
import re
import subprocess
import time
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Add project root to path
project_root = Path(__file__).resolve().parent.parent

# Import metrics tracker (optional - graceful fallback if not available)
try:
    from systems.output_flywheel.unified_tools_metrics import track_tool_usage
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    def track_tool_usage(*args, **kwargs):
        """Fallback if metrics not available."""
        pass


class UnifiedAnalyzer:
    """Unified analysis system consolidating all analysis capabilities."""
    
    def __init__(self, project_root: Path = None):
        """Initialize unified analyzer."""
        self.project_root = project_root or Path.cwd()
        self.skip_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env"}
    
    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository metadata and structure."""
        metadata = {"name": repo_path.name, "path": str(repo_path), "exists": repo_path.exists()}
        if not repo_path.exists():
            return metadata
        
        try:
            result = subprocess.run(['git', 'log', '-1', '--format=%ad', '--date=short'],
                                  cwd=repo_path, capture_output=True, text=True)
            metadata["last_commit"] = result.stdout.strip()
            result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'],
                                  cwd=repo_path, capture_output=True, text=True)
            metadata["total_commits"] = int(result.stdout.strip()) if result.stdout.strip() else 0
            py_files = list(repo_path.rglob("*.py"))
            metadata["python_files"] = len(py_files)
            metadata["has_tests"] = (repo_path / "tests").exists() or (repo_path / "test").exists()
            metadata["has_cicd"] = (repo_path / ".github" / "workflows").exists()
            metadata["has_license"] = (repo_path / "LICENSE").exists()
            metadata["has_readme"] = (repo_path / "README.md").exists()
            score = 0
            if metadata["has_tests"]: score += 25
            if metadata["has_cicd"]: score += 25
            if metadata["has_license"]: score += 20
            if metadata["has_readme"]: score += 20
            if metadata["total_commits"] > 10: score += 10
            metadata["quality_score"] = score
        except Exception as e:
            metadata["error"] = str(e)
        return metadata
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Get comprehensive project structure."""
        structure = {}
        total_files = 0
        total_dirs = 0
        file_types = Counter()
        
        for root, dirs, files in os.walk(self.project_root):
            rel_path = os.path.relpath(root, self.project_root)
            if rel_path == ".":
                rel_path = ""
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            file_counts = Counter(Path(f).suffix.lower() for f in files)
            structure[rel_path or "."] = {
                "files": dict(file_counts),
                "file_count": len(files),
                "subdirs": len(dirs),
            }
            total_files += len(files)
            total_dirs += len(dirs)
            file_types.update(file_counts)
        
        return {
            "structure": structure,
            "total_files": total_files,
            "total_dirs": total_dirs,
            "file_types": dict(file_types),
        }
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file."""
        try:
            if file_path.suffix != ".py":
                return {"file_path": str(file_path), "language": file_path.suffix}
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(file_path))
            
            functions, classes = [], {}
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes[node.name] = {"methods": methods, "line_count": len(node.body)}
            
            return {
                "file_path": str(file_path),
                "language": ".py",
                "functions": functions,
                "classes": classes,
                "line_count": len(content.splitlines()),
            }
        except Exception as e:
            return {"file_path": str(file_path), "error": str(e)}
    
    def detect_consolidation_opportunities(self, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect consolidation opportunities between repositories."""
        groups = defaultdict(list)
        
        for repo in repos:
            name = repo.get("name", "")
            normalized = re.sub(r'[^\w\s-]', '', name.lower().replace('-', '_').replace(' ', '_'))
            groups[normalized].append(repo)
        
        consolidation_ops = []
        for norm_name, repo_list in groups.items():
            if len(repo_list) > 1:
                consolidation_ops.append({
                    "group": norm_name,
                    "repos": repo_list,
                    "count": len(repo_list),
                    "similarity": self._calculate_similarity(repo_list),
                })
        
        return {
            "total_groups": len(consolidation_ops),
            "opportunities": consolidation_ops,
        }
    
    def _calculate_similarity(self, repos: List[Dict[str, Any]]) -> float:
        """Calculate average similarity between repos."""
        if len(repos) < 2:
            return 1.0
        similarities = []
        for i in range(len(repos)):
            for j in range(i + 1, len(repos)):
                name1 = repos[i].get("name", "")
                name2 = repos[j].get("name", "")
                sim = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
                similarities.append(sim)
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def analyze_overlaps(self, analysis_dir: Path) -> Dict[str, Any]:
        """Analyze repository overlaps from analysis files."""
        overlaps = []
        if not analysis_dir.exists():
            return {"overlaps": overlaps, "total": 0}
        
        repos_data = {}
        for file_path in analysis_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                repo_name = self._extract_repo_name(content, file_path.name)
                if repo_name:
                    repos_data[repo_name] = {
                        "name": repo_name,
                        "filename": file_path.name,
                        "tech_stack": self._extract_tech_stack(content),
                    }
            except Exception:
                pass
        
        # Find similar repos
        for name1, repo1 in repos_data.items():
            for name2, repo2 in repos_data.items():
                if name1 < name2:
                    similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
                    if similarity > 0.7:
                        overlaps.append({
                            "repo1": repo1,
                            "repo2": repo2,
                            "similarity": similarity,
                        })
        
        return {"overlaps": overlaps, "total": len(overlaps)}
    
    def _extract_repo_name(self, content: str, filename: str) -> Optional[str]:
        """Extract repository name from content."""
        match = re.search(r"^#+\s+(.+?)(?:\s+Analysis|\s+Repo)?$", content, re.MULTILINE)
        return match.group(1).strip() if match else filename.replace("_analysis.md", "").replace(".md", "")
    
    def _extract_tech_stack(self, content: str) -> List[str]:
        """Extract tech stack from content."""
        keywords = ['Python', 'JavaScript', 'TypeScript', 'React', 'Node', 'FastAPI', 'Flask']
        return [k for k in keywords if k.lower() in content.lower()]
    
    def run_full_analysis(self, repos: List[str] = None, analysis_dir: Path = None) -> Dict[str, Any]:
        """Run comprehensive analysis suite."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "analyses": {}
        }
        
        # Project structure
        results["analyses"]["structure"] = self.analyze_project_structure()
        
        # Repository analysis
        if repos:
            repo_metadata = [self.analyze_repository(Path(r)) for r in repos]
            results["analyses"]["repositories"] = repo_metadata
            results["analyses"]["consolidation"] = self.detect_consolidation_opportunities(repo_metadata)
        
        # Overlap analysis
        if analysis_dir:
            results["analyses"]["overlaps"] = self.analyze_overlaps(analysis_dir)
        
        return results
    
    def print_analysis_report(self, results: Dict[str, Any]):
        """Print formatted analysis report."""
        print("\n" + "=" * 70)
        print("📊 UNIFIED ANALYSIS REPORT")
        print("=" * 70)
        
        analyses = results.get("analyses", {})
        
        # Structure
        if "structure" in analyses:
            struct = analyses["structure"]
            print(f"\n📁 Project Structure:")
            print(f"   Total Files: {struct.get('total_files', 0)}")
            print(f"   Total Directories: {struct.get('total_dirs', 0)}")
            print(f"   File Types: {len(struct.get('file_types', {}))}")
        
        # Consolidation
        if "consolidation" in analyses:
            consolid = analyses["consolidation"]
            print(f"\n🔄 Consolidation Opportunities: {consolid.get('total_groups', 0)} groups")
            for opp in consolid.get("opportunities", [])[:5]:
                print(f"   - {opp['group']}: {opp['count']} repos (similarity: {opp['similarity']:.1%})")
        
        # Overlaps
        if "overlaps" in analyses:
            overlaps = analyses["overlaps"]
            print(f"\n🔀 Overlaps Detected: {overlaps.get('total', 0)}")
        
        print(f"\n🕐 Timestamp: {results.get('timestamp', 'unknown')}")
        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified Analyzer - Consolidated analysis for all systems",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--category", "-c",
        choices=["repository", "structure", "file", "consolidation", "overlaps", "all"],
        default="all",
        help="Analysis category (default: all)"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Analyze specific file"
    )
    
    parser.add_argument(
        "--repos",
        type=str,
        help="Comma-separated repository paths"
    )
    
    parser.add_argument(
        "--analysis-dir",
        type=str,
        help="Directory containing analysis files for overlap detection"
    )
    
    parser.add_argument(
        "--project-root",
        type=str,
        help="Project root directory (default: current directory)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    start_time = time.time()
    category_used = args.category if args.category else "unknown"
    
    project_root_path = Path(args.project_root) if args.project_root else Path.cwd()
    analyzer = UnifiedAnalyzer(project_root=project_root_path)
    
    if args.category == "all":
        repos_list = args.repos.split(",") if args.repos else None
        analysis_dir_path = Path(args.analysis_dir) if args.analysis_dir else None
        results = analyzer.run_full_analysis(repos=repos_list, analysis_dir=analysis_dir_path)
    elif args.category == "structure":
        results = {"analysis": analyzer.analyze_project_structure()}
    elif args.category == "file":
        if args.file:
            results = {"analysis": analyzer.analyze_file(Path(args.file))}
        else:
            results = {"analysis": {"error": "File path required for file analysis"}}
    elif args.category == "repository":
        if args.repos:
            repos_list = args.repos.split(",")
            repo_metadata = [analyzer.analyze_repository(Path(r)) for r in repos_list]
            results = {"analysis": {"repositories": repo_metadata}}
        else:
            results = {"analysis": {"error": "Repository paths required"}}
    elif args.category == "consolidation":
        if args.repos:
            repos_list = args.repos.split(",")
            repo_metadata = [analyzer.analyze_repository(Path(r)) for r in repos_list]
            results = {"analysis": analyzer.detect_consolidation_opportunities(repo_metadata)}
        else:
            results = {"analysis": {"error": "Repository paths required"}}
    elif args.category == "overlaps":
        if args.analysis_dir:
            results = {"analysis": analyzer.analyze_overlaps(Path(args.analysis_dir))}
        else:
            results = {"analysis": {"error": "Analysis directory required"}}
    
    # Track metrics
    execution_time = time.time() - start_time
    
    # Determine success (no errors in results)
    success = True
    if "analysis" in results:
        analysis_result = results["analysis"]
        if isinstance(analysis_result, dict) and analysis_result.get("error"):
            success = False
    elif "analyses" in results:
        analyses = results["analyses"]
        if isinstance(analyses, list):
            for a in analyses:
                if isinstance(a, dict) and a.get("error"):
                    success = False
    
    if METRICS_AVAILABLE:
        from systems.output_flywheel.unified_tools_metrics import UnifiedToolsMetricsTracker
        tracker = UnifiedToolsMetricsTracker()
        tracker.track_tool_usage(
            tool_name="unified_analyzer",
            category=category_used,
            success=success,
            execution_time=execution_time
        )
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if "analyses" in results:
            analyzer.print_analysis_report(results)
        elif "analysis" in results:
            print(json.dumps(results["analysis"], indent=2))
        else:
            print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()


