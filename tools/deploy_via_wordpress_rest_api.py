"""
Deploy via WordPress REST API
==============================

Uses WordPress REST API to deploy theme files programmatically.
More reliable than browser automation - direct API calls.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
"""

import base64
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("❌ requests not installed. Install with: pip install requests")
    sys.exit(1)


class WordPressRESTAPI:
    """WordPress REST API client for file deployment."""
    
    def __init__(self, site_url: str, username: str, password: str):
        """
        Initialize WordPress REST API client.
        
        Args:
            site_url: WordPress site URL (e.g., https://example.com)
            username: WordPress username
            password: WordPress application password (not regular password)
        """
        self.site_url = site_url.rstrip('/')
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.username = username
        self.password = password
        self.session = requests.Session()
        
        # Basic auth for REST API
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.session.headers.update({
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        })
    
    def check_api_availability(self) -> bool:
        """Check if WordPress REST API is available."""
        try:
            response = self.session.get(f"{self.site_url}/wp-json/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ WordPress REST API available: {data.get('name', 'Unknown')}")
                return True
            else:
                print(f"⚠️  WordPress REST API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error checking REST API: {e}")
            return False
    
    def update_theme_file(
        self,
        theme: str,
        file_path: str,
        file_content: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Update a theme file via REST API using custom plugin endpoint.
        
        Requires: Theme File Editor API plugin installed and activated.
        
        Args:
            theme: Theme name
            file_path: File path relative to theme (e.g., 'functions.php')
            file_content: New file content
            dry_run: If True, only validate without updating
            
        Returns:
            Dict with success status and message
        """
        if dry_run:
            print(f"🔍 DRY RUN: Would update {file_path} in theme {theme}")
            print(f"   Content length: {len(file_content)} bytes")
            return {
                "success": True,
                "message": "Dry run completed - no changes made",
                "dry_run": True
            }
        
        # Use custom plugin endpoint
        endpoint = f"{self.site_url}/wp-json/theme-file-editor/v1/update-file"
        
        payload = {
            "theme": theme,
            "file": file_path,
            "content": file_content
        }
        
        try:
            print(f"📤 Sending file update request to: {endpoint}")
            print(f"   Theme: {theme}")
            print(f"   File: {file_path}")
            print(f"   Content size: {len(file_content):,} bytes")
            
            response = self.session.post(endpoint, json=payload, timeout=TimeoutConstants.HTTP_DEFAULT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ File updated successfully!")
                    print(f"   Bytes written: {data.get('bytes_written', 'N/A'):,}")
                    return {
                        "success": True,
                        "message": data.get("message", "File updated successfully"),
                        "bytes_written": data.get("bytes_written", 0)
                    }
                else:
                    error_msg = data.get("message", "Unknown error")
                    print(f"❌ Update failed: {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg
                    }
            elif response.status_code == 401:
                print("❌ Authentication failed - check username and application password")
                return {
                    "success": False,
                    "message": "Authentication failed - check credentials"
                }
            elif response.status_code == 403:
                error_data = response.json()
                error_msg = error_data.get("message", "Permission denied")
                print(f"❌ Permission denied: {error_msg}")
                print("💡 Ensure:")
                print("   - User has Administrator role")
                print("   - DISALLOW_FILE_EDIT is not set in wp-config.php")
                return {
                    "success": False,
                    "message": error_msg
                }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("message", f"HTTP {response.status_code}")
                print(f"❌ Update failed: {error_msg}")
                return {
                    "success": False,
                    "message": error_msg,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout - server may be slow or unreachable")
            return {
                "success": False,
                "message": "Request timeout"
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return {
                "success": False,
                "message": f"Request failed: {e}"
            }
    
    def get_theme_file(
        self,
        theme: str,
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get theme file content via REST API.
        
        Args:
            theme: Theme name
            file_path: File path relative to theme
            
        Returns:
            Dict with file content or None if error
        """
        endpoint = f"{self.site_url}/wp-json/theme-file-editor/v1/get-file"
        
        params = {
            "theme": theme,
            "file": file_path
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=TimeoutConstants.HTTP_DEFAULT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {
                        "content": data.get("content", ""),
                        "size": data.get("size", 0),
                        "file": data.get("file", file_path),
                        "theme": data.get("theme", theme)
                    }
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("message", f"HTTP {response.status_code}")
                print(f"❌ Failed to get file: {error_msg}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting file: {e}")
            return None
    
    def check_plugin_installed(self) -> bool:
        """Check if Theme File Editor API plugin is installed."""
        endpoint = f"{self.site_url}/wp-json/theme-file-editor/v1/update-file"
        
        try:
            # Try a test request (will fail auth but should return 401, not 404)
            response = self.session.post(endpoint, json={}, timeout=TimeoutConstants.HTTP_QUICK)
            
            # 404 means endpoint doesn't exist (plugin not installed)
            if response.status_code == 404:
                return False
            
            # 401/403 means endpoint exists but auth/permission failed (plugin installed)
            return response.status_code in (401, 403, 400)
            
        except:
            return False


def deploy_via_rest_api(
    site_url: str,
    theme: str,
    file_path: Path,
    username: Optional[str] = None,
    password: Optional[str] = None,
    dry_run: bool = False
) -> bool:
    """
    Deploy file via WordPress REST API.
    
    Args:
        site_url: WordPress site URL
        theme: Theme name
        file_path: Local file path to deploy
        username: WordPress username (or from .env)
        password: WordPress application password (or from .env)
        dry_run: If True, only validate without deploying
        
    Returns:
        True if successful, False otherwise
    """
    if not HAS_REQUESTS:
        print("❌ requests library not installed")
        return False
    
    # Get credentials
    username = username or os.getenv("WORDPRESS_USER")
    password = password or os.getenv("WORDPRESS_APP_PASSWORD")
    
    if not username or not password:
        print("❌ WordPress credentials not provided")
        print("💡 Set WORDPRESS_USER and WORDPRESS_APP_PASSWORD in .env")
        print("💡 Note: Use Application Password, not regular password")
        return False
    
    # Read file content
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # Initialize API client
    api = WordPressRESTAPI(site_url, username, password)
    
    # Check API availability
    if not api.check_api_availability():
        print("❌ WordPress REST API not available")
        return False
    
    # Check if plugin is installed
    print("🔍 Checking for Theme File Editor API plugin...")
    if not api.check_plugin_installed():
        print("❌ Theme File Editor API plugin not installed")
        print("💡 Install the plugin from: websites/wordpress-plugins/theme-file-editor-api/")
        print("💡 Or use browser automation: deploy_via_wordpress_admin.py")
        return False
    
    print("✅ Theme File Editor API plugin detected")
    print()
    
    # Attempt deployment
    result = api.update_theme_file(theme, file_path.name, file_content, dry_run)
    
    if result["success"]:
        print("✅ File deployed successfully via REST API")
        return True
    else:
        print(f"⚠️  {result['message']}")
        if "alternative" in result:
            print(f"💡 {result['alternative']}")
        return False


def main():
    """Main CLI entry point."""
    import argparse
    from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(description="Deploy file via WordPress REST API")
    parser.add_argument("--site", required=True, help="WordPress site URL")
    parser.add_argument("--theme", required=True, help="Theme name")
    parser.add_argument("--file", required=True, type=Path, help="File path to deploy")
    parser.add_argument("--username", help="WordPress username (or use .env)")
    parser.add_argument("--password", help="WordPress app password (or use .env)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without deploying")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 WordPress REST API Deployment")
    print("=" * 60)
    print()
    
    success = deploy_via_rest_api(
        site_url=args.site,
        theme=args.theme,
        file_path=args.file,
        username=args.username,
        password=args.password,
        dry_run=args.dry_run
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

