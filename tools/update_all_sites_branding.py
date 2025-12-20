#!/usr/bin/env python3
"""
Update All Sites with Swarm Branding
====================================

Removes Flavio restaurant branding and applies Swarm branding to all WordPress sites.

Author: Agent-1 (Integration & Core Systems Specialist)
"""

import sys
from pathlib import Path
from typing import List, Dict

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from wordpress_manager import WordPressManager
except ImportError:
    print("❌ wordpress_manager not available")
    sys.exit(1)


SITES_TO_UPDATE = [
    "weareswarm.online",
    "weareswarm.site",
    "prismblossom.online",
    "freerideinvestor",
    "southwestsecret",  # Fixed: use site_key from config
    "ariajet.site",
    "tradingrobotplug.com",
    "dadudekc.com",
]

SWARM_MENU_ITEMS = [
    {"title": "Capabilities", "url": "/#capabilities"},
    {"title": "Live Activity", "url": "/#activity"},
    {"title": "Agents", "url": "/#agents"},
    {"title": "About", "url": "/about"},
]

RESTAURANT_MENU_ITEMS_TO_REMOVE = [
    "Our Menu",
    "Menu",
    "Hi tory",
    "History",
    "Make Reservation",
    "Reservation",
    "Contact",
    "About Us",
]


def create_swarm_menu(manager: WordPressManager, menu_name: str = "Swarm Primary") -> bool:
    """Create or update Swarm menu."""
    import json
    
    # Check if menu exists
    stdout, stderr, code = manager.wp_cli("menu list --format=json")
    if code != 0:
        print(f"❌ Failed to list menus: {stderr}")
        return False
    
    menus = json.loads(stdout) if stdout.strip() else []
    menu_id = None
    
    for menu in menus:
        if menu.get("name") == menu_name:
            menu_id = menu.get("term_id")
            break
    
    # Create menu if it doesn't exist
    if not menu_id:
        stdout, stderr, code = manager.wp_cli(f'menu create "{menu_name}"')
        if code != 0:
            print(f"❌ Failed to create menu: {stderr}")
            return False
        
        # Get menu ID
        stdout, stderr, code = manager.wp_cli("menu list --format=json")
        menus = json.loads(stdout) if stdout.strip() else []
        for menu in menus:
            if menu.get("name") == menu_name:
                menu_id = menu.get("term_id")
                break
    
    if not menu_id:
        print(f"❌ Could not create or find menu: {menu_name}")
        return False
    
    # Clear existing items
    stdout, stderr, code = manager.wp_cli(f'menu item list "{menu_name}" --format=json')
    if code == 0 and stdout.strip():
        items = json.loads(stdout)
        for item in items:
            item_id = item.get("db_id")
            if item_id:
                manager.wp_cli(f'menu item delete {item_id}')
    
    # Add Swarm menu items
    # Try to get site URL from config or infer from site_key
    site_url = "https://example.com"
    if hasattr(manager, '_get_site_url'):
        site_url = manager._get_site_url() or site_url
    elif manager.site_key:
        # Infer URL from site_key
        domain = manager.site_key.replace(".online", "").replace(".site", "").replace(".com", "")
        for tld in [".com", ".online", ".site"]:
            if manager.site_key.endswith(tld):
                site_url = f"https://{manager.site_key}"
                break
            elif f"{domain}{tld}" in manager.site_key:
                site_url = f"https://{manager.site_key}"
                break
    for item in SWARM_MENU_ITEMS:
        url = item["url"]
        if not url.startswith("http"):
            url = f"{site_url}{url}"
        
        stdout, stderr, code = manager.wp_cli(
            f'menu item add-custom "{menu_name}" "{item["title"]}" {url}'
        )
        if code != 0:
            print(f"⚠️  Warning: Failed to add menu item '{item['title']}': {stderr}")
    
    # Check available menu locations
    stdout, stderr, code = manager.wp_cli("menu location list --format=json")
    locations = []
    if code == 0 and stdout.strip():
        try:
            locations_data = json.loads(stdout)
            locations = [loc.get("location") for loc in locations_data]
        except:
            pass
    
    # Assign to primary location (or first available location)
    target_location = "primary" if "primary" in locations else (locations[0] if locations else None)
    
    if target_location:
        stdout, stderr, code = manager.wp_cli(f'menu location assign "{menu_name}" {target_location}')
        if code == 0:
            print(f"✅ Menu '{menu_name}' assigned to {target_location} location")
            return True
        else:
            print(f"⚠️  Warning: Failed to assign menu to {target_location}: {stderr}")
            # Try to assign to any location
            if locations:
                for loc in locations:
                    stdout, stderr, code = manager.wp_cli(f'menu location assign "{menu_name}" {loc}')
                    if code == 0:
                        print(f"✅ Menu '{menu_name}' assigned to {loc} location")
                        return True
    else:
        print(f"⚠️  Warning: No menu locations found")
    
    return False


