#!/usr/bin/env python3
"""
Blog Post Generator - "An Honest Review" Series
==============================================

Generates blog posts for DaDudeKC website reviewing each repository.
Uses writing style YAML to match authentic voice.

Author: Agent-7 (Web Development Specialist)
Priority: HIGH
"""

import json
import random
import sys
from pathlib import Path
from typing import Any

import yaml

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class BlogPostGenerator:
    """Generates blog posts following the 'An Honest Review' structure."""

    def __init__(self, style_guide_path: str | Path, repos_data_path: str | Path):
        """Initialize generator with style guide and repo data."""
        self.style_guide_path = Path(style_guide_path)
        self.repos_data_path = Path(repos_data_path)
        self.style_guide: dict[str, Any] = {}
        self.repos: list[dict[str, Any]] = []
        self.output_dir = project_root / "docs" / "blog" / "repo_reviews"
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

    def find_overlaps(self, repo: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify overlapping repositories for overlap alert section."""
        repo_name = repo.get("name", "").lower()
        overlaps = []

        for other_repo in self.repos:
            if other_repo.get("name", "").lower() == repo_name:
                continue

            other_name = other_repo.get("name", "").lower()

            # Check for name similarity
            if self._names_similar(repo_name, other_name):
                overlaps.append(
                    {
                        "name": other_repo.get("name"),
                        "reason": "Similar name",
                        "type": "name_similarity",
                    }
                )

            # Check for same agent (might indicate related work)
            if (
                repo.get("agent") == other_repo.get("agent")
                and repo.get("agent") is not None
            ):
                overlaps.append(
                    {
                        "name": other_repo.get("name"),
                        "reason": f"Same agent ({repo.get('agent')})",
                        "type": "agent_match",
                    }
                )

        return overlaps[:5]  # Limit to 5 overlaps

    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two repo names are similar."""
        # Simple similarity check
        if len(name1) < 3 or len(name2) < 3:
            return False

        # Check for common words
        words1 = set(name1.replace("-", "_").split("_"))
        words2 = set(name2.replace("-", "_").split("_"))
        common = words1.intersection(words2)

        if len(common) > 0 and len(common) >= min(len(words1), len(words2)) * 0.5:
            return True

        # Check prefix/suffix similarity
        if name1[:4] == name2[:4] or name1[-4:] == name2[-4:]:
            return True

        return False

    def get_style_phrase(self, category: str) -> str:
        """Get a random phrase from style guide category."""
        patterns = self.style_guide.get("writing_patterns", {})
        phrases = patterns.get(category, [])

        if phrases:
            return random.choice(phrases)
        return ""

    def generate_what_it_is(self, repo: dict[str, Any]) -> str:
        """Generate 'What It Is' section."""
        name = repo.get("name", "Unknown")
        opening = self.get_style_phrase("opening_styles") or "So I've been working on..."

        return f"""## What It Is

{opening} **{name}**. This is one of those projects I vibe coded when I was trying to solve a specific problem. Honestly, it's {random.choice(['pretty straightforward', 'kinda complex', 'a bit messy', 'actually pretty clean'])} - {random.choice(['a tool', 'an app', 'a script', 'a system'])} that does what it says on the tin."""

    def generate_why_built(self, repo: dict[str, Any]) -> str:
        """Generate 'Why I Built It' section."""
        name = repo.get("name", "Unknown")
        reflection = (
            self.get_style_phrase("reflection_patterns")
            or "Looking back, I built this because..."
        )

        return f"""## Why I Built It

{reflection} I needed something that could handle {name.replace('-', ' ').replace('_', ' ')}. The thing is, I couldn't find exactly what I wanted out there, so I {random.choice(['threw together', 'hacked together', 'built'])} this in {random.choice(['a weekend', 'a few days', 'my spare time'])}. 

Was it the best solution? Probably not. But it was *my* solution, and that's what matters when you're vibe coding."""

    def generate_what_learned(self, repo: dict[str, Any]) -> str:
        """Generate 'What I Learned' section."""
        casual = random.choice(
            self.style_guide.get("voice_markers", {}).get("casual_phrases", ["honestly"])
        )

        return f"""## What I Learned

{casual.capitalize()}, this project taught me a lot. I learned about {random.choice(['how to structure code better', 'the importance of testing', 'why documentation matters', 'how to handle edge cases', 'the value of simplicity'])}. 

The thing I wish I knew before starting? {random.choice(['How much time this would take', 'That there was a simpler way', 'That I should have planned better', 'That this would become part of a bigger system'])}. But that's the beauty of vibe coding - you learn as you go."""

    def generate_what_worked(self, repo: dict[str, Any]) -> str:
        """Generate 'What Worked' section."""
        return f"""## What Worked

The parts that actually worked? {random.choice(['The core functionality', 'The user interface', 'The data processing', 'The integration', 'The overall architecture'])}. It's {random.choice(['actually works', 'kinda works', 'works well enough'])} for what I needed it to do.

I'm particularly proud of how {random.choice(['clean', 'simple', 'efficient', 'maintainable'])} the {random.choice(['code structure', 'API design', 'data flow', 'error handling'])} turned out. Small wins, but wins nonetheless."""

    def generate_what_didnt(self, repo: dict[str, Any]) -> str:
        """Generate 'What Didn't' section."""
        issue = random.choice(
            ["The error handling", "The documentation", "The testing", "The performance", "The user experience"]
        )
        approach = random.choice(["over-engineered", "under-engineered"])
        result = random.choice(["it shows", "I learned from it", "I'd do it differently now"])
        biggest = random.choice(
            ["not planning for scale", "skipping tests", "poor documentation", "rushing the implementation", "not thinking about edge cases"]
        )
        
        return f"""## What Didn't

Now for the honest part - what didn't work. {issue} could definitely be better. I {approach} some parts, and {result}.

The biggest issue? Probably {biggest}. But hey, that's how you learn, right?"""

    def generate_overlap_alert(self, repo: dict[str, Any]) -> str:
        """Generate 'Overlap Alert' section with overlap analysis."""
        overlaps = self.find_overlaps(repo)

        if not overlaps:
            return """## Overlap Alert

Looking at my other projects, this one is pretty unique. No major overlaps that I can see - which is both good and bad. Good because it means I'm not duplicating work, bad because maybe I should have built on something existing instead."""

        overlap_list = "\n".join(
            f"- **{overlap['name']}**: {overlap['reason']}" for overlap in overlaps
        )

        return f"""## Overlap Alert

🚨 **Overlap Detected!** This project has some connections to other repos:

{overlap_list}

**Consolidation Opportunity?** Maybe. These could potentially be merged or at least share more code. But honestly, sometimes having separate repos is fine - especially if they serve different purposes or were built at different times."""

    def generate_would_build_again(self, repo: dict[str, Any]) -> str:
        """Generate 'Would I Build It Again?' section."""
        reflection = (
            self.get_style_phrase("reflection_patterns")
            or "If I did this again..."
        )

        return f"""## Would I Build It Again?

{reflection} I'd probably {random.choice(['do it differently', 'use a different approach', 'plan it better', 'build on existing code', 'make it simpler'])}. 

Would I build it again from scratch? {random.choice(['Probably not', 'Maybe', 'Definitely', 'Only if I had to'])}. But I don't regret building it - every project teaches you something, and this one was no exception."""

    def generate_verdict(self, repo: dict[str, Any]) -> str:
        """Generate 'The Verdict' section."""
        closing = (
            self.get_style_phrase("closing_styles")
            or "Anyway, that's the honest review..."
        )

        name = repo.get("name", "Unknown")
        goldmine = repo.get("goldmine", False)

        verdict_text = f"""## The Verdict

{closing} **{name}** is what it is - a vibe coded project that {random.choice(['works', 'kinda works', 'does the job', 'needs work'])}. 

"""
        if goldmine:
            verdict_text += "**Goldmine Alert**: This one is marked as a goldmine - meaning it has significant value or potential. Definitely worth keeping and maybe even expanding.\n\n"

        verdict_text += f"""It's out there if you want to check it out. Take it or leave it - but hopefully you can learn something from my mistakes (and successes) along the way."""

        return verdict_text

    def generate_post(self, repo: dict[str, Any]) -> str:
        """Generate complete blog post for a repository."""
        name = repo.get("name", "Unknown")
        title = f"An Honest Review: {name}"

        sections = [
            f"# {title}\n",
            self.generate_what_it_is(repo),
            self.generate_why_built(repo),
            self.generate_what_learned(repo),
            self.generate_what_worked(repo),
            self.generate_what_didnt(repo),
            self.generate_overlap_alert(repo),
            self.generate_would_build_again(repo),
            self.generate_verdict(repo),
        ]

        return "\n\n".join(sections)

    def save_post(self, repo: dict[str, Any], content: str) -> Path:
        """Save blog post to file."""
        name = repo.get("name", "unknown")
        filename = f"{name.replace('/', '_')}_review.md"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def generate_all(self) -> list[Path]:
        """Generate blog posts for all repositories."""
        print(f"📝 Generating blog posts for {len(self.repos)} repositories...")
        generated_files = []

        for i, repo in enumerate(self.repos, 1):
            if not repo.get("name") or repo.get("name") == "Unknown":
                continue

            print(f"  [{i}/{len(self.repos)}] Generating post for {repo.get('name')}...")
            post_content = self.generate_post(repo)
            filepath = self.save_post(repo, post_content)
            generated_files.append(filepath)

        return generated_files

    def generate_single(self, repo_name: str) -> Path | None:
        """Generate blog post for a single repository."""
        repo = next((r for r in self.repos if r.get("name") == repo_name), None)

        if not repo:
            print(f"❌ Repository '{repo_name}' not found")
            return None

        print(f"📝 Generating blog post for {repo_name}...")
        post_content = self.generate_post(repo)
        filepath = self.save_post(repo, post_content)
        print(f"✅ Saved to: {filepath}")
        return filepath


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate 'An Honest Review' blog posts for repositories"
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

    args = parser.parse_args()

    generator = BlogPostGenerator(args.style_guide, args.repos_data)

    try:
        generator.load_style_guide()
        generator.load_repos()

        if args.repo:
            generator.generate_single(args.repo)
        else:
            files = generator.generate_all()
            print(f"\n✅ Generated {len(files)} blog posts in {generator.output_dir}")

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

