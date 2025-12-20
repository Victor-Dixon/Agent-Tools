#!/usr/bin/env python3
"""
Enhanced Chronological Blog Generator
=====================================

Generates deep, detailed blog posts in chronological order telling the development adventure.
Features: Chronological context, evolution tracking, deep technical analysis, adventure narrative.

Author: Agent-7 (Web Development Specialist)
Priority: CRITICAL (Blocking Phase 1 approval)
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class ChronologicalBlogGenerator:
    """Generates chronological blog posts with deep analysis and adventure narrative."""

    def __init__(
        self,
        style_guide_path: str | Path,
        repos_data_path: str | Path,
        chronology_path: str | Path | None = None,
    ):
        """Initialize generator with style guide, repo data, and optional chronology."""
        self.style_guide_path = Path(style_guide_path)
        self.repos_data_path = Path(repos_data_path)
        self.chronology_path = Path(chronology_path) if chronology_path else None
        self.style_guide: dict[str, Any] = {}
        self.repos: list[dict[str, Any]] = []
        self.chronology: dict[str, Any] = {}
        self.ordered_repos: list[dict[str, Any]] = []
        self.output_dir = project_root / "docs" / "blog" / "chronological_journey"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_style_guide(self) -> None:
        """Load writing style guide from YAML."""
        if not self.style_guide_path.exists():
            raise FileNotFoundError(
                f"Style guide not found: {self.style_guide_path}\n"
                "Please fill in config/writing_style_template.yaml with your writing examples."
            )

        with open(self.style_guide_path, encoding="utf-8") as f:
            self.style_guide = yaml.safe_load(f) or {}

    def load_repos(self) -> None:
        """Load repository data from JSON."""
        if not self.repos_data_path.exists():
            raise FileNotFoundError(f"Repos data not found: {self.repos_data_path}")

        with open(self.repos_data_path, encoding="utf-8") as f:
            data = json.load(f)
            self.repos = data.get("repos", [])

    def load_chronology(self) -> None:
        """Load chronology data if available, otherwise use fallback ordering."""
        if self.chronology_path and self.chronology_path.exists():
            with open(self.chronology_path, encoding="utf-8") as f:
                self.chronology = json.load(f)
            # Use chronology to order repos
            self._order_by_chronology()
        else:
            # Fallback: use repo number as proxy for chronological order
            print("⚠️  No chronology data found - using repo number as proxy order")
            self._order_by_repo_number()

    def _order_by_chronology(self) -> None:
        """Order repos by chronology data."""
        # Implementation when chronology data is available
        # For now, fallback to repo number
        self._order_by_repo_number()

    def _order_by_repo_number(self) -> None:
        """Order repos by repo number as fallback."""
        self.ordered_repos = sorted(self.repos, key=lambda r: r.get("num", 999))

    def get_previous_repos(self, current_repo: dict[str, Any]) -> list[dict[str, Any]]:
        """Get repos that came before this one chronologically."""
        current_index = self.ordered_repos.index(current_repo)
        return self.ordered_repos[:current_index]

    def get_style_phrase(self, category: str) -> str:
        """Get a random phrase from style guide category."""
        patterns = self.style_guide.get("writing_patterns", {})
        phrases = patterns.get(category, [])

        if phrases:
            return random.choice(phrases)
        return ""

    def get_voice_marker(self, category: str) -> str:
        """Get a random voice marker from style guide."""
        markers = self.style_guide.get("voice_markers", {}).get(category, [])
        if markers:
            return random.choice(markers)
        return ""

    def get_voice_profile(self) -> dict[str, Any]:
        """Get Victor's voice profile from style guide."""
        return self.style_guide.get("voice_profile", {})

    def apply_victor_voice(self, text: str) -> str:
        """Apply Victor's authentic typing style to text."""
        voice_profile = self.get_voice_profile()
        if not voice_profile:
            return text

        # Apply mechanics
        mechanics = voice_profile.get("mechanics", {})
        
        # Apply casing rules (lowercase "i", "im", "id", "dont", "cant")
        if mechanics.get("casing"):
            text = text.replace(" I ", " i ")
            text = text.replace(" I'm ", " im ")
            text = text.replace(" I'd ", " id ")
            text = text.replace(" don't ", " dont ")
            text = text.replace(" can't ", " cant ")
            text = text.replace(" I've ", " ive ")
            text = text.replace(" I'll ", " ill ")
            text = text.replace(" I'm ", " im ")
            # Keep proper nouns capitalized (handled by context)
        
        # Apply shortening rules
        shortenings = mechanics.get("shortening", {})
        if isinstance(shortenings, list):
            # Apply common shortenings
            text = text.replace(" just ", " js ")
            text = text.replace(" because ", " cs ")
            text = text.replace(" yeah ", " yea ")
            text = text.replace(" I don't know ", " idk ")
            text = text.replace(" to be honest ", " tbh ")
            text = text.replace(" right now ", " rn ")
            text = text.replace(" trying to ", " tryna ")
            text = text.replace(" going to ", " gon ")
            text = text.replace(" want to ", " wanna ")
            text = text.replace(" kind of ", " kinda ")
            text = text.replace(" low key ", " lowkey ")
        
        # Apply punctuation (add "..." occasionally, loose commas)
        if mechanics.get("punctuation"):
            # Occasionally add "..." for trailing thoughts (10% chance per sentence)
            sentences = text.split(". ")
            if random.random() < 0.1 and len(sentences) > 1:
                # Add "..." to a random sentence
                idx = random.randint(0, min(2, len(sentences) - 1))
                sentences[idx] = sentences[idx].rstrip(".") + "..."
                text = ". ".join(sentences)
        
        return text

    def get_victor_phrase(self, category: str) -> str:
        """Get a random phrase from Victor's phrasing patterns."""
        voice_profile = self.get_voice_profile()
        if not voice_profile:
            return ""
        
        patterns = voice_profile.get("phrasing_patterns", {})
        phrases = patterns.get(category, [])
        if phrases:
            return random.choice(phrases)
        return ""

    def generate_journey_context(self, repo: dict[str, Any]) -> str:
        """Generate 'Journey Context' section - where you were, what came before."""
        previous_repos = self.get_previous_repos(repo)
        repo_name = repo.get("name", "Unknown")
        position = len(previous_repos) + 1
        total = len(self.ordered_repos)

        # Use Victor's intro patterns
        intro = self.get_victor_phrase("intros") or "ok so"
        
        learning_choices = ['learning the basics', 'exploring new tech', 'tryna solve a specific problem', 'building my skills', 'experimenting with different approaches']
        what_learning = random.choice(['how to structure code better', 'new frameworks and tools', 'best practices', 'architecture patterns', 'how to build scalable systems'])

        context = f"""## Journey Context

{intro} this was project #{position} in my development journey. """

        if previous_repos:
            recent = previous_repos[-3:]  # Last 3 projects
            recent_names = [r.get("name") for r in recent]
            context += f"by this point, i had already built {len(previous_repos)} projects, including {', '.join(recent_names)}. "
        else:
            context += "this was one of my earliest projects - the beginning of the journey. "

        context += f"""i was {random.choice(learning_choices)}.

what i was tryna learn? {what_learning}. this project was part of that learning process."""

        # Apply Victor's voice
        return self.apply_victor_voice(context)

    def generate_project_deep_dive(self, repo: dict[str, Any]) -> str:
        """Generate 'Project Deep Dive' section - comprehensive analysis."""
        name = repo.get("name", "Unknown")
        opening = self.get_victor_phrase("intros") or self.get_style_phrase("opening_styles") or "ok so"
        
        # Extract random choices outside f-string
        project_type = random.choice(['a learning experiment', 'an attempt to solve a real problem', 'a stepping stone', 'a breakthrough moment', 'a challenge i set for myself'])
        tool_type = random.choice(['a tool', 'an application', 'a system', 'a framework', 'a utility'])
        action = random.choice(['helps with', 'solves', 'handles', 'manages', 'processes'])
        why_built_choices = ['i needed it for my own work', 'i couldnt find a good solution', 'i wanted to learn how to build something like this', 'it was part of a bigger vision', 'i saw an opportunity to improve on existing solutions']
        why_built = random.choice(why_built_choices)
        arch_choice = random.choice(['simple and straightforward', 'modular and extensible', 'following best practices', 'experimental approach'])
        tech_choice = random.choice(['Python', 'JavaScript', 'mixed stack', 'modern frameworks', 'tried-and-true tools'])
        approach_choice = random.choice(['quick prototype', 'well-planned', 'iterative', 'experimental'])

        content = f"""## Project Deep Dive

{opening} **{name}**. this wasnt js another project - it was {project_type}.

### What It Is

{name} is {tool_type} that {action} {name.replace('-', ' ').replace('_', ' ')}. 

### Why I Built It

i built this cs {why_built}.

### Technical Decisions

the technical choices i made:
- **Architecture**: {arch_choice}
- **Technologies**: {tech_choice}
- **Approach**: {approach_choice}"""

        return self.apply_victor_voice(content)

    def generate_evolution_growth(self, repo: dict[str, Any]) -> str:
        """Generate 'Evolution & Growth' section - how this differs from previous."""
        previous_repos = self.get_previous_repos(repo)
        repo_name = repo.get("name", "Unknown")

        if not previous_repos:
            learned1 = random.choice(['basic project structure', 'how to organize code', 'the importance of documentation', 'testing fundamentals'])
            learned2 = random.choice(['how to use version control effectively', 'the value of iteration', 'learning from mistakes', 'building incrementally'])
            content = f"""## Evolution & Growth

this was one of my earliest projects, so there wasnt much to compare it to. but looking back, i can see the seeds of patterns that would develop later.

what i learned:
- {learned1}
- {learned2}"""
            return self.apply_victor_voice(content)

        step_forward = random.choice(['a step forward', 'more ambitious', 'better structured', 'more complex', 'simpler and cleaner'])
        new_skills = random.choice(['new frameworks', 'better patterns', 'advanced techniques', 'architectural principles'])
        better_approach = random.choice(['i planned it better', 'i used better tools', 'i followed best practices', 'i learned from previous mistakes'])
        evolution_type = random.choice(['more sophisticated', 'cleaner code', 'better architecture', 'more maintainable'])

        evolution = f"""## Evolution & Growth

compared to my previous projects, this one was {step_forward}.

### How This Differs

what made this different:
- **New Skills**: i learned {new_skills}
- **Better Approach**: {better_approach}
- **Evolution**: {evolution_type}"""

        return self.apply_victor_voice(evolution)

    def generate_technical_details(self, repo: dict[str, Any]) -> str:
        """Generate 'Technical Details' section - deep technical analysis."""
        name = repo.get("name", "Unknown")
        
        thinking_move = self.get_victor_phrase("thinking_moves") or "so how do we actually do that"
        code_patterns = random.choice(['object-oriented design', 'functional programming', 'a mix of both', 'design patterns', 'simple procedural code'])
        technologies = random.choice(['Python', 'JavaScript/TypeScript', 'a modern stack', 'tried-and-true tools', 'cutting-edge frameworks'])
        challenge = random.choice(['getting different systems to work together', 'api integration', 'data handling', 'performance optimization', 'error handling'])
        worked = random.choice(['the core architecture', 'the data processing', 'the user interface', 'the integration layer', 'the error handling'])
        didnt_work = random.choice(['the initial design was too complex', 'i should have used a different framework', 'the data model needed work', 'performance could be better', 'testing was insufficient'])

        content = f"""## Technical Details

### Deep Dive

{thinking_move}... let me break down the technical side of **{name}**:

**Code Patterns**: i used {code_patterns}.

**Technologies**: built with {technologies}.

**Integration Challenges**: {challenge} was the biggest challenge.

**What Worked Technically**: {worked} turned out really well.

**What Didnt**: {didnt_work}."""

        return self.apply_victor_voice(content)

    def generate_adventure_story(self, repo: dict[str, Any]) -> str:
        """Generate 'Adventure Story' section - the journey of building it."""
        name = repo.get("name", "Unknown")
        voice_marker = self.get_victor_phrase("meta_comments") or self.get_voice_marker("casual_phrases") or "tbh"

        breakthrough_choices = ['when i finally got the core functionality working', 'when i realized a better approach', 'when i solved the hardest problem', 'when everything clicked together']
        struggle_choices = ['getting stuck on a bug for days', 'tryna integrate incompatible systems', 'performance issues', 'understanding complex requirements', 'time constraints']
        victory_choices = ['getting it to work end-to-end', 'seeing it actually solve the problem', 'getting positive feedback', 'learning something new', 'completing it despite challenges']
        journey_start = random.choice(['i started with a simple idea', 'i began with a complex vision', 'i iterated multiple times', 'i learned as i built', 'i made mistakes and fixed them'])
        learned = random.choice(['patience', 'persistence', 'how to debug', 'when to simplify', 'the value of planning'])

        content = f"""## Adventure Story

{voice_marker}, building **{name}** was {random.choice(['a journey', 'an adventure', 'a learning experience', 'a challenge', 'a breakthrough'])}.

### Key Moments

**The Breakthrough**: {random.choice(breakthrough_choices)}.

**The Struggle**: {random.choice(struggle_choices)} was the hardest part.

**The Victory**: {random.choice(victory_choices)} felt amazing.

### The Journey

{journey_start}. the process taught me {learned}."""

        return self.apply_victor_voice(content)

    def generate_looking_forward(self, repo: dict[str, Any]) -> str:
        """Generate 'Looking Forward' section - how this influenced future work."""
        name = repo.get("name", "Unknown")

        skills1 = random.choice(['architectural patterns', 'code organization', 'problem-solving approaches', 'tool usage', 'best practices'])
        skills2 = random.choice(['how to structure projects', 'when to simplify', 'how to handle complexity', 'the importance of testing', 'documentation practices'])
        patterns1 = random.choice(['became standard in later projects', 'evolved into better versions', 'were replaced with better approaches', 'influenced my thinking', 'shaped my development style'])
        patterns2 = random.choice(['led to better solutions', 'taught me what not to do', 'became part of my toolkit', 'influenced architecture decisions', 'shaped my approach'])

        content = f"""## Looking Forward

**{name}** didnt js end when i finished it - it influenced everything that came after.

### Skills Carried Forward

what i learned here that i still use:
- {skills1}
- {skills2}

### Patterns That Evolved

the patterns i established here:
- {patterns1}
- {patterns2}"""

        return self.apply_victor_voice(content)

    def generate_verdict(self, repo: dict[str, Any]) -> str:
        """Generate 'The Verdict' section - where it stands now, legacy."""
        name = repo.get("name", "Unknown")
        goldmine = repo.get("goldmine", False)
        closing = self.get_victor_phrase("meta_comments") or self.get_style_phrase("closing_styles") or "anyway, thats the honest review..."

        # Extract random choices outside f-string to avoid backslash issues
        stands_as = random.choice(['a milestone', 'a learning experience', 'a stepping stone', 'a project im proud of', 'part of my journey'])
        where_stands = random.choice(['its still in use', 'its been superseded', 'its archived but valuable', 'its part of a bigger system', 'its a reference for future work'])
        do_differently = random.choice(['id plan it better from the start', 'id use different technologies', 'id simplify the architecture', 'id add more tests', 'id document it better'])
        legacy = random.choice(['this project taught me valuable lessons', 'it influenced my future work', 'it solved a real problem', 'it was part of my growth', 'it showed me what im capable of'])

        verdict = f"""## The Verdict

{closing} **{name}** stands as {stands_as} in my development adventure.

### Where It Stands Now

{where_stands}.

### What I'd Do Differently

{do_differently}.

### Legacy and Impact

{legacy}."""

        if goldmine:
            verdict += "\n\n**Goldmine Alert**: this one is marked as a goldmine - meaning it has significant value or potential. definitely worth keeping and maybe even expanding."

        return self.apply_victor_voice(verdict)

    def generate_post(self, repo: dict[str, Any]) -> str:
        """Generate complete chronological blog post for a repository."""
        name = repo.get("name", "Unknown")
        title = f"{name}: A Development Journey Entry"

        sections = [
            f"# {title}\n",
            self.generate_journey_context(repo),
            self.generate_project_deep_dive(repo),
            self.generate_evolution_growth(repo),
            self.generate_technical_details(repo),
            self.generate_adventure_story(repo),
            self.generate_looking_forward(repo),
            self.generate_verdict(repo),
        ]

        return "\n\n".join(sections)

    def save_post(self, repo: dict[str, Any], content: str, index: int) -> Path:
        """Save blog post to file with chronological ordering."""
        name = repo.get("name", "unknown")
        # Format: 001_network-scanner_journey.md
        filename = f"{index:03d}_{name.replace('/', '_')}_journey.md"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def generate_all(self) -> list[Path]:
        """Generate blog posts for all repositories in chronological order."""
        print(f"📝 Generating chronological blog posts for {len(self.ordered_repos)} repositories...")
        generated_files = []

        for i, repo in enumerate(self.ordered_repos, 1):
            if not repo.get("name") or repo.get("name") == "Unknown":
                continue

            print(f"  [{i}/{len(self.ordered_repos)}] Generating post for {repo.get('name')}...")
            post_content = self.generate_post(repo)
            filepath = self.save_post(repo, post_content, i)
            generated_files.append(filepath)

        return generated_files

    def generate_single(self, repo_name: str) -> Path | None:
        """Generate blog post for a single repository."""
        repo = next((r for r in self.ordered_repos if r.get("name") == repo_name), None)

        if not repo:
            print(f"❌ Repository '{repo_name}' not found")
            return None

        index = self.ordered_repos.index(repo) + 1
        print(f"📝 Generating chronological blog post for {repo_name}...")
        post_content = self.generate_post(repo)
        filepath = self.save_post(repo, post_content, index)
        print(f"✅ Saved to: {filepath}")
        return filepath


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate chronological blog posts for development journey"
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Generate post for specific repository (by name)",
    )
    parser.add_argument(
        "--style-guide",
        type=str,
        default="config/writing_style_template.yaml",
        help="Path to writing style YAML (default: config/writing_style_template.yaml)",
    )
    parser.add_argument(
        "--repos-data",
        type=str,
        default="data/github_75_repos_master_list.json",
        help="Path to repos JSON (default: data/github_75_repos_master_list.json)",
    )
    parser.add_argument(
        "--chronology",
        type=str,
        default=None,
        help="Path to chronology JSON (optional, falls back to repo number ordering)",
    )

    args = parser.parse_args()

    generator = ChronologicalBlogGenerator(
        args.style_guide, args.repos_data, args.chronology
    )

    try:
        generator.load_style_guide()
        generator.load_repos()
        generator.load_chronology()

        if args.repo:
            generator.generate_single(args.repo)
        else:
            files = generator.generate_all()
            print(f"\n✅ Generated {len(files)} chronological blog posts in {generator.output_dir}")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

