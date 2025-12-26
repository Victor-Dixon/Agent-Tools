import pytest
import shutil
from pathlib import Path
from swarm_mcp.core.consensus import ConsensusEngine, VoteType, ConsensusRule

@pytest.fixture
def consensus_engine(tmp_path):
    engine = ConsensusEngine(storage_dir=str(tmp_path / "consensus"))
    return engine

def test_propose_and_vote(consensus_engine):
    # Create proposal
    proposal = consensus_engine.propose(
        proposer="agent-1",
        title="Use Python",
        description="Python is good",
        category="tech",
        rule=ConsensusRule.MAJORITY
    )
    
    assert proposal.status == "open"
    assert proposal.proposer == "agent-1"
    
    # Vote
    consensus_engine.vote(proposal.id, "agent-2", VoteType.APPROVE, "I like it")
    consensus_engine.vote(proposal.id, "agent-3", VoteType.REJECT, "I prefer Go")
    
    # Check tally
    tally = consensus_engine.get_tally(proposal.id)
    assert tally["tally"]["approve"]["count"] == 1
    assert tally["tally"]["reject"]["count"] == 1

def test_resolution_majority(consensus_engine):
    proposal = consensus_engine.propose(
        proposer="agent-1",
        title="Majority Vote",
        description="desc",
        rule=ConsensusRule.MAJORITY
    )
    
    consensus_engine.vote(proposal.id, "agent-2", VoteType.APPROVE, "yes")
    consensus_engine.vote(proposal.id, "agent-3", VoteType.APPROVE, "yes")
    consensus_engine.vote(proposal.id, "agent-4", VoteType.REJECT, "no")
    
    result = consensus_engine.resolve(proposal.id, force=True) # Force because deadline/status might be open
    
    assert result["passed"] is True
    assert result["status"] == "passed"

def test_resolution_unanimous_fail(consensus_engine):
    proposal = consensus_engine.propose(
        proposer="agent-1",
        title="Unanimous Vote",
        description="desc",
        rule=ConsensusRule.UNANIMOUS
    )
    
    consensus_engine.vote(proposal.id, "agent-2", VoteType.APPROVE, "yes")
    consensus_engine.vote(proposal.id, "agent-3", VoteType.REJECT, "no")
    
    result = consensus_engine.resolve(proposal.id, force=True)
    
    assert result["passed"] is False
    assert result["status"] == "rejected"
