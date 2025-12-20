#!/usr/bin/env python3
"""
Repository Analyzer - Consolidated Repository & Project Analysis Tool
======================================================================

Consolidates repository batch analysis, consolidation detection, overlap analysis,
architecture analysis, and project analysis into a single unified tool.

Replaces:
- repo_batch_analyzer.py
- repo_consolidation_analyzer.py
- repo_overlap_analyzer.py
- enhanced_repo_consolidation_analyzer.py
- architecture_repo_analyzer.py
- project_analyzer_core.py
- project_analyzer_file.py
- project_analyzer_reports.py

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
SSOT Domain: analytics

<!-- SSOT Domain: analytics -->
"""

import ast
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# SSOT Domain: analytics


class RepositoryAnalyzer:
    """Unified repository and project analyzer."""

    def __init__(self, project_root: Path = None):
        """Initialize analyzer."""
        self.project_root = project_root or Path.cwd()
        self.skip_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env"}

    def analyze_repo_metadata(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository metadata."""
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

    def get_project_structure(self) -> Dict[str, Any]:
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

    def generate_report(self, analysis: Dict[str, Any], output_path: Path):
        """Generate analysis report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        s = analysis.get('structure', {})
        c = analysis.get('consolidation', {})
        report = f"# Repository Analysis Report\n\n**Generated**: {datetime.now().isoformat()}\n**Project Root**: {self.project_root}\n\n---\n\n## 📊 Project Structure\n\n- **Total Files**: {s.get('total_files', 0)}\n- **Total Directories**: {s.get('total_dirs', 0)}\n- **File Types**: {len(s.get('file_types', {}))}\n\n---\n\n## 🔄 Consolidation Opportunities\n\n**Total Groups**: {c.get('total_groups', 0)}\n\n"
        for i, opp in enumerate(c.get('opportunities', [])[:10], 1):
            report += f"### {i}. {opp['group']}\n- **Repos**: {opp['count']}\n- **Similarity**: {opp['similarity']:.1%}\n\n"
        report += "\n---\n\n🐝 **WE. ARE. SWARM. ⚡🔥**\n"
        output_path.write_text(report, encoding="utf-8")
        print(f"✅ Report saved to: {output_path}")

    def analyze(self, repos: List[str] = None, analysis_dir: Path = None) -> Dict[str, Any]:
        """Run comprehensive repository analysis."""
        print("🔍 REPOSITORY ANALYZER")
        print("=" * 60)
        
        structure = self.get_project_structure()
        print(f"✅ Project structure analyzed: {structure['total_files']} files")
        
        consolidation = {"total_groups": 0, "opportunities": []}
        if repos:
            repo_metadata = [self.analyze_repo_metadata(Path(r)) for r in repos]
            consolidation = self.detect_consolidation_opportunities(repo_metadata)
            print(f"✅ Consolidation analysis: {consolidation['total_groups']} groups")
        
        overlaps = {"overlaps": [], "total": 0}
        if analysis_dir:
            overlaps = self.analyze_overlaps(analysis_dir)
            print(f"✅ Overlap analysis: {overlaps['total']} overlaps")
        
        return {
            "summary": {
                "total_files": structure["total_files"],
                "total_dirs": structure["total_dirs"],
                "consolidation_groups": consolidation["total_groups"],
                "overlaps": overlaps["total"],
                "analysis_date": datetime.now().isoformat(),
            },
            "structure": structure,
            "consolidation": consolidation,
            "overlaps": overlaps,
        }

    def save_results(self, results: Dict[str, Any], output_path: Path):
        """Save analysis results."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to: {output_path}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Repository Analyzer")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root")
    parser.add_argument("--repos", type=str, help="Comma-separated repo names")
    parser.add_argument("--analysis-dir", type=Path, help="Repository analysis directory")
    parser.add_argument("--output", type=Path, default=Path("agent_workspaces/Agent-5/repository_analysis.json"), help="Output JSON")
    parser.add_argument("--report", type=Path, default=Path("agent_workspaces/Agent-5/repository_analysis_report.md"), help="Output report")
    args = parser.parse_args()
    analyzer = RepositoryAnalyzer(project_root=args.project_root)
    repos_list = args.repos.split(",") if args.repos else None
    results = analyzer.analyze(repos=repos_list, analysis_dir=args.analysis_dir)
    analyzer.save_results(results, args.output)
    analyzer.generate_report(results, args.report)
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

