#!/usr/bin/env python3
"""
Fix GitHub PR Issues - Streamlined One-Command Solution
=======================================================

Automatically diagnoses and fixes common GitHub PR creation issues.

Usage:
    python tools/fix_github_prs.py
    python tools/fix_github_prs.py --repo Streamertools --head merge-MeTuber-20251124
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants


def clear_gh_token():
    """Clear GH_TOKEN environment variable."""
    cleared = False
    if "GH_TOKEN" in os.environ:
        del os.environ["GH_TOKEN"]
        cleared = True
    if "GITHUB_TOKEN" in os.environ:
        # Don't delete GITHUB_TOKEN - we need it for API calls
        # Just note that it exists
        pass
    if cleared:
        print("✅ Cleared GH_TOKEN environment variable")
    return cleared


def check_gh_auth():
    """Check GitHub CLI authentication status."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_QUICK
        )
        if result.returncode == 0 and "Logged in" in result.stdout:
            print("✅ GitHub CLI authenticated")
            return True
        else:
            print("❌ GitHub CLI not authenticated")
            return False
    except Exception:
        print("❌ GitHub CLI not available")
        return False


def check_github_token():
    """Check if GitHub token is available from .env file (not environment)."""
    # Read directly from .env file to ensure we use the file token, not env var
    env_file = project_root / ".env"
    token = None
    
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass
    
    # Fallback to SSOT utility if .env doesn't have it
    if not token:
        from src.core.utils.github_utils import get_github_token
        token = get_github_token(project_root)
    
    if token:
        # Verify token is not empty
        token = token.strip()
        if token:
            # Check if we got it from .env or env var
            env_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
            if env_token and env_token != token:
                print(f"⚠️  Using token from .env file (env var differs)")
            print(f"✅ GitHub token found ({len(token)} chars)")
            return token
        else:
            print("❌ GitHub token is empty")
            return None
    else:
        print("❌ GitHub token not found")
        return None


def authenticate_with_token(token):
    """Authenticate GitHub CLI using token non-interactively."""
    try:
        # Validate token
        token = token.strip()
        if not token:
            print("⚠️  Token is empty")
            return False
        
        # Debug: Show token source
        print(f"🔐 Using token from .env file ({len(token)} chars)")
        
        # Clear GITHUB_TOKEN and GH_TOKEN from environment during auth
        # (gh auth login --with-token fails if these are set)
        env = os.environ.copy()
        github_token_backup = env.pop("GITHUB_TOKEN", None)  # Remove but save for restore
        gh_token_backup = env.pop("GH_TOKEN", None)  # Remove but save for restore
        
        # Always use stdin method (more reliable than PowerShell echo)
        return authenticate_with_token_stdin(token, env, github_token_backup)
            
    except subprocess.TimeoutExpired:
        print("⚠️  Authentication timed out")
        return False
    except FileNotFoundError:
        print("⚠️  GitHub CLI (gh) not found - install from https://cli.github.com")
        return False
    except Exception as e:
        print(f"⚠️  Could not auto-authenticate: {e}")
        return False


def authenticate_with_token_stdin(token, env, github_token_backup):
    """Authenticate using stdin pipe (most reliable method)."""
    try:
        # Validate token format (GitHub tokens start with ghp_ or ghp_)
        if not (token.startswith("ghp_") or token.startswith("gho_") or token.startswith("ghu_")):
            print(f"⚠️  Token format unexpected (should start with ghp_, gho_, or ghu_)")
            print(f"   Token preview: {token[:10]}...")
        
        # Use subprocess with stdin to pipe token
        process = subprocess.Popen(
            ["gh", "auth", "login", "--with-token"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        
        # Ensure token ends with newline (required by gh auth login --with-token)
        # Also ensure no extra whitespace
        token_clean = token.strip() + "\n"
        stdout, stderr = process.communicate(input=token_clean, timeout=TimeoutConstants.HTTP_SHORT)
        
        # Restore GITHUB_TOKEN after auth (needed for API calls)
        if github_token_backup:
            os.environ["GITHUB_TOKEN"] = github_token_backup
        
        if process.returncode == 0:
            print("✅ Authenticated GitHub CLI with token from .env file")
            return True
        else:
            error_msg = stderr or stdout
            # Show full error for debugging
            print(f"⚠️  Authentication failed:")
            print(f"   Error: {error_msg[:200]}")
            if "no token found" in error_msg.lower():
                print(f"   Issue: Token not recognized by gh CLI")
                print(f"   Solution: Verify token is valid at https://github.com/settings/tokens")
            elif "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
                print(f"   Issue: Token is invalid or expired")
                print(f"   Solution: Generate new token at https://github.com/settings/tokens")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Authentication timed out")
        return False
    except Exception as e:
        print(f"⚠️  Stdin auth failed: {e}")
        return False


def main():
    """Main fix routine."""
    print("🔧 Fixing GitHub PR Issues...\n")
    
    # Step 1: Clear GH_TOKEN
    cleared = clear_gh_token()
    
    # Step 2: Check auth
    auth_ok = check_gh_auth()
    
    # Step 3: Check token
    token = check_github_token()
    
    print("\n" + "=" * 60)
    
    # Step 4: Auto-authenticate if token available but not authenticated
    if not auth_ok and token:
        print("\n🔐 Attempting auto-authentication with token from .env...")
        if authenticate_with_token(token):
            # Verify auth worked
            auth_ok = check_gh_auth()
            if auth_ok:
                print("\n✅ Auto-authentication successful! GitHub PR tools ready.\n")
                sys.exit(0)
    
    if not auth_ok:
        print("\n🚨 ACTION REQUIRED:")
        if token:
            print("   Token found but authentication failed. Try:")
            print("   Option 1: Verify token is valid: https://github.com/settings/tokens")
            print("   Option 2: Run manually: echo YOUR_TOKEN | gh auth login --with-token")
        else:
            print("   Option 1: Add GITHUB_TOKEN=your_token to .env file, then run this script again")
            print("   Option 2: Run manually: echo YOUR_TOKEN | gh auth login --with-token")
        print("   Option 3: Run: gh auth login (interactive)\n")
        sys.exit(1)
    elif not token:
        print("\n⚠️  GitHub token not found in .env file")
        print("   Add GITHUB_TOKEN=your_token to .env file")
        print("   Then run this script again for automatic authentication.\n")
        sys.exit(2)
    else:
        print("\n✅ All checks passed! GitHub PR tools should work.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

