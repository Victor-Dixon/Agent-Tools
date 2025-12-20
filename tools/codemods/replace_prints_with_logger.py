"""
Codemod: Replace print() with logging
=====================================

Automatically replaces print() statements with proper logging calls.
Skips test files and handles various print() patterns.

Usage:
    python tools/codemods/replace_prints_with_logger.py
"""
from __future__ import annotations
import ast
import astor
from pathlib import Path


def should_skip_file(path: Path) ->bool:
    """Check if file should be skipped."""
    path_str = str(path)
    if 'test' in path_str.lower() or path_str.endswith('conftest.py'):
        return True
    skip_dirs = ['__pycache__', '.venv', 'node_modules', '.git',
        '.pytest_cache']
    if any(skip_dir in path_str for skip_dir in skip_dirs):
        return True
    return False


def transform_file(file_path: Path) ->bool:
    """
    Transform print() statements to logging in a single file.
    Returns True if file was modified, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
        changed = False


        class PrintTransformer(ast.NodeTransformer):

            def visit_Call(self, node):
                nonlocal changed
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    changed = True
                    if node.args:
                        if len(node.args) == 1:
                            new_node = ast.parse('logger.info()').body[0].value
                            new_node.args = node.args
                        else:
                            format_string = ''
                            format_args = []
                            for i, arg in enumerate(node.args):
                                if i > 0:
                                    format_string += ' '
                                if isinstance(arg, ast.Str):
                                    format_string += arg.s
                                elif isinstance(arg, ast.Name):
                                    format_string += '{' + arg.id + '}'
                                    format_args.append(arg)
                                else:
                                    format_string += '{}'
                                    format_args.append(arg)
                            if format_args:
                                fstring = ast.JoinedStr()
                                fstring.values = [ast.Constant(value=
                                    format_string)]
                                new_node = ast.parse('logger.info()').body[0
                                    ].value
                                new_node.args = [ast.Str(s=format_string)]
                            else:
                                new_node = ast.parse('logger.info()').body[0
                                    ].value
                                new_node.args = [ast.Str(s=format_string)]
                    else:
                        new_node = ast.parse('logger.info("")').body[0].value
                    return new_node
                return self.generic_visit(node)
        transformer = PrintTransformer()
        new_tree = transformer.visit(tree)
        if changed:
            ast.fix_missing_locations(new_tree)
            if 'import logging' not in source:
                if 'logger =' not in source and 'logger=' not in source:
                    logging_setup = (
                        'import logging\nlogger = logging.getLogger(__name__)\n'
                        )
                    new_source = logging_setup + astor.to_source(new_tree)
                else:
                    new_source = astor.to_source(new_tree)
            elif 'logger =' not in source and 'logger=' not in source:
                new_source = (
                    'import logging\nlogger = logging.getLogger(__name__)\n' +
                    astor.to_source(new_tree))
            else:
                new_source = astor.to_source(new_tree)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_source)
            return True
    except Exception as e:
        logger.info(f'[ERROR] {file_path}: {e}')
        return False
    return False


def main():
    """Main entry point."""
    logger.info('🔧 Replacing print() statements with logging...')
    root_dir = Path('.')
    files_processed = 0
    files_modified = 0
    total_prints_found = 0
    for py_file in root_dir.rglob('*.py'):
        if should_skip_file(py_file):
            continue
        files_processed += 1
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print_count = content.count('print(')
            if print_count == 0:
                continue
            total_prints_found += print_count
            logger.info(
                f'FILE {py_file}: Found {print_count} print() statement(s)')
            if transform_file(py_file):
                files_modified += 1
                logger.info(f'SUCCESS {py_file}: Transformed')
        except Exception as e:
            logger.info(f'[ERROR] {py_file}: {e}')
    logger.info('\nTRANSFORMATION SUMMARY:')
    logger.info(f'Files processed: {files_processed}')
    logger.info(f'Files modified: {files_modified}')
    logger.info(f'Total print() statements found: {total_prints_found}')
    if files_modified == 0:
        logger.info('SUCCESS No print() statements found in non-test files!')
    else:
        logger.info(
            f'SUCCESS Successfully transformed {files_modified} file(s)')


if __name__ == '__main__':
    main()
