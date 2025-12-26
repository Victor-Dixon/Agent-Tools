#!/usr/bin/env python3
"""
Demo: Consensus Engine
"""
from swarm_mcp.core.consensus import ConsensusEngine, VoteType, ConsensusRule

def main():
    print("🐺 Consensus Demo")
    print("=================")
    
    engine = ConsensusEngine(storage_dir="./demo_consensus")
    
    # 1. Create a proposal
    print("\n1. Agent-1 proposes architecture change...")
    proposal = engine.propose(
        proposer="agent-1",
        title="Switch to PostgreSQL",
        description="We need better transaction support",
        category="architecture",
        rule=ConsensusRule.MAJORITY
    )
    print(f"   Proposal created: {proposal.id}")
    
    # 2. Agents vote
    print("\n2. Agents casting votes...")
    
    print("   Agent-2 votes APPROVE")
    engine.vote(proposal.id, "agent-2", VoteType.APPROVE, "Agreed, we need ACID")
    
    print("   Agent-3 votes REJECT")
    engine.vote(proposal.id, "agent-3", VoteType.REJECT, "Too much migration effort")
    
    print("   Agent-4 votes APPROVE")
    engine.vote(proposal.id, "agent-4", VoteType.APPROVE, "Worth the effort")
    
    # 3. Resolve
    print("\n3. Resolving proposal...")
    result = engine.resolve(proposal.id)
    
    print(f"   Passed: {result['passed']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Tally: {result['tally']}")

if __name__ == "__main__":
    main()
