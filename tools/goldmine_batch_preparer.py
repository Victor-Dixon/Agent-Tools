#!/usr/bin/env python3
"""
Goldmine batch preparation helper.

Reads config/goldmine_batch_targets.json and emits
repo_safe_merge command templates plus cache reminders.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

CONFIG_PATH = Path("config/goldmine_batch_targets.json")


def load_config(path: Path = CONFIG_PATH) -> Dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Config file {path} missing. Create it before running this tool."
        )
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def ensure_cache(cache_root: Path) -> None:
    cache_root.mkdir(parents=True, exist_ok=True)


def format_command(target: Dict[str, str]) -> str:
    source_name = target["source_repo"].split("/")[-1]
    target_name = target["target_repo"].split("/")[-1]
    branch_name = target.get("branch_name") or f"goldmine-{target_name.lower()}"
    return (
        f"python tools/repo_safe_merge.py {target_name} {source_name} {branch_name}"
    )


def list_targets(targets: List[Dict[str, str]]) -> None:
    for target in targets:
        print(
            f"- {target['label']} | "
            f"{target['source_repo']} → {target['target_repo']} | "
            f"branch={target.get('branch_name', 'auto')} | "
            f"priority={target.get('priority', 'normal')}"
        )


def generate_plan(targets: List[Dict[str, str]]) -> str:
    lines = [
        "# Goldmine Batch Automation Plan",
        "",
        "Remember: ensure D:/Temp repo cache is clean before launching.",
        "",
    ]
    for target in targets:
        lines.append(f"## {target['label']}")
        lines.append(f"* Source: `{target['source_repo']}`")
        lines.append(f"* Target: `{target['target_repo']}`")
        lines.append(f"* Branch: `{target.get('branch_name', 'auto-generated')}`")
        lines.append(f"* Priority: {target.get('priority', 'normal')}")
        notes = target.get("notes")
        if notes:
            lines.append(f"* Notes: {notes}")
        lines.append("")
        lines.append("```bash")
        lines.append(format_command(target))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare automation commands for the upcoming goldmine batch."
    )
    parser.add_argument("--list", action="store_true", help="List configured targets")
    parser.add_argument(
        "--generate-commands",
        action="store_true",
        help="Print repo_safe_merge command templates",
    )
    parser.add_argument(
        "--output",
        help="Write detailed plan (Markdown) to the specified file",
    )
    args = parser.parse_args()

    config = load_config()
    cache_root = Path(config.get("cache_root", "D:/Temp/repo_cache"))
    ensure_cache(cache_root)

    targets = config.get("targets", [])
    if not targets:
        print("No targets defined in config/goldmine_batch_targets.json")
        return 0

    if args.list or (not args.generate_commands and not args.output):
        print("Configured goldmine targets:")
        list_targets(targets)

    if args.generate_commands:
        print("\nCommand templates:")
        for target in targets:
            print(format_command(target))

    if args.output:
        plan = generate_plan(targets)
        output_path = Path(args.output)
        output_path.write_text(plan, encoding="utf-8")
        print(f"Wrote plan to {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

