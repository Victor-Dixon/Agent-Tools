#!/usr/bin/env python3
"""
Comprehensive Website Audit Tool
=================================

Audits all configured WordPress websites for:
- SFTP connectivity and credentials
- Theme status and activation
- Site accessibility and responsiveness
- Content and functionality verification

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <300 lines
"""

import json
import logging
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveWebsiteAuditor:
    """Comprehensive auditor for all configured websites."""

    def __init__(self):
        self.sites_config = self._load_sites_config()
        self.audit_results = {}

    def _load_sites_config(self) -> Dict:
        """Load site configurations from sites.json."""
        config_file = Path("D:/Agent_Cellphone_V2_Repository/.deploy_credentials/sites.json")
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return {}

    def audit_all_sites(self) -> Dict:
        """Audit all configured websites comprehensively."""
        logger.info("🔍 Starting comprehensive website audit...")

        sites_to_audit = [
            "freerideinvestor",
            "prismblossom.online",
            "southwestsecret.com",
            "weareswarm.online",
            "weareswarm.site",
            "tradingrobotplug.com",
            "ariajet.site"
        ]

        for site_key in sites_to_audit:
            if site_key in self.sites_config:
                logger.info(f"📊 Auditing {site_key}...")
                self.audit_results[site_key] = self._audit_single_site(site_key)
            else:
                logger.warning(f"⚠️  Site {site_key} not found in configuration")
                self.audit_results[site_key] = {
                    "status": "NOT_CONFIGURED",
                    "error": "Site not found in sites.json"
                }

        return self.audit_results

    def _audit_single_site(self, site_key: str) -> Dict:
        """Audit a single website comprehensively."""
        result = {
            "site_key": site_key,
            "status": "UNKNOWN",
            "connectivity": {},
            "theme_status": {},
            "site_accessibility": {},
            "content_check": {},
            "issues": [],
            "recommendations": []
        }

        config = self.sites_config.get(site_key)
        if not config:
            result["status"] = "CONFIG_ERROR"
            result["issues"].append("Site configuration missing")
            return result

        # 1. Test SFTP connectivity
        result["connectivity"] = self._test_sftp_connectivity(config)

        # 2. Check theme status
        result["theme_status"] = self._check_theme_status(site_key, config)

        # 3. Test site accessibility
        result["site_accessibility"] = self._test_site_accessibility(site_key)

        # 4. Content verification
        result["content_check"] = self._verify_content(site_key)

        # Determine overall status
        result["status"] = self._determine_overall_status(result)

        # Generate recommendations
        result["recommendations"] = self._generate_recommendations(result)

        return result

    def _test_sftp_connectivity(self, config: Dict) -> Dict:
        """Test SFTP connectivity for deployment."""
        try:
            import paramiko

            host = config.get("host")
            port = config.get("port", 65002)
            username = config.get("username")
            password = config.get("password")

            if not all([host, username, password]):
                return {"status": "FAILED", "error": "Missing credentials"}

            transport = paramiko.Transport((host, port))
            transport.banner_timeout = 10
            transport.connect(username=username, password=password)

            sftp = paramiko.SFTPClient.from_transport(transport)

            # Test basic operations
            try:
                sftp.listdir('.')
                connectivity_status = "SUCCESS"
                error = None
            except Exception as e:
                connectivity_status = "PARTIAL"
                error = f"Directory listing failed: {str(e)}"

            sftp.close()
            transport.close()

            return {
                "status": connectivity_status,
                "host": host,
                "port": port,
                "username": username,
                "error": error
            }

        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def _check_theme_status(self, site_key: str, config: Dict) -> Dict:
        """Check theme status and activation."""
        # This would require wordpress_manager integration
        # For now, return basic info
        return {
            "configured_theme": config.get("remote_path", "").split("/")[-1],
            "remote_path": config.get("remote_path"),
            "status": "NEEDS_VERIFICATION"
        }

    def _test_site_accessibility(self, site_key: str) -> Dict:
        """Test if the website is accessible."""
        # Construct URL
        if site_key == "freerideinvestor":
            url = "https://freerideinvestor.com"
        elif site_key == "prismblossom.online":
            url = "https://prismblossom.online"
        elif site_key == "southwestsecret.com":
            url = "https://southwestsecret.com"
        elif site_key == "weareswarm.online":
            url = "https://weareswarm.online"
        elif site_key == "weareswarm.site":
            url = "https://weareswarm.site"
        elif site_key == "tradingrobotplug.com":
            url = "https://tradingrobotplug.com"
        elif site_key == "ariajet.site":
            url = "https://ariajet.site"
        else:
            return {"status": "UNKNOWN", "url": None, "error": "Unknown site"}

        try:
            response = requests.get(url, timeout=10, verify=False)
            return {
                "status": "SUCCESS" if response.status_code == 200 else "HTTP_ERROR",
                "url": url,
                "http_status": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {"status": "FAILED", "url": url, "error": str(e)}

    def _verify_content(self, site_key: str) -> Dict:
        """Verify site content and functionality."""
        # Basic content checks
        return {
            "content_type": "NEEDS_MANUAL_VERIFICATION",
            "theme_active": "NEEDS_VERIFICATION",
            "functionality": "NEEDS_TESTING"
        }

    def _determine_overall_status(self, result: Dict) -> str:
        """Determine overall site status."""
        if result["connectivity"].get("status") == "FAILED":
            return "CONNECTIVITY_ISSUES"
        elif result["site_accessibility"].get("status") == "FAILED":
            return "ACCESSIBILITY_ISSUES"
        elif result["connectivity"].get("status") == "SUCCESS" and result["site_accessibility"].get("status") == "SUCCESS":
            return "OPERATIONAL"
        else:
            return "NEEDS_ATTENTION"

    def _generate_recommendations(self, result: Dict) -> List[str]:
        """Generate recommendations based on audit results."""
        recommendations = []

        if result["connectivity"].get("status") == "FAILED":
            recommendations.append("Fix SFTP credentials and connectivity")

        if result["site_accessibility"].get("status") == "FAILED":
            recommendations.append("Investigate site accessibility issues")

        if result["theme_status"].get("status") == "NEEDS_VERIFICATION":
            recommendations.append("Verify theme activation and deployment")

        if result["content_check"].get("content_type") == "NEEDS_MANUAL_VERIFICATION":
            recommendations.append("Perform manual content and functionality verification")

        if not recommendations:
            recommendations.append("Site appears operational - monitor regularly")

        return recommendations

    def generate_audit_report(self) -> str:
        """Generate comprehensive audit report."""
        report = ["# 🔍 Comprehensive Website Audit Report", ""]
        report.append(f"**Audit Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Sites Audited**: {len(self.audit_results)}")
        report.append("")

        # Summary stats
        operational = sum(1 for r in self.audit_results.values() if r.get("status") == "OPERATIONAL")
        issues = sum(1 for r in self.audit_results.values() if r.get("status") not in ["OPERATIONAL", "UNKNOWN"])

        report.append("## 📊 Audit Summary")
        report.append(f"- ✅ **Operational**: {operational} sites")
        report.append(f"- ⚠️  **Issues Found**: {issues} sites")
        report.append("")

        # Detailed results
        for site_key, result in self.audit_results.items():
            report.append(f"## 🌐 {site_key}")
            report.append(f"**Status**: {result.get('status', 'UNKNOWN')}")

            # Connectivity
            conn = result.get("connectivity", {})
            report.append(f"**SFTP**: {conn.get('status', 'UNKNOWN')}")

            # Accessibility
            access = result.get("site_accessibility", {})
            if access.get("url"):
                report.append(f"**URL**: {access['url']}")
                report.append(f"**HTTP Status**: {access.get('http_status', 'UNKNOWN')}")

            # Issues
            if result.get("issues"):
                report.append("**Issues**:")
                for issue in result["issues"]:
                    report.append(f"  - {issue}")

            # Recommendations
            if result.get("recommendations"):
                report.append("**Recommendations**:")
                for rec in result["recommendations"]:
                    report.append(f"  - {rec}")

            report.append("")

        return "\n".join(report)

    def save_report(self, filename: str = None):
        """Save audit report to file."""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"WEBSITE_AUDIT_COMPREHENSIVE_{timestamp}.md"

        report_path = Path("D:/Agent_Cellphone_V2_Repository") / filename
        with open(report_path, 'w') as f:
            f.write(self.generate_audit_report())

        logger.info(f"📄 Report saved to: {report_path}")
        return report_path


def main():
    """Main audit execution."""
    auditor = ComprehensiveWebsiteAuditor()

    # Run comprehensive audit
    results = auditor.audit_all_sites()

    # Generate and save report
    report_path = auditor.save_report()

    # Print summary
    print("\n" + "="*60)
    print("🔍 WEBSITE AUDIT COMPLETE")
    print("="*60)
    print(f"📄 Report saved: {report_path}")
    print(f"📊 Sites audited: {len(results)}")

    operational = sum(1 for r in results.values() if r.get("status") == "OPERATIONAL")
    print(f"✅ Operational: {operational}")
    print(f"⚠️  Needs attention: {len(results) - operational}")

    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()
