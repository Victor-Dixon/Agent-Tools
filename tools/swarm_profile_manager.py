#!/usr/bin/env python3
"""
Swarm Profile Manager
=====================

Manages the collective swarm profile - the identity, capabilities, and stats
of the Agent Cellphone V2 Swarm as a unified entity.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-02
Priority: MEDIUM
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class SwarmProfileManager:
    """Manages the swarm's collective profile."""
    
    def __init__(self, profile_path: Optional[Path] = None):
        """Initialize swarm profile manager."""
        if profile_path is None:
            profile_path = PROJECT_ROOT / "swarm_profile.json"
        
        self.profile_path = Path(profile_path)
        self.profile: Dict[str, Any] = {}
        self._load_profile()
    
    def _load_profile(self) -> None:
        """Load swarm profile from file."""
        if self.profile_path.exists():
            with open(self.profile_path, "r", encoding="utf-8") as f:
                self.profile = json.load(f)
        else:
            self._create_default_profile()
    
    def _create_default_profile(self) -> None:
        """Create default swarm profile."""
        self.profile = {
            "swarm_id": "agent_cellphone_v2_swarm",
            "swarm_name": "Agent Cellphone V2 Swarm",
            "swarm_tagline": "WE. ARE. SWARM. ⚡🔥",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "version": "2.0",
        }
    
    def save_profile(self) -> bool:
        """Save swarm profile to file."""
        try:
            self.profile["last_updated"] = datetime.now().isoformat()
            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(self.profile, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving swarm profile: {e}")
            return False
    
    def update_stats(self, stats: Dict[str, Any]) -> bool:
        """Update swarm statistics."""
        if "stats" not in self.profile:
            self.profile["stats"] = {}
        
        self.profile["stats"].update(stats)
        return self.save_profile()
    
    def add_achievement(self, achievement: str, category: str = "major_milestones") -> bool:
        """Add achievement to swarm profile."""
        if "achievements" not in self.profile:
            self.profile["achievements"] = {}
        
        if category not in self.profile["achievements"]:
            self.profile["achievements"][category] = []
        
        if achievement not in self.profile["achievements"][category]:
            self.profile["achievements"][category].append(achievement)
            return self.save_profile()
        
        return True
    
    def update_active_projects(self, projects: List[str]) -> bool:
        """Update active projects list."""
        if "stats" not in self.profile:
            self.profile["stats"] = {}
        
        self.profile["stats"]["active_projects"] = projects
        return self.save_profile()
    
    def update_blockers(self, blockers: List[str]) -> bool:
        """Update current blockers list."""
        if "stats" not in self.profile:
            self.profile["stats"] = {}
        
        self.profile["stats"]["current_blockers"] = blockers
        return self.save_profile()
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current swarm profile."""
        return self.profile.copy()
    
    def get_identity(self) -> Dict[str, Any]:
        """Get swarm identity information."""
        return self.profile.get("identity", {})
    
    def get_stats(self) -> Dict[str, Any]:
        """Get swarm statistics."""
        return self.profile.get("stats", {})
    
    def get_achievements(self) -> Dict[str, Any]:
        """Get swarm achievements."""
        return self.profile.get("achievements", {})
    
    def generate_summary(self) -> str:
        """Generate human-readable summary of swarm profile."""
        identity = self.get_identity()
        stats = self.get_stats()
        achievements = self.get_achievements()
        
        summary = f"""# 🐝 Swarm Profile Summary

**Name**: {self.profile.get('swarm_name', 'Unknown')}  
**Tagline**: {self.profile.get('swarm_tagline', '')}  
**Version**: {self.profile.get('version', 'Unknown')}

## Identity

**Mission**: {identity.get('mission', 'Not defined')}  
**Values**: {', '.join(identity.get('personality', {}).get('values', []))}

## Stats

**Active Projects**: {len(stats.get('active_projects', []))}  
**Current Blockers**: {len(stats.get('current_blockers', []))}  
**Compliance Rate**: {stats.get('compliance_rate', 'Unknown')}

## Achievements

**Major Milestones**: {len(achievements.get('major_milestones', []))}  
**Repos Reduced**: {achievements.get('repository_consolidation', {}).get('repos_reduced', 0)}

---
*Last Updated: {self.profile.get('last_updated', 'Unknown')}*

🐝 **WE. ARE. SWARM. ⚡🔥**
"""
        return summary


def main():
    """CLI interface for swarm profile manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage swarm profile")
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show current swarm profile"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show profile summary"
    )
    parser.add_argument(
        "--update-stats",
        type=str,
        help="Update stats (JSON string)"
    )
    parser.add_argument(
        "--add-achievement",
        type=str,
        help="Add achievement"
    )
    parser.add_argument(
        "--update-projects",
        type=str,
        nargs="+",
        help="Update active projects list"
    )
    parser.add_argument(
        "--update-blockers",
        type=str,
        nargs="+",
        help="Update blockers list"
    )
    
    args = parser.parse_args()
    
    manager = SwarmProfileManager()
    
    if args.show:
        print(json.dumps(manager.get_profile(), indent=2))
    elif args.summary:
        print(manager.generate_summary())
    elif args.update_stats:
        stats = json.loads(args.update_stats)
        if manager.update_stats(stats):
            print("✅ Stats updated")
    elif args.add_achievement:
        if manager.add_achievement(args.add_achievement):
            print(f"✅ Achievement added: {args.add_achievement}")
    elif args.update_projects:
        if manager.update_active_projects(args.update_projects):
            print(f"✅ Active projects updated: {len(args.update_projects)} projects")
    elif args.update_blockers:
        if manager.update_blockers(args.update_blockers):
            print(f"✅ Blockers updated: {len(args.update_blockers)} blockers")
    else:
        print(manager.generate_summary())


if __name__ == "__main__":
    main()

