#!/usr/bin/env python3
"""
MCP Server for Release Management
Automates versioning and releases: version bumping, changelogs, GitHub releases, and tags.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def _run_command(cmd: List[str], cwd: str = ".") -> Dict[str, Any]:
    """Run a command and return result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=120
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_current_version(cwd: str = ".") -> Optional[str]:
    """Get current version from package.json, pyproject.toml, or Cargo.toml."""
    path = Path(cwd)
    
    # Check package.json
    pkg_json = path / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text())
            return data.get("version")
        except:
            pass
    
    # Check pyproject.toml
    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        except:
            pass
    
    # Check Cargo.toml
    cargo = path / "Cargo.toml"
    if cargo.exists():
        try:
            content = cargo.read_text()
            match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
        except:
            pass
    
    # Try git describe
    result = _run_command(["git", "describe", "--tags", "--abbrev=0"], cwd)
    if result.get("success") and result.get("stdout"):
        tag = result["stdout"].strip()
        return tag.lstrip("v")
    
    return None


def _parse_version(version: str) -> tuple:
    """Parse semver string into tuple."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)(?:-(.+))?", version)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)), match.group(4))
    return (0, 0, 0, None)


def bump_version(
    bump_type: str = "patch",
    prerelease: Optional[str] = None,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Semantic versioning bump (major/minor/patch).
    
    Args:
        bump_type: Type of version bump (major, minor, patch)
        prerelease: Optional prerelease tag (alpha, beta, rc)
        cwd: Working directory
    """
    current = _get_current_version(cwd)
    if not current:
        return {"success": False, "error": "Could not determine current version"}
    
    major, minor, patch, _ = _parse_version(current)
    
    if bump_type == "major":
        new_version = f"{major + 1}.0.0"
    elif bump_type == "minor":
        new_version = f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        new_version = f"{major}.{minor}.{patch + 1}"
    else:
        return {"success": False, "error": f"Invalid bump type: {bump_type}"}
    
    if prerelease:
        new_version = f"{new_version}-{prerelease}"
    
    path = Path(cwd)
    files_updated = []
    
    # Update package.json
    pkg_json = path / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text())
            data["version"] = new_version
            pkg_json.write_text(json.dumps(data, indent=2) + "\n")
            files_updated.append("package.json")
        except:
            pass
    
    # Update pyproject.toml
    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            new_content = re.sub(
                r'(version\s*=\s*["\'])([^"\']+)(["\'])',
                f'\\g<1>{new_version}\\g<3>',
                content,
                count=1
            )
            pyproject.write_text(new_content)
            files_updated.append("pyproject.toml")
        except:
            pass
    
    # Update Cargo.toml
    cargo = path / "Cargo.toml"
    if cargo.exists():
        try:
            content = cargo.read_text()
            new_content = re.sub(
                r'(version\s*=\s*")([^"]+)(")',
                f'\\g<1>{new_version}\\g<3>',
                content,
                count=1
            )
            cargo.write_text(new_content)
            files_updated.append("Cargo.toml")
        except:
            pass
    
    return {
        "success": True,
        "previous_version": current,
        "new_version": new_version,
        "bump_type": bump_type,
        "prerelease": prerelease,
        "files_updated": files_updated
    }


