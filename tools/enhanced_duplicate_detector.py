#!/usr/bin/env python3
"""
Enhanced Duplicate Detector - Agent-2
======================================

Enhanced duplicate detection with content-based analysis.
"""

import os
import sys
import hashlib
import subprocess
import tempfile
import shutil
import time
import stat
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from src.core.config.timeout_constants import TimeoutConstants

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
from src.core.utils.github_utils import get_github_token


def get_github_username() -> Optional[str]:
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


def ensure_dir_removed(dir_path: Path, name: str):
    """Ensure directory is completely removed."""
    if dir_path.exists():
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


def calculate_file_hash(file_path: Path) -> Optional[str]:
    """Calculate SHA256 hash of file content."""
    try:
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception:
        return None


def identify_exact_duplicates(repo_dir: Path, exclude_patterns: List[str]) -> Dict[str, List[Path]]:
    """Identify exact duplicates using content hashing."""
    hash_to_files = defaultdict(list)
    
    for file_path in repo_dir.rglob("*"):
        if not file_path.is_file():
            continue
        
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            continue
        
        if ".git" in file_path.parts or "__pycache__" in file_path.parts:
            continue
        
        file_hash = calculate_file_hash(file_path)
        if file_hash:
            hash_to_files[file_hash].append(file_path)
    
    # Return only duplicates (2+ files with same hash)
    return {hash_val: paths for hash_val, paths in hash_to_files.items() if len(paths) > 1}


def identify_name_duplicates(repo_dir: Path, exclude_patterns: List[str]) -> Dict[str, List[Path]]:
    """Identify name-based duplicates."""
    name_to_files = defaultdict(list)
    
    for file_path in repo_dir.rglob("*.py"):
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            continue
        
        if ".git" in file_path.parts or "__pycache__" in file_path.parts:
            continue
        
        name_to_files[file_path.name].append(file_path)
    
    return {name: paths for name, paths in name_to_files.items() if len(paths) > 1}


def determine_ssot_version(file_paths: List[Path], repo_dir: Path, merged_repo_patterns: List[str] = None) -> Optional[Path]:
    """Determine SSOT version using enhanced priority rules based on integration patterns."""
    if merged_repo_patterns is None:
        merged_repo_patterns = ["digitaldreamscape", "thea", "dreambank", "content", "freework", "metuber", "streamertools"]
    
    # Priority 1: Files in root or main directories (not in subdirectories)
    for path in file_paths:
        rel_path = path.relative_to(repo_dir)
        if rel_path.parent == Path(".") or len(rel_path.parts) <= 2:
            return path
    
    # Priority 2: Files not in merged repo directories
    for path in file_paths:
        path_str = str(path.relative_to(repo_dir)).lower()
        if not any(pattern in path_str for pattern in merged_repo_patterns):
            return path
    
    # Priority 3: Files in src/ or main source directories
    for path in file_paths:
        path_str = str(path.relative_to(repo_dir)).lower()
        if path_str.startswith("src/") or path_str.startswith("lib/") or path_str.startswith("app/"):
            return path
    
    # Priority 4: Files not in test directories
    for path in file_paths:
        path_str = str(path.relative_to(repo_dir)).lower()
        if "test" not in path_str and "tests" not in path_str:
            return path
    
    # Default: First file found
    return file_paths[0] if file_paths else None


def generate_resolution_script(
    repo_dir: Path,
    exact_duplicates: Dict[str, List[Path]],
    name_duplicates: Dict[str, List[Path]],
    merged_repo_patterns: List[str] = None
) -> str:
    """Generate resolution script for duplicates."""
    if merged_repo_patterns is None:
        merged_repo_patterns = ["digitaldreamscape", "thea", "dreambank", "content", "freework", "metuber", "streamertools"]
    
    script_lines = ["#!/usr/bin/env python3", "# Auto-generated duplicate resolution script", ""]
    script_lines.append("import os")
    script_lines.append("from pathlib import Path")
    script_lines.append("")
    script_lines.append("# Exact Duplicates Resolution")
    
    for hash_val, paths in exact_duplicates.items():
        ssot = determine_ssot_version(paths, repo_dir, merged_repo_patterns)
        if ssot:
            script_lines.append(f"# {ssot.name} - SSOT version")
            for path in paths:
                if path != ssot:
                    rel_path = path.relative_to(repo_dir)
                    script_lines.append(f"# os.remove('{rel_path}')  # Uncomment to remove")
    
    return "\n".join(script_lines)


