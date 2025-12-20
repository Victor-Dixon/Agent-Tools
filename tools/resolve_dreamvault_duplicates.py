#!/usr/bin/env python3
"""
Resolve DreamVault Duplicate Files - Agent-2
===========================================

Helps resolve duplicate files in DreamVault repository by:
1. Identifying virtual environment files to remove
2. Identifying actual code duplicates
3. Providing cleanup recommendations
"""

from src.core.utils.file_utils import ensure_directory_removed as ensure_dir_removed
from src.core.utils.github_utils import get_github_token
import os
import sys
import subprocess
import tempfile
import shutil
import time
import stat
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


# SSOT: Use github_utils.get_github_token() instead

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_EXTENDED = 300


def get_github_username() -> Optional[str]:
    """Get GitHub username from environment or .env file."""
    username = os.getenv("GITHUB_USERNAME")
    if username:
        return username

    env_path = Path(".env")
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GITHUB_USERNAME="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return None


# Use SSOT utility for directory removal


def clone_dreamvault(temp_base: Path, token: str, username: str) -> Optional[Path]:
    """Clone DreamVault repository."""
    owner = "Dadudekc"
    repo = "DreamVault"
    repo_dir = temp_base / repo

    try:
        repo_url = f"https://{username}:{token}@github.com/{owner}/{repo}.git"
        print(f"📥 Cloning {repo}...")
        subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            check=True, timeout=TimeoutConstants.HTTP_EXTENDED, capture_output=True, text=True
        )
        print(f"✅ Cloned {repo} successfully")
        return repo_dir
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clone {repo}: {e.stderr}")
        return None
    except Exception as e:
        print(f"❌ Error cloning {repo}: {e}")
        return None


