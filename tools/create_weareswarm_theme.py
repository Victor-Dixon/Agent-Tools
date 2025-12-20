#!/usr/bin/env python3
"""
Create WeAreSwarm.online Theme
==============================

Creates a professional dark tech theme for weareswarm.online with modern styling.

Author: Agent-2
V2 Compliant: <300 lines
"""

import json
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load credentials
creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
with open(creds_file) as f:
    creds_data = json.load(f)

SITE_CONFIG = creds_data["weareswarm.online"]
SITE_URL = SITE_CONFIG["site_url"]
USERNAME = SITE_CONFIG["username"]
APP_PASSWORD = SITE_CONFIG["app_password"]

API_BASE = f"{SITE_URL}/wp-json/wp/v2"
AUTH = HTTPBasicAuth(USERNAME, APP_PASSWORD.replace(" ", ""))


def get_weareswarm_theme_css() -> str:
    """Generate WeAreSwarm tech theme CSS."""
    return """
/* WeAreSwarm.online - Tech Theme */
/* Brand: Multi-Agent Swarm System */
/* Applied: 2025-12-19 */

/* Color Palette */
:root {
    --swarm-dark: #0a0a0f;
    --swarm-darker: #050508;
    --swarm-blue: #00d4ff;
    --swarm-cyan: #00ffff;
    --swarm-purple: #8b5cf6;
    --swarm-text: #e5e7eb;
    --swarm-text-dim: #9ca3af;
    --swarm-card: #1a1a24;
    --swarm-border: #2d2d3a;
}

/* Base Typography */
body,
body * {
    font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    color: var(--swarm-text) !important;
    background-color: var(--swarm-dark) !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6,
.wp-block-heading,
h1.wp-block-heading,
h2.wp-block-heading,
h3.wp-block-heading {
    font-family: 'Inter', 'SF Pro Display', sans-serif !important;
    font-weight: 700 !important;
    color: var(--swarm-text) !important;
    line-height: 1.3 !important;
}

h1, h1.wp-block-heading {
    font-size: 2.5em !important;
    color: var(--swarm-cyan) !important;
}

h2, h2.wp-block-heading {
    font-size: 2em !important;
    color: var(--swarm-blue) !important;
    border-bottom: 2px solid var(--swarm-border) !important;
    padding-bottom: 0.5rem !important;
    margin-top: 2rem !important;
}

h3, h3.wp-block-heading {
    font-size: 1.5em !important;
    color: var(--swarm-text) !important;
}

/* Links */
a {
    color: var(--swarm-cyan) !important;
    text-decoration: none !important;
    transition: color 0.2s ease !important;
}

a:hover {
    color: var(--swarm-blue) !important;
}

/* Buttons */
.wp-block-button__link,
.wp-element-button,
button,
input[type="submit"],
a.button {
    background: linear-gradient(135deg, var(--swarm-blue) 0%, var(--swarm-purple) 100%) !important;
    color: var(--swarm-dark) !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

.wp-block-button__link:hover,
.wp-element-button:hover,
button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 16px rgba(0, 212, 255, 0.3) !important;
}

/* Cards */
.wp-block-group,
.wp-block-columns,
article,
.post {
    background: var(--swarm-card) !important;
    border: 1px solid var(--swarm-border) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
}

/* Code Blocks */
pre,
code,
.wp-block-code {
    background: var(--swarm-darker) !important;
    color: var(--swarm-cyan) !important;
    border: 1px solid var(--swarm-border) !important;
    border-radius: 6px !important;
    padding: 1rem !important;
    font-family: 'Fira Code', 'Consolas', monospace !important;
}

/* Activity Feed Styling */
.swarm-activity-item {
    background: var(--swarm-card) !important;
    border-left: 4px solid var(--swarm-blue) !important;
    padding: 1rem !important;
    margin: 0.75rem 0 !important;
    border-radius: 6px !important;
}

.swarm-activity-meta {
    color: var(--swarm-text-dim) !important;
    font-size: 0.875rem !important;
    margin-bottom: 0.5rem !important;
}

/* Navigation */
nav,
.wp-block-navigation {
    background: var(--swarm-darker) !important;
    border-bottom: 1px solid var(--swarm-border) !important;
}

nav a,
.wp-block-navigation a {
    color: var(--swarm-text) !important;
}

nav a:hover,
.wp-block-navigation a:hover {
    color: var(--swarm-cyan) !important;
}

/* Footer */
footer,
.site-footer {
    background: var(--swarm-darker) !important;
    border-top: 1px solid var(--swarm-border) !important;
    color: var(--swarm-text-dim) !important;
}

/* Responsive */
@media (max-width: 768px) {
    h1, h1.wp-block-heading {
        font-size: 2em !important;
    }
    
    h2, h2.wp-block-heading {
        font-size: 1.5em !important;
    }
}
"""


def deploy_theme_css():
    """Deploy theme CSS to WordPress via Additional CSS."""
    print(f"🎨 Deploying WeAreSwarm theme to {SITE_URL}...")

    css_content = get_weareswarm_theme_css()

    # WordPress doesn't have a direct API for Additional CSS, so we'll create a custom CSS file
    # that can be enqueued via a plugin or functions.php

    # For now, we'll create instructions and save the CSS file
    css_file = project_root / "sites" / "weareswarm.online" / "swarm_theme.css"
    css_file.parent.mkdir(parents=True, exist_ok=True)
    css_file.write_text(css_content, encoding='utf-8')

    print(f"  ✅ Theme CSS saved to: {css_file}")
    print(f"  📝 Next steps:")
    print(f"     1. Upload {css_file.name} to WordPress")
    print(f"     2. Add to Appearance → Additional CSS, OR")
    print(f"     3. Enqueue via functions.php or a custom plugin")

    return True


def main():
    """Main execution."""
    print("🚀 Creating WeAreSwarm.online theme\n")

    success = deploy_theme_css()

    if success:
        print(f"\n✅ Theme creation complete!")
        print(f"   CSS file ready for deployment")
    else:
        print(f"\n❌ Failed to create theme")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
