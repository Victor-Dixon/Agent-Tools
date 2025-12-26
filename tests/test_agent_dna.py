import pytest
from swarm_mcp.core.agent_dna import AgentDNA

@pytest.fixture
def agent_dna(tmp_path):
    return AgentDNA(storage_dir=str(tmp_path / "dna"))

def test_record_task_and_profile_update(agent_dna):
    record = agent_dna.record_task(
        agent_id="agent-1",
        category="python",
        description="fix bug",
        files=["main.py"],
        duration_minutes=30,
        success=True,
        quality_score=0.9
    )
    
    assert record.agent_id == "agent-1"
    
    profile = agent_dna.get_profile("agent-1")
    assert profile is not None
    assert profile.total_tasks == 1
    assert profile.success_rate == 1.0
    assert profile.category_scores["python"] == 0.9

def test_find_best_agent(agent_dna):
    # Agent 1 is good at python
    agent_dna.record_task("agent-1", "python", "task1", ["a.py"], 10, True, 1.0)
    agent_dna.record_task("agent-1", "python", "task2", ["b.py"], 10, True, 1.0)
    
    # Agent 2 is bad at python
    agent_dna.record_task("agent-2", "python", "task3", ["c.py"], 10, False, 0.0)
    
    best = agent_dna.find_best_agent(category="python")
    assert best[0] == "agent-1"

def test_calculate_strengths(agent_dna):
    # Add multiple successful tasks
    for i in range(3):
        agent_dna.record_task("agent-1", "frontend", f"task{i}", ["ui.tsx"], 20, True, 0.9)
    
    profile = agent_dna.get_profile("agent-1")
    assert "frontend" in profile.strengths
