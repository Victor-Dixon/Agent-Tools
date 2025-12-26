#!/usr/bin/env python3
"""
Security Scanner Server - MCP server for proactive security checks.

Tools:
- scan_secrets: Find hardcoded secrets and API keys
- check_dependencies: CVE vulnerability scan
- audit_permissions: Check file permission issues
- check_env_exposure: Ensure .env files are not committed
- generate_security_report: Full security audit report
"""

import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# Secret patterns to detect
SECRET_PATTERNS = [
    # API Keys
    (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', "API Key"),
    (r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', "Secret Key"),
    
    # AWS
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
    (r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?', "AWS Secret Access Key"),
    
    # GitHub
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
    (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth Token"),
    (r'ghu_[a-zA-Z0-9]{36}', "GitHub User Token"),
    (r'ghs_[a-zA-Z0-9]{36}', "GitHub Server Token"),
    (r'ghr_[a-zA-Z0-9]{36}', "GitHub Refresh Token"),
    
    # Slack
    (r'xox[baprs]-[0-9a-zA-Z]{10,48}', "Slack Token"),
    
    # Stripe
    (r'sk_live_[0-9a-zA-Z]{24}', "Stripe Live Secret Key"),
    (r'rk_live_[0-9a-zA-Z]{24}', "Stripe Live Restricted Key"),
    
    # Private Keys
    (r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----', "Private Key"),
    
    # Database URLs
    (r'(?i)(postgres|mysql|mongodb)://[^:]+:[^@]+@[^\s"\']+', "Database Connection String"),
    
    # Generic Passwords
    (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']', "Password"),
    
    # JWT
    (r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', "JWT Token"),
    
    # Generic Bearer Token
    (r'(?i)bearer\s+[a-zA-Z0-9_\-.]+', "Bearer Token"),
]

# Files to exclude from secret scanning
EXCLUDED_EXTENSIONS = {'.lock', '.sum', '.map', '.min.js', '.min.css', '.svg', '.png', '.jpg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.eot'}
EXCLUDED_DIRS = {'node_modules', '.git', 'vendor', 'venv', '.venv', '__pycache__', 'dist', 'build', '.next', 'coverage'}


def scan_secrets(
    project_path: str = ".",
    exclude_patterns: list[str] | None = None,
    include_tests: bool = False,
    max_file_size_kb: int = 500
) -> dict[str, Any]:
    """Scan for hardcoded secrets and API keys in the codebase."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    findings = []
    files_scanned = 0
    files_skipped = 0
    
    exclude_patterns = exclude_patterns or []
    if not include_tests:
        exclude_patterns.extend(['**/test/**', '**/tests/**', '**/*_test.*', '**/*_spec.*'])
    
    for file_path in project_path.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in EXCLUDED_DIRS):
            files_skipped += 1
            continue
        
        # Skip excluded extensions
        if file_path.suffix.lower() in EXCLUDED_EXTENSIONS:
            files_skipped += 1
            continue
        
        # Skip large files
        try:
            if file_path.stat().st_size > max_file_size_kb * 1024:
                files_skipped += 1
                continue
        except OSError:
            continue
        
        # Check exclude patterns
        rel_path = str(file_path.relative_to(project_path))
        skip = False
        for pattern in exclude_patterns:
            if Path(rel_path).match(pattern):
                skip = True
                break
        if skip:
            files_skipped += 1
            continue
        
        # Scan file
        try:
            content = file_path.read_text(errors='ignore')
            files_scanned += 1
            
            for pattern, secret_type in SECRET_PATTERNS:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line = content.split('\n')[line_num - 1].strip()
                    
                    # Mask the actual secret
                    secret_value = match.group(0)
                    if len(secret_value) > 10:
                        masked = secret_value[:4] + '*' * (len(secret_value) - 8) + secret_value[-4:]
                    else:
                        masked = '*' * len(secret_value)
                    
                    findings.append({
                        "file": rel_path,
                        "line": line_num,
                        "type": secret_type,
                        "masked_value": masked,
                        "context": line[:100] if len(line) > 100 else line
                    })
                    
        except Exception:
            continue
    
    # Deduplicate findings
    unique_findings = []
    seen = set()
    for f in findings:
        key = (f["file"], f["line"], f["type"])
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)
    
    return {
        "success": True,
        "findings": unique_findings,
        "total_findings": len(unique_findings),
        "files_scanned": files_scanned,
        "files_skipped": files_skipped,
        "has_secrets": len(unique_findings) > 0
    }


def check_dependencies(
    project_path: str = ".",
    package_manager: str = "auto"
) -> dict[str, Any]:
    """Check dependencies for known vulnerabilities (CVE scan)."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    results = []
    
    # Auto-detect and run appropriate vulnerability scanners
    if package_manager == "auto" or package_manager == "npm":
        if (project_path / "package.json").exists():
            try:
                result = subprocess.run(
                    ["npm", "audit", "--json"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("vulnerabilities", {})
                    
                    npm_vulns = []
                    for name, vuln_info in vulnerabilities.items():
                        npm_vulns.append({
                            "package": name,
                            "severity": vuln_info.get("severity", "unknown"),
                            "via": vuln_info.get("via", [])[:3] if isinstance(vuln_info.get("via"), list) else [],
                            "fixAvailable": vuln_info.get("fixAvailable", False)
                        })
                    
                    results.append({
                        "scanner": "npm audit",
                        "vulnerabilities": npm_vulns[:50],  # Limit results
                        "summary": audit_data.get("metadata", {}).get("vulnerabilities", {}),
                        "total": len(vulnerabilities)
                    })
                except json.JSONDecodeError:
                    results.append({
                        "scanner": "npm audit",
                        "error": "Failed to parse npm audit output",
                        "raw": result.stderr[:500]
                    })
            except subprocess.TimeoutExpired:
                results.append({"scanner": "npm audit", "error": "Timeout"})
            except FileNotFoundError:
                results.append({"scanner": "npm audit", "error": "npm not found"})
    
    if package_manager == "auto" or package_manager == "pip":
        if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            # Try pip-audit first
            try:
                result = subprocess.run(
                    ["pip-audit", "--format=json"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0 or result.stdout:
                    try:
                        audit_data = json.loads(result.stdout)
                        pip_vulns = []
                        for vuln in audit_data:
                            pip_vulns.append({
                                "package": vuln.get("name"),
                                "version": vuln.get("version"),
                                "vulnerability_id": vuln.get("id"),
                                "description": vuln.get("description", "")[:200],
                                "fix_versions": vuln.get("fix_versions", [])
                            })
                        results.append({
                            "scanner": "pip-audit",
                            "vulnerabilities": pip_vulns[:50],
                            "total": len(pip_vulns)
                        })
                    except json.JSONDecodeError:
                        results.append({
                            "scanner": "pip-audit",
                            "error": "Failed to parse output",
                            "raw": result.stderr[:500]
                        })
            except FileNotFoundError:
                # Try safety as fallback
                try:
                    result = subprocess.run(
                        ["safety", "check", "--json"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    results.append({
                        "scanner": "safety",
                        "output": result.stdout[:2000]
                    })
                except FileNotFoundError:
                    results.append({
                        "scanner": "pip-audit/safety",
                        "error": "Neither pip-audit nor safety installed"
                    })
            except subprocess.TimeoutExpired:
                results.append({"scanner": "pip-audit", "error": "Timeout"})
    
    if package_manager == "auto" or package_manager == "cargo":
        if (project_path / "Cargo.toml").exists():
            try:
                result = subprocess.run(
                    ["cargo", "audit", "--json"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                try:
                    audit_data = json.loads(result.stdout)
                    vulns = audit_data.get("vulnerabilities", {}).get("list", [])
                    results.append({
                        "scanner": "cargo audit",
                        "vulnerabilities": vulns[:50],
                        "total": len(vulns)
                    })
                except json.JSONDecodeError:
                    results.append({
                        "scanner": "cargo audit",
                        "output": result.stdout[:2000]
                    })
            except FileNotFoundError:
                results.append({"scanner": "cargo audit", "error": "cargo-audit not installed"})
            except subprocess.TimeoutExpired:
                results.append({"scanner": "cargo audit", "error": "Timeout"})
    
    total_vulns = sum(r.get("total", 0) for r in results if "total" in r)
    
    return {
        "success": True,
        "results": results,
        "total_vulnerabilities": total_vulns,
        "has_vulnerabilities": total_vulns > 0
    }


def audit_permissions(
    project_path: str = ".",
    check_sensitive: bool = True
) -> dict[str, Any]:
    """Audit file permissions for security issues."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    issues = []
    files_checked = 0
    
    # Sensitive file patterns
    sensitive_patterns = [
        '.env*', '*.pem', '*.key', '*.crt', '*credentials*', '*secret*',
        'id_rsa*', 'id_dsa*', 'id_ecdsa*', 'id_ed25519*', '*.p12', '*.pfx'
    ]
    
    for file_path in project_path.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in EXCLUDED_DIRS):
            continue
        
        try:
            file_stat = file_path.stat()
            mode = file_stat.st_mode
            files_checked += 1
            
            rel_path = str(file_path.relative_to(project_path))
            
            # Check for world-readable sensitive files
            if check_sensitive:
                is_sensitive = any(file_path.match(p) for p in sensitive_patterns)
                if is_sensitive:
                    # Check if world-readable (others can read)
                    if mode & stat.S_IROTH:
                        issues.append({
                            "file": rel_path,
                            "issue": "Sensitive file is world-readable",
                            "severity": "high",
                            "current_mode": oct(mode)[-3:],
                            "recommended_mode": "600"
                        })
                    # Check if group-readable
                    elif mode & stat.S_IRGRP:
                        issues.append({
                            "file": rel_path,
                            "issue": "Sensitive file is group-readable",
                            "severity": "medium",
                            "current_mode": oct(mode)[-3:],
                            "recommended_mode": "600"
                        })
            
            # Check for world-writable files (security risk)
            if mode & stat.S_IWOTH:
                issues.append({
                    "file": rel_path,
                    "issue": "File is world-writable",
                    "severity": "high",
                    "current_mode": oct(mode)[-3:],
                    "recommended": "Remove world-write permission"
                })
            
            # Check for executable scripts that shouldn't be
            if file_path.suffix in {'.json', '.yaml', '.yml', '.txt', '.md', '.env'}:
                if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                    issues.append({
                        "file": rel_path,
                        "issue": "Non-script file has executable permission",
                        "severity": "low",
                        "current_mode": oct(mode)[-3:]
                    })
                    
        except OSError:
            continue
    
    return {
        "success": True,
        "issues": issues,
        "total_issues": len(issues),
        "files_checked": files_checked,
        "has_issues": len(issues) > 0,
        "by_severity": {
            "high": len([i for i in issues if i.get("severity") == "high"]),
            "medium": len([i for i in issues if i.get("severity") == "medium"]),
            "low": len([i for i in issues if i.get("severity") == "low"])
        }
    }


def check_env_exposure(
    project_path: str = "."
) -> dict[str, Any]:
    """Ensure .env files are not committed to version control."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    issues = []
    recommendations = []
    
    # Find all .env files
    env_files = list(project_path.rglob('.env*'))
    env_files = [f for f in env_files if f.is_file() and '.git' not in f.parts]
    
    # Check .gitignore
    gitignore_path = project_path / '.gitignore'
    gitignore_patterns = []
    
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        gitignore_patterns = [
            line.strip() for line in gitignore_content.split('\n')
            if line.strip() and not line.startswith('#')
        ]
    
    # Check if .env patterns are in .gitignore
    env_ignored = any(
        p in ['.env', '.env*', '.env.*', '*.env', '.env.local', '.env.*.local']
        for p in gitignore_patterns
    )
    
    if not env_ignored and env_files:
        issues.append({
            "type": "missing_gitignore",
            "message": ".env files are not ignored in .gitignore",
            "severity": "critical"
        })
        recommendations.append("Add '.env*' to your .gitignore file")
    
    # Check if any .env files are tracked by git
    if (project_path / '.git').exists():
        try:
            result = subprocess.run(
                ["git", "ls-files", "--cached"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            tracked_files = result.stdout.strip().split('\n')
            
            for env_file in env_files:
                rel_path = str(env_file.relative_to(project_path))
                if rel_path in tracked_files:
                    issues.append({
                        "type": "tracked_env_file",
                        "file": rel_path,
                        "message": f"{rel_path} is tracked by git",
                        "severity": "critical"
                    })
                    recommendations.append(f"Remove {rel_path} from git: git rm --cached {rel_path}")
        except:
            pass
    
    # Check for .env files with secrets
    for env_file in env_files:
        try:
            content = env_file.read_text()
            rel_path = str(env_file.relative_to(project_path))
            
            # Skip example/template files
            if any(x in rel_path for x in ['example', 'template', 'sample']):
                continue
            
            # Check for actual secrets (not placeholders)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '=' in line and not line.strip().startswith('#'):
                    key, _, value = line.partition('=')
                    value = value.strip().strip('"\'')
                    
                    # Check if value looks like a real secret
                    if value and not value.startswith('<') and not value.startswith('${'):
                        if len(value) > 10 and not value.lower() in ['true', 'false', 'null', 'none']:
                            # Check for common secret patterns
                            if any(x in key.upper() for x in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'CREDENTIAL']):
                                issues.append({
                                    "type": "potential_secret",
                                    "file": rel_path,
                                    "line": i + 1,
                                    "key": key.strip(),
                                    "severity": "high"
                                })
        except:
            continue
    
    return {
        "success": True,
        "env_files_found": [str(f.relative_to(project_path)) for f in env_files],
        "gitignore_has_env": env_ignored,
        "issues": issues,
        "total_issues": len(issues),
        "recommendations": recommendations,
        "is_safe": len([i for i in issues if i.get("severity") in ["critical", "high"]]) == 0
    }


def generate_security_report(
    project_path: str = ".",
    include_secrets_scan: bool = True,
    include_dependency_scan: bool = True,
    include_permissions_audit: bool = True,
    include_env_check: bool = True
) -> dict[str, Any]:
    """Generate a comprehensive security audit report."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    report = {
        "project": str(project_path),
        "scans": {},
        "summary": {
            "total_issues": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "recommendations": []
    }
    
    # Run all requested scans
    if include_secrets_scan:
        secrets_result = scan_secrets(str(project_path))
        report["scans"]["secrets"] = secrets_result
        if secrets_result.get("has_secrets"):
            report["summary"]["total_issues"] += secrets_result.get("total_findings", 0)
            report["summary"]["high"] += secrets_result.get("total_findings", 0)
            report["recommendations"].append("Remove hardcoded secrets and use environment variables")
    
    if include_dependency_scan:
        deps_result = check_dependencies(str(project_path))
        report["scans"]["dependencies"] = deps_result
        if deps_result.get("has_vulnerabilities"):
            report["summary"]["total_issues"] += deps_result.get("total_vulnerabilities", 0)
            report["recommendations"].append("Update vulnerable dependencies to patched versions")
    
    if include_permissions_audit:
        perms_result = audit_permissions(str(project_path))
        report["scans"]["permissions"] = perms_result
        if perms_result.get("has_issues"):
            report["summary"]["total_issues"] += perms_result.get("total_issues", 0)
            severity_counts = perms_result.get("by_severity", {})
            report["summary"]["high"] += severity_counts.get("high", 0)
            report["summary"]["medium"] += severity_counts.get("medium", 0)
            report["summary"]["low"] += severity_counts.get("low", 0)
            report["recommendations"].append("Fix file permissions for sensitive files")
    
    if include_env_check:
        env_result = check_env_exposure(str(project_path))
        report["scans"]["env_exposure"] = env_result
        if not env_result.get("is_safe"):
            critical_count = len([i for i in env_result.get("issues", []) if i.get("severity") == "critical"])
            high_count = len([i for i in env_result.get("issues", []) if i.get("severity") == "high"])
            report["summary"]["critical"] += critical_count
            report["summary"]["high"] += high_count
            report["summary"]["total_issues"] += env_result.get("total_issues", 0)
            report["recommendations"].extend(env_result.get("recommendations", []))
    
    # Calculate overall security score (0-100)
    total = report["summary"]["total_issues"]
    critical = report["summary"]["critical"]
    high = report["summary"]["high"]
    
    if critical > 0:
        score = max(0, 30 - critical * 10)
    elif high > 0:
        score = max(30, 70 - high * 5)
    elif total > 0:
        score = max(70, 95 - total)
    else:
        score = 100
    
    report["security_score"] = score
    report["success"] = True
    
    return report


# MCP Server Implementation
TOOLS = [
    {
        "name": "scan_secrets",
        "description": "Scan for hardcoded secrets and API keys in the codebase",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "exclude_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Glob patterns for files to exclude"
                },
                "include_tests": {
                    "type": "boolean",
                    "description": "Include test files in the scan",
                    "default": False
                },
                "max_file_size_kb": {
                    "type": "integer",
                    "description": "Maximum file size to scan in KB",
                    "default": 500
                }
            }
        }
    },
    {
        "name": "check_dependencies",
        "description": "Check dependencies for known CVE vulnerabilities",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "package_manager": {
                    "type": "string",
                    "description": "Package manager (auto, npm, pip, cargo)",
                    "default": "auto"
                }
            }
        }
    },
    {
        "name": "audit_permissions",
        "description": "Audit file permissions for security issues",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "check_sensitive": {
                    "type": "boolean",
                    "description": "Check permissions on sensitive files (keys, certs, etc.)",
                    "default": True
                }
            }
        }
    },
    {
        "name": "check_env_exposure",
        "description": "Ensure .env files are not exposed or committed to git",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                }
            }
        }
    },
    {
        "name": "generate_security_report",
        "description": "Generate a comprehensive security audit report",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "include_secrets_scan": {
                    "type": "boolean",
                    "description": "Include secrets scanning",
                    "default": True
                },
                "include_dependency_scan": {
                    "type": "boolean",
                    "description": "Include dependency vulnerability scan",
                    "default": True
                },
                "include_permissions_audit": {
                    "type": "boolean",
                    "description": "Include file permissions audit",
                    "default": True
                },
                "include_env_check": {
                    "type": "boolean",
                    "description": "Include .env exposure check",
                    "default": True
                }
            }
        }
    }
]


def handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Route tool calls to appropriate functions."""
    if name == "scan_secrets":
        return scan_secrets(**arguments)
    elif name == "check_dependencies":
        return check_dependencies(**arguments)
    elif name == "audit_permissions":
        return audit_permissions(**arguments)
    elif name == "check_env_exposure":
        return check_env_exposure(**arguments)
    elif name == "generate_security_report":
        return generate_security_report(**arguments)
    else:
        return {"error": f"Unknown tool: {name}"}


def main():
    """Main MCP server loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {
                            "name": "security-scanner-server",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": TOOLS}
                }
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                tool_args = request.get("params", {}).get("arguments", {})
                result = handle_tool_call(tool_name, tool_args)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                }
            elif method == "notifications/initialized":
                continue
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
            
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
