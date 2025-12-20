#!/usr/bin/env python3
"""
Automatic Preference Learning - Self-Improving System
======================================================

Automatically learns from interactions and updates preferences based on:
- Response quality (successful vs failed interactions)
- Effective communication styles
- What works best for each user (Aria/Carmyn)

<!-- SSOT Domain: qa -->

Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


class AutomaticPreferenceLearner:
    """Automatic learning system for user preferences."""
    
    def __init__(self, user: str = "aria", preferences_path: Path = None):
        """Initialize learner for specific user."""
        self.user = user.lower()
        if preferences_path is None:
            project_root = Path(__file__).parent.parent
            preferences_path = project_root / "agent_workspaces" / "Agent-8" / f"{self.user}_preferences.json"
        
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
            f"{self.user}_id": self.user,
            "name": self.user.capitalize(),
            "last_updated": datetime.now().isoformat(),
            "preferences": {},
            "interaction_history": {"total_interactions": 0},
            "learning_insights": {}
        }
    
    def learn_from_interaction(
        self,
        message: str,
        response: Optional[str] = None,
        response_quality: str = "good",
        feedback: Optional[str] = None,
        response_time_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Learn from an interaction and update preferences automatically.
        
        Args:
            message: Original message from user
            response: Agent-8's response (if available)
            response_quality: "excellent", "good", "poor", "failed"
            feedback: User feedback (if provided)
            response_time_seconds: How long it took to respond
        
        Returns:
            Dictionary of insights learned
        """
        insights = {
            "communication_patterns": [],
            "effective_approaches": [],
            "improvement_areas": [],
            "preference_updates": []
        }
        
        message_lower = message.lower()
        
        # 1. Learn from response quality
        if response_quality == "excellent":
            insights["effective_approaches"].append({
                "approach": "Excellent response",
                "context": message[:100],
                "timestamp": datetime.now().isoformat()
            })
            # Update preference: this style works well
            self._update_preference_if_better("response_quality", "excellent")
        
        elif response_quality == "poor" or response_quality == "failed":
            insights["improvement_areas"].append({
                "area": "Response quality",
                "context": message[:100],
                "timestamp": datetime.now().isoformat()
            })
        
        # 2. Learn from response time
        if response_time_seconds:
            if response_time_seconds < 60:
                # Fast response - user might prefer quick responses
                self._update_preference_if_better("response_speed", "preferred_fast")
                insights["communication_patterns"].append("Fast response appreciated")
            elif response_time_seconds > 300:
                # Slow response - might need to adjust
                insights["improvement_areas"].append("Response time could be faster")
        
        # 3. Learn from message content patterns
        if "quick" in message_lower or "fast" in message_lower or "asap" in message_lower:
            self._update_preference("response_speed", "preferred_fast", "preferences")
            insights["communication_patterns"].append("User prefers fast responses")
        
        if "detailed" in message_lower or "explain" in message_lower or "how" in message_lower:
            self._update_preference("detail_level", "preferred_detailed", "preferences")
            insights["communication_patterns"].append("User prefers detailed explanations")
        
        if "simple" in message_lower or "brief" in message_lower or "short" in message_lower:
            self._update_preference("detail_level", "preferred_simple", "preferences")
            insights["communication_patterns"].append("User prefers simple/brief responses")
        
        # 4. Learn from feedback
        if feedback:
            feedback_lower = feedback.lower()
            if any(word in feedback_lower for word in ["great", "perfect", "excellent", "thanks", "love"]):
                # Positive feedback - learn what worked
                insights["effective_approaches"].append({
                    "approach": "Positive feedback received",
                    "feedback": feedback[:100],
                    "timestamp": datetime.now().isoformat()
                })
                self._update_preference_if_better("last_positive_feedback", feedback[:200])
            
            elif any(word in feedback_lower for word in ["confused", "unclear", "didn't work", "wrong"]):
                # Negative feedback - learn what to avoid
                insights["improvement_areas"].append({
                    "area": "Negative feedback received",
                    "feedback": feedback[:100],
                    "timestamp": datetime.now().isoformat()
                })
        
        # 5. Learn from response content (if available)
        if response:
            response_lower = response.lower()
            
            # Track what response styles work
            if len(response) < 200:
                # Short response - might work well
                insights["communication_patterns"].append("Short responses effective")
            elif len(response) > 1000:
                # Long response - might be too much
                insights["improvement_areas"].append("Responses might be too long")
            
            # Learn from response structure
            if "step" in response_lower and "1" in response_lower:
                # Step-by-step approach
                insights["effective_approaches"].append("Step-by-step format works well")
                self._update_preference_if_better("response_format", "step_by_step")
            
            if "example" in response_lower or "here's" in response_lower:
                # Examples work well
                insights["effective_approaches"].append("Examples are effective")
                self._update_preference_if_better("response_format", "with_examples")
        
        # 6. Learn from topic patterns
        topics = self._extract_topics(message)
        if topics:
            # Track which topics lead to successful interactions
            if response_quality in ["excellent", "good"]:
                for topic in topics:
                    self._track_successful_topic(topic)
                    insights["effective_approaches"].append(f"Topic '{topic}' handled well")
        
        # Save insights
        self._save_insights(insights)
        
        # Update interaction history
        self._update_interaction_history(message, response_quality, response_time_seconds)
        
        # Save preferences
        self._save_preferences()
        
        return insights
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extract topics from message."""
        topics = []
        message_lower = message.lower()
        
        # Topic detection patterns
        topic_patterns = {
            "gaming": ["game", "gaming", "gamer"],
            "wordpress": ["wordpress", "wp", "theme"],
            "coding": ["code", "coding", "programming", "script"],
            "design": ["design", "ui", "ux", "graphic"],
            "music": ["music", "song", "track", "mix"],
            "dj": ["dj", "disc jockey", "mixing"],
            "r&b": ["r&b", "rb", "rhythm", "blues"],
            "dance": ["dance", "dancing"],
            "jazz": ["jazz"],
            "website": ["website", "site", "web"],
        }
        
        for topic, patterns in topic_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                topics.append(topic)
        
        return topics
    
    def _track_successful_topic(self, topic: str):
        """Track that a topic was handled successfully."""
        if "learning_insights" not in self.preferences:
            self.preferences["learning_insights"] = {}
        
        if "successful_topics" not in self.preferences["learning_insights"]:
            self.preferences["learning_insights"]["successful_topics"] = {}
        
        if topic not in self.preferences["learning_insights"]["successful_topics"]:
            self.preferences["learning_insights"]["successful_topics"][topic] = 0
        
        self.preferences["learning_insights"]["successful_topics"][topic] += 1
    
    def _update_preference_if_better(self, key: str, value: Any):
        """Update preference only if it's an improvement."""
        current = self.preferences.get("preferences", {}).get(key)
        
        # Simple heuristic: if we don't have a value, or if new value is "excellent", update
        if current is None or (isinstance(value, str) and "excellent" in value.lower()):
            self._update_preference(key, value, "preferences")
    
    def _update_preference(self, key: str, value: Any, category: str = "preferences"):
        """Update a preference."""
        if category not in self.preferences:
            self.preferences[category] = {}
        
        self.preferences[category][key] = value
        self.preferences["last_updated"] = datetime.now().isoformat()
    
    def _save_insights(self, insights: Dict[str, Any]):
        """Save learning insights."""
        if "learning_insights" not in self.preferences:
            self.preferences["learning_insights"] = {}
        
        # Merge insights
        for key, value in insights.items():
            if key not in self.preferences["learning_insights"]:
                self.preferences["learning_insights"][key] = []
            
            if isinstance(value, list):
                self.preferences["learning_insights"][key].extend(value)
                # Keep only last 20 insights per category
                if len(self.preferences["learning_insights"][key]) > 20:
                    self.preferences["learning_insights"][key] = \
                        self.preferences["learning_insights"][key][-20:]
    
    def _update_interaction_history(
        self,
        message: str,
        response_quality: str,
        response_time_seconds: Optional[float]
    ):
        """Update interaction history."""
        history = self.preferences.get("interaction_history", {})
        history["total_interactions"] = history.get("total_interactions", 0) + 1
        history["last_interaction"] = datetime.now().isoformat()
        
        # Track quality distribution
        if "quality_distribution" not in history:
            history["quality_distribution"] = {"excellent": 0, "good": 0, "poor": 0, "failed": 0}
        
        if response_quality in history["quality_distribution"]:
            history["quality_distribution"][response_quality] += 1
        
        # Track average response time
        if response_time_seconds:
            if "response_times" not in history:
                history["response_times"] = []
            history["response_times"].append(response_time_seconds)
            # Keep only last 50 response times
            if len(history["response_times"]) > 50:
                history["response_times"] = history["response_times"][-50:]
            
            # Calculate average
            if history["response_times"]:
                avg_time = sum(history["response_times"]) / len(history["response_times"])
                history["average_response_time_seconds"] = avg_time
        
        self.preferences["interaction_history"] = history
    
    def _save_preferences(self):
        """Save preferences to file."""
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
        self.preferences_path.write_text(
            json.dumps(self.preferences, indent=2),
            encoding='utf-8'
        )
    
    def get_learned_preferences_summary(self) -> str:
        """Get a summary of what has been learned."""
        prefs = self.preferences.get("preferences", {})
        history = self.preferences.get("interaction_history", {})
        insights = self.preferences.get("learning_insights", {})
        
        summary = f"""**Learned Preferences for {self.user.capitalize()}:**

**Communication Patterns:**
- Response Speed: {prefs.get('response_speed', 'not learned yet')}
- Detail Level: {prefs.get('detail_level', 'not learned yet')}
- Response Format: {prefs.get('response_format', 'not learned yet')}

**Interaction Statistics:**
- Total Interactions: {history.get('total_interactions', 0)}
- Quality Distribution: {history.get('quality_distribution', {})}
- Average Response Time: {history.get('average_response_time_seconds', 0):.1f}s

**Successful Topics:**
{self._format_successful_topics(insights.get('successful_topics', {}))}

**Effective Approaches:** {len(insights.get('effective_approaches', []))} recorded
**Improvement Areas:** {len(insights.get('improvement_areas', []))} identified"""
        
        return summary
    
    def _format_successful_topics(self, topics: Dict[str, int]) -> str:
        """Format successful topics for display."""
        if not topics:
            return "  (none yet)"
        
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return "\n".join([f"  - {topic}: {count} successful interactions" for topic, count in sorted_topics[:5]])


