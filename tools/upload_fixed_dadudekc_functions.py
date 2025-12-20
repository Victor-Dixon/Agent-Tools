#!/usr/bin/env python3
"""Upload fixed functions.php"""
from pathlib import Path
from tools.wordpress_manager import WordPressManager

m = WordPressManager("dadudekc.com")
m.connect()
m.deploy_file(Path("temp/dadudekc_functions.php"),
              "domains/dadudekc.com/public_html/wp-content/themes/accounting-grove/functions.php")
m.purge_caches()
m.disconnect()
print("✅ Fixed and uploaded")
