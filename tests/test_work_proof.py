import pytest
import json
from swarm_mcp.core.work_proof import WorkProofSystem

@pytest.fixture
def proof_system(tmp_path):
    # We need a dummy repo path. using tmp_path
    (tmp_path / "dummy.txt").write_text("initial content")
    return WorkProofSystem(storage_dir=str(tmp_path / "proofs"), repo_path=str(tmp_path))

def test_commit_and_prove(proof_system, tmp_path):
    # Commit
    commitment = proof_system.commit(
        agent_id="agent-1",
        task="Modify dummy",
        files=["dummy.txt"]
    )
    
    assert commitment.id in proof_system.active_commitments
    
    # Do work (modify file)
    (tmp_path / "dummy.txt").write_text("modified content")
    
    # Prove
    proof = proof_system.prove(commitment.id)
    
    assert proof.valid is True
    assert "dummy.txt" in proof.files_modified
    assert commitment.id not in proof_system.active_commitments

def test_invalid_proof_no_changes(proof_system, tmp_path):
    commitment = proof_system.commit(
        agent_id="agent-1",
        task="Do nothing",
        files=["dummy.txt"]
    )
    
    # No changes made
    
    proof = proof_system.prove(commitment.id)
    
    assert proof.valid is False
    assert "No file changes detected" in proof.validation_notes
