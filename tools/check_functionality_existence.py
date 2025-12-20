#!/usr/bin/env python3
"""
Check Functionality Existence Tool
===================================

Before implementing or deleting files, check if the functionality already exists
elsewhere in the project in a different form.

<!-- SSOT Domain: infrastructure -->

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-01
Priority: CRITICAL - Prevents duplicate implementation or premature deletion
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Optional


class FunctionalityExistenceChecker:
    """Check if functionality already exists in project."""
    
    def __init__(self, src_root: str = "src", project_root: str = "."):
        """Initialize checker."""
        self.src_root = Path(src_root)
        self.project_root = Path(project_root)
        self.functionality_map: Dict[str, List[Path]] = defaultdict(list)
        
    def extract_functionality_indicators(self, file_path: Path) -> Dict[str, Any]:
        """Extract functionality indicators from a file."""
        indicators = {
            "classes": [],
            "functions": [],
            "keywords": [],
            "imports": [],
            "capabilities": [],
        }
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content, str(file_path))
                
                # Extract classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        indicators["classes"].append(node.name)
                        # Check base classes for capability hints
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                indicators["keywords"].append(base.id)
                
                # Extract functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        indicators["functions"].append(node.name)
                        # Extract docstring for capability hints
                        docstring = ast.get_docstring(node)
                        if docstring:
                            indicators["keywords"].extend(
                                re.findall(r'\b\w+\b', docstring.lower())[:10]
                            )
                
            except SyntaxError:
                pass
            
            # Extract imports
            imports = re.findall(r'(?:from|import)\s+(\S+)', content)
            indicators["imports"] = [imp.split('.')[0] for imp in imports[:10]]
            
            # Extract capability keywords from content
            capability_keywords = [
                "manager", "engine", "service", "handler", "processor",
                "analyzer", "coordinator", "orchestrator", "validator",
                "monitor", "reporter", "scraper", "parser", "extractor"
            ]
            
            for keyword in capability_keywords:
                if keyword.lower() in content.lower():
                    indicators["keywords"].append(keyword)
                    indicators["capabilities"].append(keyword)
            
            # Extract from file path/name
            path_parts = str(file_path).lower().replace("\\", "/").split("/")
            indicators["keywords"].extend(path_parts)
            
        except Exception:
            pass
        
        return indicators
    
    def find_similar_functionality(self, target_file: Path, all_files: List[Path]) -> List[Dict[str, Any]]:
        """Find files with similar functionality."""
        target_indicators = self.extract_functionality_indicators(target_file)
        target_keywords = set(
            target_indicators["classes"] + 
            target_indicators["functions"] + 
            target_indicators["capabilities"] +
            [target_file.stem.lower()]
        )
        
        similar_files = []
        
        for other_file in all_files:
            if other_file == target_file:
                continue
            
            other_indicators = self.extract_functionality_indicators(other_file)
            other_keywords = set(
                other_indicators["classes"] + 
                other_indicators["functions"] + 
                other_indicators["capabilities"] +
                [other_file.stem.lower()]
            )
            
            # Calculate similarity
            common_keywords = target_keywords.intersection(other_keywords)
            similarity_score = len(common_keywords) / max(len(target_keywords), len(other_keywords), 1)
            
            if similarity_score > 0.3:  # 30% similarity threshold
                similar_files.append({
                    "file": str(other_file.relative_to(self.src_root)),
                    "similarity_score": round(similarity_score, 2),
                    "common_keywords": list(common_keywords)[:5],
                    "classes": other_indicators["classes"],
                    "functions": other_indicators["functions"][:5],
                })
        
        # Sort by similarity
        similar_files.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return similar_files[:5]  # Top 5 matches
    
    def check_functionality_exists(self, file_path: Path, all_files: List[Path]) -> Dict[str, Any]:
        """Check if file's functionality exists elsewhere."""
        result = {
            "file_path": str(file_path),
            "relative_path": str(file_path.relative_to(self.src_root)),
            "functionality_exists": False,
            "similar_files": [],
            "recommendation": "IMPLEMENT_OR_INTEGRATE",
        }
        
        # Find similar functionality
        similar = self.find_similar_functionality(file_path, all_files)
        result["similar_files"] = similar
        
        if similar:
            # Check if similar file has higher implementation ratio
            highest_similarity = similar[0]["similarity_score"]
            
            if highest_similarity > 0.7:
                result["functionality_exists"] = True
                result["recommendation"] = "REVIEW_DUPLICATE - Similar functionality exists, may be duplicate"
            elif highest_similarity > 0.5:
                result["functionality_exists"] = True
                result["recommendation"] = "CHECK_IF_DUPLICATE - Similar functionality exists, verify if duplicate"
            else:
                result["recommendation"] = "POSSIBLE_DUPLICATE - Some similar functionality, investigate"
        
        return result
    
    def analyze_files(self, files_to_check: List[Path]) -> Dict[str, Any]:
        """Analyze multiple files for functionality existence."""
        print(f"🔍 Checking functionality existence for {len(files_to_check)} files...")
        print("Building functionality map from all source files...\n")
        
        # Get all source files for comparison
        all_source_files = []
        for path in self.src_root.rglob("*.py"):
            if "__pycache__" not in str(path):
                all_source_files.append(path)
        
        print(f"📊 Comparing against {len(all_source_files)} source files in project...\n")
        
        results = {
            "summary": {
                "total_checked": len(files_to_check),
                "functionality_exists": 0,
                "possible_duplicates": 0,
                "no_existing_functionality": 0,
            },
            "files": [],
        }
        
        for i, file_path in enumerate(files_to_check, 1):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(files_to_check)}")
            
            result = self.check_functionality_exists(file_path, all_source_files)
            results["files"].append(result)
            
            if result["functionality_exists"]:
                results["summary"]["functionality_exists"] += 1
            elif result["similar_files"]:
                results["summary"]["possible_duplicates"] += 1
            else:
                results["summary"]["no_existing_functionality"] += 1
        
        return results


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check if functionality already exists")
    parser.add_argument(
        "--files-json",
        default="agent_workspaces/Agent-5/comprehensive_verification_results.json",
        help="JSON file with files to check"
    )
    parser.add_argument(
        "--category",
        choices=["needs_implementation", "needs_integration", "truly_unused", "all"],
        default="needs_implementation",
        help="Which category to check"
    )
    parser.add_argument(
        "--output",
        default="agent_workspaces/Agent-5/functionality_existence_check.json",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    print("🔍 FUNCTIONALITY EXISTENCE CHECK")
    print("=" * 60)
    print("Checking if functionality already exists before implementing/deleting\n")
    
    # Load files to check
    if not Path(args.files_json).exists():
        print(f"❌ File not found: {args.files_json}")
        return
    
    with open(args.files_json, "r", encoding="utf-8") as f:
        verification_data = json.load(f)
    
    # Get files from specified category
    files_to_check = []
    
    if args.category == "all":
        for category in ["needs_implementation", "needs_integration", "truly_unused"]:
            for file_info in verification_data["by_category"].get(category, []):
                file_path = Path(file_info["file_path"])
                if file_path.exists():
                    files_to_check.append(file_path)
    else:
        for file_info in verification_data["by_category"].get(args.category, []):
            file_path = Path(file_info["file_path"])
            if file_path.exists():
                files_to_check.append(file_path)
    
    print(f"📋 Checking {len(files_to_check)} files from category: {args.category}\n")
    
    checker = FunctionalityExistenceChecker()
    results = checker.analyze_files(files_to_check)
    
    print("\n" + "=" * 60)
    print("📊 FUNCTIONALITY EXISTENCE SUMMARY")
    print("=" * 60)
    summary = results["summary"]
    print(f"Total Files Checked: {summary['total_checked']}")
    print(f"✅ Functionality Already Exists: {summary['functionality_exists']}")
    print(f"⚠️  Possible Duplicates: {summary['possible_duplicates']}")
    print(f"🔨 No Existing Functionality (Can Implement): {summary['no_existing_functionality']}")
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_path}")
    
    # Show top duplicates
    duplicates = [f for f in results["files"] if f["functionality_exists"]]
    if duplicates:
        print("\n" + "=" * 60)
        print("⚠️  TOP FUNCTIONALITY DUPLICATES")
        print("=" * 60)
        for dup in duplicates[:10]:
            print(f"\n{dup['relative_path']}")
            print(f"  Similar to: {dup['similar_files'][0]['file']}")
            print(f"  Similarity: {dup['similar_files'][0]['similarity_score']}")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()




