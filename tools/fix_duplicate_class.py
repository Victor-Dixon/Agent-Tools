#!/usr/bin/env python3
"""Fix duplicate SafeRepoMergeV2 class in repo_safe_merge_v2.py"""

from pathlib import Path

file_path = Path("tools/repo_safe_merge_v2.py")
content = file_path.read_text(encoding='utf-8')

# Find the first complete file ending (after first main())
first_main_end = content.find('if __name__ == "__main__":\n    main()\n\n')

if first_main_end > 0:
    # Keep everything up to and including the first main()
    new_content = content[:first_main_end + len('if __name__ == "__main__":\n    main()\n')]
    
    # Write back
    file_path.write_text(new_content, encoding='utf-8')
    print(f"✅ Removed duplicate: {len(content)} → {len(new_content)} bytes")
    print(f"   Removed {len(content) - len(new_content)} bytes ({len(content) - len(new_content)} characters)")
else:
    print("⚠️ Could not find duplicate pattern")


