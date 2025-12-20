#!/usr/bin/env python3
"""
Nightly Site Audit Tool
=======================

Runs a lightweight QA audit across all configured sites and generates:
- docs/site_audit/broken_links.json  (nav/footer/CTA link issues)
- docs/site_audit/forms_test.json    (form/checkout submission results)
- docs/site_audit/site_audit_summary.md

It also auto-files **high‑severity** issues into the `MASTER_TASK_LOG.md` INBOX
with stable IDs so the board can drive fixes.

Author: Agent-4 (Tech‑Debt Captain)
V2 Compliant: <300 lines
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Required packages not installed. Run:")
    print("   pip install requests beautifulsoup4")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SITES_CONFIG_PATH = PROJECT_ROOT / ".deploy_credentials" / "sites.json"
MASTER_TASK_LOG_PATH = PROJECT_ROOT / "MASTER_TASK_LOG.md"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "site_audit"

TIMEOUT = 10
USER_AGENT = "NightlySiteAudit/1.0 (Agent-4 automated QA)"


def load_sites_config() -> Dict[str, Dict[str, Any]]:
    """Load site configs from sites.json."""
    if not SITES_CONFIG_PATH.exists():
        print(f"❌ Sites config not found: {SITES_CONFIG_PATH}")
        return {}
    with SITES_CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def fetch_homepage(session: requests.Session, site_url: str) -> Tuple[str | None, int | None, str | None]:
    """Fetch homepage HTML; return (text, status, error)."""
    try:
        resp = session.get(site_url, timeout=TIMEOUT)
        return resp.text, resp.status_code, None
    except Exception as exc:  # pragma: no cover - network failure path
        return None, None, str(exc)


def collect_candidate_links(soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
    """Collect nav/footer/CTA links with basic context."""
    links: List[Dict[str, Any]] = []
    seen: set[Tuple[str, str]] = set()

    def add_link(a_tag, source: str) -> None:
        href = (a_tag.get("href") or "").strip()
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            return
        absolute = urljoin(base_url, href)
        key = (absolute, source)
        if key in seen:
            return
        seen.add(key)
        links.append(
            {
                "url": absolute,
                "source": source,
                "text": (a_tag.get_text(strip=True) or "")[:80],
            }
        )

    for nav in soup.find_all("nav"):
        for a in nav.find_all("a"):
            add_link(a, "nav")

    for footer in soup.find_all("footer"):
        for a in footer.find_all("a"):
            add_link(a, "footer")

    cta_keywords = [
        "cta",
        "button",
        "btn",
        "primary",
        "sign up",
        "signup",
        "get started",
        "book",
        "contact",
        "checkout",
        "buy",
        "order",
    ]
    for a in soup.find_all("a"):
        classes = " ".join(a.get("class", []))
        text = (a.get_text(strip=True) or "").lower()
        if any(k in classes.lower() for k in ["btn", "button", "cta", "primary"]) or any(
            k in text for k in cta_keywords
        ):
            add_link(a, "cta")

    return links


def check_link(session: requests.Session, url: str) -> Tuple[int | None, bool, str | None]:
    """Return (status_code, ok_flag, error_message)."""
    try:
        resp = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        return resp.status_code, resp.status_code < 400, None
    except Exception as exc:  # pragma: no cover - network failure path
        return None, False, str(exc)


def link_severity(site_domain: str, link: Dict[str, Any], status: int | None, ok: bool) -> str:
    """Heuristic severity for a broken link."""
    if ok:
        return "INFO"
    source = link.get("source", "")
    parsed = urlparse(link["url"])
    is_same_domain = parsed.netloc.endswith(site_domain)
    path = parsed.path or ""
    if "checkout" in path or "cart" in path or "payment" in path:
        return "CRITICAL"
    if source in {"nav", "footer"} and is_same_domain:
        return "HIGH"
    if status and status >= 500:
        return "HIGH"
    return "MEDIUM"


def collect_forms(soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
    """Collect basic form metadata from the page."""
    forms: List[Dict[str, Any]] = []
    for idx, form in enumerate(soup.find_all("form"), start=1):
        action = (form.get("action") or "").strip() or base_url
        method = (form.get("method") or "GET").strip().upper()
        inputs: List[Dict[str, str]] = []
        for inp in form.find_all("input"):
            name = inp.get("name")
            if not name:
                continue
            itype = (inp.get("type") or "text").lower()
            inputs.append({"name": name, "type": itype})
        forms.append(
            {
                "id": f"form-{idx}",
                "action": urljoin(base_url, action),
                "method": method,
                "inputs": inputs,
            }
        )
    return forms


def build_form_payload(inputs: List[Dict[str, str]]) -> Dict[str, str]:
    """Build a safe, generic payload for form submission."""
    data: Dict[str, str] = {}
    for field in inputs:
        name = field["name"]
        itype = field["type"]
        if itype in {"submit", "button", "image", "file"}:
            continue
        if itype == "email":
            data[name] = "audit@example.com"
        elif itype in {"checkbox", "radio"}:
            data[name] = "on"
        else:
            data[name] = "TEST_AUDIT"
    return data


def test_form(session: requests.Session, form: Dict[str, Any]) -> Dict[str, Any]:
    """Submit a form once with a generic payload and record the result."""
    result: Dict[str, Any] = {
        "form_id": form["id"],
        "action": form["action"],
        "method": form["method"],
        "status": None,
        "ok": False,
        "error": None,
    }
    payload = build_form_payload(form["inputs"])
    try:
        if form["method"] == "POST":
            resp = session.post(form["action"], data=payload, timeout=TIMEOUT, allow_redirects=True)
        else:
            resp = session.get(form["action"], params=payload, timeout=TIMEOUT, allow_redirects=True)
        result["status"] = resp.status_code
        result["ok"] = resp.status_code < 400
        if not result["ok"]:
            result["error"] = f"Non-OK HTTP status: {resp.status_code}"
    except Exception as exc:  # pragma: no cover - network failure path
        result["error"] = str(exc)
    return result


def form_severity(action_url: str, ok: bool, status: int | None) -> str:
    """Severity for a form failure."""
    if ok:
        return "INFO"
    path = urlparse(action_url).path or ""
    if "checkout" in path or "cart" in path or "payment" in path or "order" in path:
        return "CRITICAL"
    if status and status >= 500:
        return "HIGH"
    return "MEDIUM"


def make_issue_id(kind: str, site_key: str, target: str) -> str:
    """Stable issue ID based on site + target URL."""
    slug = re.sub(r"[^A-Za-z0-9]", "", site_key).upper() or "SITE"
    digest = hashlib.sha1(target.encode("utf-8")).hexdigest()[:8].upper()
    return f"SA-{slug}-{kind}-{digest}"


def load_existing_issue_ids() -> set[str]:
    """Scan MASTER_TASK_LOG for existing SITE_AUDIT issue IDs."""
    if not MASTER_TASK_LOG_PATH.exists():
        return set()
    text = MASTER_TASK_LOG_PATH.read_text(encoding="utf-8")
    return set(re.findall(r"\[(SA-[A-Z0-9\-]{5,})\]", text))


def append_issues_to_master_log(tasks: List[str]) -> None:
    """Append new tasks under INBOX in MASTER_TASK_LOG.md."""
    if not tasks:
        return
    if not MASTER_TASK_LOG_PATH.exists():
        print(f"⚠️ MASTER_TASK_LOG not found at {MASTER_TASK_LOG_PATH}, skipping task filing.")
        return
    lines = MASTER_TASK_LOG_PATH.read_text(encoding="utf-8").splitlines()
    inbox_idx = None
    insert_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("## ") and "INBOX" in line:
            inbox_idx = i
        elif inbox_idx is not None and line.strip().startswith("---"):
            insert_idx = i
            break
    if insert_idx is None:
        insert_idx = len(lines)
    new_lines = lines[:insert_idx] + tasks + lines[insert_idx:]
    MASTER_TASK_LOG_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def run_audit() -> int:
    """Main audit orchestration."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sites_cfg = load_sites_config()
    if not sites_cfg:
        return 1

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    broken_links_report: Dict[str, Any] = {"generated_at": datetime.utcnow().isoformat() + "Z", "sites": {}}
    forms_report: Dict[str, Any] = {"generated_at": broken_links_report["generated_at"], "sites": {}}
    new_inbox_tasks: List[str] = []
    existing_ids = load_existing_issue_ids()

    for site_key, cfg in sites_cfg.items():
        site_url = cfg.get("site_url")
        if not site_url:
            continue

        domain = urlparse(site_url).netloc
        print(f"🔍 Auditing {site_key} ({site_url})")
        html, status, error = fetch_homepage(session, site_url)
        site_links: List[Dict[str, Any]] = []
        site_broken: List[Dict[str, Any]] = []
        site_forms: List[Dict[str, Any]] = []
        form_issues: List[Dict[str, Any]] = []

        if html and status and status < 400:
            soup = BeautifulSoup(html, "html.parser")
            site_links = collect_candidate_links(soup, site_url)
            for link in site_links:
                code, ok, err = check_link(session, link["url"])
                sev = link_severity(domain, link, code, ok)
                record = {
                    "url": link["url"],
                    "source": link["source"],
                    "text": link["text"],
                    "status": code,
                    "ok": ok,
                    "error": err,
                    "severity": sev,
                }
                if not ok:
                    site_broken.append(record)
                    if sev in {"HIGH", "CRITICAL"}:
                        issue_id = make_issue_id("LINK", site_key, link["url"])
                        if issue_id not in existing_ids:
                            existing_ids.add(issue_id)
                            task = (
                                f"- [ ] [SITE_AUDIT][{sev}][{issue_id}] "
                                f"{site_key}: {link['source']} link '{link['text'] or link['url']}' "
                                f"-> {code or 'ERROR'} ({link['url']})"
                            )
                            new_inbox_tasks.append(task)

            raw_forms = collect_forms(soup, site_url)
            for form in raw_forms:
                result = test_form(session, form)
                site_forms_result = {**form, **result}
                site_forms_result.pop("inputs", None)
                site_forms_result["has_inputs"] = bool(form["inputs"])
                site_forms.append(site_forms_result)
                if not result["ok"]:
                    sev = form_severity(result["action"], result["ok"], result["status"])
                    issue = {
                        "form_id": form["id"],
                        "action": result["action"],
                        "status": result["status"],
                        "error": result["error"],
                        "severity": sev,
                    }
                    form_issues.append(issue)
                    if sev in {"HIGH", "CRITICAL"}:
                        issue_id = make_issue_id("FORM", site_key, result["action"])
                        if issue_id not in existing_ids:
                            existing_ids.add(issue_id)
                            task = (
                                f"- [ ] [SITE_AUDIT][{sev}][{issue_id}] "
                                f"{site_key}: form {form['id']} POST to {result['action']} "
                                f"failed ({result['status'] or 'ERROR'})"
                            )
                            new_inbox_tasks.append(task)
        else:
            # Homepage not accessible; treat as a single high-severity issue
            issue = {
                "url": site_url,
                "source": "homepage",
                "text": "",
                "status": status,
                "ok": False,
                "error": error or "Homepage not reachable",
                "severity": "HIGH",
            }
            site_broken.append(issue)
            issue_id = make_issue_id("LINK", site_key, site_url)
            if issue_id not in existing_ids:
                existing_ids.add(issue_id)
                task = (
                    f"- [ ] [SITE_AUDIT][HIGH][{issue_id}] "
                    f"{site_key}: homepage not reachable ({status or 'ERROR'}) {site_url}"
                )
                new_inbox_tasks.append(task)

        broken_links_report["sites"][site_key] = {
            "site_url": site_url,
            "homepage_status": status,
            "broken_links": site_broken,
        }
        forms_report["sites"][site_key] = {
            "site_url": site_url,
            "homepage_status": status,
            "forms_tested": site_forms,
            "form_issues": form_issues,
        }

    # Write JSON reports (last-run snapshot)
    (OUTPUT_DIR / "broken_links.json").write_text(
        json.dumps(broken_links_report, indent=2), encoding="utf-8"
    )
    (OUTPUT_DIR / "forms_test.json").write_text(
        json.dumps(forms_report, indent=2), encoding="utf-8"
    )

    # Write human-readable summary
    summary_lines: List[str] = []
    summary_lines.append("# Nightly Site Audit Summary")
    summary_lines.append(f"**Generated at**: {broken_links_report['generated_at']}")
    summary_lines.append("")
    for site_key, data in broken_links_report["sites"].items():
        broken = data["broken_links"]
        forms_data = forms_report["sites"].get(site_key, {})
        form_issues = forms_data.get("form_issues", [])
        summary_lines.append(f"## {site_key}")
        summary_lines.append(f"- Broken links: {len(broken)}")
        summary_lines.append(f"- Form issues: {len(form_issues)}")
        summary_lines.append("")
    (OUTPUT_DIR / "site_audit_summary.md").write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )

    # File high-severity issues into MASTER_TASK_LOG INBOX
    append_issues_to_master_log(new_inbox_tasks)

    print("✅ Nightly site audit complete.")
    print(f"📄 Broken links report: {OUTPUT_DIR / 'broken_links.json'}")
    print(f"📄 Forms test report:   {OUTPUT_DIR / 'forms_test.json'}")
    print(f"📄 Summary markdown:    {OUTPUT_DIR / 'site_audit_summary.md'}")
    if new_inbox_tasks:
        print(f"📝 New INBOX tasks filed: {len(new_inbox_tasks)}")
    else:
        print("ℹ️ No new INBOX tasks filed (no new high-severity issues).")

    return 0


if __name__ == "__main__":
    sys.exit(run_audit())


