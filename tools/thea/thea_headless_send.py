#!/usr/bin/env python3
"""
Headless Thea send/receive helper.

Uses undetected_chromedriver + saved cookies to send a prompt and capture
the assistant reply text without needing the Discord bot or PyAutoGUI.
"""

import argparse
import json
import sys
from pathlib import Path

from src.infrastructure.browser.browser_models import BrowserConfig, TheaConfig
from src.infrastructure.browser.thea_browser_service import TheaBrowserService


def run_headless_prompt(
    message: str,
    timeout: float,
    poll_interval: float,
    headless: bool,
    allow_manual: bool,
    cookie_path: str | None,
    conversation_url: str | None,
) -> dict:
    cfg = BrowserConfig(headless=headless)
    thea_cfg = TheaConfig()
    if cookie_path:
        thea_cfg.cookie_file = cookie_path
    if conversation_url:
        thea_cfg.conversation_url = conversation_url

    svc = TheaBrowserService(cfg, thea_cfg)
    if not svc.initialize():
        return {"ok": False, "error": "init_failed"}

    authed = svc.ensure_thea_authenticated(allow_manual=allow_manual and not headless)
    if not authed:
        svc.close()
        return {"ok": False, "error": "auth_failed"}

    reply = svc.send_prompt_and_get_response_text(
        prompt=message, timeout=timeout, poll_interval=poll_interval
    )
    svc.close()

    if reply is None:
        return {"ok": False, "error": "no_reply"}

    return {"ok": True, "response": reply}


def main():
    parser = argparse.ArgumentParser(
        description="Headless Thea send/receive using saved cookies."
    )
    parser.add_argument("-m", "--message", required=True, help="Prompt to send")
    parser.add_argument("--timeout", type=float, default=90.0, help="Wait seconds for reply")
    parser.add_argument(
        "--poll-interval", type=float, default=2.0, help="Polling interval in seconds"
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Run non-headless (useful for debugging); still avoids PyAutoGUI",
    )
    parser.add_argument(
        "--allow-manual",
        action="store_true",
        help="Allow manual login if cookies fail (ignored when headless)",
    )
    parser.add_argument(
        "--cookie-path",
        default="data/thea_cookies.json",
        help="Path to thea cookies JSON",
    )
    parser.add_argument(
        "--conversation-url",
        default=None,
        help="Override Thea conversation URL (default from TheaConfig)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional file to write response JSON {prompt,response}",
    )

    args = parser.parse_args()

    result = run_headless_prompt(
        message=args.message,
        timeout=args.timeout,
        poll_interval=args.poll_interval,
        headless=not args.visible,
        allow_manual=args.allow_manual,
        cookie_path=args.cookie_path,
        conversation_url=args.conversation_url,
    )

    print(json.dumps(result, indent=2))

    if args.out and result.get("ok"):
        Path(args.out).write_text(
            json.dumps(
                {"prompt": args.message, "response": result.get("response")},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()






