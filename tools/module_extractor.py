#!/usr/bin/env python3
"""
Module Extractor - Automated Function Extraction
================================================

Helps extract functions/classes from large files into focused modules.
Based on experience refactoring swarm_mission_control.py and swarm_orchestrator.py.

Author: Agent-8 (Quality Assurance) - Thread Experience Tool
Created: 2025-10-14
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import List, Tuple


def extract_function_or_class(file_path: Path, name: str) -> Tuple[str | None, int, int]:
    """
    Extract a function or class from a file.
    
    Returns: (code, start_line, end_line)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if node.name == name:
                    # Get the function/class code
                    start_line = node.lineno - 1  # 0-indexed
                    end_line = node.end_lineno
                    
                    # Include decorators
                    if node.decorator_list:
                        start_line = node.decorator_list[0].lineno - 1
                    
                    code = '\n'.join(lines[start_line:end_line])
                    return code, start_line + 1, end_line
        
        return None, 0, 0
        
    except Exception as e:
        print(f"Error extracting {name}: {e}")
        return None, 0, 0


def list_extractable_items(file_path: Path) -> List[dict]:
    """List all functions and classes that can be extracted."""
    items = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                # Only top-level items
                if isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    item_type = "function"
                elif isinstance(node, ast.AsyncFunctionDef) and node.col_offset == 0:
                    item_type = "async_function"
                elif isinstance(node, ast.ClassDef) and node.col_offset == 0:
                    item_type = "class"
                else:
                    continue
                
                lines = node.end_lineno - node.lineno + 1
                items.append({
                    "name": node.name,
                    "type": item_type,
                    "lines": lines,
                    "start": node.lineno,
                    "end": node.end_lineno
                })
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
    
    return items


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Module Extractor - Extract functions/classes into focused modules"
    )
    parser.add_argument("--file", required=True, help="Source file to extract from")
    parser.add_argument("--list", action="store_true", help="List extractable items")
    parser.add_argument("--extract", help="Name of function/class to extract")
    parser.add_argument("--output", help="Output file for extracted code")
    
    args = parser.parse_args()
    
    source_file = Path(args.file)
    if not source_file.exists():
        print(f"Error: {args.file} not found")
        return 1
    
    if args.list:
        # List mode
        items = list_extractable_items(source_file)
        
        print(f"\n📋 EXTRACTABLE ITEMS FROM {args.file}")
        print("="*80)
        
        functions = [i for i in items if 'function' in i['type']]
        classes = [i for i in items if i['type'] == 'class']
        
        if functions:
            print(f"\n🔧 FUNCTIONS ({len(functions)}):")
            for item in sorted(functions, key=lambda x: x['lines'], reverse=True):
                status = "⚠️" if item['lines'] > 30 else "✅"
                print(f"  {status} {item['name']} ({item['lines']} lines, L{item['start']}-{item['end']})")
        
        if classes:
            print(f"\n🏛️  CLASSES ({len(classes)}):")
            for item in sorted(classes, key=lambda x: x['lines'], reverse=True):
                status = "⚠️" if item['lines'] > 200 else "✅"
                print(f"  {status} {item['name']} ({item['lines']} lines, L{item['start']}-{item['end']})")
        
        total_lines = sum(i['lines'] for i in items)
        print(f"\n📊 TOTAL: {len(items)} items, {total_lines} lines")
        print("="*80 + "\n")
        
        return 0
    
    elif args.extract and args.output:
        # Extract mode
        code, start, end = extract_function_or_class(source_file, args.extract)
        
        if not code:
            print(f"Error: '{args.extract}' not found in {args.file}")
            return 1
        
        # Write to output file
        output_path = Path(args.output)
        
        # Create module header
        header = f'''#!/usr/bin/env python3
"""
{output_path.stem.replace('_', ' ').title()} - Extracted Module
{'='*len(output_path.stem + ' - Extracted Module')}

Extracted from {source_file.name}

Author: Agent-8 (Module Extraction Tool)
Created: 2025-10-14
"""

'''
        
        full_content = header + code + "\n\n\n__all__ = ['" + args.extract + "']\n"
        
        output_path.write_text(full_content, encoding='utf-8')
        
        print(f"\n✅ Extracted '{args.extract}' ({end - start + 1} lines)")
        print(f"📁 Saved to: {args.output}")
        print(f"📍 Original location: L{start}-{end} in {args.file}")
        print(f"\n💡 Next step: Remove lines {start}-{end} from {args.file}")
        print(f"💡 Then add: from .{output_path.stem} import {args.extract}\n")
        
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

