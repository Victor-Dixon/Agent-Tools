import subprocess
import sys
import os

def run_swarm_cmd(args, description):
    print(f"\n--- {description} ---")
    cmd = [sys.executable, "-m", "swarm_mcp.cli"] + args
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✅ Success")
            output = result.stdout.strip()
            if output:
                print(output)
            else:
                print("(No output)")
        else:
            print("❌ Failed")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("🐺 Starting Swarm Tool Showcase")
    print("========================================")
    
    # 1. Check Status
    run_swarm_cmd(["status"], "Checking Swarm Status")
    
    # 2. Check Agent Profile
    run_swarm_cmd(["profile", "--agent", "agent-1"], "Checking Agent-1 Profile")
    
    # 3. List Patterns
    run_swarm_cmd(["patterns"], "Listing Discovered Patterns")
    
    # 4. Scan for Tasks
    run_swarm_cmd(["tasks", "--path", "tools/"], "Scanning 'tools/' for Tasks")
    
    # 5. Check Conflicts
    run_swarm_cmd(["conflict", "--list"], "Listing Active Conflicts/Intents")
    
    # 6. Check Voting
    run_swarm_cmd(["vote", "--agent", "agent-1"], "Checking Active Votes")
    
    # 7. Check Inbox
    run_swarm_cmd(["inbox", "agent-1"], "Checking Agent-1 Inbox")

    print("\n✅ Showcase Complete")

if __name__ == "__main__":
    main()
