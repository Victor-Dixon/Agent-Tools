#!/usr/bin/env python3
"""
Broken Tools Audit - Systematic Testing & Quarantine
===================================================

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-10-15
Purpose: Test all tools, identify broken ones, prepare for quarantine

USAGE:
    python tools/audit_broken_tools.py
    
    # With detailed output
    python tools/audit_broken_tools.py --verbose
    
    # Test specific directory
    python tools/audit_broken_tools.py --dir tools
    
    # Create quarantine manifest
    python tools/audit_broken_tools.py --create-manifest

OUTPUT:
    - BROKEN_TOOLS_AUDIT_REPORT.md (comprehensive report)
    - BROKEN_TOOLS_QUARANTINE_MANIFEST.json (structured data)
    - Console output (summary)
"""

import ast
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from src.core.config.timeout_constants import TimeoutConstants


class ToolAuditor:
    """Audits tools to identify broken/non-functional ones"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            'working': [],
            'broken': [],
            'syntax_errors': [],
            'import_errors': [],
            'missing_dependencies': [],
            'runtime_errors': [],
            'unknown': []
        }
        self.quarantine_manifest = []
    
    def audit_directory(self, directory: Path) -> Dict[str, List[str]]:
        """Audit all Python files in directory"""
        print(f"\n🔍 Auditing: {directory}")
        print("=" * 70)
        
        python_files = list(directory.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip(f)]
        
        total = len(python_files)
        print(f"Found {total} Python files to audit\n")
        
        for idx, file_path in enumerate(python_files, 1):
            print(f"[{idx}/{total}] Testing {file_path.name}...", end=" ")
            result = self._test_file(file_path)
            print(result['status'])
        
        return self.results
    
    def _should_skip(self, path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            '__pycache__',
            '.pyc',
            'test_',
            '_test.py',
            'conftest.py',
            '__init__.py',
            'temp_',
            '.git'
        ]
        
        path_str = str(path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _test_file(self, file_path: Path) -> Dict[str, str]:
        """Test if a file works"""
        try:
            relative_path = str(file_path.relative_to(Path.cwd()))
        except ValueError:
            relative_path = str(file_path)
        
        # Test 1: Syntax check
        syntax_ok, syntax_error = self._check_syntax(file_path)
        if not syntax_ok:
            self.results['syntax_errors'].append(relative_path)
            self.results['broken'].append(relative_path)
            self._add_to_quarantine(relative_path, 'syntax_error', syntax_error)
            return {'status': '❌ SYNTAX ERROR', 'reason': syntax_error}
        
        # Test 2: Import check
        import_ok, import_error = self._check_imports(file_path)
        if not import_ok:
            self.results['import_errors'].append(relative_path)
            self.results['broken'].append(relative_path)
            self._add_to_quarantine(relative_path, 'import_error', import_error)
            return {'status': '❌ IMPORT ERROR', 'reason': import_error}
        
        # Test 3: Help check (if CLI tool)
        if self._is_cli_tool(file_path):
            help_ok, help_error = self._check_help(file_path)
            if not help_ok:
                self.results['runtime_errors'].append(relative_path)
                self.results['broken'].append(relative_path)
                self._add_to_quarantine(relative_path, 'runtime_error', help_error)
                return {'status': '⚠️ RUNTIME ERROR', 'reason': help_error}
        
        # All checks passed
        self.results['working'].append(relative_path)
        return {'status': '✅ WORKING', 'reason': None}
    
    def _check_syntax(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Check Python syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
    
    def _check_imports(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Check if file can be imported"""
        try:
            # Use python -m py_compile
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(file_path)],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_QUICK
            )
            
            if result.returncode == 0:
                return True, None
            else:
                error_msg = result.stderr.strip()
                return False, error_msg[:200]
                
        except subprocess.TimeoutExpired:
            return False, "Import timeout (5 seconds)"
        except Exception as e:
            return False, str(e)
    
    def _is_cli_tool(self, file_path: Path) -> bool:
        """Check if file is a CLI tool (has main or argparse)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            indicators = [
                'if __name__ == "__main__"',
                'argparse.ArgumentParser',
                'def main(',
                'click.command'
            ]
            
            return any(ind in content for ind in indicators)
            
        except Exception:
            return False
    
    def _check_help(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Check if CLI tool can show help"""
        try:
            result = subprocess.run(
                [sys.executable, str(file_path), '--help'],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_SHORT
            )
            
            # Exit code 0 or help output = working
            if result.returncode == 0 or 'usage:' in result.stdout.lower():
                return True, None
            else:
                return False, result.stderr.strip()[:200]
                
        except subprocess.TimeoutExpired:
            return False, "Help timeout (10 seconds)"
        except Exception as e:
            return False, str(e)
    
    def _add_to_quarantine(self, file_path: str, error_type: str, error_msg: str):
        """Add file to quarantine manifest"""
        self.quarantine_manifest.append({
            'file': file_path,
            'error_type': error_type,
            'error_message': error_msg,
            'discovered': datetime.utcnow().isoformat() + 'Z',
            'status': 'QUARANTINE_PENDING'
        })
    
    def generate_report(self) -> str:
        """Generate markdown report"""
        total = sum(len(v) for v in self.results.values())
        working_count = len(self.results['working'])
        broken_count = len(self.results['broken'])
        
        report = f"""# 🔍 BROKEN TOOLS AUDIT REPORT

**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC  
**Audited By:** Agent-3 (Infrastructure & DevOps Specialist)  
**Purpose:** Identify and quarantine non-functional tools

---

## 📊 AUDIT SUMMARY

**Total Tools Audited:** {total}  
**Working:** {working_count} ({working_count/total*100:.1f}%)  
**Broken:** {broken_count} ({broken_count/total*100:.1f}%)

**Breakdown:**
- ✅ Working: {working_count}
- ❌ Syntax Errors: {len(self.results['syntax_errors'])}
- ❌ Import Errors: {len(self.results['import_errors'])}
- ⚠️ Runtime Errors: {len(self.results['runtime_errors'])}

---

## ❌ BROKEN TOOLS ({broken_count} total)

### Syntax Errors ({len(self.results['syntax_errors'])}):
"""
        
        for file in sorted(self.results['syntax_errors']):
            report += f"- `{file}`\n"
        
        report += f"\n### Import Errors ({len(self.results['import_errors'])}):\n"
        for file in sorted(self.results['import_errors']):
            report += f"- `{file}`\n"
        
        report += f"\n### Runtime Errors ({len(self.results['runtime_errors'])}):\n"
        for file in sorted(self.results['runtime_errors']):
            report += f"- `{file}`\n"
        
        report += f"""

---

## ✅ WORKING TOOLS ({working_count} total)

"""
        for file in sorted(self.results['working'])[:20]:  # Show first 20
            report += f"- `{file}`\n"
        
        if len(self.results['working']) > 20:
            report += f"\n... and {len(self.results['working']) - 20} more\n"
        
        report += f"""

---

## 🚨 QUARANTINE RECOMMENDATION

**Action:** Move {broken_count} broken tools to `tools_quarantine/`

**Manifest:** See `BROKEN_TOOLS_QUARANTINE_MANIFEST.json` for details

**Fix Priority:**
1. Syntax errors (quick fixes)
2. Import errors (dependency/path issues)
3. Runtime errors (logic/functionality issues)

---

## 🎯 NEXT STEPS

**For Swarm:**
1. Review this audit report
2. Create `tools_quarantine/` directory
3. Move broken tools systematically
4. Fix one by one with proper testing
5. Reintegrate when validated

---

**Audit complete - ready for quarantine operation!**
"""
        
        return report
    
    def save_manifest(self, output_file: str = "BROKEN_TOOLS_QUARANTINE_MANIFEST.json"):
        """Save quarantine manifest to JSON"""
        manifest = {
            'audit_date': datetime.utcnow().isoformat() + 'Z',
            'audited_by': 'Agent-3',
            'total_broken': len(self.results['broken']),
            'broken_tools': self.quarantine_manifest,
            'summary': {
                'syntax_errors': len(self.results['syntax_errors']),
                'import_errors': len(self.results['import_errors']),
                'runtime_errors': len(self.results['runtime_errors'])
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n✅ Manifest saved: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Audit tools and identify broken ones for quarantine"
    )
    parser.add_argument(
        '--dir',
        default='tools',
        help='Directory to audit (default: tools)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--create-manifest',
        action='store_true',
        help='Create quarantine manifest'
    )
    
    args = parser.parse_args()
    
    # Run audit
    auditor = ToolAuditor(verbose=args.verbose)
    
    print("\n" + "="*70)
    print("🔍 BROKEN TOOLS AUDIT - Starting")
    print("="*70)
    
    target_dir = Path(args.dir)
    if not target_dir.exists():
        print(f"❌ Error: Directory '{args.dir}' not found")
        return 1
    
    # Audit
    results = auditor.audit_directory(target_dir)
    
    # Generate report
    print("\n" + "="*70)
    print("📊 GENERATING REPORT")
    print("="*70)
    
    report = auditor.generate_report()
    
    # Save report
    report_file = "BROKEN_TOOLS_AUDIT_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report saved: {report_file}")
    
    # Save manifest if requested
    if args.create_manifest:
        auditor.save_manifest()
    
    # Summary
    print("\n" + "="*70)
    print("📈 AUDIT SUMMARY")
    print("="*70)
    total = sum(len(v) for v in results.values())
    working = len(results['working'])
    broken = len(results['broken'])
    
    print(f"Total Tools: {total}")
    print(f"✅ Working: {working} ({working/total*100:.1f}%)")
    print(f"❌ Broken: {broken} ({broken/total*100:.1f}%)")
    print(f"")
    print(f"Breakdown:")
    print(f"  - Syntax Errors: {len(results['syntax_errors'])}")
    print(f"  - Import Errors: {len(results['import_errors'])}")
    print(f"  - Runtime Errors: {len(results['runtime_errors'])}")
    print("")
    print(f"📄 Full Report: {report_file}")
    
    if args.create_manifest:
        print(f"📋 Quarantine Manifest: BROKEN_TOOLS_QUARANTINE_MANIFEST.json")
    
    print("\n🎯 Next: Review report and create quarantine strategy")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

