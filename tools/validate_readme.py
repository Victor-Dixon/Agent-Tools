#!/usr/bin/env python3
"""
README Validation Tool - Automated README Quality Checker
=========================================================

Validates README.md files for:
- Required sections presence
- Completeness and accuracy
- Formatting standards
- Link validity
- Code block formatting

Usage:
    python tools/validate_readme.py [--readme README.md] [--strict]

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class ValidationResult:
    """Result of a validation check."""
    section: str
    passed: bool
    message: str
    severity: str = "info"  # info, warning, error


class ReadmeValidator:
    """Validates README.md files for completeness and quality."""
    
    # Required sections (case-insensitive)
    REQUIRED_SECTIONS = [
        "overview",
        "architecture",
        "quick start",
        "installation",
        "development standards",
        "agent system",
        "project structure",
        "contributing",
        "documentation",
        "current status"
    ]
    
    # Recommended sections
    RECOMMENDED_SECTIONS = [
        "features",
        "tools",
        "license",
        "acknowledgments",
        "support"
    ]
    
    def __init__(self, readme_path: Optional[Path] = None, strict: bool = False):
        """Initialize validator."""
        self.readme_path = readme_path or project_root / "README.md"
        self.strict = strict
        self.results: List[ValidationResult] = []
        
    def validate(self) -> Tuple[bool, List[ValidationResult]]:
        """Run all validation checks."""
        if not self.readme_path.exists():
            self.results.append(ValidationResult(
                "file_exists",
                False,
                f"README.md not found at {self.readme_path}",
                "error"
            ))
            return False, self.results
        
        content = self.readme_path.read_text(encoding='utf-8')
        
        # Run all checks
        self._check_file_size(content)
        self._check_required_sections(content)
        self._check_recommended_sections(content)
        self._check_table_of_contents(content)
        self._check_code_blocks(content)
        self._check_links(content)
        self._check_formatting(content)
        self._check_badges(content)
        
        # Determine overall pass/fail
        has_errors = any(r.severity == "error" and not r.passed for r in self.results)
        has_warnings = any(r.severity == "warning" and not r.passed for r in self.results)
        
        passed = not has_errors and (not self.strict or not has_warnings)
        
        return passed, self.results
    
    def _check_file_size(self, content: str):
        """Check README file size (should be substantial)."""
        lines = content.split('\n')
        non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        
        if len(lines) < 50:
            self.results.append(ValidationResult(
                "file_size",
                False,
                f"README is too short ({len(lines)} lines, minimum 50 recommended)",
                "warning"
            ))
        elif len(lines) > 1000:
            self.results.append(ValidationResult(
                "file_size",
                False,
                f"README is very long ({len(lines)} lines, consider splitting)",
                "info"
            ))
        else:
            self.results.append(ValidationResult(
                "file_size",
                True,
                f"README size appropriate ({len(lines)} lines)",
                "info"
            ))
    
    def _check_required_sections(self, content: str):
        """Check for required sections."""
        content_lower = content.lower()
        missing = []
        
        for section in self.REQUIRED_SECTIONS:
            # Check for section headers (## or ###) with optional emojis
            # Pattern: ## [emoji] Section Name or ## Section Name
            pattern = rf'^#+\s*[^\w]*{re.escape(section)}'
            if not re.search(pattern, content_lower, re.MULTILINE | re.IGNORECASE):
                missing.append(section)
        
        if missing:
            self.results.append(ValidationResult(
                "required_sections",
                False,
                f"Missing required sections: {', '.join(missing)}",
                "error"
            ))
        else:
            self.results.append(ValidationResult(
                "required_sections",
                True,
                "All required sections present",
                "info"
            ))
    
    def _check_recommended_sections(self, content: str):
        """Check for recommended sections."""
        content_lower = content.lower()
        found = []
        missing = []
        
        for section in self.RECOMMENDED_SECTIONS:
            # Check for section headers with optional emojis
            pattern = rf'^#+\s*[^\w]*{re.escape(section)}'
            if re.search(pattern, content_lower, re.MULTILINE | re.IGNORECASE):
                found.append(section)
            else:
                missing.append(section)
        
        if missing:
            self.results.append(ValidationResult(
                "recommended_sections",
                False,
                f"Missing recommended sections: {', '.join(missing)}",
                "warning"
            ))
        else:
            self.results.append(ValidationResult(
                "recommended_sections",
                True,
                f"All recommended sections present ({len(found)})",
                "info"
            ))
    
    def _check_table_of_contents(self, content: str):
        """Check for table of contents."""
        toc_patterns = [
            r'##\s*table\s+of\s+contents',
            r'##\s*toc',
            r'##\s*contents'
        ]
        
        has_toc = any(re.search(pattern, content, re.IGNORECASE | re.MULTILINE) 
                     for pattern in toc_patterns)
        
        if not has_toc:
            self.results.append(ValidationResult(
                "table_of_contents",
                False,
                "Table of contents not found (recommended for long READMEs)",
                "warning"
            ))
        else:
            self.results.append(ValidationResult(
                "table_of_contents",
                True,
                "Table of contents present",
                "info"
            ))
    
    def _check_code_blocks(self, content: str):
        """Check code block formatting."""
        # Count code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        
        if not code_blocks:
            self.results.append(ValidationResult(
                "code_blocks",
                False,
                "No code blocks found (examples are helpful)",
                "warning"
            ))
        else:
            # Check for language tags
            with_lang = sum(1 for block in code_blocks 
                          if re.match(r'```\w+', block))
            
            self.results.append(ValidationResult(
                "code_blocks",
                True,
                f"Found {len(code_blocks)} code blocks ({with_lang} with language tags)",
                "info"
            ))
    
    def _check_links(self, content: str):
        """Check for links and validate format."""
        # Find markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        
        if not links:
            self.results.append(ValidationResult(
                "links",
                False,
                "No links found (consider adding references)",
                "warning"
            ))
        else:
            # Check for broken link patterns
            broken = []
            for text, url in links:
                if url.startswith('http') and '://' not in url:
                    broken.append(f"{text} -> {url}")
            
            if broken:
                self.results.append(ValidationResult(
                    "links",
                    False,
                    f"Potentially broken links: {', '.join(broken[:3])}",
                    "warning"
                ))
            else:
                self.results.append(ValidationResult(
                    "links",
                    True,
                    f"Found {len(links)} links",
                    "info"
                ))
    
    def _check_formatting(self, content: str):
        """Check markdown formatting."""
        issues = []
        
        # Check for proper heading hierarchy
        headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
        if headings:
            prev_level = 0
            for level, text in headings:
                level_num = len(level)
                if level_num > prev_level + 1 and prev_level > 0:
                    issues.append(f"Heading hierarchy jump: {text}")
                prev_level = level_num
        
        # Check for long lines (should wrap)
        long_lines = [i+1 for i, line in enumerate(content.split('\n'))
                     if len(line) > 120 and not line.strip().startswith('```')]
        
        if long_lines:
            issues.append(f"Long lines (>120 chars) at: {', '.join(map(str, long_lines[:5]))}")
        
        if issues:
            self.results.append(ValidationResult(
                "formatting",
                False,
                f"Formatting issues: {'; '.join(issues[:3])}",
                "warning"
            ))
        else:
            self.results.append(ValidationResult(
                "formatting",
                True,
                "Formatting looks good",
                "info"
            ))
    
    def _check_badges(self, content: str):
        """Check for badges (optional but nice)."""
        badge_patterns = [
            r'!\[.*?\]\(https?://.*?badge.*?\)',
            r'!\[.*?\]\(https?://.*?shield.*?\)'
        ]
        
        badges = sum(len(re.findall(pattern, content)) 
                    for pattern in badge_patterns)
        
        if badges == 0:
            self.results.append(ValidationResult(
                "badges",
                False,
                "No badges found (optional but nice for project visibility)",
                "info"
            ))
        else:
            self.results.append(ValidationResult(
                "badges",
                True,
                f"Found {badges} badge(s)",
                "info"
            ))
    
    def print_report(self):
        """Print validation report."""
        passed, results = self.validate()
        
        print("\n" + "="*60)
        print("📋 README VALIDATION REPORT")
        print("="*60)
        print(f"File: {self.readme_path}")
        print(f"Mode: {'STRICT' if self.strict else 'STANDARD'}")
        print("="*60 + "\n")
        
        # Group by severity
        errors = [r for r in results if r.severity == "error" and not r.passed]
        warnings = [r for r in results if r.severity == "warning" and not r.passed]
        info = [r for r in results if r.passed or r.severity == "info"]
        
        if errors:
            print("❌ ERRORS:")
            for result in errors:
                print(f"   • {result.section}: {result.message}")
            print()
        
        if warnings:
            print("⚠️  WARNINGS:")
            for result in warnings:
                print(f"   • {result.section}: {result.message}")
            print()
        
        if info:
            print("ℹ️  INFO:")
            for result in info:
                status = "✅" if result.passed else "ℹ️"
                print(f"   {status} {result.section}: {result.message}")
            print()
        
        print("="*60)
        if passed:
            print("✅ README VALIDATION PASSED")
        else:
            print("❌ README VALIDATION FAILED")
            if errors:
                print(f"   {len(errors)} error(s) must be fixed")
            if warnings and self.strict:
                print(f"   {len(warnings)} warning(s) must be addressed (strict mode)")
        print("="*60 + "\n")
        
        return passed


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate README.md for completeness and quality"
    )
    parser.add_argument(
        '--readme',
        type=Path,
        help='Path to README.md (default: project root README.md)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )
    
    args = parser.parse_args()
    
    validator = ReadmeValidator(args.readme, args.strict)
    passed = validator.print_report()
    
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()

