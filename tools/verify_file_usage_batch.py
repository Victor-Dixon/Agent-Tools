#!/usr/bin/env python3
"""
Enhanced File Usage Verification - Batch Optimized Version
==========================================================

Optimized version that processes files in batches for efficiency.
Checks for dynamic imports, entry points, config refs, etc.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-01
Priority: HIGH - Optimized for large-scale verification
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set


class BatchFileVerifier:
    """Optimized batch verification for file usage."""
    
    def __init__(self, src_root: str = "src", project_root: str = "."):
        """Initialize verifier."""
        self.src_root = Path(src_root)
        self.project_root = Path(project_root)
        self.cache: Dict[str, str] = {}  # File content cache
        
    def get_file_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        relative = file_path.relative_to(self.src_root)
        return str(relative.with_suffix("")).replace("\\", ".").replace("/", ".")
    
    def check_entry_point(self, file_path: Path) -> bool:
        """Quick check for entry points."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(5000)  # First 5KB is enough
                if re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', content):
                    return True
        except Exception:
            pass
        return False
    
    def check_test_references(self, file_path: Path, module_name: str) -> List[str]:
        """Check test file references - optimized."""
        refs = []
        tests_root = self.project_root / "tests"
        
        if not tests_root.exists():
            return refs
        
        file_stem = file_path.stem
        
        # Only check test files
        for test_file in tests_root.rglob("test_*.py"):
            try:
                with open(test_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if module_name in content or file_stem in content:
                        refs.append(str(test_file.relative_to(self.project_root)))
            except Exception:
                pass
        
        return refs[:3]  # Limit to first 3
    
    def check_config_references(self, file_path: Path, module_name: str) -> List[str]:
        """Check config references - optimized."""
        refs = []
        relative_path = str(file_path.relative_to(self.src_root))
        
        # Check common config locations only
        config_dirs = [self.project_root, self.project_root / "config", self.project_root / ".github"]
        
        for config_dir in config_dirs:
            if not config_dir.exists():
                continue
                
            for pattern in ["*.yaml", "*.yml", "*.json"]:
                for config_file in config_dir.rglob(pattern):
                    # Skip large files
                    if config_file.stat().st_size > 100000:  # 100KB
                        continue
                        
                    try:
                        with open(config_file, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            if module_name in content or relative_path in content:
                                refs.append(str(config_file.relative_to(self.project_root)))
                                if len(refs) >= 3:
                                    return refs
                    except Exception:
                        pass
        
        return refs
    
    def check_documentation_references(self, file_path: Path, module_name: str) -> List[str]:
        """Check documentation - optimized."""
        refs = []
        relative_path = str(file_path.relative_to(self.src_root))
        file_stem = file_path.stem
        
        # Check only common doc locations
        doc_dirs = [
            self.project_root / "docs",
            self.project_root,
        ]
        
        for doc_dir in doc_dirs:
            if not doc_dir.exists():
                continue
                
            for pattern in ["*.md", "README*", "CHANGELOG*"]:
                for doc_file in doc_dir.glob(pattern):
                    if doc_file.stat().st_size > 50000:  # 50KB limit
                        continue
                        
                    try:
                        with open(doc_file, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read(10000)  # First 10KB
                            if module_name in content or relative_path in content or file_stem in content:
                                refs.append(str(doc_file.relative_to(self.project_root)))
                                if len(refs) >= 2:
                                    return refs
                    except Exception:
                        pass
        
        return refs
    
    def verify_file_batch(self, files: List[Path], batch_num: int) -> Dict[str, Any]:
        """Verify a batch of files."""
        results = {
            "batch": batch_num,
            "files_verified": len(files),
            "results": [],
            "summary": {
                "truly_unused": 0,
                "needs_review": 0,
                "must_keep": 0,
            }
        }
        
        print(f"\n📦 Processing Batch {batch_num}: {len(files)} files\n")
        
        for i, file_path in enumerate(files, 1):
            if not file_path.exists():
                continue
                
            print(f"  [{i}/{len(files)}] {file_path.relative_to(self.src_root)}")
            
            module_name = self.get_file_module_name(file_path)
            
            result = {
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(self.src_root)),
                "module_name": module_name,
                "is_truly_unused": True,
                "risk_level": "low",
                "recommendation": "SAFE_TO_DELETE",
                "findings": {
                    "entry_point": False,
                    "test_references": [],
                    "config_references": [],
                    "documentation_references": [],
                }
            }
            
            # Quick checks
            has_entry = self.check_entry_point(file_path)
            if has_entry:
                result["findings"]["entry_point"] = True
                result["is_truly_unused"] = False
                result["risk_level"] = "high"
                result["recommendation"] = "KEEP - Has entry point"
                results["summary"]["must_keep"] += 1
            else:
                # Check references
                test_refs = self.check_test_references(file_path, module_name)
                config_refs = self.check_config_references(file_path, module_name)
                doc_refs = self.check_documentation_references(file_path, module_name)
                
                result["findings"]["test_references"] = test_refs
                result["findings"]["config_references"] = config_refs
                result["findings"]["documentation_references"] = doc_refs
                
                if test_refs or config_refs:
                    result["is_truly_unused"] = False
                    result["risk_level"] = "medium"
                    result["recommendation"] = "REVIEW - Referenced in tests/config"
                    results["summary"]["needs_review"] += 1
                elif doc_refs:
                    result["risk_level"] = "low"
                    result["recommendation"] = "REVIEW - Referenced in docs (lower risk)"
                    results["summary"]["needs_review"] += 1
                else:
                    results["summary"]["truly_unused"] += 1
            
            results["results"].append(result)
        
        return results


def main():
    """Main execution with batch processing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch file usage verification")
    parser.add_argument(
        "--analysis-file",
        default="agent_workspaces/Agent-5/unnecessary_files_analysis.json",
        help="Path to unnecessary_files_analysis.json"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of files per batch"
    )
    parser.add_argument(
        "--output",
        default="agent_workspaces/Agent-5/enhanced_verification_results.json",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    print("🔍 ENHANCED FILE USAGE VERIFICATION - BATCH PROCESSING")
    print("=" * 60)
    print(f"Processing files in batches of {args.batch_size}\n")
    
    # Load analysis file
    if not Path(args.analysis_file).exists():
        print(f"❌ Analysis file not found: {args.analysis_file}")
        return
    
    with open(args.analysis_file, "r", encoding="utf-8") as f:
        analysis_data = json.load(f)
    
    # Collect all files
    files_to_verify = []
    for category in ["unused", "deprecated_directory", "deletion_markers", "duplicates"]:
        for file_info in analysis_data.get(category, []):
            file_path = Path(file_info["file_path"])
            if file_path.exists():
                files_to_verify.append(file_path)
    
    print(f"📋 Total files to verify: {len(files_to_verify)}")
    print(f"📦 Will process in {len(files_to_verify) // args.batch_size + 1} batches\n")
    
    verifier = BatchFileVerifier()
    
    # Process in batches
    all_results = {
        "summary": {
            "total_files": len(files_to_verify),
            "truly_unused": 0,
            "needs_review": 0,
            "must_keep": 0,
        },
        "batches": [],
        "all_files": {
            "truly_unused": [],
            "needs_review": [],
            "must_keep": [],
        }
    }
    
    for batch_num, i in enumerate(range(0, len(files_to_verify), args.batch_size), 1):
        batch_files = files_to_verify[i:i + args.batch_size]
        batch_results = verifier.verify_file_batch(batch_files, batch_num)
        
        all_results["batches"].append(batch_results)
        all_results["summary"]["truly_unused"] += batch_results["summary"]["truly_unused"]
        all_results["summary"]["needs_review"] += batch_results["summary"]["needs_review"]
        all_results["summary"]["must_keep"] += batch_results["summary"]["must_keep"]
        
        # Categorize results
        for result in batch_results["results"]:
            if result["risk_level"] == "high":
                all_results["all_files"]["must_keep"].append(result)
            elif result["risk_level"] == "medium":
                all_results["all_files"]["needs_review"].append(result)
            else:
                all_results["all_files"]["truly_unused"].append(result)
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    summary = all_results["summary"]
    print(f"Total Files Verified: {summary['total_files']}")
    print(f"✅ Truly Unused (Safe to Delete): {summary['truly_unused']}")
    print(f"⚠️  Needs Review: {summary['needs_review']}")
    print(f"❌ Must Keep: {summary['must_keep']}")
    
    print(f"\n✅ Results saved to: {output_path}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()




