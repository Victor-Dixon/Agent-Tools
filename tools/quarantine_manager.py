#!/usr/bin/env python3
"""
Quarantine Manager - Systematic Tool Repair Coordination
========================================================

Manages the quarantine → fix → reintegrate workflow for broken tools.

USAGE:
    # List quarantined tools
    python tools/quarantine_manager.py list
    
    # Assign tool to agent
    python tools/quarantine_manager.py assign --tool broken.py --agent Agent-1
    
    # Mark as fixed
    python tools/quarantine_manager.py mark-fixed --tool broken.py
    
    # Reintegrate
    python tools/quarantine_manager.py reintegrate --tool broken.py
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class QuarantineManager:
    """Manages broken tool quarantine and repair workflow"""
    
    def __init__(self, manifest_path: str = "BROKEN_TOOLS_MANIFEST.json"):
        self.manifest_path = Path(manifest_path)
        self.quarantine_root = Path("tools_quarantine")
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load quarantine manifest"""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        return {
            'audit_date': datetime.utcnow().isoformat() + 'Z',
            'quarantined_tools': [],
            'fixed_tools': [],
            'summary': {
                'total_quarantined': 0,
                'total_fixed': 0,
                'by_category': {}
            }
        }
    
    def _save_manifest(self):
        """Save manifest"""
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def quarantine_tool(
        self,
        tool_path: str,
        error_type: str,
        error_message: str,
        priority: str = "medium"
    ):
        """Move tool to quarantine"""
        source = Path(tool_path)
        
        if not source.exists():
            print(f"❌ Tool not found: {tool_path}")
            return False
        
        # Determine category directory
        category_map = {
            'syntax_error': 'syntax',
            'import_error': 'imports',
            'dependency_error': 'dependencies',
            'runtime_error': 'runtime',
            'config_error': 'config'
        }
        
        category = category_map.get(error_type, 'runtime')
        quarantine_dir = self.quarantine_root / category
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        # Move file
        dest = quarantine_dir / source.name
        shutil.move(str(source), str(dest))
        
        # Update manifest
        entry = {
            'original_path': str(source),
            'quarantine_path': str(dest),
            'error_type': error_type,
            'error_message': error_message,
            'priority': priority,
            'assigned_to': None,
            'status': 'quarantined',
            'quarantine_date': datetime.utcnow().isoformat() + 'Z',
            'fix_date': None
        }
        
        self.manifest['quarantined_tools'].append(entry)
        self.manifest['summary']['total_quarantined'] += 1
        self._save_manifest()
        
        print(f"✅ Quarantined: {source.name} → {category}/")
        return True
    
    def list_quarantined(
        self,
        assigned_to: Optional[str] = None,
        category: Optional[str] = None
    ):
        """List quarantined tools"""
        tools = self.manifest.get('quarantined_tools', [])
        
        if assigned_to:
            tools = [t for t in tools if t['assigned_to'] == assigned_to]
        
        if category:
            tools = [t for t in tools if t['error_type'] == category]
        
        print(f"\n📋 QUARANTINED TOOLS ({len(tools)} total)\n")
        print("="*70)
        
        for tool in tools:
            print(f"\n🔧 {Path(tool['original_path']).name}")
            print(f"   Category: {tool['error_type']}")
            print(f"   Error: {tool['error_message'][:60]}")
            print(f"   Priority: {tool['priority']}")
            print(f"   Assigned: {tool['assigned_to'] or 'UNASSIGNED'}")
            print(f"   Status: {tool['status']}")
    
    def assign_tool(self, tool_name: str, agent_id: str):
        """Assign quarantined tool to agent"""
        for tool in self.manifest['quarantined_tools']:
            if tool_name in tool['original_path']:
                tool['assigned_to'] = agent_id
                tool['status'] = 'assigned'
                self._save_manifest()
                print(f"✅ Assigned {tool_name} to {agent_id}")
                return True
        
        print(f"❌ Tool not found: {tool_name}")
        return False
    
    def mark_fixed(self, tool_name: str):
        """Mark tool as fixed"""
        for tool in self.manifest['quarantined_tools']:
            if tool_name in tool['original_path']:
                tool['status'] = 'fixed'
                tool['fix_date'] = datetime.utcnow().isoformat() + 'Z'
                
                # Move to summary
                self.manifest['fixed_tools'].append(tool)
                self.manifest['summary']['total_fixed'] += 1
                
                self._save_manifest()
                print(f"✅ Marked as fixed: {tool_name}")
                return True
        
        print(f"❌ Tool not found: {tool_name}")
        return False
    
    def reintegrate_tool(self, tool_name: str):
        """Move fixed tool back to original location"""
        for idx, tool in enumerate(self.manifest['quarantined_tools']):
            if tool_name in tool['original_path'] and tool['status'] == 'fixed':
                source = Path(tool['quarantine_path'])
                dest = Path(tool['original_path'])
                
                if source.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(dest))
                    
                    # Remove from quarantine list
                    self.manifest['quarantined_tools'].pop(idx)
                    self._save_manifest()
                    
                    print(f"✅ Reintegrated: {tool_name}")
                    return True
        
        print(f"❌ Tool not ready for reintegration: {tool_name}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Manage tool quarantine")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List quarantined tools')
    list_parser.add_argument('--assigned-to', help='Filter by agent')
    list_parser.add_argument('--category', help='Filter by error category')
    
    # Assign command
    assign_parser = subparsers.add_parser('assign', help='Assign tool to agent')
    assign_parser.add_argument('--tool', required=True, help='Tool name')
    assign_parser.add_argument('--agent', required=True, help='Agent ID')
    
    # Mark fixed
    fixed_parser = subparsers.add_parser('mark-fixed', help='Mark tool as fixed')
    fixed_parser.add_argument('--tool', required=True, help='Tool name')
    
    # Reintegrate
    reint_parser = subparsers.add_parser('reintegrate', help='Reintegrate fixed tool')
    reint_parser.add_argument('--tool', required=True, help='Tool name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = QuarantineManager()
    
    if args.command == 'list':
        manager.list_quarantined(
            assigned_to=args.assigned_to,
            category=args.category
        )
    elif args.command == 'assign':
        manager.assign_tool(args.tool, args.agent)
    elif args.command == 'mark-fixed':
        manager.mark_fixed(args.tool)
    elif args.command == 'reintegrate':
        manager.reintegrate_tool(args.tool)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

