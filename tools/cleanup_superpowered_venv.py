#!/usr/bin/env python3
"""
Cleanup Superpowered-TTRPG Venv Files - Agent-7
================================================

Removes virtual environment files from Superpowered-TTRPG repository.
Following Agent-2's execute_dreamvault_cleanup.py pattern.

Author: Agent-7
Date: 2025-11-27
Priority: HIGH (CRITICAL - 2,079 venv files detected)
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
import stat
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
from src.core.config.timeout_constants import TimeoutConstants
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
                    if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return None


def get_github_username() -> Optional[str]:
    """Get GitHub username from environment or .env file."""
    username = os.getenv("GITHUB_USERNAME", "Dadudekc")
    env_path = Path(".env")
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GITHUB_USERNAME="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return username


def ensure_dir_removed(dir_path: Path, name: str):
    """Ensure directory is completely removed."""
    if dir_path.exists():
        print(f"🧹 Removing {name} directory: {dir_path}")
        try:
            shutil.rmtree(dir_path, ignore_errors=True)
            time.sleep(0.5)
            if dir_path.exists():
                def remove_readonly(func, path, exc):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                shutil.rmtree(dir_path, onerror=remove_readonly)
                time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Cleanup warning for {name}: {e}")


def remove_virtual_env_files(repo_dir: Path) -> int:
    """Remove virtual environment files and directories."""
    venv_patterns = [
        "venv",
        ".venv",
        "env",
        ".env",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd"
    ]
    
    removed_count = 0
    
    # Remove venv directories
    for pattern in ["venv", ".venv", "env"]:
        venv_dir = repo_dir / pattern
        if venv_dir.exists() and venv_dir.is_dir():
            print(f"🧹 Removing {pattern}/ directory...")
            ensure_dir_removed(venv_dir, pattern)
            removed_count += 1
    
    # Remove __pycache__ directories
    for pycache_dir in repo_dir.rglob("__pycache__"):
        if pycache_dir.is_dir():
            print(f"🧹 Removing {pycache_dir.relative_to(repo_dir)}...")
            ensure_dir_removed(pycache_dir, "__pycache__")
            removed_count += 1
    
    # Remove .pyc, .pyo, .pyd files
    for ext in [".pyc", ".pyo", ".pyd"]:
        for pyc_file in repo_dir.rglob(f"*{ext}"):
            if pyc_file.is_file():
                try:
                    pyc_file.unlink()
                    removed_count += 1
                except Exception as e:
                    print(f"⚠️ Could not remove {pyc_file.relative_to(repo_dir)}: {e}")
    
    return removed_count


def update_gitignore(repo_dir: Path):
    """Update .gitignore to exclude venv files."""
    gitignore_path = repo_dir / ".gitignore"
    
    venv_patterns = [
        "# Virtual Environment",
        "venv/",
        ".venv/",
        "env/",
        ".env/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "*.py[cod]",
        "*$py.class"
    ]
    
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        
        # Check if venv patterns already exist
        has_venv_patterns = any(pattern in content for pattern in ["venv/", ".venv/", "__pycache__/"])
        
        if not has_venv_patterns:
            print("📝 Updating .gitignore with venv patterns...")
            content += "\n" + "\n".join(venv_patterns) + "\n"
            gitignore_path.write_text(content, encoding="utf-8")
            print("✅ .gitignore updated")
        else:
            print("✅ .gitignore already has venv patterns")
    else:
        print("📝 Creating .gitignore with venv patterns...")
        gitignore_path.write_text("\n".join(venv_patterns) + "\n", encoding="utf-8")
        print("✅ .gitignore created")


def clone_repo(temp_base: Path, token: str, username: str, repo_name: str) -> Optional[Path]:
    """Clone repository."""
    owner = "Dadudekc"
    repo_dir = temp_base / repo_name
    
    try:
        repo_url = f"https://{username}:{token}@github.com/{owner}/{repo_name}.git"
        print(f"📥 Cloning {repo_name}...")
        subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            check=True,
            capture_output=True,
            timeout=TimeoutConstants.HTTP_EXTENDED
        )
        print(f"✅ Cloned {repo_name} successfully")
        return repo_dir
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clone {repo_name}: {e.stderr.decode() if e.stderr else str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error cloning {repo_name}: {e}")
        return None


def commit_and_push(repo_dir: Path, token: str, username: str, repo_name: str):
    """Commit and push cleanup changes."""
    try:
        # Configure git
        subprocess.run(
            ["git", "config", "user.name", "Agent-7"],
            cwd=repo_dir,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "agent-7@swarm.ai"],
            cwd=repo_dir,
            check=True,
            capture_output=True
        )
        
        # Add changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_dir,
            check=True,
            capture_output=True
        )
        
        # Check if there are changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("ℹ️ No changes to commit (venv files may have been in .gitignore)")
            return True
        
        # Commit
        subprocess.run(
            ["git", "commit", "-m", "Cleanup: Remove virtual environment files (Agent-7)"],
            cwd=repo_dir,
            check=True,
            capture_output=True
        )
        print("✅ Changes committed")
        
        # Push
        repo_url = f"https://{username}:{token}@github.com/Dadudekc/{repo_name}.git"
        subprocess.run(
            ["git", "push", repo_url, "main"],
            cwd=repo_dir,
            check=True,
            capture_output=True
        )
        print("✅ Changes pushed to GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git operation failed: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        print(f"⚠️ Error with git operations: {e}")
        return False


def main():
    """Main execution."""
    print("=" * 60)
    print("🧹 SUPERPOWERED-TTRPG VENV CLEANUP")
    print("=" * 60)
    print()
    
    token = get_github_token()
    if not token:
        print("❌ ERROR: GITHUB_TOKEN or GH_TOKEN required")
        sys.exit(1)
    
    username = get_github_username()
    repo_name = "Superpowered-TTRPG"
    
    # Create temp directory
    temp_base = Path(tempfile.gettempdir()) / "superpowered_venv_cleanup"
    temp_base.mkdir(exist_ok=True)
    
    try:
        # Clone repo
        repo_dir = clone_repo(temp_base, token, username, repo_name)
        if not repo_dir:
            sys.exit(1)
        
        # Remove venv files
        print("\n🧹 Removing virtual environment files...")
        removed_count = remove_virtual_env_files(repo_dir)
        print(f"✅ Removed {removed_count} venv items")
        
        # Update .gitignore
        print("\n📝 Updating .gitignore...")
        update_gitignore(repo_dir)
        
        # Commit and push
        print("\n💾 Committing and pushing changes...")
        if commit_and_push(repo_dir, token, username, repo_name):
            print("\n✅ Venv cleanup complete!")
        else:
            print("\n⚠️ Cleanup complete but push failed (check manually)")
        
    finally:
        # Cleanup temp directory
        if temp_base.exists():
            print(f"\n🧹 Cleaning up temp directory...")
            ensure_dir_removed(temp_base, "temp")
    
    print("\n" + "=" * 60)
    print("✅ CLEANUP COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()







