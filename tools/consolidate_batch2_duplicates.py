#!/usr/bin/env python3
"""
Consolidate Batch 2 Duplicates
===============================

Consolidates Batch 2 duplicate files (15 groups, temp_repos/Thea/ directory).

Task: Batch 2 Consolidation (LOW priority)
- SSOT verified by Agent-8 ✅
- 15 groups, ~15 duplicate files to eliminate
- All SSOT files in temp_repos/Thea/ directory

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <300 lines
"""

import sys
import hashlib
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def get_file_hash(file_path: Path) -> str:
    """Get MD5 hash of file."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def verify_ssot(ssot_path: Path) -> Dict[str, any]:
    """Verify SSOT file exists and is valid."""
    if not ssot_path.exists():
        return {
            "valid": False,
            "error": f"SSOT file not found: {ssot_path}"
        }
    
    ssot_hash = get_file_hash(ssot_path)
    ssot_size = ssot_path.stat().st_size
    
    return {
        "valid": True,
        "path": str(ssot_path),
        "hash": ssot_hash,
        "size": ssot_size,
        "exists": True
    }


def find_duplicates(ssot_path: Path, duplicate_paths: List[str]) -> Dict[str, any]:
    """Find and verify duplicate files."""
    ssot_hash = get_file_hash(ssot_path)
    duplicates_found = []
    missing_files = []
    different_files = []
    
    for dup_path_str in duplicate_paths:
        dup_path = project_root / dup_path_str.replace("\\", "/")
        
        if not dup_path.exists():
            missing_files.append(str(dup_path))
            continue
        
        dup_hash = get_file_hash(dup_path)
        
        if dup_hash == ssot_hash:
            duplicates_found.append({
                "path": str(dup_path),
                "hash": dup_hash,
                "size": dup_path.stat().st_size
            })
        else:
            different_files.append({
                "path": str(dup_path),
                "hash": dup_hash,
                "ssot_hash": ssot_hash
            })
    
    return {
        "duplicates": duplicates_found,
        "missing": missing_files,
        "different": different_files,
        "total_found": len(duplicates_found)
    }


def delete_duplicates(duplicates: List[Dict]) -> Dict[str, any]:
    """Delete duplicate files."""
    deleted = []
    errors = []
    
    for dup in duplicates:
        dup_path = Path(dup["path"])
        try:
            if dup_path.exists():
                dup_path.unlink()
                deleted.append(str(dup_path))
        except Exception as e:
            errors.append({
                "file": str(dup_path),
                "error": str(e)
            })
    
    return {
        "deleted": deleted,
        "errors": errors,
        "count": len(deleted)
    }


def main():
    """Main execution."""
    print("🔧 Consolidate Batch 2 Duplicates")
    print("   Task: Batch 2 Consolidation (15 groups, temp_repos/Thea/)")
    print("   SSOT Verification: ✅ PASSED (Agent-8)")
    print()
    
    # Batch 2 groups from verification report
    batch2_groups = [
        {
            "ssot": "temp_repos/Thea/demos/gui_components/conversation_viewer.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/demos/gui_components/conversation_viewer.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/demos/training_data_extraction/conversation_analyzer.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/demos/training_data_extraction/conversation_analyzer.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/scripts/workflows/chatgpt_integration.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/scripts/workflows/chatgpt_integration.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/chatgpt_api_client.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/chatgpt_api_client.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/check_conversation_duplicates.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/check_conversation_duplicates.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/content/enrich_conversation_data.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/content/enrich_conversation_data.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/conversation_storage.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/conversation_storage.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/conversation_system.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/conversation_system.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/create_conversations_json.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/create_conversations_json.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/demo_conversation_context.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/demo_conversation_context.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/ingest_conversations.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/ingest_conversations.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/intelligence/analysis/conversation_analyzer.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/intelligence/analysis/conversation_analyzer.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/legacy/chat_with_my_agent.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/legacy/chat_with_my_agent.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/legacy/chatgpt_dreamscape_agent.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/legacy/chatgpt_dreamscape_agent.py"
            ]
        },
        {
            "ssot": "temp_repos/Thea/src/dreamscape/core/legacy/conversation_legacy.py",
            "duplicates": [
                "agent_workspaces/Agent-2/extracted_logic/ai_framework/conversation/src/dreamscape/core/legacy/conversation_legacy.py"
            ]
        }
    ]
    
    total_deleted = 0
    total_errors = 0
    
    # Process each group
    for i, group in enumerate(batch2_groups, 1):
        ssot_path = project_root / group["ssot"]
        
        print(f"📋 Group {i}/15: {ssot_path.name}")
        
        # Verify SSOT
        ssot_result = verify_ssot(ssot_path)
        if not ssot_result["valid"]:
            print(f"   ⚠️  SSOT verification failed: {ssot_result['error']}")
            continue
        
        # Find duplicates
        duplicates_result = find_duplicates(ssot_path, group["duplicates"])
        
        if duplicates_result["total_found"] == 0:
            print(f"   ⚠️  No duplicates found (may already be deleted)")
            continue
        
        # Delete duplicates (dry run first)
        if "--execute" not in sys.argv:
            print(f"   📝 Would delete {duplicates_result['total_found']} duplicate(s)")
            continue
        
        # Execute deletion
        delete_result = delete_duplicates(duplicates_result['duplicates'])
        total_deleted += delete_result["count"]
        total_errors += len(delete_result["errors"])
        
        if delete_result["count"] > 0:
            print(f"   ✅ Deleted {delete_result['count']} duplicate(s)")
        if delete_result["errors"]:
            print(f"   ⚠️  {len(delete_result['errors'])} error(s) during deletion")
    
    print()
    
    if "--execute" not in sys.argv:
        print("⚠️  DRY RUN MODE - No files deleted")
        print("   Use --execute flag to actually delete files")
        print()
        print("📋 Summary:")
        print(f"   Groups: 15")
        print(f"   SSOT Location: temp_repos/Thea/")
        print(f"   Ready for consolidation: ✅")
        return 0
    
    print("🎯 Consolidation complete!")
    print(f"   Files eliminated: {total_deleted}")
    print(f"   Errors: {total_errors}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

