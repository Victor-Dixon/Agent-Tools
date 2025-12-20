#!/usr/bin/env python3
"""
Repository Analysis Completion Enforcer
Agent-8 (QA & Autonomous Systems Specialist)

Purpose: Prevent running out of gas mid-mission
Ensures ALL repos analyzed before mission marked complete
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

TRACKER_FILE = Path("agent_workspaces/Agent-8/REPO_ANALYSIS_TRACKER.json")

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def load_tracker() -> Dict:
    """Load the tracker file"""
    if not TRACKER_FILE.exists():
        print(f"{Colors.RED}❌ Tracker file not found!{Colors.END}")
        return None
    return json.loads(TRACKER_FILE.read_text())


def save_tracker(tracker: Dict):
    """Save tracker file"""
    TRACKER_FILE.write_text(json.dumps(tracker, indent=2))


def show_status():
    """Show current mission status"""
    tracker = load_tracker()
    if not tracker:
        return
    
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}")
    print(f"🎯 REPO ANALYSIS MISSION STATUS")
    print(f"{'='*70}{Colors.END}\n")
    
    print(f"Agent: {tracker['agent']}")
    print(f"Assignment: {tracker['assignment']}")
    print(f"Current Cycle: {tracker['current_cycle']}")
    print(f"Deadline: {tracker['deadline_cycle']}")
    
    progress = tracker['progress']
    print(f"\n{Colors.BOLD}Progress:{Colors.END}")
    print(f"  Completed: {Colors.GREEN}{progress['completed']}/10{Colors.END}")
    print(f"  In Progress: {Colors.YELLOW}{progress['in_progress']}{Colors.END}")
    print(f"  Not Started: {Colors.RED}{progress['not_started']}{Colors.END}")
    print(f"  Completion: {Colors.GREEN}{progress['completion_percentage']}%{Colors.END}")
    
    print(f"\n{Colors.BOLD}Repos:{Colors.END}")
    for repo in tracker['repos']:
        status_icon = {
            'COMPLETE': f'{Colors.GREEN}✅{Colors.END}',
            'IN_PROGRESS': f'{Colors.YELLOW}⏳{Colors.END}',
            'NOT_STARTED': f'{Colors.RED}❌{Colors.END}'
        }.get(repo['status'], '❓')
        
        critical = ' 🚨 CRITICAL!' if repo.get('critical') else ''
        devlog = ' (devlog posted)' if repo.get('devlog_posted') else ''
        
        print(f"  {status_icon} Repo {repo['id']}/10: {repo['name']}{critical}{devlog}")
    
    print(f"\n{Colors.BOLD}Next Action:{Colors.END}")
    next_repo = next((r for r in tracker['repos'] if r['status'] == 'NOT_STARTED'), None)
    if next_repo:
        print(f"  🚀 Analyze: {next_repo['name']}")
        print(f"  📋 Gas file: {next_repo['gas_file']}")
        print(f"  💪 Progress after: {next_repo['id']}/10 = {next_repo['id']*10}%")
    else:
        in_progress = [r for r in tracker['repos'] if r['status'] == 'IN_PROGRESS']
        if in_progress:
            print(f"  ⏳ Complete: {in_progress[0]['name']}")
        else:
            print(f"  🎉 ALL REPOS COMPLETE!")


def get_next_repo() -> Optional[Dict]:
    """Get next repo that needs analysis (ENFORCED)"""
    tracker = load_tracker()
    if not tracker:
        return None
    
    # Find first repo that's NOT complete
    for repo in tracker['repos']:
        if repo['status'] != 'COMPLETE':
            return repo
    
    return None


def mark_started(repo_id: int):
    """Mark repo as started"""
    tracker = load_tracker()
    if not tracker:
        return
    
    for repo in tracker['repos']:
        if repo['id'] == repo_id:
            repo['status'] = 'IN_PROGRESS'
            repo['analysis_started'] = datetime.now().isoformat()
            repo['gas_delivered'] = True
            
            # Update progress
            tracker['progress']['in_progress'] = sum(1 for r in tracker['repos'] if r['status'] == 'IN_PROGRESS')
            tracker['progress']['not_started'] = sum(1 for r in tracker['repos'] if r['status'] == 'NOT_STARTED')
            
            save_tracker(tracker)
            print(f"{Colors.GREEN}✅ Repo {repo_id} marked as STARTED: {repo['name']}{Colors.END}")
            print(f"{Colors.BLUE}📋 Gas file: {repo['gas_file']}{Colors.END}")
            return
    
    print(f"{Colors.RED}❌ Repo ID {repo_id} not found!{Colors.END}")


def mark_complete(repo_id: int, devlog_url: str = None):
    """Mark repo as complete (REQUIRES devlog URL!)"""
    tracker = load_tracker()
    if not tracker:
        return
    
    for repo in tracker['repos']:
        if repo['id'] == repo_id:
            if repo['status'] != 'IN_PROGRESS':
                print(f"{Colors.RED}❌ Cannot mark complete - repo not started!{Colors.END}")
                print(f"{Colors.YELLOW}⚠️  Use --start {repo_id} first{Colors.END}")
                return
            
            if not devlog_url:
                print(f"{Colors.RED}❌ Cannot mark complete - devlog URL required!{Colors.END}")
                print(f"{Colors.YELLOW}⚠️  Use --complete {repo_id} --devlog <url>{Colors.END}")
                return
            
            repo['status'] = 'COMPLETE'
            repo['analysis_completed'] = datetime.now().isoformat()
            repo['devlog_posted'] = True
            repo['devlog_url'] = devlog_url
            repo['checkpoint_passed'] = True
            
            # Update progress
            tracker['progress']['completed'] = sum(1 for r in tracker['repos'] if r['status'] == 'COMPLETE')
            tracker['progress']['in_progress'] = sum(1 for r in tracker['repos'] if r['status'] == 'IN_PROGRESS')
            tracker['progress']['not_started'] = sum(1 for r in tracker['repos'] if r['status'] == 'NOT_STARTED')
            tracker['progress']['completion_percentage'] = (tracker['progress']['completed'] / tracker['total_repos']) * 100
            
            save_tracker(tracker)
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ REPO {repo_id} COMPLETE!{Colors.END}")
            print(f"{Colors.GREEN}   {repo['name']}{Colors.END}")
            print(f"{Colors.GREEN}   Devlog: {devlog_url}{Colors.END}")
            print(f"\n{Colors.BOLD}Progress: {tracker['progress']['completed']}/10 = {tracker['progress']['completion_percentage']}%{Colors.END}\n")
            
            # Check if ALL complete
            if tracker['progress']['completed'] == 10:
                print(f"{Colors.GREEN}{Colors.BOLD}🎉🎉🎉 MISSION COMPLETE! ALL 10 REPOS ANALYZED! 🎉🎉🎉{Colors.END}\n")
                tracker['status'] = 'COMPLETE'
                save_tracker(tracker)
            else:
                next_repo = get_next_repo()
                if next_repo:
                    print(f"{Colors.BLUE}🚀 NEXT: Repo {next_repo['id']} - {next_repo['name']}{Colors.END}")
                    print(f"{Colors.BLUE}📋 Gas: {next_repo['gas_file']}{Colors.END}\n")
            return
    
    print(f"{Colors.RED}❌ Repo ID {repo_id} not found!{Colors.END}")


def check_can_proceed() -> bool:
    """Check if can proceed or if blocked by incomplete repos"""
    tracker = load_tracker()
    if not tracker:
        return False
    
    incomplete = [r for r in tracker['repos'] if r['status'] != 'COMPLETE']
    
    if not incomplete:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL REPOS COMPLETE! MISSION ACCOMPLISHED!{Colors.END}\n")
        return True
    
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  INCOMPLETE REPOS DETECTED!{Colors.END}\n")
    print(f"{Colors.RED}Cannot proceed until ALL repos analyzed:{Colors.END}\n")
    
    for repo in incomplete:
        print(f"  ❌ Repo {repo['id']}/10: {repo['name']}")
        print(f"     Status: {repo['status']}")
        print(f"     Gas: {repo['gas_file']}")
        if repo.get('critical'):
            print(f"     {Colors.RED}🚨 CRITICAL REPO!{Colors.END}")
        print()
    
    print(f"{Colors.BOLD}ENFORCEMENT: Must complete {len(incomplete)} repos before mission ends!{Colors.END}\n")
    return False


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Repo Analysis Completion Enforcer")
    parser.add_argument('--status', action='store_true', help='Show mission status')
    parser.add_argument('--next', action='store_true', help='Get next repo to analyze')
    parser.add_argument('--start', type=int, metavar='REPO_ID', help='Mark repo as started')
    parser.add_argument('--complete', type=int, metavar='REPO_ID', help='Mark repo as complete')
    parser.add_argument('--devlog', type=str, metavar='URL', help='Discord devlog URL (required with --complete)')
    parser.add_argument('--check', action='store_true', help='Check if can proceed (enforcement)')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.next:
        next_repo = get_next_repo()
        if next_repo:
            print(f"\n{Colors.BLUE}{Colors.BOLD}🚀 NEXT REPO TO ANALYZE:{Colors.END}")
            print(f"  Repo {next_repo['id']}/10: {next_repo['name']}")
            print(f"  Gas file: {next_repo['gas_file']}")
            if next_repo.get('critical'):
                print(f"  {Colors.RED}🚨 CRITICAL ANALYSIS REQUIRED!{Colors.END}")
            print()
        else:
            print(f"\n{Colors.GREEN}🎉 ALL REPOS COMPLETE!{Colors.END}\n")
    elif args.start:
        mark_started(args.start)
    elif args.complete:
        mark_complete(args.complete, args.devlog)
    elif args.check:
        check_can_proceed()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()


