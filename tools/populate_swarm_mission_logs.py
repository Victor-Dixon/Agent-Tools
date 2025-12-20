#!/usr/bin/env python3
"""
Populate Swarm Mission Logs
===========================

Tool to populate mission logs for the Swarm Intelligence theme's live activity feed.
Uses WP-CLI to directly set WordPress options.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from wordpress_manager import WordPressManager
except ImportError:
    print("❌ wordpress_manager not available")
    sys.exit(1)


def populate_sample_logs(site_key: str = "weareswarm.online") -> bool:
    """Populate sample mission logs for testing."""
    manager = WordPressManager(site_key)
    
    if not manager.connect():
        print(f"❌ Failed to connect to {site_key}")
        return False
    
    # Sample mission logs (newest first)
    base_time = int(datetime.now().timestamp())
    sample_logs = [
        {
            "id": f"log_{base_time + 4}",
            "agent": "Captain Agent-4",
            "message": "Swarm coordination active - all agents operational",
            "priority": "normal",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "unix_timestamp": base_time + 4,
            "tags": ["coordination", "status"]
        },
        {
            "id": f"log_{base_time + 3}",
            "agent": "Agent-1",
            "message": "Navigation menus updated - restaurant branding removed",
            "priority": "normal",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "unix_timestamp": base_time + 3,
            "tags": ["branding", "navigation", "cleanup"]
        },
        {
            "id": f"log_{base_time + 2}",
            "agent": "Agent-2",
            "message": "V2 compliance exception approved for wordpress_manager.py",
            "priority": "normal",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "unix_timestamp": base_time + 2,
            "tags": ["v2", "compliance", "architecture"]
        },
        {
            "id": f"log_{base_time + 1}",
            "agent": "Agent-7",
            "message": "Swarm Intelligence theme activated on weareswarm.online",
            "priority": "normal",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "unix_timestamp": base_time + 1,
            "tags": ["theme", "activation", "web"]
        },
        {
            "id": f"log_{base_time}",
            "agent": "Agent-1",
            "message": "Swarm branding tools created and deployed successfully",
            "priority": "normal",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "unix_timestamp": base_time,
            "tags": ["branding", "deployment", "tools"]
        },
    ]
    
    print(f"📝 Adding {len(sample_logs)} mission log entries to {site_key}...")
    
    # Convert to JSON
    logs_json = json.dumps(sample_logs)
    
    # Use WP-CLI eval to set the option directly
    # Escape JSON for PHP string
    escaped_json = logs_json.replace("\\", "\\\\").replace("'", "\\'")
    
    php_code = f"update_option('swarm_mission_logs', json_decode('{escaped_json}', true)); echo 'success';"
    
    stdout, stderr, code = manager.wp_cli(f'eval "{php_code}"')
    
    if code == 0:
        print(f"✅ Successfully added {len(sample_logs)} mission logs")
        
        # Verify
        stdout, stderr, code = manager.wp_cli("option get swarm_mission_logs --format=json")
        if code == 0 and stdout.strip():
            try:
                stored_logs = json.loads(stdout)
                print(f"✅ Verified: {len(stored_logs)} logs stored")
            except Exception as e:
                print(f"⚠️  Verification parse error: {e}")
        
        # Flush cache
        manager.purge_caches()
        return True
    else:
        print(f"❌ Failed to add mission logs: {stderr}")
        return False


def add_single_log(site_key: str, agent: str, message: str, 
                  priority: str = "normal", tags: Optional[List[str]] = None) -> bool:
    """Add a single mission log entry."""
    manager = WordPressManager(site_key)
    
    if not manager.connect():
        print(f"❌ Failed to connect to {site_key}")
        return False
    
    # Get existing logs
    stdout, stderr, code = manager.wp_cli("option get swarm_mission_logs --format=json")
    existing_logs = []
    if code == 0 and stdout.strip():
        try:
            existing_logs = json.loads(stdout)
        except:
            pass
    
    # Create new log entry
    new_log = {
        "id": f"log_{int(datetime.now().timestamp())}",
        "agent": agent,
        "message": message,
        "priority": priority,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unix_timestamp": int(datetime.now().timestamp()),
    }
    
    if tags:
        new_log["tags"] = tags
    
    # Add to beginning (newest first)
    existing_logs.insert(0, new_log)
    
    # Keep last 200
    existing_logs = existing_logs[:200]
    
    # Save via WP-CLI
    logs_json = json.dumps(existing_logs)
    escaped_json = logs_json.replace("\\", "\\\\").replace("'", "\\'")
    php_code = f"update_option('swarm_mission_logs', json_decode('{escaped_json}', true)); echo 'success';"
    
    stdout, stderr, code = manager.wp_cli(f'eval "{php_code}"')
    
    if code == 0:
        print(f"✅ Mission log added: {agent} - {message[:50]}...")
        manager.purge_caches()
        return True
    else:
        print(f"❌ Failed to add mission log: {stderr}")
        return False


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate Swarm mission logs")
    parser.add_argument("--site", default="weareswarm.online", help="Site key")
    parser.add_argument("--agent", help="Agent name")
    parser.add_argument("--message", help="Mission log message")
    parser.add_argument("--priority", default="normal", choices=["normal", "urgent"], 
                       help="Priority level")
    parser.add_argument("--tags", nargs="+", help="Tags for the log entry")
    parser.add_argument("--sample", action="store_true", 
                       help="Populate sample mission logs")
    
    args = parser.parse_args()
    
    if args.sample:
        success = populate_sample_logs(args.site)
        sys.exit(0 if success else 1)
    elif args.agent and args.message:
        success = add_single_log(args.site, args.agent, args.message, 
                               args.priority, args.tags)
        sys.exit(0 if success else 1)
    else:
        print("Usage:")
        print("  --sample                    Populate sample logs")
        print("  --agent NAME --message MSG  Add single log entry")
        sys.exit(1)


if __name__ == "__main__":
    main()
