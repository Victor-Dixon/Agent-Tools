#!/usr/bin/env python3
"""
Verify Tools Consolidation Execution Status
===========================================

Checks if tools consolidation has been executed (tools archived/merged)
or if only analysis has been completed.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
Priority: HIGH - Verification for Agent-1 coordination
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def verify_consolidation_execution():
    """Verify if tools consolidation has been executed."""
    
    tools_dir = Path("tools")
    deprecated_dir = Path("tools/deprecated")
    
    # Tools identified for consolidation (from analysis)
    tools_to_archive = [
        "comprehensive_project_analyzer.py",
        "v2_compliance_checker.py",
        "v2_compliance_batch_checker.py",
        "quick_line_counter.py",
        "agent_toolbelt.py",
        "captain_toolbelt_help.py",
        "refactor_validator.py",
        "duplication_reporter.py",
    ]
    
    # Tools to keep (preferred versions)
    tools_to_keep = {
        "comprehensive_project_analyzer.py": "projectscanner_core.py",
        "v2_compliance_checker.py": "v2_checker_cli.py",
        "v2_compliance_batch_checker.py": "v2_checker_cli.py",
        "quick_line_counter.py": "quick_linecount.py",
        "agent_toolbelt.py": "toolbelt.py",
        "captain_toolbelt_help.py": "toolbelt_help.py",
        "refactor_validator.py": "refactor_analyzer.py",
        "duplication_reporter.py": "duplication_analyzer.py",
    }
    
    print("🔍 VERIFYING TOOLS CONSOLIDATION EXECUTION STATUS")
    print("=" * 60)
    
    # Check deprecated directory
    deprecated_exists = deprecated_dir.exists()
    print(f"\n📁 Deprecated Directory: {'✅ EXISTS' if deprecated_exists else '❌ NOT FOUND'}")
    
    if deprecated_exists:
        deprecated_files = list(deprecated_dir.glob("*.py"))
        print(f"   Files in deprecated/: {len(deprecated_files)}")
        if deprecated_files:
            print("   Archived files:")
            for f in deprecated_files[:10]:
                print(f"     - {f.name}")
    
    # Check each tool
    print("\n📋 TOOLS CONSOLIDATION STATUS:")
    print("-" * 60)
    
    execution_status = {
        "archived": [],
        "still_in_tools": [],
        "keep_version_exists": [],
        "keep_version_missing": [],
    }
    
    for tool_name in tools_to_archive:
        tool_path = tools_dir / tool_name
        deprecated_path = deprecated_dir / tool_name if deprecated_dir.exists() else None
        keep_tool = tools_to_keep.get(tool_name)
        keep_path = tools_dir / keep_tool if keep_tool else None
        
        print(f"\n🔍 {tool_name}:")
        
        # Check if archived
        if deprecated_path and deprecated_path.exists():
            print(f"   ✅ ARCHIVED in deprecated/")
            execution_status["archived"].append(tool_name)
        elif tool_path.exists():
            print(f"   ❌ STILL IN tools/ (not archived)")
            execution_status["still_in_tools"].append(tool_name)
        else:
            print(f"   ⚠️ NOT FOUND (may have been deleted)")
        
        # Check if keep version exists
        if keep_tool:
            if keep_path and keep_path.exists():
                print(f"   ✅ Keep version exists: {keep_tool}")
                execution_status["keep_version_exists"].append(keep_tool)
            else:
                print(f"   ❌ Keep version missing: {keep_tool}")
                execution_status["keep_version_missing"].append(keep_tool)
    
    # Check captain tools
    print("\n👑 CAPTAIN TOOLS STATUS:")
    print("-" * 60)
    
    captain_tools = list(tools_dir.glob("*captain*.py"))
    print(f"   Captain tools found: {len(captain_tools)}")
    if captain_tools:
        print("   Captain tools:")
        for t in captain_tools[:10]:
            print(f"     - {t.name}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 EXECUTION STATUS SUMMARY:")
    print("-" * 60)
    print(f"   ✅ Archived: {len(execution_status['archived'])}/{len(tools_to_archive)}")
    print(f"   ❌ Still in tools/: {len(execution_status['still_in_tools'])}/{len(tools_to_archive)}")
    print(f"   ✅ Keep versions exist: {len(execution_status['keep_version_exists'])}/{len(tools_to_keep)}")
    print(f"   ❌ Keep versions missing: {len(execution_status['keep_version_missing'])}/{len(tools_to_keep)}")
    
    # Determine execution status
    if len(execution_status["archived"]) == len(tools_to_archive):
        status = "✅ EXECUTION COMPLETE"
        message = "All duplicate tools have been archived. Consolidation execution is COMPLETE."
    elif len(execution_status["archived"]) > 0:
        status = "⚠️ PARTIAL EXECUTION"
        message = f"Some tools archived ({len(execution_status['archived'])}/{len(tools_to_archive)}), but consolidation is INCOMPLETE."
    else:
        status = "❌ EXECUTION NOT STARTED"
        message = "No tools have been archived. Only analysis has been completed. Execution is needed."
    
    print("\n" + "=" * 60)
    print(f"🎯 VERDICT: {status}")
    print(f"   {message}")
    print("=" * 60)
    
    # Generate report
    report_path = Path("agent_workspaces/Agent-2/TOOLS_CONSOLIDATION_EXECUTION_VERIFICATION.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    report = f"""# 🔍 TOOLS CONSOLIDATION EXECUTION VERIFICATION - Agent-2

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent**: Agent-2 (Architecture & Design Specialist)  
**Status**: {status}  
**Priority**: HIGH

