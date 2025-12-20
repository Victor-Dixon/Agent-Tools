#!/usr/bin/env python3
"""Remove duplicate content from repo_safe_merge_v2.py"""

from pathlib import Path

file_path = Path("tools/repo_safe_merge_v2.py")
content = file_path.read_text(encoding='utf-8')

# Find the first complete main() block
first_main_pattern = 'if __name__ == "__main__":\n    main()\n'
first_main_end = content.find(first_main_pattern)

if first_main_end > 0:
    # Keep everything up to and including the first main()
    new_content = content[:first_main_end + len(first_main_pattern)]
    
    # Write back
    file_path.write_text(new_content, encoding='utf-8')
    print(f"✅ Removed duplicate: {len(content)} → {len(new_content)} bytes")
    print(f"   Removed {len(content) - len(new_content)} bytes")
    print(f"   Lines: {content.count(chr(10))} → {new_content.count(chr(10))}")
else:
    print("⚠️ Could not find duplicate pattern")


