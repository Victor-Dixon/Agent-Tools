#!/usr/bin/env python3
"""
Comment-Code Mismatch Analyzer
===============================

Identifies cases where code doesn't match comments, docstrings, or documentation.

Checks for:
1. Function signatures that don't match docstrings
2. Parameter mismatches between docstrings and actual parameters
3. Return type mismatches
4. Class attributes mentioned in docstrings but not in code
5. Method names in comments that don't exist
6. Outdated comments describing removed/changed functionality
7. Type hints that don't match docstrings

Author: Agent-4 (Captain)
Date: 2025-12-12
Priority: HIGH - Code quality improvement
"""

import ast
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Mismatch:
    """Represents a comment-code mismatch."""
    file_path: str
    line_number: int
    mismatch_type: str
    description: str
    code_snippet: Optional[str] = None
    comment_snippet: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical


class CommentCodeAnalyzer:
    """Analyzes code for comment-code mismatches."""
    
    def __init__(self, workspace_root: Path):
        """Initialize analyzer."""
        self.workspace_root = workspace_root
        self.mismatches: List[Mismatch] = []
        self.exclude_patterns = {
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "venv",
            "env",
            "build",
            "dist",
            ".pytest_cache",
            "htmlcov",
            ".coverage"
        }
    
    def analyze_file(self, file_path: Path) -> List[Mismatch]:
        """Analyze a single Python file for mismatches."""
        mismatches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                logger.warning(f"Syntax error in {file_path}: {e}")
                return mismatches
            
            # Get all lines for context
            lines = content.split('\n')
            
            # Check function/docstring mismatches
            mismatches.extend(self._check_function_docstring_mismatches(
                tree, lines, file_path
            ))
            
            # Check class/docstring mismatches
            mismatches.extend(self._check_class_docstring_mismatches(
                tree, lines, file_path
            ))
            
            # Check inline comment mismatches
            mismatches.extend(self._check_inline_comment_mismatches(
                lines, file_path
            ))
            
            # Check type hint mismatches
            mismatches.extend(self._check_type_hint_mismatches(
                tree, lines, file_path
            ))
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
        
        return mismatches
    
    def _check_function_docstring_mismatches(
        self,
        tree: ast.AST,
        lines: List[str],
        file_path: Path
    ) -> List[Mismatch]:
        """Check for mismatches between function signatures and docstrings."""
        mismatches = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                docstring = ast.get_docstring(node)
                
                if not docstring:
                    continue
                
                # Get function parameters
                params = [arg.arg for arg in node.args.args]
                # Remove 'self' and 'cls' for method analysis
                params_clean = [p for p in params if p not in ('self', 'cls')]
                
                # Check for parameter mentions in docstring
                param_pattern = r'(\w+)\s*[:\(]'
                docstring_params = re.findall(param_pattern, docstring)
                
                # IMPROVEMENT 2: Docstring section detection
                # Recognize docstring sections (Args:, Returns:, Raises:, etc.)
                # and don't treat them as parameters
                docstring_sections = {'Args', 'Arguments', 'Parameters', 'Returns', 
                                     'Return', 'Raises', 'Yields', 'Note', 'Example', 
                                     'Examples', 'See Also', 'Warning', 'Warnings'}
                
                # Check for Args: section
                args_section = re.search(r'Args?:?\s*\n(.*?)(?=\n\s*(?:Returns?|Raises?|Yields?|Note|Example|See|Warning|\w+):|$)', 
                                        docstring, re.DOTALL | re.IGNORECASE)
                if args_section:
                    args_text = args_section.group(1)
                    # Extract parameter names from Args section
                    for line in args_text.split('\n'):
                        if ':' in line:
                            param_name = line.strip().split(':')[0].strip()
                            # Skip if it's a docstring section header, not a parameter
                            if param_name in docstring_sections:
                                continue
                            if param_name and param_name not in params_clean:
                                # Parameter mentioned in docstring but not in signature
                                mismatches.append(Mismatch(
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    mismatch_type="parameter_missing",
                                    description=(
                                        f"Function '{func_name}' docstring mentions "
                                        f"parameter '{param_name}' but it's not in "
                                        f"function signature"
                                    ),
                                    code_snippet=f"def {func_name}({', '.join(params)})",
                                    comment_snippet=line.strip(),
                                    severity="high"
                                ))
                
                # IMPROVEMENT 2: Improved Returns: section detection
                # Better regex to stop at next docstring section
                returns_section = re.search(r'Returns?:?\s*\n(.*?)(?=\n\s*(?:Args?|Raises?|Yields?|Note|Example|See|Warning|\w+):|$)', 
                                           docstring, re.DOTALL | re.IGNORECASE)
                if returns_section:
                    # IMPROVEMENT 3: Enhanced context-aware analysis using AST
                    # Check if function actually returns something (more thorough)
                    # Look for return statements in all code paths
                    has_return = False
                    returns_text = returns_section.group(1).strip().lower()
                    
                    # Check for explicit return statements
                    for n in ast.walk(node):
                        if isinstance(n, ast.Return):
                            has_return = True
                            break
                    
                    # Check for generator functions (yield statements)
                    has_yield = any(
                        isinstance(n, ast.Yield) or isinstance(n, ast.YieldFrom)
                        for n in ast.walk(node)
                    )
                    
                    # Check if Returns section explicitly says None or nothing
                    returns_none = (
                        'none' in returns_text or 
                        'nothing' in returns_text or
                        'void' in returns_text or
                        returns_text.strip() == ''
                    )
                    
                    # Only flag if:
                    # 1. Returns section describes a value (not None/nothing)
                    # 2. Function has no return statement
                    # 3. Function is not a generator (yield would be different)
                    if not has_return and not has_yield and not returns_none:
                        # Check if it's a property or setter (these don't need returns)
                        is_property = any(
                            isinstance(d, ast.Name) and d.id == 'property'
                            for d in node.decorator_list
                        )
                        if not is_property:
                            mismatches.append(Mismatch(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                mismatch_type="return_mismatch",
                                description=(
                                    f"Function '{func_name}' docstring describes return "
                                    f"value but function has no return statement"
                                ),
                                code_snippet=f"def {func_name}(...)",
                                comment_snippet=returns_section.group(1).strip()[:100],
                                severity="medium"
                            ))
        
        return mismatches
    
    def _check_class_docstring_mismatches(
        self,
        tree: ast.AST,
        lines: List[str],
        file_path: Path
    ) -> List[Mismatch]:
        """Check for mismatches between class docstrings and implementation."""
        mismatches = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                docstring = ast.get_docstring(node)
                
                if not docstring:
                    continue
                
                # Get class methods
                method_names = {
                    n.name for n in node.body 
                    if isinstance(n, ast.FunctionDef)
                }
                
                # Check for method mentions in docstring
                method_pattern = r'(\w+)\s*\(\)'
                docstring_methods = re.findall(method_pattern, docstring)
                
                for method_name in docstring_methods:
                    if method_name not in method_names and method_name != class_name:
                        mismatches.append(Mismatch(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            mismatch_type="method_missing",
                            description=(
                                f"Class '{class_name}' docstring mentions method "
                                f"'{method_name}()' but method doesn't exist"
                            ),
                            code_snippet=f"class {class_name}",
                            comment_snippet=f"Method: {method_name}()",
                            severity="high"
                        ))
        
        return mismatches
    
    def _check_inline_comment_mismatches(
        self,
        lines: List[str],
        file_path: Path
    ) -> List[Mismatch]:
        """Check for inline comments that don't match code.
        
        IMPROVEMENT: Multi-line return detection - checks lines i+1 through i+5
        for return statements when comment mentions "return", using AST for context.
        """
        mismatches = []
        
        # Parse AST for context-aware analysis
        try:
            content = '\n'.join(lines)
            tree = ast.parse(content)
            # Build line-to-function mapping
            line_to_func = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for line_num in range(node.lineno, node.end_lineno + 1):
                        line_to_func[line_num] = node
        except SyntaxError:
            tree = None
            line_to_func = {}
        
        for i, line in enumerate(lines, 1):
            # Skip docstrings
            if '"""' in line or "'''" in line:
                continue
            
            # Check for TODO/FIXME that might indicate outdated comments
            if re.search(r'(TODO|FIXME|XXX|HACK).*comment', line, re.I):
                mismatches.append(Mismatch(
                    file_path=str(file_path),
                    line_number=i,
                    mismatch_type="outdated_comment_marker",
                    description=f"Line contains TODO/FIXME about comments: {line.strip()[:80]}",
                    code_snippet=line.strip(),
                    severity="low"
                ))
            
            # IMPROVEMENT 1: Enhanced multi-line return detection with AST context
            # Check if comment mentions "return" and look for return statement
            # in next 5 lines (not just next line), using AST for accuracy
            comment_text = line.split('#', 1)[1] if '#' in line else ''
            if comment_text and re.search(r'\breturn\b', comment_text, re.I):
                # Skip if we're inside a docstring or string literal
                if tree and i in line_to_func:
                    func_node = line_to_func[i]
                    # Check if this line is within the function's docstring
                    if func_node.body and isinstance(func_node.body[0], ast.Expr):
                        docstring_node = func_node.body[0]
                        if isinstance(docstring_node.value, (ast.Str, ast.Constant)):
                            docstring_end = docstring_node.end_lineno if hasattr(docstring_node, 'end_lineno') else docstring_node.lineno
                            if i <= docstring_end:
                                continue  # Skip docstring lines
                
                # Look for return statement in next 5 lines using AST
                found_return = False
                
                # First try AST-based detection (more accurate)
                if tree and i in line_to_func:
                    func_node = line_to_func[i]
                    # Check if there's a return statement in this function after line i
                    for node in ast.walk(func_node):
                        if isinstance(node, ast.Return):
                            if node.lineno > i and node.lineno <= i + 5:
                                found_return = True
                                break
                
                # Fallback to regex if AST didn't find it
                if not found_return:
                    for j in range(i + 1, min(i + 6, len(lines) + 1)):
                        if j > len(lines):
                            break
                        check_line = lines[j - 1] if j > 0 else ''
                        # Check if line contains return statement (not in comment)
                        code_part = check_line.split('#')[0] if '#' in check_line else check_line
                        if re.search(r'^\s*return\b', code_part):
                            found_return = True
                            break
                
                # Only flag if comment says "return" but no return found in next 5 lines
                # AND we're in a context where return would be expected (inside function)
                if not found_return and tree and i in line_to_func:
                    # Lower severity - could be describing function behavior, not this line
                    mismatches.append(Mismatch(
                        file_path=str(file_path),
                        line_number=i,
                        mismatch_type="return_comment_mismatch",
                        description=(
                            f"Comment mentions 'return' but no return statement found "
                            f"in next 5 lines (may be describing function behavior)"
                        ),
                        code_snippet=line.strip()[:100],
                        severity="low"
                    ))
            
            # Check for function calls in comments that might not exist
            comment_match = re.search(r'#.*?(\w+)\s*\(', line)
            if comment_match:
                func_name = comment_match.group(1)
                # This is a simple check - could be enhanced
                # to verify function actually exists
        
        return mismatches
    
    def _check_type_hint_mismatches(
        self,
        tree: ast.AST,
        lines: List[str],
        file_path: Path
    ) -> List[Mismatch]:
        """Check for mismatches between type hints and docstrings."""
        mismatches = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                docstring = ast.get_docstring(node)
                
                if not docstring:
                    continue
                
                # Check for type hints in function signature
                has_type_hints = any(
                    arg.annotation is not None 
                    for arg in node.args.args
                )
                
                # Check for return type hint
                return_type_hint = node.returns is not None
                
                # Check if docstring mentions types
                type_pattern = r':\s*(\w+|List\[|Dict\[|Optional\[)'
                docstring_types = re.findall(type_pattern, docstring)
                
                if docstring_types and not has_type_hints and not return_type_hint:
                    # Docstring has type info but no type hints
                    mismatches.append(Mismatch(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        mismatch_type="type_hint_missing",
                        description=(
                            f"Function '{func_name}' docstring contains type "
                            f"information but function has no type hints"
                        ),
                        code_snippet=f"def {func_name}(...)",
                        comment_snippet=f"Types mentioned: {', '.join(docstring_types[:3])}",
                        severity="medium"
                    ))
        
        return mismatches
    
    def analyze_directory(self, directory: Path) -> List[Mismatch]:
        """Analyze all Python files in a directory."""
        all_mismatches = []
        
        for py_file in directory.rglob("*.py"):
            # Skip excluded patterns
            if any(exclude in str(py_file) for exclude in self.exclude_patterns):
                continue
            
            logger.info(f"Analyzing {py_file}")
            mismatches = self.analyze_file(py_file)
            all_mismatches.extend(mismatches)
        
        return all_mismatches
    
    def generate_report(self, mismatches: List[Mismatch]) -> str:
        """Generate a human-readable report."""
        if not mismatches:
            return "✅ No comment-code mismatches found!"
        
        # Group by severity
        by_severity = defaultdict(list)
        for mismatch in mismatches:
            by_severity[mismatch.severity].append(mismatch)
        
        report = []
        report.append("=" * 80)
        report.append("COMMENT-CODE MISMATCH ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nTotal Mismatches Found: {len(mismatches)}")
        report.append(f"  Critical: {len(by_severity.get('critical', []))}")
        report.append(f"  High: {len(by_severity.get('high', []))}")
        report.append(f"  Medium: {len(by_severity.get('medium', []))}")
        report.append(f"  Low: {len(by_severity.get('low', []))}")
        report.append("")
        
        # Report by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity not in by_severity:
                continue
            
            report.append(f"\n{'=' * 80}")
            report.append(f"{severity.upper()} SEVERITY MISMATCHES ({len(by_severity[severity])})")
            report.append(f"{'=' * 80}\n")
            
            for mismatch in by_severity[severity]:
                report.append(f"File: {mismatch.file_path}:{mismatch.line_number}")
                report.append(f"Type: {mismatch.mismatch_type}")
                report.append(f"Description: {mismatch.description}")
                if mismatch.code_snippet:
                    report.append(f"Code: {mismatch.code_snippet[:100]}")
                if mismatch.comment_snippet:
                    report.append(f"Comment: {mismatch.comment_snippet[:100]}")
                report.append("")
        
        return "\n".join(report)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze code for comment-code mismatches"
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="src",
        help="Directory to analyze (default: src)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for report (default: stdout)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Analyze single file instead of directory"
    )
    
    args = parser.parse_args()
    
    workspace_root = Path(".")
    analyzer = CommentCodeAnalyzer(workspace_root)
    
    if args.file:
        mismatches = analyzer.analyze_file(Path(args.file))
    else:
        target_dir = workspace_root / args.directory
        mismatches = analyzer.analyze_directory(target_dir)
    
    report = analyzer.generate_report(mismatches)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()

