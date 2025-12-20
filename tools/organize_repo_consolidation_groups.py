#!/usr/bin/env python3
"""
Repository Consolidation Group Organizer
=========================================

Organizes similar repos into consolidation groups by creating organized folders
and moving analysis files into appropriate groups. This helps prepare repos
for future merging without deleting anything yet.

Builds on Agent-3 and Agent-8's work.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-01-27
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any


# Consolidation groups based on Agent-8's strategy + new findings
CONSOLIDATION_GROUPS = {
    "dream_projects": {
        "target": "DreamVault",
        "target_repo_num": 15,
        "merge_from": [
            {"name": "DreamBank", "repo_nums": [3]},
            {"name": "DigitalDreamscape", "repo_nums": [59]},
        ],
        "note": "AutoDream_Os is Agent_Cellphone_V2 - DO NOT MERGE",
        "reduction": 2
    },
    "trading_bots": {
        "target": "trading-leads-bot",
        "target_repo_num": 17,
        "merge_from": [
            {"name": "trade-analyzer", "repo_nums": [4]},
            {"name": "UltimateOptionsTradingRobot", "repo_nums": [5]},
            {"name": "TheTradingRobotPlug", "repo_nums": [38]},
            {"name": "contract-leads", "repo_nums": [20]},
            {"name": "TBOWTactics", "repo_nums": [26, 33]},  # Duplicate analyses
        ],
        "reduction": 5
    },
    "gpt_automation": {
        "target": "gpt-automation",
        "target_repo_num": 4,
        "merge_from": [
            {"name": "gpt_automation", "repo_nums": [57]},
        ],
        "reduction": 1
    },
    "dadudekc_projects": {
        "target": "DaDudeKC-Website",
        "target_repo_num": 28,
        "merge_from": [
            {"name": "DaDudekC", "repo_nums": [29]},
            {"name": "dadudekcwebsite", "repo_nums": [35]},
            {"name": "dadudekc", "repo_nums": [36]},
        ],
        "reduction": 3
    },
    "streaming_tools": {
        "target": "Streamertools",
        "target_repo_num": 25,
        "merge_from": [
            {"name": "MeTuber", "repo_nums": [27]},
            {"name": "Streamertools", "repo_nums": [31]},  # Duplicate analysis
        ],
        "reduction": 2
    },
    "ml_models": {
        "target": "MachineLearningModelMaker",
        "target_repo_num": 2,
        "merge_from": [
            {"name": "LSTMmodel_trainer", "repo_nums": [18, 55]},  # Keep 18, archive 55
        ],
        "reduction": 1
    },
    "resume_templates": {
        "target": "my-resume",
        "target_repo_num": 12,
        "merge_from": [
            {"name": "my_personal_templates", "repo_nums": [54]},
            {"name": "my-resume", "repo_nums": [53]},  # Duplicate analysis
        ],
        "reduction": 2
    },
    "duplicate_analyses": {
        "target": None,
        "note": "Archive duplicate analyses of same repo",
        "duplicates": [
            {"repo_name": "network-scanner", "keep": [1], "archive": ["2025-10-15_agent1_CRITICAL_FINDING_repo01.md", "2025-10-15_agent1_repo01_network_scanner.md"]},
            {"repo_name": "TROOP", "keep": [16], "archive": [60]},
            {"repo_name": "FocusForge", "keep": [24], "archive": [32]},
            {"repo_name": "Superpowered-TTRPG", "keep": [30], "archive": [37]},
        ]
    }
}


def find_analysis_file(repo_num: int, devlogs_path: Path) -> Path | None:
    """Find analysis file for a repo number."""
    patterns = [
        f"*repo*{repo_num}*",
        f"*Repo*_{repo_num}_*",
        f"*github*analysis*{repo_num}*",
        f"*github_repo_analysis*{repo_num}*",
    ]
    
    for pattern in patterns:
        matches = list(devlogs_path.glob(pattern))
        if matches:
            return matches[0]
    
    return None


def find_analysis_by_name(repo_name: str, devlogs_path: Path) -> List[Path]:
    """Find analysis files by repo name."""
    repo_name_lower = repo_name.lower().replace('-', '_').replace(' ', '_')
    matches = []
    
    for devlog_file in devlogs_path.glob('*.md'):
        filename_lower = devlog_file.stem.lower()
        if repo_name_lower in filename_lower:
            matches.append(devlog_file)
    
    return matches


def organize_consolidation_groups():
    """Organize repos into consolidation groups."""
    devlogs_path = Path('swarm_brain/devlogs/repository_analysis')
    groups_path = Path('repo_consolidation_groups')
    
    # Create groups directory
    groups_path.mkdir(exist_ok=True)
    
    print(f"📦 Organizing {len(CONSOLIDATION_GROUPS)} consolidation groups...")
    print()
    
    organized_count = 0
    
    for group_name, group_info in CONSOLIDATION_GROUPS.items():
        group_dir = groups_path / group_name
        group_dir.mkdir(exist_ok=True)
        
        print(f"📁 Group: {group_name}")
        print(f"   Target: {group_info.get('target', 'N/A')}")
        
        # Create README for group
        readme_content = f"""# {group_name.replace('_', ' ').title()} Consolidation Group

