#!/usr/bin/env python3
"""
Identify Consolidation Candidates - Phase 2
============================================

Identifies tools that can be replaced by unified_monitor, unified_validator, or unified_analyzer.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-02
Priority: HIGH - Tools Consolidation Phase 2
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Unified tools capabilities (from reading the files)
UNIFIED_MONITOR_CAPABILITIES = {
    "keywords": ["monitor", "health", "status", "check", "queue", "service", "agent", "infrastructure", "test", "coverage"],
    "functions": ["monitor_queue_health", "monitor_service_health", "monitor_agent_status", "monitor_infrastructure", "monitor_test_coverage"]
}

UNIFIED_VALIDATOR_CAPABILITIES = {
    "keywords": ["validate", "verify", "check", "ssot", "import", "config", "queue", "session", "consolidation"],
    "functions": ["validate_ssot_config", "validate_imports", "validate_code_docs", "validate_queue_behavior", "validate_session_transition", "validate_consolidation"]
}

UNIFIED_ANALYZER_CAPABILITIES = {
    "keywords": ["analyze", "scan", "audit", "report", "structure", "code", "ast", "complexity", "import", "messaging", "technical", "debt", "github", "repo", "architecture"],
    "functions": ["analyze_project_structure", "analyze_code_file", "analyze_messaging_files", "analyze_technical_debt", "analyze_github_repo", "analyze_architecture"]
}

def analyze_tool_for_consolidation(tool_path: Path) -> Dict:
    """Analyze if tool can be replaced by unified tool."""
    try:
        content = tool_path.read_text(encoding="utf-8")
        content_lower = content.lower()
        
        # Check for unified tool imports (already using unified tools)
        if "unified_monitor" in content or "unified_validator" in content or "unified_analyzer" in content:
            return {
                "name": tool_path.stem,
                "path": str(tool_path),
                "status": "already_using_unified",
                "can_archive": False
            }
        
        # Check monitoring keywords
        monitoring_score = sum(1 for kw in UNIFIED_MONITOR_CAPABILITIES["keywords"] if kw in content_lower)
        
        # Check validation keywords
        validation_score = sum(1 for kw in UNIFIED_VALIDATOR_CAPABILITIES["keywords"] if kw in content_lower)
        
        # Check analysis keywords
        analysis_score = sum(1 for kw in UNIFIED_ANALYZER_CAPABILITIES["keywords"] if kw in content_lower)
        
        # Determine category
        scores = {
            "monitoring": monitoring_score,
            "validation": validation_score,
            "analysis": analysis_score
        }
        
        max_score = max(scores.values())
        if max_score < 2:  # Not enough keywords to be a candidate
            return {
                "name": tool_path.stem,
                "path": str(tool_path),
                "status": "not_candidate",
                "can_archive": False
            }
        
        # Determine which unified tool can replace it
        category = max(scores, key=scores.get)
        
        # Check if it's a simple wrapper or duplicate
        lines = len(content.splitlines())
        is_simple = lines < 100 and max_score >= 3
        
        return {
            "name": tool_path.stem,
            "path": str(tool_path),
            "category": category,
            "score": max_score,
            "lines": lines,
            "status": "candidate" if is_simple or max_score >= 5 else "review_needed",
            "can_archive": is_simple,
            "unified_replacement": f"unified_{category}.py"
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
    tools_dir = Path(__file__).parent
    tools = list(tools_dir.glob("*.py"))
    
    # Exclude unified tools and special files
    exclude = {"unified_monitor.py", "unified_validator.py", "unified_analyzer.py", 
               "__init__.py", "__main__.py", "identify_consolidation_candidates.py"}
    tools = [t for t in tools if t.name not in exclude]
    
    print(f"🔍 Analyzing {len(tools)} tools for consolidation candidates...\n")
    
    candidates = {
        "monitoring": [],
        "validation": [],
        "analysis": [],
        "review_needed": [],
        "already_using_unified": [],
        "not_candidate": []
    }
    
    for tool_path in tools:
        result = analyze_tool_for_consolidation(tool_path)
        
        if result.get("status") == "candidate":
            category = result.get("category")
            candidates[category].append(result)
        elif result.get("status") == "review_needed":
            candidates["review_needed"].append(result)
        elif result.get("status") == "already_using_unified":
            candidates["already_using_unified"].append(result)
        else:
            candidates["not_candidate"].append(result)
    
    # Print summary
    print("=" * 60)
    print("📊 CONSOLIDATION CANDIDATES SUMMARY")
    print("=" * 60)
    print(f"\n✅ Monitoring Candidates: {len(candidates['monitoring'])}")
    print(f"✅ Validation Candidates: {len(candidates['validation'])}")
    print(f"✅ Analysis Candidates: {len(candidates['analysis'])}")
    print(f"⚠️  Review Needed: {len(candidates['review_needed'])}")
    print(f"ℹ️  Already Using Unified: {len(candidates['already_using_unified'])}")
    print(f"❌ Not Candidates: {len(candidates['not_candidate'])}")
    
    # Save results
    output_path = tools_dir.parent / "agent_workspaces" / "Agent-8" / "CONSOLIDATION_CANDIDATES_PHASE2.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_path}")
    
    # Show top candidates
    print("\n" + "=" * 60)
    print("🔝 TOP CONSOLIDATION CANDIDATES")
    print("=" * 60)
    
    for category in ["monitoring", "validation", "analysis"]:
        if candidates[category]:
            print(f"\n📊 {category.upper()} ({len(candidates[category])} candidates):")
            sorted_candidates = sorted(candidates[category], key=lambda x: x.get("score", 0), reverse=True)
            for i, candidate in enumerate(sorted_candidates[:10], 1):
                print(f"   {i}. {candidate['name']} (score: {candidate['score']}, lines: {candidate['lines']})")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")

if __name__ == "__main__":
    main()




