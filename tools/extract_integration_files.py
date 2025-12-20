"""Extract files needing integration from verification JSON."""

import json
from pathlib import Path

def main():
    """Extract integration files list."""
    json_path = Path("agent_workspaces/Agent-7/category1_verification.json")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    needs_integration = data.get('by_category', {}).get('needs_integration', [])
    
    print(f"Files needing integration: {len(needs_integration)}\n")
    
    for i, file_info in enumerate(needs_integration[:25], 1):
        file_path = file_info.get('file_path', '')
        print(f"{i}. {file_path}")
    
    # Save to file
    output_path = Path("agent_workspaces/Agent-7/INTEGRATION_FILES_LIST.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "total_files": len(needs_integration),
            "files": [f.get('file_path') for f in needs_integration[:25]]
        }, f, indent=2)
    
    print(f"\n✅ List saved to: {output_path}")

if __name__ == "__main__":
    main()




