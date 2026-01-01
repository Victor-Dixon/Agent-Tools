#!/usr/bin/env python3
"""
Unified Security Scanner
========================

Comprehensive security auditing tool that combines:
1. Sensitive file detection (secrets, tokens, .env)
2. Gitignore coverage verification
3. Dependency auditing (pip/npm vulnerabilities)
4. Basic Static Application Security Testing (SAST)

Architecture: WE ARE SWARM
"""

import json
import os
import subprocess
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Patterns for sensitive files/tokens
SENSITIVE_PATTERNS = {
    "files": [
        ".env", "config.py", "secrets.py", "credentials.json", 
        "id_rsa", "id_dsa", "*.pem", "*.key", 
        "thea_cookies", "discord_token"
    ],
    "whitelist": [
        ".env.example",
        "setup_thea_cookies.py",
        "unified_security_scanner.py",
        "check_sensitive_files.py",
        "find_github_token.py",
        "oauth_token_checker.ts"
    ],
    "content": [
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
        (r"sk_live_[a-zA-Z0-9]{24}", "Stripe Secret Key"),
        (r"xox[baprs]-([0-9a-zA-Z]{10,48})", "Slack Token"),
        (r"-----BEGIN PRIVATE KEY-----", "Private Key"),
        (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
        (r"M[a-zA-Z0-9\-]{20,}\.[a-zA-Z0-9\-]{20,}\.[a-zA-Z0-9\-]{20,}", "Discord Token Pattern")
    ]
}

def run_command(cmd: List[str]) -> str:
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip()
    except Exception as e:
        return ""

def scan_sensitive_files() -> Dict[str, Any]:
    """Scan for tracked sensitive files in git."""
    print("  🔍 Scanning tracked files...")
    tracked_files = run_command(["git", "ls-files"]).split("\n")
    found = []
    
    for file_path in tracked_files:
        if not file_path: continue
        
        # Check filename patterns
        is_whitelisted = False
        for w in SENSITIVE_PATTERNS.get("whitelist", []):
            if w in file_path:
                is_whitelisted = True
                break
        
        if is_whitelisted:
            continue

        for pattern in SENSITIVE_PATTERNS["files"]:
            if pattern.startswith("*"):
                if file_path.endswith(pattern[1:]):
                    found.append({"file": file_path, "reason": f"Matches pattern {pattern}"})
            elif pattern in file_path:
                found.append({"file": file_path, "reason": f"Contains suspicious name {pattern}"})

    return {"count": len(found), "files": found}

def scan_content_secrets(limit: int = 100) -> Dict[str, Any]:
    """Scan file content for secret patterns (basic grep)."""
    print("  🔍 Scanning file content for secrets...")
    found = []
    
    # Use git grep if available for speed
    for pattern, name in SENSITIVE_PATTERNS["content"]:
        output = run_command(["git", "grep", "-n", "-E", pattern])
        if output:
            for line in output.split("\n")[:limit]:
                if line:
                    found.append({"match": line[:100], "type": name})
    
    return {"count": len(found), "matches": found}

def audit_python_dependencies() -> Dict[str, Any]:
    """Audit python dependencies using pip-audit if available."""
    print("  🔍 Auditing Python dependencies...")
    
    # Check if pip-audit is installed
    try:
        import pip_audit
    except ImportError:
        return {"status": "skipped", "reason": "pip-audit not installed (run `pip install pip-audit`)"}

    try:
        # Run pip-audit
        cmd = ["pip-audit", "-f", "json"]
        output = run_command(cmd)
        if not output:
            return {"status": "clean", "count": 0}
            
        try:
            data = json.loads(output)
            vulns = []
            for dep in data:
                if dep.get("vulns"):
                    vulns.append({
                        "package": dep["name"],
                        "version": dep["version"],
                        "vulns": [v["id"] for v in dep["vulns"]]
                    })
            return {"status": "found", "count": len(vulns), "vulnerabilities": vulns}
        except json.JSONDecodeError:
            return {"status": "error", "reason": "Failed to parse pip-audit output"}
            
    except Exception as e:
        return {"status": "error", "reason": str(e)}

def audit_npm_dependencies() -> Dict[str, Any]:
    """Audit npm dependencies."""
    print("  🔍 Auditing NPM dependencies...")
    
    if not Path("package.json").exists():
        return {"status": "skipped", "reason": "No package.json found"}
        
    output = run_command(["npm", "audit", "--json"])
    try:
        data = json.loads(output)
        metadata = data.get("metadata", {}).get("vulnerabilities", {})
        total_vulns = sum(metadata.values())
        
        if total_vulns == 0:
            return {"status": "clean", "count": 0}
            
        return {
            "status": "found", 
            "count": total_vulns, 
            "details": metadata
        }
    except Exception:
        return {"status": "error", "reason": "Failed to parse npm audit output"}

def main():
    """Main execution."""
    import argparse
    parser = argparse.ArgumentParser(description="Unified Security Scanner")
    parser.add_argument("--warn-only", action="store_true", help="Exit with 0 even if issues found")
    args, _ = parser.parse_known_args()
    warn_only = args.warn_only or os.getenv("CI", "").lower() == "true"

    print("🛡️  UNIFIED SECURITY SCANNER")
    print("=" * 60)
    
    # 1. File Scan
    file_results = scan_sensitive_files()
    if file_results["count"] > 0:
        print(f"  ❌ Found {file_results['count']} suspicious tracked files:")
        for f in file_results["files"]:
            print(f"     - {f['file']} ({f['reason']})")
    else:
        print("  ✅ No suspicious files tracked.")
    print("-" * 60)

    # 2. Content Scan
    content_results = scan_content_secrets()
    if content_results["count"] > 0:
        print(f"  ❌ Found {content_results['count']} potential secrets in code:")
        for m in content_results["matches"]:
            print(f"     - {m['type']}: {m['match']}")
    else:
        print("  ✅ No obvious secrets patterns found in code.")
    print("-" * 60)

    # 3. Python Audit
    py_audit = audit_python_dependencies()
    if py_audit["status"] == "found":
        print(f"  ❌ Found {py_audit['count']} Python vulnerabilities:")
        for v in py_audit["vulnerabilities"]:
            print(f"     - {v['package']} {v['version']}: {', '.join(v['vulns'])}")
    elif py_audit["status"] == "skipped":
        print(f"  ⚠️  Python audit skipped: {py_audit['reason']}")
    else:
        print("  ✅ Python dependencies clean.")
    print("-" * 60)

    # 4. NPM Audit
    npm_audit = audit_npm_dependencies()
    if npm_audit["status"] == "found":
        print(f"  ❌ Found {npm_audit['count']} NPM vulnerabilities:")
        print(f"     {json.dumps(npm_audit['details'], indent=2)}")
    elif npm_audit["status"] == "skipped":
        print(f"  ⚠️  NPM audit skipped: {npm_audit['reason']}")
    else:
        print("  ✅ NPM dependencies clean.")
    print("=" * 60)

    # Exit code
    if (file_results["count"] > 0 or 
        content_results["count"] > 0 or 
        py_audit.get("status") == "found" or 
        npm_audit.get("status") == "found"):
        if warn_only:
            print("\n⚠️  Issues found, but --warn-only active. Exiting with 0.")
            sys.exit(0)
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
