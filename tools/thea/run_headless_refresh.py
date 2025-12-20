#!/usr/bin/env python3
"""
Run a headless Thea refresh using undetected_chromedriver and existing cookies.
Logs to stdout for quick verification.
"""

import os
import traceback
from datetime import datetime

from src.infrastructure.browser.thea_browser_service import TheaBrowserService
from src.infrastructure.browser.browser_models import BrowserConfig, TheaConfig


def main():
    print("=== Thea headless refresh ===", datetime.utcnow().isoformat())
    cookie_path = "data/thea_cookies.json"
    print("cookie_path:", os.path.abspath(cookie_path), "exists:", os.path.exists(cookie_path))
    try:
        svc = TheaBrowserService(BrowserConfig(headless=True), TheaConfig())
        ok_init = svc.initialize()
        print("init:", ok_init)
        ok_auth = svc.ensure_thea_authenticated(allow_manual=False)
        print("auth:", ok_auth)
        svc.close()
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()







