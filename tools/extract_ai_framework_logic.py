#!/usr/bin/env python3
"""
Extract AI Framework Logic - Agent-2
====================================

Extracts AI framework logic from DigitalDreamscape and Thea merged into DreamVault.
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


def extract_ai_files(repo_dir: Path, output_dir: Path) -> Dict[str, List[Path]]:
    """Extract AI framework files."""
    ai_files = {
        "models": [],
        "conversation": [],
        "nlp": [],
        "other": []
    }
    
    # Find AI-related files
    patterns = {
        "models": ["*model*.py", "*ai*.py"],
        "conversation": ["*conversation*.py", "*chat*.py"],
        "nlp": ["*nlp*.py", "*language*.py"]
    }
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            for file_path in repo_dir.rglob(pattern):
                if ".git" in file_path.parts or "site-packages" in str(file_path):
                    continue
                
                rel_path = file_path.relative_to(repo_dir)
                output_path = output_dir / category / rel_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    output_path.write_text(content, encoding="utf-8")
                    ai_files[category].append(output_path)
                except Exception:
                    pass
    
    return ai_files


def analyze_ai_code(ai_files: Dict[str, List[Path]]) -> Dict:
    """Analyze extracted AI code."""
    analysis = {
        "classes": [],
        "functions": [],
        "imports": [],
        "models": len(ai_files["models"]),
        "conversation": len(ai_files["conversation"]),
        "nlp": len(ai_files["nlp"])
    }
    
    all_files = []
    for file_list in ai_files.values():
        all_files.extend(file_list)
    
    for file_path in all_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            
            for line in lines:
                if line.strip().startswith("class "):
                    class_name = line.strip().split("class ")[1].split("(")[0].strip()
                    analysis["classes"].append(f"{file_path.name}:{class_name}")
                elif line.strip().startswith("def ") and not line.strip().startswith("def _"):
                    func_name = line.strip().split("def ")[1].split("(")[0].strip()
                    analysis["functions"].append(f"{file_path.name}:{func_name}")
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
    temp_base = Path(tempfile.mkdtemp(prefix=f"extract_ai_{timestamp}_"))
    output_dir = project_root / "agent_workspaces" / "Agent-2" / "extracted_logic" / "ai_framework"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        repo_dir = clone_dreamvault(temp_base, token, username)
        if not repo_dir:
            return 1
        
        print("📥 Extracting AI framework files...")
        ai_files = extract_ai_files(repo_dir, output_dir)
        total_files = sum(len(files) for files in ai_files.values())
        print(f"✅ Extracted {total_files} AI framework files")
        print(f"   Models: {len(ai_files['models'])}")
        print(f"   Conversation: {len(ai_files['conversation'])}")
        print(f"   NLP: {len(ai_files['nlp'])}")
        
        print("🔍 Analyzing AI framework code...")
        analysis = analyze_ai_code(ai_files)
        
        print(f"\n📊 AI Framework Code Analysis:")
        print(f"   Classes: {len(analysis['classes'])}")
        print(f"   Functions: {len(analysis['functions'])}")
        print(f"   Imports: {len(analysis['imports'])}")
        
        # Save analysis
        analysis_file = output_dir / "analysis.md"
        with open(analysis_file, "w", encoding="utf-8") as f:
            f.write("# AI Framework Logic Analysis\n\n")
            f.write(f"**Files Extracted**: {total_files}\n")
            f.write(f"- Models: {analysis['models']}\n")
            f.write(f"- Conversation: {analysis['conversation']}\n")
            f.write(f"- NLP: {analysis['nlp']}\n\n")
            f.write(f"**Classes**: {len(analysis['classes'])}\n")
            for cls in analysis['classes'][:30]:
                f.write(f"- {cls}\n")
            if len(analysis['classes']) > 30:
                f.write(f"- ... and {len(analysis['classes']) - 30} more\n")
            f.write(f"\n**Functions**: {len(analysis['functions'])}\n")
            for func in analysis['functions'][:30]:
                f.write(f"- {func}\n")
            if len(analysis['functions']) > 30:
                f.write(f"- ... and {len(analysis['functions']) - 30} more\n")
        
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

