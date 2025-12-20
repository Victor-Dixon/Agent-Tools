#!/usr/bin/env python3
"""
Execute DreamVault Cleanup - Agent-2
=====================================

Executes cleanup of DreamVault repository:
1. Removes virtual environment files
2. Resolves code duplicates (keeps SSOT versions)
3. Updates .gitignore
4. Commits changes
"""

from src.core.utils.file_utils import ensure_directory_removed as ensure_dir_removed
import os
import sys
import subprocess
import tempfile
import shutil
import time
import stat
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30
        HTTP_MEDIUM = 60
        HTTP_LONG = 120
        HTTP_EXTENDED = 300
        HTTP_SHORT = 10

try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or .env file."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token

    env_path = Path(".env")
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GITHUB_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return None


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


def remove_virtual_env_files(repo_dir: Path) -> int:
    """Remove virtual environment files and directories."""
    removed_count = 0

    # Patterns to remove
    patterns = [
        "**/lib/python*/site-packages/**",
        "**/lib64/python*/site-packages/**",
        "**/venv/**",
        "**/env/**",
        "**/.venv/**",
        "**/virtualenv/**",
    ]

    print("🧹 Removing virtual environment files...")

    # Remove directories first
    for pattern in patterns:
        matches = list(repo_dir.glob(pattern))
        for match in matches:
            if match.is_dir() and ".git" not in match.parts:
                try:
                    shutil.rmtree(match, ignore_errors=True)
                    removed_count += 1
                    if removed_count % 100 == 0:
                        print(f"   Removed {removed_count} items...")
                except Exception as e:
                    print(f"⚠️ Could not remove {match}: {e}")

    # Remove __pycache__ directories
    for pycache in repo_dir.rglob("__pycache__"):
        if pycache.is_dir() and ".git" not in pycache.parts:
            try:
                shutil.rmtree(pycache, ignore_errors=True)
                removed_count += 1
            except Exception:
                pass

    # Remove .pyc, .pyo, .pyd files
    for ext in ["*.pyc", "*.pyo", "*.pyd"]:
        for file_path in repo_dir.rglob(ext):
            if ".git" not in file_path.parts:
                try:
                    file_path.unlink()
                    removed_count += 1
                except Exception:
                    pass

    print(f"✅ Removed {removed_count} virtual environment items")
    return removed_count


def identify_code_duplicates(repo_dir: Path, exclude_patterns: List[str]) -> Dict[str, List[Path]]:
    """Identify code duplicates."""
    duplicates = defaultdict(list)

    for file_path in repo_dir.rglob("*.py"):
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            continue
        if ".git" in file_path.parts or "__pycache__" in file_path.parts:
            continue
        duplicates[file_path.name].append(file_path)

    return {name: paths for name, paths in duplicates.items() if len(paths) > 1}


def determine_ssot_version(file_paths: List[Path], repo_dir: Path) -> Optional[Path]:
    """Determine SSOT version to keep."""
    for path in file_paths:
        path_str = str(path.relative_to(repo_dir)).lower()
        if "digitaldreamscape" not in path_str and "thea" not in path_str and "dreambank" not in path_str:
            return path
        if path.parent == repo_dir or len(path.relative_to(repo_dir).parts) <= 2:
            return path
    return file_paths[0] if file_paths else None


def resolve_code_duplicates(repo_dir: Path) -> int:
    """Resolve code duplicates by removing non-SSOT versions."""
    exclude_patterns = ["lib/python",
                        "site-packages", "venv", "env", "__pycache__"]
    code_duplicates = identify_code_duplicates(repo_dir, exclude_patterns)

    removed_count = 0

    print(f"🔧 Resolving {len(code_duplicates)} code duplicate groups...")

    for name, paths in code_duplicates.items():
        ssot = determine_ssot_version(paths, repo_dir)
        if not ssot:
            continue

        for path in paths:
            if path != ssot and path.exists():
                try:
                    path.unlink()
                    removed_count += 1
                    if removed_count % 10 == 0:
                        print(f"   Removed {removed_count} duplicate files...")
                except Exception as e:
                    print(f"⚠️ Could not remove {path}: {e}")

    print(f"✅ Removed {removed_count} duplicate files")
    return removed_count


def update_gitignore(repo_dir: Path) -> bool:
    """Update .gitignore with virtual environment patterns."""
    gitignore_path = repo_dir / ".gitignore"

    patterns_to_add = [
        "# Virtual environment files",
        "lib/python*/site-packages/",
        "venv/",
        "env/",
        ".venv/",
        "virtualenv/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache/",
    ]

    existing_content = ""
    if gitignore_path.exists():
        existing_content = gitignore_path.read_text(encoding="utf-8")

    # Check if patterns already exist
    if any(pattern in existing_content for pattern in patterns_to_add[1:]):
        print("✅ .gitignore already contains virtual environment patterns")
        return True

    # Add patterns
    new_content = existing_content
    if not new_content.endswith("\n"):
        new_content += "\n"
    new_content += "\n" + "\n".join(patterns_to_add) + "\n"

    gitignore_path.write_text(new_content, encoding="utf-8")
    print("✅ Updated .gitignore")
    return True


def commit_changes(repo_dir: Path, token: str, username: str) -> bool:
    """Commit cleanup changes."""
    try:
        # Configure git
        subprocess.run(
            ["git", "config", "user.name", username],
            cwd=repo_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT
        )
        subprocess.run(
            ["git", "config", "user.email",
                f"{username}@users.noreply.github.com"],
            cwd=repo_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT
        )

        # Add all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_dir, check=True, timeout=TimeoutConstants.HTTP_MEDIUM
        )

        # Check if there are changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
        )

        if not status.stdout.strip():
            print("ℹ️ No changes to commit")
            return True

        # Commit
        commit_message = "Cleanup: Remove virtual environment files and resolve code duplicates"
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_dir, check=True, timeout=TimeoutConstants.HTTP_MEDIUM
        )
        print("✅ Changes committed")

        # Push
        repo_url = f"https://{username}:{token}@github.com/Dadudekc/DreamVault.git"
        subprocess.run(
            ["git", "push", "origin", "master"],
            cwd=repo_dir, check=True, timeout=TimeoutConstants.HTTP_LONG
        )
        print("✅ Changes pushed to repository")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error during commit: {e}")
        return False


def main():
    """Main entry point."""
    token = get_github_token()
    username = get_github_username()

    if not token or not username:
        print("❌ GITHUB_TOKEN or GITHUB_USERNAME not found.")
        return 1

    timestamp = int(time.time() * 1000000)
    temp_base = Path(tempfile.mkdtemp(
        prefix=f"dreamvault_cleanup_{timestamp}_"))

    try:
        # Clone repository
        repo_dir = clone_dreamvault(temp_base, token, username)
        if not repo_dir:
            return 1

        # Remove virtual environment files
        venv_removed = remove_virtual_env_files(repo_dir)

        # Resolve code duplicates
        duplicates_removed = resolve_code_duplicates(repo_dir)

        # Update .gitignore
        update_gitignore(repo_dir)

        # Commit and push changes
        if venv_removed > 0 or duplicates_removed > 0:
            commit_changes(repo_dir, token, username)

        print("\n" + "="*60)
        print("✅ DREAMVAULT CLEANUP COMPLETE")
        print("="*60)
        print(f"   Virtual environment files removed: {venv_removed}")
        print(f"   Code duplicates removed: {duplicates_removed}")
        print(f"   .gitignore updated")
        print(f"   Changes committed and pushed")

        return 0

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ensure_dir_removed(temp_base, "temp_repo_clone")


if __name__ == "__main__":
    sys.exit(main())
