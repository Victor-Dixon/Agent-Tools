#!/usr/bin/env python3
"""
Duplicate File Content Comparison - Finalization
Compares ~30-35 duplicate files for deletion decisions
"""

import filecmp
import hashlib
import json
from pathlib import Path
from typing import List, Tuple, Dict

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file content."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def compare_files(file1: Path, file2: Path) -> Dict:
    """Compare two files and return comparison results."""
    result = {
        'file1': str(file1),
        'file2': str(file2),
        'both_exist': file1.exists() and file2.exists(),
        'identical': False,
        'same_size': False,
        'same_hash': False,
        'filecmp_match': False,
    }
    
    if not result['both_exist']:
        return result
    
    # Size comparison
    try:
        result['same_size'] = file1.stat().st_size == file2.stat().st_size
        
        if result['same_size']:
            # Hash comparison
            hash1 = calculate_file_hash(file1)
            hash2 = calculate_file_hash(file2)
            result['same_hash'] = hash1 == hash2 and not hash1.startswith("ERROR")
            
            # Filecmp comparison (byte-by-byte)
            result['filecmp_match'] = filecmp.cmp(str(file1), str(file2), shallow=False)
            result['identical'] = result['filecmp_match']
    except Exception as e:
        result['error'] = str(e)
    
    return result

# Files needing comparison from duplicate resolution plan
duplicate_groups = [
    # Utils files (3 files)
    [
        'src/gui/utils.py',
        'src/vision/utils.py',
        'src/web/vector_database/utils.py',
    ],
    # Enums files (3 files)
    [
        'src/core/intelligent_context/enums.py',
        'src/core/ssot/unified_ssot/enums.py',
        'src/core/vector_strategic_oversight/unified_strategic_oversight/enums.py',
    ],
    # Metrics files (3 files)
    [
        'src/core/intelligent_context/metrics.py',
        'src/core/metrics.py',
        'src/obs/metrics.py',
    ],
    # FSM models (2 files)
    [
        'src/core/constants/fsm_models.py',
        'src/gaming/dreamos/fsm_models.py',
    ],
    # Messaging protocol models (2 files)
    [
        'src/core/messaging_protocol_models.py',
        'src/services/protocol/messaging_protocol_models.py',
    ],
    # Task executor (2 files)
    [
        'src/core/managers/execution/task_executor.py',
        'src/core/ssot/unified_ssot/execution/task_executor.py',
    ],
    # Metric manager (2 files)
    [
        'src/core/managers/monitoring/metric_manager.py',
        'src/core/performance/unified_dashboard/metric_manager.py',
    ],
    # Widget manager (2 files)
    [
        'src/core/managers/monitoring/widget_manager.py',
        'src/core/performance/unified_dashboard/widget_manager.py',
    ],
    # Engine files (2 files)
    [
        'src/core/performance/unified_dashboard/engine.py',
        'src/workflows/engine.py',
    ],
    # Extraction tools (2 files)
    [
        'src/core/refactoring/extraction_tools.py',
        'src/core/refactoring/tools/extraction_tools.py',
    ],
    # FSM bridge (2 files)
    [
        'src/message_task/fsm_bridge.py',
        'src/orchestrators/overnight/fsm_bridge.py',
    ],
]

def main():
    print("🔍 Comparing ~30-35 duplicate files for finalization...\n")
    
    all_results = []
    identical_pairs = []
    different_pairs = []
    
    for group in duplicate_groups:
        if len(group) < 2:
            continue
        
        # Compare all pairs in the group
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                file1 = Path(group[i])
                file2 = Path(group[j])
                
                comparison = compare_files(file1, file2)
                all_results.append(comparison)
                
                if comparison.get('identical', False):
                    identical_pairs.append(comparison)
                elif comparison.get('both_exist', False):
                    different_pairs.append(comparison)
    
    print("=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    print(f"\nTotal comparisons: {len(all_results)}")
    print(f"Identical files: {len(identical_pairs)}")
    print(f"Different files: {len(different_pairs)}")
    print(f"Files not found: {len(all_results) - len(identical_pairs) - len(different_pairs)}")
    
    if identical_pairs:
        print("\n✅ IDENTICAL FILES (Safe to delete one):")
        for r in identical_pairs:
            print(f"\n   File 1: {r['file1']}")
            print(f"   File 2: {r['file2']}")
            print(f"   Recommendation: DELETE {r['file2']} (keep {r['file1']})")
    
    if different_pairs:
        print("\n⚠️  DIFFERENT FILES (Keep both or merge):")
        for r in different_pairs[:10]:  # Show first 10
            print(f"\n   {r['file1']}")
            print(f"   vs {r['file2']}")
            print(f"   Same size: {r['same_size']}, Same hash: {r['same_hash']}")
    
    # Save results
    results_file = Path("agent_workspaces/Agent-8/DUPLICATE_COMPARISON_RESULTS.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_comparisons': len(all_results),
            'identical_pairs': identical_pairs,
            'different_pairs': different_pairs,
            'all_results': all_results
        }, f, indent=2)
    
    print(f"\n📝 Results saved to: {results_file}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")

if __name__ == '__main__':
    main()




