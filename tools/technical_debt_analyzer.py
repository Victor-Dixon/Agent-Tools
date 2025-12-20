#!/usr/bin/env python3
"""
Technical Debt Analyzer - Consolidated Analysis Tool
====================================================

Consolidates technical debt marker analysis, duplicate file detection,
and consolidation recommendations into a single unified tool.

Replaces:
- analyze_technical_debt_markers.py
- comprehensive_duplicate_analyzer.py (duplicate aspects)
- analyze_duplicate_code_consolidation.py (consolidation aspects)
- unified_analyzer.py (technical debt aspects)

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
SSOT Domain: analytics

FIXED: 2025-12-18 by Agent-4
- Added file existence verification before duplicate detection
- Added empty file (0 bytes) filtering
- Added SSOT validation (verify exists and contains content)
- Added duplicate file existence verification in recommendations
"""

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Priority levels
PRIORITY_P0 = "P0 - Critical"
PRIORITY_P1 = "P1 - High"
PRIORITY_P2 = "P2 - Medium"
PRIORITY_P3 = "P3 - Low"

# Marker patterns
MARKER_PATTERNS = {
    "BUG": {"pattern": re.compile(r"BUG[:\s]+(.+)", re.IGNORECASE), "priority": PRIORITY_P0},
    "FIXME": {"pattern": re.compile(r"FIXME[:\s]+(.+)", re.IGNORECASE), "priority": PRIORITY_P0},
    "TODO": {"pattern": re.compile(r"TODO[:\s]+(.+)", re.IGNORECASE), "priority": PRIORITY_P1},
    "DEPRECATED": {"pattern": re.compile(r"DEPRECATED[:\s]+(.+)", re.IGNORECASE), "priority": PRIORITY_P2},
    "REFACTOR": {"pattern": re.compile(r"REFACTOR[:\s]+(.+)", re.IGNORECASE), "priority": PRIORITY_P3},
    "HACK": {"pattern": re.compile(r"HACK[:\s]+(.+)", re.IGNORECASE), "priority": PRIORITY_P2},
    "XXX": {"pattern": re.compile(r"XXX[:\s]+(.+)", re.IGNORECASE), "priority": PRIORITY_P2},
    "NOTE": {"pattern": re.compile(r"NOTE[:\s]+(.+)", re.IGNORECASE), "priority": PRIORITY_P3},
}


