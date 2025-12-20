#!/usr/bin/env python3
"""
Extract Portfolio Management Logic - Agent-2
============================================

Extracts portfolio management logic from DreamBank merged into DreamVault.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
import stat
from pathlib import Path
from typing import Optional, Dict, List

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
        except Exception:
            pass


def clone_dreamvault(temp_base: Path, token: str, username: str) -> Optional[Path]:
    owner = "Dadudekc"
    repo = "DreamVault"
    repo_dir = temp_base / repo
    
    try:
        repo_url = f"https://{username}:{token}@github.com/{owner}/{repo}.git"
        subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            check=True, timeout=TimeoutConstants.HTTP_EXTENDED, capture_output=True, text=True
        )
        return repo_dir
    except Exception:
        return None


def extract_portfolio_files(repo_dir: Path, output_dir: Path) -> List[Path]:
    """Extract portfolio management files."""
    portfolio_files = []
    
    # Find portfolio-related files
    patterns = ["*portfolio*.py", "*stock*.py", "*financial*.py"]
    
    for pattern in patterns:
        for file_path in repo_dir.rglob(pattern):
            if ".git" in file_path.parts or "site-packages" in str(file_path):
                continue
            
            rel_path = file_path.relative_to(repo_dir)
            output_path = output_dir / rel_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                output_path.write_text(content, encoding="utf-8")
                portfolio_files.append(output_path)
            except Exception:
                pass
    
    return portfolio_files


def analyze_portfolio_code(portfolio_files: List[Path]) -> Dict:
    """Analyze extracted portfolio code."""
    analysis = {
        "classes": [],
        "functions": [],
        "imports": [],
        "dependencies": []
    }
    
    for file_path in portfolio_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            
            for line in lines:
                # Extract classes
                if line.strip().startswith("class "):
                    class_name = line.strip().split("class ")[1].split("(")[0].strip()
                    analysis["classes"].append(f"{file_path.name}:{class_name}")
                
                # Extract functions
                elif line.strip().startswith("def ") and not line.strip().startswith("def _"):
                    func_name = line.strip().split("def ")[1].split("(")[0].strip()
                    analysis["functions"].append(f"{file_path.name}:{func_name}")
                
                # Extract imports
                elif line.strip().startswith("import ") or line.strip().startswith("from "):
                    import_line = line.strip()
                    if import_line not in analysis["imports"]:
                        analysis["imports"].append(import_line)
        except Exception:
            pass
    
    return analysis


def main():
    token = get_github_token()
    username = get_github_username()
    
    if not token or not username:
        print("❌ GITHUB_TOKEN or GITHUB_USERNAME not found.")
        return 1
    
    timestamp = int(time.time() * 1000000)
    temp_base = Path(tempfile.mkdtemp(prefix=f"extract_portfolio_{timestamp}_"))
    output_dir = project_root / "agent_workspaces" / "Agent-2" / "extracted_logic" / "portfolio"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        repo_dir = clone_dreamvault(temp_base, token, username)
        if not repo_dir:
            return 1
        
        print("📥 Extracting portfolio management files...")
        portfolio_files = extract_portfolio_files(repo_dir, output_dir)
        print(f"✅ Extracted {len(portfolio_files)} portfolio files")
        
        print("🔍 Analyzing portfolio code...")
        analysis = analyze_portfolio_code(portfolio_files)
        
        print(f"\n📊 Portfolio Code Analysis:")
        print(f"   Classes: {len(analysis['classes'])}")
        print(f"   Functions: {len(analysis['functions'])}")
        print(f"   Imports: {len(analysis['imports'])}")
        
        # Save analysis
        analysis_file = output_dir / "analysis.md"
        with open(analysis_file, "w", encoding="utf-8") as f:
            f.write("# Portfolio Management Logic Analysis\n\n")
            f.write(f"**Files Extracted**: {len(portfolio_files)}\n\n")
            f.write(f"**Classes**: {len(analysis['classes'])}\n")
            for cls in analysis['classes']:
                f.write(f"- {cls}\n")
            f.write(f"\n**Functions**: {len(analysis['functions'])}\n")
            for func in analysis['functions'][:20]:
                f.write(f"- {func}\n")
            if len(analysis['functions']) > 20:
                f.write(f"- ... and {len(analysis['functions']) - 20} more\n")
        
        print(f"✅ Analysis saved to: {analysis_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
from src.core.config.timeout_constants import TimeoutConstants
        traceback.print_exc()
        return 1
    finally:
        ensure_dir_removed(temp_base, "temp_repo_clone")


if __name__ == "__main__":
    sys.exit(main())

