#!/usr/bin/env python3
"""
Demo: Work Proof
"""
import time
from pathlib import Path
from swarm_mcp.core.work_proof import WorkProofSystem

def main():
    print("🐺 Work Proof Demo")
    print("================")
    
    # Setup dummy file
    Path("demo_file.txt").write_text("Original content")
    
    system = WorkProofSystem(storage_dir="./demo_proofs")
    
    # 1. Commit
    print("\n1. Agent-1 commits to work...")
    commitment = system.commit(
        agent_id="agent-1",
        task="Update demo file",
        files=["demo_file.txt"]
    )
    print(f"   Commitment ID: {commitment.id}")
    
    # 2. Do Work
    print("\n2. Agent-1 doing work...")
    time.sleep(1)
    Path("demo_file.txt").write_text("Updated content by Agent-1")
    
    # 3. Generate Proof
    print("\n3. Generating proof...")
    proof = system.prove(commitment.id)
    
    print(f"   Proof Generated!")
    print(f"   Duration: {proof.duration_seconds:.2f}s")
    print(f"   Files Modified: {proof.files_modified}")
    print(f"   Valid: {proof.valid}")
    
    # Cleanup
    Path("demo_file.txt").unlink()

if __name__ == "__main__":
    main()
