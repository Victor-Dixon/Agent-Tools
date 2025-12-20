#!/usr/bin/env python3
"""
Generate Agent-7 Repo Checklists - Agent-3 Support Tool
========================================================

Generates individual integration checklists for Agent-7's 8 repos.
Applies Agent-3's proven 10-step integration pattern.

Usage:
    python tools/generate_agent7_repo_checklists.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Agent-7's 8 repos (from STAGE1_ASSIGNMENT_EXECUTION.md)
AGENT7_REPOS = [
    # Priority 1: Case Variations (3 repos)
    {"name": "FocusForge", "owner": "dadudekc", "merged_from": ["focusforge"], "source_repo": "focusforge"},
    {"name": "TBOWTactics", "owner": "dadudekc", "merged_from": ["tbowtactics"], "source_repo": "tbowtactics"},
    {"name": "Superpowered-TTRPG", "owner": "dadudekc", "merged_from": ["superpowered_ttrpg"], "source_repo": "superpowered_ttrpg"},
    # Priority 2: Consolidation Logs (5 repos)
    {"name": "selfevolving_ai", "owner": "dadudekc", "merged_from": ["gpt_automation"], "source_repo": "gpt_automation"},
    {"name": "Agent_Cellphone", "owner": "dadudekc", "merged_from": ["intelligent-multi-agent"], "source_repo": "intelligent-multi-agent"},
    {"name": "my-resume", "owner": "dadudekc", "merged_from": ["my_resume", "my_personal_templates"], "source_repo": "my_resume"},
    {"name": "trading-leads-bot", "owner": "dadudekc", "merged_from": ["trade-analyzer"], "source_repo": "trade-analyzer"},
]

INTEGRATION_STEPS = [
    ("1. Repository Structure Review", "Map merged repo directories, identify SSOT structure"),
    ("2. Dependency Analysis", "List all dependencies, identify conflicts"),
    ("3. Duplicate File Detection", "Find duplicates, identify venv files"),
    ("4. Verify Merged Content", "Verify merged directories present, check key files"),
    ("5. Dependency Integration", "Merge dependency lists, resolve conflicts"),
    ("6. Entry Point Configuration", "Verify entry points configured, update setup.py"),
    ("7. Structure Verification", "Verify SSOT structure maintained"),
    ("8. Dependency Verification", "Verify all dependencies available, test imports"),
    ("9. CI/CD Verification", "Verify workflows exist, check functionality"),
    ("10. Final Integration Check", "Check for integration issues, verify no broken imports"),
]

TOOLBELT_TOOLS = [
    ("--analyze-duplicates", "General-purpose duplicate analyzer"),
    ("--check-integration", "Integration issue checker"),
    ("--merge-duplicates", "Duplicate file merge analysis"),
    ("--verify-cicd", "CI/CD pipeline verification"),
]


def generate_checklist(repo_name: str, owner: str = "dadudekc", merged_from: list = None) -> str:
    """Generate integration checklist for a repo."""
    merged_list = merged_from or ["<merged-repo-1>", "<merged-repo-2>"]
    merged_str = ", ".join(merged_list)
    
    checklist = f"""# Stage 1 Integration Checklist: {repo_name}

**Owner**: {owner}  
**Status**: ⏳ PENDING  
**Pattern**: Agent-3 Success Model (2 repos, 0 issues)  
**Merged From**: {merged_str}

---

## 📋 **10-STEP INTEGRATION CHECKLIST**

"""
    
    for step_num, (step_name, step_desc) in enumerate(INTEGRATION_STEPS, 1):
        checklist += f"""### {step_name}
**Description**: {step_desc}

- [ ] Step {step_num} completed
- [ ] Findings documented
- [ ] Issues identified (if any)
- [ ] Resolution plan created (if needed)

"""
    
    checklist += f"""
## 🛠️ **TOOLBELT TOOLS TO USE**

"""
    for flag, desc in TOOLBELT_TOOLS:
        checklist += f"- ✅ `python tools/agent_toolbelt.py {flag}` - {desc}\n"
    
    checklist += f"""
## 📊 **VERIFICATION COMMANDS**

```bash
# 1. Structure Review
git clone https://github.com/{owner}/{repo_name}.git
cd {repo_name}
find . -type d -maxdepth 3 | sort

# 2. Dependency Analysis
python tools/agent_toolbelt.py --analyze-duplicates --repo {owner}/{repo_name} --check-venv

# 3. Duplicate Detection
python tools/agent_toolbelt.py --analyze-duplicates --repo {owner}/{repo_name} --check-venv

# 4. CI/CD Verification
python tools/agent_toolbelt.py --verify-cicd {repo_name}

# 5. Integration Check
python tools/agent_toolbelt.py --check-integration --repo {owner}/{repo_name}
```

---

## 🎯 **SUCCESS CRITERIA**

- ✅ All merged content verified present
- ✅ Dependencies integrated and working
- ✅ No duplicate conflicts
- ✅ Structure maintained
- ✅ CI/CD functional (if applicable)
- ✅ 0 critical issues

---

## 📚 **REFERENCE**

**Pattern Source**: Agent-3 (2 repos, 0 issues)  
**Support Package**: `agent_workspaces/Agent-7/AGENT3_INTEGRATION_SUPPORT_PACKAGE.md`  
**Support**: Available from Agent-3
"""
    
    return checklist


def main():
    """Main execution function."""
    print("🔍 Agent-7 Repo Checklist Generator")
    print("=" * 60)
    print()
    
    if not AGENT7_REPOS:
        print("⚠️ Agent-7 repos not yet identified")
        print("📋 Creating template checklist...")
        print()
        
        # Create template
        template = generate_checklist("REPO_NAME", "OWNER")
        output_file = Path("agent_workspaces/Agent-7/STAGE1_INTEGRATION_CHECKLIST_TEMPLATE.md")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(template)
        print(f"✅ Template created: {output_file}")
        print()
        print("📝 To generate checklists for specific repos:")
        print("   1. Update AGENT7_REPOS in this script")
        print("   2. Run: python tools/generate_agent7_repo_checklists.py")
        return 0
    
    print(f"📊 Generating checklists for {len(AGENT7_REPOS)} repos...")
    print()
    
    for repo in AGENT7_REPOS:
        checklist = generate_checklist(
            repo["name"],
            repo.get("owner", "dadudekc"),
            repo.get("merged_from", [])
        )
        output_file = Path(f"agent_workspaces/Agent-7/STAGE1_CHECKLIST_{repo['name']}.md")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(checklist)
        print(f"✅ Created: {output_file.name}")
    
    print()
    print("✅ All checklists generated!")
    print("📋 Share with Agent-7 for Stage 1 integration work")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