class TechnicalDebtAnalyzer:
    """Unified technical debt analyzer with duplicate detection."""

    def __init__(self, project_root: str = "."):
        """Initialize analyzer."""
        self.project_root = Path(project_root)
        self.markers: List[Dict[str, Any]] = []
        self.file_extensions = [".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c"]
        self.excluded_patterns = {
            ".git", "__pycache__", "node_modules", ".venv", "venv",
            "htmlcov", ".pytest_cache", "dist", "build", ".tox"
        }

    def find_source_files(self) -> List[Path]:
        """Find all source files to analyze."""
        source_files = []
        for ext in self.file_extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                if any(skip in str(file_path) for skip in self.excluded_patterns):
                    continue
                source_files.append(file_path)
        return sorted(source_files)

    def analyze_markers(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a file for technical debt markers."""
        markers_found = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for line_num, line in enumerate(content.split("\n"), 1):
                for marker_type, marker_info in MARKER_PATTERNS.items():
                    match = marker_info["pattern"].search(line)
                    if match:
                        markers_found.append({
                            "file_path": str(file_path),
                            "relative_path": str(file_path.relative_to(self.project_root)),
                            "line_number": line_num,
                            "marker_type": marker_type,
                            "priority": marker_info["priority"],
                            "marker_text": match.group(1).strip()[:200],
                            "full_line": line.strip()[:200],
                        })
        except Exception:
            pass
        return markers_found

    def calculate_hash(self, file_path: Path) -> Optional[str]:
        """Calculate SHA256 hash of file."""
        try:
            # Verify file exists and is not empty
            if not file_path.exists():
                return None
            file_size = file_path.stat().st_size
            if file_size == 0:
                return None  # Skip empty files
            return hashlib.sha256(file_path.read_bytes()).hexdigest()
        except Exception:
            return None

    def detect_duplicates(self) -> Tuple[Dict[str, List[Path]], Dict[str, List[Path]]]:
        """Detect duplicate files by hash and name."""
        files_by_hash: Dict[str, List[Path]] = defaultdict(list)
        files_by_name: Dict[str, List[Path]] = defaultdict(list)
        
        source_files = self.find_source_files()
        for file_path in source_files:
            # Verify file exists before processing
            if not file_path.exists():
                continue
            # Skip empty files (0 bytes)
            try:
                if file_path.stat().st_size == 0:
                    continue
            except Exception:
                continue
            
            file_hash = self.calculate_hash(file_path)
            if file_hash:
                files_by_hash[file_hash].append(file_path)
            if file_path.suffix in ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md']:
                files_by_name[file_path.name].append(file_path)
        
        exact_duplicates = {h: paths for h, paths in files_by_hash.items() if len(paths) > 1}
        name_duplicates = {n: paths for n, paths in files_by_name.items() if len(paths) > 1}
        
        return exact_duplicates, name_duplicates

    def determine_ssot(self, paths: List[Path]) -> Optional[Path]:
        """Determine single source of truth file."""
        # Filter to only existing, non-empty files
        valid_paths = []
        for path in paths:
            if not path.exists():
                continue
            try:
                if path.stat().st_size == 0:
                    continue  # Skip empty files
            except Exception:
                continue
            valid_paths.append(path)
        
        if not valid_paths:
            return None  # No valid SSOT found
        
        # Prefer src/core/ or src/services/ paths
        for path in valid_paths:
            rel = path.relative_to(self.project_root)
            if str(rel).startswith('src/core/') or str(rel).startswith('src/services/'):
                return path
        return min(valid_paths, key=lambda p: len(p.relative_to(self.project_root).parts))

    def generate_consolidation_recommendations(
        self, exact_duplicates: Dict[str, List[Path]]
    ) -> List[Dict[str, Any]]:
        """Generate consolidation recommendations for duplicates."""
        recommendations = []
        for hash_val, paths in exact_duplicates.items():
            # Verify all paths exist before processing
            existing_paths = [p for p in paths if p.exists()]
            if len(existing_paths) < 2:
                continue  # Skip groups with less than 2 existing files
            
            ssot = self.determine_ssot(existing_paths)
            if ssot is None:
                continue  # Skip if no valid SSOT found
            
            # Verify SSOT is not empty
            try:
                if ssot.stat().st_size == 0:
                    continue  # Skip empty SSOT files
            except Exception:
                continue
            
            duplicates = [p for p in existing_paths if p != ssot]
            if not duplicates:
                continue  # Skip if no duplicates after filtering
            
            # Verify all duplicate files exist
            valid_duplicates = [p for p in duplicates if p.exists()]
            if not valid_duplicates:
                continue
            
            recommendations.append({
                "ssot": str(ssot.relative_to(self.project_root)),
                "duplicates": [str(p.relative_to(self.project_root)) for p in valid_duplicates],
                "count": len(existing_paths),
                "action": "DELETE",
                "risk": "LOW"
            })
        return recommendations

    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze entire codebase for technical debt."""
        print("🔍 Analyzing codebase for technical debt...")
        
        source_files = self.find_source_files()
        print(f"📁 Found {len(source_files)} source files\n")
        
        # Analyze markers
        markers_by_type = defaultdict(int)
        markers_by_priority = defaultdict(int)
        
        for i, file_path in enumerate(source_files, 1):
            if i % 100 == 0:
                print(f"  Analyzing file {i}/{len(source_files)}...")
            file_markers = self.analyze_markers(file_path)
            self.markers.extend(file_markers)
            for marker in file_markers:
                markers_by_type[marker["marker_type"]] += 1
                markers_by_priority[marker["priority"]] += 1
        
        # Detect duplicates
        print("\n🔍 Detecting duplicate files...")
        exact_duplicates, name_duplicates = self.detect_duplicates()
        consolidation_recs = self.generate_consolidation_recommendations(exact_duplicates)
        
        print(f"\n✅ Analysis complete!")
        print(f"   Markers: {len(self.markers)}")
        print(f"   Exact duplicates: {len(exact_duplicates)} groups")
        print(f"   Same-name files: {len(name_duplicates)} groups\n")
        
        return {
            "summary": {
                "total_markers": len(self.markers),
                "files_analyzed": len(source_files),
                "exact_duplicate_groups": len(exact_duplicates),
                "same_name_groups": len(name_duplicates),
                "consolidation_opportunities": len(consolidation_recs),
                "analysis_date": datetime.now().isoformat(),
            },
            "markers": {
                "by_type": dict(markers_by_type),
                "by_priority": dict(markers_by_priority),
                "all": self.markers,
            },
            "duplicates": {
                "exact": {h: [str(p.relative_to(self.project_root)) for p in paths]
                         for h, paths in exact_duplicates.items()},
                "same_name": {n: [str(p.relative_to(self.project_root)) for p in paths]
                            for n, paths in name_duplicates.items()},
            },
            "consolidation_recommendations": consolidation_recs,
        }

    def save_results(self, results: Dict[str, Any], output_path: Path):
        """Save analysis results to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to: {output_path}")

    def generate_report(self, results: Dict[str, Any], report_path: Path):
        """Generate markdown report."""
        report_path.parent.mkdir(parents=True, exist_ok=True)
        summary = results["summary"]
        markers = results["markers"]
        
        report = f"""# Technical Debt Analysis Report

**Generated**: {summary['analysis_date']}  
**Total Markers**: {summary['total_markers']}  
**Files Analyzed**: {summary['files_analyzed']}  
**Duplicate Groups**: {summary['exact_duplicate_groups']}  
**Consolidation Opportunities**: {summary['consolidation_opportunities']}

---

## 📊 Markers by Type

"""
        for marker_type, count in sorted(markers["by_type"].items(), key=lambda x: x[1], reverse=True):
            report += f"- **{marker_type}**: {count}\n"
        
        report += "\n---\n\n## 📊 Markers by Priority\n\n"
        for priority in [PRIORITY_P0, PRIORITY_P1, PRIORITY_P2, PRIORITY_P3]:
            if priority in markers["by_priority"]:
                report += f"- **{priority}**: {markers['by_priority'][priority]}\n"
        
        if results["consolidation_recommendations"]:
            report += "\n---\n\n## 🔄 Consolidation Recommendations\n\n"
            report += f"**Total Opportunities**: {len(results['consolidation_recommendations'])}\n\n"
            for i, rec in enumerate(results["consolidation_recommendations"][:10], 1):
                report += f"### {i}. {Path(rec['ssot']).name}\n"
                report += f"- **Keep**: `{rec['ssot']}`\n"
                report += f"- **Delete**: {len(rec['duplicates'])} files\n"
                report += f"- **Risk**: {rec['risk']}\n\n"
        
        report += "\n---\n\n🐝 **WE. ARE. SWARM. ⚡🔥**\n"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ Report saved to: {report_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Technical Debt Analyzer")
    parser.add_argument("--output", type=Path,
                       default=Path("agent_workspaces/Agent-5/technical_debt_analysis.json"),
                       help="Output JSON file path")
    parser.add_argument("--report", type=Path,
                       default=Path("agent_workspaces/Agent-5/TECHNICAL_DEBT_REPORT.md"),
                       help="Output markdown report path")
    parser.add_argument("--project-root", type=str, default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    print("🔍 TECHNICAL DEBT ANALYZER")
    print("=" * 60)
    print()
    
    analyzer = TechnicalDebtAnalyzer(project_root=args.project_root)
    results = analyzer.analyze_codebase()
    analyzer.save_results(results, args.output)
    analyzer.generate_report(results, args.report)
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Markers: {results['summary']['total_markers']}")
    print(f"Duplicate Groups: {results['summary']['exact_duplicate_groups']}")
    print(f"Consolidation Opportunities: {results['summary']['consolidation_opportunities']}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()