def main():
    """CLI for automatic preference learning."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automatic Preference Learning")
    parser.add_argument("--user", type=str, default="aria", choices=["aria", "carmyn"],
                       help="User to learn preferences for")
    parser.add_argument("--message", type=str, required=True,
                       help="Message from user")
    parser.add_argument("--response", type=str, default=None,
                       help="Agent-8's response (optional)")
    parser.add_argument("--quality", type=str, default="good",
                       choices=["excellent", "good", "poor", "failed"],
                       help="Response quality")
    parser.add_argument("--feedback", type=str, default=None,
                       help="User feedback (optional)")
    parser.add_argument("--response-time", type=float, default=None,
                       help="Response time in seconds (optional)")
    parser.add_argument("--summary", action="store_true",
                       help="Show learned preferences summary")
    
    args = parser.parse_args()
    
    learner = AutomaticPreferenceLearner(user=args.user)
    
    if args.summary:
        print(learner.get_learned_preferences_summary())
    else:
        insights = learner.learn_from_interaction(
            message=args.message,
            response=args.response,
            response_quality=args.quality,
            feedback=args.feedback,
            response_time_seconds=args.response_time
        )
        
        print(f"✅ Learned from interaction for {args.user}")
        print(f"   Insights: {len(insights.get('effective_approaches', []))} effective approaches")
        print(f"   Improvements: {len(insights.get('improvement_areas', []))} areas identified")
        print(f"   Patterns: {len(insights.get('communication_patterns', []))} patterns learned")


if __name__ == "__main__":
    sys.exit(main() or 0)

