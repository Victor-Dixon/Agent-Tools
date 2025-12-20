#!/usr/bin/env python3
"""Verify dadudekc.com font fix deployment."""

from tools.wordpress_manager import WordPressManager
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


print("🔍 Verifying dadudekc.com font fix deployment...\n")

manager = WordPressManager("dadudekc.com")

if not manager.connect():
    print("❌ Failed to connect")
    sys.exit(1)

# Check if the PHP file exists
print("1. Checking if PHP fix file exists on server...")
stdout, stderr, code = manager.wp_cli(
    "eval \"echo file_exists(get_template_directory() . '/dadudekc_font_fix_css.php') ? 'EXISTS' : 'NOT_FOUND';\""
)
if "EXISTS" in stdout:
    print("   ✅ PHP fix file exists on server")
else:
    print("   ❌ PHP fix file NOT found on server")
    print(f"   Output: {stdout}")

# Check if functions.php includes it
print("\n2. Checking if functions.php includes the fix file...")
stdout, stderr, code = manager.wp_cli(
    "eval \"\\$func_path = get_template_directory() . '/functions.php'; "
    "\\$content = file_exists(\\$func_path) ? file_get_contents(\\$func_path) : ''; "
    "echo strpos(\\$content, 'dadudekc_font_fix_css') !== false ? 'FOUND' : 'NOT_FOUND';\""
)
if "FOUND" in stdout:
    print("   ✅ functions.php includes the fix file")
else:
    print("   ❌ functions.php does NOT include the fix file")
    print(f"   Output: {stdout}")

# Try to manually include and test
print("\n3. Testing if the function would load...")
stdout, stderr, code = manager.wp_cli(
    "eval \"\\$fix_path = get_template_directory() . '/dadudekc_font_fix_css.php'; "
    "if (file_exists(\\$fix_path)) { "
    "  require_once \\$fix_path; "
    "  echo function_exists('dadudekc_font_rendering_fix') ? 'FUNCTION_EXISTS' : 'FUNCTION_NOT_FOUND'; "
    "} else { "
    "  echo 'FILE_NOT_FOUND'; "
    "}\""
)
if "FUNCTION_EXISTS" in stdout:
    print("   ✅ Function can be loaded successfully")
else:
    print("   ❌ Function could not be loaded")
    print(f"   Output: {stdout}")
    if stderr:
        print(f"   Error: {stderr}")

# Flush cache again
print("\n4. Flushing cache...")
manager.purge_caches()
print("   ✅ Cache flushed")

manager.disconnect()

