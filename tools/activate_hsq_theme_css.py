#!/usr/bin/env python3
"""Activate Houston Sip Queen theme CSS by adding to functions.php."""

from tools.wordpress_manager import WordPressManager
import sys
from pathlib import Path
import tempfile

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


print("🎨 Activating Houston Sip Queen theme CSS in functions.php...\n")

manager = WordPressManager("houstonsipqueen.com")

if not manager.connect():
    print("❌ Failed to connect")
    sys.exit(1)

# Get remote functions.php path
remote_base = manager.config.get("remote_base", "")
if not remote_base:
    remote_base = "domains/houstonsipqueen.com/public_html/wp-content/themes/houstonsipqueen"
func_path = remote_base + "/functions.php"

print(f"Working with: {func_path}")

# Download functions.php
try:
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
        tmp_path = Path(tmp_file.name)

    try:
        manager.conn_manager.sftp.get(func_path, str(tmp_path))
        print("   ✅ Downloaded functions.php")
        content = tmp_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        # Create new file if it doesn't exist
        content = "<?php\n"
        print("   ℹ️  functions.php not found, creating new file")

    # Check if already included
    if 'hsq_theme_css.php' in content:
        print("   ℹ️  Theme CSS already included in functions.php")
        manager.disconnect()
        sys.exit(0)

    # Add require statement
    content = content.rstrip()
    content += "\n\n// Houston Sip Queen Luxury Theme CSS - Applied 2025-12-17\n"
    content += "require_once get_template_directory() . '/hsq_theme_css.php';\n"

    tmp_path.write_text(content, encoding='utf-8')

    # Upload back
    manager.conn_manager.sftp.put(str(tmp_path), func_path)
    print("   ✅ Updated functions.php with theme CSS include")

    tmp_path.unlink()

    print("\n✅ Theme CSS activated successfully!")
    print("   The CSS will now load automatically via wp_head hook")

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Flush cache
print("\n🔄 Flushing cache...")
manager.purge_caches()

manager.disconnect()
print("\n✅ Complete!")

