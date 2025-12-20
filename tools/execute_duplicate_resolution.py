#!/usr/bin/env python3
"""
Execute Duplicate File Resolution - Technical Debt Reduction
============================================================

Safely deletes duplicate files based on analysis results.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-12-02
"""

import json
from pathlib import Path
from typing import List, Dict
import argparse


def verify_file_identical(file1: Path, file2: Path) -> bool:
    """Verify two files are truly identical."""
    if not file1.exists() or not file2.exists():
        return False
    
    if file1.stat().st_size != file2.stat().st_size:
        return False
    
    return file1.read_bytes() == file2.read_bytes()


def check_imports(file_path: Path, repo_root: Path) -> List[str]:
    """Check if file is imported anywhere."""
    imports = []
    file_name = file_path.name
    file_stem = file_path.stem
    
    # Only check Python files for Python imports
    if file_path.suffix != '.py':
        return []
    
    # Get relative import path
    try:
        rel_path = file_path.relative_to(repo_root)
        if 'src' not in str(rel_path):
            return []  # Only check src/ files
        
        # Build import path (e.g., src/core/messaging.py -> src.core.messaging)
        import_parts = rel_path.with_suffix('').parts
        if import_parts[0] != 'src':
            return []
        
        import_path = '.'.join(import_parts)
        module_name = import_parts[-1]
    except Exception:
        return []
    
    # Search for imports in Python files only
    for py_file in repo_root.rglob("*.py"):
        if py_file == file_path:
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # More precise import detection
            import_patterns = [
                f"from {import_path} import",
                f"from {import_path}.",
                f"import {module_name}",
            ]
            
            for pattern in import_patterns:
                # Check if pattern appears as actual import (not in string/comment)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith(pattern) or f" {pattern} " in line:
                        # Basic check: not in string literal
                        if '"' not in line[:line.find(pattern)] and "'" not in line[:line.find(pattern)]:
                            imports.append(str(py_file.relative_to(repo_root)))
                            break
                if imports and str(py_file.relative_to(repo_root)) in imports:
                    break
        except Exception:
            pass
    
    return imports


def execute_resolution(
    analysis_data: Dict,
    dry_run: bool = True,
    max_files: int = 50
) -> Dict:
    """Execute duplicate file resolution."""
    results = {
        'deleted': [],
        'skipped': [],
        'errors': [],
        'total_safe': 0
    }
    
    repo_root = Path.cwd()
    identical_groups = analysis_data['categories']['identical_safe_delete']
    
    print(f"🔍 Processing {len(identical_groups)} identical file groups...")
    print(f"📊 Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"📊 Max files: {max_files}")
    print("")
    
    count = 0
    for group in identical_groups:
        if count >= max_files:
            break
        
        ssot_path = repo_root / group['ssot']
        
        for dup_path_str in group['duplicates']:
            if count >= max_files:
                break
            
            dup_path = repo_root / dup_path_str
            
            # Verify files exist
            if not ssot_path.exists():
                results['errors'].append({
                    'file': dup_path_str,
                    'reason': f'SSOT file missing: {group["ssot"]}'
                })
                continue
            
            if not dup_path.exists():
                results['skipped'].append({
                    'file': dup_path_str,
                    'reason': 'File already deleted'
                })
                continue
            
            # Verify files are identical
            if not verify_file_identical(ssot_path, dup_path):
                results['skipped'].append({
                    'file': dup_path_str,
                    'reason': 'Files not identical (safety check)'
                })
                continue
            
            # Check imports
            imports = check_imports(dup_path, repo_root)
            if imports:
                results['skipped'].append({
                    'file': dup_path_str,
                    'reason': f'File is imported in {len(imports)} files',
                    'imports': imports[:5]  # Show first 5
                })
                continue
            
            # Delete file
            if not dry_run:
                try:
                    dup_path.unlink()
                    results['deleted'].append(dup_path_str)
                    count += 1
                    print(f"✅ Deleted: {dup_path_str}")
                except Exception as e:
                    results['errors'].append({
                        'file': dup_path_str,
                        'reason': str(e)
                    })
            else:
                results['deleted'].append(dup_path_str)
                count += 1
                print(f"🔍 Would delete: {dup_path_str}")
    
    results['total_safe'] = count
    return results


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Execute duplicate file resolution')
    parser.add_argument('--execute', action='store_true', help='Actually delete files (default: dry run)')
    parser.add_argument('--max-files', type=int, default=50, help='Maximum files to process')
    parser.add_argument('--data-file', type=str, default='docs/technical_debt/DUPLICATE_ANALYSIS_DATA.json',
                       help='Path to analysis data JSON')
    
    args = parser.parse_args()
    
    # Load analysis data
    data_path = Path(args.data_file)
    if not data_path.exists():
        print(f"❌ Analysis data not found: {data_path}")
        print("   Run: python tools/comprehensive_duplicate_analyzer.py")
        return 1
    
    with open(data_path) as f:
        analysis_data = json.load(f)
    
    # Execute resolution
    results = execute_resolution(
        analysis_data,
        dry_run=not args.execute,
        max_files=args.max_files
    )
    
    # Print summary
    print("")
    print("=" * 60)
    print("📊 Resolution Summary")
    print("=" * 60)
    print(f"✅ Deleted/Safe to delete: {len(results['deleted'])}")
    print(f"⏭️  Skipped: {len(results['skipped'])}")
    print(f"❌ Errors: {len(results['errors'])}")
    print("")
    
    if results['skipped']:
        print("⏭️  Skipped Files:")
        for item in results['skipped'][:10]:
            print(f"   - {item['file']}: {item['reason']}")
        if len(results['skipped']) > 10:
            print(f"   ... and {len(results['skipped']) - 10} more")
        print("")
    
    if results['errors']:
        print("❌ Errors:")
        for item in results['errors']:
            print(f"   - {item['file']}: {item['reason']}")
        print("")
    
    if not args.execute:
        print("💡 Run with --execute to actually delete files")
        print("💡 Use --max-files to limit batch size")
    
    return 0


if __name__ == '__main__':
    exit(main())

