#!/usr/bin/env python3
"""
Execute Phase 1 File Deletion - Technical Debt Quick Wins
==========================================================

Executes Phase 1 file deletion in batches of 10 files.
Validates after each batch to ensure system stability.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import shutil

PROJECT_ROOT = Path(__file__).parent.parent
MANIFEST_FILE = PROJECT_ROOT / "agent_workspaces" / "Agent-7" / "FILE_DELETION_MANIFEST.json"
BACKUP_DIR = PROJECT_ROOT / "docs" / "archive" / "consolidation" / "phase1_deletion_backup"
BATCH_SIZE = 10

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_manifest() -> Dict:
    """Load deletion manifest."""
    if not MANIFEST_FILE.exists():
        raise FileNotFoundError(f"Manifest file not found: {MANIFEST_FILE}")
    
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Handle nested structure
        if "deletion_manifest" in data:
            return data["deletion_manifest"]
        return data


def create_backup(file_path: Path) -> bool:
    """Create backup of file before deletion."""
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        relative_path = file_path.relative_to(PROJECT_ROOT)
        backup_path = BACKUP_DIR / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.is_file():
            shutil.copy2(file_path, backup_path)
            logger.info(f"✅ Backed up: {relative_path}")
            return True
        elif file_path.is_dir():
            shutil.copytree(file_path, backup_path, dirs_exist_ok=True)
            logger.info(f"✅ Backed up directory: {relative_path}")
            return True
        else:
            logger.warning(f"⚠️  File not found (may already be deleted): {relative_path}")
            return False
    except Exception as e:
        logger.error(f"❌ Error backing up {file_path}: {e}")
        return False


def delete_file(file_path: Path) -> Tuple[bool, str]:
    """Delete a file or directory."""
    try:
        if not file_path.exists():
            return True, "File already deleted"
        
        # Create backup first
        if not create_backup(file_path):
            return False, "Backup failed"
        
        if file_path.is_file():
            file_path.unlink()
            logger.info(f"✅ Deleted file: {file_path.relative_to(PROJECT_ROOT)}")
            return True, "File deleted"
        elif file_path.is_dir():
            shutil.rmtree(file_path)
            logger.info(f"✅ Deleted directory: {file_path.relative_to(PROJECT_ROOT)}")
            return True, "Directory deleted"
        else:
            return False, "Unknown file type"
    except Exception as e:
        logger.error(f"❌ Error deleting {file_path}: {e}")
        return False, str(e)


def verify_batch_deletion(files: List[Path]) -> Tuple[int, int]:
    """Verify that files in batch were successfully deleted."""
    deleted = 0
    failed = 0
    
    for file_path in files:
        if not file_path.exists():
            deleted += 1
        else:
            failed += 1
            logger.warning(f"⚠️  File still exists: {file_path.relative_to(PROJECT_ROOT)}")
    
    return deleted, failed


def execute_batch_deletion(files: List[Dict], batch_num: int) -> Dict:
    """Execute deletion for a batch of files."""
    logger.info(f"\n{'='*60}")
    logger.info(f"📦 BATCH {batch_num} - Processing {len(files)} files")
    logger.info(f"{'='*60}\n")
    
    batch_results = {
        "batch_number": batch_num,
        "total_files": len(files),
        "deleted": 0,
        "failed": 0,
        "skipped": 0,
        "errors": []
    }
    
    for file_info in files:
        file_path_str = file_info.get("path", "")
        reason = file_info.get("reason", "Technical debt reduction")
        
        if not file_path_str:
            batch_results["skipped"] += 1
            continue
        
        file_path = PROJECT_ROOT / file_path_str
        
        logger.info(f"🗑️  Deleting: {file_path_str}")
        logger.info(f"   Reason: {reason}")
        
        success, message = delete_file(file_path)
        
        if success:
            batch_results["deleted"] += 1
        else:
            batch_results["failed"] += 1
            batch_results["errors"].append({
                "file": file_path_str,
                "error": message
            })
            logger.error(f"❌ Failed to delete {file_path_str}: {message}")
    
    # Verify batch
    logger.info(f"\n🔍 Verifying batch {batch_num} deletion...")
    file_paths = [PROJECT_ROOT / f.get("path", "") for f in files if f.get("path")]
    deleted_count, failed_count = verify_batch_deletion(file_paths)
    
    logger.info(f"\n📊 Batch {batch_num} Results:")
    logger.info(f"   ✅ Deleted: {deleted_count}/{len(files)}")
    logger.info(f"   ❌ Failed: {failed_count}/{len(files)}")
    
    return batch_results


def main():
    """Execute Phase 1 file deletion in batches."""
    logger.info("🚨 PHASE 1 FILE DELETION - Technical Debt Quick Wins")
    logger.info("=" * 60)
    
    # Load manifest
    logger.info("📋 Loading deletion manifest...")
    manifest = load_manifest()
    
    files_to_delete = manifest.get("files", [])
    total_files = len(files_to_delete)
    
    # Convert file paths to file info dicts if needed
    if files_to_delete and isinstance(files_to_delete[0], str):
        files_to_delete = [{"path": f, "reason": "Technical debt reduction - Category 1: Truly Unused"} for f in files_to_delete]
    
    logger.info(f"📊 Total files to delete: {total_files}")
    logger.info(f"📦 Batch size: {BATCH_SIZE}")
    logger.info(f"📁 Backup directory: {BACKUP_DIR.relative_to(PROJECT_ROOT)}")
    logger.info("")
    
    # Process in batches
    all_results = []
    total_batches = (total_files + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_num in range(1, total_batches + 1):
        start_idx = (batch_num - 1) * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, total_files)
        batch_files = files_to_delete[start_idx:end_idx]
        
        batch_result = execute_batch_deletion(batch_files, batch_num)
        all_results.append(batch_result)
        
        # Pause between batches for verification
        if batch_num < total_batches:
            logger.info(f"\n⏸️  Pausing before next batch...")
            logger.info(f"   Progress: {batch_num}/{total_batches} batches complete")
            logger.info("")
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info("📊 FINAL SUMMARY")
    logger.info(f"{'='*60}\n")
    
    total_deleted = sum(r["deleted"] for r in all_results)
    total_failed = sum(r["failed"] for r in all_results)
    total_skipped = sum(r["skipped"] for r in all_results)
    
    logger.info(f"✅ Total Deleted: {total_deleted}/{total_files}")
    logger.info(f"❌ Total Failed: {total_failed}/{total_files}")
    logger.info(f"⏭️  Total Skipped: {total_skipped}/{total_files}")
    logger.info(f"📁 Backup Location: {BACKUP_DIR.relative_to(PROJECT_ROOT)}")
    
    # Save results
    results_file = PROJECT_ROOT / "docs" / "archive" / "consolidation" / "phase1_deletion_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    results = {
        "total_files": total_files,
        "total_deleted": total_deleted,
        "total_failed": total_failed,
        "total_skipped": total_skipped,
        "batches": all_results,
        "backup_location": str(BACKUP_DIR.relative_to(PROJECT_ROOT))
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\n✅ Results saved to: {results_file.relative_to(PROJECT_ROOT)}")
    
    if total_failed > 0:
        logger.warning(f"\n⚠️  {total_failed} files failed to delete. Review errors above.")
        return 1
    
    logger.info("\n✅ Phase 1 file deletion complete!")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

