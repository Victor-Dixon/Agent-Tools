#!/usr/bin/env python3
"""
Documentation Cleanup Tool - V2 COMPLIANT REFACTORED
====================================================

⚠️ REFACTORED: cleanup_documentation.py was 448 lines.
Split into 3 V2-compliant modules:
  - cleanup_documentation_reference_scanner.py (124 lines)
  - cleanup_documentation_deduplicator.py (117 lines)
  - cleanup_documentation_refactored.py (289 lines)

Archive-first documentation cleanup with safety guards.

Refactored: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-10-11
License: MIT
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from cleanup_documentation_deduplicator import DocumentationDeduplicator
from cleanup_documentation_reference_scanner import ReferenceScanner


class DocumentationCleanup:
    """Archive-first documentation cleanup with safety guards."""

    # Preserve allowlist - canonical docs
    PRESERVE_ALLOWLIST = {
        "README.md",
        "AGENTS.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "CHANGELOG.md",
        "ROADMAP.md",
    }

    # Preserve patterns
    PRESERVE_PATTERNS = [
        r"^docs/handbook/",
        r"^docs/specs/",
        r"^\.github/",
    ]

    # C2: Ephemeral naming patterns
    EPHEMERAL_PATTERN = re.compile(
        r"(outdated|temp|tmp|backup|bak|old|deprecated|"
        r"consolidation_|swarm_|survey_|notes_|scratch|playground)",
        re.IGNORECASE,
    )

    # Exclude patterns
    EXCLUDE_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".archive"}

    # Documentation extensions
    DOC_EXTENSIONS = {".md", ".rst", ".txt"}

    def __init__(self, repo_root: Path, dry_run: bool = True, interactive: bool = False):
        """Initialize cleanup tool."""
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.interactive = interactive
        self.timestamp = datetime.now().strftime("%Y%m%d")
        self.archive_dir = repo_root / ".archive" / f"docs-{self.timestamp}"
        self.tmp_dir = Path(tempfile.gettempdir())

        # Results tracking
        self.all_docs: list[Path] = []
        self.candidates: dict[str, list[Path]] = defaultdict(list)
        self.referenced_files: set[Path] = set()
        self.archive_set: list[Path] = []

        # Initialize modules
        self.ref_scanner = ReferenceScanner(repo_root)
        self.deduplicator = DocumentationDeduplicator(repo_root)

    def run(self) -> None:
        """Execute the cleanup process."""
        print("=" * 70)
        print("DOCUMENTATION CLEANUP - ARCHIVE-FIRST POLICY")
        print("=" * 70)
        print(f"Mode: {'DRY-RUN' if self.dry_run else 'EXECUTE'}")
        print(f"Repository: {self.repo_root}")
        print(f"Archive target: {self.archive_dir}")
        print()

        # Phase 1: Scan files
        print("[1/7] Scanning documentation files...")
        self.scan_documentation_files()
        self._write_list(self.tmp_dir / "docs_scan_all.txt", self.all_docs)
        print(f"  Found {len(self.all_docs)} documentation files")

        # Phase 2: Apply criteria
        print("\n[2/7] Applying selection criteria (C2, C4, C5)...")
        self.apply_criteria()
        all_candidates = self._flatten_candidates()
        self._write_list(self.tmp_dir / "docs_candidates_raw.txt", all_candidates)
        print(f"  C2 (Ephemeral): {len(self.candidates['C2'])} files")
        print(f"  C4 (Legacy archive): {len(self.candidates['C4'])} files")
        print(f"  C5 (Agent chatter): {len(self.candidates['C5'])} files")
        print(f"  Total candidates: {len(all_candidates)} files")

        # Phase 3: Preserve allowlist
        print("\n[3/7] Applying preserve allowlist...")
        filtered_candidates = self.apply_preserve_allowlist(all_candidates)
        self._write_list(self.tmp_dir / "docs_candidates.txt", filtered_candidates)
        print(f"  After allowlist: {len(filtered_candidates)} files")

        # Phase 4: Reference guard
        print("\n[4/7] Applying reference guard (C1)...")
        self.referenced_files = self.ref_scanner.scan_references(filtered_candidates)
        safe_candidates = [f for f in filtered_candidates if f not in self.referenced_files]
        self._write_list(self.tmp_dir / "docs_references.txt", list(self.referenced_files))
        print(f"  Referenced (skipped): {len(self.referenced_files)} files")
        print(f"  Safe candidates: {len(safe_candidates)} files")

        # Phase 5: Deduplication
        print("\n[5/7] Applying deduplication guard (C3)...")
        self.archive_set = self.deduplicator.apply_deduplication(safe_candidates)
        self._write_list(self.tmp_dir / "docs_archive_set.txt", self.archive_set)
        print(f"  Final archive set: {len(self.archive_set)} files")

        # Phase 6: Report
        print("\n[6/7] Generating cleanup report...")
        self.generate_report()

        # Phase 7: Execute
        if not self.dry_run:
            print("\n[7/7] Executing archive operation...")
            self.execute_archive()
            print("\n✅ Archive operation completed successfully")
        else:
            print("\n[7/7] Skipping archive (dry-run mode)")
            print(f"\n💡 To execute: python {__file__} --execute")

        print("\n" + "=" * 70)
        print("CLEANUP COMPLETE")
        print("=" * 70)

    def scan_documentation_files(self) -> None:
        """Scan repository for all documentation files."""
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                if file_path.suffix in self.DOC_EXTENSIONS:
                    rel_path = file_path.relative_to(self.repo_root)
                    self.all_docs.append(rel_path)

    def apply_criteria(self) -> None:
        """Apply criteria C2, C4, C5."""
        for doc in self.all_docs:
            doc_str = str(doc)
            # C2: Ephemeral
            if self.EPHEMERAL_PATTERN.search(doc.name):
                self.candidates["C2"].append(doc)
            # C4: Legacy archive
            if doc_str.startswith("docs/archive/"):
                self.candidates["C4"].append(doc)
            # C5: Agent chatter
            if self._is_agent_chatter(doc):
                self.candidates["C5"].append(doc)

    def _is_agent_chatter(self, doc: Path) -> bool:
        """Check if file is agent chatter."""
        doc_str = str(doc)
        patterns = [
            r"^Agent-[^/]+/.*\.md$",
            r"^agent[^/]+/.*\.md$",
            r"^runtime/.*\.md$",
            r"^agent_workspaces/.*\.md$",
            r"^thea_responses/.*\.md$",
        ]
        return any(re.match(p, doc_str, re.IGNORECASE) for p in patterns)

    def apply_preserve_allowlist(self, candidates: list[Path]) -> list[Path]:
        """Filter out preserved files."""
        filtered = []
        for doc in candidates:
            if doc.name in self.PRESERVE_ALLOWLIST:
                continue
            if any(re.match(p, str(doc)) for p in self.PRESERVE_PATTERNS):
                continue
            filtered.append(doc)
        return filtered

    def generate_report(self) -> None:
        """Generate summary report."""
        report = {
            "timestamp": self.timestamp,
            "mode": "dry-run" if self.dry_run else "execute",
            "summary": {
                "total_docs": len(self.all_docs),
                "candidates": {
                    "C2_ephemeral": len(self.candidates["C2"]),
                    "C4_legacy_archive": len(self.candidates["C4"]),
                    "C5_agent_chatter": len(self.candidates["C5"]),
                    "total": len(self._flatten_candidates()),
                },
                "referenced_skipped": len(self.referenced_files),
                "final_archive_set": len(self.archive_set),
            },
            "archive_set": [str(f) for f in sorted(self.archive_set)],
        }

        report_path = self.tmp_dir / f"docs_cleanup_report_{self.timestamp}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print("\n📊 CLEANUP SUMMARY")
        print(f"  Total docs scanned:      {report['summary']['total_docs']}")
        print(f"  Candidates identified:   {report['summary']['candidates']['total']}")
        print(f"    - C2 (Ephemeral):      {report['summary']['candidates']['C2_ephemeral']}")
        print(f"    - C4 (Legacy archive): {report['summary']['candidates']['C4_legacy_archive']}")
        print(f"    - C5 (Agent chatter):  {report['summary']['candidates']['C5_agent_chatter']}")
        print(f"  Referenced (skipped):    {report['summary']['referenced_skipped']}")
        print(f"  Final archive set:       {report['summary']['final_archive_set']}")
        print(f"\n📄 Report saved: {report_path}")

        if self.archive_set:
            print("\n📋 Sample files to archive (first 20):")
            for file in sorted(self.archive_set)[:20]:
                print(f"  - {file}")
            if len(self.archive_set) > 20:
                print(f"  ... and {len(self.archive_set) - 20} more")

    def execute_archive(self) -> None:
        """Execute archive operation."""
        if not self.archive_set:
            print("  No files to archive")
            return

        self.archive_dir.mkdir(parents=True, exist_ok=True)
        rollback_script = self.archive_dir / "rollback.sh"
        rollback_lines = ["#!/bin/bash", "set -euo pipefail", "# Rollback script\n"]

        archived_count = 0
        for file in self.archive_set:
            if self.interactive:
                response = input(f"Archive {file}? [y/N] ")
                if response.lower() != "y":
                    continue

            source = self.repo_root / file
            if not source.exists():
                print(f"  ⚠️  Skipping {file} (not found)")
                continue

            dest = self.archive_dir / file
            dest.parent.mkdir(parents=True, exist_ok=True)

            try:
                result = subprocess.run(
                    ["git", "mv", str(source), str(dest)],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    archived_count += 1
                    rollback_lines.append(f"git mv {dest} {source}")
                else:
                    shutil.move(str(source), str(dest))
                    archived_count += 1
                    rollback_lines.append(f"mv {dest} {source}")
            except Exception as e:
                print(f"  ❌ Error archiving {file}: {e}")
                continue

        with open(rollback_script, "w") as f:
            f.write("\n".join(rollback_lines))
        rollback_script.chmod(0o755)

        print(f"  ✅ Archived {archived_count} files")
        print(f"  📜 Rollback script: {rollback_script}")

        manifest = {
            "timestamp": self.timestamp,
            "archived_files": [str(f) for f in self.archive_set],
            "count": archived_count,
        }
        manifest_path = self.archive_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        try:
            subprocess.run(["git", "add", str(self.archive_dir)], cwd=self.repo_root, check=True)
            subprocess.run(
                ["git", "commit", "-m", "chore(docs): archive outdated/duplicate/ephemeral docs"],
                cwd=self.repo_root,
                check=True,
            )
            print("  ✅ Changes committed to git")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Git commit failed: {e}")

    def _flatten_candidates(self) -> list[Path]:
        """Flatten candidates dict."""
        all_candidates = set()
        for files in self.candidates.values():
            all_candidates.update(files)
        return sorted(all_candidates)

    def _write_list(self, path: Path, items: list[Path]) -> None:
        """Write list to file."""
        with open(path, "w") as f:
            for item in sorted(items):
                f.write(f"{item}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Archive-first documentation cleanup")
    parser.add_argument("--execute", action="store_true", help="Execute archive")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root")
    args = parser.parse_args()

    cleanup = DocumentationCleanup(
        repo_root=args.repo_root, dry_run=not args.execute, interactive=args.interactive
    )
    cleanup.run()


if __name__ == "__main__":
    main()