def generate_enhanced_report(
    repo_dir: Path,
    exact_duplicates: Dict[str, List[Path]],
    name_duplicates: Dict[str, List[Path]],
    merged_repo_patterns: List[str] = None
) -> str:
    """Generate enhanced duplicate detection report."""
    if merged_repo_patterns is None:
        merged_repo_patterns = ["digitaldreamscape", "thea", "dreambank", "content", "freework", "metuber", "streamertools"]
    
    report = []
    report.append("="*60)
    report.append("📋 ENHANCED DUPLICATE DETECTION REPORT")
    report.append("="*60)
    
    report.append(f"\n🔍 Exact Duplicates (Content-Based):")
    report.append(f"   Total Groups: {len(exact_duplicates)}")
    
    total_exact = sum(len(paths) for paths in exact_duplicates.values())
    report.append(f"   Total Files: {total_exact}")
    
    if exact_duplicates:
        report.append(f"\n   Top 10 Exact Duplicate Groups:")
        sorted_exact = sorted(exact_duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for hash_val, paths in sorted_exact:
            report.append(f"      {paths[0].name}: {len(paths)} locations")
            ssot = determine_ssot_version(paths, repo_dir, merged_repo_patterns)
            if ssot:
                report.append(f"         SSOT: {ssot.relative_to(repo_dir)}")
                for path in paths[:3]:
                    if path != ssot:
                        report.append(f"         Remove: {path.relative_to(repo_dir)}")
                if len(paths) > 3:
                    report.append(f"         ... and {len(paths) - 3} more")
    
    report.append(f"\n📋 Name-Based Duplicates:")
    report.append(f"   Total Groups: {len(name_duplicates)}")
    
    total_name = sum(len(paths) for paths in name_duplicates.values())
    report.append(f"   Total Files: {total_name}")
    
    if name_duplicates:
        report.append(f"\n   Top 10 Name-Based Duplicate Groups:")
        sorted_name = sorted(name_duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for name, paths in sorted_name:
            report.append(f"      {name}: {len(paths)} locations")
            ssot = determine_ssot_version(paths, repo_dir, merged_repo_patterns)
            if ssot:
                report.append(f"         SSOT: {ssot.relative_to(repo_dir)}")
    
    report.append(f"\n🔧 Recommendations:")
    report.append(f"   1. Remove exact duplicates (keep SSOT versions)")
    report.append(f"   2. Review name-based duplicates (may have different content)")
    report.append(f"   3. Update imports if needed")
    report.append(f"   4. Test functionality after cleanup")
    
    return "\n".join(report)


def main():
    """Main entry point."""
    token = get_github_token()
    username = get_github_username()
    
    if not token or not username:
        print("❌ GITHUB_TOKEN or GITHUB_USERNAME not found.")
        return 1
    
    # Get repo name from command line or use DreamVault
    repo_name = sys.argv[1] if len(sys.argv) > 1 else "DreamVault"
    
    timestamp = int(time.time() * 1000000)
    temp_base = Path(tempfile.mkdtemp(prefix=f"enhanced_dup_{timestamp}_"))
    
    try:
        owner = "Dadudekc"
        repo_url = f"https://{username}:{token}@github.com/{owner}/{repo_name}.git"
        repo_dir = temp_base / repo_name
        
        print(f"📥 Cloning {repo_name}...")
        subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            check=True, timeout=TimeoutConstants.HTTP_EXTENDED, capture_output=True, text=True
        )
        print(f"✅ Cloned {repo_name} successfully")
        
        exclude_patterns = ["lib/python", "site-packages", "venv", "env", "__pycache__"]
        
        print("\n🔍 Identifying exact duplicates (content-based)...")
        exact_duplicates = identify_exact_duplicates(repo_dir, exclude_patterns)
        
        print("🔍 Identifying name-based duplicates...")
        name_duplicates = identify_name_duplicates(repo_dir, exclude_patterns)
        
        print("📋 Generating enhanced report...")
        merged_patterns = ["digitaldreamscape", "thea", "dreambank", "content", "freework", "metuber", "streamertools"]
        report = generate_enhanced_report(repo_dir, exact_duplicates, name_duplicates, merged_patterns)
        print(report)
        
        # Save report
        report_file = project_root / "agent_workspaces" / "Agent-2" / f"{repo_name}_ENHANCED_DUPLICATES.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ Report saved to: {report_file}")
        
        # Generate resolution script
        resolution_script = generate_resolution_script(repo_dir, exact_duplicates, name_duplicates, merged_patterns)
        script_file = project_root / "agent_workspaces" / "Agent-2" / f"{repo_name}_RESOLUTION_SCRIPT.py"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(resolution_script)
        print(f"✅ Resolution script saved to: {script_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ensure_dir_removed(temp_base, "temp_repo_clone")


if __name__ == "__main__":
    sys.exit(main())

