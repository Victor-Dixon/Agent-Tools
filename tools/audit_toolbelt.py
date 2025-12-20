#!/usr/bin/env python3
"""
Toolbelt Auditor
================

Tests all 100 tools in the toolbelt and identifies which ones work vs need fixing.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import json
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools_v2.tool_registry import get_tool_registry
from tools_v2.toolbelt_core import get_toolbelt_core

logging.basicConfig(level=logging.ERROR)  # Suppress info logs during testing


def audit_all_tools():
    """Test all tools and categorize as working or broken."""
    registry = get_tool_registry()
    core = get_toolbelt_core()
    
    all_tools = registry.list_tools()
    
    working = []
    broken = []
    
    print(f"🔍 AUDITING {len(all_tools)} TOOLS...\n")
    
    for i, tool_name in enumerate(all_tools, 1):
        print(f"Testing {i}/{len(all_tools)}: {tool_name}...", end=" ")
        
        try:
            # Try to resolve the tool
            adapter_class = registry.resolve(tool_name)
            adapter = adapter_class()
            
            # Try to get spec
            spec = adapter.get_spec()
            
            # Try to get help
            help_text = adapter.get_help()
            
            # Tool loaded successfully
            working.append({
                'tool': tool_name,
                'category': spec.category,
                'version': spec.version
            })
            print("✅")
            
        except Exception as e:
            broken.append({
                'tool': tool_name,
                'error': str(e),
                'error_type': type(e).__name__
            })
            print(f"❌ ({type(e).__name__})")
    
    # Generate report
    print(f"\n{'='*60}")
    print("📊 AUDIT RESULTS")
    print(f"{'='*60}")
    print(f"✅ Working: {len(working)}/{len(all_tools)} ({len(working)/len(all_tools)*100:.1f}%)")
    print(f"❌ Broken: {len(broken)}/{len(all_tools)} ({len(broken)/len(all_tools)*100:.1f}%)")
    print(f"{'='*60}\n")
    
    if broken:
        print("🚨 BROKEN TOOLS (Need Fixing):")
        print(f"{'='*60}")
        
        # Group by error type
        error_types = {}
        for tool in broken:
            error_type = tool['error_type']
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(tool)
        
        for error_type, tools in error_types.items():
            print(f"\n{error_type} ({len(tools)} tools):")
            for tool in tools:
                print(f"  ❌ {tool['tool']}")
                print(f"     Error: {tool['error'][:80]}...")
        
        print(f"\n{'='*60}\n")
    
    # Save results
    results = {
        'total_tools': len(all_tools),
        'working_count': len(working),
        'broken_count': len(broken),
        'working_tools': working,
        'broken_tools': broken,
        'timestamp': str(Path('runtime/swarm_brain.json').stat().st_mtime if Path('runtime/swarm_brain.json').exists() else 0)
    }
    
    output_path = Path('runtime/toolbelt_audit.json')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Audit results saved to: {output_path}")
    
    # Create quarantine list
    if broken:
        quarantine_path = Path('runtime/toolbelt_quarantine.json')
        quarantine = {
            'quarantined_tools': [t['tool'] for t in broken],
            'count': len(broken),
            'details': broken,
            'status': 'NEEDS_FIXING'
        }
        
        with open(quarantine_path, 'w') as f:
            json.dump(quarantine, f, indent=2)
        
        print(f"🚨 Quarantine list saved to: {quarantine_path}")
        print(f"\n{'='*60}")
        print(f"🔧 {len(broken)} TOOLS QUARANTINED FOR SWARM FIXING")
        print(f"{'='*60}\n")
    
    return results


if __name__ == '__main__':
    results = audit_all_tools()
    
    # Exit with error code if any tools broken
    sys.exit(0 if results['broken_count'] == 0 else 1)

