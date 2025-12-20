#!/usr/bin/env python3
"""Fix syntax error in dadudekc.com functions.php."""

from tools.wordpress_manager import WordPressManager
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


print("🔧 Fixing syntax error in functions.php...\n")

manager = WordPressManager("dadudekc.com")

if not manager.connect():
    print("❌ Failed to connect")
    sys.exit(1)

# First, let's see what's on line 51
print("1. Checking functions.php content around line 51...")
stdout, stderr, code = manager.wp_cli(
    "eval \"\\$func_path = get_template_directory() . '/functions.php'; "
    "if (file_exists(\\$func_path)) { "
    "  \\$lines = file(\\$func_path); "
    "  \\$start = max(0, 45); "
    "  \\$end = min(count(\\$lines), 55); "
    "  for (\\$i = \\$start; \\$i < \\$end; \\$i++) { "
    "    echo (\\$i+1) . ': ' . \\$lines[\\$i]; "
    "  } "
    "} else { "
    "  echo 'FILE_NOT_FOUND'; "
    "}\""
)
print("Lines 46-55:")
print(stdout)

# Now let's remove any problematic lines and add the require correctly
print("\n2. Fixing functions.php by removing problematic lines...")
stdout, stderr, code = manager.wp_cli(
    "eval \"\\$func_path = get_template_directory() . '/functions.php'; "
    "if (file_exists(\\$func_path)) { "
    "  \\$content = file_get_contents(\\$func_path); "
    "  // Remove any lines that contain 'dadudekc_font_fix_css' that might be malformed "
    "  \\$lines = explode(PHP_EOL, \\$content); "
    "  \\$new_lines = []; "
    "  foreach (\\$lines as \\$line) { "
    "    // Keep lines that don't contain our malformed addition "
    "    if (strpos(\\$line, 'dadudekc_font_fix_css') === false || "
    "        (strpos(\\$line, 'require_once') !== false && strpos(\\$line, 'dadudekc_font_fix_css') !== false)) { "
    "      \\$new_lines[] = \\$line; "
    "    } "
    "  } "
    "  \\$clean_content = implode(PHP_EOL, \\$new_lines); "
    "  // Add the correct require statement at the end if it doesn't exist "
    "  if (strpos(\\$clean_content, 'dadudekc_font_fix_css') === false) { "
    "    \\$clean_content = rtrim(\\$clean_content) . PHP_EOL . PHP_EOL . "
    "      '// Font Rendering Fix - Applied 2025-12-17' . PHP_EOL . "
    "      'require_once get_template_directory() . \\'/dadudekc_font_fix_css.php\\';' . PHP_EOL; "
    "  } "
    "  file_put_contents(\\$func_path, \\$clean_content); "
    "  echo 'FIXED'; "
    "} else { "
    "  echo 'FILE_NOT_FOUND'; "
    "}\""
)

if "FIXED" in stdout:
    print("   ✅ functions.php fixed!")
else:
    print("   ❌ Could not fix automatically")
    print(f"   Output: {stdout}")
    if stderr:
        print(f"   Error: {stderr}")

# Verify the syntax is now correct
print("\n3. Verifying PHP syntax...")
stdout, stderr, code = manager.wp_cli(
    "eval \"\\$func_path = get_template_directory() . '/functions.php'; "
    "if (file_exists(\\$func_path)) { "
    "  \\$output = []; "
    "  \\$return = 0; "
    "  exec('php -l ' . escapeshellarg(\\$func_path) . ' 2>&1', \\$output, \\$return); "
    "  echo implode(PHP_EOL, \\$output); "
    "} else { "
    "  echo 'FILE_NOT_FOUND'; "
    "}\""
)
print("PHP syntax check:")
print(stdout)

# Deploy the PHP fix file again to make sure it's there
print("\n4. Deploying PHP fix file...")
php_fix_path = project_root / "tools" / "dadudekc_font_fix_css.php"
if php_fix_path.exists():
    success = manager.deploy_file(
        php_fix_path, remote_path="dadudekc_font_fix_css.php", auto_flush_cache=False)
    if success:
        print("   ✅ PHP fix file deployed")
    else:
        print("   ❌ Failed to deploy PHP fix file")
else:
    print("   ❌ PHP fix file not found locally")

# Flush cache
print("\n5. Flushing cache...")
manager.purge_caches()

manager.disconnect()
print("\n✅ Fix attempt complete!")

