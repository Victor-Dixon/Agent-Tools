#!/usr/bin/env python3
"""
Unified Environment Manager
===========================

DevOps utility for:
1. Environment verification (dependencies, versions)
2. Configuration checks (.env, paths)
3. Infrastructure status (Docker, Services)

Architecture: WE ARE SWARM
"""

import sys
import os
import shutil
import subprocess
import json
from pathlib import Path

REQUIRED_TOOLS = {
    "git": "git --version",
    "python3": "python3 --version",
    "pip": "pip --version",
    "docker": "docker --version",
    "npm": "npm --version",
    "node": "node --version"
}

REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    # Add other critical vars here
]

def check_tools():
    """Check availability of required tools."""
    results = {}
    for tool, cmd in REQUIRED_TOOLS.items():
        if shutil.which(tool):
            try:
                ver = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT).decode().strip()
                results[tool] = {"status": "installed", "version": ver}
            except:
                results[tool] = {"status": "error", "version": "unknown"}
        else:
            results[tool] = {"status": "missing", "version": None}
    return results

def check_env_vars():
    """Check for required environment variables."""
    # Try to load .env if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    results = {}
    for var in REQUIRED_ENV_VARS:
        results[var] = "set" if os.getenv(var) else "missing"
    return results

def check_docker_status():
    """Check if docker daemon is running."""
    if not shutil.which("docker"):
        return "missing"
    try:
        subprocess.check_call(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "running"
    except subprocess.CalledProcessError:
        return "stopped"

def main():
    print("🌍 UNIFIED ENVIRONMENT CHECK")
    print("=" * 60)
    
    # Tools
    print("\n🛠️  Tools:")
    tools = check_tools()
    for tool, info in tools.items():
        icon = "✅" if info["status"] == "installed" else "❌"
        ver = f"({info['version']})" if info['version'] else ""
        print(f"  {icon} {tool:<10} {info['status'].upper()} {ver}")

    # Env Vars
    print("\n🔑 Environment Variables:")
    envs = check_env_vars()
    for var, status in envs.items():
        icon = "✅" if status == "set" else "❌"
        print(f"  {icon} {var:<20} {status.upper()}")

    # Docker
    print("\n🐳 Infrastructure:")
    docker_stat = check_docker_status()
    d_icon = "✅" if docker_stat == "running" else "❌"
    print(f"  {d_icon} Docker Daemon      {docker_stat.upper()}")

    # Summary
    print("\n" + "=" * 60)
    
    # Fail if critical missing
    if tools["python3"]["status"] != "installed" or tools["git"]["status"] != "installed":
        print("❌ CRITICAL: Basic development tools missing.")
        sys.exit(1)
        
    sys.exit(0)

if __name__ == "__main__":
    main()
