#!/usr/bin/env python3
"""
Execute Streamertools Duplicate Resolution - Agent-3
=====================================================

Resolves duplicate files in Streamertools repository:
1. GUI Components (4 duplicates each)
2. Style Manager (3 locations)
3. Test Files (3 locations)
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional

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


def clone_streamertools(temp_base: Path, token: str, username: str) -> Optional[Path]:
    """Clone Streamertools repository."""
    owner = "Dadudekc"
    repo = "Streamertools"
    repo_dir = temp_base / repo
    
    try:
        repo_url = f"https://{username}:{token}@github.com/{owner}/{repo}.git"
        print(f"📥 Cloning {repo}...")
        subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            check=True, timeout=TimeoutConstants.HTTP_EXTENDED, capture_output=True, text=True
        )
        print(f"✅ Cloned {repo}")
        return repo_dir
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clone {repo}: {e.stderr}")
        return None


def compare_files(file1: Path, file2: Path) -> bool:
    """Compare two files to see if they're identical."""
    try:
        if not file1.exists() or not file2.exists():
            return False
        return file1.read_bytes() == file2.read_bytes()
    except Exception:
        return False


def resolve_gui_components(repo_dir: Path) -> Dict[str, List[str]]:
    """Resolve GUI component duplicates."""
    ssot_base = repo_dir / "src" / "gui" / "components"
    duplicates = {
        "action_buttons.py": [
            "gui_components/action_buttons.py",
            "MeTuber/gui_components/action_buttons.py",
            "MeTuber/src/gui/components/action_buttons.py",
        ],
        "device_selector.py": [
            "gui_components/device_selector.py",
            "MeTuber/gui_components/device_selector.py",
            "MeTuber/src/gui/components/device_selector.py",
        ],
        "parameter_controls.py": [
            "gui_components/parameter_controls.py",
            "MeTuber/gui_components/parameter_controls.py",
            "MeTuber/src/gui/components/parameter_controls.py",
        ],
        "style_tab_manager.py": [
            "gui_components/style_tab_manager.py",
            "MeTuber/gui_components/style_tab_manager.py",
            "MeTuber/src/gui/components/style_tab_manager.py",
        ],
    }
    
    resolved = {}
    for filename, duplicate_paths in duplicates.items():
        ssot_file = ssot_base / filename
        if not ssot_file.exists():
            print(f"⚠️ SSOT file not found: {ssot_file}")
            continue
        
        resolved[filename] = []
        for dup_path in duplicate_paths:
            dup_file = repo_dir / dup_path.replace("/", os.sep)
            if dup_file.exists():
                # Compare files
                if not compare_files(ssot_file, dup_file):
                    print(f"⚠️ Files differ: {ssot_file.name}")
                    print(f"   SSOT: {ssot_file}")
                    print(f"   Duplicate: {dup_file}")
                    print(f"   💡 Use merge_duplicate_file_functionality.py to analyze differences")
                resolved[filename].append(str(dup_file))
    
    return resolved


def resolve_style_manager(repo_dir: Path) -> List[str]:
    """Resolve style manager duplicates."""
    candidates = [
        repo_dir / "MeTuber" / "src" / "core" / "style_manager.py",
        repo_dir / "src" / "core" / "style_manager.py",
        repo_dir / "src" / "gui" / "modules" / "style_manager.py",
    ]
    
    # Determine SSOT (likely src/core/style_manager.py)
    ssot = repo_dir / "src" / "core" / "style_manager.py"
    duplicates = []
    
    for candidate in candidates:
        if candidate == ssot:
            continue
        if candidate.exists():
            if not compare_files(ssot, candidate):
                print(f"⚠️ Style manager files differ: {candidate}")
            duplicates.append(str(candidate))
    
    return duplicates


def resolve_test_files(repo_dir: Path) -> List[str]:
    """Resolve test file duplicates."""
    ssot = repo_dir / "tests" / "test_consolidated_styles.py"
    duplicates = [
        repo_dir / "test_consolidated_styles.py",
        repo_dir / "MeTuber" / "tests" / "test_consolidated_styles.py",
    ]
    
    resolved = []
    for dup in duplicates:
        if dup.exists() and dup != ssot:
            if not compare_files(ssot, dup):
                print(f"⚠️ Test files differ: {dup}")
            resolved.append(str(dup))
    
    return resolved


def main():
    """Main execution function."""
    token = get_github_token()
    username = get_github_username()
    
    if not token or not username:
        print("❌ GitHub token and username required")
        print("Set GITHUB_TOKEN and GITHUB_USERNAME environment variables")
        return 1
    
    with tempfile.TemporaryDirectory() as temp_base:
        temp_path = Path(temp_base)
        repo_dir = clone_streamertools(temp_path, token, username)
        
        if not repo_dir:
            return 1
        
        print("\n🔍 Analyzing duplicates...")
        
        # Resolve GUI components
        print("\n📦 Resolving GUI components...")
        gui_resolved = resolve_gui_components(repo_dir)
        print(f"✅ Found {len(gui_resolved)} GUI component duplicates")
        
        # Resolve style manager
        print("\n📦 Resolving style manager...")
        style_duplicates = resolve_style_manager(repo_dir)
        print(f"✅ Found {len(style_duplicates)} style manager duplicates")
        
        # Resolve test files
        print("\n📦 Resolving test files...")
        test_duplicates = resolve_test_files(repo_dir)
        print(f"✅ Found {len(test_duplicates)} test file duplicates")
        
        print("\n📊 Summary:")
        print(f"   GUI Components: {sum(len(v) for v in gui_resolved.values())} duplicates")
        print(f"   Style Manager: {len(style_duplicates)} duplicates")
        print(f"   Test Files: {len(test_duplicates)} duplicates")
        
        print("\n⚠️ NOTE: This tool analyzes duplicates.")
        print("   Actual removal should be done manually after review.")
        print("   Files may have different functionality that needs merging.")
        
        return 0


if __name__ == "__main__":
    sys.exit(main())

