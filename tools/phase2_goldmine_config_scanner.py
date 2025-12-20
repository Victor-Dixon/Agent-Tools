#!/usr/bin/env python3
"""
Phase 2 Goldmine Config Scanner
================================

Scans goldmine repositories for config files to support Phase 2 consolidation.
Identifies config patterns, dependencies, and conflicts.

Created: 2025-01-28
Agent: Agent-1 (Integration & Core Systems Specialist)
"""

import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.unified_config_utils import (
    UnifiedConfigurationConsolidator,
    FileScanner,
    EnvironmentVariableScanner,
    HardcodedValueScanner,
    ConfigConstantScanner,
    SettingsPatternScanner
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Target goldmine repos for Phase 2
GOLDMINE_REPOS = {
    "trading-leads-bot": {
        "repo_num": 17,
        "agent": "Agent-2",
        "target_for": "contract-leads merge"
    },
    "Agent_Cellphone": {
        "repo_num": 6,
        "agent": "Agent-1",
        "target_for": "intelligent-multi-agent merge"
    }
}

GITHUB_USER = "Dadudekc"
TEMP_BASE = Path(tempfile.gettempdir()) / "phase2_config_scan"


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment."""
    return os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")


def clone_repo(repo_name: str, temp_dir: Path) -> Optional[Path]:
    """Clone repository to temporary directory."""
    token = get_github_token()
    repo_url = f"https://github.com/{GITHUB_USER}/{repo_name}.git"
    
    if token:
        repo_url = f"https://{token}@github.com/{GITHUB_USER}/{repo_name}.git"
    
    repo_dir = temp_dir / repo_name
    
    # Remove if exists
    if repo_dir.exists():
        import shutil
from src.core.config.timeout_constants import TimeoutConstants
        shutil.rmtree(repo_dir)
    
    try:
        logger.info(f"📥 Cloning {repo_name}...")
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(repo_dir)],
            check=True,
            capture_output=True,
            timeout=TimeoutConstants.HTTP_LONG
        )
        logger.info(f"✅ Cloned {repo_name}")
        return repo_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to clone {repo_name}: {e.stderr.decode() if e.stderr else str(e)}")
        return None
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Timeout cloning {repo_name}")
        return None


def find_config_files(repo_path: Path) -> List[Path]:
    """Find all potential config files in repository."""
    config_patterns = [
        "**/config.py",
        "**/config_manager.py",
        "**/config_*.py",
        "**/settings.py",
        "**/settings_*.py",
        "**/.env",
        "**/.env.*",
        "**/config.json",
        "**/config.yaml",
        "**/config.yml",
        "**/settings.json",
        "**/settings.yaml",
        "**/settings.yml",
    ]
    
    config_files = []
    for pattern in config_patterns:
        config_files.extend(repo_path.rglob(pattern))
    
    # Filter out common exclusions
    excluded = {".git", "__pycache__", "venv", "env", "node_modules", ".venv"}
    config_files = [
        f for f in config_files
        if not any(excluded_dir in f.parts for excluded_dir in excluded)
    ]
    
    return sorted(set(config_files))


def analyze_config_structure(config_file: Path) -> Dict[str, Any]:
    """Analyze structure of a config file."""
    analysis = {
        "file": str(config_file.relative_to(config_file.parts[0])),
        "type": "unknown",
        "patterns": [],
        "imports": [],
        "classes": [],
        "functions": [],
        "variables": []
    }
    
    try:
        content = config_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Detect file type
        if config_file.suffix == '.py':
            analysis["type"] = "python"
            
            # Find imports
            for line in lines:
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    analysis["imports"].append(line.strip())
            
            # Find class definitions
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('class '):
                    class_name = line.strip().split('(')[0].replace('class ', '').strip()
                    analysis["classes"].append({"name": class_name, "line": i})
            
            # Find function definitions
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('def ') and not line.strip().startswith('def _'):
                    func_name = line.strip().split('(')[0].replace('def ', '').strip()
                    analysis["functions"].append({"name": func_name, "line": i})
            
            # Find variable assignments (config-like)
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and '=' in stripped:
                    if any(keyword in stripped.lower() for keyword in ['config', 'setting', 'default', 'api_key', 'token', 'url']):
                        parts = stripped.split('=')
                        if len(parts) == 2:
                            var_name = parts[0].strip()
                            analysis["variables"].append({"name": var_name, "line": i})
        
        elif config_file.suffix in ['.json', '.yaml', '.yml']:
            analysis["type"] = config_file.suffix[1:]
            # Could parse JSON/YAML here if needed
        
        elif config_file.name.startswith('.env'):
            analysis["type"] = "environment"
    
    except Exception as e:
        logger.warning(f"Error analyzing {config_file}: {e}")
        analysis["error"] = str(e)
    
    return analysis


def scan_repo_configs(repo_path: Path) -> Dict[str, Any]:
    """Scan repository for config files and patterns."""
    logger.info(f"🔍 Scanning {repo_path.name} for config files...")
    
    # Find config files
    config_files = find_config_files(repo_path)
    logger.info(f"   Found {len(config_files)} config files")
    
    # Analyze each config file
    config_analysis = []
    for config_file in config_files:
        analysis = analyze_config_structure(config_file)
        config_analysis.append(analysis)
    
    # Use UnifiedConfigurationConsolidator to scan patterns
    consolidator = UnifiedConfigurationConsolidator()
    patterns = consolidator.scan_configuration_patterns(repo_path)
    
    # Find config-related imports
    config_imports = []
    for py_file in repo_path.rglob("*.py"):
        if any(excluded in py_file.parts for excluded in [".git", "__pycache__", "venv", "env"]):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if 'import' in line and any(keyword in line.lower() for keyword in ['config', 'setting', 'env']):
                    config_imports.append({
                        "file": str(py_file.relative_to(repo_path)),
                        "import": line.strip()
                    })
        except Exception:
            pass
    
    return {
        "config_files": config_analysis,
        "config_patterns": {
            "total": sum(len(p) for p in patterns.values()),
            "by_type": {k: len(v) for k, v in patterns.items()}
        },
        "config_imports": config_imports[:50],  # Limit to first 50
        "summary": {
            "total_config_files": len(config_files),
            "python_configs": len([f for f in config_analysis if f["type"] == "python"]),
            "json_configs": len([f for f in config_analysis if f["type"] == "json"]),
            "yaml_configs": len([f for f in config_analysis if f["type"] in ["yaml", "yml"]]),
            "env_configs": len([f for f in config_analysis if f["type"] == "environment"]),
        }
    }


def generate_report(results: Dict[str, Dict[str, Any]]) -> str:
    """Generate markdown report from scan results."""
    report = """# 🔍 Phase 2 Goldmine Config Scanning Report

**Date**: 2025-01-28  
**Agent**: Agent-1 (Integration & Core Systems Specialist)  
**Purpose**: Config analysis for Phase 2 goldmine consolidation

---

## 📊 Executive Summary

"""
    
    for repo_name, data in results.items():
        repo_info = GOLDMINE_REPOS[repo_name]
        summary = data["summary"]
        
        report += f"""### {repo_name} (Repo #{repo_info['repo_num']})

**Agent**: {repo_info['agent']}  
**Target For**: {repo_info['target_for']}

**Config Files Found**: {summary['total_config_files']}
- Python configs: {summary['python_configs']}
- JSON configs: {summary['json_configs']}
- YAML configs: {summary['yaml_configs']}
- Environment files: {summary['env_configs']}

**Config Patterns**: {data['config_patterns']['total']} total
"""
        for pattern_type, count in data['config_patterns']['by_type'].items():
            report += f"- {pattern_type}: {count}\n"
        
        report += "\n---\n\n"
    
    # Detailed file analysis
    report += "## 📁 Detailed Config File Analysis\n\n"
    
    for repo_name, data in results.items():
        report += f"### {repo_name}\n\n"
        
        if not data["config_files"]:
            report += "**No config files found.**\n\n"
            continue
        
        for config in data["config_files"][:20]:  # Limit to first 20
            report += f"#### `{config['file']}`\n\n"
            report += f"- **Type**: {config['type']}\n"
            
            if config.get("classes"):
                report += f"- **Classes**: {', '.join([c['name'] for c in config['classes']])}\n"
            
            if config.get("functions"):
                report += f"- **Functions**: {', '.join([f['name'] for f in config['functions'][:5]])}\n"
            
            if config.get("variables"):
                report += f"- **Config Variables**: {len(config['variables'])} found\n"
            
            if config.get("imports"):
                report += f"- **Imports**: {len(config['imports'])} config-related imports\n"
            
            report += "\n"
        
        if len(data["config_files"]) > 20:
            report += f"*... and {len(data['config_files']) - 20} more config files*\n\n"
    
    # Config imports analysis
    report += "## 🔗 Config Import Dependencies\n\n"
    
    for repo_name, data in results.items():
        if data["config_imports"]:
            report += f"### {repo_name}\n\n"
            report += f"**Total config-related imports**: {len(data['config_imports'])}\n\n"
            
            # Show sample imports
            for imp in data["config_imports"][:10]:
                report += f"- `{imp['file']}`: `{imp['import']}`\n"
            
            if len(data["config_imports"]) > 10:
                report += f"*... and {len(data['config_imports']) - 10} more imports*\n"
            
            report += "\n"
    
    # Migration recommendations
    report += """## 🎯 Migration Recommendations

### Next Steps:
1. **Map config files to config_ssot equivalents**
2. **Identify naming conflicts** (same config names, different values)
3. **Document structure conflicts** (different config structures)
4. **Create migration paths** for each conflict
5. **Plan shim creation** for backward compatibility

### Expected Config Locations:
- `config.py` → Migrate to `src/core/config_ssot.py`
- `config_manager.py` → Use `src/core/config_ssot.py` ConfigManager
- `settings.py` → Map to config_ssot settings
- Environment variables → Use config_ssot env loader

---

**Status**: ✅ Config scanning complete  
**Next Action**: Agent-6 to review and coordinate first goldmine merge

🐝 WE. ARE. SWARM. ⚡🔥🚀
"""
    
    return report


def main():
    """Main execution function."""
    logger.info("🚀 Phase 2 Goldmine Config Scanner")
    logger.info("=" * 50)
    
    # Create temp directory
    TEMP_BASE.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for repo_name, repo_info in GOLDMINE_REPOS.items():
        logger.info(f"\n📦 Processing {repo_name} (Repo #{repo_info['repo_num']})...")
        
        # Clone repo
        repo_path = clone_repo(repo_name, TEMP_BASE)
        if not repo_path:
            logger.error(f"❌ Skipping {repo_name} - clone failed")
            continue
        
        # Scan configs
        scan_results = scan_repo_configs(repo_path)
        results[repo_name] = scan_results
        
        logger.info(f"✅ Completed scan for {repo_name}")
        logger.info(f"   - Config files: {scan_results['summary']['total_config_files']}")
        logger.info(f"   - Config patterns: {scan_results['config_patterns']['total']}")
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    report_path = project_root / "docs" / "organization" / "PHASE2_GOLDMINE_CONFIG_ANALYSIS.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    
    logger.info(f"\n✅ Report saved to: {report_path}")
    
    # Also save JSON results
    json_path = project_root / "docs" / "organization" / "PHASE2_GOLDMINE_CONFIG_ANALYSIS.json"
    json_path.write_text(json.dumps(results, indent=2, default=str), encoding='utf-8')
    logger.info(f"✅ JSON results saved to: {json_path}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 SCAN SUMMARY")
    print("=" * 50)
    for repo_name, data in results.items():
        print(f"\n{repo_name}:")
        print(f"  Config files: {data['summary']['total_config_files']}")
        print(f"  Config patterns: {data['config_patterns']['total']}")
        print(f"  Config imports: {len(data['config_imports'])}")
    
    print("\n✅ Phase 2 config scanning complete!")
    print(f"📄 Full report: {report_path}")


if __name__ == "__main__":
    main()

