#!/usr/bin/env python3
"""Generate comprehensive markdown report from analysis JSON."""

import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
json_file = project_root / "agent_workspaces" / "Agent-5" / "COMPREHENSIVE_TOOLS_ANALYSIS_2025-12-06.json"
report_file = project_root / "agent_workspaces" / "Agent-5" / "COMPREHENSIVE_TOOLS_ANALYSIS_REPORT_2025-12-06.md"

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Generate markdown report
report = f"""# 📊 Comprehensive Tools Analysis Report

**Agent**: Agent-5 (Business Intelligence Specialist)  
**Date**: 2025-12-06  
**Total Tools Analyzed**: {data['summary']['total_tools']}  
**Status**: ✅ **COMPLETE**

---

## 📋 EXECUTIVE SUMMARY

- **Total Tools**: {data['summary']['total_tools']}
- **Categories**: {data['summary']['total_categories']}
- **Registered in Toolbelt**: {data['summary']['registered_tools']}
- **Unregistered**: {data['summary']['unregistered_tools']}
- **Consolidation Opportunities**: {data['summary']['consolidation_opportunities']} categories
- **Deletion Candidates**: {data['summary']['deletion_candidates']} tools
- **Integration Opportunities**: {data['summary']['integration_opportunities']} tools

---

## 📁 TOOL CATEGORIZATION

"""

# Add categories
categories_sorted = sorted(
    [(k, v['count']) for k, v in data['categories'].items()],
    key=lambda x: -x[1]
)

report += "| Category | Count | Top Tools |\n"
report += "|----------|-------|-----------|\n"

for cat, count in categories_sorted:
    tools = data['categories'][cat]['tools'][:5]
    tools_str = ", ".join(tools) if tools else "N/A"
    if len(tools_str) > 60:
        tools_str = tools_str[:57] + "..."
    report += f"| **{cat}** | {count} | {tools_str} |\n"

report += "\n---\n\n## 🔄 CONSOLIDATION OPPORTUNITIES\n\n"

# Add consolidation opportunities
for opp in data['consolidation_opportunities'][:10]:
    report += f"### **{opp['category'].upper()}** ({opp['count']} tools)\n\n"
    report += f"**Recommendation**: {opp['recommendation']}\n\n"
    report += "**Tools**:\n"
    for tool in opp['tools'][:10]:
        report += f"- `{tool['name']}` ({tool['line_count']} lines)\n"
    if len(opp['tools']) > 10:
        report += f"- ... and {len(opp['tools']) - 10} more\n"
    report += "\n"

report += "\n---\n\n## 🗑️ DELETION CANDIDATES\n\n"

# Add deletion candidates
report += "### **High Priority Deletion Candidates**\n\n"
report += "| Tool | Reason | Lines |\n"
report += "|------|--------|-------|\n"

for candidate in data['deletion_candidates'][:30]:
    tool = candidate['tool']
    reason = candidate['reason']
    lines = tool['line_count']
    name = tool['name']
    if len(name) > 40:
        name = name[:37] + "..."
    report += f"| `{name}` | {reason} | {lines} |\n"

report += "\n---\n\n## 🔗 INTEGRATION OPPORTUNITIES\n\n"

if data['integration_opportunities']:
    for opp in data['integration_opportunities'][:10]:
        tool = opp['tool']
        report += f"- **`{tool['name']}`**: {opp['recommendation']} - {opp['reason']}\n"
else:
    report += "**Note**: Integration opportunities analysis needs enhancement. Tools using core services should be reviewed for conversion to services/CLI/library functions.\n"

report += "\n---\n\n## 📊 DETAILED FINDINGS\n\n"

# Add detailed category breakdown
report += "### **Category Breakdown**\n\n"
for cat, count in categories_sorted:
    tools_list = data['categories'][cat]['tools']
    report += f"#### **{cat.upper()}** ({count} tools)\n\n"
    if len(tools_list) <= 20:
        for tool in tools_list:
            report += f"- `{tool}`\n"
    else:
        for tool in tools_list[:20]:
            report += f"- `{tool}`\n"
        report += f"- ... and {len(tools_list) - 20} more\n"
    report += "\n"

