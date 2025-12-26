#!/usr/bin/env python3
"""
Demo: Agent DNA & Learning
"""
from swarm_mcp.core.agent_dna import AgentDNA

def main():
    print("🐺 Agent DNA Demo")
    print("===============")
    
    dna = AgentDNA(storage_dir="./demo_dna")
    
    # 1. Train Agent-1 (Backend Expert)
    print("\n1. Recording tasks for Agent-1...")
    dna.record_task(
        agent_id="agent-1",
        category="backend",
        description="API endpoint",
        files=["api.py"],
        duration_minutes=30,
        success=True,
        quality_score=0.95
    )
    dna.record_task(
        agent_id="agent-1",
        category="database",
        description="Schema migration",
        files=["models.py"],
        duration_minutes=45,
        success=True,
        quality_score=0.9
    )
    
    # 2. Train Agent-2 (Frontend Expert)
    print("2. Recording tasks for Agent-2...")
    dna.record_task(
        agent_id="agent-2",
        category="frontend",
        description="React component",
        files=["ui.tsx"],
        duration_minutes=20,
        success=True,
        quality_score=0.9
    )
    
    # 3. Find best agent for a task
    print("\n3. Finding best agent for 'backend' work...")
    best = dna.find_best_agent(category="backend")
    print(f"   Winner: {best[0]} (Score: {best[1]:.2f})")
    
    print("\n4. Finding best agent for 'frontend' work...")
    best = dna.find_best_agent(category="frontend")
    print(f"   Winner: {best[0]} (Score: {best[1]:.2f})")

if __name__ == "__main__":
    main()
