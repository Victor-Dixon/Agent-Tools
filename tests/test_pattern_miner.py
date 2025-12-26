import pytest
from swarm_mcp.core.pattern_miner import PatternMiner

@pytest.fixture
def miner(tmp_path):
    return PatternMiner(storage_dir=str(tmp_path / "patterns"))

def test_record_event(miner):
    event = miner.record_event(
        event_type="task_complete",
        agents=["agent-1"],
        context={"category": "test"},
        outcome="success"
    )
    
    assert event.outcome == "success"
    assert len(miner.events) == 1

def test_mine_patterns(miner):
    # Create 5 successful events with same pair
    for i in range(5):
        miner.record_event(
            event_type="collaboration",
            agents=["agent-1", "agent-2"],
            context={"category": "pairing"},
            outcome="success",
            quality_score=0.9
        )
        
    # Should have mined a pairing pattern
    patterns = miner.get_patterns("pairing")
    assert len(patterns) >= 1
    assert "agent-1" in patterns[0].name or "agent-2" in patterns[0].name

def test_suggest(miner):
    # Create pattern first
    for i in range(5):
        miner.record_event(
            event_type="collaboration",
            agents=["agent-1", "agent-2"],
            context={"category": "frontend"},
            outcome="success",
            quality_score=0.9
        )
        
    suggestions = miner.suggest(
        context={"category": "frontend"},
        agents=["agent-1", "agent-2"]
    )
    
    assert len(suggestions) > 0
    assert suggestions[0].confidence > 0.5
