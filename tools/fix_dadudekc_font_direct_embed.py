#!/usr/bin/env python3
"""Fix dadudekc.com font issue by embedding CSS directly in functions.php."""

from tools.wordpress_manager import WordPressManager
import sys
from pathlib import Path
import tempfile

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


print("🔧 Fixing font rendering by embedding CSS directly in functions.php...\n")

# The CSS fix code
css_fix_code = """/* Font Rendering Fix - Applied 2025-12-17 */
body, body *, .wp-block-post-content, .wp-block-post-excerpt, .wp-block-group, .wp-block-cover,
h1, h2, h3, h4, h5, h6, p, span, div, a, li, td, th {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol" !important;
}
.wp-block-heading, h1.wp-block-heading, h2.wp-block-heading, h3.wp-block-heading, h4.wp-block-heading, h5.wp-block-heading, h6.wp-block-heading {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}
.wp-block-site-title, .wp-block-site-title a, .wp-block-navigation-item, .wp-block-navigation-item__content {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}
footer, footer * {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}
* {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}"""

# PHP function to add CSS
php_function = f"""function dadudekc_font_rendering_fix() {{
    ?>
    <style id="dadudekc-font-fix">
    {css_fix_code}
    </style>
    <?php
}}
add_action('wp_head', 'dadudekc_font_rendering_fix', 999);
"""

manager = WordPressManager("dadudekc.com")

if not manager.connect():
    print("❌ Failed to connect")
    sys.exit(1)

# Get functions.php path
remote_base = manager.config.get("remote_base", "")
if "accounting-grove-dark" in remote_base:
    func_path = remote_base + "/functions.php"
elif "accounting-grove" in remote_base:
    func_path = remote_base + "/functions.php"
else:
    func_path = "domains/dadudekc.com/public_html/wp-content/themes/accounting-grove-dark/functions.php"

print(f"Working with: {func_path}")

# Download functions.php
try:
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.php', encoding='utf-8') as tmp_file:
        tmp_path = Path(tmp_file.name)

    manager.conn_manager.sftp.get(func_path, str(tmp_path))
    print("   ✅ Downloaded functions.php")

    content = tmp_path.read_text(encoding='utf-8')

    # Remove any existing font fix code
    lines = content.split('\n')
    cleaned_lines = []
    skip_section = False

    for line in lines:
        if 'dadudekc_font_rendering_fix' in line or ('Font Rendering Fix' in line and '2025-12-17' in line):
            skip_section = True
            continue
        if skip_section:
            if line.strip() == '' and 'add_action' not in '\n'.join(cleaned_lines[-5:]):
                skip_section = False
                continue
            if 'add_action' in line and 'dadudekc_font_rendering_fix' in line:
                skip_section = False
                continue
            continue
        cleaned_lines.append(line)

    cleaned_content = '\n'.join(cleaned_lines).rstrip()

    # Add the new function
    cleaned_content += "\n\n// Font Rendering Fix - Applied 2025-12-17\n"
    cleaned_content += php_function

    tmp_path.write_text(cleaned_content, encoding='utf-8')

    # Upload back
    manager.conn_manager.sftp.put(str(tmp_path), func_path)
    print("   ✅ Uploaded fixed functions.php with embedded CSS")

    tmp_path.unlink()

    print("\n✅ Font fix embedded successfully!")
    print("   The CSS will be injected via wp_head hook")

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

