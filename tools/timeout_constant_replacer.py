#!/usr/bin/env python3
"""
Timeout Constant Replacer - Automated SSOT Consolidation Tool
============================================================

Purpose: Automate replacement of hardcoded timeout values with TimeoutConstants SSOT references.
Impact: Reduces manual work from hours to minutes for large-scale timeout consolidation.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-04
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants


class TimeoutReplacer:
    """Automated timeout constant replacement tool."""
    
    # Mapping of timeout values to TimeoutConstants attributes
    TIMEOUT_MAPPING = {
        30: "TimeoutConstants.HTTP_DEFAULT",
        10: "TimeoutConstants.HTTP_SHORT",
        60: "TimeoutConstants.HTTP_MEDIUM",
        120: "TimeoutConstants.HTTP_LONG",
        300: "TimeoutConstants.HTTP_EXTENDED",
        5: "TimeoutConstants.HTTP_QUICK",
    }
    
    # Patterns to match timeout assignments
    TIMEOUT_PATTERNS = [
        r'timeout\s*=\s*(\d+)',  # timeout=30
        r'timeout\s*:\s*(\d+)',  # timeout: 30
        r'timeout\s*=\s*(\d+\.\d+)',  # timeout=30.0
    ]
    
    # Patterns to exclude (Discord UI View timeouts, etc.)
    EXCLUDE_PATTERNS = [
        r'super\(\)\.__init__\(timeout=',  # Discord UI View
        r'View\(timeout=',  # Discord UI View
        r'Modal\(timeout=',  # Discord UI Modal
    ]
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "replacements_made": 0,
            "replacements_by_timeout": {},
            "files_skipped": [],
            "errors": [],
        }
    
    def should_exclude_line(self, line: str) -> bool:
        """Check if line should be excluded from replacement."""
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, line):
                return True
        return False
    
    def find_timeout_occurrences(self, content: str) -> List[Tuple[int, str, int]]:
        """
        Find all timeout occurrences in content.
        
        Returns:
            List of (line_number, line_content, timeout_value) tuples
        """
        occurrences = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if self.should_exclude_line(line):
                continue
            
            for pattern in self.TIMEOUT_PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    timeout_value = float(match.group(1))
                    timeout_int = int(timeout_value)
                    if timeout_int in self.TIMEOUT_MAPPING:
                        occurrences.append((line_num, line, timeout_int))
        
        return occurrences
    
    def replace_timeout_in_line(self, line: str, timeout_value: int) -> str:
        """Replace timeout value with TimeoutConstants reference."""
        constant_name = self.TIMEOUT_MAPPING[timeout_value]
        
        # Replace timeout=30 with timeout=TimeoutConstants.HTTP_DEFAULT
        line = re.sub(
            rf'timeout\s*=\s*{timeout_value}(?:\.0)?\b',
            f'timeout={constant_name}',
            line
        )
        
        # Replace timeout: 30 with timeout: TimeoutConstants.HTTP_DEFAULT
        line = re.sub(
            rf'timeout\s*:\s*{timeout_value}(?:\.0)?\b',
            f'timeout: {constant_name}',
            line
        )
        
        return line
    
    def ensure_import(self, content: str) -> bool:
        """Check if TimeoutConstants import exists, add if missing."""
        if 'from src.core.config.timeout_constants import TimeoutConstants' in content:
            return False  # Already imported
        
        if 'import TimeoutConstants' in content:
            return False  # Already imported (different format)
        
        # Find last import statement
        lines = content.split('\n')
        last_import_idx = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                last_import_idx = i
        
        if last_import_idx >= 0:
            # Insert after last import
            lines.insert(last_import_idx + 1, 'from src.core.config.timeout_constants import TimeoutConstants')
            return '\n'.join(lines)
        else:
            # No imports found, add at top
            lines.insert(0, 'from src.core.config.timeout_constants import TimeoutConstants')
            return '\n'.join(lines)
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single file for timeout replacements."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Find timeout occurrences
            occurrences = self.find_timeout_occurrences(content)
            
            if not occurrences:
                if self.verbose:
                    print(f"  ⏭️  No timeout occurrences found: {file_path}")
                return False
            
            # Replace occurrences
            lines = content.split('\n')
            modified = False
            
            for line_num, line, timeout_value in occurrences:
                new_line = self.replace_timeout_in_line(line, timeout_value)
                if new_line != line:
                    lines[line_num - 1] = new_line
                    modified = True
                    self.stats["replacements_made"] += 1
                    self.stats["replacements_by_timeout"].setdefault(
                        timeout_value, 0
                    )
                    self.stats["replacements_by_timeout"][timeout_value] += 1
                    
                    if self.verbose:
                        print(f"    Line {line_num}: {timeout_value} → {self.TIMEOUT_MAPPING[timeout_value]}")
            
            if modified:
                # Ensure import exists
                content = '\n'.join(lines)
                content = self.ensure_import(content)
                
                if not self.dry_run:
                    file_path.write_text(content, encoding='utf-8')
                    self.stats["files_modified"] += 1
                    print(f"  ✅ Modified: {file_path} ({len(occurrences)} replacements)")
                else:
                    print(f"  🔍 Would modify: {file_path} ({len(occurrences)} replacements)")
                    if self.verbose:
                        print(f"    Preview:\n{content[:500]}...")
            
            self.stats["files_processed"] += 1
            return modified
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            self.stats["errors"].append(error_msg)
            print(f"  ❌ {error_msg}")
            return False
    
    def process_directory(self, directory: Path, pattern: str = "*.py") -> None:
        """Process all matching files in directory recursively."""
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                self.process_file(file_path)
    
    def print_stats(self) -> None:
        """Print replacement statistics."""
        print("\n" + "=" * 60)
        print("📊 REPLACEMENT STATISTICS")
        print("=" * 60)
        print(f"Files Processed: {self.stats['files_processed']}")
        print(f"Files Modified: {self.stats['files_modified']}")
        print(f"Total Replacements: {self.stats['replacements_made']}")
        print("\nReplacements by Timeout Value:")
        for timeout_value, count in sorted(self.stats["replacements_by_timeout"].items()):
            constant_name = self.TIMEOUT_MAPPING[timeout_value]
            print(f"  {timeout_value}s → {constant_name}: {count} replacements")
        
        if self.stats["errors"]:
            print(f"\nErrors: {len(self.stats['errors'])}")
            for error in self.stats["errors"]:
                print(f"  ❌ {error}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No files were actually modified")


def main():
    parser = argparse.ArgumentParser(
        description="Automated timeout constant replacement tool"
    )
    parser.add_argument(
        "target",
        help="File or directory to process",
        type=Path
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--pattern",
        default="*.py",
        help="File pattern to match (default: *.py)"
    )
    
    args = parser.parse_args()
    
    replacer = TimeoutReplacer(dry_run=args.dry_run, verbose=args.verbose)
    
    target = args.target
    if not target.exists():
        print(f"❌ Error: {target} does not exist")
        sys.exit(1)
    
    print("🔧 TIMEOUT CONSTANT REPLACER")
    print("=" * 60)
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No files will be modified")
    print()
    
    if target.is_file():
        print(f"Processing file: {target}")
        replacer.process_file(target)
    elif target.is_dir():
        print(f"Processing directory: {target}")
        replacer.process_directory(target, args.pattern)
    else:
        print(f"❌ Error: {target} is not a file or directory")
        sys.exit(1)
    
    replacer.print_stats()
    
    if not args.dry_run and replacer.stats["files_modified"] > 0:
        print("\n✅ Replacement complete! Remember to:")
        print("  1. Run linter on modified files")
        print("  2. Test affected functionality")
        print("  3. Update documentation if needed")


if __name__ == "__main__":
    main()


