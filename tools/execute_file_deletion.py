"""
File Deletion Execution Script
Executes safe deletion of Category 1 files in batches.
"""

import json
import sys
from pathlib import Path

def delete_files(manifest_path: str, batch_size: int = 10):
    """Delete files from manifest in batches."""
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    files = manifest['deletion_manifest']['files']
    total = len(files)
    deleted = []
    failed = []
    
    print(f"📋 Deletion Manifest: {total} files to delete")
    print(f"📦 Batch size: {batch_size}\n")
    
    # Process in batches
    for batch_num in range(0, total, batch_size):
        batch = files[batch_num:batch_num + batch_size]
        batch_num_display = (batch_num // batch_size) + 1
        print(f"🔄 Processing Batch {batch_num_display} ({len(batch)} files)...")
        
        for file_path in batch:
            p = Path(file_path)
            try:
                if p.exists():
                    p.unlink()
                    deleted.append(file_path)
                    print(f"  ✅ Deleted: {file_path}")
                else:
                    print(f"  ⚠️  Not found (already deleted?): {file_path}")
                    deleted.append(file_path)  # Count as success
            except Exception as e:
                failed.append((file_path, str(e)))
                print(f"  ❌ Failed: {file_path} - {e}")
        
        print(f"\n📊 Batch {batch_num_display} Complete: {len(deleted)} deleted, {len(failed)} failed\n")
    
    # Summary
    print("=" * 60)
    print(f"✅ DELETION COMPLETE")
    print(f"   Total files: {total}")
    print(f"   Successfully deleted: {len(deleted)}")
    print(f"   Failed: {len(failed)}")
    print("=" * 60)
    
    if failed:
        print("\n❌ Failed files:")
        for file_path, error in failed:
            print(f"   - {file_path}: {error}")
    
    return deleted, failed

if __name__ == "__main__":
    manifest_path = "agent_workspaces/Agent-7/FILE_DELETION_MANIFEST.json"
    batch_size = 10
    
    if len(sys.argv) > 1:
        manifest_path = sys.argv[1]
    if len(sys.argv) > 2:
        batch_size = int(sys.argv[2])
    
    deleted, failed = delete_files(manifest_path, batch_size)
    
    # Save results
    results = {
        "deleted": deleted,
        "failed": [{"file": f, "error": e} for f, e in failed],
        "total_deleted": len(deleted),
        "total_failed": len(failed)
    }
    
    results_path = "agent_workspaces/Agent-7/FILE_DELETION_RESULTS.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_path}")
    
    sys.exit(0 if not failed else 1)




