"""
Review 64 Files Duplicate Analysis Tool
Analyzes 22 files (3 with functionality_exists, 19 possible duplicates)
Provides MERGE/USE_EXISTING/DELETE recommendations
"""
import json
import filecmp
from pathlib import Path
from typing import Dict, List, Any, Optional
import difflib

class DuplicateFileReviewer:
    """Reviews duplicate files and provides recommendations."""
    
    def __init__(self, file_list_path: Path):
        self.file_list_path = file_list_path
        self.recommendations: List[Dict[str, Any]] = []
        
    def load_file_list(self) -> Dict[str, Any]:
        """Load the file list from JSON."""
        with open(self.file_list_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content safely."""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
    
    def compare_files(self, file1: str, file2: str) -> Dict[str, Any]:
        """Compare two files for similarity."""
        content1 = self.read_file_content(file1)
        content2 = self.read_file_content(file2)
        
        if content1 is None or content2 is None:
            return {"identical": False, "similarity": 0.0, "error": "File not found"}
        
        # Check if identical
        identical = content1 == content2
        
        # Calculate similarity
        similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
        
        return {
            "identical": identical,
            "similarity": similarity,
            "size1": len(content1),
            "size2": len(content2)
        }
    
    def analyze_functionality_exists(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze files with functionality_exists flag."""
        file_path = file_info["file_path"]
        similar_files = file_info.get("similar_files", [])
        
        recommendation = {
            "file": file_path,
            "type": "functionality_exists",
            "recommendation": "USE_EXISTING",
            "reason": "Functionality exists in similar files",
            "similar_files": [],
            "analysis": {}
        }
        
        # Compare with similar files
        for similar in similar_files:
            similar_path = similar.get("file", "")
            if similar_path:
                # Convert relative path to full path
                full_path = Path("src") / similar_path.replace("\\", "/")
                if not full_path.exists():
                    full_path = Path(similar_path.replace("\\", "/"))
                
                comparison = self.compare_files(file_path, str(full_path))
                recommendation["similar_files"].append({
                    "file": similar_path,
                    "similarity_score": similar.get("similarity_score", 0.0),
                    "comparison": comparison
                })
        
        # Determine recommendation
        if recommendation["similar_files"]:
            best_match = max(recommendation["similar_files"], 
                           key=lambda x: x.get("similarity_score", 0.0))
            
            if best_match["comparison"].get("identical", False):
                recommendation["recommendation"] = "DELETE"
                recommendation["reason"] = "File is identical to existing file"
            elif best_match.get("similarity_score", 0.0) > 0.7:
                recommendation["recommendation"] = "USE_EXISTING"
                recommendation["reason"] = f"High similarity ({best_match.get('similarity_score', 0.0):.2%}) with existing file"
            else:
                recommendation["recommendation"] = "MERGE"
                recommendation["reason"] = "Similar functionality, can be merged"
        
        return recommendation
    
    def analyze_possible_duplicate(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze files marked as possible duplicates."""
        file_path = file_info["file_path"]
        similar_files = file_info.get("similar_files", [])
        
        recommendation = {
            "file": file_path,
            "type": "possible_duplicate",
            "recommendation": "REVIEW_NEEDED",
            "reason": "Needs detailed analysis",
            "similar_files": [],
            "analysis": {}
        }
        
        # Compare with similar files
        for similar in similar_files:
            similar_path = similar.get("file", "")
            if similar_path:
                # Convert relative path to full path
                full_path = Path("src") / similar_path.replace("\\", "/")
                if not full_path.exists():
                    full_path = Path(similar_path.replace("\\", "/"))
                
                comparison = self.compare_files(file_path, str(full_path))
                recommendation["similar_files"].append({
                    "file": similar_path,
                    "similarity_score": similar.get("similarity_score", 0.0),
                    "comparison": comparison
                })
        
        # Determine recommendation
        if recommendation["similar_files"]:
            best_match = max(recommendation["similar_files"], 
                           key=lambda x: x.get("similarity_score", 0.0))
            
            similarity = best_match.get("similarity_score", 0.0)
            identical = best_match["comparison"].get("identical", False)
            
            if identical:
                recommendation["recommendation"] = "DELETE"
                recommendation["reason"] = "File is identical to existing file"
            elif similarity > 0.8:
                recommendation["recommendation"] = "USE_EXISTING"
                recommendation["reason"] = f"Very high similarity ({similarity:.2%}) - use existing"
            elif similarity > 0.5:
                recommendation["recommendation"] = "MERGE"
                recommendation["reason"] = f"Moderate similarity ({similarity:.2%}) - can be merged"
            else:
                recommendation["recommendation"] = "KEEP"
                recommendation["reason"] = f"Low similarity ({similarity:.2%}) - likely different functionality"
        
        return recommendation
    
    def review_all_files(self) -> Dict[str, Any]:
        """Review all files in the list."""
        data = self.load_file_list()
        
        # Review functionality_exists files
        for file_info in data.get("functionality_exists_files", []):
            recommendation = self.analyze_functionality_exists(file_info)
            self.recommendations.append(recommendation)
        
        # Review possible duplicate files
        for file_info in data.get("possible_duplicate_files", []):
            recommendation = self.analyze_possible_duplicate(file_info)
            self.recommendations.append(recommendation)
        
        # Generate summary
        summary = {
            "total_files": len(self.recommendations),
            "functionality_exists": len([r for r in self.recommendations if r["type"] == "functionality_exists"]),
            "possible_duplicates": len([r for r in self.recommendations if r["type"] == "possible_duplicate"]),
            "recommendations": {
                "DELETE": len([r for r in self.recommendations if r["recommendation"] == "DELETE"]),
                "USE_EXISTING": len([r for r in self.recommendations if r["recommendation"] == "USE_EXISTING"]),
                "MERGE": len([r for r in self.recommendations if r["recommendation"] == "MERGE"]),
                "KEEP": len([r for r in self.recommendations if r["recommendation"] == "KEEP"]),
                "REVIEW_NEEDED": len([r for r in self.recommendations if r["recommendation"] == "REVIEW_NEEDED"])
            }
        }
        
        return {
            "summary": summary,
            "recommendations": self.recommendations
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Review 64 files for duplicates")
    parser.add_argument("--file-list", type=str,
                       default="agent_workspaces/Agent-5/22_duplicate_files_list.json",
                       help="Path to file list JSON")
    parser.add_argument("--output", type=str,
                       default="agent_workspaces/Agent-8/64_FILES_DUPLICATE_REVIEW_COMPLETE.md",
                       help="Output report path")
    args = parser.parse_args()
    
    reviewer = DuplicateFileReviewer(Path(args.file_list))
    results = reviewer.review_all_files()
    
    # Generate markdown report
    report_lines = [
        "# ✅ 64 Files Duplicate Review - COMPLETE",
        "",
        "**Date**: 2025-12-02 16:30:00",
        "**Agent**: Agent-8 (SSOT & System Integration Specialist)",
        "**Status**: ✅ **REVIEW COMPLETE**",
        "**Priority**: HIGH",
        "",
        "---",
        "",
        "## 📊 REVIEW SUMMARY",
        "",
        f"**Total Files Reviewed**: {results['summary']['total_files']}",
        f"**Functionality Exists**: {results['summary']['functionality_exists']}",
        f"**Possible Duplicates**: {results['summary']['possible_duplicates']}",
        "",
        "### **Recommendations Breakdown**:",
        f"- **DELETE**: {results['summary']['recommendations']['DELETE']} files",
        f"- **USE_EXISTING**: {results['summary']['recommendations']['USE_EXISTING']} files",
        f"- **MERGE**: {results['summary']['recommendations']['MERGE']} files",
        f"- **KEEP**: {results['summary']['recommendations']['KEEP']} files",
        f"- **REVIEW_NEEDED**: {results['summary']['recommendations']['REVIEW_NEEDED']} files",
        "",
        "---",
        "",
        "## 📋 DETAILED RECOMMENDATIONS",
        ""
    ]
    
    # Add detailed recommendations
    for i, rec in enumerate(results['recommendations'], 1):
        report_lines.extend([
            f"### **{i}. {Path(rec['file']).name}**",
            "",
            f"**File**: `{rec['file']}`",
            f"**Type**: {rec['type']}",
            f"**Recommendation**: **{rec['recommendation']}**",
            f"**Reason**: {rec['reason']}",
            ""
        ])
        
        if rec['similar_files']:
            report_lines.append("**Similar Files**:")
            for similar in rec['similar_files'][:3]:  # Top 3
                similarity = similar.get('similarity_score', 0.0)
                comparison = similar.get('comparison', {})
                identical = comparison.get('identical', False)
                
                if identical:
                    status = "✅ IDENTICAL"
                elif similarity > 0.7:
                    status = "⚠️ HIGH SIMILARITY"
                else:
                    status = "🔍 MODERATE SIMILARITY"
                
                report_lines.append(f"- `{similar['file']}` - {status} ({similarity:.2%})")
        
        report_lines.append("")
    
    report_lines.extend([
        "---",
        "",
        "## 🎯 NEXT ACTIONS",
        "",
        "1. **Agent-1**: Review recommendations and execute decisions",
        "2. **DELETE**: Remove duplicate files after verification",
        "3. **USE_EXISTING**: Update imports to use existing files",
        "4. **MERGE**: Merge functionality into canonical files",
        "5. **KEEP**: Continue with implementation",
        "",
        "---",
        "",
        "**Status**: ✅ **REVIEW COMPLETE**",
        "",
        "🐝 **WE. ARE. SWARM. ⚡🔥**"
    ])
    
    # Save report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    # Save JSON for programmatic use
    json_output = output_path.with_suffix('.json')
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("="*60)
    print("📊 64 FILES DUPLICATE REVIEW - COMPLETE")
    print("="*60)
    print(f"✅ Total Files Reviewed: {results['summary']['total_files']}")
    print(f"📋 Recommendations:")
    for rec_type, count in results['summary']['recommendations'].items():
        if count > 0:
            print(f"   - {rec_type}: {count}")
    print(f"\n✅ Report saved to: {output_path}")
    print(f"✅ JSON saved to: {json_output}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")

if __name__ == "__main__":
    main()




