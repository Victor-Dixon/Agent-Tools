#!/usr/bin/env python3
"""
MCP Server for Dependency Management
Automates package maintenance: outdated checks, vulnerability audits, updates, and cleanup.
"""

import json
import os
import re
import subprocess
import sys
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
            timeout=300
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


def _detect_package_manager(cwd: str = ".") -> str:
    """Detect which package manager is in use."""
    path = Path(cwd)
    if (path / "package-lock.json").exists() or (path / "package.json").exists():
        if (path / "yarn.lock").exists():
            return "yarn"
        if (path / "pnpm-lock.yaml").exists():
            return "pnpm"
        return "npm"
    if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
        if (path / "Pipfile").exists():
            return "pipenv"
        if (path / "poetry.lock").exists():
            return "poetry"
        return "pip"
    if (path / "Cargo.toml").exists():
        return "cargo"
    if (path / "go.mod").exists():
        return "go"
    return "unknown"


def check_outdated(
    package_manager: Optional[str] = None,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Find outdated npm/pip/cargo packages.
    
    Args:
        package_manager: Override auto-detection (npm, pip, yarn, pnpm, cargo, poetry)
        cwd: Working directory
    """
    pm = package_manager or _detect_package_manager(cwd)
    
    if pm == "npm":
        result = _run_command(["npm", "outdated", "--json"], cwd)
        if result.get("stdout"):
            try:
                outdated = json.loads(result["stdout"])
                packages = []
                for name, info in outdated.items():
                    packages.append({
                        "name": name,
                        "current": info.get("current", "unknown"),
                        "wanted": info.get("wanted", "unknown"),
                        "latest": info.get("latest", "unknown"),
                        "type": info.get("type", "dependencies")
                    })
                return {
                    "success": True,
                    "package_manager": pm,
                    "outdated_count": len(packages),
                    "packages": packages
                }
            except json.JSONDecodeError:
                pass
        return {"success": True, "package_manager": pm, "outdated_count": 0, "packages": []}
    
    elif pm == "yarn":
        result = _run_command(["yarn", "outdated", "--json"], cwd)
        packages = []
        if result.get("stdout"):
            for line in result["stdout"].split("\n"):
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("type") == "table":
                            for row in data.get("data", {}).get("body", []):
                                if len(row) >= 4:
                                    packages.append({
                                        "name": row[0],
                                        "current": row[1],
                                        "wanted": row[2],
                                        "latest": row[3]
                                    })
                    except json.JSONDecodeError:
                        continue
        return {
            "success": True,
            "package_manager": pm,
            "outdated_count": len(packages),
            "packages": packages
        }
    
    elif pm == "pip":
        result = _run_command(["pip", "list", "--outdated", "--format=json"], cwd)
        if result.get("success") and result.get("stdout"):
            try:
                outdated = json.loads(result["stdout"])
                packages = [{
                    "name": p["name"],
                    "current": p["version"],
                    "latest": p["latest_version"],
                    "type": p.get("latest_filetype", "unknown")
                } for p in outdated]
                return {
                    "success": True,
                    "package_manager": pm,
                    "outdated_count": len(packages),
                    "packages": packages
                }
            except json.JSONDecodeError:
                pass
        return {"success": True, "package_manager": pm, "outdated_count": 0, "packages": []}
    
    elif pm == "cargo":
        result = _run_command(["cargo", "outdated", "--format", "json"], cwd)
        if result.get("success") and result.get("stdout"):
            try:
                data = json.loads(result["stdout"])
                packages = []
                for dep in data.get("dependencies", []):
                    packages.append({
                        "name": dep.get("name"),
                        "current": dep.get("project"),
                        "latest": dep.get("latest"),
                        "kind": dep.get("kind", "normal")
                    })
                return {
                    "success": True,
                    "package_manager": pm,
                    "outdated_count": len(packages),
                    "packages": packages
                }
            except json.JSONDecodeError:
                pass
        return {"success": True, "package_manager": pm, "outdated_count": 0, "packages": []}
    
    elif pm == "poetry":
        result = _run_command(["poetry", "show", "--outdated"], cwd)
        packages = []
        if result.get("stdout"):
            for line in result["stdout"].split("\n"):
                parts = line.split()
                if len(parts) >= 3:
                    packages.append({
                        "name": parts[0],
                        "current": parts[1],
                        "latest": parts[2]
                    })
        return {
            "success": True,
            "package_manager": pm,
            "outdated_count": len(packages),
            "packages": packages
        }
    
    return {"success": False, "error": f"Unsupported package manager: {pm}"}


def check_vulnerabilities(
    package_manager: Optional[str] = None,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Security audit for dependencies (npm audit, pip-audit, cargo audit).
    
    Args:
        package_manager: Override auto-detection
        cwd: Working directory
    """
    pm = package_manager or _detect_package_manager(cwd)
    
    if pm == "npm":
        result = _run_command(["npm", "audit", "--json"], cwd)
        if result.get("stdout"):
            try:
                audit = json.loads(result["stdout"])
                vulnerabilities = []
                advisories = audit.get("advisories", {}) or audit.get("vulnerabilities", {})
                
                for name, info in advisories.items():
                    if isinstance(info, dict):
                        vulnerabilities.append({
                            "name": name if not info.get("name") else info.get("name"),
                            "severity": info.get("severity", "unknown"),
                            "title": info.get("title", info.get("via", [{}])[0].get("title", "Unknown") if isinstance(info.get("via"), list) else "Unknown"),
                            "url": info.get("url", ""),
                            "range": info.get("range", info.get("vulnerable_versions", "")),
                            "fixAvailable": info.get("fixAvailable", False)
                        })
                
                metadata = audit.get("metadata", {})
                return {
                    "success": True,
                    "package_manager": pm,
                    "vulnerability_count": len(vulnerabilities),
                    "vulnerabilities": vulnerabilities,
                    "summary": {
                        "critical": metadata.get("vulnerabilities", {}).get("critical", 0),
                        "high": metadata.get("vulnerabilities", {}).get("high", 0),
                        "moderate": metadata.get("vulnerabilities", {}).get("moderate", 0),
                        "low": metadata.get("vulnerabilities", {}).get("low", 0),
                    }
                }
            except json.JSONDecodeError:
                pass
        return {
            "success": True,
            "package_manager": pm,
            "vulnerability_count": 0,
            "vulnerabilities": []
        }
    
    elif pm == "pip":
        # Try pip-audit first
        result = _run_command(["pip-audit", "--format", "json"], cwd)
        if result.get("success") and result.get("stdout"):
            try:
                vulns = json.loads(result["stdout"])
                vulnerabilities = [{
                    "name": v.get("name"),
                    "version": v.get("version"),
                    "id": v.get("vulns", [{}])[0].get("id", "") if v.get("vulns") else "",
                    "description": v.get("vulns", [{}])[0].get("description", "") if v.get("vulns") else "",
                    "fix_versions": v.get("vulns", [{}])[0].get("fix_versions", []) if v.get("vulns") else []
                } for v in vulns if v.get("vulns")]
                return {
                    "success": True,
                    "package_manager": pm,
                    "vulnerability_count": len(vulnerabilities),
                    "vulnerabilities": vulnerabilities
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback to safety
        result = _run_command(["safety", "check", "--json"], cwd)
        if result.get("stdout"):
            try:
                data = json.loads(result["stdout"])
                vulnerabilities = [{
                    "name": v[0],
                    "version": v[2],
                    "id": v[4],
                    "description": v[3]
                } for v in data.get("vulnerabilities", [])]
                return {
                    "success": True,
                    "package_manager": pm,
                    "vulnerability_count": len(vulnerabilities),
                    "vulnerabilities": vulnerabilities
                }
            except (json.JSONDecodeError, IndexError):
                pass
        
        return {"success": True, "package_manager": pm, "vulnerability_count": 0, "vulnerabilities": [], "note": "pip-audit or safety not installed"}
    
    elif pm == "cargo":
        result = _run_command(["cargo", "audit", "--json"], cwd)
        if result.get("stdout"):
            try:
                audit = json.loads(result["stdout"])
                vulnerabilities = [{
                    "name": v.get("package", {}).get("name"),
                    "version": v.get("package", {}).get("version"),
                    "id": v.get("advisory", {}).get("id"),
                    "title": v.get("advisory", {}).get("title"),
                    "severity": v.get("advisory", {}).get("severity"),
                    "url": v.get("advisory", {}).get("url")
                } for v in audit.get("vulnerabilities", {}).get("list", [])]
                return {
                    "success": True,
                    "package_manager": pm,
                    "vulnerability_count": len(vulnerabilities),
                    "vulnerabilities": vulnerabilities
                }
            except json.JSONDecodeError:
                pass
        return {"success": True, "package_manager": pm, "vulnerability_count": 0, "vulnerabilities": []}
    
    return {"success": False, "error": f"Unsupported package manager: {pm}"}


def update_package(
    package_name: str,
    version: Optional[str] = None,
    package_manager: Optional[str] = None,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Safely update a package with lockfile.
    
    Args:
        package_name: Name of the package to update
        version: Optional specific version (default: latest)
        package_manager: Override auto-detection
        cwd: Working directory
    """
    pm = package_manager or _detect_package_manager(cwd)
    
    if pm == "npm":
        pkg = f"{package_name}@{version}" if version else f"{package_name}@latest"
        result = _run_command(["npm", "install", pkg], cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "version": version or "latest",
                "message": f"Successfully updated {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Update failed")}
    
    elif pm == "yarn":
        pkg = f"{package_name}@{version}" if version else package_name
        result = _run_command(["yarn", "upgrade", pkg], cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "version": version or "latest",
                "message": f"Successfully updated {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Update failed")}
    
    elif pm == "pip":
        pkg = f"{package_name}=={version}" if version else package_name
        result = _run_command(["pip", "install", "--upgrade", pkg], cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "version": version or "latest",
                "message": f"Successfully updated {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Update failed")}
    
    elif pm == "poetry":
        if version:
            result = _run_command(["poetry", "add", f"{package_name}@{version}"], cwd)
        else:
            result = _run_command(["poetry", "update", package_name], cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "version": version or "latest",
                "message": f"Successfully updated {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Update failed")}
    
    elif pm == "cargo":
        result = _run_command(["cargo", "update", "-p", package_name], cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "message": f"Successfully updated {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Update failed")}
    
    return {"success": False, "error": f"Unsupported package manager: {pm}"}


def add_package(
    package_name: str,
    version: Optional[str] = None,
    dev: bool = False,
    package_manager: Optional[str] = None,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Add a package with latest version.
    
    Args:
        package_name: Name of the package to add
        version: Optional specific version (default: latest)
        dev: Install as dev dependency
        package_manager: Override auto-detection
        cwd: Working directory
    """
    pm = package_manager or _detect_package_manager(cwd)
    
    if pm == "npm":
        pkg = f"{package_name}@{version}" if version else package_name
        cmd = ["npm", "install", pkg]
        if dev:
            cmd.append("--save-dev")
        result = _run_command(cmd, cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "version": version or "latest",
                "dev": dev,
                "message": f"Successfully added {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Add failed")}
    
    elif pm == "yarn":
        pkg = f"{package_name}@{version}" if version else package_name
        cmd = ["yarn", "add", pkg]
        if dev:
            cmd.append("--dev")
        result = _run_command(cmd, cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "version": version or "latest",
                "dev": dev,
                "message": f"Successfully added {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Add failed")}
    
    elif pm == "pip":
        pkg = f"{package_name}=={version}" if version else package_name
        result = _run_command(["pip", "install", pkg], cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "version": version or "latest",
                "message": f"Successfully added {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Add failed")}
    
    elif pm == "poetry":
        pkg = f"{package_name}@{version}" if version else package_name
        cmd = ["poetry", "add", pkg]
        if dev:
            cmd.append("--dev")
        result = _run_command(cmd, cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "version": version or "latest",
                "dev": dev,
                "message": f"Successfully added {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Add failed")}
    
    elif pm == "cargo":
        if version:
            result = _run_command(["cargo", "add", package_name, "--vers", version], cwd)
        else:
            result = _run_command(["cargo", "add", package_name], cwd)
        if result.get("success"):
            return {
                "success": True,
                "package_manager": pm,
                "package": package_name,
                "message": f"Successfully added {package_name}"
            }
        return {"success": False, "error": result.get("stderr", "Add failed")}
    
    return {"success": False, "error": f"Unsupported package manager: {pm}"}


