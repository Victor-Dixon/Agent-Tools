#!/usr/bin/env python3
"""
TSLA Daily Plan Poster
======================

Posts a daily trading plan/report to WordPress using Application Password auth.

Usage:
  WP_URL="https://freerideinvestor.com" \
  WP_USER="your-user" \
  WP_APP_PASS="xxxx xxxx xxxx xxxx" \
  python tools/tsla_daily_plan_poster.py --symbol TSLA --category-id 12

Dry run (print only):
  python tools/tsla_daily_plan_poster.py --dry-run

Notes:
  - Requires WordPress Application Password (username + app password).
  - Set --category-id to file under a specific category (optional).
"""

import argparse
import os
from datetime import datetime
from textwrap import dedent
from typing import Optional

import requests


def build_daily_plan(symbol: str = "TSLA", date_str: Optional[str] = None) -> tuple[str, str]:
    """Build a daily plan title and content."""
    today = date_str or datetime.now().strftime("%Y-%m-%d")
    title = f"{symbol} Daily Plan — {today}"
    content = dedent(
        f"""
        ## Daily {symbol} Plan — {today}

        ### Market Bias
        - Neutral / Bullish / Bearish (fill based on premarket + trend)

        ### Strategy Engine (Improved {symbol} Strategy - Risk-True)
        **Core Logic**
        - Long when price is above MA50 & MA200 and RSI is not overheated.
        - Short when price is below MA50 & MA200 and RSI is not too washed.

        **Risk Model**
        - Risk % equity per trade uses strategy sizing.
        - Stop based on % of price.

        ### Watch Levels
        - Premarket high/low
        - Yesterday high/low
        - Major weekly pivot

        ### If/Then Scenarios
        - If {symbol} holds above trend + RSI stays controlled → look for clean long structure.
        - If {symbol} loses trend with momentum → short setups only.

        ### Rules to Prioritize Today
        - Max 1–2 A+ setups.
        - Respect stop without debate.
        - No revenge trades.

        ### End-of-Day Recap (fill later)
        - What I did right:
        - What I did wrong:
        - What I will change tomorrow:
        """
    ).strip()
    return title, content


def post_to_wordpress(
    base_url: str,
    user: str,
    app_password: str,
    title: str,
    content: str,
    category_id: Optional[int] = None,
) -> dict:
    """Publish a post to WordPress via REST + application password auth."""
    endpoint = f"{base_url.rstrip('/')}/wp-json/wp/v2/posts"
    payload = {
        "title": title,
        "content": content,
        "status": "publish",
    }
    if category_id:
        payload["categories"] = [category_id]

    response = requests.post(
        endpoint,
        auth=(user, app_password),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Post a daily trading plan to WordPress using application password auth."
    )
    parser.add_argument("--symbol", default="TSLA", help="Ticker symbol (default: TSLA)")
    parser.add_argument("--date", help="Date string (YYYY-MM-DD). Defaults to today.")
    parser.add_argument(
        "--category-id",
        type=int,
        help="Optional WordPress category ID to assign to the post.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the post instead of publishing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_app_pass = os.getenv("WP_APP_PASS")

    if not args.dry_run and not all([wp_url, wp_user, wp_app_pass]):
        print("❌ Missing env: WP_URL, WP_USER, WP_APP_PASS are required unless --dry-run.")
        return 1

    title, content = build_daily_plan(symbol=args.symbol, date_str=args.date)

    if args.dry_run:
        print(f"Title: {title}\n")
        print(content)
        return 0

    try:
        result = post_to_wordpress(
            base_url=wp_url,
            user=wp_user,
            app_password=wp_app_pass,
            title=title,
            content=content,
            category_id=args.category_id,
        )
    except requests.HTTPError as exc:
        print(f"❌ Publish failed: {exc} — {exc.response.text if exc.response else ''}")
        return 1

    post_id = result.get("id")
    link = result.get("link")
    print(f"✅ Posted daily plan as ID {post_id}: {link}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

