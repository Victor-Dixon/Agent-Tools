from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Authoritative cleanup auditor.

- Scans working tree (ignoring .git and common caches)
- Reports totals by type, duplicate groups (by SHA256), temp/versioned patterns
- Compares against last commit (if git available)
- Risk guards: abort if .py count < MIN_PY or drop > MAX_PY_DROP unless --force
- Emits JSON and Markdown reports under runtime/reports/
"""
import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
CONFIG_PATH = os.path.join('tools', 'audit_config.json')
AUDITIGNORE_PATH = '.auditignore'


def load_config():
    cfg = {}
    try:
        with open(CONFIG_PATH, encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception:
        pass
    return cfg


def load_ignores():
    pats = []
    try:
        with open(AUDITIGNORE_PATH, encoding='utf-8') as f:
            for ln in f:
                s = ln.strip()
                if s and not s.startswith('#'):
                    pats.append(s)
    except Exception:
        pass
    return pats


def path_ignored_by_patterns(path: str, pats: list[str]) ->bool:
    for p in pats:
        if fnmatch.fnmatch(path, p) or p in path:
            return True
    return False


cfg = load_config()
IGNORE_DIRS = set(cfg.get('ignore_dirs', ['.git', '.venv', 'venv',
    'node_modules', '.mypy_cache', '__pycache__', '.pytest_cache',
    '.ruff_cache', '.cache', 'dist', 'build', '.idea', '.vscode']))
TEMP_PATTERNS = ['.*\\.tmp$', '.*~$', '^~.*', '.*\\.bak$', '.*\\.swp$',
    '.*\\.log$', '.*\\.DS_Store$', '.*\\.orig$']
VERSIONED_PATTERNS = ['.*[_\\-\\.]v\\d{1,4}(\\.\\d+)?\\.[A-Za-z0-9]+$',
    '.*copy\\s*\\(\\d+\\)\\.[A-Za-z0-9]+$']
RISK_MIN_PY = int(cfg.get('min_py', 10))
RISK_MAX_PY_DROP = float(cfg.get('max_py_drop', 0.8))


def is_ignored_dir(name: str) ->bool:
    return name in IGNORE_DIRS


def sha256_file(path: str) ->str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda : f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def list_files(root: str) ->list[str]:
    acc = []
    audit_ignores = load_ignores()
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if not is_ignored_dir(x)]
        for fn in files:
            fp = os.path.join(d, fn)
            rel = os.path.relpath(fp, root)
            if path_ignored_by_patterns(rel, audit_ignores):
                continue
            acc.append(fp)
    return acc


def ext_of(path: str) ->str:
    _, ext = os.path.splitext(path)
    return (ext or '').lower()


def match_any(patterns: list[str], path: str) ->bool:
    b = os.path.basename(path)
    for p in patterns:
        if re.match(p, b, re.IGNORECASE):
            return True
    return False


def git_available() ->bool:
    try:
        subprocess.check_output(['git', 'rev-parse',
            '--is-inside-work-tree'], stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def git_head_stats() ->dict[str, list[str]]:
    """Returns changed/added/deleted vs HEAD (working tree)."""
    stats = {'A': [], 'M': [], 'D': [], 'R': [], '?': []}
    try:
        out = subprocess.check_output(['git', 'status', '--porcelain'],
            text=True)
        for line in out.splitlines():
            code = line[:2].strip()
            path = line[3:].strip()
            if code.startswith('D'):
                stats['D'].append(path)
            elif code.startswith('A'):
                stats['A'].append(path)
            elif code.startswith('M'):
                stats['M'].append(path)
            elif code.startswith('R'):
                stats['R'].append(path)
            elif code.startswith('?'):
                stats['?'].append(path)
    except Exception:
        pass
    return stats


def percent(n: int, d: int) ->float:
    return 100.0 * n / d if d else 0.0


def main():
    ap = argparse.ArgumentParser(description='Authoritative cleanup auditor')
    ap.add_argument('--repo', default='.', help='Repo root')
    ap.add_argument('--force', action='store_true', help='Override loss guards'
        )
    ap.add_argument('--dup-limit', type=int, default=int(cfg.get(
        'dup_limit', 50)), help='Max files to hash for duplicates (0=no limit)'
        )
    args = ap.parse_args()
    root = os.path.abspath(args.repo)
    os.chdir(root)
    ts = time.strftime('%Y%m%d-%H%M%S')
    outdir = os.path.join('runtime', 'reports')
    os.makedirs(outdir, exist_ok=True)
    json_path = os.path.join(outdir, f'cleanup_{ts}.json')
    md_path = os.path.join(outdir, f'cleanup_{ts}.md')
    files = list_files('.')
    total = len(files)
    by_ext: dict[str, int] = defaultdict(int)
    temps, versioned = [], []
    py_files = []
    for p in files:
        e = ext_of(p)
        by_ext[e] += 1
        if e == '.py':
            py_files.append(p)
        if match_any(TEMP_PATTERNS, p):
            temps.append(p)
        if match_any(VERSIONED_PATTERNS, p):
            versioned.append(p)
    dup_sample = files if args.dup_limit == 0 else files[:args.dup_limit]
    hashes: dict[str, list[str]] = defaultdict(list)
    for p in dup_sample:
        try:
            h = sha256_file(p)
            hashes[h].append(p)
        except Exception:
            continue
    dup_groups = [v for v in hashes.values() if len(v) > 1]
    dup_count = sum(len(g) for g in dup_groups)
    git_stats = git_head_stats() if git_available() else None
    py_count = len(py_files)
    risk_flag = False
    risk_msgs: list[str] = []
    if py_count < RISK_MIN_PY:
        risk_flag = True
        risk_msgs.append(
            f'.py count dangerously low: {py_count} < {RISK_MIN_PY}')
    py_head = None
    if git_available():
        try:
            out = subprocess.check_output(['git', 'ls-files', '*.py'], text
                =True)
            py_head = len([ln for ln in out.splitlines() if ln.strip()])
            if py_head and py_count < (1.0 - RISK_MAX_PY_DROP) * py_head:
                risk_flag = True
                drop = 1.0 - py_count / max(py_head, 1)
                risk_msgs.append(
                    f'.py drop {drop:.1%} exceeds {int(RISK_MAX_PY_DROP * 100)}% threshold (HEAD={py_head}, now={py_count})'
                    )
        except Exception:
            pass
    report = {'timestamp': ts, 'root': root, 'totals': {'files': total,
        'by_ext': dict(sorted(by_ext.items(), key=lambda kv: (-kv[1], kv[0]
        ))), 'py_files': py_count}, 'patterns': {'temporary_files': temps,
        'versioned_files': versioned}, 'duplicates': {'groups': dup_groups,
        'file_count_in_groups': dup_count, 'sampled': args.dup_limit != 0,
        'sample_size': len(dup_sample)}, 'git': git_stats, 'risk': {
        'flagged': risk_flag, 'messages': risk_msgs, 'min_py': RISK_MIN_PY,
        'max_py_drop': RISK_MAX_PY_DROP, 'py_head': py_head}, 'notes': {
        'ignore_dirs': sorted(IGNORE_DIRS), 'temp_patterns': TEMP_PATTERNS,
        'versioned_patterns': VERSIONED_PATTERNS}}
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    def top_exts(n=10):
        items = sorted(by_ext.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
        return '\n'.join(f"- `{ext or '(no ext)'}`: {cnt}" for ext, cnt in
            items)
    md = []
    md.append(f'# Cleanup Audit — {ts}')
    md.append(f'- Root: `{root}`')
    md.append(f'- Total files: **{total}**  |  Python files: **{py_count}**')
    if git_stats is not None:
        a, m, d = len(git_stats['A']), len(git_stats['M']), len(git_stats['D'])
        md.append(
            f'- Working tree vs HEAD → Added: **{a}**, Modified: **{m}**, Deleted: **{d}**'
            )
    md.append('\n## Top File Types')
    md.append(top_exts())
    md.append('\n## Pattern Matches')
    md.append(f'- Temporary files: **{len(temps)}**')
    md.append(f'- Versioned files: **{len(versioned)}**')
    md.append('\n## Duplicate Summary')
    md.append(
        f'- Groups: **{len(dup_groups)}**, Files in groups: **{dup_count}** (sample={len(dup_sample)})'
        )
    if report['risk']['flagged']:
        md.append('\n## ⚠️ Risk Alerts')
        for msg in risk_msgs:
            md.append(f'- {msg}')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    if risk_flag and not args.force:
        logger.info(f'❌ Loss guard triggered. See {md_path}')
        return 1
    if risk_flag and args.force:
        logger.info(f'⚠️ Proceeding under --force. See {md_path}')
        logger.info(json_path)
        return 2
    logger.info(f'✅ Audit OK → {md_path}')
    logger.info(json_path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