def remove_unused(
    package_manager: Optional[str] = None,
    cwd: str = ".",
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Find and optionally remove unused dependencies.
    
    Args:
        package_manager: Override auto-detection
        cwd: Working directory
        dry_run: If True, only list unused packages without removing
    """
    pm = package_manager or _detect_package_manager(cwd)
    
    if pm in ["npm", "yarn", "pnpm"]:
        # Use depcheck for npm/yarn
        result = _run_command(["npx", "depcheck", "--json"], cwd)
        if result.get("stdout"):
            try:
                data = json.loads(result["stdout"])
                unused = data.get("dependencies", [])
                unused_dev = data.get("devDependencies", [])
                missing = data.get("missing", {})
                
                if not dry_run and (unused or unused_dev):
                    for pkg in unused + unused_dev:
                        if pm == "npm":
                            _run_command(["npm", "uninstall", pkg], cwd)
                        elif pm == "yarn":
                            _run_command(["yarn", "remove", pkg], cwd)
                    
                return {
                    "success": True,
                    "package_manager": pm,
                    "dry_run": dry_run,
                    "unused_dependencies": unused,
                    "unused_dev_dependencies": unused_dev,
                    "missing_dependencies": list(missing.keys()),
                    "total_unused": len(unused) + len(unused_dev),
                    "action": "removed" if not dry_run else "listed"
                }
            except json.JSONDecodeError:
                pass
        return {"success": True, "package_manager": pm, "unused_dependencies": [], "note": "depcheck not available or no unused dependencies"}
    
    elif pm == "pip":
        # Use pip-autoremove or deptry
        result = _run_command(["pip", "freeze"], cwd)
        if result.get("success") and result.get("stdout"):
            installed = [line.split("==")[0].lower() for line in result["stdout"].split("\n") if "==" in line]
            
            # Check imports in Python files
            used_imports = set()
            for py_file in Path(cwd).rglob("*.py"):
                try:
                    content = py_file.read_text()
                    imports = re.findall(r'^(?:from|import)\s+(\w+)', content, re.MULTILINE)
                    used_imports.update(i.lower() for i in imports)
                except:
                    continue
            
            # Map package names to import names (simplified)
            potentially_unused = [pkg for pkg in installed if pkg not in used_imports]
            
            return {
                "success": True,
                "package_manager": pm,
                "dry_run": dry_run,
                "potentially_unused": potentially_unused[:20],  # Limit output
                "note": "This is a heuristic check. Some packages may use different import names.",
                "total_packages": len(installed),
                "action": "listed"
            }
        return {"success": True, "package_manager": pm, "potentially_unused": []}
    
    return {"success": False, "error": f"Unsupported package manager: {pm}"}


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
                            "check_outdated": {
                                "description": "Find outdated npm/pip/cargo packages",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "package_manager": {
                                            "type": "string",
                                            "enum": ["npm", "yarn", "pnpm", "pip", "poetry", "cargo"],
                                            "description": "Override auto-detection of package manager"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "check_vulnerabilities": {
                                "description": "Security audit for dependencies (npm audit, pip-audit, cargo audit)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "package_manager": {
                                            "type": "string",
                                            "enum": ["npm", "pip", "cargo"],
                                            "description": "Override auto-detection of package manager"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "update_package": {
                                "description": "Safely update a package with lockfile",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "package_name": {
                                            "type": "string",
                                            "description": "Name of the package to update"
                                        },
                                        "version": {
                                            "type": "string",
                                            "description": "Optional specific version (default: latest)"
                                        },
                                        "package_manager": {
                                            "type": "string",
                                            "description": "Override auto-detection"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    },
                                    "required": ["package_name"]
                                }
                            },
                            "add_package": {
                                "description": "Add a package with latest version",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "package_name": {
                                            "type": "string",
                                            "description": "Name of the package to add"
                                        },
                                        "version": {
                                            "type": "string",
                                            "description": "Optional specific version"
                                        },
                                        "dev": {
                                            "type": "boolean",
                                            "default": False,
                                            "description": "Install as dev dependency"
                                        },
                                        "package_manager": {
                                            "type": "string",
                                            "description": "Override auto-detection"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    },
                                    "required": ["package_name"]
                                }
                            },
                            "remove_unused": {
                                "description": "Find and remove unused dependencies",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "package_manager": {
                                            "type": "string",
                                            "description": "Override auto-detection"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        },
                                        "dry_run": {
                                            "type": "boolean",
                                            "default": True,
                                            "description": "If true, only list unused packages"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "serverInfo": {"name": "dependency-management-server", "version": "1.0.0"}
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

                if tool_name == "check_outdated":
                    result = check_outdated(**arguments)
                elif tool_name == "check_vulnerabilities":
                    result = check_vulnerabilities(**arguments)
                elif tool_name == "update_package":
                    result = update_package(**arguments)
                elif tool_name == "add_package":
                    result = add_package(**arguments)
                elif tool_name == "remove_unused":
                    result = remove_unused(**arguments)
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
