#!/usr/bin/env python3
"""
Type Annotations Tool - Add Missing Type Hints
==============================================

Scans Python files for missing type annotations and adds them.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-12-04
License: MIT
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def find_files_without_annotations(directory: Path) -> List[Tuple[Path, List[str]]]:
    """Find files with functions/methods missing type annotations."""
    results: List[Tuple[Path, List[str]]] = []
    
    for py_file in directory.rglob("*.py"):
        if "test" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=str(py_file))
                
            missing_annotations: List[str] = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has return type annotation
                    if node.returns is None:
                        # Check if it's not a simple getter/setter
                        if not (len(node.args.args) == 1 and node.name.startswith(("get_", "set_", "is_", "has_"))):
                            missing_annotations.append(f"Function '{node.name}' missing return type")
                    
                    # Check if parameters have type annotations
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != "self" and arg.arg != "cls":
                            missing_annotations.append(f"Function '{node.name}' parameter '{arg.arg}' missing type")
                            
            if missing_annotations:
                results.append((py_file, missing_annotations))
                
        except Exception as e:
            print(f"Error parsing {py_file}: {e}")
    
    return results


def add_basic_annotations(file_path: Path) -> bool:
    """Add basic type annotations to a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        modified = False
        new_lines: List[str] = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Match function definitions without return type
            func_match = re.match(r'^(\s*)def (\w+)\((.*?)\):\s*$', line)
            if func_match:
                indent = func_match.group(1)
                func_name = func_match.group(2)
                params = func_match.group(3)
                
                # Skip if already has return type
                if "->" in line:
                    new_lines.append(line)
                    i += 1
                    continue
                
                # Determine return type based on function name/body
                return_type = infer_return_type(func_name, lines, i)
                
                # Add return type annotation
                new_line = f"{indent}def {func_name}({params}) -> {return_type}:\n"
                new_lines.append(new_line)
                modified = True
            else:
                new_lines.append(line)
            
            i += 1
        
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def infer_return_type(func_name: str, lines: List[str], line_idx: int) -> str:
    """Infer return type from function name and body."""
    # Common patterns
    if func_name.startswith(("get_", "fetch_", "load_", "read_")):
        return "Any"
    elif func_name.startswith(("is_", "has_", "can_", "should_")):
        return "bool"
    elif func_name.startswith(("create_", "build_", "make_")):
        return "Any"
    elif func_name.startswith("list_") or func_name.endswith("_list"):
        return "List[Any]"
    elif func_name.startswith("dict_") or func_name.endswith("_dict"):
        return "Dict[str, Any]"
    elif func_name in ("__init__", "__enter__", "__exit__"):
        return "None"
    
    # Check function body for return statements
    try:
        for i in range(line_idx + 1, min(line_idx + 20, len(lines))):
            if "return" in lines[i]:
                if "return None" in lines[i] or "return" == lines[i].strip():
                    return "None"
                elif "return True" in lines[i] or "return False" in lines[i]:
                    return "bool"
                elif "return []" in lines[i] or "return list" in lines[i]:
                    return "List[Any]"
                elif "return {}" in lines[i] or "return dict" in lines[i]:
                    return "Dict[str, Any]"
                elif "return ''" in lines[i] or "return str" in lines[i]:
                    return "str"
                elif "return 0" in lines[i] or "return int" in lines[i]:
                    return "int"
    except:
        pass
    
    return "Any"


def main() -> None:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Add type annotations to Python files")
    parser.add_argument("--directory", "-d", default="src", help="Directory to scan")
    parser.add_argument("--file", "-f", help="Specific file to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--fix", action="store_true", help="Actually add annotations")
    
    args = parser.parse_args()
    
    if args.file:
        files_to_check = [Path(args.file)]
    else:
        directory = Path(args.directory)
        results = find_files_without_annotations(directory)
        files_to_check = [path for path, _ in results]
    
    if args.dry_run:
        print("Files missing type annotations:")
        for file_path in files_to_check[:20]:  # Limit output
            print(f"  {file_path}")
        print(f"\nTotal: {len(files_to_check)} files")
    elif args.fix:
        print("Adding type annotations...")
        fixed = 0
        for file_path in files_to_check:
            if add_basic_annotations(file_path):
                print(f"  Fixed: {file_path}")
                fixed += 1
        print(f"\nFixed {fixed} files")
    else:
        print("Use --dry-run to see files or --fix to add annotations")


if __name__ == "__main__":
    main()


