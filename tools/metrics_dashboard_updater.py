#!/usr/bin/env python3
"""
Metrics Dashboard Updater Tool
==============================

Automatically updates Phase 1 metrics dashboard with progress updates.
Parses progress messages and updates dashboard sections accordingly.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-01-27
V2 Compliance: ✅ (<400 lines)
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class MetricsDashboardUpdater:
    """Updates Phase 1 metrics dashboard with progress information."""
    
    def __init__(self, dashboard_path: str = "docs/organization/PHASE1_METRICS_DASHBOARD.md"):
        """Initialize updater with dashboard path."""
        self.dashboard_path = Path(dashboard_path)
        self.dashboard_content = ""
        
    def load_dashboard(self) -> str:
        """Load current dashboard content."""
        if self.dashboard_path.exists():
            self.dashboard_content = self.dashboard_path.read_text(encoding='utf-8')
        else:
            self.dashboard_content = self._create_empty_dashboard()
        return self.dashboard_content
    
    def update_progress(self, batch: str, completed: int, total: int, 
                       status: str = "IN PROGRESS") -> bool:
        """Update batch progress in dashboard."""
        self.load_dashboard()
        
        # Calculate percentage
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        # Update batch progress section
        pattern = rf"(\*\*Batch {batch}\*\*.*?)(\d+)/(\d+) merges \((\d+)%\)"
        replacement = rf"\1{completed}/{total} merges ({percentage}%)"
        
        if re.search(pattern, self.dashboard_content, re.DOTALL):
            self.dashboard_content = re.sub(pattern, replacement, 
                                          self.dashboard_content, flags=re.DOTALL)
        else:
            # Add new batch entry if not found
            batch_section = f"**Batch {batch}**: 🚀 **{status}** - {completed}/{total} merges ({percentage}%)"
            # Insert after executive summary
            exec_summary_end = self.dashboard_content.find("---", 
                                                          self.dashboard_content.find("## 🎯 **EXECUTIVE SUMMARY**"))
            if exec_summary_end > 0:
                self.dashboard_content = (self.dashboard_content[:exec_summary_end] + 
                                        f"\n{batch_section}\n" + 
                                        self.dashboard_content[exec_summary_end:])
        
        return self._save_dashboard()
    
    def add_completed_merge(self, source: str, target: str, pr_number: Optional[str] = None,
                           merged: bool = False) -> bool:
        """Add completed merge to dashboard."""
        self.load_dashboard()
        
        # Format merge entry
        if merged:
            merge_entry = f"  - {source} → {target} ✅ **MERGED INTO MASTER** ✅"
        elif pr_number:
            merge_entry = f"  - {source} → {target} ✅ **COMPLETE** (PR #{pr_number} verified) ✅"
        else:
            merge_entry = f"  - {source} → {target} ✅ **COMPLETE** ✅"
        
        # Find completed merges section
        pattern = r"(\*\*Completed Merges\*\*.*?)(\n- \*\*Remaining Merges\*\*)"
        match = re.search(pattern, self.dashboard_content, re.DOTALL)
        
        if match:
            # Check if merge already exists
            if source not in match.group(1) and target not in match.group(1):
                # Insert before "Remaining Merges"
                insert_pos = match.end(1)
                self.dashboard_content = (self.dashboard_content[:insert_pos] + 
                                        f"\n{merge_entry}" + 
                                        self.dashboard_content[insert_pos:])
        else:
            # Add new completed merges section
            section = f"\n**Completed Merges**:\n{merge_entry}\n"
            # Insert after batch summary
            batch_summary_end = self.dashboard_content.find("---", 
                                                           self.dashboard_content.find("**Batch 2 Summary**"))
            if batch_summary_end > 0:
                self.dashboard_content = (self.dashboard_content[:batch_summary_end] + 
                                        section + 
                                        self.dashboard_content[batch_summary_end:])
        
        return self._save_dashboard()
    
    def update_blocker(self, blocker_name: str, status: str, impact: str,
                      workaround: Optional[str] = None) -> bool:
        """Update blocker status in dashboard."""
        self.load_dashboard()
        
        # Find blocker section
        pattern = rf"(\*\*🚨 CRITICAL: {re.escape(blocker_name)}\*\*.*?)(\*\*Status\*\*:.*?)(\n)"
        match = re.search(pattern, self.dashboard_content, re.DOTALL)
        
        if match:
            # Update status
            new_status = f"**Status**: {status}"
            self.dashboard_content = (self.dashboard_content[:match.start(2)] + 
                                    new_status + 
                                    self.dashboard_content[match.end(2):])
            
            # Update workaround if provided
            if workaround:
                workaround_pattern = rf"(\*\*Workaround\*\*:.*?)(\n)"
                workaround_match = re.search(workaround_pattern, 
                                           self.dashboard_content[match.start():match.end()], 
                                           re.DOTALL)
                if workaround_match:
                    new_workaround = f"**Workaround**: {workaround}"
                    self.dashboard_content = (self.dashboard_content[:match.start() + workaround_match.start(1)] + 
                                            new_workaround + 
                                            self.dashboard_content[match.start() + workaround_match.end(1):])
        else:
            # Add new blocker section
            blocker_section = f"""
