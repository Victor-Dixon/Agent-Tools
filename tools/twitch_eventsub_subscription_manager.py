#!/usr/bin/env python3
"""
Twitch EventSub Subscription Manager
====================================

Tool to manage Twitch EventSub webhook subscriptions via CLI.

Allows creating, listing, and deleting EventSub subscriptions without
manual API calls.

V2 Compliance: <400 lines, single responsibility
Author: Agent-4 (Captain)
Created: 2025-12-15
License: MIT
"""

import os
import sys
import json
import requests
from typing import Optional, Dict, Any
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TwitchEventSubManager:
    """Manage Twitch EventSub webhook subscriptions."""
    
    def __init__(
        self,
        client_id: str,
        access_token: str,
        webhook_secret: Optional[str] = None,
        webhook_url: Optional[str] = None,
    ):
        """
        Initialize EventSub manager.
        
        Args:
            client_id: Twitch API client ID
            access_token: Twitch API access token (OAuth)
            webhook_secret: Webhook secret for subscriptions
            webhook_url: Webhook callback URL
        """
        self.client_id = client_id
        self.access_token = access_token
        self.webhook_secret = webhook_secret
        self.webhook_url = webhook_url
        self.api_base = "https://api.twitch.tv/helix/eventsub/subscriptions"
        
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    def create_subscription(
        self,
        event_type: str,
        broadcaster_user_id: str,
        webhook_url: Optional[str] = None,
        webhook_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create EventSub webhook subscription.
        
        Args:
            event_type: Event type (e.g., "channel.channel_points_custom_reward_redemption.add")
            broadcaster_user_id: Twitch broadcaster user ID
            webhook_url: Webhook callback URL (uses instance default if not provided)
            webhook_secret: Webhook secret (uses instance default if not provided)
            
        Returns:
            API response with subscription details
        """
        url = webhook_url or self.webhook_url
        secret = webhook_secret or self.webhook_secret
        
        if not url:
            raise ValueError("webhook_url required (set via parameter or instance)")
        if not secret:
            raise ValueError("webhook_secret required (set via parameter or instance)")
        
        payload = {
            "type": event_type,
            "version": "1",
            "condition": {
                "broadcaster_user_id": broadcaster_user_id,
            },
            "transport": {
                "method": "webhook",
                "callback": url,
                "secret": secret,
            },
        }
        
        response = requests.post(
            self.api_base,
            headers=self._get_headers(),
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    
    def list_subscriptions(
        self,
        status: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List EventSub subscriptions.
        
        Args:
            status: Filter by status (optional)
            event_type: Filter by event type (optional)
            
        Returns:
            API response with subscription list
        """
        params = {}
        if status:
            params["status"] = status
        if event_type:
            params["type"] = event_type
        
        response = requests.get(
            self.api_base,
            headers=self._get_headers(),
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    
    def delete_subscription(self, subscription_id: str) -> bool:
        """
        Delete EventSub subscription.
        
        Args:
            subscription_id: Subscription ID to delete
            
        Returns:
            True if successful
        """
        response = requests.delete(
            f"{self.api_base}?id={subscription_id}",
            headers=self._get_headers(),
            timeout=10,
        )
        response.raise_for_status()
        return True
    
    def create_channel_points_subscription(
        self,
        broadcaster_user_id: str,
        webhook_url: Optional[str] = None,
        webhook_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create subscription for channel points redemptions.
        
        Convenience method for the most common use case.
        
        Args:
            broadcaster_user_id: Twitch broadcaster user ID
            webhook_url: Webhook callback URL
            webhook_secret: Webhook secret
            
        Returns:
            API response with subscription details
        """
        return self.create_subscription(
            event_type="channel.channel_points_custom_reward_redemption.add",
            broadcaster_user_id=broadcaster_user_id,
            webhook_url=webhook_url,
            webhook_secret=webhook_secret,
        )


def main():
    """CLI interface for EventSub subscription management."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage Twitch EventSub webhook subscriptions"
    )
    parser.add_argument(
        "--client-id",
        default=os.getenv("TWITCH_CLIENT_ID"),
        help="Twitch API client ID (or set TWITCH_CLIENT_ID env var)",
    )
    parser.add_argument(
        "--access-token",
        default=os.getenv("TWITCH_ACCESS_TOKEN"),
        help="Twitch API access token (or set TWITCH_ACCESS_TOKEN env var)",
    )
    parser.add_argument(
        "--webhook-secret",
        default=os.getenv("TWITCH_EVENTSUB_WEBHOOK_SECRET"),
        help="Webhook secret (or set TWITCH_EVENTSUB_WEBHOOK_SECRET env var)",
    )
    parser.add_argument(
        "--webhook-url",
        default=os.getenv("TWITCH_EVENTSUB_WEBHOOK_URL"),
        help="Webhook callback URL (or set TWITCH_EVENTSUB_WEBHOOK_URL env var)",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create subscription
    create_parser = subparsers.add_parser("create", help="Create subscription")
    create_parser.add_argument(
        "--event-type",
        default="channel.channel_points_custom_reward_redemption.add",
        help="Event type (default: channel points redemption)",
    )
    create_parser.add_argument(
        "--broadcaster-id",
        required=True,
        help="Broadcaster Twitch user ID",
    )
    
    # List subscriptions
    list_parser = subparsers.add_parser("list", help="List subscriptions")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--event-type", help="Filter by event type")
    
    # Delete subscription
    delete_parser = subparsers.add_parser("delete", help="Delete subscription")
    delete_parser.add_argument("--id", required=True, help="Subscription ID")
    
    args = parser.parse_args()
    
    # Validate required credentials
    if not args.client_id:
        print("❌ Error: TWITCH_CLIENT_ID required")
        sys.exit(1)
    if not args.access_token:
        print("❌ Error: TWITCH_ACCESS_TOKEN required")
        sys.exit(1)
    
    # Create manager
    manager = TwitchEventSubManager(
        client_id=args.client_id,
        access_token=args.access_token,
        webhook_secret=args.webhook_secret,
        webhook_url=args.webhook_url,
    )
    
    try:
        if args.command == "create":
            if not args.webhook_url:
                print("❌ Error: --webhook-url required for create")
                sys.exit(1)
            if not args.webhook_secret:
                print("❌ Error: --webhook-secret required for create")
                sys.exit(1)
            
            result = manager.create_subscription(
                event_type=args.event_type,
                broadcaster_user_id=args.broadcaster_id,
            )
            print("✅ Subscription created successfully!")
            print(json.dumps(result, indent=2))
            
        elif args.command == "list":
            result = manager.list_subscriptions(
                status=args.status,
                event_type=args.event_type,
            )
            subscriptions = result.get("data", [])
            print(f"📋 Found {len(subscriptions)} subscription(s):\n")
            for sub in subscriptions:
                print(f"ID: {sub['id']}")
                print(f"Type: {sub['type']}")
                print(f"Status: {sub['status']}")
                print(f"Created: {sub['created_at']}")
                print("-" * 50)
                
        elif args.command == "delete":
            manager.delete_subscription(args.id)
            print(f"✅ Subscription {args.id} deleted successfully!")
            
        else:
            parser.print_help()
            sys.exit(1)
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        if e.response is not None:
            try:
                error_data = e.response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(e.response.text)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

