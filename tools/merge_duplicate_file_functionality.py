#!/usr/bin/env python3
"""
Merge Duplicate File Functionality - Agent-3
=============================================

Compares duplicate files and identifies unique functionality to merge.
Helps resolve duplicate files by analyzing differences and suggesting merges.

Usage:
    python tools/merge_duplicate_file_functionality.py <file1> <file2> [output]
"""

import sys
import difflib
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def read_file_lines(filepath: Path) -> List[str]:
    """Read file and return lines."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.readlines()
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return []


def analyze_differences(file1: Path, file2: Path) -> Dict:
    """Analyze differences between two files."""
    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)
    
    if not lines1 or not lines2:
        return {
            "identical": False,
            "error": "Could not read one or both files"
        }
    
    # Check if identical
    if lines1 == lines2:
        return {
            "identical": True,
            "similarity": 1.0,
            "unique_in_file1": [],
            "unique_in_file2": [],
            "recommendation": "Files are identical - safe to remove duplicate"
        }
    
    # Calculate similarity
    similarity = difflib.SequenceMatcher(None, lines1, lines2).ratio()
    
    # Find unique lines
    unique_in_file1 = []
    unique_in_file2 = []
    
    # Use difflib to find differences
    diff = list(difflib.unified_diff(
        lines1, lines2,
        fromfile=str(file1),
        tofile=str(file2),
        lineterm=''
    ))
    
    # Parse diff to find unique sections
    current_file = None
    for line in diff:
        if line.startswith('---'):
            current_file = 1
        elif line.startswith('+++'):
            current_file = 2
        elif line.startswith('-') and not line.startswith('---'):
            if current_file == 1:
                unique_in_file1.append(line[1:].strip())
        elif line.startswith('+') and not line.startswith('+++'):
            if current_file == 2:
                unique_in_file2.append(line[1:].strip())
    
    # Generate recommendation
    if similarity > 0.9:
        recommendation = "Files are very similar - likely safe to merge with minor adjustments"
    elif similarity > 0.7:
        recommendation = "Files have significant differences - manual review required before merge"
    else:
        recommendation = "Files are substantially different - may serve different purposes, review carefully"
    
    return {
        "identical": False,
        "similarity": similarity,
        "unique_in_file1": unique_in_file1[:20],  # Limit output
        "unique_in_file2": unique_in_file2[:20],
        "total_unique_file1": len(unique_in_file1),
        "total_unique_file2": len(unique_in_file2),
        "recommendation": recommendation,
        "diff_summary": f"{len(unique_in_file1)} unique lines in file1, {len(unique_in_file2)} unique lines in file2"
    }


def generate_merge_suggestion(file1: Path, file2: Path, ssot_file: Path) -> str:
    """Generate merge suggestion report."""
    analysis = analyze_differences(file1, file2)
    
    report = f"""
# Merge Analysis: {file1.name}

## Files Compared:
- File 1: {file1}
- File 2: {file2}
- SSOT: {ssot_file}

## Analysis Results:
- **Identical**: {analysis.get('identical', False)}
- **Similarity**: {analysis.get('similarity', 0):.2%}
- **Unique in File 1**: {analysis.get('total_unique_file1', 0)} lines
- **Unique in File 2**: {analysis.get('total_unique_file2', 0)} lines

## Recommendation:
{analysis.get('recommendation', 'Review required')}

## Next Steps:
1. Review unique functionality in both files
2. Identify which features should be preserved
3. Merge unique functionality into SSOT version
4. Test merged version
5. Remove duplicates after merge verified
"""
    
    if analysis.get('unique_in_file1'):
        report += "\n## Unique Functionality in File 1:\n"
        for line in analysis['unique_in_file1'][:10]:
            report += f"- {line}\n"
    
    if analysis.get('unique_in_file2'):
        report += "\n## Unique Functionality in File 2:\n"
        for line in analysis['unique_in_file2'][:10]:
            report += f"- {line}\n"
    
    return report


def main():
    """Main execution function."""
    if len(sys.argv) < 3:
        print("Usage: python merge_duplicate_file_functionality.py <file1> <file2> [ssot_file]")
        print("\nExample:")
        print("  python merge_duplicate_file_functionality.py file1.py file2.py ssot.py")
        sys.exit(1)
    
    file1 = Path(sys.argv[1])
    file2 = Path(sys.argv[2])
    ssot_file = Path(sys.argv[3]) if len(sys.argv) > 3 else file1
    
    if not file1.exists():
        print(f"❌ File not found: {file1}")
        sys.exit(1)
    
    if not file2.exists():
        print(f"❌ File not found: {file2}")
        sys.exit(1)
    
    print(f"🔍 Analyzing differences between:")
    print(f"   File 1: {file1}")
    print(f"   File 2: {file2}")
    print(f"   SSOT: {ssot_file}")
    print()
    
    analysis = analyze_differences(file1, file2)
    
    if analysis.get('identical'):
        print("✅ Files are identical - safe to remove duplicate")
        print(f"   Recommendation: {analysis.get('recommendation')}")
    else:
        print(f"⚠️ Files differ:")
        print(f"   Similarity: {analysis.get('similarity', 0):.2%}")
        print(f"   Unique in File 1: {analysis.get('total_unique_file1', 0)} lines")
        print(f"   Unique in File 2: {analysis.get('total_unique_file2', 0)} lines")
        print(f"   Recommendation: {analysis.get('recommendation')}")
        
        if analysis.get('unique_in_file1') or analysis.get('unique_in_file2'):
            print("\n📋 Generating merge suggestion report...")
            report = generate_merge_suggestion(file1, file2, ssot_file)
            output_file = file1.parent / f"{file1.stem}_merge_analysis.md"
            output_file.write_text(report)
            print(f"✅ Report saved to: {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