def remove_restaurant_menu_items(manager: WordPressManager) -> bool:
    """Remove restaurant menu items from all menus."""
    import json
    
    stdout, stderr, code = manager.wp_cli("menu list --format=json")
    if code != 0:
        return False
    
    menus = json.loads(stdout) if stdout.strip() else []
    removed_count = 0
    
    for menu in menus:
        menu_name = menu.get("name")
        stdout, stderr, code = manager.wp_cli(f'menu item list "{menu_name}" --format=json')
        if code != 0:
            continue
        
        items = json.loads(stdout) if stdout.strip() else []
        for item in items:
            title = item.get("title", "").lower()
            url = item.get("url", "").lower()
            
            # Check if it's a restaurant item
            is_restaurant = False
            for restaurant_item in RESTAURANT_MENU_ITEMS_TO_REMOVE:
                if restaurant_item.lower() in title or "menu" in url or "reservation" in url:
                    is_restaurant = True
                    break
            
            if is_restaurant:
                item_id = item.get("db_id")
                if item_id:
                    manager.wp_cli(f'menu item delete {item_id}')
                    removed_count += 1
                    print(f"  ✅ Removed: {item.get('title')}")
    
    return removed_count > 0


def update_site_branding(site_key: str) -> Dict[str, any]:
    """Update branding for a single site."""
    print(f"\n{'='*60}")
    print(f"🎨 Updating branding for: {site_key}")
    print(f"{'='*60}")
    
    result = {
        "site": site_key,
        "success": False,
        "errors": [],
        "actions": []
    }
    
    try:
        manager = WordPressManager(site_key)
        
        if not manager.connect():
            result["errors"].append("Failed to connect")
            return result
        
        # Step 1: Remove restaurant menu items
        print("\n1️⃣ Removing restaurant menu items...")
        if remove_restaurant_menu_items(manager):
            result["actions"].append("Removed restaurant menu items")
        
        # Step 2: Create/update Swarm menu
        print("\n2️⃣ Creating Swarm menu...")
        if create_swarm_menu(manager):
            result["actions"].append("Created Swarm menu")
        
        # Step 3: Flush cache
        print("\n3️⃣ Flushing cache...")
        if manager.purge_caches():
            result["actions"].append("Cache flushed")
        
        result["success"] = True
        print(f"\n✅ Successfully updated {site_key}")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"\n❌ Error updating {site_key}: {e}")
    
    finally:
        if 'manager' in locals():
            manager.disconnect()
    
    return result


def main():
    """Main execution."""
    print("🐝 Swarm Branding Update Tool")
    print("=" * 60)
    print(f"Updating {len(SITES_TO_UPDATE)} sites...")
    print()
    
    results = []
    
    for site in SITES_TO_UPDATE:
        result = update_site_branding(site)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    for result in successful:
        print(f"   - {result['site']}: {', '.join(result['actions'])}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(results)}")
        for result in failed:
            print(f"   - {result['site']}: {', '.join(result['errors'])}")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

