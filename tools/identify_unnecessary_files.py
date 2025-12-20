#!/usr/bin/env python3
"""
Identify Unnecessary Files for Deletion
========================================

Identifies files that should be deleted instead of tested:
- Unused files (not imported anywhere)
- Dead code files
- Duplicate files
- Files in deprecated/temp directories
- Files marked for deletion

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-01
Priority: HIGH - Saves time by not testing files that should be deleted
"""

import ast
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set


class UnnecessaryFileIdentifier:
    """Identify files that should be deleted, not tested."""

    def __init__(self, src_root: str = "src", exclude_patterns: List[str] = None):
        """Initialize identifier."""
        self.src_root = Path(src_root)
        self.exclude_patterns = exclude_patterns or [
            "__pycache__",
            "__init__.py",
            ".pyc",
            "test_",
            "conftest.py"
        ]
        self.imports_map: Dict[str, Set[str]] = defaultdict(set)
        self.file_imports: Dict[str, Set[str]] = {}
        self.unused_files: List[Dict[str, Any]] = []
        
    def find_all_source_files(self) -> List[Path]:
        """Find all Python source files."""
        source_files = []
        for path in self.src_root.rglob("*.py"):
            if any(pattern in str(path) for pattern in self.exclude_patterns):
                continue
            source_files.append(path)
        return sorted(source_files)
    
    def get_file_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        relative = file_path.relative_to(self.src_root)
        return str(relative.with_suffix("")).replace("\\", ".").replace("/", ".")
    
    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract all imports from a file."""
        imports = set()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, str(file_path))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split(".")[0])
        except Exception as e:
            # File might be empty or have syntax errors
            pass
        
        return imports
    
    def build_import_map(self, source_files: List[Path]):
        """Build map of what each file imports."""
        for file_path in source_files:
            module_name = self.get_file_module_name(file_path)
            imports = self.extract_imports(file_path)
            self.file_imports[str(file_path)] = imports
            for imp in imports:
                self.imports_map[imp].add(str(file_path))
    
    def check_if_file_is_imported(self, file_path: Path) -> bool:
        """Check if a file is imported by any other file."""
        module_name = self.get_file_module_name(file_path)
        module_parts = module_name.split(".")
        
        # Check various import patterns
        patterns_to_check = [
            module_name,
            module_parts[-1],  # Just the filename
            ".".join(module_parts[-2:]),  # Last two parts
        ]
        
        # Also check if any file imports something from this module's parent
        for pattern in patterns_to_check:
            if pattern in self.imports_map:
                # Check if any file actually imports from this specific path
                for importing_file in self.imports_map[pattern]:
                    if importing_file != str(file_path):
                        return True
        
        return False
    
    def is_in_deprecated_directory(self, file_path: Path) -> bool:
        """Check if file is in deprecated/temp directory."""
        path_str = str(file_path).lower()
        deprecated_patterns = [
            "deprecated",
            "temp",
            "old",
            "legacy",
            "archive",
            "unused",
            "backup",
            ".bak",
            "tmp"
        ]
        return any(pattern in path_str for pattern in deprecated_patterns)
    
    def has_deletion_markers(self, file_path: Path) -> bool:
        """Check if file has markers indicating it should be deleted."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                deletion_markers = [
                    "todo: delete",
                    "delete this",
                    "deprecated",
                    "unused",
                    "dead code",
                    "to be removed",
                    "remove this",
                    "not used"
                ]
                return any(marker in content for marker in deletion_markers)
        except Exception:
            return False
    
    def is_duplicate_file(self, file_path: Path, all_files: List[Path]) -> Dict[str, Any]:
        """Check if file appears to be a duplicate."""
        file_name = file_path.name
        duplicate_candidates = []
        
        for other_file in all_files:
            if other_file == file_path:
                continue
            if other_file.name == file_name:
                duplicate_candidates.append(str(other_file))
        
        if len(duplicate_candidates) > 0:
            return {
                "is_duplicate": True,
                "duplicate_of": duplicate_candidates,
                "count": len(duplicate_candidates) + 1
            }
        
        return {"is_duplicate": False}
    
    def identify_unnecessary_files(self) -> Dict[str, Any]:
        """Identify all unnecessary files."""
        source_files = self.find_all_source_files()
        print(f"🔍 Analyzing {len(source_files)} source files...")
        
        # Build import map
        print("📊 Building import dependency map...")
        self.build_import_map(source_files)
        
        unnecessary_files = {
            "unused": [],  # Not imported anywhere
            "deprecated_directory": [],  # In deprecated/temp directories
            "deletion_markers": [],  # Has deletion markers
            "duplicates": [],  # Duplicate files
            "summary": {}
        }
        
        for file_path in source_files:
            file_info = {
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(self.src_root)),
                "module_name": self.get_file_module_name(file_path),
                "reasons": []
            }
            
            is_unnecessary = False
            
            # Check if unused
            if not self.check_if_file_is_imported(file_path):
                file_info["reasons"].append("Not imported by any other file")
                unnecessary_files["unused"].append(file_info)
                is_unnecessary = True
            
            # Check if in deprecated directory
            if self.is_in_deprecated_directory(file_path):
                if not is_unnecessary:
                    unnecessary_files["deprecated_directory"].append(file_info)
                    file_info["reasons"].append("In deprecated/temp directory")
                    is_unnecessary = True
            
            # Check for deletion markers
            if self.has_deletion_markers(file_path):
                if not is_unnecessary:
                    unnecessary_files["deletion_markers"].append(file_info)
                    file_info["reasons"].append("Contains deletion markers")
                    is_unnecessary = True
            
            # Check for duplicates
            duplicate_info = self.is_duplicate_file(file_path, source_files)
            if duplicate_info["is_duplicate"]:
                if not is_unnecessary:
                    unnecessary_files["duplicates"].append({
                        **file_info,
                        **duplicate_info
                    })
                    file_info["reasons"].append(f"Duplicate of {len(duplicate_info['duplicate_of'])} other files")
                    is_unnecessary = True
        
        # Generate summary
        total_unnecessary = (
            len(unnecessary_files["unused"]) +
            len(unnecessary_files["deprecated_directory"]) +
            len(unnecessary_files["deletion_markers"]) +
            len(unnecessary_files["duplicates"])
        )
        
        unnecessary_files["summary"] = {
            "total_source_files": len(source_files),
            "unnecessary_files_count": total_unnecessary,
            "unused_files": len(unnecessary_files["unused"]),
            "deprecated_directory": len(unnecessary_files["deprecated_directory"]),
            "deletion_markers": len(unnecessary_files["deletion_markers"]),
            "duplicates": len(unnecessary_files["duplicates"]),
            "files_needing_tests": len(source_files) - total_unnecessary,
            "time_saved": f"~{total_unnecessary * 30} minutes (assuming 30 min per test file)"
        }
        
        return unnecessary_files


