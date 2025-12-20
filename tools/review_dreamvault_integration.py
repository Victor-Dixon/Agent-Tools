#!/usr/bin/env python3
"""
Review DreamVault Integration - Agent-2
=====================================

Reviews DreamVault repository structure and verifies merged repos logic integration.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
import stat
from pathlib import Path
from typing import Dict, List, Optional

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


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or .env file."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token
    
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, "r") as f:
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
    
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("GITHUB_USERNAME="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return None


# Use SSOT utility for directory removal
from src.core.utils.file_utils import ensure_directory_removed
from src.core.config.timeout_constants import TimeoutConstants

# Alias for backward compatibility
def ensure_dir_removed(dir_path: Path, name: str):
    """Ensure directory is completely removed (uses SSOT utility)."""
    ensure_directory_removed(dir_path, name)


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


def check_git_history(repo_dir: Path) -> Dict:
    """Check git history for merge commits from merged repos."""
    merges = {
        "DreamBank": {"found": False, "commits": []},
        "DigitalDreamscape": {"found": False, "commits": []},
        "Thea": {"found": False, "commits": []}
    }
    
    try:
        # Check for merge commits
        result = subprocess.run(
            ["git", "log", "--all", "--merges", "--oneline", "--grep", "DreamBank"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
        )
        if result.returncode == 0 and result.stdout.strip():
            merges["DreamBank"]["found"] = True
            merges["DreamBank"]["commits"] = result.stdout.strip().split("\n")[:5]
        
        result = subprocess.run(
            ["git", "log", "--all", "--merges", "--oneline", "--grep", "DigitalDreamscape"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
        )
        if result.returncode == 0 and result.stdout.strip():
            merges["DigitalDreamscape"]["found"] = True
            merges["DigitalDreamscape"]["commits"] = result.stdout.strip().split("\n")[:5]
        
        result = subprocess.run(
            ["git", "log", "--all", "--merges", "--oneline", "--grep", "Thea"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
        )
        if result.returncode == 0 and result.stdout.strip():
            merges["Thea"]["found"] = True
            merges["Thea"]["commits"] = result.stdout.strip().split("\n")[:5]
    except Exception as e:
        print(f"⚠️ Could not check git history: {e}")
    
    return merges


def analyze_repo_structure(repo_dir: Path) -> Dict:
    """Analyze repository structure and identify merged repos."""
    structure = {
        "total_files": 0,
        "python_files": 0,
        "directories": [],
        "merged_repos": {
            "DreamBank": {"found": False, "files": [], "directories": [], "indicators": []},
            "DigitalDreamscape": {"found": False, "files": [], "directories": [], "indicators": []},
            "Thea": {"found": False, "files": [], "directories": [], "indicators": []}
        },
        "root_files": [],
        "readme": None,
        "requirements": None
    }
    
    if not repo_dir.exists():
        return structure
    
    # Check for README
    readme_files = list(repo_dir.glob("README*"))
    if readme_files:
        structure["readme"] = str(readme_files[0].relative_to(repo_dir))
    
    # Check for requirements
    req_files = list(repo_dir.glob("requirements*.txt"))
    if req_files:
        structure["requirements"] = [str(f.relative_to(repo_dir)) for f in req_files]
    
    # Check git history for merge commits
    git_merges = check_git_history(repo_dir)
    for repo_name in structure["merged_repos"]:
        if git_merges[repo_name]["found"]:
            structure["merged_repos"][repo_name]["found"] = True
            structure["merged_repos"][repo_name]["indicators"].extend(git_merges[repo_name]["commits"])
    
    # Analyze directory structure
    for item in repo_dir.iterdir():
        if item.is_file():
            structure["total_files"] += 1
            structure["root_files"].append(item.name)
            if item.suffix == ".py":
                structure["python_files"] += 1
        elif item.is_dir() and item.name not in [".git", "__pycache__", ".pytest_cache"]:
            structure["directories"].append(item.name)
            
            # Check for merged repo indicators (more flexible matching)
            dir_lower = item.name.lower()
            if "dreambank" in dir_lower or "portfolio" in dir_lower or "bank" in dir_lower:
                structure["merged_repos"]["DreamBank"]["found"] = True
                structure["merged_repos"]["DreamBank"]["directories"].append(item.name)
            if "digitaldreamscape" in dir_lower or "dreamscape" in dir_lower:
                structure["merged_repos"]["DigitalDreamscape"]["found"] = True
                structure["merged_repos"]["DigitalDreamscape"]["directories"].append(item.name)
            if "thea" in dir_lower:
                structure["merged_repos"]["Thea"]["found"] = True
                structure["merged_repos"]["Thea"]["directories"].append(item.name)
    
    # Search for specific file patterns that indicate merged repos
    # DreamBank indicators: portfolio, stock, trading
    for pattern in ["*portfolio*", "*stock*", "*trading*"]:
        matches = list(repo_dir.rglob(pattern))
        if matches:
            structure["merged_repos"]["DreamBank"]["found"] = True
            structure["merged_repos"]["DreamBank"]["indicators"].append(f"Found {len(matches)} files matching {pattern}")
    
    # Thea indicators: thea, ai assistant, large framework
    for pattern in ["*thea*", "*assistant*", "*framework*"]:
        matches = list(repo_dir.rglob(pattern))
        if matches and "thea" in pattern.lower():
            structure["merged_repos"]["Thea"]["found"] = True
            structure["merged_repos"]["Thea"]["indicators"].append(f"Found {len(matches)} files matching {pattern}")
    
    # Count files in merged repo directories
    for repo_name, info in structure["merged_repos"].items():
        for dir_name in info["directories"]:
            dir_path = repo_dir / dir_name
            if dir_path.exists():
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        info["files"].append(str(file_path.relative_to(repo_dir)))
    
    return structure


def check_integration_points(repo_dir: Path) -> Dict:
    """Check for integration points and potential issues."""
    integration = {
        "imports": [],
        "duplicates": [],
        "conflicts": [],
        "dependencies": []
    }
    
    # Check for duplicate functionality
    python_files = list(repo_dir.rglob("*.py"))
    file_names = {}
    for py_file in python_files:
        name = py_file.name
        if name in file_names:
            integration["duplicates"].append({
                "file": name,
                "locations": [str(py_file.relative_to(repo_dir)), file_names[name]]
            })
        else:
            file_names[name] = str(py_file.relative_to(repo_dir))
    
    # Check for requirements files
    req_files = list(repo_dir.glob("requirements*.txt"))
    for req_file in req_files:
        try:
            with open(req_file, "r") as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                integration["dependencies"].extend(deps)
        except Exception:
            pass
    
    return integration


def print_analysis_report(structure: Dict, integration: Dict):
    """Print analysis report."""
    print("\n" + "="*60)
    print("📊 DREAMVAULT INTEGRATION ANALYSIS REPORT")
    print("="*60)
    
    print(f"\n📁 Repository Structure:")
    print(f"   Total Files: {structure['total_files']}")
    print(f"   Python Files: {structure['python_files']}")
    print(f"   Directories: {len(structure['directories'])}")
    if structure['readme']:
        print(f"   README: {structure['readme']}")
    if structure['requirements']:
        print(f"   Requirements: {', '.join(structure['requirements'])}")
    
    print(f"\n🔗 Merged Repos Status:")
    for repo_name, info in structure["merged_repos"].items():
        status = "✅ FOUND" if info["found"] else "❌ NOT FOUND"
        print(f"   {repo_name}: {status}")
        if info["found"]:
            if info["directories"]:
                print(f"      Directories: {', '.join(info['directories'])}")
            if info["files"]:
                print(f"      Files: {len(info['files'])}")
            if info["indicators"]:
                print(f"      Indicators: {len(info['indicators'])} found")
                for indicator in info["indicators"][:3]:  # Show first 3
                    print(f"         - {indicator[:80]}")
    
    print(f"\n🔍 Integration Analysis:")
    print(f"   Duplicate Files: {len(integration['duplicates'])}")
    if integration['duplicates']:
        print(f"   ⚠️ Duplicates found:")
        for dup in integration['duplicates'][:5]:  # Show first 5
            print(f"      - {dup['file']}: {len(dup['locations'])} locations")
    
    print(f"   Dependencies: {len(set(integration['dependencies']))} unique")
    
    print("\n" + "="*60)


def main():
    """Main entry point."""
    token = get_github_token()
    username = get_github_username()
    
    if not token or not username:
        print("❌ GITHUB_TOKEN or GITHUB_USERNAME not found.")
        return 1
    
    # Create temp directory
    timestamp = int(time.time() * 1000000)
    temp_base = Path(tempfile.mkdtemp(prefix=f"dreamvault_review_{timestamp}_"))
    
    try:
        # Clone repository
        repo_dir = clone_dreamvault(temp_base, token, username)
        if not repo_dir:
            return 1
        
        # Analyze structure
        print("\n🔍 Analyzing repository structure...")
        structure = analyze_repo_structure(repo_dir)
        
        # Check integration points
        print("🔍 Checking integration points...")
        integration = check_integration_points(repo_dir)
        
        # Print report
        print_analysis_report(structure, integration)
        
        # Summary
        print("\n📋 Summary:")
        merged_count = sum(1 for info in structure["merged_repos"].values() if info["found"])
        print(f"   Merged Repos Found: {merged_count}/3")
        if merged_count == 3:
            print("   ✅ All merged repos found in repository")
        else:
            print(f"   ⚠️ {3 - merged_count} merged repo(s) not clearly identified")
        
        if integration["duplicates"]:
            print(f"   ⚠️ {len(integration['duplicates'])} duplicate files found - may need cleanup")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    finally:
        ensure_dir_removed(temp_base, "temp_repo_clone")


if __name__ == "__main__":
    sys.exit(main())