def identify_virtual_env_files(repo_dir: Path) -> List[Path]:
    """Identify virtual environment files that should be removed."""
    virtual_env_paths = []

    # Common virtual environment patterns
    patterns = [
        "**/lib/python*/site-packages/**",
        "**/lib64/python*/site-packages/**",
        "**/venv/**",
        "**/env/**",
        "**/.venv/**",
        "**/virtualenv/**",
        "**/__pycache__/**",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.pytest_cache/**",
    ]

    print("🔍 Identifying virtual environment files...")
    for pattern in patterns:
        matches = list(repo_dir.glob(pattern))
        for match in matches:
            if match.is_file() or match.is_dir():
                # Skip .git directory
                if ".git" not in match.parts:
                    virtual_env_paths.append(match)

    return virtual_env_paths


def identify_code_duplicates(repo_dir: Path, exclude_patterns: List[str]) -> Dict[str, List[Path]]:
    """Identify actual code duplicates (excluding virtual env files)."""
    duplicates = defaultdict(list)

    print("🔍 Identifying code duplicates (excluding virtual env)...")
    for file_path in repo_dir.rglob("*.py"):
        # Skip virtual env files
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            continue

        # Skip .git directory
        if ".git" in file_path.parts:
            continue

        # Skip __pycache__
        if "__pycache__" in file_path.parts:
            continue

        duplicates[file_path.name].append(file_path)

    # Filter to only actual duplicates (2+ files with same name)
    return {name: paths for name, paths in duplicates.items() if len(paths) > 1}


def determine_ssot_version(file_paths: List[Path], repo_dir: Path) -> Optional[Path]:
    """Determine which version should be kept (SSOT principle)."""
    # Priority order:
    # 1. Files in root or main directories (not in merged repo directories)
    # 2. Files in DreamVault original structure
    # 3. Files not in DigitalDreamscape, Thea, or DreamBank directories

    for path in file_paths:
        path_str = str(path.relative_to(repo_dir)).lower()

        # Prefer files not in merged repo directories
        if "digitaldreamscape" not in path_str and "thea" not in path_str and "dreambank" not in path_str:
            return path

        # Prefer files in root or main directories
        if path.parent == repo_dir or len(path.relative_to(repo_dir).parts) <= 2:
            return path

    # Default: first file
    return file_paths[0] if file_paths else None


def generate_cleanup_report(repo_dir: Path, virtual_env_files: List[Path], code_duplicates: Dict) -> str:
    """Generate cleanup report with recommendations."""
    report = []
    report.append("="*60)
    report.append("📋 DREAMVAULT DUPLICATE RESOLUTION REPORT")
    report.append("="*60)

    report.append(f"\n📁 Virtual Environment Files to Remove:")
    report.append(f"   Total: {len(virtual_env_files)} files/directories")

    # Group by directory
    venv_dirs = defaultdict(list)
    for path in virtual_env_files:
        if path.is_dir():
            venv_dirs["directories"].append(path)
        else:
            parent = path.parent
            venv_dirs[str(parent)].append(path)

    report.append(f"   Directories: {len(venv_dirs.get('directories', []))}")
    report.append(
        f"   Files: {len(virtual_env_files) - len(venv_dirs.get('directories', []))}")

    # Show top directories
    if venv_dirs.get("directories"):
        report.append(f"\n   Top directories to remove:")
        for dir_path in sorted(venv_dirs["directories"], key=lambda x: str(x))[:10]:
            rel_path = dir_path.relative_to(repo_dir)
            report.append(f"      - {rel_path}")

    report.append(f"\n📋 Code Duplicates to Resolve:")
    report.append(f"   Total: {len(code_duplicates)} duplicate file names")

    # Show top duplicates
    sorted_dups = sorted(code_duplicates.items(),
                         key=lambda x: len(x[1]), reverse=True)[:10]
    report.append(f"\n   Top 10 code duplicates:")
    for name, paths in sorted_dups:
        report.append(f"      {name}: {len(paths)} locations")
        ssot = determine_ssot_version(paths, repo_dir)
        if ssot:
            report.append(f"         SSOT: {ssot.relative_to(repo_dir)}")
            for path in paths[:3]:
                if path != ssot:
                    rel_path = path.relative_to(repo_dir)
                    report.append(f"         Remove: {rel_path}")
        if len(paths) > 3:
            report.append(f"         ... and {len(paths) - 3} more")

    report.append(f"\n🔧 Recommended Actions:")
    report.append(f"   1. Remove virtual environment directories:")
    report.append(f"      - DigitalDreamscape/lib/python3.11/site-packages/")
    report.append(f"      - Any other venv/env directories")
    report.append(f"   2. Add to .gitignore:")
    report.append(f"      - lib/python*/site-packages/")
    report.append(f"      - venv/")
    report.append(f"      - env/")
    report.append(f"      - __pycache__/")
    report.append(f"      - *.pyc")
    report.append(f"   3. Resolve code duplicates:")
    report.append(f"      - Keep SSOT versions (DreamVault original)")
    report.append(f"      - Remove duplicates from merged repos")
    report.append(f"      - Update imports if needed")
    report.append(f"   4. Ensure dependencies in requirements.txt")

    return "\n".join(report)


def main():
    """Main entry point."""
    token = get_github_token()
    username = get_github_username()

    if not token or not username:
        print("❌ GITHUB_TOKEN or GITHUB_USERNAME not found.")
        return 1

    # Create temp directory
    timestamp = int(time.time() * 1000000)
    temp_base = Path(tempfile.mkdtemp(
        prefix=f"dreamvault_resolve_{timestamp}_"))

    try:
        # Clone repository
        repo_dir = clone_dreamvault(temp_base, token, username)
        if not repo_dir:
            return 1

        # Identify virtual environment files
        print("\n🔍 Identifying virtual environment files...")
        virtual_env_files = identify_virtual_env_files(repo_dir)

        # Identify code duplicates (excluding virtual env)
        exclude_patterns = ["lib/python",
                            "site-packages", "venv", "env", "__pycache__"]
        code_duplicates = identify_code_duplicates(repo_dir, exclude_patterns)

        # Generate cleanup report
        print("\n📋 Generating cleanup report...")
        report = generate_cleanup_report(
            repo_dir, virtual_env_files, code_duplicates)
        print(report)

        # Save report to file
        report_file = project_root / "agent_workspaces" / \
            "Agent-2" / "DREAMVAULT_CLEANUP_REPORT.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ Cleanup report saved to: {report_file}")

        return 0

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ensure_dir_removed(temp_base, "temp_repo_clone")


if __name__ == "__main__":
    sys.exit(main())
