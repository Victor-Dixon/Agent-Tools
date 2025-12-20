#!/usr/bin/env python3
"""Fix functions.php syntax error via SFTP."""

from tools.wordpress_manager import WordPressManager
import sys
from pathlib import Path
import tempfile

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


print("🔧 Fixing functions.php syntax error via SFTP...\n")

manager = WordPressManager("dadudekc.com")

if not manager.connect():
    print("❌ Failed to connect")
    sys.exit(1)

# Get the remote path - functions.php is in the theme directory
remote_base = manager.config.get("remote_base", "")
if not remote_base:
    # Fallback: construct from site key
    remote_base = "domains/dadudekc.com/public_html/wp-content/themes/accounting-grove-dark"

# The functions.php is in the theme directory (same as remote_base)
# Try both theme names
for theme_name in ["accounting-grove-dark", "accounting-grove"]:
    # Construct path: replace theme name in remote_base
    if "accounting-grove-dark" in remote_base:
        func_path = remote_base.replace(
            "accounting-grove-dark", theme_name) + "/functions.php"
    elif "accounting-grove" in remote_base:
        func_path = remote_base.replace(
            "accounting-grove", theme_name) + "/functions.php"
    else:
        # Construct from scratch
        base_dir = remote_base.rsplit(
            "/", 1)[0] if "/" in remote_base else "domains/dadudekc.com/public_html/wp-content/themes"
        func_path = f"{base_dir}/{theme_name}/functions.php"

    print(f"Trying: {func_path}")

    # Download the file
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
            tmp_path = Path(tmp_file.name)

        # Download via SFTP
        try:
            manager.conn_manager.sftp.get(func_path, str(tmp_path))
            print(f"   ✅ Downloaded functions.php")
        except FileNotFoundError:
            print(f"   ⚠️  File not found at this path, trying next...")
            continue

        # Read and fix the file
        content = tmp_path.read_text(encoding='utf-8')

        # Remove any old font fix code and replace with new safe version
        lines = content.split('\n')
        cleaned_lines = []
        in_font_fix_section = False
        skip_until_newline = False

        for i, line in enumerate(lines):
            # Detect start of font fix section
            if 'dadudekc_font_fix_css' in line or ('Font Rendering Fix' in line and i > 40):
                if not in_font_fix_section:
                    in_font_fix_section = True
                    skip_until_newline = True
                    # Skip this line and all subsequent lines until we're out of the section
                continue

            # Skip lines that are part of the old font fix section
            if in_font_fix_section:
                # If we hit a blank line and the next non-blank line doesn't look like part of our fix, we're done
                if line.strip() == '':
                    # Check if next non-blank line is our code
                    found_next = False
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip() and ('dadudekc_font_fix_css' in lines[j] or 'Font Rendering Fix' in lines[j]):
                            found_next = True
                            break
                    if not found_next:
                        in_font_fix_section = False
                        skip_until_newline = False
                continue

            cleaned_lines.append(line)

        cleaned_content = '\n'.join(cleaned_lines)

        # Remove trailing whitespace and add correct require
        cleaned_content = cleaned_content.rstrip()

        # Add the correct require statement (always replace old one)
        if True:  # Always add the safe version
            cleaned_content += "\n\n// Font Rendering Fix - Applied 2025-12-17\n"
            # Use get_stylesheet_directory() for child themes, with fallback
            font_fix_code = """$font_fix_path = get_stylesheet_directory() . '/dadudekc_font_fix_css.php';
if (!file_exists($font_fix_path)) {
    $font_fix_path = get_template_directory() . '/dadudekc_font_fix_css.php';
}
if (file_exists($font_fix_path)) {
    require_once $font_fix_path;
}
"""
            cleaned_content += font_fix_code
            print("   ✅ Added correct require statement with fallback")
        else:
            print("   ℹ️  Require statement already exists (checking if valid)...")

        # Write the fixed content
        tmp_path.write_text(cleaned_content, encoding='utf-8')

        # Upload back
        manager.conn_manager.sftp.put(str(tmp_path), func_path)
        print(f"   ✅ Uploaded fixed functions.php")

        # Clean up
        tmp_path.unlink()

        print(f"\n✅ Successfully fixed functions.php for theme: {theme_name}")
        break

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        continue

# Flush cache
print("\n🔄 Flushing cache...")
manager.purge_caches()

manager.disconnect()
print("\n✅ Fix complete!")

