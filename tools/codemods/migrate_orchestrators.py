import logging
logger = logging.getLogger(__name__)
"""Zero-dep codemod to migrate legacy orchestrator imports/usages.

- Dry-run by default; print unified diffs
- --write to apply in-place
- Uses simple token/line replace (safe subset) — review diff before commit
"""
from __future__ import annotations
import argparse
import difflib
import json
import os
import sys
MAP = {}


def load_map(path: str) ->dict:
    try:
        return json.load(open(path, encoding='utf-8'))
    except Exception:
        return {}


def transform(text: str, m: dict) ->str:
    out = text
    for old, new in m.items():
        out = out.replace(old, new)
    return out


def iter_py(root: str):
    for d, _, files in os.walk(root):
        if any(part in {'.git', 'venv', '.venv', 'node_modules', 'dist',
            'build', '__pycache__'} for part in d.split(os.sep)):
            continue
        for f in files:
            if f.endswith('.py'):
                yield os.path.join(d, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--map', default='runtime/migrations/orchestrator-map.json'
        )
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    m = load_map(args.map)
    if not m:
        logger.info(f'[codemod] mapping file empty or missing: {args.map}')
        return 1
    rc = 0
    for p in iter_py(args.root):
        src = open(p, encoding='utf-8').read()
        dst = transform(src, m)
        if src != dst:
            if args.write:
                open(p, 'w', encoding='utf-8').write(dst)
                logger.info(f'[codemod] updated: {p}')
            else:
                diff = difflib.unified_diff(src.splitlines(True), dst.
                    splitlines(True), fromfile=p, tofile=p)
                sys.stdout.writelines(diff)
                rc = 2
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
