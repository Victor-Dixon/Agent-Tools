#!/usr/bin/env python3
"""
Find GitHub Token Tool
======================

Searches for FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN in:
- Environment variables
- .env files
- Configuration files
- Any other files in the repository

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-20
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import re

# Add project root to path if running from tools directory
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))


def search_environment_variables() -> Dict[str, Optional[str]]:
    """Search for token in environment variables."""
    results = {}
    token_name = "FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN"
    
    # Check current environment
    token = os.getenv(token_name)
    if token:
        results["environment"] = f"Found in environment: {token[:10]}...{token[-4:] if len(token) > 14 else ''}"
    else:
        results["environment"] = "Not found in environment variables"
    
    return results


def search_env_files(search_path: Path) -> List[Dict[str, str]]:
    """Search for token in .env files."""
    results = []
    token_pattern = re.compile(r'FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN\s*=\s*(.+)', re.IGNORECASE)
    
    # Common .env file locations
    env_files = [
        search_path / ".env",
        search_path / ".env.local",
        search_path / ".env.production",
        search_path / "env.example",
        search_path / ".envexample",
    ]
    
    # Also search for any .env* files
    for env_file in search_path.rglob(".env*"):
        if env_file.is_file() and env_file not in env_files:
            env_files.append(env_file)
    
    for env_file in env_files:
        if env_file.exists() and env_file.is_file():
            try:
                with open(env_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        match = token_pattern.search(line)
                        if match:
                            token_value = match.group(1).strip().strip('"').strip("'")
                            # Mask token for display
                            masked = f"{token_value[:10]}...{token_value[-4:]}" if len(token_value) > 14 else "***"
                            results.append({
                                "file": str(env_file.relative_to(search_path)),
                                "line": line_num,
                                "token_preview": masked,
                                "full_path": str(env_file)
                            })
            except Exception as e:
                pass  # Skip files we can't read
    
    return results


def search_config_files(search_path: Path) -> List[Dict[str, str]]:
    """Search for token in configuration files."""
    results = []
    token_name = "FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN"
    
    # Common config file patterns
    config_patterns = [
        "**/*config*.json",
        "**/*config*.yaml",
        "**/*config*.yml",
        "**/*.credentials*",
        "**/*secrets*",
        "**/*.key*",
    ]
    
    for pattern in config_patterns:
        for config_file in search_path.rglob(pattern):
            if config_file.is_file() and config_file.suffix in ['.json', '.yaml', '.yml', '.txt', '.py']:
                try:
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if token_name in content:
                            # Try to extract token value
                            token_pattern = re.compile(
                                rf'{re.escape(token_name)}\s*[:=]\s*["\']?([^"\'\s]+)["\']?',
                                re.IGNORECASE
                            )
                            match = token_pattern.search(content)
                            if match:
                                token_value = match.group(1)
                                masked = f"{token_value[:10]}...{token_value[-4:]}" if len(token_value) > 14 else "***"
                                results.append({
                                    "file": str(config_file.relative_to(search_path)),
                                    "token_preview": masked,
                                    "full_path": str(config_file)
                                })
                except Exception:
                    pass
    
    return results


def search_code_files(search_path: Path) -> List[Dict[str, str]]:
    """Search for token references in code files."""
    results = []
    token_name = "FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN"
    
    # Search Python files
    for py_file in search_path.rglob("*.py"):
        if py_file.is_file():
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if token_name in line:
                            results.append({
                                "file": str(py_file.relative_to(search_path)),
                                "line": line_num,
                                "code_snippet": line.strip()[:100],
                                "full_path": str(py_file)
                            })
                            break  # Only report once per file
            except Exception:
                pass
    
    return results


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Find FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN")
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="Path to search (default: current directory or Agent_Cellphone_V2_Repository)"
    )
    parser.add_argument(
        "--show-token",
        action="store_true",
        help="Show full token (use with caution)"
    )
    
    args = parser.parse_args()
    
    # Determine search path
    if args.path:
        search_path = Path(args.path)
    else:
        # Try to find Agent_Cellphone_V2_Repository
        current = Path.cwd()
        if "Agent_Cellphone_V2_Repository" in str(current):
            search_path = current
        else:
            # Try parent directories
            for parent in current.parents:
                if parent.name == "Agent_Cellphone_V2_Repository":
                    search_path = parent
                    break
            else:
                search_path = current
    
    if not search_path.exists():
        print(f"❌ Path not found: {search_path}")
        return 1
    
    print(f"🔍 Searching for FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN")
    print(f"📁 Search path: {search_path}")
    print("=" * 60)
    
    # Search environment variables
    print("\n1️⃣ Environment Variables:")
    env_results = search_environment_variables()
    for key, value in env_results.items():
        print(f"   {key}: {value}")
    
    # Search .env files
    print("\n2️⃣ .env Files:")
    env_files = search_env_files(search_path)
    if env_files:
        for result in env_files:
            print(f"   ✅ Found in: {result['file']} (line {result['line']})")
            if args.show_token:
                print(f"      Token: {result.get('token_preview', 'N/A')}")
            else:
                print(f"      Token preview: {result.get('token_preview', 'N/A')}")
    else:
        print("   ❌ Not found in .env files")
    
    # Search config files
    print("\n3️⃣ Configuration Files:")
    config_files = search_config_files(search_path)
    if config_files:
        for result in config_files:
            print(f"   ✅ Found in: {result['file']}")
            if args.show_token:
                print(f"      Token: {result.get('token_preview', 'N/A')}")
            else:
                print(f"      Token preview: {result.get('token_preview', 'N/A')}")
    else:
        print("   ❌ Not found in configuration files")
    
    # Search code files (references)
    print("\n4️⃣ Code File References:")
    code_files = search_code_files(search_path)
    if code_files:
        print(f"   ✅ Found {len(code_files)} file(s) referencing the token:")
        for result in code_files[:10]:  # Limit to first 10
            print(f"      - {result['file']}:{result.get('line', 'N/A')}")
            if 'code_snippet' in result:
                print(f"        {result['code_snippet']}")
        if len(code_files) > 10:
            print(f"      ... and {len(code_files) - 10} more files")
    else:
        print("   ❌ No code files found referencing the token")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    total_found = len(env_files) + len(config_files)
    if env_results.get("environment") and "Found" in env_results["environment"]:
        total_found += 1
    
    if total_found > 0:
        print(f"   ✅ Token found in {total_found} location(s)")
        if not args.show_token:
            print("   💡 Use --show-token to see token previews")
    else:
        print("   ❌ Token not found")
        print("   💡 Set it in environment or .env file:")
        print("      export FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN=your_token")
        print("      or add to .env file:")
        print("      FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN=your_token")
    
    return 0 if total_found > 0 else 1


if __name__ == "__main__":
    sys.exit(main())

