#!/usr/bin/env python3
"""
Send a prompt to Thea from a file and save the reply.

Thin wrapper around thea_headless_send that:
- Reads the prompt from a file path
- Uses saved cookies (headless by default)
- Writes both prompt and response to an output file if requested
"""

import argparse
import json
import logging
from pathlib import Path

from src.infrastructure.browser.browser_models import BrowserConfig, TheaConfig
from src.infrastructure.browser.thea_browser_service import TheaBrowserService

# Configure logging to show debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def send_prompt_from_file(
    prompt_path: str,
    timeout: float,
    poll_interval: float,
    headless: bool,
    allow_manual: bool,
    cookie_path: str | None,
    conversation_url: str | None,
) -> dict:
    prompt_text = Path(prompt_path).read_text(encoding="utf-8")

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
        prompt=prompt_text, timeout=timeout, poll_interval=poll_interval
    )
    svc.close()

    if reply is None:
        return {"ok": False, "error": "no_reply"}

    return {"ok": True, "response": reply, "prompt": prompt_text}


def main():
    parser = argparse.ArgumentParser(
        description="Send Thea a prompt from a file and capture the reply."
    )
    parser.add_argument("prompt_path", help="Path to the prompt file (UTF-8)")
    parser.add_argument(
        "--timeout", type=float, default=120.0, help="Seconds to wait for reply"
    )
    parser.add_argument(
        "--poll-interval", type=float, default=2.0, help="Polling interval in seconds"
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Run non-headless (useful if cookies need manual refresh)",
    )
    parser.add_argument(
        "--allow-manual",
        action="store_true",
        help="Allow manual login if cookies fail (ignored when headless)",
    )
    parser.add_argument(
        "--cookie-path",
        default="data/thea_cookies.json",
        help="Path to Thea cookies JSON",
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

    result = send_prompt_from_file(
        prompt_path=args.prompt_path,
        timeout=args.timeout,
        poll_interval=args.poll_interval,
        headless=not args.visible,
        allow_manual=args.allow_manual,
        cookie_path=args.cookie_path,
        conversation_url=args.conversation_url,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.out and result.get("ok"):
        Path(args.out).write_text(
            json.dumps(
                {"prompt": result.get("prompt"), "response": result.get("response")},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()

