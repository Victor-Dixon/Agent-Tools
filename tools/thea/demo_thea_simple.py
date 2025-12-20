#!/usr/bin/env python3
"""
Simple Thea Demo - Watch the Automation!
=========================================
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.services.thea import TheaService

print()
print("=" * 70)
print("🎬 THEA AUTOMATION DEMO - WATCH YOUR SCREEN!")
print("=" * 70)
print()
print("Browser will open in 3 seconds...")
print("Make sure you can see the browser window!")
print()

import time

time.sleep(3)

# Create and use Thea service
thea = TheaService(cookie_file="thea_cookies.json", headless=False)

message = """Hello Thea! This is Agent-3 testing the consolidated browser automation.

Today's achievements:
- Discord: 9→4 files
- Browser: 15→5 files  
- V2 compliance: 100%

Please confirm you received this! 🐝"""

print("📤 Sending message...")
print(f"Message: {message[:60]}...")
print()
print("👀 WATCH THE BROWSER WINDOW!")
print()

result = thea.communicate(message, save=True)

print()
print("=" * 70)
print("📊 RESULT")
print("=" * 70)
print(f"Success: {result['success']}")
print(f"Response: {result['response'][:200] if result['response'] else 'None'}...")
print()

thea.cleanup()
print("✅ Demo complete!")
print()
