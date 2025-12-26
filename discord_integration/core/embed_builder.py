#!/usr/bin/env python3
"""
Embed Builder
=============

Creates beautiful Discord embeds for server status,
alerts, leaderboards, and notifications.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EmbedField:
    """A field in a Discord embed."""
    name: str
    value: str
    inline: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "inline": self.inline,
        }


@dataclass
class EmbedFooter:
    """Footer for a Discord embed."""
    text: str
    icon_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"text": self.text}
        if self.icon_url:
            result["icon_url"] = self.icon_url
        return result


@dataclass
class EmbedAuthor:
    """Author section for a Discord embed."""
    name: str
    url: Optional[str] = None
    icon_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"name": self.name}
        if self.url:
            result["url"] = self.url
        if self.icon_url:
            result["icon_url"] = self.icon_url
        return result


@dataclass
class DiscordEmbed:
    """A Discord embed object."""
    title: str
    description: str = ""
    color: int = 0x00d9ff
    url: Optional[str] = None
    timestamp: Optional[str] = None
    thumbnail_url: Optional[str] = None
    image_url: Optional[str] = None
    fields: List[EmbedField] = field(default_factory=list)
    footer: Optional[EmbedFooter] = None
    author: Optional[EmbedAuthor] = None
    
    def to_dict(self) -> Dict[str, Any]:
        embed = {
            "title": self.title,
            "color": self.color,
        }
        
        if self.description:
            embed["description"] = self.description
        if self.url:
            embed["url"] = self.url
        if self.timestamp:
            embed["timestamp"] = self.timestamp
        if self.thumbnail_url:
            embed["thumbnail"] = {"url": self.thumbnail_url}
        if self.image_url:
            embed["image"] = {"url": self.image_url}
        if self.fields:
            embed["fields"] = [f.to_dict() for f in self.fields]
        if self.footer:
            embed["footer"] = self.footer.to_dict()
        if self.author:
            embed["author"] = self.author.to_dict()
        
        return embed


class EmbedBuilder:
    """
    Builder for creating Discord embeds.
    
    Provides pre-built templates for common game server scenarios.
    """
    
    # Color palette
    COLORS = {
        "success": 0x2ecc71,   # Green
        "warning": 0xf39c12,   # Orange
        "error": 0xe74c3c,     # Red
        "info": 0x3498db,      # Blue
        "primary": 0x00d9ff,   # Cyan
        "purple": 0x9b59b6,    # Purple
        "gray": 0x95a5a6,      # Gray
    }
    
    # Game icons (placeholder URLs - would use actual game icons)
    GAME_ICONS = {
        "lethal-company": "https://cdn.thunderstore.io/live/modicons/png/LethalCompany.png",
        "valheim": "https://cdn.thunderstore.io/live/modicons/png/Valheim.png",
        "minecraft": "https://minecraft.net/favicon.ico",
    }
    
    @classmethod
    def server_status(
        cls,
        server_name: str,
        game: str,
        status: str,
        player_count: int,
        max_players: int,
        ip: str = "",
        port: int = 0,
        mods_count: int = 0,
        uptime: str = "",
    ) -> DiscordEmbed:
        """Create a server status embed."""
        # Determine color and emoji based on status
        if status.lower() in ["online", "healthy"]:
            color = cls.COLORS["success"]
            status_emoji = "🟢"
        elif status.lower() in ["starting", "restarting"]:
            color = cls.COLORS["warning"]
            status_emoji = "🟡"
        else:
            color = cls.COLORS["error"]
            status_emoji = "🔴"
        
        # Player bar visualization
        if max_players > 0:
            fill = int((player_count / max_players) * 10)
            player_bar = "█" * fill + "░" * (10 - fill)
        else:
            player_bar = "░" * 10
        
        fields = [
            EmbedField(
                name="Status",
                value=f"{status_emoji} {status.title()}",
                inline=True,
            ),
            EmbedField(
                name="Players",
                value=f"`{player_count}/{max_players}`\n{player_bar}",
                inline=True,
            ),
        ]
        
        if ip and port:
            fields.append(EmbedField(
                name="Connect",
                value=f"`{ip}:{port}`",
                inline=True,
            ))
        
        if mods_count:
            fields.append(EmbedField(
                name="Mods",
                value=f"`{mods_count}` installed",
                inline=True,
            ))
        
        if uptime:
            fields.append(EmbedField(
                name="Uptime",
                value=uptime,
                inline=True,
            ))
        
        return DiscordEmbed(
            title=f"🎮 {server_name}",
            description=f"**{game.replace('-', ' ').title()}** Server Status",
            color=color,
            timestamp=datetime.utcnow().isoformat(),
            thumbnail_url=cls.GAME_ICONS.get(game.lower()),
            fields=fields,
            footer=EmbedFooter(text="Last updated"),
        )
    
    @classmethod
    def player_join(
        cls,
        player_name: str,
        server_name: str,
        player_count: int,
        max_players: int,
    ) -> DiscordEmbed:
        """Create a player join notification embed."""
        return DiscordEmbed(
            title="👋 Player Joined",
            description=f"**{player_name}** joined **{server_name}**",
            color=cls.COLORS["success"],
            timestamp=datetime.utcnow().isoformat(),
            fields=[
                EmbedField(
                    name="Players Online",
                    value=f"`{player_count}/{max_players}`",
                    inline=True,
                ),
            ],
        )
    
    @classmethod
    def player_leave(
        cls,
        player_name: str,
        server_name: str,
        player_count: int,
        max_players: int,
        session_time: str = "",
    ) -> DiscordEmbed:
        """Create a player leave notification embed."""
        fields = [
            EmbedField(
                name="Players Online",
                value=f"`{player_count}/{max_players}`",
                inline=True,
            ),
        ]
        
        if session_time:
            fields.append(EmbedField(
                name="Session Time",
                value=session_time,
                inline=True,
            ))
        
        return DiscordEmbed(
            title="👋 Player Left",
            description=f"**{player_name}** left **{server_name}**",
            color=cls.COLORS["gray"],
            timestamp=datetime.utcnow().isoformat(),
            fields=fields,
        )
    
    @classmethod
    def alert(
        cls,
        alert_type: str,
        severity: str,
        message: str,
        server_name: str = "",
        recommendations: Optional[List[str]] = None,
    ) -> DiscordEmbed:
        """Create an alert notification embed."""
        severity_config = {
            "critical": {"color": cls.COLORS["error"], "emoji": "🚨"},
            "warning": {"color": cls.COLORS["warning"], "emoji": "⚠️"},
            "info": {"color": cls.COLORS["info"], "emoji": "ℹ️"},
        }
        
        config = severity_config.get(severity.lower(), severity_config["info"])
        
        description = message
        if server_name:
            description = f"**Server:** {server_name}\n\n{message}"
        
        fields = []
        if recommendations:
            rec_text = "\n".join(f"• {r}" for r in recommendations[:5])
            fields.append(EmbedField(
                name="Recommendations",
                value=rec_text,
                inline=False,
            ))
        
        return DiscordEmbed(
            title=f"{config['emoji']} {alert_type.replace('_', ' ').title()}",
            description=description,
            color=config["color"],
            timestamp=datetime.utcnow().isoformat(),
            fields=fields,
        )
    
    @classmethod
    def mod_update(
        cls,
        mod_name: str,
        old_version: str,
        new_version: str,
        action: str = "available",  # available, deployed, failed
    ) -> DiscordEmbed:
        """Create a mod update notification embed."""
        if action == "available":
            color = cls.COLORS["info"]
            title = "🔄 Mod Update Available"
            desc = f"**{mod_name}** has a new version"
        elif action == "deployed":
            color = cls.COLORS["success"]
            title = "✅ Mod Updated"
            desc = f"**{mod_name}** has been updated"
        else:
            color = cls.COLORS["error"]
            title = "❌ Mod Update Failed"
            desc = f"Failed to update **{mod_name}**"
        
        return DiscordEmbed(
            title=title,
            description=desc,
            color=color,
            timestamp=datetime.utcnow().isoformat(),
            fields=[
                EmbedField(name="Old Version", value=f"`{old_version}`", inline=True),
                EmbedField(name="New Version", value=f"`{new_version}`", inline=True),
            ],
        )
    
    @classmethod
    def backup_complete(
        cls,
        backup_id: str,
        backup_type: str,
        size: str,
        file_count: int,
        duration: str = "",
    ) -> DiscordEmbed:
        """Create a backup completion notification embed."""
        fields = [
            EmbedField(name="Type", value=backup_type.title(), inline=True),
            EmbedField(name="Size", value=size, inline=True),
            EmbedField(name="Files", value=str(file_count), inline=True),
        ]
        
        if duration:
            fields.append(EmbedField(name="Duration", value=duration, inline=True))
        
        return DiscordEmbed(
            title="💾 Backup Complete",
            description=f"Backup `{backup_id}` created successfully",
            color=cls.COLORS["success"],
            timestamp=datetime.utcnow().isoformat(),
            fields=fields,
        )
    
    @classmethod
    def leaderboard(
        cls,
        title: str,
        entries: List[Dict[str, Any]],
        stat_name: str = "Score",
        show_rank: bool = True,
    ) -> DiscordEmbed:
        """Create a leaderboard embed."""
        medals = ["🥇", "🥈", "🥉"]
        
        lines = []
        for i, entry in enumerate(entries[:10]):
            if show_rank and i < 3:
                prefix = medals[i]
            elif show_rank:
                prefix = f"`{i+1}.`"
            else:
                prefix = "•"
            
            name = entry.get("name", "Unknown")
            value = entry.get("value", 0)
            
            lines.append(f"{prefix} **{name}** — {value:,}")
        
        return DiscordEmbed(
            title=f"🏆 {title}",
            description="\n".join(lines) if lines else "No entries yet",
            color=cls.COLORS["purple"],
            timestamp=datetime.utcnow().isoformat(),
            footer=EmbedFooter(text=f"Showing top {len(entries)} by {stat_name}"),
        )
    
    @classmethod
    def server_restart(
        cls,
        server_name: str,
        reason: str = "Scheduled maintenance",
        eta_minutes: int = 5,
    ) -> DiscordEmbed:
        """Create a server restart notification embed."""
        return DiscordEmbed(
            title="🔄 Server Restarting",
            description=f"**{server_name}** is restarting",
            color=cls.COLORS["warning"],
            timestamp=datetime.utcnow().isoformat(),
            fields=[
                EmbedField(name="Reason", value=reason, inline=True),
                EmbedField(name="ETA", value=f"~{eta_minutes} minutes", inline=True),
            ],
        )
    
    @classmethod
    def custom(
        cls,
        title: str,
        description: str = "",
        color: str = "primary",
        fields: Optional[List[Dict[str, Any]]] = None,
        thumbnail_url: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> DiscordEmbed:
        """Create a custom embed."""
        embed_color = cls.COLORS.get(color, cls.COLORS["primary"])
        
        embed_fields = []
        if fields:
            for f in fields:
                embed_fields.append(EmbedField(
                    name=f.get("name", ""),
                    value=f.get("value", ""),
                    inline=f.get("inline", True),
                ))
        
        return DiscordEmbed(
            title=title,
            description=description,
            color=embed_color,
            timestamp=datetime.utcnow().isoformat(),
            fields=embed_fields,
            thumbnail_url=thumbnail_url,
            image_url=image_url,
        )
