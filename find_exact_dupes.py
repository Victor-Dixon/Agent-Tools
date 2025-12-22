import hashlib
from pathlib import Path
from collections import defaultdict

def get_file_hash(path):
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def find_exact_duplicates():
    hashes = defaultdict(list)
    tools_dir = Path("tools")
    
    if not tools_dir.exists():
        return
        
    for path in tools_dir.rglob("*.py"):
        if path.is_file():
            h = get_file_hash(path)
            if h:
                hashes[h].append(str(path))
                
    duplicates = {k: v for k, v in hashes.items() if len(v) > 1}
    
    if duplicates:
        print("# Exact Content Duplicates")
        for h, paths in duplicates.items():
            print(f"- Group {h[:8]}:")
            for p in paths:
                print(f"  - {p}")
    else:
        print("No exact content duplicates found in tools/")

if __name__ == "__main__":
    find_exact_duplicates()
