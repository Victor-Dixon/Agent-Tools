#!/usr/bin/env python3
"""
Thea Automation - Messaging Module
==================================

Handles message sending and response capture.

V2 Compliance: Single responsibility (messaging operations only)
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path

try:
    import pyautogui
    import pyperclip

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from response_detector import ResponseDetector, ResponseWaitResult

    DETECTOR_AVAILABLE = True
except ImportError:
    DETECTOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class TheaMessagingManager:
    """Manages message sending and response capture for Thea automation."""

    def __init__(self, driver, responses_dir: str | Path, timeout: int = 120):
        """
        Initialize messaging manager.

        Args:
            driver: Selenium WebDriver instance
            responses_dir: Directory to save responses
            timeout: Timeout in seconds for response capture
        """
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError("PyAutoGUI is required: pip install pyautogui pyperclip")

        self.driver = driver
        self.responses_dir = Path(responses_dir)
        self.responses_dir.mkdir(exist_ok=True)
        self.timeout = timeout
        self.detector = None

        if not DETECTOR_AVAILABLE:
            logger.warning("ResponseDetector not available - response capture may not work")

    def send_message(self, message: str, wait_for_response: bool = True) -> str | None:
        """
        Send message to Thea and optionally wait for response.

        Args:
            message: Message to send
            wait_for_response: Whether to wait for and capture response

        Returns:
            Response text if wait_for_response=True, else None
        """
        try:
            # Send message via clipboard paste
            logger.info(f"📤 Sending message: {message[:50]}...")
            pyperclip.copy(message)
            time.sleep(0.5)

            # Paste and send
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.5)
            pyautogui.press("enter")
            logger.info("✅ Message sent")

            # Wait for response if requested
            if wait_for_response:
                return self.wait_for_response()

            return None

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None

    def wait_for_response(self) -> str | None:
        """
        Wait for and capture Thea's response.

        Returns:
            str: Response text, or None if failed
        """
        try:
            logger.info("⏳ Waiting for response...")

            if not DETECTOR_AVAILABLE:
                logger.warning("ResponseDetector not available - manual wait")
                time.sleep(10)
                return "⚠️ Response detection not available"

            if not self.detector:
                self.detector = ResponseDetector(self.driver)

            # Wait for response
            result = self.detector.wait_until_complete(
                timeout=self.timeout, stable_secs=3.0, auto_continue=True
            )

            return self._process_response_result(result)

        except Exception as e:
            logger.error(f"Failed to capture response: {e}")
            return None

    def _process_response_result(self, result) -> str | None:
        """
        Process response wait result.

        Args:
            result: ResponseWaitResult from detector

        Returns:
            str: Response text or warning message
        """
        if result == ResponseWaitResult.COMPLETE:
            logger.info("✅ Response complete")
            response = self.detector.get_last_response_text()
            return response
        else:
            logger.warning(f"⚠️ Response status: {result}")
            response = self.detector.get_last_response_text()
            return response or f"⚠️ Response incomplete: {result}"

    def save_conversation(self, message: str, response: str, thea_url: str) -> str:
        """
        Save conversation to JSON file.

        Args:
            message: Message that was sent
            response: Response received
            thea_url: URL of Thea instance

        Returns:
            str: Path to saved file, or empty string if failed
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = self.responses_dir / f"conversation_{timestamp}.json"

            data = {
                "timestamp": timestamp,
                "message": message,
                "response": response,
                "thea_url": thea_url,
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved to: {filename}")
            return str(filename)

        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return ""
