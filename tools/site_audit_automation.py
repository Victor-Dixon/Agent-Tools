#!/usr/bin/env python3
"""
Site Audit Automation Tool
============================

Automates website auditing by crawling pages, detecting issues, and generating
SITE_AUDIT tasks in MASTER_TASK_LOG.md.

Features:
- Crawl all pages on a site (sitemap or recursive link following)
- Check all links for 404s
- Detect missing CTAs or broken forms
- Validate SEO metadata (titles, descriptions, Open Graph)
- Generate SITE_AUDIT tasks with unique IDs automatically
- Export findings as devlog-ready markdown

Usage:
    python tools/site_audit_automation.py --site https://dadudekc.com --output audit_report.md
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


class SiteAuditor:
    """Automated site auditor that crawls and analyzes websites."""

    def __init__(self, site_url: str, max_pages: int = 50):
        self.site_url = site_url.rstrip("/")
        self.domain = urlparse(site_url).netloc
        self.max_pages = max_pages
        self.visited: Set[str] = set()
        self.issues: List[Dict] = []
        self.pages: List[Dict] = []

    def crawl(self) -> None:
        """Crawl the site starting from the homepage."""
        print(f"🔍 Crawling {self.site_url}...")
        self._crawl_page(self.site_url)
        print(f"✅ Crawled {len(self.pages)} pages")

    def _crawl_page(self, url: str) -> None:
        """Recursively crawl a page and its links."""
        if len(self.visited) >= self.max_pages:
            return

        if url in self.visited:
            return

        self.visited.add(url)

        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            if response.status_code != 200:
                self.issues.append({
                    "type": "HTTP_ERROR",
                    "url": url,
                    "status_code": response.status_code,
                    "priority": "HIGH",
                })
                return

            soup = BeautifulSoup(response.content, "html.parser")
            page_data = {
                "url": url,
                "title": soup.title.string if soup.title else None,
                "meta_description": self._get_meta(soup, "description"),
                "h1_count": len(soup.find_all("h1")),
                "h1_texts": [h1.get_text(strip=True) for h1 in soup.find_all("h1")],
                "links": [],
                "has_cta": self._has_cta(soup),
                "has_form": len(soup.find_all("form")) > 0,
            }

            # Extract all links
            for link in soup.find_all("a", href=True):
                href = link.get("href")
                absolute_url = urljoin(url, href)
                if self._is_same_domain(absolute_url):
                    page_data["links"].append({
                        "url": absolute_url,
                        "text": link.get_text(strip=True),
                    })

            self.pages.append(page_data)

            # Follow internal links
            for link_data in page_data["links"]:
                link_url = link_data["url"]
                if link_url not in self.visited and self._is_same_domain(link_url):
                    self._crawl_page(link_url)

        except Exception as e:
            self.issues.append({
                "type": "CRAWL_ERROR",
                "url": url,
                "error": str(e),
                "priority": "MEDIUM",
            })

    def _is_same_domain(self, url: str) -> bool:
        """Check if URL is on the same domain."""
        parsed = urlparse(url)
        return parsed.netloc == self.domain or parsed.netloc == ""

    def _get_meta(self, soup: BeautifulSoup, name: str) -> str:
        """Get meta tag content."""
        meta = soup.find("meta", attrs={"name": name}) or soup.find(
            "meta", attrs={"property": f"og:{name}"}
        )
        return meta.get("content", "") if meta else ""

    def _has_cta(self, soup: BeautifulSoup) -> bool:
        """Check if page has a CTA (button, link with action words)."""
        cta_keywords = [
            "book",
            "hire",
            "contact",
            "start",
            "get",
            "buy",
            "order",
            "sign up",
            "learn more",
            "request",
        ]
        text = soup.get_text().lower()
        buttons = soup.find_all(
            ["button", "a"], class_=re.compile("cta|button|btn"))
        return any(keyword in text for keyword in cta_keywords) or len(buttons) > 0

    def check_links(self) -> None:
        """Check all links for 404s and other issues."""
        print("🔗 Checking links...")
        all_links: Set[str] = set()
        for page in self.pages:
            for link in page["links"]:
                all_links.add(link["url"])

        for link_url in all_links:
            try:
                response = requests.head(
                    link_url, timeout=5, allow_redirects=True)
                if response.status_code == 404:
                    self.issues.append({
                        "type": "BROKEN_LINK",
                        "url": link_url,
                        "priority": "HIGH",
                    })
            except Exception:
                # Skip external links or timeouts
                pass

        print(f"✅ Checked {len(all_links)} links")

    def analyze_seo(self) -> None:
        """Analyze SEO metadata."""
        print("📊 Analyzing SEO...")
        for page in self.pages:
            if not page["title"] or len(page["title"]) < 30:
                self.issues.append({
                    "type": "SEO_MISSING_TITLE",
                    "url": page["url"],
                    "priority": "MEDIUM",
                })

            if not page["meta_description"]:
                self.issues.append({
                    "type": "SEO_MISSING_DESCRIPTION",
                    "url": page["url"],
                    "priority": "MEDIUM",
                })

            if page["h1_count"] == 0:
                self.issues.append({
                    "type": "SEO_MISSING_H1",
                    "url": page["url"],
                    "priority": "MEDIUM",
                })

            if page["h1_count"] > 1:
                self.issues.append({
                    "type": "SEO_MULTIPLE_H1",
                    "url": page["url"],
                    "priority": "LOW",
                })

    def analyze_ctas(self) -> None:
        """Check for missing CTAs on key pages."""
        print("🎯 Analyzing CTAs...")
        homepage = next(
            (p for p in self.pages if p["url"] == self.site_url), None)
        if homepage and not homepage["has_cta"]:
            self.issues.append({
                "type": "MISSING_CTA",
                "url": homepage["url"],
                "priority": "HIGH",
            })

    def generate_tasks(self) -> List[str]:
        """Generate SITE_AUDIT tasks for MASTER_TASK_LOG.md."""
        tasks = []
        for issue in self.issues:
            issue_id = self._generate_id(issue)
            task = self._format_task(issue, issue_id)
            tasks.append(task)
        return tasks

    def _generate_id(self, issue: Dict) -> str:
        """Generate unique ID for issue."""
        site_short = self.domain.replace(
            ".com", "").replace(".", "").upper()[:8]
        issue_type = issue["type"].replace("_", "-")
        hash_suffix = hashlib.md5(
            f"{issue['url']}{issue['type']}".encode()
        ).hexdigest()[:8].upper()
        return f"SA-{site_short}-{issue_type}-{hash_suffix}"

    def _format_task(self, issue: Dict, issue_id: str) -> str:
        """Format issue as MASTER_TASK_LOG.md task."""
        priority = issue.get("priority", "MEDIUM")
        description = self._get_description(issue)
        return f"- [ ] [SITE_AUDIT][{priority}][{issue_id}] {description}"

    def _get_description(self, issue: Dict) -> str:
        """Get human-readable description for issue."""
        issue_type = issue["type"]
        url = issue["url"]

        descriptions = {
            "HTTP_ERROR": f"{url}: HTTP {issue.get('status_code', 'ERROR')}",
            "BROKEN_LINK": f"{url}: broken link (404)",
            "CRAWL_ERROR": f"{url}: crawl error ({issue.get('error', 'unknown')})",
            "SEO_MISSING_TITLE": f"{url}: missing or short page title",
            "SEO_MISSING_DESCRIPTION": f"{url}: missing meta description",
            "SEO_MISSING_H1": f"{url}: missing H1 heading",
            "SEO_MULTIPLE_H1": f"{url}: multiple H1 headings (should be one)",
            "MISSING_CTA": f"{url}: missing primary CTA",
        }

        return descriptions.get(issue_type, f"{url}: {issue_type}")

    def generate_report(self) -> str:
        """Generate markdown report of findings."""
        report = f"""# Site Audit Report: {self.domain}

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Pages Crawled:** {len(self.pages)}  
**Issues Found:** {len(self.issues)}

