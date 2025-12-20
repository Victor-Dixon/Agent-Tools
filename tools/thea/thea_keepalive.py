#!/usr/bin/env python3
"""
Thea Keepalive Helper
---------------------
Headless refresh of existing Thea cookies with self-throttling.
Use this to keep thea_cookies.json warm without invoking the Discord bot.
"""

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

from src.infrastructure.browser.thea_browser_service import TheaBrowserService
from src.infrastructure.browser.browser_models import BrowserConfig, TheaConfig


def read_last_refresh(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return float(data.get("ts"))
    except Exception:
        return None


def write_last_refresh(path: Path, ts: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"ts": ts}, indent=2), encoding="utf-8")


def ensure_keepalive(cookie_path: Path, last_refresh_path: Path, min_interval_minutes: int) -> bool:
    now = time.time()
    if not cookie_path.exists():
        print(f"❌ Cookies missing at {cookie_path}. Run manual login first.")
        return False

    last = read_last_refresh(last_refresh_path)
    if last and (now - last) < (min_interval_minutes * 60):
        age_min = (now - last) / 60
        print(f"⏭️  Skip refresh (age {age_min:.1f}m < {min_interval_minutes}m).")
        return True

    try:
        svc = TheaBrowserService(BrowserConfig(headless=True), TheaConfig())
        ok_init = svc.initialize()
        print("init:", ok_init)
        if not ok_init:
            return False
        ok_auth = svc.ensure_thea_authenticated(allow_manual=False)
        print("auth:", ok_auth)
        svc.close()
        if ok_auth:
            write_last_refresh(last_refresh_path, now)
        return ok_auth
    except Exception as e:
        print(f"❌ Keepalive error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Headless Thea keepalive using existing cookies.")
    parser.add_argument("--cookie-path", default="data/thea_cookies.json", help="Path to Thea cookies JSON")
    parser.add_argument(
        "--last-refresh-path",
        default="data/thea_last_refresh.json",
        help="Path to store last refresh timestamp",
    )
    parser.add_argument("--min-interval-minutes", type=int, default=60, help="Minimum minutes between refreshes")
    args = parser.parse_args()

    cookie_path = Path(args.cookie_path)
    last_refresh_path = Path(args.last_refresh_path)

    print("=== Thea keepalive ===", datetime.utcnow().isoformat())
    print("cookie_path:", cookie_path.resolve(), "exists:", cookie_path.exists())
    ok = ensure_keepalive(cookie_path, last_refresh_path, args.min_interval_minutes)
    print("result:", ok)


if __name__ == "__main__":
    main()







