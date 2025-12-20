#!/usr/bin/env python3
"""
Measure Delegation Overhead
============================

Measures time and communication overhead in agent delegation patterns.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-13
Priority: URGENT - Gap Closure Order
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

def analyze_delegation_overhead() -> Dict:
    """Analyze delegation overhead from artifacts and coordination files."""
    
    artifacts_dir = Path("artifacts")
    docs_dir = Path("docs")
    inbox_dir = Path("agent_workspaces")
    
    delegations = []
    coordinations = []
    handoffs = []
    
    # Find delegation mentions in artifacts
    for artifact_file in artifacts_dir.glob("*.md"):
        try:
            content = artifact_file.read_text(encoding='utf-8')
            
            # Find delegations
            if "delegated" in content.lower() or "delegation" in content.lower():
                delegations.append({
                    "file": str(artifact_file),
                    "mentions": len(re.findall(r'delegat', content, re.IGNORECASE))
                })
            
            # Find coordinations
            if "coordination" in content.lower() or "bilateral" in content.lower():
                coordinations.append({
                    "file": str(artifact_file),
                    "mentions": len(re.findall(r'coordinat|bilateral', content, re.IGNORECASE))
                })
            
            # Find handoffs
            if "handoff" in content.lower() or "phase" in content.lower():
                handoffs.append({
                    "file": str(artifact_file),
                    "mentions": len(re.findall(r'handoff|phase', content, re.IGNORECASE))
                })
        except Exception:
            continue
    
    # Count coordination files
    coordination_files = list(docs_dir.glob("*COORDINATION*.md"))
    
    # Count inbox messages (proxy for communication overhead)
    inbox_messages = 0
    for agent_dir in inbox_dir.glob("Agent-*/inbox"):
        if agent_dir.exists():
            inbox_messages += len(list(agent_dir.glob("*.md")))
    
    # Calculate overhead metrics
    total_delegations = len(delegations)
    total_coordinations = len(coordinations)
    total_handoffs = len(handoffs)
    total_coordination_files = len(coordination_files)
    
    return {
        "delegation_count": total_delegations,
        "coordination_count": total_coordinations,
        "handoff_count": total_handoffs,
        "coordination_files": total_coordination_files,
        "inbox_messages": inbox_messages,
        "delegation_files": delegations,
        "coordination_files_list": [str(f) for f in coordination_files],
        "overhead_score": total_delegations + total_coordinations + total_handoffs,
        "timestamp": datetime.now().isoformat()
    }

def generate_recommendations(metrics: Dict) -> List[str]:
    """Generate recommendations to reduce delegation overhead."""
    recommendations = []
    
    if metrics["delegation_count"] > 5:
        recommendations.append("High delegation count - consider batch delegations")
    
    if metrics["coordination_files"] > 3:
        recommendations.append("Multiple coordination files - consolidate coordination patterns")
    
    if metrics["inbox_messages"] > 50:
        recommendations.append("High inbox message count - implement async coordination")
    
    if metrics["handoff_count"] > 10:
        recommendations.append("Many handoff points - streamline phase transitions")
    
    return recommendations

if __name__ == "__main__":
    print("📊 Measuring Delegation Overhead...\n")
    
    metrics = analyze_delegation_overhead()
    
    print(f"Delegation Files: {metrics['delegation_count']}")
    print(f"Coordination Files: {metrics['coordination_count']}")
    print(f"Handoff Points: {metrics['handoff_count']}")
    print(f"Coordination Documents: {metrics['coordination_files']}")
    print(f"Inbox Messages: {metrics['inbox_messages']}")
    print(f"\nOverhead Score: {metrics['overhead_score']}")
    
    recommendations = generate_recommendations(metrics)
    if recommendations:
        print("\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  - {rec}")
    
    # Save metrics
    output_file = Path("artifacts/2025-12-13_agent-5_delegation-overhead-metrics.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✅ Metrics saved to: {output_file}")