---

## 🎯 **VERIFICATION RESULT**

**Status**: {status}

**Message**: {message}

---

## 📊 **DETAILED STATUS**

### **Tools to Archive** ({len(tools_to_archive)} total):

#### **✅ Archived** ({len(execution_status['archived'])}):
"""
    
    for tool in execution_status["archived"]:
        report += f"- ✅ `{tool}` - Archived in `tools/deprecated/`\n"
    
    report += f"""
#### **❌ Still in tools/** ({len(execution_status['still_in_tools'])}):
"""
    
    for tool in execution_status["still_in_tools"]:
        keep = tools_to_keep.get(tool, "N/A")
        report += f"- ❌ `{tool}` - Still in `tools/` (should be archived, keep: `{keep}`)\n"
    
    report += f"""
### **Keep Versions** ({len(tools_to_keep)} total):

#### **✅ Keep Versions Exist** ({len(execution_status['keep_version_exists'])}):
"""
    
    for tool in execution_status["keep_version_exists"]:
        report += f"- ✅ `{tool}` - Exists in `tools/`\n"
    
    report += f"""
#### **❌ Keep Versions Missing** ({len(execution_status['keep_version_missing'])}):
"""
    
    for tool in execution_status["keep_version_missing"]:
        report += f"- ❌ `{tool}` - Missing (should exist)\n"
    
    report += f"""
---

## 👑 **CAPTAIN TOOLS**

**Captain tools found**: {len(captain_tools)}

"""
    
    if captain_tools:
        report += "**Captain tools**:\n"
        for t in captain_tools:
            report += f"- `{t.name}`\n"
    else:
        report += "No captain tools found.\n"
    
    report += f"""
---

## 🎯 **RECOMMENDATION**

"""
    
    if status == "✅ EXECUTION COMPLETE":
        report += "✅ **Consolidation execution is COMPLETE.** Phase 1 can proceed.\n"
    elif status == "⚠️ PARTIAL EXECUTION":
        report += "⚠️ **Consolidation execution is INCOMPLETE.** Need to archive remaining tools before Phase 1.\n"
    else:
        report += "❌ **Consolidation execution has NOT STARTED.** Need to execute consolidation plan (archive 8 tools) before Phase 1.\n"
    
    report += f"""
---

## 🐝 **WE. ARE. SWARM.**

**Status**: {status}

**Agent-2 (Architecture & Design Specialist)**  
**Tools Consolidation Execution Verification - {datetime.now().strftime('%Y-%m-%d')}**

---

*Verification complete. Ready for Agent-1 coordination.*
"""
    
    report_path.write_text(report, encoding="utf-8")
    print(f"\n📝 Report created: {report_path}")
    
    return status, execution_status


if __name__ == "__main__":
    verify_consolidation_execution()
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