report += "\n---\n\n## 🎯 RECOMMENDATIONS\n\n"

report += """### **Immediate Actions** (High Priority):

1. **Execute Agent-8's Consolidation Plan** (156 tools → ~10 unified tools):
   - Captain Tools → `unified_captain.py`
   - GitHub Tools → `unified_github.py`
   - Verification Tools → `unified_verifier.py`
   - Archive/Cleanup → `unified_cleanup.py`
   - WordPress Tools → `unified_wordpress.py`
   - Discord Tools → `unified_discord.py`
   - Agent Tools → `unified_agent.py`

2. **Review and Delete Small/Unused Tools** (64 candidates):
   - Tools < 20 lines (likely stubs)
   - Tools not registered and no main function
   - Verify no dependencies before deletion

3. **Complete Toolbelt Registration**:
   - 464 tools unregistered
   - Register active tools in toolbelt
   - Archive or delete unused tools

### **Short-Term Actions** (Medium Priority):

4. **Enhance Integration Analysis**:
   - Review tools using core services
   - Convert appropriate tools to services
   - Integrate into CLI framework
   - Create library functions

5. **Complete Remaining Consolidations**:
   - Consolidation tools (37 tools)
   - Repository tools (22 tools)
   - Workflow tools (16 tools)
   - Testing tools (53 tools - many duplicates)

### **Long-Term Actions** (Ongoing):

6. **Maintain Tool Inventory**:
   - Regular analysis of new tools
   - Monitor tool usage
   - Identify new consolidation opportunities
   - Keep toolbelt registry updated

---

## 📈 ESTIMATED IMPACT

### **If All Consolidations Executed**:

- **Current**: 464 tools
- **After Agent-8 Consolidations**: ~310 tools (156 → 10)
- **After Deletion of Candidates**: ~250 tools (64 deleted)
- **After Remaining Consolidations**: ~200 tools (estimated)
- **Potential Final**: ~150-200 tools (50-60% reduction overall)

### **Benefits**:
- ✅ Reduced maintenance burden
- ✅ Clearer tool organization
- ✅ Better discoverability
- ✅ Improved SSOT compliance
- ✅ Easier onboarding
- ✅ Faster tool execution

---

## ✅ VERIFICATION CHECKLIST

### **Analysis Completeness**:
- [x] All 464 tools cataloged
- [x] All tools categorized (22 categories)
- [x] Consolidation opportunities identified (15 categories)
- [x] Deletion candidates identified (64 tools)
- [ ] Integration opportunities enhanced (needs improvement)
- [x] Master consolidation plan created

### **Next Steps**:
- [ ] Execute Agent-8's consolidation plan
- [ ] Review deletion candidates
- [ ] Register active tools in toolbelt
- [ ] Enhance integration analysis
- [ ] Create unified tools for high-priority categories

---

## 📝 NOTES

- **Toolbelt Registration**: 0 tools registered (registry check needs improvement)
- **Integration Analysis**: Needs enhancement to detect tools using core services
- **Testing Tools**: 53 tools identified, many appear to be duplicates
- **Miscellaneous**: 191 tools in miscellaneous category need further analysis

---

**Report Generated By**: Agent-5 (Business Intelligence Specialist)  
**Analysis Tool**: `tools/comprehensive_tool_analyzer.py`  
**Data Source**: `agent_workspaces/Agent-5/COMPREHENSIVE_TOOLS_ANALYSIS_2025-12-06.json`  
**Date**: 2025-12-06  
**Status**: ✅ **ANALYSIS COMPLETE**

🐝 WE. ARE. SWARM. ⚡🔥🚀
"""

# Write report
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✅ Report generated: {report_file}")
print(f"📊 Summary:")
print(f"   Total tools: {data['summary']['total_tools']}")
print(f"   Categories: {data['summary']['total_categories']}")
print(f"   Consolidation opportunities: {data['summary']['consolidation_opportunities']}")
print(f"   Deletion candidates: {data['summary']['deletion_candidates']}")