**Target Repository**: {group_info.get('target', 'N/A')}
**Reduction**: {group_info.get('reduction', 0)} repos

## Consolidation Plan

### Target (Keep):
- {group_info.get('target', 'N/A')} (Repo #{group_info.get('target_repo_num', 'N/A')})

### Merge From:
"""
        for merge_repo in group_info.get('merge_from', []):
            readme_content += f"- {merge_repo['name']} (Repos {merge_repo['repo_nums']})\n"
        
        if group_info.get('note'):
            readme_content += f"\n**Note**: {group_info['note']}\n"
        
        readme_content += f"\n## Status\n\n- [ ] Repos organized into this group\n- [ ] Content merged to target\n- [ ] Secondary repos archived\n- [ ] Documentation updated\n"
        
        (group_dir / 'README.md').write_text(readme_content)
        
        # Copy target analysis
        target_repo_num = group_info.get('target_repo_num')
        if target_repo_num:
            target_file = find_analysis_file(target_repo_num, devlogs_path)
            if target_file:
                shutil.copy2(target_file, group_dir / f"TARGET_{target_file.name}")
                print(f"   ✅ Target analysis copied")
        
        # Copy merge-from analyses
        for merge_repo in group_info.get('merge_from', []):
            for repo_num in merge_repo['repo_nums']:
                merge_file = find_analysis_file(repo_num, devlogs_path)
                if merge_file:
                    dest_name = f"MERGE_FROM_{merge_repo['name']}_{merge_file.name}"
                    shutil.copy2(merge_file, group_dir / dest_name)
                    organized_count += 1
                    print(f"   ✅ {merge_repo['name']} analysis copied")
        
        print()
    
    # Handle duplicate analyses
    print("📋 Handling duplicate analyses...")
    duplicates_dir = groups_path / "duplicate_analyses"
    duplicates_dir.mkdir(exist_ok=True)
    
    for dup_info in CONSOLIDATION_GROUPS['duplicate_analyses']['duplicates']:
        repo_name = dup_info['repo_name']
        keep_repos = dup_info.get('keep', [])
        archive_repos = dup_info.get('archive', [])
        
        print(f"   {repo_name}: Keep {keep_repos}, Archive {archive_repos}")
    
    print()
    print(f"✅ Organized {organized_count} repo analyses into consolidation groups")
    print(f"📁 Groups created in: {groups_path}")
    
    return organized_count


def main():
    """Main organization function."""
    print("📦 Repository Consolidation Group Organizer")
    print("=" * 60)
    print("Building on Agent-3 and Agent-8's consolidation work...")
    print()
    
    organized = organize_consolidation_groups()
    
    print()
    print("=" * 60)
    print(f"✅ Organization complete: {organized} repo analyses organized")
    print()
    print("📋 Next steps:")
    print("   1. Review consolidation groups in repo_consolidation_groups/")
    print("   2. Verify target repos are correct")
    print("   3. Get user approval for consolidations")
    print("   4. Execute repo merging (after approval)")


if __name__ == '__main__':
    main()


