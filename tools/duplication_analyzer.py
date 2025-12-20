#!/usr/bin/env python3
"""
Duplication Analyzer - Consolidated Duplicate Detection Tool
=============================================================

Consolidates duplicate file detection, hash-based duplicate detection,
and consolidation analysis into a single unified tool.

Replaces:
- comprehensive_duplicate_analyzer.py (if exists)
- duplication_analyzer.py (if exists)
- duplication_analysis.py (if exists)
- analyze_duplicate_code_consolidation.py (consolidation aspects)

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-07
V2 Compliant: Yes (<300 lines)
SSOT Domain: analytics

FIXED: 2025-12-18 by Agent-3
- Added file existence verification before duplicate detection
- Added empty file (0 bytes) filtering
- Added SSOT validation (verify exists and contains content)
- Added duplicate file existence verification in recommendations

<!-- SSOT Domain: analytics -->
"""

import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
import sys
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class DuplicationAnalyzer:
    """Unified duplication analyzer with hash-based and name-based detection."""

    def __init__(self, project_root: str = "."):
        """Initialize analyzer."""
        self.project_root = Path(project_root)
        self.file_extensions = [".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".md"]
        self.excluded_patterns = {
            ".git", "__pycache__", "node_modules", ".venv", "venv",
            "htmlcov", ".pytest_cache", "dist", "build", ".tox", ".coverage"
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

    def detect_duplicates_by_hash(self) -> Dict[str, List[Path]]:
        """Detect exact duplicate files by hash."""
        files_by_hash: Dict[str, List[Path]] = defaultdict(list)
        
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
        
        # Return only groups with duplicates
        exact_duplicates = {h: paths for h, paths in files_by_hash.items() if len(paths) > 1}
        return exact_duplicates

    def detect_duplicates_by_name(self) -> Dict[str, List[Path]]:
        """Detect files with same name in different locations."""
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
            files_by_name[file_path.name].append(file_path)
        
        # Return only groups with duplicates
        name_duplicates = {n: paths for n, paths in files_by_name.items() if len(paths) > 1}
        return name_duplicates

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
        # Prefer shorter paths (closer to root)
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
                "risk": "LOW" if len(existing_paths) == 2 else "MEDIUM"
            })
        return recommendations

    def analyze_code_consolidation(self) -> Dict[str, Any]:
        """Analyze code consolidation opportunities."""
        exact_duplicates = self.detect_duplicates_by_hash()
        name_duplicates = self.detect_duplicates_by_name()
        consolidation_recs = self.generate_consolidation_recommendations(exact_duplicates)
        
        return {
            "exact_duplicates": {
                "count": len(exact_duplicates),
                "groups": {h: [str(p.relative_to(self.project_root)) for p in paths]
                          for h, paths in exact_duplicates.items()}
            },
            "name_duplicates": {
                "count": len(name_duplicates),
                "groups": {n: [str(p.relative_to(self.project_root)) for p in paths]
                          for n, paths in name_duplicates.items()}
            },
            "consolidation_recommendations": consolidation_recs,
        }

    def analyze(self) -> Dict[str, Any]:
        """Run comprehensive duplication analysis."""
        print("🔍 DUPLICATION ANALYZER")
        print("=" * 60)
        print()
        
        print("🔍 Detecting duplicate files...")
        exact_duplicates = self.detect_duplicates_by_hash()
        name_duplicates = self.detect_duplicates_by_name()
        consolidation_recs = self.generate_consolidation_recommendations(exact_duplicates)
        
        print(f"\n✅ Analysis complete!")
        print(f"   Exact duplicates: {len(exact_duplicates)} groups")
        print(f"   Same-name files: {len(name_duplicates)} groups")
        print(f"   Consolidation opportunities: {len(consolidation_recs)}\n")
        
        return {
            "summary": {
                "exact_duplicate_groups": len(exact_duplicates),
                "same_name_groups": len(name_duplicates),
                "consolidation_opportunities": len(consolidation_recs),
                "analysis_date": datetime.now().isoformat(),
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
        
        report = f"""# Duplication Analysis Report

**Generated**: {summary['analysis_date']}  
**Exact Duplicate Groups**: {summary['exact_duplicate_groups']}  
**Same-Name Groups**: {summary['same_name_groups']}  
**Consolidation Opportunities**: {summary['consolidation_opportunities']}

---

## 🔄 Consolidation Recommendations

"""
        if results["consolidation_recommendations"]:
            for i, rec in enumerate(results["consolidation_recommendations"][:20], 1):
                report += f"### {i}. {Path(rec['ssot']).name}\n"
                report += f"- **Keep**: `{rec['ssot']}`\n"
                report += f"- **Delete**: {len(rec['duplicates'])} files\n"
                report += f"- **Risk**: {rec['risk']}\n\n"
        else:
            report += "No consolidation opportunities found.\n"
        
        report += "\n---\n\n🐝 **WE. ARE. SWARM. ⚡🔥**\n"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ Report saved to: {report_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Duplication Analyzer")
    parser.add_argument("--output", type=Path,
                       default=Path("agent_workspaces/Agent-5/duplication_analysis.json"),
                       help="Output JSON file path")
    parser.add_argument("--report", type=Path,
                       default=Path("agent_workspaces/Agent-5/DUPLICATION_REPORT.md"),
                       help="Output markdown report path")
    parser.add_argument("--project-root", type=str, default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    print("🔍 DUPLICATION ANALYZER")
    print("=" * 60)
    print()
    
    analyzer = DuplicationAnalyzer(project_root=args.project_root)
    results = analyzer.analyze()
    analyzer.save_results(results, args.output)
    analyzer.generate_report(results, args.report)
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Exact Duplicate Groups: {results['summary']['exact_duplicate_groups']}")
    print(f"Same-Name Groups: {results['summary']['same_name_groups']}")
    print(f"Consolidation Opportunities: {results['summary']['consolidation_opportunities']}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

