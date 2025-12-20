#!/usr/bin/env python3
"""
Update FreeRideInvestor.com Premium Report with Real Metrics
============================================================

Replaces placeholder metrics in premium TSLA strategy report with real backtest data.

Author: Agent-2
"""

from tools.strategy_blog_automation import TSLA_STRATEGY
import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Import strategy config

# Load credentials
creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
with open(creds_file) as f:
    creds_data = json.load(f)

SITE_CONFIG = creds_data["freerideinvestor"]
SITE_URL = SITE_CONFIG["site_url"]
USERNAME = SITE_CONFIG["username"]
APP_PASSWORD = SITE_CONFIG["app_password"]

API_BASE = f"{SITE_URL}/wp-json/wp/v2"
AUTH = HTTPBasicAuth(USERNAME, APP_PASSWORD.replace(" ", ""))


def format_currency(value: float) -> str:
    """Format currency value."""
    return f"${value:,.2f}"


def format_percent(value: float) -> str:
    """Format percentage value."""
    return f"{value:.2f}%"


def get_premium_report_page() -> Optional[Dict]:
    """Get the premium report page."""
    url = f"{API_BASE}/pages"
    params = {"slug": "tsla-strategy-report-premium", "per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)
    if response.status_code == 200:
        pages = response.json()
        return pages[0] if pages else None

    # Also try posts
    url = f"{API_BASE}/posts"
    params = {"slug": "tsla-strategy-report-premium", "per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)
    if response.status_code == 200:
        posts = response.json()
        return posts[0] if posts else None

    return None


def generate_premium_metrics_section() -> str:
    """Generate premium metrics section with real data."""
    metrics = TSLA_STRATEGY["backtest_metrics"]

    # Calculate profit factor
    profit_factor = metrics["gross_profit"] / \
        abs(metrics["gross_loss"]) if metrics["gross_loss"] != 0 else 0
    outperformance = metrics["net_profit"] - metrics["buy_hold_return"]
    outperformance_pct = metrics["net_profit_pct"] - \
        metrics["buy_hold_return_pct"]

    section = f"""
<!-- wp:heading {{"level": 2}} -->
<h2>Detailed Performance Metrics</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>Backtest Period:</strong> Historical data analysis</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level": 3}} -->
<h3>Profit & Loss Summary</h3>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>Initial Capital:</strong> {format_currency(metrics["initial_capital"])}</li>
<li><strong>Net Profit:</strong> {format_currency(metrics["net_profit"])} ({format_percent(metrics["net_profit_pct"])})</li>
<li><strong>Gross Profit:</strong> {format_currency(metrics["gross_profit"])} ({format_percent(metrics["gross_profit_pct"])})</li>
<li><strong>Gross Loss:</strong> {format_currency(metrics["gross_loss"])} ({format_percent(metrics["gross_loss_pct"])})</li>
<li><strong>Profit Factor:</strong> {profit_factor:.2f}</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading {{"level": 3}} -->
<h3>Risk Metrics</h3>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>Max Equity Drawdown:</strong> {format_currency(metrics["max_equity_drawdown"])} ({format_percent(metrics["max_equity_drawdown_pct"])})</li>
<li><strong>Max Equity Run-up:</strong> {format_currency(metrics["max_equity_runup"])} ({format_percent(metrics["max_equity_runup_pct"])})</li>
<li><strong>Average Drawdown:</strong> {format_currency(metrics["avg_equity_drawdown"])} ({format_percent(metrics["avg_equity_drawdown_pct"])})</li>
<li><strong>Average Run-up:</strong> {format_currency(metrics["avg_equity_runup"])} ({format_percent(metrics["avg_equity_runup_pct"])})</li>
<li><strong>Avg Drawdown Duration:</strong> {metrics["avg_drawdown_duration"]}</li>
<li><strong>Avg Run-up Duration:</strong> {metrics["avg_runup_duration"]}</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading {{"level": 3}} -->
<h3>Comparison Metrics</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>Buy & Hold Return:</strong> {format_currency(metrics["buy_hold_return"])} ({format_percent(metrics["buy_hold_return_pct"])})</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>Strategy Outperformance:</strong> {format_currency(outperformance)} ({format_percent(outperformance_pct)})</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level": 3}} -->
<h3>Position Sizing</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>Max Contracts Held:</strong> {metrics["max_contracts_held"]}</p>
<!-- /wp:paragraph -->
"""

    return section


def update_premium_report(page_id: int, content: str) -> bool:
    """Update premium report page with real metrics."""
    # Check for placeholder indicators
    placeholder_patterns = [
        r"placeholder",
        r"TBD",
        r"coming soon",
        r"example",
        r"sample",
        r"\[PLACEHOLDER\]",
        r"XXX",
        r"0\.00",
        r"\$0\.00"
    ]

    has_placeholders = any(
        re.search(pattern, content, re.IGNORECASE)
        for pattern in placeholder_patterns
    )

    if not has_placeholders:
        print("⏭️  No obvious placeholders found in content")
        # Still check if metrics section is missing
        if "Detailed Performance Metrics" not in content:
            print("📝 Adding detailed metrics section...")
            # Append metrics section before closing tags
            metrics_section = generate_premium_metrics_section()
            # Insert before any closing divs or at end
            if "</div>" in content:
                content = content.replace(
                    "</div>", metrics_section + "</div>", 1)
            else:
                content += metrics_section
        else:
            print("✅ Premium report already has metrics section")
            return True

    # Replace placeholder metrics with real data
    metrics_section = generate_premium_metrics_section()

    # Try to find and replace existing metrics section
    metrics_pattern = r'(<!-- wp:heading.*?Detailed Performance Metrics.*?<!-- /wp:heading -->.*?<!-- /wp:paragraph -->)'
    if re.search(metrics_pattern, content, re.DOTALL):
        content = re.sub(metrics_pattern, metrics_section,
                         content, flags=re.DOTALL)
        print("✅ Replaced existing metrics section")
    else:
        # Append new metrics section
        content += metrics_section
        print("✅ Added new metrics section")

    # Update page
    url = f"{API_BASE}/pages/{page_id}"
    data = {"content": content}
    response = requests.post(url, json=data, auth=AUTH, timeout=30)

    if response.status_code == 200:
        print(f"✅ Updated premium report page (ID: {page_id})")
        return True
    else:
        print(
            f"❌ Failed to update page: {response.status_code} - {response.text}")
        return False


def main():
    """Main execution."""
    print("🔧 Updating FreeRideInvestor.com premium report with real metrics...\n")

    # Get premium report page
    page = get_premium_report_page()
    if not page:
        print("❌ Could not find premium report page at /tsla-strategy-report-premium")
        print("💡 Creating premium report page...")

        # Create the page
        url = f"{API_BASE}/pages"
        content = generate_premium_metrics_section()
        data = {
            "title": "TSLA Strategy Report - Premium",
            "slug": "tsla-strategy-report-premium",
            "status": "publish",
            "content": f"<h1>TSLA Strategy Report - Premium</h1>{content}"
        }
        response = requests.post(url, json=data, auth=AUTH, timeout=30)
        if response.status_code == 201:
            page_id = response.json().get("id")
            print(f"✅ Created premium report page (ID: {page_id})")
        else:
            print(
                f"❌ Failed to create page: {response.status_code} - {response.text}")
            sys.exit(1)
    else:
        page_id = page["id"]
        content = page.get("content", {}).get("rendered", "")
        print(f"✅ Found premium report page (ID: {page_id})")

        # Update with real metrics
        update_premium_report(page_id, content)

    print("\n✅ Premium report update complete!")
    print(f"📋 View at: {SITE_URL}/tsla-strategy-report-premium")


if __name__ == "__main__":
    main()