def main():
    """Main execution."""
    print("🚨 IDENTIFYING UNNECESSARY FILES FOR DELETION")
    print("=" * 60)
    print("Goal: Find files that should be deleted, not tested\n")
    
    identifier = UnnecessaryFileIdentifier()
    results = identifier.identify_unnecessary_files()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    summary = results["summary"]
    print(f"Total Source Files: {summary['total_source_files']}")
    print(f"Unnecessary Files: {summary['unnecessary_files_count']}")
    print(f"  - Unused (not imported): {summary['unused_files']}")
    print(f"  - In deprecated directories: {summary['deprecated_directory']}")
    print(f"  - Has deletion markers: {summary['deletion_markers']}")
    print(f"  - Duplicates: {summary['duplicates']}")
    print(f"\n✅ Files Actually Needing Tests: {summary['files_needing_tests']}")
    print(f"⏱️  Time Saved: {summary['time_saved']}")
    
    # Save results
    output_dir = Path("agent_workspaces/Agent-5")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "unnecessary_files_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    # Print top 20 unused files
    if results["unused"]:
        print("\n" + "=" * 60)
        print("🔴 TOP 20 UNUSED FILES (Consider deleting)")
        print("=" * 60)
        for i, file_info in enumerate(results["unused"][:20], 1):
            print(f"{i}. {file_info['relative_path']}")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()




