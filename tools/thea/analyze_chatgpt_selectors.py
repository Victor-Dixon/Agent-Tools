#!/usr/bin/env python3
"""
ChatGPT Selector Analysis Tool

Analyzes the current ChatGPT page structure and suggests selectors for:
- Prompt textarea/input field
- Send/submit button
- Response areas

Usage:
    python tools/thea/analyze_chatgpt_selectors.py --url "https://chat.openai.com"
    python tools/thea/analyze_chatgpt_selectors.py --analyze-current
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import undetected_chromedriver as uc

from src.infrastructure.browser.browser_models import BrowserConfig
from src.infrastructure.browser.thea_browser_service import TheaBrowserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatGPTAnalyzer:
    """Analyzes ChatGPT page structure for automation selectors."""

    def __init__(self, headless: bool = False, use_thea_service: bool = True):
        self.headless = headless
        self.use_thea_service = use_thea_service
        self.driver = None
        self.thea_service = None

    def setup_driver(self):
        """Initialize driver - either Thea service or direct Chrome."""
        if self.use_thea_service:
            # Use Thea browser service for authentication
            from src.infrastructure.browser.thea_browser_service import TheaBrowserService
            config = BrowserConfig(headless=self.headless)
            self.thea_service = TheaBrowserService(config)
            success = self.thea_service.initialize()
            if not success:
                raise Exception("Failed to initialize Thea browser service")
            self.driver = self.thea_service.driver
        else:
            # Direct Chrome setup
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')

            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')

            self.driver = uc.Chrome(options=options)
            self.driver.implicitly_wait(10)

    def load_page(self, url: str, wait_for_element: str = None, cookie_path: str = None):
        """Load the ChatGPT page and wait for it to be ready."""
        logger.info(f"Loading page: {url}")

        if self.use_thea_service and self.thea_service:
            # Use Thea service to load page with authentication
            self.thea_service.driver.get(url)
            if cookie_path:
                self.thea_service.thea_config.cookie_file = cookie_path
                # Extract base URL for cookie loading
                from urllib.parse import urlparse
                parsed = urlparse(url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"
                self.thea_service._load_cookies(base_url)

            # Try to ensure we're authenticated
            authed = self.thea_service.ensure_thea_authenticated(allow_manual=False)
            if not authed:
                logger.warning("Thea authentication may have failed")

        else:
            # Direct page load
            self.driver.get(url)

        # Wait for page to be ready
        if wait_for_element:
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                )
                logger.info("Page loaded successfully")
            except TimeoutException:
                logger.warning(f"Timeout waiting for element: {wait_for_element}")
        else:
            # Wait for common ChatGPT elements
            common_selectors = [
                "textarea",
                "div[contenteditable='true']",
                "[data-testid]",
                ".composer",
                "form",
                "[role='textbox']"
            ]
            for selector in common_selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found element with selector: {selector}")
                    break
                except TimeoutException:
                    continue

    def analyze_input_elements(self) -> List[Dict[str, Any]]:
        """Analyze all potential input elements on the page."""
        elements_data = []

        # Common input element selectors
        input_selectors = [
            "textarea",
            "input[type='text']",
            "input:not([type])",
            "div[contenteditable='true']",
            "[role='textbox']",
            "[data-testid*='input']",
            "[aria-label*='message']",
            "[placeholder*='message']"
        ]

        for selector in input_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for i, element in enumerate(elements):
                    try:
                        element_data = self._analyze_element(element, selector, i)
                        if element_data:
                            elements_data.append(element_data)
                    except Exception as e:
                        logger.debug(f"Error analyzing element {i} with {selector}: {e}")
                        continue
            except Exception as e:
                logger.debug(f"Error finding elements with {selector}: {e}")
                continue

        return elements_data

    def analyze_button_elements(self) -> List[Dict[str, Any]]:
        """Analyze all potential button elements on the page."""
        elements_data = []

        # Common button element selectors
        button_selectors = [
            "button",
            "input[type='submit']",
            "[role='button']",
            "[aria-label*='send']",
            "[data-testid*='send']",
            "svg[aria-label*='send']",
            "[class*='send']"
        ]

        for selector in button_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for i, element in enumerate(elements):
                    try:
                        element_data = self._analyze_element(element, selector, i)
                        if element_data:
                            elements_data.append(element_data)
                    except Exception as e:
                        logger.debug(f"Error analyzing button {i} with {selector}: {e}")
                        continue
            except Exception as e:
                logger.debug(f"Error finding buttons with {selector}: {e}")
                continue

        return elements_data

    def _analyze_element(self, element, base_selector: str, index: int) -> Dict[str, Any]:
        """Analyze a single element and extract relevant data."""
        try:
            # Basic properties
            data = {
                "selector": f"{base_selector}:nth-of-type({index + 1})",
                "tag_name": element.tag_name,
                "visible": element.is_displayed(),
                "enabled": element.is_enabled(),
                "location": element.location,
                "size": element.size,
            }

            # Attributes
            attributes = {}
            important_attrs = [
                'id', 'class', 'name', 'type', 'role', 'aria-label',
                'data-testid', 'placeholder', 'contenteditable',
                'value', 'title', 'alt'
            ]

            for attr in important_attrs:
                try:
                    value = element.get_attribute(attr)
                    if value:
                        attributes[attr] = value
                except:
                    pass

            data["attributes"] = attributes

            # Text content
            try:
                data["text_content"] = element.text
            except:
                data["text_content"] = ""

            # CSS properties that might indicate functionality
            try:
                data["css_cursor"] = element.value_of_css_property("cursor")
                data["css_pointer_events"] = element.value_of_css_property("pointer-events")
            except:
                pass

            # Score the element for relevance
            data["relevance_score"] = self._score_element_relevance(data)

            return data

        except Exception as e:
            logger.debug(f"Error analyzing element: {e}")
            return None

    def _score_element_relevance(self, element_data: Dict[str, Any]) -> int:
        """Score an element for how likely it is to be the target element."""
        score = 0
        attrs = element_data.get("attributes", {})
        text_content = element_data.get("text_content", "").lower()

        # High relevance indicators
        if element_data.get("tag_name") == "textarea":
            score += 20
        if attrs.get("contenteditable") == "true":
            score += 15
        if "textbox" in attrs.get("role", ""):
            score += 15

        # Medium relevance indicators
        if "message" in attrs.get("aria-label", "").lower():
            score += 10
        if "message" in attrs.get("placeholder", "").lower():
            score += 10
        if "send" in attrs.get("aria-label", "").lower():
            score += 10
        if "send" in text_content:
            score += 10
        if "submit" in attrs.get("type", ""):
            score += 10

        # Position-based scoring (inputs/buttons are usually near bottom)
        location = element_data.get("location", {})
        if location.get("y", 0) > 500:
            score += 5

        # Size-based scoring (inputs/buttons are usually reasonably sized)
        size = element_data.get("size", {})
        width = size.get("width", 0)
        height = size.get("height", 0)
        if 50 < width < 800 and 20 < height < 200:
            score += 5

        return score

    def suggest_selectors(self, elements_data: List[Dict[str, Any]], element_type: str) -> List[Dict[str, Any]]:
        """Suggest the best selectors based on analysis."""
        # Sort by relevance score
        sorted_elements = sorted(elements_data, key=lambda x: x.get("relevance_score", 0), reverse=True)

        suggestions = []
        for element in sorted_elements[:5]:  # Top 5 suggestions
            suggestion = {
                "selector": element["selector"],
                "score": element["relevance_score"],
                "tag_name": element["tag_name"],
                "attributes": element["attributes"],
                "location": element["location"],
                "size": element["size"],
            }
            suggestions.append(suggestion)

        return suggestions

    def generate_selector_report(self, url: str, cookie_path: str = None) -> Dict[str, Any]:
        """Generate a complete selector analysis report."""
        logger.info("Starting ChatGPT selector analysis...")

        report = {
            "url": url,
            "cookie_path": cookie_path,
            "timestamp": json.dumps(None),  # Will be set by datetime.now().isoformat()
            "input_elements": [],
            "button_elements": [],
            "suggested_input_selectors": [],
            "suggested_button_selectors": [],
            "recommendations": []
        }

        try:
            self.setup_driver()
            self.load_page(url, cookie_path=cookie_path)

            # Analyze elements
            report["input_elements"] = self.analyze_input_elements()
            report["button_elements"] = self.analyze_button_elements()

            # Generate suggestions
            report["suggested_input_selectors"] = self.suggest_selectors(
                report["input_elements"], "input"
            )
            report["suggested_button_selectors"] = self.suggest_selectors(
                report["button_elements"], "button"
            )

            # Generate recommendations
            report["recommendations"] = self._generate_recommendations(report)

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            report["error"] = str(e)
        finally:
            if self.driver:
                self.driver.quit()

        return report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on the analysis."""
        recommendations = []

        input_suggestions = report.get("suggested_input_selectors", [])
        button_suggestions = report.get("suggested_button_selectors", [])

        if input_suggestions:
            top_input = input_suggestions[0]
            recommendations.append(
                f"Try input selector: '{top_input['selector']}' (score: {top_input['score']})"
            )

        if button_suggestions:
            top_button = button_suggestions[0]
            recommendations.append(
                f"Try button selector: '{top_button['selector']}' (score: {top_button['score']})"
            )

        # Additional recommendations
        if not input_suggestions:
            recommendations.append("No input elements found - page may not be loaded or requires authentication")

        if not button_suggestions:
            recommendations.append("No button elements found - may need to wait for page to fully load")

        if len(input_suggestions) > 1:
            recommendations.append("Multiple input candidates found - test each selector systematically")

        return recommendations

    def save_report(self, report: Dict[str, Any], output_file: str):
        """Save the analysis report to a JSON file."""
        import datetime
        report["timestamp"] = datetime.datetime.now().isoformat()

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="ChatGPT Selector Analysis Tool")
    parser.add_argument("--url", default="https://chat.openai.com",
                       help="URL to analyze")
    parser.add_argument("--output", "-o", default="data/cache/thea/selector_analysis.json",
                       help="Output file for analysis report")
    parser.add_argument("--cookie-path", default="data/thea_cookies.json",
                       help="Path to Thea cookies for authentication")
    parser.add_argument("--headless", action="store_true",
                       help="Run in headless mode")
    parser.add_argument("--no-thea-service", action="store_true",
                       help="Don't use Thea service (direct Chrome)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    analyzer = ChatGPTAnalyzer(
        headless=args.headless,
        use_thea_service=not args.no_thea_service
    )
    report = analyzer.generate_selector_report(args.url, args.cookie_path)

    # Print summary
    print("\n=== CHATGPT SELECTOR ANALYSIS REPORT ===")
    print(f"URL: {report['url']}")
    print(f"Input elements found: {len(report['input_elements'])}")
    print(f"Button elements found: {len(report['button_elements'])}")

    print("\n🎯 TOP INPUT SELECTOR SUGGESTIONS:")
    for i, suggestion in enumerate(report['suggested_input_selectors'][:3], 1):
        print(f"{i}. {suggestion['selector']} (score: {suggestion['score']})")

    print("\n🎯 TOP BUTTON SELECTOR SUGGESTIONS:")
    for i, suggestion in enumerate(report['suggested_button_selectors'][:3], 1):
        print(f"{i}. {suggestion['selector']} (score: {suggestion['score']})")

    print("\n💡 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"• {rec}")

    # Save detailed report
    analyzer.save_report(report, args.output)
    print(f"\n📄 Detailed report saved to: {args.output}")


if __name__ == "__main__":
    main()
