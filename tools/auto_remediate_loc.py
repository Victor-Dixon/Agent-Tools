import logging
logger = logging.getLogger(__name__)
"""
Auto-Remediate LOC Violations
=============================

Scans for file/class/function LOC breaches and emits refactor TODOs + skeleton split modules.

Usage:
    python tools/auto_remediate_loc.py

Outputs:
    runtime/v2_refactor_plan.json - Detailed refactor plan
    runtime/refactor_suggestions.txt - Human-readable suggestions
"""
from __future__ import annotations
import ast
import json
from pathlib import Path
from typing import Dict, List, Any
MAX_FILE_LOC = 400
MAX_CLASS_LOC = 100
MAX_FUNCTION_LOC = 50
ROOT = Path('.')
EXCLUDE_PATTERNS = ['__pycache__', '.venv', 'node_modules', '.git', 'build',
    'dist', 'tests', '.pytest_cache', '.tox', '.coverage', 'htmlcov',
    '*.egg-info', '.mypy_cache']


def should_exclude(path: Path) ->bool:
    """Check if path should be excluded."""
    path_str = str(path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)


def count_lines(node: ast.AST) ->int:
    """Count lines for AST node."""
    if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
        return (node.end_lineno or 0) - (node.lineno or 0) + 1
    return 0


