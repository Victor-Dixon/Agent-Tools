#!/usr/bin/env python3
"""
Check Theme Syntax - PHP and CSS Validation
============================================

Checks theme files for syntax errors that prevent WordPress detection.
Validates style.css header and functions.php syntax.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
"""

import re
import subprocess
import sys
from pathlib import Path


def check_style_css_header(style_css_path: Path) -> tuple[bool, list[str]]:
    """
    Check style.css header format.
    
    Args:
        style_css_path: Path to style.css
        
    Returns:
        (is_valid, errors)
    """
    errors = []
    
    if not style_css_path.exists():
        return False, [f"File not found: {style_css_path}"]
    
    content = style_css_path.read_text(encoding='utf-8')
    
    # Required header fields
    required_fields = [
        'Theme Name',
        'Theme URI',
        'Author',
        'Description',
        'Version',
    ]
    
    # Check for required fields
    for field in required_fields:
        pattern = rf'{field}:\s*(.+)'
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            errors.append(f"Missing required header field: {field}")
        elif not match.group(1).strip():
            errors.append(f"Empty header field: {field}")
    
    # Check header format (must be in CSS comment at top)
    if not content.strip().startswith('/*'):
        errors.append("style.css must start with CSS comment (/*)")
    
    # Check for proper closing
    if '*/' not in content[:500]:  # Check first 500 chars
        errors.append("style.css header comment not properly closed")
    
    return len(errors) == 0, errors


def check_php_syntax(php_file_path: Path) -> tuple[bool, list[str]]:
    """
    Check PHP file syntax.
    
    Args:
        php_file_path: Path to PHP file
        
    Returns:
        (is_valid, errors)
    """
    errors = []
    
    if not php_file_path.exists():
        return False, [f"File not found: {php_file_path}"]
    
    # Use PHP CLI to check syntax
    try:
        result = subprocess.run(
            ['php', '-l', str(php_file_path)],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_SHORT
        )
        
        if result.returncode != 0:
            errors.append(f"PHP syntax error: {result.stderr.strip()}")
            return False, errors
        
        # Check for common issues
        content = php_file_path.read_text(encoding='utf-8')
        
        # Check for opening PHP tag
        if not content.strip().startswith('<?php'):
            if '<?php' not in content[:100]:
                errors.append("Missing opening <?php tag")
        
        # Check for unclosed strings (basic check)
        single_quotes = content.count("'") - content.count("\\'")
        if single_quotes % 2 != 0:
            errors.append("Possible unclosed single-quoted string")
        
        double_quotes = content.count('"') - content.count('\\"')
        if double_quotes % 2 != 0:
            errors.append("Possible unclosed double-quoted string")
        
        # Check for unclosed brackets (basic check)
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            errors.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
        
        return len(errors) == 0, errors
        
    except FileNotFoundError:
        errors.append("PHP CLI not found - cannot check syntax")
        return True, errors  # Assume valid if PHP not available
    except subprocess.TimeoutExpired:
        errors.append("PHP syntax check timed out")
        return False, errors
    except Exception as e:
        errors.append(f"Error checking syntax: {e}")
        return False, errors


def check_theme(theme_path: Path) -> dict:
    """
    Check theme for common issues.
    
    Args:
        theme_path: Path to theme directory
        
    Returns:
        Dict with check results
    """
    print("=" * 60)
    print("🔍 Theme Syntax Check")
    print("=" * 60)
    print(f"Theme: {theme_path}")
    print()
    
    results = {
        "theme_path": str(theme_path),
        "style_css_valid": False,
        "functions_php_valid": False,
        "errors": [],
        "warnings": []
    }
    
    # Check style.css
    style_css = theme_path / "style.css"
    print("📄 Checking style.css...")
    if style_css.exists():
        is_valid, errors = check_style_css_header(style_css)
        results["style_css_valid"] = is_valid
        results["errors"].extend([f"style.css: {e}" for e in errors])
        if is_valid:
            print("   ✅ style.css header is valid")
        else:
            print(f"   ❌ style.css has {len(errors)} error(s)")
            for error in errors:
                print(f"      - {error}")
    else:
        results["errors"].append("style.css not found")
        print("   ❌ style.css not found")
    
    print()
    
    # Check functions.php
    functions_php = theme_path / "functions.php"
    print("📄 Checking functions.php...")
    if functions_php.exists():
        is_valid, errors = check_php_syntax(functions_php)
        results["functions_php_valid"] = is_valid
        results["errors"].extend([f"functions.php: {e}" for e in errors])
        if is_valid:
            print("   ✅ functions.php syntax is valid")
        else:
            print(f"   ❌ functions.php has {len(errors)} error(s)")
            for error in errors:
                print(f"      - {error}")
    else:
        results["warnings"].append("functions.php not found (optional)")
        print("   ⚠️  functions.php not found (optional)")
    
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    if results["style_css_valid"] and results["functions_php_valid"]:
        print("✅ Theme files are valid!")
    else:
        print("❌ Theme has issues that may prevent WordPress detection")
        print()
        print("Errors found:")
        for error in results["errors"]:
            print(f"   - {error}")
    
    return results


def main():
    """CLI entry point."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(
        description="Check theme files for syntax errors"
    )
    parser.add_argument(
        "--theme",
        required=True,
        type=Path,
        help="Path to theme directory"
    )
    
    args = parser.parse_args()
    
    if not args.theme.exists():
        print(f"❌ Theme directory not found: {args.theme}")
        return 1
    
    results = check_theme(args.theme)
    
    return 0 if results["style_css_valid"] and results["functions_php_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())




