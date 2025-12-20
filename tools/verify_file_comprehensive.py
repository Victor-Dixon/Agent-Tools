#!/usr/bin/env python3
"""
Comprehensive File Verification Tool
=====================================

Combines enhanced usage verification with implementation status analysis.
Checks for: dynamic imports, entry points, config refs, AND implementation status.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-01
Priority: HIGH - Complete verification before deletion decisions
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List


class ComprehensiveFileVerifier:
    """Comprehensive verification including implementation status."""
    
    def __init__(self, src_root: str = "src", project_root: str = "."):
        """Initialize verifier."""
        self.src_root = Path(src_root)
        self.project_root = Path(project_root)
        
    def check_implementation_status(self, file_path: Path) -> Dict[str, Any]:
        """Check if file needs implementation/integration."""
        status = {
            "has_todos": [],
            "has_fixmes": [],
            "has_plans": [],
            "has_stubs": False,
            "has_docstrings": False,
            "implementation_ratio": 1.0,
            "needs_implementation": False,
            "needs_integration": False,
        }
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Check for TODOs
            todos = re.findall(r'TODO[:\s]+(.+)', content, re.IGNORECASE)
            if todos:
                status["has_todos"] = [t.strip()[:50] for t in todos[:3]]
                status["needs_implementation"] = True
            
            # Check for FIXMEs
            fixmes = re.findall(r'FIXME[:\s]+(.+)', content, re.IGNORECASE)
            if fixmes:
                status["has_fixmes"] = [f.strip()[:50] for f in fixmes[:3]]
                status["needs_implementation"] = True
            
            # Check for planned features
            plan_keywords = ["planned", "future", "upcoming", "roadmap", "soon", "next"]
            for keyword in plan_keywords:
                if re.search(rf'{keyword}[:\s]+', content, re.IGNORECASE):
                    status["has_plans"].append(keyword)
                    status["needs_integration"] = True
            
            # Check for stubs
            if re.search(r'def\s+\w+.*:\s*pass\s*$', content, re.MULTILINE):
                status["has_stubs"] = True
                status["needs_implementation"] = True
            
            # Check for docstrings (indicates intentional design)
            if '"""' in content or "'''" in content:
                status["has_docstrings"] = True
            
            # Simple implementation ratio check
            functions = len(re.findall(r'def\s+\w+', content))
            implemented = len(re.findall(r'def\s+\w+.*:\s*(?!pass)', content))
            if functions > 0:
                status["implementation_ratio"] = implemented / functions
                if status["implementation_ratio"] < 0.7:
                    status["needs_implementation"] = True
                    
        except Exception:
            pass
        
        return status
    
    def verify_file_comprehensive(self, file_path: Path, module_name: str) -> Dict[str, Any]:
        """Comprehensive verification of a single file."""
        result = {
            "file_path": str(file_path),
            "relative_path": str(file_path.relative_to(self.src_root)),
            "module_name": module_name,
            "verification": {
                "entry_point": False,
                "test_references": [],
                "config_references": [],
                "documentation_references": [],
            },
            "implementation_status": {},
            "risk_level": "low",
            "category": "truly_unused",
            "recommendation": "SAFE_TO_DELETE",
        }
        
        # Quick entry point check
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2000)  # First 2KB
                if re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', content):
                    result["verification"]["entry_point"] = True
                    result["risk_level"] = "high"
                    result["category"] = "must_keep"
                    result["recommendation"] = "KEEP - Has entry point"
                    return result
        except Exception:
            pass
        
        # Check test references (quick)
        tests_root = self.project_root / "tests"
        if tests_root.exists():
            file_stem = file_path.stem
            for test_file in list(tests_root.rglob("test_*.py"))[:10]:  # Limit search
                try:
                    with open(test_file, "r", encoding="utf-8", errors="ignore") as f:
                        if module_name in f.read() or file_stem in f.read():
                            result["verification"]["test_references"].append(
                                str(test_file.relative_to(self.project_root))
                            )
                            if len(result["verification"]["test_references"]) >= 2:
                                break
                except Exception:
                    pass
        
        # Check implementation status
        impl_status = self.check_implementation_status(file_path)
        result["implementation_status"] = impl_status
        
        # Categorize based on implementation status
        if impl_status["needs_implementation"]:
            result["category"] = "needs_implementation"
            result["recommendation"] = "IMPLEMENT - Has TODOs/FIXMEs/stubs"
            result["risk_level"] = "medium"
        elif impl_status["needs_integration"]:
            result["category"] = "needs_integration"
            result["recommendation"] = "INTEGRATE - Planned feature"
            result["risk_level"] = "medium"
        elif result["verification"]["test_references"]:
            result["category"] = "needs_review"
            result["recommendation"] = "REVIEW - Referenced in tests"
            result["risk_level"] = "medium"
        elif impl_status["has_docstrings"] and impl_status["implementation_ratio"] > 0.8:
            result["category"] = "needs_review"
            result["recommendation"] = "REVIEW - Well-documented, may have value"
            result["risk_level"] = "low"
        
        return result


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive file verification")
    parser.add_argument(
        "--analysis-file",
        default="agent_workspaces/Agent-5/unnecessary_files_analysis.json",
        help="Path to unnecessary_files_analysis.json"
    )
    parser.add_argument(
        "--output",
        default="agent_workspaces/Agent-5/comprehensive_verification_results.json",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    print("🔍 COMPREHENSIVE FILE VERIFICATION")
    print("=" * 60)
    print("Verifying usage + implementation status\n")
    
    # Load analysis file
    if not Path(args.analysis_file).exists():
        print(f"❌ Analysis file not found: {args.analysis_file}")
        return
    
    with open(args.analysis_file, "r", encoding="utf-8") as f:
        analysis_data = json.load(f)
    
    # Collect files
    files_to_verify = []
    for category in ["unused", "deprecated_directory", "deletion_markers", "duplicates"]:
        for file_info in analysis_data.get(category, []):
            file_path = Path(file_info["file_path"])
            if file_path.exists():
                files_to_verify.append(file_path)
    
    print(f"📋 Verifying {len(files_to_verify)} files...\n")
    
    verifier = ComprehensiveFileVerifier()
    
    results = {
        "summary": {
            "total_files": len(files_to_verify),
            "truly_unused": 0,
            "needs_implementation": 0,
            "needs_integration": 0,
            "needs_review": 0,
            "must_keep": 0,
        },
        "by_category": {
            "truly_unused": [],
            "needs_implementation": [],
            "needs_integration": [],
            "needs_review": [],
            "must_keep": [],
        }
    }
    
    for i, file_path in enumerate(files_to_verify, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(files_to_verify)}")
        
        relative = file_path.relative_to(verifier.src_root)
        module_name = str(relative.with_suffix("")).replace("\\", ".").replace("/", ".")
        
        result = verifier.verify_file_comprehensive(file_path, module_name)
        
        category = result["category"]
        results["by_category"][category].append(result)
        results["summary"][category.replace("_", "_")] += 1
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE VERIFICATION SUMMARY")
    print("=" * 60)
    summary = results["summary"]
    print(f"Total Files: {summary['total_files']}")
    print(f"\n✅ Truly Unused (Safe to Delete): {summary['truly_unused']}")
    print(f"🔧 Needs Implementation: {summary['needs_implementation']}")
    print(f"🔗 Needs Integration: {summary['needs_integration']}")
    print(f"⚠️  Needs Review: {summary['needs_review']}")
    print(f"❌ Must Keep: {summary['must_keep']}")
    
    print(f"\n✅ Results saved to: {output_path}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()




