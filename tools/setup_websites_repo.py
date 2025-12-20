#!/usr/bin/env python3
"""
Websites Repository Setup Tool
===============================

Initializes and configures the websites repository for automatic syncing.

Usage:
    python tools/setup_websites_repo.py --repo-url https://github.com/Dadudekc/websites.git

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class WebsitesRepoSetup:
    """Sets up websites repository for syncing."""
    
    def __init__(self, websites_path: Path, repo_url: str):
        """
        Initialize setup tool.
        
        Args:
            websites_path: Path to websites repository
            repo_url: GitHub repository URL
        """
        self.websites_path = Path(websites_path)
        self.repo_url = repo_url
    
    def check_git_repo(self) -> bool:
        """Check if path is a git repository."""
        git_dir = self.websites_path / ".git"
        return git_dir.exists() and git_dir.is_dir()
    
    def initialize_repo(self) -> bool:
        """Initialize git repository if needed."""
        if self.check_git_repo():
            print(f"✅ Git repository already exists: {self.websites_path}")
            return True
        
        print(f"📦 Initializing git repository: {self.websites_path}")
        try:
            subprocess.run(
                ["git", "init"],
                cwd=self.websites_path,
                check=True,
                capture_output=True
            )
            print("✅ Git repository initialized")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to initialize git: {e}")
            return False
    
    def setup_remote(self) -> bool:
        """Set up remote repository."""
        try:
            # Check if remote exists
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.websites_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                current_url = result.stdout.strip()
                if current_url == self.repo_url:
                    print(f"✅ Remote already configured: {self.repo_url}")
                    return True
                else:
                    print(f"⚠️  Remote URL mismatch. Current: {current_url}")
                    print(f"   Updating to: {self.repo_url}")
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", self.repo_url],
                        cwd=self.websites_path,
                        check=True
                    )
                    print("✅ Remote URL updated")
                    return True
            else:
                # Add remote
                print(f"📡 Adding remote: {self.repo_url}")
                subprocess.run(
                    ["git", "remote", "add", "origin", self.repo_url],
                    cwd=self.websites_path,
                    check=True
                )
                print("✅ Remote added")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup remote: {e}")
            return False
    
    def create_gitignore(self) -> bool:
        """Create .gitignore file if it doesn't exist."""
        gitignore_path = self.websites_path / ".gitignore"
        
        if gitignore_path.exists():
            print("✅ .gitignore already exists")
            return True
        
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Environment
.env
.env.local

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# WordPress
wp-config.php
.htaccess.local

# Temporary
*.tmp
*.bak
*.swp
"""
        
        try:
            gitignore_path.write_text(gitignore_content)
            print("✅ Created .gitignore")
            return True
        except Exception as e:
            print(f"❌ Failed to create .gitignore: {e}")
            return False
    
    def setup(self) -> bool:
        """Run complete setup."""
        print(f"\n{'='*60}")
        print(f"🔧 WEBSITES REPOSITORY SETUP")
        print(f"{'='*60}")
        print(f"Path: {self.websites_path}")
        print(f"Repository: {self.repo_url}")
        print(f"{'='*60}\n")
        
        if not self.websites_path.exists():
            print(f"❌ Path does not exist: {self.websites_path}")
            return False
        
        steps = [
            ("Initialize Git Repository", self.initialize_repo),
            ("Setup Remote", self.setup_remote),
            ("Create .gitignore", self.create_gitignore),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Setup failed at: {step_name}")
                return False
        
        print(f"\n{'='*60}")
        print("✅ SETUP COMPLETE!")
        print(f"{'='*60}\n")
        print("Next steps:")
        print("1. Create GitHub repository if it doesn't exist")
        print("2. Add repository URL to GitHub Secrets as WEBSITES_REPO")
        print("3. Add GitHub token to Secrets as WEBSITES_REPO_TOKEN")
        print("4. Test sync: python tools/sync_websites_repo.py --all --dry-run")
        print()
        
        return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Setup websites repository for automatic syncing"
    )
    parser.add_argument(
        '--repo-url',
        default='git@github.com:Victor-Dixon/Websites.git',
        help='GitHub repository URL (default: git@github.com:Victor-Dixon/Websites.git)'
    )
    parser.add_argument(
        '--websites-path',
        type=Path,
        default=Path("D:/websites"),
        help='Path to websites repository (default: D:/websites)'
    )
    
    args = parser.parse_args()
    
    setup = WebsitesRepoSetup(args.websites_path, args.repo_url)
    success = setup.setup()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