def generate_changelog(
    from_tag: Optional[str] = None,
    to_tag: str = "HEAD",
    output_file: Optional[str] = None,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Auto-generate changelog from git commits.
    
    Args:
        from_tag: Starting tag/commit (default: last tag)
        to_tag: Ending tag/commit (default: HEAD)
        output_file: Optional file to write changelog
        cwd: Working directory
    """
    # Get from_tag if not specified
    if not from_tag:
        result = _run_command(["git", "describe", "--tags", "--abbrev=0"], cwd)
        if result.get("success") and result.get("stdout"):
            from_tag = result["stdout"].strip()
        else:
            from_tag = ""
    
    # Get commits
    range_spec = f"{from_tag}..{to_tag}" if from_tag else to_tag
    result = _run_command([
        "git", "log", range_spec,
        "--pretty=format:%H|%s|%an|%ai",
        "--no-merges"
    ], cwd)
    
    if not result.get("success"):
        return {"success": False, "error": f"Failed to get git log: {result.get('stderr', '')}"}
    
    # Parse commits and categorize
    categories = {
        "feat": {"title": "Features", "commits": []},
        "fix": {"title": "Bug Fixes", "commits": []},
        "docs": {"title": "Documentation", "commits": []},
        "style": {"title": "Styling", "commits": []},
        "refactor": {"title": "Code Refactoring", "commits": []},
        "perf": {"title": "Performance Improvements", "commits": []},
        "test": {"title": "Tests", "commits": []},
        "build": {"title": "Build System", "commits": []},
        "ci": {"title": "CI/CD", "commits": []},
        "chore": {"title": "Chores", "commits": []},
        "other": {"title": "Other Changes", "commits": []}
    }
    
    breaking_changes = []
    
    for line in result.get("stdout", "").split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 3)
        if len(parts) >= 2:
            commit_hash, subject = parts[0], parts[1]
            author = parts[2] if len(parts) > 2 else ""
            
            # Check for breaking changes
            if "BREAKING" in subject.upper() or "!" in subject.split(":")[0] if ":" in subject else False:
                breaking_changes.append({"hash": commit_hash[:8], "subject": subject})
            
            # Categorize by conventional commit prefix
            categorized = False
            for prefix in categories.keys():
                if subject.lower().startswith(f"{prefix}:") or subject.lower().startswith(f"{prefix}("):
                    categories[prefix]["commits"].append({
                        "hash": commit_hash[:8],
                        "subject": subject,
                        "author": author
                    })
                    categorized = True
                    break
            
            if not categorized:
                categories["other"]["commits"].append({
                    "hash": commit_hash[:8],
                    "subject": subject,
                    "author": author
                })
    
    # Generate markdown
    version = _get_current_version(cwd) or "Unreleased"
    date = datetime.now().strftime("%Y-%m-%d")
    
    changelog_md = f"# Changelog\n\n## [{version}] - {date}\n\n"
    
    if breaking_changes:
        changelog_md += "### ⚠ BREAKING CHANGES\n\n"
        for bc in breaking_changes:
            changelog_md += f"- {bc['subject']} ({bc['hash']})\n"
        changelog_md += "\n"
    
    for cat_key, cat_data in categories.items():
        if cat_data["commits"]:
            changelog_md += f"### {cat_data['title']}\n\n"
            for commit in cat_data["commits"]:
                changelog_md += f"- {commit['subject']} ({commit['hash']})\n"
            changelog_md += "\n"
    
    # Write to file if specified
    if output_file:
        try:
            output_path = Path(cwd) / output_file
            
            # Prepend to existing changelog
            existing = ""
            if output_path.exists():
                existing = output_path.read_text()
                # Remove existing header
                existing = re.sub(r'^# Changelog\s*\n*', '', existing)
            
            output_path.write_text(changelog_md + existing)
        except Exception as e:
            return {"success": False, "error": f"Failed to write changelog: {e}"}
    
    # Count commits per category
    commit_counts = {k: len(v["commits"]) for k, v in categories.items() if v["commits"]}
    
    return {
        "success": True,
        "version": version,
        "from_tag": from_tag or "initial",
        "to_tag": to_tag,
        "total_commits": sum(len(v["commits"]) for v in categories.values()),
        "commit_counts": commit_counts,
        "breaking_changes": len(breaking_changes),
        "changelog": changelog_md,
        "output_file": output_file
    }


def create_release(
    version: Optional[str] = None,
    title: Optional[str] = None,
    notes: Optional[str] = None,
    draft: bool = False,
    prerelease: bool = False,
    generate_notes: bool = True,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Create a GitHub release with notes.
    
    Args:
        version: Release version/tag (default: current version)
        title: Release title (default: version)
        notes: Release notes (default: auto-generated)
        draft: Create as draft release
        prerelease: Mark as prerelease
        generate_notes: Auto-generate release notes from commits
        cwd: Working directory
    """
    version = version or _get_current_version(cwd)
    if not version:
        return {"success": False, "error": "Could not determine version"}
    
    tag = f"v{version}" if not version.startswith("v") else version
    title = title or f"Release {version}"
    
    # Generate notes if not provided
    if not notes and generate_notes:
        changelog = generate_changelog(cwd=cwd)
        if changelog.get("success"):
            notes = changelog.get("changelog", "")
    
    # Build gh release create command
    cmd = ["gh", "release", "create", tag, "--title", title]
    
    if notes:
        cmd.extend(["--notes", notes])
    else:
        cmd.append("--generate-notes")
    
    if draft:
        cmd.append("--draft")
    if prerelease:
        cmd.append("--prerelease")
    
    result = _run_command(cmd, cwd)
    
    if result.get("success"):
        return {
            "success": True,
            "version": version,
            "tag": tag,
            "title": title,
            "draft": draft,
            "prerelease": prerelease,
            "url": result.get("stdout", "").strip(),
            "message": f"Successfully created release {version}"
        }
    
    return {"success": False, "error": result.get("stderr", "Release creation failed")}


def tag_version(
    version: Optional[str] = None,
    message: Optional[str] = None,
    push: bool = True,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Create and optionally push git tag.
    
    Args:
        version: Version to tag (default: current version)
        message: Tag message (default: "Release version")
        push: Push tag to remote
        cwd: Working directory
    """
    version = version or _get_current_version(cwd)
    if not version:
        return {"success": False, "error": "Could not determine version"}
    
    tag = f"v{version}" if not version.startswith("v") else version
    message = message or f"Release {version}"
    
    # Create annotated tag
    result = _run_command(["git", "tag", "-a", tag, "-m", message], cwd)
    
    if not result.get("success"):
        if "already exists" in result.get("stderr", ""):
            return {"success": False, "error": f"Tag {tag} already exists"}
        return {"success": False, "error": result.get("stderr", "Tag creation failed")}
    
    push_result = None
    if push:
        push_result = _run_command(["git", "push", "origin", tag], cwd)
        if not push_result.get("success"):
            return {
                "success": False,
                "error": f"Tag created but push failed: {push_result.get('stderr', '')}"
            }
    
    return {
        "success": True,
        "tag": tag,
        "version": version,
        "message": message,
        "pushed": push and push_result.get("success", False)
    }


def validate_release(
    version: Optional[str] = None,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Pre-release validation checks.
    
    Args:
        version: Version to validate (default: current version)
        cwd: Working directory
    """
    version = version or _get_current_version(cwd)
    checks = []
    warnings = []
    errors = []
    
    # Check version exists
    if version:
        checks.append({"name": "version_defined", "passed": True, "version": version})
    else:
        checks.append({"name": "version_defined", "passed": False})
        errors.append("No version found in project files")
    
    # Check git status
    status = _run_command(["git", "status", "--porcelain"], cwd)
    if status.get("success"):
        uncommitted = bool(status.get("stdout", "").strip())
        checks.append({"name": "clean_working_tree", "passed": not uncommitted})
        if uncommitted:
            warnings.append("Uncommitted changes in working tree")
    
    # Check if on main/master branch
    branch = _run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if branch.get("success"):
        current_branch = branch.get("stdout", "").strip()
        is_main = current_branch in ["main", "master", "release"]
        checks.append({"name": "on_release_branch", "passed": is_main, "branch": current_branch})
        if not is_main:
            warnings.append(f"Not on main/master branch (currently on {current_branch})")
    
    # Check if tag exists
    if version:
        tag = f"v{version}" if not version.startswith("v") else version
        tag_check = _run_command(["git", "tag", "-l", tag], cwd)
        tag_exists = bool(tag_check.get("stdout", "").strip())
        checks.append({"name": "tag_not_exists", "passed": not tag_exists, "tag": tag})
        if tag_exists:
            errors.append(f"Tag {tag} already exists")
    
    # Check for CHANGELOG
    changelog_exists = (Path(cwd) / "CHANGELOG.md").exists()
    checks.append({"name": "changelog_exists", "passed": changelog_exists})
    if not changelog_exists:
        warnings.append("No CHANGELOG.md file found")
    
    # Check tests pass (npm/python)
    path = Path(cwd)
    if (path / "package.json").exists():
        test_result = _run_command(["npm", "test"], cwd)
        tests_pass = test_result.get("success", False)
        checks.append({"name": "tests_pass", "passed": tests_pass})
        if not tests_pass:
            errors.append("npm tests failed")
    elif (path / "pyproject.toml").exists() or (path / "pytest.ini").exists():
        test_result = _run_command(["pytest", "--collect-only", "-q"], cwd)
        tests_pass = test_result.get("success", False)
        checks.append({"name": "tests_discoverable", "passed": tests_pass})
    
    # Check linting
    if (path / "package.json").exists():
        lint_result = _run_command(["npm", "run", "lint", "--if-present"], cwd)
        lint_pass = lint_result.get("success", False)
        checks.append({"name": "lint_pass", "passed": lint_pass})
    
    passed = len(errors) == 0
    
    return {
        "success": True,
        "version": version,
        "ready_for_release": passed,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "summary": {
            "passed": sum(1 for c in checks if c.get("passed")),
            "failed": sum(1 for c in checks if not c.get("passed")),
            "warnings": len(warnings),
            "errors": len(errors)
        }
    }


# MCP Server Protocol
def main():
    """MCP server main loop."""
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "bump_version": {
                                "description": "Semantic versioning bump (major/minor/patch)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "bump_type": {
                                            "type": "string",
                                            "enum": ["major", "minor", "patch"],
                                            "default": "patch",
                                            "description": "Type of version bump"
                                        },
                                        "prerelease": {
                                            "type": "string",
                                            "description": "Optional prerelease tag (alpha, beta, rc)"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "generate_changelog": {
                                "description": "Auto-generate changelog from git commits",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "from_tag": {
                                            "type": "string",
                                            "description": "Starting tag/commit (default: last tag)"
                                        },
                                        "to_tag": {
                                            "type": "string",
                                            "default": "HEAD",
                                            "description": "Ending tag/commit"
                                        },
                                        "output_file": {
                                            "type": "string",
                                            "description": "Optional file to write changelog (e.g., CHANGELOG.md)"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "create_release": {
                                "description": "Create a GitHub release with notes",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "version": {
                                            "type": "string",
                                            "description": "Release version/tag (default: current version)"
                                        },
                                        "title": {
                                            "type": "string",
                                            "description": "Release title"
                                        },
                                        "notes": {
                                            "type": "string",
                                            "description": "Release notes markdown"
                                        },
                                        "draft": {
                                            "type": "boolean",
                                            "default": False,
                                            "description": "Create as draft release"
                                        },
                                        "prerelease": {
                                            "type": "boolean",
                                            "default": False,
                                            "description": "Mark as prerelease"
                                        },
                                        "generate_notes": {
                                            "type": "boolean",
                                            "default": True,
                                            "description": "Auto-generate release notes"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "tag_version": {
                                "description": "Create and push git tags",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "version": {
                                            "type": "string",
                                            "description": "Version to tag (default: current version)"
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "Tag message"
                                        },
                                        "push": {
                                            "type": "boolean",
                                            "default": True,
                                            "description": "Push tag to remote"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "validate_release": {
                                "description": "Pre-release validation checks",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "version": {
                                            "type": "string",
                                            "description": "Version to validate"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "serverInfo": {"name": "release-management-server", "version": "1.0.0"}
                }
            }
        )
    )

    # Handle tool calls
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "bump_version":
                    result = bump_version(**arguments)
                elif tool_name == "generate_changelog":
                    result = generate_changelog(**arguments)
                elif tool_name == "create_release":
                    result = create_release(**arguments)
                elif tool_name == "tag_version":
                    result = tag_version(**arguments)
                elif tool_name == "validate_release":
                    result = validate_release(**arguments)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
                        }
                    )
                )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32603, "message": str(e)}
                    }
                )
            )


if __name__ == "__main__":
    main()