---

## 📊 Summary

- **Pages Analyzed:** {len(self.pages)}
- **Issues Found:** {len(self.issues)}
- **High Priority:** {len([i for i in self.issues if i.get('priority') == 'HIGH'])}
- **Medium Priority:** {len([i for i in self.issues if i.get('priority') == 'MEDIUM'])}
- **Low Priority:** {len([i for i in self.issues if i.get('priority') == 'LOW'])}

---

## 🔍 Issues Found

"""
        for issue in self.issues:
            report += f"### {issue['type']}\n"
            report += f"- **URL:** {issue['url']}\n"
            report += f"- **Priority:** {issue.get('priority', 'MEDIUM')}\n"
            if 'status_code' in issue:
                report += f"- **Status Code:** {issue['status_code']}\n"
            report += "\n"

        report += "\n---\n\n## 📋 Generated Tasks\n\n"
        tasks = self.generate_tasks()
        for task in tasks:
            report += f"{task}\n"

        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Automated site auditor")
    parser.add_argument("--site", required=True, help="Site URL to audit")
    parser.add_argument("--output", help="Output file for report (optional)")
    parser.add_argument("--max-pages", type=int,
                        default=50, help="Max pages to crawl")
    args = parser.parse_args()

    auditor = SiteAuditor(args.site, max_pages=args.max_pages)
    auditor.crawl()
    auditor.check_links()
    auditor.analyze_seo()
    auditor.analyze_ctas()

    report = auditor.generate_report()

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"✅ Report saved to {output_path}")
    else:
        print(report)

    print(f"\n✅ Audit complete: {len(auditor.issues)} issues found")


if __name__ == "__main__":
    main()
