#!/usr/bin/env python3
"""
Update Aria Preferences - Self-Improving System
================================================

Tool for Agent-8 to update Aria's preferences based on interactions.
This makes the system self-improving - learns how Aria likes to work.

<!-- SSOT Domain: qa -->

Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class AriaPreferencesUpdater:
    """Self-improving preferences system for Aria."""
    
    def __init__(self, preferences_path: Path = None):
        """Initialize preferences updater."""
        if preferences_path is None:
            project_root = Path(__file__).parent.parent
            preferences_path = project_root / "agent_workspaces" / "Agent-8" / "aria_preferences.json"
        
        self.preferences_path = preferences_path
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load current preferences."""
        try:
            if self.preferences_path.exists():
                return json.loads(self.preferences_path.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"⚠️  Error loading preferences: {e}")
        
        # Return default structure
        return {
            "aria_id": "aria",
            "name": "Aria",
            "last_updated": datetime.now().isoformat(),
            "preferences": {},
            "interaction_history": {"total_interactions": 0},
            "learning_insights": {}
        }
    
    def update_preference(self, key: str, value: Any, category: str = "preferences"):
        """Update a specific preference."""
        if category not in self.preferences:
            self.preferences[category] = {}
        
        self.preferences[category][key] = value
        self.preferences["last_updated"] = datetime.now().isoformat()
        self._save_preferences()
        print(f"✅ Updated {category}.{key} = {value}")
    
    def add_insight(self, insight_type: str, insight: str):
        """Add a learning insight."""
        if "learning_insights" not in self.preferences:
            self.preferences["learning_insights"] = {}
        
        if insight_type not in self.preferences["learning_insights"]:
            self.preferences["learning_insights"][insight_type] = []
        
        self.preferences["learning_insights"][insight_type].append({
            "insight": insight,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 insights per type
        if len(self.preferences["learning_insights"][insight_type]) > 10:
            self.preferences["learning_insights"][insight_type] = \
                self.preferences["learning_insights"][insight_type][-10:]
        
        self.preferences["last_updated"] = datetime.now().isoformat()
        self._save_preferences()
        print(f"✅ Added insight: {insight_type} - {insight}")
    
    def record_interaction(self, topic: str, outcome: str = "success"):
        """Record an interaction for learning."""
        history = self.preferences.get("interaction_history", {})
        history["total_interactions"] = history.get("total_interactions", 0) + 1
        history["last_interaction"] = datetime.now().isoformat()
        
        topics = history.get("topics_discussed", [])
        if topic not in topics:
            topics.append(topic)
        history["topics_discussed"] = topics
        
        if outcome == "success":
            successes = history.get("successful_collaborations", [])
            successes.append({
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            })
            history["successful_collaborations"] = successes[-20:]  # Keep last 20
        
        self.preferences["interaction_history"] = history
        self.preferences["last_updated"] = datetime.now().isoformat()
        self._save_preferences()
        print(f"✅ Recorded interaction: {topic} ({outcome})")
    
    def learn_from_interaction(self, message: str, response_quality: str = "good"):
        """Learn from an interaction and update preferences."""
        message_lower = message.lower()
        
        # Detect communication style preferences
        if "quick" in message_lower or "fast" in message_lower:
            self.update_preference("response_speed", "preferred_fast", "preferences")
        
        if "detailed" in message_lower or "explain" in message_lower:
            self.update_preference("detail_level", "preferred_detailed", "preferences")
        
        if "simple" in message_lower or "brief" in message_lower:
            self.update_preference("detail_level", "preferred_simple", "preferences")
        
        # Detect project interests
        if "game" in message_lower or "gaming" in message_lower:
            self.record_interaction("gaming", response_quality)
        
        if "wordpress" in message_lower or "theme" in message_lower:
            self.record_interaction("wordpress", response_quality)
        
        if "code" in message_lower or "coding" in message_lower:
            self.record_interaction("coding", response_quality)
        
        # Add insight based on response quality
        if response_quality == "excellent":
            self.add_insight("effective_approaches", f"Excellent response for: {message[:100]}")
        elif response_quality == "poor":
            self.add_insight("improvement_areas", f"Could improve response for: {message[:100]}")
    
    def get_preferences_summary(self) -> str:
        """Get a summary of Aria's preferences for message templates."""
        prefs = self.preferences.get("preferences", {})
        history = self.preferences.get("interaction_history", {})
        
        summary = f"""**Aria's Preferences:**
- Communication Style: {prefs.get('communication_style', 'friendly and encouraging')}
- Response Tone: {prefs.get('response_tone', 'supportive and helpful')}
- Work Approach: {prefs.get('work_approach', 'creative and collaborative')}
- Project Focus: {', '.join(prefs.get('project_focus', ['gaming', 'web development']))}
- Interests: {', '.join(prefs.get('interests', ['gaming', 'coding', 'design']))}

**Interaction History**: {history.get('total_interactions', 0)} interactions
**Topics Discussed**: {', '.join(history.get('topics_discussed', []))}"""
        
        return summary
    
    def _save_preferences(self):
        """Save preferences to file."""
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
        self.preferences_path.write_text(
            json.dumps(self.preferences, indent=2),
            encoding='utf-8'
        )


def main():
    """CLI for updating preferences."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update Aria's Preferences")
    parser.add_argument("--update", nargs=2, metavar=("KEY", "VALUE"),
                       help="Update a preference (e.g., --update communication_style 'friendly')")
    parser.add_argument("--insight", nargs=2, metavar=("TYPE", "INSIGHT"),
                       help="Add a learning insight")
    parser.add_argument("--interaction", nargs=1, metavar="TOPIC",
                       help="Record an interaction")
    parser.add_argument("--learn", nargs=2, metavar=("MESSAGE", "QUALITY"),
                       help="Learn from interaction (quality: excellent/good/poor)")
    parser.add_argument("--show", action="store_true",
                       help="Show current preferences")
    
    args = parser.parse_args()
    
    updater = AriaPreferencesUpdater()
    
    if args.update:
        key, value = args.update
        updater.update_preference(key, value)
    elif args.insight:
        insight_type, insight = args.insight
        updater.add_insight(insight_type, insight)
    elif args.interaction:
        updater.record_interaction(args.interaction[0])
    elif args.learn:
        message, quality = args.learn
        updater.learn_from_interaction(message, quality)
    elif args.show:
        print(updater.get_preferences_summary())
    else:
        parser.print_help()


if __name__ == "__main__":
    sys.exit(main() or 0)

