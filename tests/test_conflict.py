import pytest
from datetime import datetime, timedelta
from swarm_mcp.core.conflict import ConflictDetector, ConflictSeverity

@pytest.fixture
def conflict_detector(tmp_path):
    return ConflictDetector(storage_dir=str(tmp_path / "conflicts"))

def test_declare_intent_no_conflict(conflict_detector):
    intent, conflicts = conflict_detector.declare_intent(
        agent_id="agent-1",
        description="Work on auth",
        files=["src/auth.py"]
    )
    
    assert intent.status == "active"
    assert len(conflicts) == 0

def test_detect_file_conflict(conflict_detector):
    # Agent 1 starts work
    conflict_detector.declare_intent(
        agent_id="agent-1",
        description="Work on auth",
        files=["src/auth.py"]
    )
    
    # Agent 2 tries same file
    conflicts = conflict_detector.check_conflicts(
        agent_id="agent-2",
        files=["src/auth.py"]
    )
    
    assert len(conflicts) == 1
    assert conflicts[0].severity == ConflictSeverity.HIGH
    assert "agent-1" in conflicts[0].agents

def test_detect_module_conflict(conflict_detector):
    conflict_detector.declare_intent(
        agent_id="agent-1",
        description="Work on db",
        modules=["database"]
    )
    
    conflicts = conflict_detector.check_conflicts(
        agent_id="agent-2",
        modules=["database"]
    )
    
    assert len(conflicts) == 1
    assert conflicts[0].severity == ConflictSeverity.MEDIUM

def test_expiration(conflict_detector):
    # Add expired intent manually or simulate it
    conflict_detector.declare_intent(
        agent_id="agent-1",
        description="Old work",
        files=["src/old.py"],
        ttl_hours=-1 # Expired immediately
    )
    
    conflicts = conflict_detector.check_conflicts(
        agent_id="agent-2",
        files=["src/old.py"]
    )
    
    # Should be no conflict because previous intent expired
    assert len(conflicts) == 0
