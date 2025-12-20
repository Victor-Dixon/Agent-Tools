"""
Verify SSOT compliance for bulk deletion batches.
Checks for broken imports, references, and SSOT violations.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Any
import subprocess

class BulkDeletionSSOTVerifier:
    """Verifies SSOT compliance for bulk deleted files."""
    
    def __init__(self, deletion_log_path: Path, duplicate_data_path: Path):
        self.deletion_log_path = deletion_log_path
        self.duplicate_data_path = duplicate_data_path
        self.deleted_files: Set[str] = set()
        self.ssot_files: Dict[str, str] = {}  # deleted -> ssot mapping
        self.violations: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        
    def load_deletion_data(self):
        """Load deleted files from execution log and duplicate analysis."""
        # Load from duplicate analysis data
        if self.duplicate_data_path.exists():
            with open(self.duplicate_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for group in data.get('categories', {}).get('identical_safe_delete', []):
                ssot = group.get('ssot', '')
                for duplicate in group.get('duplicates', []):
                    # Normalize paths
                    dup_path = str(Path(duplicate).as_posix())
                    self.deleted_files.add(dup_path)
                    if ssot:
                        self.ssot_files[dup_path] = ssot
        
        # Load from execution log if available
        if self.deletion_log_path.exists():
            with open(self.deletion_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract deleted file paths from log
                deleted_pattern = r'✅ Deleted:\s*(.+?)(?:\n|$)'
                matches = re.findall(deleted_pattern, content, re.MULTILINE)
                for match in matches:
                    file_path = str(Path(match.strip()).as_posix())
                    self.deleted_files.add(file_path)
    
    def check_file_exists(self, file_path: str) -> bool:
        """Check if a file still exists (should be deleted)."""
        return Path(file_path).exists()
    
    def check_import_references(self) -> List[Dict[str, Any]]:
        """Check for import statements referencing deleted files."""
        violations = []
        
        # Convert deleted file paths to import patterns
        import_patterns = []
        for deleted_file in self.deleted_files:
            if deleted_file.endswith('.py'):
                # Convert file path to import pattern
                # e.g., "tools/send_agent3_assignment_direct.py" -> "tools.send_agent3_assignment_direct"
                import_path = deleted_file.replace('/', '.').replace('\\', '.').replace('.py', '')
                import_patterns.append((deleted_file, import_path))
        
        # Search for imports in Python files
        repo_root = Path('.')
        for py_file in repo_root.rglob('*.py'):
            # Skip deprecated and temp directories
            if 'deprecated' in str(py_file) or 'temp_repos' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for deleted_file, import_pattern in import_patterns:
                    # Check for various import patterns
                    patterns = [
                        rf'from\s+{re.escape(import_pattern)}\s+import',
                        rf'import\s+{re.escape(import_pattern)}',
                        rf'from\s+{re.escape(import_pattern)}\.',
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, content):
                            violations.append({
                                'type': 'broken_import',
                                'deleted_file': deleted_file,
                                'referencing_file': str(py_file),
                                'import_pattern': import_pattern,
                                'severity': 'high'
                            })
                            break
            except Exception as e:
                self.warnings.append({
                    'type': 'file_read_error',
                    'file': str(py_file),
                    'error': str(e)
                })
        
        return violations
    
    def check_string_references(self) -> List[Dict[str, Any]]:
        """Check for string references to deleted files (e.g., in configs, docs)."""
        violations = []
        
        repo_root = Path('.')
        for deleted_file in self.deleted_files:
            file_name = Path(deleted_file).name
            
            # Search in common reference files
            search_files = list(repo_root.rglob('*.md')) + list(repo_root.rglob('*.json')) + \
                          list(repo_root.rglob('*.yaml')) + list(repo_root.rglob('*.yml'))
            
            for ref_file in search_files:
                # Skip deprecated and temp directories
                if 'deprecated' in str(ref_file) or 'temp_repos' in str(ref_file):
                    continue
                
                try:
                    with open(ref_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if file_name in content or deleted_file in content:
                        # Check if it's a meaningful reference (not just coincidence)
                        if re.search(rf'\b{re.escape(file_name)}\b', content):
                            violations.append({
                                'type': 'string_reference',
                                'deleted_file': deleted_file,
                                'referencing_file': str(ref_file),
                                'severity': 'medium'
                            })
                except Exception:
                    pass
        
        return violations
    
    def verify_ssot_compliance(self) -> Dict[str, Any]:
        """Run full SSOT compliance verification."""
        print("🔍 Loading deletion data...")
        self.load_deletion_data()
        
        print(f"📊 Found {len(self.deleted_files)} deleted files to verify")
        
        print("🔍 Checking for broken imports...")
        import_violations = self.check_import_references()
        self.violations.extend(import_violations)
        
        print("🔍 Checking for string references...")
        string_violations = self.check_string_references()
        self.violations.extend(string_violations)
        
        # Check if files actually exist (should be deleted)
        print("🔍 Verifying files are actually deleted...")
        still_exist = []
        for deleted_file in list(self.deleted_files)[:100]:  # Sample check
            if self.check_file_exists(deleted_file):
                still_exist.append(deleted_file)
        
        if still_exist:
            self.warnings.append({
                'type': 'file_still_exists',
                'files': still_exist[:10],  # Limit output
                'count': len(still_exist)
            })
        
        # Summary
        compliant = len(self.violations) == 0
        
        return {
            'compliant': compliant,
            'total_deleted_files': len(self.deleted_files),
            'violations': self.violations,
            'warnings': self.warnings,
            'violation_count': len(self.violations),
            'warning_count': len(self.warnings)
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify SSOT compliance for bulk deletion")
    parser.add_argument("--deletion-log", type=str, 
                       default="agent_workspaces/Agent-2/BULK_DELETION_EXECUTION_LOG.md",
                       help="Path to deletion execution log")
    parser.add_argument("--duplicate-data", type=str,
                       default="docs/technical_debt/DUPLICATE_ANALYSIS_DATA.json",
                       help="Path to duplicate analysis data")
    parser.add_argument("--output", type=str,
                       default="agent_workspaces/Agent-8/BULK_DELETION_SSOT_VERIFICATION.json",
                       help="Output JSON report path")
    args = parser.parse_args()
    
    verifier = BulkDeletionSSOTVerifier(
        deletion_log_path=Path(args.deletion_log),
        duplicate_data_path=Path(args.duplicate_data)
    )
    
    print("🚀 Starting SSOT compliance verification for bulk deletion...")
    result = verifier.verify_ssot_compliance()
    
    # Save report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SSOT COMPLIANCE VERIFICATION SUMMARY")
    print("="*60)
    print(f"✅ Compliant: {result['compliant']}")
    print(f"📁 Total Deleted Files: {result['total_deleted_files']}")
    print(f"🚨 Violations: {result['violation_count']}")
    print(f"⚠️  Warnings: {result['warning_count']}")
    
    if result['violations']:
        print("\n🚨 VIOLATIONS FOUND:")
        for i, violation in enumerate(result['violations'][:10], 1):
            print(f"  {i}. {violation['type']}: {violation.get('deleted_file', 'unknown')}")
            print(f"     → Referenced in: {violation.get('referencing_file', 'unknown')}")
    
    if result['warnings']:
        print("\n⚠️  WARNINGS:")
        for i, warning in enumerate(result['warnings'][:5], 1):
            print(f"  {i}. {warning['type']}: {warning.get('count', 1)} items")
    
    print(f"\n✅ Report saved to: {output_path}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")

if __name__ == "__main__":
    main()




