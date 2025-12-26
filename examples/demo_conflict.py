#!/usr/bin/env python3
"""
Demo: Conflict Detection
"""
from swarm_mcp.core.conflict import ConflictDetector

def main():
    print("🐺 Conflict Detection Demo")
    print("========================")
    
    detector = ConflictDetector(storage_dir="./demo_conflicts")
    
    # 1. Agent-1 declares intent
    print("\n1. Agent-1 starts working on auth...")
    intent, _ = detector.declare_intent(
        agent_id="agent-1",
        description="Fixing login bug",
        files=["src/auth/login.py", "src/auth/user.py"],
        keywords=["auth", "login"]
    )
    print(f"   Intent registered for {intent.agent_id}")
    
    # 2. Agent-2 checks for conflicts
    print("\n2. Agent-2 wants to modify user profile...")
    conflicts = detector.check_conflicts(
        agent_id="agent-2",
        files=["src/auth/user.py"], # Conflict!
        keywords=["user"]
    )
    
    if conflicts:
        print(f"   ⚠️ CONFLICT DETECTED!")
        for c in conflicts:
            print(f"   Severity: {c.severity.value}")
            print(f"   Reason: {c.reason}")
            print(f"   Between: {c.agents}")
    else:
        print("   No conflicts.")

if __name__ == "__main__":
    main()
