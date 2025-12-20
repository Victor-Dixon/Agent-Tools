#!/usr/bin/env python3
"""
Review Consolidation Candidates - Phase 2
=========================================

Reviews tools marked as "review_needed" to determine if they can be archived.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-02
Priority: HIGH - Tools Consolidation Phase 2
"""

import json
import re
from pathlib import Path
from typing import Dict, List

def analyze_tool_complexity(tool_path: Path) -> Dict:
    """Analyze tool to determine if it can be replaced by unified tool."""
    try:
        content = tool_path.read_text(encoding="utf-8")
        lines = len(content.splitlines())
        
        # Check if it's a simple wrapper
        has_main = "if __name__" in content
        has_classes = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
        has_functions = len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
        
        # Check for unified tool usage
        uses_unified = "unified_monitor" in content or "unified_validator" in content or "unified_analyzer" in content
        
        # Simple tools are candidates
        is_simple = lines < 150 and has_functions < 5 and not has_classes
        
        return {
            "name": tool_path.stem,
            "path": str(tool_path),
            "lines": lines,
            "functions": has_functions,
            "classes": has_classes,
            "uses_unified": uses_unified,
            "is_simple": is_simple,
            "can_archive": is_simple and not uses_unified
        }
    except Exception as e:
        return {
            "name": tool_path.stem,
            "path": str(tool_path),
            "error": str(e),
            "can_archive": False
        }

def main():
    """Main execution."""
    repo_root = Path(__file__).parent.parent
    candidates_path = repo_root / "agent_workspaces" / "Agent-8" / "CONSOLIDATION_CANDIDATES_PHASE2.json"
    
    if not candidates_path.exists():
        print(f"❌ Candidates file not found: {candidates_path}")
        return
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    review_needed = candidates.get("review_needed", [])
    
    print(f"🔍 Reviewing {len(review_needed)} tools marked for review...\n")
    
    reviewed = []
    for candidate in review_needed:
        tool_path = Path(candidate["path"])
        if tool_path.exists():
            analysis = analyze_tool_complexity(tool_path)
            reviewed.append(analysis)
    
    # Count how many can be archived
    can_archive = [r for r in reviewed if r.get("can_archive", False)]
    
    print(f"✅ Can archive: {len(can_archive)}")
    print(f"⚠️  Need to keep: {len(review_needed) - len(can_archive)}")
    
    # Update candidates file
    for candidate in candidates.get("review_needed", []):
        tool_name = candidate["name"]
        for reviewed_tool in reviewed:
            if reviewed_tool["name"] == tool_name and reviewed_tool.get("can_archive", False):
                candidate["can_archive"] = True
                candidate["status"] = "candidate"
                break
    
    # Save updated candidates
    with open(candidates_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2)
    
    print(f"\n✅ Updated candidates file: {candidates_path}")
    print(f"📊 New candidates ready to archive: {len(can_archive)}")
    
    return 0

if __name__ == "__main__":
    exit(main())