def analyze_file_loc(path: Path) ->Dict[str, Any]:
    """Analyze file for LOC violations."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.splitlines()
        file_loc = len(lines)
        if file_loc <= MAX_FILE_LOC:
            return None
        return {'type': 'file_loc', 'path': str(path), 'current_loc':
            file_loc, 'limit': MAX_FILE_LOC, 'excess': file_loc -
            MAX_FILE_LOC, 'severity': 'critical', 'suggestion':
            generate_file_split_suggestion(path, content)}
    except Exception as e:
        return {'type': 'error', 'path': str(path), 'error': str(e)}


def analyze_class_loc(path: Path, tree: ast.Module) ->List[Dict[str, Any]]:
    """Analyze classes for LOC violations."""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_loc = count_lines(node)
            if class_loc > MAX_CLASS_LOC:
                violations.append({'type': 'class_loc', 'path': str(path),
                    'class_name': node.name, 'current_loc': class_loc,
                    'limit': MAX_CLASS_LOC, 'excess': class_loc -
                    MAX_CLASS_LOC, 'severity': 'major', 'line_number': node
                    .lineno, 'suggestion': generate_class_split_suggestion(
                    path, node)})
    return violations


def analyze_function_loc(path: Path, tree: ast.Module) ->List[Dict[str, Any]]:
    """Analyze functions for LOC violations."""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_loc = count_lines(node)
            if func_loc > MAX_FUNCTION_LOC:
                violations.append({'type': 'function_loc', 'path': str(path
                    ), 'function_name': node.name, 'current_loc': func_loc,
                    'limit': MAX_FUNCTION_LOC, 'excess': func_loc -
                    MAX_FUNCTION_LOC, 'severity': 'minor', 'line_number':
                    node.lineno, 'suggestion':
                    generate_function_split_suggestion(path, node)})
    return violations


def generate_file_split_suggestion(path: Path, content: str) ->Dict[str, Any]:
    """Generate file splitting suggestion."""
    filename = path.stem
    dir_name = path.parent
    try:
        tree = ast.parse(content)
    except:
        return {'error': 'Cannot parse file for suggestions'}
    classes = []
    functions = []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if hasattr(node, 'names'):
                imports.extend([alias.name for alias in node.names])
            elif hasattr(node, 'module'):
                imports.append(node.module)
    return {'suggested_splits': [
        f"{filename}_core.py - Core classes: {', '.join(classes[:2])}",
        f"{filename}_utils.py - Utility functions: {', '.join(functions[:3])}",
        f'{filename}_types.py - Type definitions and imports'],
        'estimated_splits': max(2, len(classes) // 2), 'complexity_factors':
        {'classes': len(classes), 'functions': len(functions), 'imports':
        len(imports)}}


def generate_class_split_suggestion(path: Path, class_node: ast.ClassDef
    ) ->Dict[str, Any]:
    """Generate class splitting suggestion."""
    methods = []
    properties = []
    for node in ast.walk(class_node):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith('_'):
                continue
            methods.append(node.name)
        elif isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name
                ):
                properties.append(node.targets[0].id)
    return {'suggested_methods_split': [
        f"{class_node.name}Core - Core methods: {', '.join(methods[:5])}",
        f"{class_node.name}Utils - Utility methods: {', '.join(methods[5:10])}"
        ], 'properties_to_extract': properties, 'method_count': len(methods
        ), 'estimated_classes': max(1, len(methods) // 10)}


def generate_function_split_suggestion(path: Path, func_node: ast.FunctionDef
    ) ->Dict[str, Any]:
    """Generate function splitting suggestion."""
    return {'suggested_extracts': [
        f'Extract helper functions from {func_node.name}',
        f'Split into smaller functions with single responsibilities',
        f'Move complex logic to separate utility functions'],
        'estimated_functions': 2, 'complexity_indicators': ['nested_loops',
        'complex_conditionals', 'large_function']}


def generate_refactor_plan() ->Dict[str, Any]:
    """Generate complete refactor plan."""
    issues = []
    summary = {'files_analyzed': 0, 'syntax_errors': 0, 'file_violations':
        0, 'class_violations': 0, 'function_violations': 0,
        'total_violations': 0}
    logger.info('Scanning for LOC violations...')
    for py_file in ROOT.rglob('*.py'):
        if should_exclude(py_file):
            continue
        summary['files_analyzed'] += 1
        file_violation = analyze_file_loc(py_file)
        if file_violation:
            issues.append(file_violation)
            if file_violation['type'] != 'error':
                summary['file_violations'] += 1
            else:
                summary['syntax_errors'] += 1
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            class_violations = analyze_class_loc(py_file, tree)
            issues.extend(class_violations)
            summary['class_violations'] += len(class_violations)
            function_violations = analyze_function_loc(py_file, tree)
            issues.extend(function_violations)
            summary['function_violations'] += len(function_violations)
        except SyntaxError:
            summary['syntax_errors'] += 1
            issues.append({'type': 'syntax_error', 'path': str(py_file),
                'severity': 'critical'})
        except Exception as e:
            issues.append({'type': 'parse_error', 'path': str(py_file),
                'error': str(e), 'severity': 'critical'})
    summary['total_violations'] = len(issues)
    return {'summary': summary, 'issues': issues, 'generated_at': str(Path.
        cwd()), 'config': {'max_file_loc': MAX_FILE_LOC, 'max_class_loc':
        MAX_CLASS_LOC, 'max_function_loc': MAX_FUNCTION_LOC}}


def generate_text_report(plan: Dict[str, Any]) ->str:
    """Generate human-readable text report."""
    summary = plan['summary']
    report = []
    report.append('V2 LOC Refactor Plan')
    report.append('=' * 50)
    report.append('')
    report.append('SUMMARY:')
    report.append(f"Files analyzed: {summary['files_analyzed']}")
    report.append(f"Total violations: {summary['total_violations']}")
    report.append('')
    if summary['syntax_errors'] > 0:
        report.append(f"CRITICAL Syntax errors: {summary['syntax_errors']}")
    if summary['file_violations'] > 0:
        report.append(
            f"CRITICAL File LOC violations: {summary['file_violations']}")
    if summary['class_violations'] > 0:
        report.append(
            f"MAJOR Class LOC violations: {summary['class_violations']}")
    if summary['function_violations'] > 0:
        report.append(
            f"MINOR Function LOC violations: {summary['function_violations']}")
    report.append('')
    report.append('REFACTOR ACTIONS:')
    report.append('')
    for issue in plan['issues']:
        if issue['type'] == 'file_loc':
            report.append(f"FILE {issue['path']}:")
            report.append(
                f"  File: {issue['current_loc']} LOC (limit: {issue['limit']})"
                )
            report.append(f"  Excess: {issue['excess']} LOC")
            if 'suggestion' in issue and 'suggested_splits' in issue[
                'suggestion']:
                report.append('  Suggested splits:')
                for split in issue['suggestion']['suggested_splits']:
                    report.append(f'    - {split}')
            report.append('')
        elif issue['type'] == 'class_loc':
            report.append(f"CLASS {issue['path']}:{issue['line_number']}:")
            report.append(
                f"  Class '{issue['class_name']}': {issue['current_loc']} LOC (limit: {issue['limit']})"
                )
            report.append(f"  Excess: {issue['excess']} LOC")
            if 'suggestion' in issue and 'suggested_methods_split' in issue[
                'suggestion']:
                report.append('  Suggested splits:')
                for split in issue['suggestion']['suggested_methods_split']:
                    report.append(f'    - {split}')
            report.append('')
        elif issue['type'] == 'function_loc':
            report.append(f"FUNCTION {issue['path']}:{issue['line_number']}:")
            report.append(
                f"  Function '{issue['function_name']}': {issue['current_loc']} LOC (limit: {issue['limit']})"
                )
            report.append(f"  Excess: {issue['excess']} LOC")
            report.append('  Recommendation: Split into smaller functions')
            report.append('')
        elif issue['type'] in ['syntax_error', 'parse_error']:
            report.append(f"ERROR {issue['path']}:")
            report.append(f"  {issue.get('error', 'Parse error')}")
            report.append('')
    return '\n'.join(report)


def main():
    """Main entry point."""
    logger.info('🔧 Generating V2 LOC refactor plan...')
    plan = generate_refactor_plan()
    output_dir = Path('runtime')
    output_dir.mkdir(exist_ok=True)
    json_file = output_dir / 'v2_refactor_plan.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2)
    text_file = output_dir / 'refactor_suggestions.txt'
    text_report = generate_text_report(plan)
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text_report)
    summary = plan['summary']
    logger.info('\nREFACTOR PLAN GENERATED:')
    logger.info(f"Files analyzed: {summary['files_analyzed']}")
    logger.info(f"Total violations: {summary['total_violations']}")
    logger.info(f"Syntax errors: {summary['syntax_errors']}")
    logger.info(f"File LOC violations: {summary['file_violations']}")
    logger.info(f"Class LOC violations: {summary['class_violations']}")
    logger.info(f"Function LOC violations: {summary['function_violations']}")
    logger.info(f'\nJSON plan saved: {json_file}')
    logger.info(f'Text report saved: {text_file}')
    if summary['total_violations'] == 0:
        logger.info('SUCCESS No LOC violations found!')
    else:
        logger.info(
            f"WARNING {summary['total_violations']} violations require attention"
            )


if __name__ == '__main__':
    main()
