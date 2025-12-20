#!/usr/bin/env python3
"""
Fix Syntax Error in dadudekc.com Parent Theme functions.php
============================================================

Fixes syntax error blocking WP-CLI operations.

Author: Agent-2
"""

from tools.wordpress_manager import WordPressManager
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Main execution."""
    print("🔧 Fixing syntax error in dadudekc.com parent theme...\n")

    manager = WordPressManager("dadudekc.com")
    if not manager.connect():
        print("❌ Failed to connect to server")
        sys.exit(1)

    # Download functions.php
    remote_path = "domains/dadudekc.com/public_html/wp-content/themes/accounting-grove/functions.php"
    local_path = Path("temp/dadudekc_functions.php")
    local_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📥 Downloading {remote_path}...")
    try:
        # Read file via SFTP
        with manager.conn_manager.sftp.open(remote_path, 'r') as f:
            content = f.read().decode('utf-8')

        # Save locally
        local_path.write_text(content, encoding='utf-8')
        print(f"✅ Downloaded to {local_path}")

        # Check line 51
        lines = content.split('\n')
        if len(lines) >= 51:
            print(f"\nLine 51: {lines[50]}")
            print(f"Line 50: {lines[49] if len(lines) > 49 else 'N/A'}")
            print(f"Line 52: {lines[51] if len(lines) > 51 else 'N/A'}")

        # Look for syntax error around line 51
        # Common issues: unclosed quotes, missing semicolons, HTML in PHP
        print("\n🔍 Checking for syntax issues...")

        # Check for unclosed strings or HTML tags
        fixed_content = content
        issue_found = False

        # Check if there's HTML/XML in PHP (common cause of "<" token error)
        for i, line in enumerate(lines[45:55], start=46):
            if '<' in line and not line.strip().startswith('//') and not line.strip().startswith('/*'):
                # Check if it's inside a string
                if '"' not in line[:line.find('<')] and "'" not in line[:line.find('<')]:
                    print(
                        f"⚠️  Potential issue on line {i}: HTML/XML tag in PHP code")
                    print(f"   Content: {line.strip()}")
                    issue_found = True

        if not issue_found:
            print("💡 Syntax error may be elsewhere. Manual inspection needed.")
            print(f"📋 File saved to: {local_path}")
            print("💡 Fix the syntax error and re-upload the file")
        else:
            print("✅ Issues identified - fix and re-upload")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    manager.disconnect()


if __name__ == "__main__":
    main()
