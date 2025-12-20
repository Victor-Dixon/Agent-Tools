import logging
logger = logging.getLogger(__name__)
"""
Manager Migration Codemod - Phase-2 Manager Consolidation
=========================================================

Zero-dep codemod to migrate legacy manager imports/usages.
- Dry-run by default; print unified diffs
- --write to apply in-place
- Uses simple token/line replace (safe subset) — review diff before commit

Author: Agent-3 (Infrastructure & DevOps Specialist)
License: MIT
"""
from __future__ import annotations
import argparse
import difflib
import json
import os
import sys


def load_map(path: str) ->dict:
    """Load migration mapping from JSON file."""
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.info(f'[codemod] Error loading mapping file {path}: {e}')
        return {}


def transform(text: str, mapping: dict) ->str:
    """Transform text using mapping rules."""
    result = text
    for old_pattern, new_pattern in mapping.items():
        result = result.replace(old_pattern, new_pattern)
    return result


def iter_python_files(root: str):
    """Iterate over Python files in directory tree."""
    for dirpath, dirnames, filenames in os.walk(root):
        if any(part in {'.git', 'venv', '.venv', 'node_modules', 'dist',
            'build', '__pycache__'} for part in dirpath.split(os.sep)):
            continue
        for filename in filenames:
            if filename.endswith('.py'):
                yield os.path.join(dirpath, filename)


def main():
    """Main codemod function."""
    parser = argparse.ArgumentParser(description=
        'Migrate legacy managers to core managers')
    parser.add_argument('--root', default='.', help='Root directory to process'
        )
    parser.add_argument('--map', default=
        'runtime/migrations/manager-map.json', help=
        'Path to migration mapping file')
    parser.add_argument('--write', action='store_true', help=
        'Apply changes (default is dry-run)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output'
        )
    args = parser.parse_args()
    mapping = load_map(args.map)
    if not mapping:
        logger.info(f'[codemod] No mapping rules found in {args.map}')
        return 1
    if args.verbose:
        logger.info(f'[codemod] Loaded {len(mapping)} mapping rules')
    modified_files = 0
    total_files = 0
    for file_path in iter_python_files(args.root):
        total_files += 1
        try:
            with open(file_path, encoding='utf-8') as f:
                original_content = f.read()
            transformed_content = transform(original_content, mapping)
            if original_content != transformed_content:
                modified_files += 1
                if args.write:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(transformed_content)
                    logger.info(f'[codemod] Updated: {file_path}')
                else:
                    logger.info(f'[codemod] Would modify: {file_path}')
                    diff = difflib.unified_diff(original_content.splitlines
                        (True), transformed_content.splitlines(True),
                        fromfile=file_path, tofile=file_path)
                    sys.stdout.writelines(diff)
                    logger.info('')
        except Exception as e:
            logger.info(f'[codemod] Error processing {file_path}: {e}')
            continue
    if args.write:
        logger.info(
            f'[codemod] Migration complete: {modified_files}/{total_files} files updated'
            )
        return 0
    else:
        logger.info(
            f'[codemod] Dry run complete: {modified_files}/{total_files} files would be modified'
            )
        if modified_files > 0:
            logger.info('[codemod] Run with --write to apply changes')
            return 2
        else:
            return 0


if __name__ == '__main__':
    sys.exit(main())
