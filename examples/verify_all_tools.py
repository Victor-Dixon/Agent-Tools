import sys
import os
import subprocess
import json
from pathlib import Path

# Add workspace to path
sys.path.append(os.getcwd())

try:
    from tools.toolbelt_registry import TOOLS_REGISTRY
except ImportError:
    print("❌ Could not import TOOLS_REGISTRY")
    sys.exit(1)

def verify_all_tools():
    print("🧪 Verifying All Tools in Registry")
    print("================================")
    
    results = []
    
    # Ensure we run from workspace root
    cwd = os.getcwd()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd) + os.pathsep + env.get("PYTHONPATH", "")
    
    total = len(TOOLS_REGISTRY)
    passed = 0
    failed = 0
    
    for tool_id, config in TOOLS_REGISTRY.items():
        name = config["name"]
        flag = config["flags"][0] # Use the first flag
        
        print(f"Testing {name:<30} (ID: {tool_id})")
        
        # Special handling for tools that might exit 1 on "success" (e.g. security scanners finding issues)
        args = ["--help"]
        if tool_id == "security-scan":
            args = ["--warn-only"]
            
        cmd = [sys.executable, "-m", "tools.toolbelt", flag] + args
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"  ✅ OK")
                passed += 1
                results.append({"id": tool_id, "status": "ok"})
            else:
                print(f"  ❌ FAILED (Exit Code: {result.returncode})")
                print(f"     Error: {result.stderr.strip()[:200]}")
                failed += 1
                results.append({"id": tool_id, "status": "failed", "error": result.stderr})
                
        except Exception as e:
             print(f"  ❌ EXCEPTION: {e}")
             failed += 1
             results.append({"id": tool_id, "status": "exception", "error": str(e)})

    print("\n📊 Verification Summary")
    print("=======================")
    print(f"Total Tools: {total}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    
    if failed > 0:
        print("\n❌ Failures:")
        for res in results:
            if res["status"] != "ok":
                print(f"  - {res['id']}: {res.get('error', '').strip().splitlines()[0] if res.get('error') else 'Unknown error'}")

if __name__ == "__main__":
    verify_all_tools()
