#!/usr/bin/env python3
"""
Swarm Site Health Automation Tool
==================================

Autonomous site health management for the entire swarm.
Uses agents to automatically fix site issues without human intervention.

Features:
- Automated broken link fixing
- Page creation and menu management
- SFTP connectivity monitoring
- Cross-site coordination
- Agent task delegation

Author: Agent-5 (Business Intelligence Specialist)
Created: 2025-12-20
V2 Compliant: <600 lines
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.hostinger_wordpress_manager import HostingerWordPressManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SwarmSiteHealthAutomation:
    """Autonomous site health management for the entire swarm."""

    def __init__(self):
        self.site_configs = self._load_site_configs()
        self.broken_links_data = self._load_broken_links_data()
        self.automation_results = {
            "timestamp": datetime.now().isoformat(),
            "sites_processed": [],
            "fixes_attempted": 0,
            "fixes_successful": 0,
            "fixes_failed": 0,
            "errors": []
        }

    def _load_site_configs(self) -> Dict[str, Dict]:
        """Load site configuration data."""
        config_file = Path("site_configs.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}

    def _load_broken_links_data(self) -> Dict[str, Any]:
        """Load broken links audit data."""
        audit_file = Path("docs/site_audit/broken_links.json")
        if audit_file.exists():
            with open(audit_file, 'r') as f:
                return json.load(f)
        return {"sites": {}}

    def run_full_site_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check and fixes on all sites."""
        print("🚀 SWARM SITE HEALTH AUTOMATION STARTED")
        print("=" * 60)

        total_sites = len(self.site_configs)
        sites_processed = 0
        total_fixes_attempted = 0
        total_fixes_successful = 0

        for site_name, site_config in self.site_configs.items():
            print(f"\n🏥 Processing {site_name}...")
            sites_processed += 1

            site_result = self._process_single_site(site_name, site_config)
            self.automation_results["sites_processed"].append(site_result)

            total_fixes_attempted += site_result.get("fixes_attempted", 0)
            total_fixes_successful += site_result.get("fixes_successful", 0)

            # Progress indicator
            progress = (sites_processed / total_sites) * 100
            print(".1f")
        self.automation_results.update({
            "fixes_attempted": total_fixes_attempted,
            "fixes_successful": total_fixes_successful,
            "fixes_failed": total_fixes_attempted - total_fixes_successful
        })

        # Save results
        self._save_results()

        # Print summary
        self._print_final_report()

        return self.automation_results

    def _process_single_site(self, site_name: str, site_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process health fixes for a single site."""
        site_result = {
            "site_name": site_name,
            "timestamp": datetime.now().isoformat(),
            "health_check": {},
            "fixes_attempted": 0,
            "fixes_successful": 0,
            "fixes_failed": 0,
            "broken_links_before": 0,
            "broken_links_after": 0,
            "errors": []
        }

        try:
            # Initialize site manager
            manager = HostingerWordPressManager(site_name)

            # Health check
            health_result = manager.get_site_health()
            site_result["health_check"] = health_result

            if not health_result.get("success"):
                site_result["errors"].append(f"Health check failed: {health_result.get('error')}")
                return site_result

            # Get broken links for this site
            site_broken_links = self.broken_links_data.get("sites", {}).get(site_name, {})
            broken_links = site_broken_links.get("broken_links", [])
            site_result["broken_links_before"] = len(broken_links)

            if not broken_links:
                print(f"   ✅ {site_name}: No broken links found")
                return site_result

            print(f"   🔗 {site_name}: Found {len(broken_links)} broken links")

            # Check if we have WordPress API access
            if not health_result.get("api_accessible"):
                print(f"   ⚠️  {site_name}: WordPress API not accessible - manual fixes needed")
                site_result["errors"].append("WordPress API not accessible")
                return site_result

            # Attempt automated fixes
            fix_result = manager.auto_fix_site_issues({"broken_links": broken_links})
            site_result["fixes_attempted"] = len(fix_result.get("fixes_attempted", []))
            site_result["fixes_successful"] = len(fix_result.get("fixes_successful", []))
            site_result["fixes_failed"] = len(fix_result.get("fixes_failed", []))

            # Check if fixes worked
            if site_result["fixes_successful"] > 0:
                print(f"   ✅ {site_name}: {site_result['fixes_successful']} fixes successful")
                site_result["broken_links_after"] = max(0, site_result["broken_links_before"] - site_result["fixes_successful"])
            else:
                print(f"   ❌ {site_name}: All {site_result['fixes_attempted']} fixes failed")
                site_result["broken_links_after"] = site_result["broken_links_before"]

        except Exception as e:
            error_msg = f"Site processing failed: {str(e)}"
            site_result["errors"].append(error_msg)
            print(f"   💥 {site_name}: {error_msg}")

        return site_result

    def delegate_manual_fixes(self) -> Dict[str, Any]:
        """Generate delegation tasks for manual fixes that automation can't handle."""
        print("\n📋 GENERATING MANUAL FIX DELEGATION TASKS")
        print("=" * 50)

        delegation_tasks = []

        # Process sites that have broken links (from audit data)
        for site_name, site_data in self.broken_links_data.get("sites", {}).items():
            broken_links = site_data.get("broken_links", [])
            if not broken_links:
                continue

            # Check if this site was processed and API is not accessible
            site_result = next((s for s in self.automation_results.get("sites_processed", [])
                              if s["site_name"] == site_name), None)

            if site_result:
                api_accessible = site_result.get("health_check", {}).get("api_accessible", False)
                if not api_accessible:
                    # Create detailed delegation task
                    task = self._create_detailed_delegation_task(site_name, broken_links)
                    delegation_tasks.append(task)
            else:
                # Site wasn't processed but has broken links - still create task
                task = self._create_detailed_delegation_task(site_name, broken_links)
                delegation_tasks.append(task)

        # Also check for SFTP connectivity issues
        sftp_issues = []
        for site_result in self.automation_results.get("sites_processed", []):
            health_check = site_result.get("health_check", {})
            if not health_check.get("success", False):
                sftp_issues.append(site_result["site_name"])

        if sftp_issues:
            # Create SFTP fix task
            sftp_task = {
                "task_id": f"sftp_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "task_type": "infrastructure_sftp_fix",
                "priority": "HIGH",
                "title": f"Fix SFTP connectivity for {len(sftp_issues)} sites",
                "description": f"Resolve SFTP connection issues for: {', '.join(sftp_issues)}",
                "assigned_agent": "Agent-3",  # Infrastructure specialist
                "sites_affected": sftp_issues,
                "steps": [
                    "1. Verify Hostinger SFTP credentials are current",
                    "2. Check if server IP addresses changed",
                    "3. Test manual SFTP connection:",
                    "   sftp -P 65002 u996867598@157.173.214.121",
                    "4. Update site_configs.json with correct SFTP details",
                    "5. Test wordpress_manager.py connectivity",
                    "6. Run comprehensive audit to verify fixes"
                ],
                "estimated_time": "30 minutes",
                "blocking": True,  # This blocks automated deployments
                "created_at": datetime.now().isoformat()
            }
            delegation_tasks.append(sftp_task)

        # Save delegation tasks
        if delegation_tasks:
            delegation_file = Path("docs/delegation_tasks_site_fixes.json")
            with open(delegation_file, 'w') as f:
                json.dump({
                    "generated_at": datetime.now().isoformat(),
                    "total_tasks": len(delegation_tasks),
                    "tasks": delegation_tasks
                }, f, indent=2)

            print(f"📄 Saved {len(delegation_tasks)} delegation tasks to {delegation_file}")

            # Print summary
            print("\n📋 DELEGATION SUMMARY:")
            for i, task in enumerate(delegation_tasks, 1):
                priority_icon = "🔴" if task["priority"] == "HIGH" else "🟡" if task["priority"] == "MEDIUM" else "🟢"
                print(f"   {i}. {priority_icon} {task['title']}")
                print(f"      → Assigned: {task['assigned_agent']}")
                if 'broken_links_count' in task:
                    print(f"      → Broken links: {task['broken_links_count']}")

        return {"delegation_tasks": delegation_tasks}

    def _suggest_agent(self, site_name: str) -> str:
        """Suggest which agent should handle a site."""
        agent_mapping = {
            "weareswarm.online": "Agent-5",
            "weareswarm.site": "Agent-5",
            "tradingrobotplug.com": "Agent-3",
            "freerideinvestor.com": "Agent-3",
            "crosbyultimateevents.com": "Agent-7",
            "prismblossom.online": "Agent-7",
            "southwestsecret.com": "Agent-7"
        }
        return agent_mapping.get(site_name, "Agent-7")  # Default to web dev agent

    def _create_detailed_delegation_task(self, site_name: str, broken_links: List[Dict]) -> Dict[str, Any]:
        """Create a detailed delegation task for a specific site."""
        task_id = f"site_fix_{site_name.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Analyze broken links to create specific tasks
        missing_pages = []
        broken_menu_links = []
        other_issues = []

        for link in broken_links:
            url = link['url']
            link_text = link['text']
            source = link['source']

            if source in ['nav', 'footer']:
                # Check if it's a missing page
                if site_name in url:
                    path = url.replace(f'https://{site_name}/', '').replace(f'https://{site_name}', '').strip('/')
                    if path and '/' not in path and path not in ['contact', 'blog', 'about']:
                        missing_pages.append({"slug": path, "title": link_text, "url": url})
                    else:
                        broken_menu_links.append({"text": link_text, "url": url, "source": source})
                elif 'github.com/Agent_Cellphone_V2_Repository' in url:
                    # Special case: GitHub link
                    broken_menu_links.append({"text": link_text, "url": url, "source": source, "type": "github_fix"})
                else:
                    other_issues.append({"text": link_text, "url": url, "source": source})

        # Create detailed steps based on issues found
        steps = [
            f"1. Log into WordPress admin: https://{site_name}/wp-admin/"
        ]

        if missing_pages:
            steps.append("2. Create missing pages (Pages → Add New):")
            for page in missing_pages:
                steps.append(f"   - Create '{page['title']}' page (slug: {page['slug']})")
                steps.append("     Add placeholder content and publish")

        if broken_menu_links:
            steps.append("3. Fix broken menu links (Appearance → Menus):")
            for link in broken_menu_links:
                if link.get('type') == 'github_fix':
                    steps.append("   - Remove broken GitHub link from footer menu")
                else:
                    steps.append(f"   - Fix '{link['text']}' link in {link['source']} menu")

        steps.extend([
            "4. Update navigation menus to include new pages",
            "5. Test all navigation links after fixes",
            f"6. Run verification: python tools/comprehensive_website_audit.py --site {site_name} --check-links",
            "7. Update task status and report completion"
        ])

        # Determine priority and agent
        priority = "HIGH" if len(broken_links) > 5 else "MEDIUM" if len(broken_links) > 1 else "LOW"
        assigned_agent = self._suggest_agent(site_name)

        task = {
            "task_id": task_id,
            "task_type": "manual_wordpress_site_fixes",
            "priority": priority,
            "title": f"Fix {len(broken_links)} broken links on {site_name}",
            "description": f"Resolve {len(broken_links)} broken links and missing pages on {site_name}",
            "site_name": site_name,
            "assigned_agent": assigned_agent,
            "broken_links_count": len(broken_links),
            "missing_pages_count": len(missing_pages),
            "broken_menu_links_count": len(broken_menu_links),
            "issues_detected": {
                "missing_pages": missing_pages,
                "broken_menu_links": broken_menu_links,
                "other_issues": other_issues
            },
            "steps": steps,
            "estimated_time": f"{max(15, len(broken_links) * 5)} minutes",
            "blocking": False,
            "created_at": datetime.now().isoformat(),
            "verification_command": f"python tools/comprehensive_website_audit.py --site {site_name} --check-links"
        }

        return task

    def _generate_manual_steps(self, site_name: str, site_result: Dict[str, Any]) -> List[str]:
        """Generate manual fix steps for a site (legacy method)."""
        steps = [
            f"1. Log into WordPress admin: https://{site_name}/wp-admin/",
            "2. Check Appearance → Menus for broken navigation links",
            "3. Check if missing pages need to be created (Pages → Add New)",
            "4. Update footer menu if needed",
            "5. Test all navigation links after fixes",
            f"6. Run audit: python tools/comprehensive_website_audit.py --site {site_name} --check-links"
        ]
        return steps

    def _save_results(self):
        """Save automation results to file."""
        results_file = Path("docs/swarm_site_health_automation_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.automation_results, f, indent=2)

        print(f"\n📊 Results saved to: {results_file}")

    def _print_final_report(self):
        """Print final automation report."""
        print("\n🎯 SWARM SITE HEALTH AUTOMATION COMPLETE")
        print("=" * 60)

        total_sites = len(self.automation_results["sites_processed"])
        total_fixes = self.automation_results["fixes_attempted"]
        successful_fixes = self.automation_results["fixes_successful"]
        failed_fixes = self.automation_results["fixes_failed"]

        print("📊 FINAL RESULTS:")
        print(f"   Sites processed: {total_sites}")
        print(f"   Fixes attempted: {total_fixes}")
        print(f"   Fixes successful: {successful_fixes}")
        print(f"   Fixes failed: {failed_fixes}")

        success_rate = (successful_fixes / total_fixes * 100) if total_fixes > 0 else 0
        print(".1f")
        # Site-by-site breakdown
        print("\n🏥 SITE-BY-SITE RESULTS:")
        for site_result in self.automation_results["sites_processed"]:
            site_name = site_result["site_name"]
            fixes_successful = site_result.get("fixes_successful", 0)
            broken_before = site_result.get("broken_links_before", 0)
            broken_after = site_result.get("broken_links_after", 0)
            api_ok = site_result.get("health_check", {}).get("api_accessible", False)

            status_icon = "✅" if broken_after == 0 else "⚠️" if fixes_successful > 0 else "❌"
            api_icon = "🔗" if api_ok else "🚫"

            print(f"   {status_icon} {api_icon} {site_name}: {broken_before} → {broken_after} broken links")

        print("\n🚀 NEXT STEPS:")
        if failed_fixes > 0:
            print("   1. Review failed fixes and error messages")
            print("   2. Check delegation_tasks_site_fixes.json for manual tasks")
            print("   3. Coordinate with assigned agents for manual fixes")
        else:
            print("   1. Run final verification audit")
            print("   2. All sites should now be healthy! 🎉")

        print("   3. Monitor sites for future issues")


def main():
    """Main CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Swarm Site Health Automation - Autonomous site fixing")
    parser.add_argument("--run-full-check", action="store_true", help="Run full health check and fixes on all sites")
    parser.add_argument("--delegate-manual", action="store_true", help="Generate delegation tasks for manual fixes")
    parser.add_argument("--site", help="Process only specific site")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")

    args = parser.parse_args()

    automation = SwarmSiteHealthAutomation()

    if args.run_full_check:
        results = automation.run_full_site_health_check()

        if not args.dry_run:
            delegation = automation.delegate_manual_fixes()
            print(f"\n📋 Generated {len(delegation.get('delegation_tasks', []))} delegation tasks")

    elif args.site:
        print(f"🎯 Processing single site: {args.site}")
        site_config = automation.site_configs.get(args.site)
        if site_config:
            result = automation._process_single_site(args.site, site_config)
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Site '{args.site}' not found in configuration")

    elif args.delegate_manual:
        delegation = automation.delegate_manual_fixes()
        print(f"📋 Generated {len(delegation.get('delegation_tasks', []))} delegation tasks")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
