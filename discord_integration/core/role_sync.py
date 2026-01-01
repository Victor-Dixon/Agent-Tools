#!/usr/bin/env python3
"""
Role Sync
=========

Synchronizes game server roles/ranks with Discord roles.
Supports bi-directional sync and custom role mappings.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import requests

logger = logging.getLogger(__name__)


@dataclass
class RoleMapping:
    """Maps a game role to a Discord role."""
    game_role: str
    discord_role_id: str
    discord_role_name: str
    priority: int = 0  # Higher priority roles override lower
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_role": self.game_role,
            "discord_role_id": self.discord_role_id,
            "discord_role_name": self.discord_role_name,
            "priority": self.priority,
        }


@dataclass
class LinkedAccount:
    """Links a game account to a Discord account."""
    discord_id: str
    discord_username: str
    game_id: str
    game_username: str
    linked_at: str
    verified: bool = False
    current_game_roles: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "discord_id": self.discord_id,
            "discord_username": self.discord_username,
            "game_id": self.game_id,
            "game_username": self.game_username,
            "linked_at": self.linked_at,
            "verified": self.verified,
            "current_game_roles": self.current_game_roles,
        }


class RoleSync:
    """
    Synchronizes game roles with Discord roles.
    
    Features:
    - Role mapping configuration
    - Account linking
    - Automatic role assignment
    - Role hierarchy support
    """
    
    def __init__(
        self,
        bot_token: str = "",
        guild_id: str = "",
        config_path: Optional[Path] = None,
    ):
        self.bot_token = bot_token
        self.guild_id = guild_id
        self.config_path = config_path or Path.home() / ".discord_integration" / "role_sync.json"
        
        self._mappings: Dict[str, RoleMapping] = {}  # game_role -> mapping
        self._linked_accounts: Dict[str, LinkedAccount] = {}  # discord_id -> account
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load role sync configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                
                for mapping_data in data.get("mappings", []):
                    mapping = RoleMapping(**mapping_data)
                    self._mappings[mapping.game_role] = mapping
                
                for account_data in data.get("linked_accounts", []):
                    account = LinkedAccount(
                        discord_id=account_data["discord_id"],
                        discord_username=account_data["discord_username"],
                        game_id=account_data["game_id"],
                        game_username=account_data["game_username"],
                        linked_at=account_data["linked_at"],
                        verified=account_data.get("verified", False),
                        current_game_roles=account_data.get("current_game_roles", []),
                    )
                    self._linked_accounts[account.discord_id] = account
                    
            except Exception as e:
                logger.warning(f"Failed to load role sync config: {e}")
    
    def _save_config(self) -> None:
        """Save role sync configuration."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "guild_id": self.guild_id,
            "mappings": [m.to_dict() for m in self._mappings.values()],
            "linked_accounts": [a.to_dict() for a in self._linked_accounts.values()],
        }
        
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def _discord_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """Make a Discord API request."""
        if not self.bot_token:
            logger.error("Bot token not configured")
            return None
        
        url = f"https://discord.com/api/v10{endpoint}"
        headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                timeout=10,
            )
            
            if response.status_code in [200, 201, 204]:
                return response.json() if response.text else {}
            else:
                logger.error(f"Discord API error: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Discord request failed: {e}")
            return None
    
    def add_role_mapping(
        self,
        game_role: str,
        discord_role_id: str,
        discord_role_name: str,
        priority: int = 0,
    ) -> bool:
        """Add a role mapping."""
        self._mappings[game_role] = RoleMapping(
            game_role=game_role,
            discord_role_id=discord_role_id,
            discord_role_name=discord_role_name,
            priority=priority,
        )
        self._save_config()
        return True
    
    def remove_role_mapping(self, game_role: str) -> bool:
        """Remove a role mapping."""
        if game_role in self._mappings:
            del self._mappings[game_role]
            self._save_config()
            return True
        return False
    
    def list_role_mappings(self) -> List[Dict[str, Any]]:
        """List all role mappings."""
        return [m.to_dict() for m in self._mappings.values()]
    
    def link_account(
        self,
        discord_id: str,
        discord_username: str,
        game_id: str,
        game_username: str,
        verified: bool = False,
    ) -> Dict[str, Any]:
        """
        Link a game account to a Discord account.
        
        Args:
            discord_id: Discord user ID
            discord_username: Discord username
            game_id: Game-specific user ID
            game_username: In-game username
            verified: Whether the link is verified
            
        Returns:
            Link result
        """
        # Check if already linked
        if discord_id in self._linked_accounts:
            existing = self._linked_accounts[discord_id]
            return {
                "success": False,
                "error": f"Discord account already linked to {existing.game_username}",
            }
        
        # Check if game account is already linked
        for account in self._linked_accounts.values():
            if account.game_id == game_id:
                return {
                    "success": False,
                    "error": f"Game account already linked to {account.discord_username}",
                }
        
        account = LinkedAccount(
            discord_id=discord_id,
            discord_username=discord_username,
            game_id=game_id,
            game_username=game_username,
            linked_at=datetime.now().isoformat(),
            verified=verified,
        )
        
        self._linked_accounts[discord_id] = account
        self._save_config()
        
        return {
            "success": True,
            "account": account.to_dict(),
        }
    
    def unlink_account(self, discord_id: str) -> bool:
        """Unlink a Discord account."""
        if discord_id in self._linked_accounts:
            del self._linked_accounts[discord_id]
            self._save_config()
            return True
        return False
    
    def get_linked_account(self, discord_id: str) -> Optional[Dict[str, Any]]:
        """Get linked account info."""
        if discord_id in self._linked_accounts:
            return self._linked_accounts[discord_id].to_dict()
        return None
    
    def find_by_game_id(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Find linked account by game ID."""
        for account in self._linked_accounts.values():
            if account.game_id == game_id:
                return account.to_dict()
        return None
    
    def update_game_roles(
        self,
        discord_id: str,
        game_roles: List[str],
    ) -> Dict[str, Any]:
        """
        Update a user's game roles and sync to Discord.
        
        Args:
            discord_id: Discord user ID
            game_roles: Current game roles
            
        Returns:
            Sync result
        """
        if discord_id not in self._linked_accounts:
            return {"success": False, "error": "Account not linked"}
        
        account = self._linked_accounts[discord_id]
        old_roles = set(account.current_game_roles)
        new_roles = set(game_roles)
        
        # Determine role changes
        added_roles = new_roles - old_roles
        removed_roles = old_roles - new_roles
        
        # Update stored roles
        account.current_game_roles = game_roles
        self._save_config()
        
        # Sync to Discord
        roles_to_add = []
        roles_to_remove = []
        
        for role in added_roles:
            if role in self._mappings:
                roles_to_add.append(self._mappings[role].discord_role_id)
        
        for role in removed_roles:
            if role in self._mappings:
                roles_to_remove.append(self._mappings[role].discord_role_id)
        
        # Apply role changes via Discord API
        results = {
            "added": [],
            "removed": [],
            "errors": [],
        }
        
        for role_id in roles_to_add:
            success = self._add_discord_role(discord_id, role_id)
            if success:
                results["added"].append(role_id)
            else:
                results["errors"].append(f"Failed to add role {role_id}")
        
        for role_id in roles_to_remove:
            success = self._remove_discord_role(discord_id, role_id)
            if success:
                results["removed"].append(role_id)
            else:
                results["errors"].append(f"Failed to remove role {role_id}")
        
        return {
            "success": len(results["errors"]) == 0,
            "results": results,
        }
    
    def _add_discord_role(self, user_id: str, role_id: str) -> bool:
        """Add a Discord role to a user."""
        endpoint = f"/guilds/{self.guild_id}/members/{user_id}/roles/{role_id}"
        result = self._discord_request("PUT", endpoint)
        return result is not None
    
    def _remove_discord_role(self, user_id: str, role_id: str) -> bool:
        """Remove a Discord role from a user."""
        endpoint = f"/guilds/{self.guild_id}/members/{user_id}/roles/{role_id}"
        result = self._discord_request("DELETE", endpoint)
        return result is not None
    
    def sync_all_accounts(
        self,
        game_roles_provider: callable,
    ) -> Dict[str, Any]:
        """
        Sync roles for all linked accounts.
        
        Args:
            game_roles_provider: Function(game_id) -> List[str] of roles
            
        Returns:
            Sync results
        """
        results = {
            "synced": 0,
            "failed": 0,
            "errors": [],
        }
        
        for discord_id, account in self._linked_accounts.items():
            try:
                # Get current game roles
                game_roles = game_roles_provider(account.game_id)
                
                # Sync
                result = self.update_game_roles(discord_id, game_roles)
                
                if result["success"]:
                    results["synced"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].extend(result.get("results", {}).get("errors", []))
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error syncing {discord_id}: {e}")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get role sync statistics."""
        return {
            "role_mappings": len(self._mappings),
            "linked_accounts": len(self._linked_accounts),
            "verified_accounts": sum(
                1 for a in self._linked_accounts.values() if a.verified
            ),
        }


class WhitelistManager:
    """
    Manages game server whitelist based on Discord roles.
    
    Features:
    - Auto-whitelist users with specific Discord roles
    - Remove from whitelist when role is removed
    - Subscriber/VIP access management
    """
    
    def __init__(
        self,
        role_sync: RoleSync,
        whitelist_roles: Optional[List[str]] = None,
    ):
        self.role_sync = role_sync
        self.whitelist_roles = whitelist_roles or []  # Discord role IDs that grant whitelist
        
        self._whitelist: Set[str] = set()  # game_ids on whitelist
    
    def add_whitelist_role(self, role_id: str) -> None:
        """Add a role that grants whitelist access."""
        if role_id not in self.whitelist_roles:
            self.whitelist_roles.append(role_id)
    
    def remove_whitelist_role(self, role_id: str) -> None:
        """Remove a whitelist-granting role."""
        if role_id in self.whitelist_roles:
            self.whitelist_roles.remove(role_id)
    
    def check_whitelist(self, game_id: str) -> bool:
        """Check if a game ID is whitelisted."""
        return game_id in self._whitelist
    
    def get_whitelist(self) -> List[str]:
        """Get all whitelisted game IDs."""
        return list(self._whitelist)
    
    def refresh_whitelist(
        self,
        member_roles_provider: callable,
    ) -> Dict[str, Any]:
        """
        Refresh whitelist based on current Discord roles.
        
        Args:
            member_roles_provider: Function(discord_id) -> List[role_ids]
            
        Returns:
            Refresh results
        """
        new_whitelist = set()
        
        for discord_id, account in self.role_sync._linked_accounts.items():
            try:
                member_roles = member_roles_provider(discord_id)
                
                # Check if user has any whitelist role
                if any(role in self.whitelist_roles for role in member_roles):
                    new_whitelist.add(account.game_id)
                    
            except Exception as e:
                logger.warning(f"Could not check roles for {discord_id}: {e}")
        
        added = new_whitelist - self._whitelist
        removed = self._whitelist - new_whitelist
        
        self._whitelist = new_whitelist
        
        return {
            "total": len(self._whitelist),
            "added": list(added),
            "removed": list(removed),
        }
