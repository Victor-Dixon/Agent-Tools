#!/usr/bin/env python3
"""
Post Family Business Blog to dadudekc.com
========================================

Posts the "When You're Building a Family Business, Motivation Is the Real Product" blog post.

Author: Agent-2
V2 Compliant: <300 lines
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load credentials
creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
with open(creds_file) as f:
    creds_data = json.load(f)

SITE_CONFIG = creds_data["dadudekc.com"]
SITE_URL = SITE_CONFIG["site_url"]
USERNAME = SITE_CONFIG["username"]
APP_PASSWORD = SITE_CONFIG["app_password"]

API_BASE = f"{SITE_URL}/wp-json/wp/v2"
AUTH = HTTPBasicAuth(USERNAME, APP_PASSWORD.replace(" ", ""))

# Blog content
TITLE = "When You're Building a Family Business, Motivation Is the Real Product"

CONTENT = """<p>I've been in the trenches lately.<br>
Building funnels. Standing up websites. Pushing offers live.<br>
At the same time I'm trying to turn a family setup into something that actually operates like a business.</p>

<p>What I didn't expect is how fast this turned into a motivation audit.</p>

<p>Because once you stop talking about the dream and start asking people to do small, real tasks consistently, everything becomes obvious.<br>
Who moves. Who stalls. Who needs structure. Who needs accountability. Who needs a completely different lane.</p>

<p>This isn't about blaming anyone.<br>
It's me saying the quiet part out loud because I'm learning it in real time, and I know other founders are too.</p>

<p>If this thing becomes real, it's because I carried it through the ugly middle.<br>
The setup work.<br>
The follow ups.<br>
The edits.<br>
The posting.<br>
The systems.<br>
The consistency.</p>

<p>Right now, I'm the engine.</p>

<p>That's not a flex. That's a responsibility. And if I don't build this right, that responsibility turns into burnout real fast.</p>

<p>So the real question I'm wrestling with is how to build a family team that works without me dragging every wheel onto the track myself.</p>

<h2>Corey is easy to place.</h2>

<p>He doesn't have unlimited time, but he does have ambition, vision, work ethic, and leadership instincts. That's co-CEO energy. Not everyone is built for daily execution, but the people who can think clearly, decide, and move the mission forward are rare. Corey is someone I'd confidently build with long term.</p>

<p>What I see forming is me and Corey as the core company.<br>
Under that umbrella, brands like Houston Sip Queen can live as sister companies. Which is funny because it's literally my sister's brand.</p>

<h2>Catera is more complicated.</h2>

<p>Not because she can't do the work, but because the motivation doesn't consistently show up yet. I thought money would do it. I thought vision would do it. Right now neither one hits reliably.</p>

<p>So instead of forcing a partner role that creates friction, the smarter move is treating her as a contractor. Clear tasks. Clear pay. Clear expectations. Measurable output.</p>

<p>At the same time, I'm still trying to answer the real question. What actually motivates her. Because everyone has a button, and if I find it, her output could change completely.</p>

<h2>Then there's the harder lesson.</h2>

<p>Some people don't struggle with skill. They struggle with ownership.</p>

<p>I've seen moments where something needed to get done and the attitude was basically "that's not my job." Anyone who's worked service or events knows how this goes. Sometimes the work is glamorous. Sometimes it's cleanup.</p>

<p>Startups are mostly cleanup.</p>

<p>If someone can't accept that, they're not ready for a startup environment. So I'm not betting the company on potential anymore. I'm betting it on proof.</p>

<h2>The kids part is the funniest and the most stressful at the same time.</h2>

<p>Of course I want my kids to be stars. I want them learning early. I want them winning. But reality doesn't care about intentions.</p>

<p>Ari is supposed to be my star, but lately it's felt like Petey from Remember the Titans. Dropped passes. Missed routes. And it hurts more because the expectation is higher when the experience is supposed to be there.</p>

<p>As a dad, the fear is simple. If you think you're a wolf but move like a lamb, the world will eat you. Not because the world is evil, but because it's competitive.</p>

<p>Carmyn is the opposite. She's trying. She's pushing. She's showing up with that "I think I can" energy. She's not fully there yet, but effort matters. Consistency matters. I'll build with a learner who shows up before I build with a natural who doesn't.</p>

<p>The part that makes me pause is that Carmyn is about where Ari is right now, and Ari has more years in. That tells me this isn't about talent. It's about habits.</p>

<p>Then there's Kiki. No show. And honestly, no surprise. The pattern has been the pattern.</p>

<p>Some people aren't bad people. They're just not reliable. And reliability is the foundation of business.</p>

<h2>What I'm learning is that family teams need lanes, not hope.</h2>

