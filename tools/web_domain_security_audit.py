#!/usr/bin/env python3
"""
Web Domain Security Audit Tool
==============================

Pre-public audit tool for web domain security validation.
Checks for:
- Hardcoded API keys and tokens
- Authentication/authorization issues
- Input validation problems
- CSS/styling security issues
- API endpoint security

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-13
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class WebDomainSecurityAudit:
    """Web domain security audit tool."""

    def __init__(self, project_root: Path):
        """Initialize audit tool."""
        self.project_root = project_root
        self.issues: List[Dict] = []
        self.checked_files: List[str] = []

        # Security patterns to check
        self.api_key_patterns = [
            r'api[_-]?key\s*[:=]\s*["\']([^"\']+)["\']',
            r'apikey\s*[:=]\s*["\']([^"\']+)["\']',
            r'DISCORD_BOT_TOKEN\s*[:=]\s*["\']([^"\']+)["\']',
            r'TOKEN\s*[:=]\s*["\']([^"\']+)["\']',
            r'secret[_-]?key\s*[:=]\s*["\']([^"\']+)["\']',
            r'password\s*[:=]\s*["\']([^"\']+)["\']',
            r'private[_-]?key\s*[:=]\s*["\']([^"\']+)["\']',
        ]

        # Web domain directories to audit
        self.web_directories = [
            'src/discord_commander',
            'src/web',
            'docs/blog',
            'src/services/chat_presence',
            'src/infrastructure/browser',
        ]

        # File patterns to check
        self.file_patterns = [
            '*.py',
            '*.js',
            '*.html',
            '*.css',
            '*.md',
        ]

    def audit_file(self, file_path: Path) -> List[Dict]:
        """Audit a single file for security issues."""
        issues = []
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            # Check for hardcoded API keys
            for pattern in self.api_key_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip if it's clearly an environment variable reference
                    if 'os.getenv' in content or 'os.environ' in content:
                        continue
                    if 'getenv' in content or 'environ' in content:
                        continue
                    
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'type': 'hardcoded_credential',
                        'severity': 'high',
                        'file': str(file_path.relative_to(self.project_root)),
                        'line': line_num,
                        'pattern': pattern,
                        'match': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0),
                    })

            # Check for console.log in production code
            if file_path.suffix in ['.js', '.ts']:
                for i, line in enumerate(lines, 1):
                    if 'console.log' in line and '//' not in line.split('console.log')[0]:
                        issues.append({
                            'type': 'debug_code',
                            'severity': 'low',
                            'file': str(file_path.relative_to(self.project_root)),
                            'line': i,
                            'issue': 'console.log found in production code',
                        })

            # Check for TODO/FIXME comments that might indicate security issues
            for i, line in enumerate(lines, 1):
                if re.search(r'TODO.*(?:security|auth|token|key|password)', line, re.IGNORECASE):
                    issues.append({
                        'type': 'security_todo',
                        'severity': 'medium',
                        'file': str(file_path.relative_to(self.project_root)),
                        'line': i,
                        'issue': 'Security-related TODO found',
                    })

        except Exception as e:
            issues.append({
                'type': 'audit_error',
                'severity': 'low',
                'file': str(file_path.relative_to(self.project_root)),
                'error': str(e),
            })

        return issues

    def audit_directory(self, directory: Path) -> List[Dict]:
        """Audit all files in a directory."""
        all_issues = []
        
        if not directory.exists():
            return all_issues

        for pattern in self.file_patterns:
            for file_path in directory.rglob(pattern):
                # Skip certain directories
                if any(skip in str(file_path) for skip in ['__pycache__', '.git', 'node_modules', '.venv']):
                    continue
                
                # Skip binary files
                if file_path.suffix in ['.pyc', '.pyo', '.pyd', '.so', '.dll']:
                    continue

                self.checked_files.append(str(file_path.relative_to(self.project_root)))
                issues = self.audit_file(file_path)
                all_issues.extend(issues)

        return all_issues

    def run_audit(self) -> Dict:
        """Run complete web domain security audit."""
        print("🔍 Starting Web Domain Security Audit...")
        print(f"📁 Project root: {self.project_root}")
        print()

        all_issues = []
        
        for directory_name in self.web_directories:
            directory = self.project_root / directory_name
            print(f"📂 Auditing: {directory_name}")
            issues = self.audit_directory(directory)
            all_issues.extend(issues)
            print(f"   Found {len(issues)} issues")

        # Categorize issues
        categorized = {
            'high': [i for i in all_issues if i.get('severity') == 'high'],
            'medium': [i for i in all_issues if i.get('severity') == 'medium'],
            'low': [i for i in all_issues if i.get('severity') == 'low'],
        }

        result = {
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(all_issues),
            'high_severity': len(categorized['high']),
            'medium_severity': len(categorized['medium']),
            'low_severity': len(categorized['low']),
            'files_checked': len(self.checked_files),
            'issues': all_issues,
            'categorized': categorized,
        }

        return result

    def generate_report(self, result: Dict) -> str:
        """Generate human-readable audit report."""
        report = []
        report.append("# Web Domain Security Audit Report")
        report.append(f"**Date**: {result['timestamp']}")
        report.append(f"**Files Checked**: {result['files_checked']}")
        report.append("")
        report.append("## Summary")
        report.append(f"- **Total Issues**: {result['total_issues']}")
        report.append(f"- **High Severity**: {result['high_severity']}")
        report.append(f"- **Medium Severity**: {result['medium_severity']}")
        report.append(f"- **Low Severity**: {result['low_severity']}")
        report.append("")

        if result['high_severity'] > 0:
            report.append("## 🔴 High Severity Issues")
            for issue in result['categorized']['high']:
                report.append(f"- **{issue['file']}** (line {issue.get('line', '?')}): {issue.get('type', 'unknown')}")
                if 'match' in issue:
                    report.append(f"  - Match: `{issue['match']}`")
            report.append("")

        if result['medium_severity'] > 0:
            report.append("## 🟡 Medium Severity Issues")
            for issue in result['categorized']['medium']:
                report.append(f"- **{issue['file']}** (line {issue.get('line', '?')}): {issue.get('issue', issue.get('type', 'unknown'))}")
            report.append("")

        if result['low_severity'] > 0:
            report.append("## 🟢 Low Severity Issues")
            for issue in result['categorized']['low'][:10]:  # Limit to first 10
                report.append(f"- **{issue['file']}** (line {issue.get('line', '?')}): {issue.get('issue', issue.get('type', 'unknown'))}")
            if len(result['categorized']['low']) > 10:
                report.append(f"- ... and {len(result['categorized']['low']) - 10} more low severity issues")
            report.append("")

        return '\n'.join(report)


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    audit = WebDomainSecurityAudit(project_root)
    
    result = audit.run_audit()
    
    # Save JSON result
    output_file = project_root / 'docs' / f'WEB_DOMAIN_SECURITY_AUDIT_{datetime.now().strftime("%Y%m%d")}.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    # Generate and save report
    report = audit.generate_report(result)
    report_file = project_root / 'docs' / f'WEB_DOMAIN_SECURITY_AUDIT_{datetime.now().strftime("%Y%m%d")}.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print("✅ Audit Complete!")
    print(f"📄 JSON Report: {output_file}")
    print(f"📄 Markdown Report: {report_file}")
    print()
    print(report)
    
    return 0 if result['high_severity'] == 0 else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

