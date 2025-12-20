#!/usr/bin/env python3
"""
Documentation Sprawl Analyzer
==============================

Analyzes documentation files to identify candidates for safe deletion:
- Duplicate documentation
- Outdated session reports
- Unreferenced files
- Archive/old documentation

Usage:
    python tools/analyze_documentation_sprawl.py [--dry-run] [--delete]

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class DocumentationAnalyzer:
    """Analyzes documentation for safe deletion candidates."""
    
    # Patterns for files that are likely safe to delete
    SAFE_DELETE_PATTERNS = [
        # Session-specific reports (older than 7 days)
        r'.*SESSION.*\d{4}-\d{2}-\d{2}.*\.md$',
        r'.*COMPLETION.*\d{4}-\d{2}-\d{2}.*\.md$',
        r'.*REPORT.*\d{4}-\d{2}-\d{2}.*\.md$',
        r'.*STATUS.*\d{4}-\d{2}-\d{2}.*\.md$',
        
        # Agent-specific temporary reports
        r'AGENT\d+_.*_\d{4}-\d{2}-\d{2}\.md$',
        r'AGENT\d+_.*_\d{4}-\d{2}-\d{2}\.txt$',
        
        # Duplicate/backup files
        r'.*_BACKUP.*\.md$',
        r'.*_OLD.*\.md$',
        r'.*_ARCHIVE.*\.md$',
        r'.*_COPY.*\.md$',
        
        # Temporary analysis files
        r'.*_ANALYSIS.*\.json$',
        r'.*_REPORT.*\.json$',
        r'.*_SCAN.*\.json$',
    ]
    
    # Directories that are likely archives
    ARCHIVE_DIRS = [
        'archive',
        'archives',
        'backup',
        'backups',
        'old',
        'deprecated',
        'quarantine',
    ]
    
    # Files that should NEVER be deleted
    PROTECTED_FILES = [
        'README.md',
        'CODE_OF_CONDUCT.md',
        'LICENSE',
        'CHANGELOG.md',
        'CONTRIBUTING.md',
        'STANDARDS.md',
        'AGENTS.md',
    ]
    
    def __init__(self, project_root: Path):
        """Initialize analyzer."""
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.agent_workspaces = project_root / "agent_workspaces"
        self.candidates: List[Dict] = []
        self.protected: Set[Path] = set()
        
    def find_all_docs(self) -> List[Path]:
        """Find all markdown and text documentation files."""
        docs = []
        
        # Search docs directory (limit to avoid huge scans)
        if self.docs_dir.exists():
            try:
                docs.extend(list(self.docs_dir.rglob("*.md"))[:500])  # Limit to 500
                docs.extend(list(self.docs_dir.rglob("*.txt"))[:200])  # Limit to 200
            except Exception as e:
                print(f"⚠️  Error scanning docs directory: {e}")
        
        # Search agent workspaces (excluding inbox/archive) - limit scope
        if self.agent_workspaces.exists():
            try:
                for agent_dir in self.agent_workspaces.iterdir():
                    if agent_dir.is_dir() and agent_dir.name.startswith("Agent-"):
                        # Only scan top-level files, not deep recursion
                        for doc_file in agent_dir.glob("*.md"):
                            if "inbox" not in str(doc_file) and "archive" not in str(doc_file):
                                docs.append(doc_file)
                        # Also check one level deep
                        for subdir in agent_dir.iterdir():
                            if subdir.is_dir() and subdir.name not in ["inbox", "archive"]:
                                for doc_file in subdir.glob("*.md"):
                                    docs.append(doc_file)
            except Exception as e:
                print(f"⚠️  Error scanning agent workspaces: {e}")
        
        return docs
    
    def is_protected(self, file_path: Path) -> bool:
        """Check if file is protected from deletion."""
        filename = file_path.name
        
        # Check protected list
        if filename in self.PROTECTED_FILES:
            return True
        
        # Check if in protected directories
        protected_dirs = ['swarm_brain', 'standards', 'protocols', 'guides']
        for part in file_path.parts:
            if part in protected_dirs:
                return True
        
        return False
    
    def is_archive_directory(self, file_path: Path) -> bool:
        """Check if file is in an archive directory."""
        for part in file_path.parts:
            if part.lower() in self.ARCHIVE_DIRS:
                return True
        return False
    
    def matches_safe_delete_pattern(self, file_path: Path) -> bool:
        """Check if file matches safe delete patterns."""
        filename = file_path.name
        for pattern in self.SAFE_DELETE_PATTERNS:
            if re.match(pattern, filename, re.IGNORECASE):
                return True
        return False
    
    def is_old_session_file(self, file_path: Path, days: int = 7) -> bool:
        """Check if file is an old session-specific file."""
        if not file_path.exists():
            return False
        
        # Check modification time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        age = datetime.now() - mtime
        
        if age.days > days:
            # Check if filename suggests it's session-specific
            filename = file_path.name.lower()
            session_keywords = ['session', 'completion', 'report', 'status', 'summary']
            if any(keyword in filename for keyword in session_keywords):
                # Check for date pattern in filename
                if re.search(r'\d{4}-\d{2}-\d{2}', file_path.name):
                    return True
        
        return False
    
    def check_references(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Check if file is referenced in code or other docs.
        Returns: (is_referenced, reference_locations)
        """
        filename = file_path.name
        stem = file_path.stem
        references = []
        
        # Quick check: search in key files only (README, main docs)
        key_files = [
            self.project_root / "README.md",
            self.project_root / "docs" / "DOCUMENTATION_INDEX.md",
        ]
        
        for key_file in key_files:
            if key_file.exists() and key_file != file_path:
                try:
                    content = key_file.read_text(encoding='utf-8', errors='ignore')
                    if filename in content or stem in content:
                        references.append(str(key_file.relative_to(self.project_root)))
                except Exception:
                    continue
        
        # Limited search in Python files (only in src/)
        try:
            for py_file in (self.project_root / "src").rglob("*.py"):
                if len(references) >= 3:  # Limit to 3 references
                    break
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    if filename in content:
                        references.append(str(py_file.relative_to(self.project_root)))
                except Exception:
                    continue
        except Exception:
            pass
        
        return len(references) > 0, references
    
    def analyze(self) -> Dict:
        """Analyze all documentation files."""
        all_docs = self.find_all_docs()
        
        results = {
            'total_files': len(all_docs),
            'protected': [],
            'safe_to_delete': [],
            'archive_dirs': [],
            'old_session_files': [],
            'unreferenced': [],
            'duplicates': [],
        }
        
        # Group by filename to find duplicates
        filename_groups = defaultdict(list)
        for doc in all_docs:
            filename_groups[doc.name].append(doc)
        
        for doc_file in all_docs:
            rel_path = doc_file.relative_to(self.project_root)
            
            # Skip protected files
            if self.is_protected(doc_file):
                results['protected'].append(str(rel_path))
                continue
            
            # Check for duplicates
            if len(filename_groups[doc_file.name]) > 1:
                duplicates = [str(d.relative_to(self.project_root)) 
                            for d in filename_groups[doc_file.name] if d != doc_file]
                results['duplicates'].append({
                    'file': str(rel_path),
                    'duplicates': duplicates
                })
            
            # Check archive directories
            if self.is_archive_directory(doc_file):
                results['archive_dirs'].append(str(rel_path))
                continue
            
            # Check safe delete patterns
            if self.matches_safe_delete_pattern(doc_file):
                is_referenced, refs = self.check_references(doc_file)
                results['safe_to_delete'].append({
                    'file': str(rel_path),
                    'reason': 'matches_safe_delete_pattern',
                    'referenced': is_referenced,
                    'references': refs[:3]  # Limit to first 3
                })
                continue
            
            # Check old session files
            if self.is_old_session_file(doc_file):
                is_referenced, refs = self.check_references(doc_file)
                results['old_session_files'].append({
                    'file': str(rel_path),
                    'age_days': (datetime.now() - datetime.fromtimestamp(doc_file.stat().st_mtime)).days,
                    'referenced': is_referenced,
                    'references': refs[:3]
                })
                continue
        
        return results
    
    def print_report(self, results: Dict, dry_run: bool = True):
        """Print analysis report."""
        print("\n" + "="*60)
        print("📋 DOCUMENTATION SPRAWL ANALYSIS")
        print("="*60)
        print(f"Total Documentation Files: {results['total_files']}")
        print(f"Protected Files: {len(results['protected'])}")
        print(f"Safe to Delete (patterns): {len(results['safe_to_delete'])}")
        print(f"Old Session Files (>7 days): {len(results['old_session_files'])}")
        print(f"Archive Directory Files: {len(results['archive_dirs'])}")
        print(f"Duplicate Filenames: {len(results['duplicates'])}")
        print("="*60 + "\n")
        
        # Safe to delete (patterns)
        if results['safe_to_delete']:
            print("🗑️  SAFE TO DELETE (Patterns):")
            for item in results['safe_to_delete'][:20]:  # Limit output
                ref_status = "✅ Referenced" if item['referenced'] else "❌ Unreferenced"
                print(f"   • {item['file']} ({ref_status})")
                if item['references']:
                    print(f"     Referenced in: {', '.join(item['references'])}")
            if len(results['safe_to_delete']) > 20:
                print(f"   ... and {len(results['safe_to_delete']) - 20} more")
            print()
        
        # Old session files
        if results['old_session_files']:
            print("📅 OLD SESSION FILES (>7 days, unreferenced):")
            unreferenced_old = [f for f in results['old_session_files'] if not f['referenced']]
            for item in unreferenced_old[:20]:
                print(f"   • {item['file']} ({item['age_days']} days old)")
            if len(unreferenced_old) > 20:
                print(f"   ... and {len(unreferenced_old) - 20} more")
            print()
        
        # Duplicates
        if results['duplicates']:
            print("📋 DUPLICATE FILENAMES:")
            for item in results['duplicates'][:10]:
                print(f"   • {item['file']}")
                print(f"     Duplicates: {', '.join(item['duplicates'][:3])}")
            if len(results['duplicates']) > 10:
                print(f"   ... and {len(results['duplicates']) - 10} more")
            print()
        
        # Summary
        total_candidates = (
            len([f for f in results['safe_to_delete'] if not f['referenced']]) +
            len([f for f in results['old_session_files'] if not f['referenced']])
        )
        
        print("="*60)
        print(f"📊 SUMMARY")
        print("="*60)
        print(f"Total Safe to Delete (unreferenced): {total_candidates}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print("="*60 + "\n")
        
        return total_candidates


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze documentation sprawl and identify safe deletion candidates"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Preview deletions without applying (default)'
    )
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Actually delete files (use with caution)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Save analysis results to JSON file'
    )
    
    args = parser.parse_args()
    
    analyzer = DocumentationAnalyzer(project_root)
    results = analyzer.analyze()
    
    total_candidates = analyzer.print_report(results, dry_run=not args.delete)
    
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2), encoding='utf-8')
        print(f"✅ Analysis saved to: {args.output}")
    
    if args.delete and total_candidates > 0:
        print("⚠️  DELETE MODE - This will permanently delete files!")
        print(f"About to delete {total_candidates} files")
        
        # Get list of files to delete
        files_to_delete = []
        for item in results['safe_to_delete']:
            if not item['referenced']:
                files_to_delete.append(Path(project_root / item['file']))
        for item in results['old_session_files']:
            if not item['referenced']:
                files_to_delete.append(Path(project_root / item['file']))
        
        deleted_count = 0
        failed_count = 0
        
        for file_path in files_to_delete:
            try:
                if file_path.exists():
                    file_path.unlink()
                    deleted_count += 1
                    print(f"✅ Deleted: {file_path.relative_to(project_root)}")
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to delete {file_path}: {e}")
        
        print(f"\n✅ Deletion complete: {deleted_count} deleted, {failed_count} failed")
    
    sys.exit(0)


if __name__ == '__main__':
    main()