<p>I used to think building a family business was about love, loyalty, and shared dreams. Now I see it's closer to building a sports team. You don't give everyone the same position. You don't pay everyone the same. You don't run plays based on "they should want it." You run plays based on what people consistently prove.</p>

<p>So the next phase is structure.</p>

<ul>
<li>Core leadership is me and Corey.</li>
<li>Brands like Houston Sip Queen live under one umbrella.</li>
<li>Contractor roles get paid for output, not potential.</li>
<li>Clear task boards. One task, one owner, one deadline.</li>
<li>A weekly scoreboard so progress is visible.</li>
</ul>

<p>No more confusion. No more waiting on vibes.</p>

<p>I love my family. That part isn't in question.<br>
But love doesn't replace systems.</p>

<p>If I want this to become a real business that produces income, stability, and pride, I have to build it like a real business. Clear roles. Clear expectations. Real accountability.</p>

<p>The dream is free.<br>
Execution costs.</p>

<p>If you're building something with family or friends, I'd actually love to hear your situation. What worked, what didn't, and what you had to change to protect both the business and the relationships.</p>"""

EXCERPT = "Building a family business means learning who moves, who stalls, and who needs a different lane. Here's what I'm learning in real time about motivation, structure, and building a team that actually works."

TAGS = ["business", "family-business", "leadership",
        "startups", "team-building", "motivation"]
CATEGORY = "Development"  # Using existing category from config


def get_or_create_category(category_name: str):
    """Get or create a category."""
    # First, try to get existing category
    url = f"{API_BASE}/categories"
    params = {"search": category_name, "per_page": 100}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        categories = response.json()
        for cat in categories:
            if cat["name"].lower() == category_name.lower():
                return cat["id"]

    # Create category if not found
    url = f"{API_BASE}/categories"
    data = {"name": category_name}
    response = requests.post(url, json=data, auth=AUTH, timeout=30)

    if response.status_code == 201:
        return response.json()["id"]

    return None


def get_or_create_tags(tag_names: list):
    """Get or create tags, return list of tag IDs."""
    tag_ids = []

    for tag_name in tag_names:
        # Try to get existing tag
        url = f"{API_BASE}/tags"
        params = {"search": tag_name, "per_page": 100}
        response = requests.get(url, params=params, auth=AUTH, timeout=30)

        if response.status_code == 200:
            tags = response.json()
            for tag in tags:
                if tag["name"].lower() == tag_name.lower():
                    tag_ids.append(tag["id"])
                    break
            else:
                # Create tag if not found
                url = f"{API_BASE}/tags"
                data = {"name": tag_name}
                response = requests.post(url, json=data, auth=AUTH, timeout=30)
                if response.status_code == 201:
                    tag_ids.append(response.json()["id"])

    return tag_ids


def check_existing_post(title: str):
    """Check if post with this title already exists."""
    url = f"{API_BASE}/posts"
    params = {"search": title, "per_page": 10}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        posts = response.json()
        for post in posts:
            if post["title"]["rendered"] == title:
                return post
    return None


def create_post():
    """Create the blog post."""
    print(f"📝 Posting blog to {SITE_URL}...")

    # Check if post already exists
    existing = check_existing_post(TITLE)
    if existing:
        print(f"  ⚠️  Post already exists: {existing['link']}")
        return existing

    # Get or create category
    print(f"  📂 Getting category: {CATEGORY}")
    category_id = get_or_create_category(CATEGORY)
    if not category_id:
        print(f"  ⚠️  Could not get/create category, continuing anyway...")

    # Get or create tags
    print(f"  🏷️  Getting/creating tags: {', '.join(TAGS)}")
    tag_ids = get_or_create_tags(TAGS)

    # Prepare post data
    post_data = {
        "title": TITLE,
        "content": CONTENT,
        "excerpt": EXCERPT,
        "status": "publish",
        "format": "standard",
    }

    if category_id:
        post_data["categories"] = [category_id]

    if tag_ids:
        post_data["tags"] = tag_ids

    # Create post
    print(f"  ✍️  Creating post: {TITLE}")
    url = f"{API_BASE}/posts"
    response = requests.post(url, json=post_data, auth=AUTH, timeout=30)

    if response.status_code == 201:
        post = response.json()
        print(f"  ✅ Post created successfully!")
        print(f"     Post ID: {post['id']}")
        print(f"     URL: {post['link']}")
        print(f"     Status: {post['status']}")
        return post
    else:
        print(f"  ❌ Error creating post: {response.status_code}")
        print(f"     Response: {response.text}")
        return None


def main():
    """Main execution."""
    print("🚀 Posting family business blog to dadudekc.com\n")

    post = create_post()

    if post:
        print(f"\n✅ Blog post published successfully!")
        print(f"   View at: {post['link']}")
    else:
        print(f"\n❌ Failed to publish blog post")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
