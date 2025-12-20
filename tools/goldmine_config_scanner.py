#!/usr/bin/env python3
"""
Goldmine Config Scanner - Phase 2 Execution Tool

Scans goldmine repositories for config files to prepare for Phase 2 consolidation.
Identifies config patterns, dependencies, and potential conflicts.

V2 Compliant: <400 lines
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple


class GoldmineConfigScanner:
    """Scans goldmine repos for config files."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.config_patterns = [
            r'config\.py$',
            r'config_manager\.py$',
            r'ConfigManager',
            r'config_core\.py$',
            r'unified_config\.py$',
        ]
        self.config_files: List[Dict] = []
        
    def scan_repo(self, repo_path: Path) -> List[Dict]:
        """Scan a repository for config files."""
        if not repo_path.exists():
            return []
            
        config_files = []
        
        # Scan for config files
        for root, dirs, files in os.walk(repo_path):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check if matches config patterns
                for pattern in self.config_patterns:
                    if re.search(pattern, str(file_path), re.IGNORECASE):
                        config_files.append({
                            'path': str(file_path.relative_to(repo_path)),
                            'full_path': str(file_path),
                            'pattern_matched': pattern,
                            'size': file_path.stat().st_size if file_path.exists() else 0,
                        })
                        break
        
        return config_files
    
    def analyze_config_file(self, config_path: Path) -> Dict:
        """Analyze a config file for patterns and dependencies."""
        if not config_path.exists():
            return {}
            
        content = config_path.read_text(errors='ignore')
        
        analysis = {
            'has_dataclass': bool(re.search(r'@dataclass|class.*Config', content)),
            'has_manager': bool(re.search(r'class.*Manager|ConfigManager', content)),
            'has_accessors': bool(re.search(r'def get_|def load_|def read_', content)),
            'imports_config_ssot': bool(re.search(r'from.*config_ssot|import.*config_ssot', content)),
            'imports_config_core': bool(re.search(r'from.*config_core|import.*config_core', content)),
            'imports_unified_config': bool(re.search(r'from.*unified_config|import.*unified_config', content)),
            'line_count': len(content.splitlines()),
        }
        
        return analysis


def scan_goldmine_repos():
    """Scan all goldmine repos for config files."""
    repo_root = Path(__file__).parent.parent
    
    # Goldmine repos to scan
    goldmine_repos = [
        ('trading-leads-bot', 'Repo #17'),
        ('Agent_Cellphone', 'Repo #6'),
        ('TROOP', 'Repo #16'),
        ('FocusForge', 'Repo #24'),
        ('Superpowered-TTRPG', 'Repo #30'),
    ]
    
    scanner = GoldmineConfigScanner(repo_root)
    results = {}
    
    print("🔍 Goldmine Config Scanner - Phase 2 Execution")
    print("=" * 60)
    
    for repo_name, repo_id in goldmine_repos:
        # Try common locations
        possible_paths = [
            repo_root.parent / repo_name,
            repo_root / 'repos' / repo_name,
            repo_root / repo_name,
        ]
        
        repo_path = None
        for path in possible_paths:
            if path.exists() and path.is_dir():
                repo_path = path
                break
        
        if not repo_path:
            print(f"\n⚠️  {repo_name} ({repo_id}): NOT FOUND")
            results[repo_name] = {
                'status': 'not_found',
                'config_files': [],
            }
            continue
        
        print(f"\n📁 Scanning {repo_name} ({repo_id})...")
        config_files = scanner.scan_repo(repo_path)
        
        if config_files:
            print(f"   ✅ Found {len(config_files)} config file(s):")
            for cfg in config_files:
                print(f"      - {cfg['path']}")
        else:
            print(f"   ℹ️  No config files found")
        
        # Analyze config files
        analyzed = []
        for cfg in config_files:
            cfg_path = Path(cfg['full_path'])
            analysis = scanner.analyze_config_file(cfg_path)
            analyzed.append({
                **cfg,
                'analysis': analysis,
            })
        
        results[repo_name] = {
            'status': 'scanned',
            'repo_path': str(repo_path),
            'config_files': analyzed,
        }
    
    # Save results
    output_file = repo_root / 'docs' / 'organization' / 'PHASE2_GOLDMINE_CONFIG_SCAN_RESULTS.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Scan complete! Results saved to: {output_file}")
    print("=" * 60)
    
    return results


if __name__ == '__main__':
    scan_goldmine_repos()

