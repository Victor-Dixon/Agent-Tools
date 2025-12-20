#!/usr/bin/env python3
"""
Report Truthfulness Enhancer
============================

Adds scope tags and verifiable evidence links to Agent-2 reports
to ensure claims can be verified and are truthful.

Author: Agent-2 (Architecture & Design Specialist)
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class ReportTruthfulnessEnhancer:
    """Enhance reports with scope tags and evidence links."""

    # SSOT Domain mapping for scope tags
    SSOT_DOMAINS = {
        'infrastructure': 'infrastructure',
        'integration': 'integration',
        'communication': 'communication',
        'architecture': 'architecture',
        'web': 'web',
        'analytics': 'analytics',
        'core': 'core',
        'tools': 'tools',
        'documentation': 'documentation',
    }

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize enhancer."""
        self.repo_root = repo_root or project_root
        self.git_available = self._check_git()

    def _check_git(self) -> bool:
        """Check if git is available."""
        try:
            import subprocess
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                timeout=2,
                cwd=self.repo_root
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_file_commit_hash(self, file_path: Path) -> Optional[str]:
        """Get latest commit hash for a file."""
        if not self.git_available:
            return None

        try:
            import subprocess
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H', '--', str(file_path)],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.repo_root
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()[:12]  # Short hash
        except Exception:
            pass
        return None

    def get_file_line_count(self, file_path: Path) -> Optional[int]:
        """Get line count for a file."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return len(f.readlines())
        except Exception:
            pass
        return None

    def infer_scope(self, file_path: Path, content: str) -> str:
        """Infer SSOT domain scope from file path and content."""
        path_str = str(file_path)

        # Check path patterns
        if 'infrastructure' in path_str.lower():
            return 'infrastructure'
        if 'integration' in path_str.lower():
            return 'integration'
        if 'messaging' in path_str.lower() or 'communication' in path_str.lower():
            return 'communication'
        if 'architecture' in path_str.lower() or 'design' in path_str.lower():
            return 'architecture'
        if 'web' in path_str.lower() or 'wordpress' in path_str.lower():
            return 'web'
        if 'analytics' in path_str.lower():
            return 'analytics'
        if 'core' in path_str.lower():
            return 'core'
        if 'tools' in path_str.lower():
            return 'tools'
        if 'docs' in path_str.lower() or 'documentation' in path_str.lower():
            return 'documentation'

        # Check content for SSOT comments
        ssot_match = re.search(
            r'<!--\s*SSOT\s+Domain:\s*(\w+)', content, re.IGNORECASE)
        if ssot_match:
            return ssot_match.group(1).lower()

        # Default
        return 'general'

    def create_evidence_link(self, file_path: Path, label: Optional[str] = None) -> str:
        """Create verifiable evidence link for a file."""
        # Resolve absolute path if relative
        if not file_path.is_absolute():
            file_path = (self.repo_root / file_path).resolve()
        rel_path = file_path.relative_to(self.repo_root)
        commit_hash = self.get_file_commit_hash(file_path)
        line_count = self.get_file_line_count(file_path)

        # Create label
        if not label:
            label = rel_path.name

        # Build link components
        link_parts = [f"[`{label}`]({rel_path})"]

        # Add verification info
        verification_info = []
        if commit_hash:
            verification_info.append(f"commit: `{commit_hash}`")
        if line_count is not None:
            verification_info.append(f"{line_count} lines")
        if verification_info:
            link_parts.append(f" ({', '.join(verification_info)})")

        return ''.join(link_parts)

    def enhance_artifacts_section(self, content: str, artifacts: List[Tuple[str, Path]]) -> str:
        """Enhance artifacts section with evidence links."""
        # Find artifacts section
        artifacts_pattern = r'(##\s+Artifacts?\s+Created?\s*\n)'
        match = re.search(artifacts_pattern, content, re.IGNORECASE)

        if not match:
            # Add artifacts section if missing
            content += "\n\n## Artifacts Created\n\n"
            artifacts_pos = len(content)
        else:
            artifacts_pos = match.end()

        # Build enhanced artifacts list
        enhanced_artifacts = []
        for artifact_label, artifact_path in artifacts:
            if artifact_path.exists():
                evidence_link = self.create_evidence_link(
                    artifact_path, artifact_label)
                scope = self.infer_scope(artifact_path, artifact_path.read_text(
                    encoding='utf-8', errors='ignore')[:500])
                scope_tag = f"<!-- SSOT Domain: {scope} -->"
                enhanced_artifacts.append(f"- {evidence_link} {scope_tag}")
            else:
                enhanced_artifacts.append(
                    f"- `{artifact_path}` ⚠️ (file not found)")

        # Replace or add artifacts
        artifacts_section = "\n".join(enhanced_artifacts) + "\n"

        # Check if we need to replace existing artifacts list
        if match:
            # Find end of existing artifacts list
            next_section = re.search(
                r'\n##\s+', content[artifacts_pos:], re.IGNORECASE)
            if next_section:
                end_pos = artifacts_pos + next_section.start()
                existing_content = content[artifacts_pos:end_pos]
                # Replace numbered/bulleted list
                existing_content = re.sub(
                    r'^\d+\.\s+.*$|^-\s+.*$',
                    '',
                    existing_content,
                    flags=re.MULTILINE
                )
                content = content[:artifacts_pos] + \
                    artifacts_section + content[end_pos:]
            else:
                # Replace to end
                content = content[:artifacts_pos] + artifacts_section
        else:
            content += artifacts_section

        return content

    def add_scope_tags(self, content: str, inferred_scope: Optional[str] = None) -> str:
        """Add scope tags to report header."""
        # Find or add header
        if not content.startswith('<!--'):
            # Infer scope if not provided
            if not inferred_scope:
                # Try to infer from content
                if 'wordpress' in content.lower() or 'blog' in content.lower():
                    inferred_scope = 'web'
                elif 'architecture' in content.lower() or 'design' in content.lower():
                    inferred_scope = 'architecture'
                elif 'infrastructure' in content.lower():
                    inferred_scope = 'infrastructure'
                else:
                    inferred_scope = 'general'

            scope_tag = f"<!-- SSOT Domain: {inferred_scope} -->\n"
            content = scope_tag + content

        return content

    def extract_claims_from_content(self, content: str) -> List[str]:
        """Extract verifiable claims from report content."""
        claims = []

        # Pattern 1: "Created X" or "Generated X" statements
        created_pattern = r'[✅✅⏳❌]\s*(?:Created|Generated|Built|Implemented|Added|Fixed|Completed|Finished)\s+([^.\n]+)'
        matches = re.finditer(created_pattern, content, re.IGNORECASE)
        for match in matches:
            claim = match.group(1).strip()
            if len(claim) > 10 and len(claim) < 200:  # Reasonable claim length
                claims.append(f"Created/Generated: {claim}")

        # Pattern 2: Findings with "Found" or "Identified"
        found_pattern = r'(?:Found|Identified|Discovered|Detected)\s+([^.\n]+(?:issue|problem|bug|error|violation|duplicate|missing))'
        matches = re.finditer(found_pattern, content, re.IGNORECASE)
        for match in matches:
            claim = match.group(1).strip()
            if len(claim) > 10 and len(claim) < 200:
                claims.append(f"Found/Identified: {claim}")

        # Pattern 3: Status statements with numbers/metrics
        metric_pattern = r'(\d+[/\s]+(?:files|posts|sites|tests|violations|agents|lines|modules)[^.\n]*)'
        matches = re.finditer(metric_pattern, content, re.IGNORECASE)
        for match in matches:
            claim = match.group(1).strip()
            if claim not in [c.split(': ')[-1] for c in claims]:  # Avoid duplicates
                claims.append(f"Metric: {claim}")

        # Pattern 4: Tool/artifact mentions with paths
        tool_pattern = r'`([^`]+\.(?:py|md|json|yaml|yml))`'
        matches = re.finditer(tool_pattern, content)
        for match in matches:
            tool_path = match.group(1)
            if tool_path not in [c.split(': ')[-1] for c in claims]:
                claims.append(f"Tool/Artifact: {tool_path}")

        # Remove duplicates while preserving order
        seen = set()
        unique_claims = []
        for claim in claims:
            claim_key = claim.lower()
            if claim_key not in seen:
                seen.add(claim_key)
                unique_claims.append(claim)

        return unique_claims[:10]  # Limit to top 10 most relevant

    def add_verification_section(self, content: str, claims: Optional[List[str]] = None) -> str:
        """Add verification section with evidence for claims."""
        # Auto-extract claims if not provided
        if not claims:
            claims = self.extract_claims_from_content(content)

        # If still no claims, provide default guidance
        if not claims:
            claims = ["Report content requires manual claim verification"]

        verification_section = "\n\n## Verification & Evidence\n\n"
        verification_section += "**Claims Made in This Report:**\n\n"

        for i, claim in enumerate(claims, 1):
            verification_section += f"{i}. {claim}\n"

        verification_section += "\n**Evidence Links:**\n"
        verification_section += "- All artifacts linked above with commit hashes\n"
        verification_section += "- File paths are relative to repository root\n"
        verification_section += "- Line counts verified at report generation time\n"
        verification_section += "- Commit hashes provide git verification\n\n"
        verification_section += "**Verification Instructions:**\n"
        verification_section += "1. Check artifact links - files should exist at specified paths\n"
        verification_section += "2. Verify commit hashes using: `git log --oneline <file_path>`\n"
        verification_section += "3. Confirm line counts match reported values\n"
        verification_section += "4. Review scope tags for SSOT domain alignment\n"

        # Insert before final status section if it exists
        status_pattern = r'\n##\s+Status\s*\n'
        status_match = re.search(status_pattern, content, re.IGNORECASE)
        if status_match:
            content = content[:status_match.start(
            )] + verification_section + content[status_match.start():]
        else:
            content += verification_section

        return content

    def enhance_report(
        self,
        report_path: Path,
        artifacts: List[Tuple[str, Path]],
        scope: Optional[str] = None,
        claims: Optional[List[str]] = None,
        auto_extract_claims: bool = True
    ) -> str:
        """Enhance a report with truthfulness improvements."""
        if not report_path.exists():
            raise FileNotFoundError(f"Report not found: {report_path}")

        content = report_path.read_text(encoding='utf-8')

        # Add scope tags
        content = self.add_scope_tags(content, scope)

        # Enhance artifacts section
        content = self.enhance_artifacts_section(content, artifacts)

        # Add verification section (auto-extract claims if not provided and enabled)
        if auto_extract_claims and not claims:
            claims = self.extract_claims_from_content(content)

        if claims or auto_extract_claims:
            content = self.add_verification_section(content, claims)

        return content


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhance reports with scope tags and evidence links")
    parser.add_argument("report", help="Path to report file to enhance")
    parser.add_argument("--artifacts", nargs="+",
                        help="Artifact files (format: label:path)")
    parser.add_argument(
        "--scope", help="SSOT domain scope (e.g., web, infrastructure)")
    parser.add_argument("--claims", help="Claims file (JSON array of strings)")
    parser.add_argument("--no-auto-claims", action="store_true",
                        help="Disable automatic claim extraction")
    parser.add_argument(
        "--output", help="Output file (default: overwrite input)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show enhanced content without saving")

    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"❌ Report not found: {report_path}")
        return 1

    enhancer = ReportTruthfulnessEnhancer()

    # Parse artifacts
    artifacts = []
    if args.artifacts:
        for artifact_spec in args.artifacts:
            if ':' in artifact_spec:
                label, path = artifact_spec.split(':', 1)
                path_obj = Path(path.strip())
                # Resolve relative to repo root
                if not path_obj.is_absolute():
                    path_obj = (enhancer.repo_root / path_obj).resolve()
                artifacts.append((label.strip(), path_obj))
            else:
                path_obj = Path(artifact_spec.strip())
                # Resolve relative to repo root
                if not path_obj.is_absolute():
                    path_obj = (enhancer.repo_root / path_obj).resolve()
                artifacts.append((path_obj.name, path_obj))

    # Parse claims
    claims = None
    if args.claims:
        claims_path = Path(args.claims)
        if claims_path.exists():
            with open(claims_path, 'r', encoding='utf-8') as f:
                claims = json.load(f)
        else:
            print(f"⚠️  Claims file not found: {claims_path}")

    # Enhance report
    try:
        enhanced_content = enhancer.enhance_report(
            report_path,
            artifacts,
            scope=args.scope,
            claims=claims,
            auto_extract_claims=not args.no_auto_claims
        )

        if args.dry_run:
            print(enhanced_content)
        else:
            output_path = Path(args.output) if args.output else report_path
            output_path.write_text(enhanced_content, encoding='utf-8')
            print(f"✅ Enhanced report saved to: {output_path}")

        return 0
    except Exception as e:
        print(f"❌ Error enhancing report: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