#### **🚨 CRITICAL: {blocker_name}**
**Status**: {status}
**Impact**: {impact}
{f'**Workaround**: {workaround}' if workaround else ''}
"""
            # Insert in blockers section
            blockers_section = self.dashboard_content.find("## 🚨 **CRITICAL BLOCKERS & ISSUES**")
            if blockers_section > 0:
                active_blockers_start = self.dashboard_content.find("### **Active Blockers**", 
                                                                  blockers_section)
                if active_blockers_start > 0:
                    self.dashboard_content = (self.dashboard_content[:active_blockers_start] + 
                                            blocker_section + 
                                            self.dashboard_content[active_blockers_start:])
        
        return self._save_dashboard()
    
    def add_update_log_entry(self, title: str, content: str) -> bool:
        """Add entry to update log."""
        self.load_dashboard()
        
        # Format update entry
        timestamp = datetime.now().strftime("%Y-%m-%d")
        entry = f"""
### **{timestamp} - {title}**
{content}
"""
        
        # Find update log section
        update_log_start = self.dashboard_content.find("## 📅 **UPDATE LOG**")
        if update_log_start > 0:
            # Insert after update log header
            next_section = self.dashboard_content.find("### **", update_log_start + 1)
            if next_section > 0:
                self.dashboard_content = (self.dashboard_content[:next_section] + 
                                        entry + 
                                        self.dashboard_content[next_section:])
            else:
                # Append to end of update log section
                update_log_end = self.dashboard_content.find("---", update_log_start)
                if update_log_end > 0:
                    self.dashboard_content = (self.dashboard_content[:update_log_end] + 
                                            entry + 
                                            self.dashboard_content[update_log_end:])
        
        return self._save_dashboard()
    
    def _save_dashboard(self) -> bool:
        """Save updated dashboard content."""
        try:
            self.dashboard_path.write_text(self.dashboard_content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"❌ Error saving dashboard: {e}")
            return False
    
    def _create_empty_dashboard(self) -> str:
        """Create empty dashboard template."""
        return """# 📊 Phase 1 Metrics Dashboard

**Created By**: Agent-5 (Business Intelligence Specialist)  
**Date**: 2025-01-27  
**Status**: ✅ **ACTIVE - ONGOING TRACKING**  

---

## 🎯 **EXECUTIVE SUMMARY**

### **Overall Progress**
- **Starting Repos**: 75
- **Current Repos**: 75
- **Target**: 50 repos
- **Progress**: 0/25 repos (0%)

---

## 📅 **UPDATE LOG**

---

"""


def main():
    """CLI interface for dashboard updater."""
    import sys
    
    updater = MetricsDashboardUpdater()
    
    if len(sys.argv) < 2:
        print("Usage: python metrics_dashboard_updater.py <command> [args...]")
        print("\nCommands:")
        print("  progress <batch> <completed> <total> - Update batch progress")
        print("  merge <source> <target> [pr_number] [merged] - Add completed merge")
        print("  blocker <name> <status> <impact> [workaround] - Update blocker")
        print("  update <title> <content> - Add update log entry")
        return
    
    command = sys.argv[1]
    
    if command == "progress" and len(sys.argv) >= 5:
        batch = sys.argv[2]
        completed = int(sys.argv[3])
        total = int(sys.argv[4])
        if updater.update_progress(batch, completed, total):
            print(f"✅ Updated Batch {batch} progress: {completed}/{total}")
        else:
            print("❌ Failed to update progress")
    
    elif command == "merge" and len(sys.argv) >= 4:
        source = sys.argv[2]
        target = sys.argv[3]
        pr_number = sys.argv[4] if len(sys.argv) > 4 else None
        merged = len(sys.argv) > 5 and sys.argv[5].lower() == "true"
        if updater.add_completed_merge(source, target, pr_number, merged):
            print(f"✅ Added merge: {source} → {target}")
        else:
            print("❌ Failed to add merge")
    
    elif command == "blocker" and len(sys.argv) >= 5:
        name = sys.argv[2]
        status = sys.argv[3]
        impact = sys.argv[4]
        workaround = sys.argv[5] if len(sys.argv) > 5 else None
        if updater.update_blocker(name, status, impact, workaround):
            print(f"✅ Updated blocker: {name}")
        else:
            print("❌ Failed to update blocker")
    
    elif command == "update" and len(sys.argv) >= 4:
        title = sys.argv[2]
        content = " ".join(sys.argv[3:])
        if updater.add_update_log_entry(title, content):
            print(f"✅ Added update log entry: {title}")
        else:
            print("❌ Failed to add update log entry")
    
    else:
        print("❌ Invalid command or arguments")


if __name__ == "__main__":
    main()




