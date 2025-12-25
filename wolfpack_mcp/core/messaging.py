"""
Pack Messaging - Wolf-to-wolf communication system.

🐺 Wolves communicate through howls - the pack always knows.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class HowlUrgency(Enum):
    """Howl urgency levels."""
    EMERGENCY = 1  # 🚨 Drop everything
    URGENT = 2     # ⚡ Priority
    NORMAL = 3     # 📢 Standard
    LOW = 4        # 💬 When you can


class HowlType(Enum):
    """Types of howls."""
    WOLF_TO_WOLF = "w2w"
    ALPHA_TO_PACK = "a2p"
    WOLF_TO_ALPHA = "w2a"
    PACK_HOWL = "pack"
    SYSTEM = "system"


@dataclass
class Howl:
    """A howl in the pack communication system."""
    id: str
    sender: str
    recipient: str
    content: str
    howl_type: HowlType = HowlType.WOLF_TO_WOLF
    urgency: HowlUrgency = HowlUrgency.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    heard: bool = False


class MessageQueue:
    """
    🐺 Pack message queue - howls echo through the territory.
    
    Example:
        queue = MessageQueue(territory="./pack_messages")
        
        # Send a howl
        queue.howl("scout-1", "alpha", "Found prey at sector 7")
        
        # Check incoming howls
        howls = queue.listen("alpha")
        
        # Mark as heard
        queue.mark_heard(howls[0].id, "alpha")
    """
    
    def __init__(self, territory: str = "./pack_messages"):
        """
        Initialize message queue.
        
        Args:
            territory: Directory for pack communications
        """
        self.territory = Path(territory)
        self.territory.mkdir(parents=True, exist_ok=True)
        self._howl_counter = 0
    
    def _generate_id(self) -> str:
        """Generate unique howl ID."""
        self._howl_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"howl_{timestamp}_{self._howl_counter}"
    
    def send(
        self,
        sender: str,
        recipient: str,
        content: str,
        urgency: HowlUrgency = HowlUrgency.NORMAL,
        howl_type: HowlType = HowlType.WOLF_TO_WOLF,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Howl:
        """
        🐺 Send a howl from one wolf to another.
        
        Args:
            sender: Sending wolf
            recipient: Receiving wolf
            content: Howl content
            urgency: How urgent
            howl_type: Type of howl
            metadata: Extra data
            
        Returns:
            The sent howl
        """
        msg = Howl(
            id=self._generate_id(),
            sender=sender,
            recipient=recipient,
            content=content,
            howl_type=howl_type,
            urgency=urgency,
            metadata=metadata or {}
        )
        
        # Save to recipient's territory
        inbox = self.territory / recipient / "incoming"
        inbox.mkdir(parents=True, exist_ok=True)
        
        howl_file = inbox / f"{msg.id}.json"
        howl_data = {
            "id": msg.id,
            "sender": msg.sender,
            "recipient": msg.recipient,
            "content": msg.content,
            "howl_type": msg.howl_type.value,
            "urgency": msg.urgency.value,
            "timestamp": msg.timestamp.isoformat(),
            "metadata": msg.metadata,
            "heard": False
        }
        howl_file.write_text(json.dumps(howl_data, indent=2))
        
        return msg
    
    def listen(
        self,
        wolf_id: str,
        unheard_only: bool = False,
        limit: int = 50
    ) -> List[Howl]:
        """
        🐺 Listen for incoming howls.
        
        Args:
            wolf_id: Wolf listening
            unheard_only: Only unheard howls
            limit: Max howls to return
            
        Returns:
            List of howls
        """
        inbox = self.territory / wolf_id / "incoming"
        if not inbox.exists():
            return []
        
        howls = []
        for howl_file in sorted(inbox.glob("*.json"), reverse=True):
            if len(howls) >= limit:
                break
            
            try:
                data = json.loads(howl_file.read_text())
                if unheard_only and data.get("heard"):
                    continue
                
                msg = Howl(
                    id=data["id"],
                    sender=data["sender"],
                    recipient=data["recipient"],
                    content=data["content"],
                    howl_type=HowlType(data.get("howl_type", "w2w")),
                    urgency=HowlUrgency(data.get("urgency", 3)),
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    metadata=data.get("metadata", {}),
                    heard=data.get("heard", False)
                )
                howls.append(msg)
            except Exception:
                pass
        
        return howls
    
    def mark_heard(self, howl_id: str, wolf_id: str) -> bool:
        """Mark a howl as heard."""
        howl_file = self.territory / wolf_id / "incoming" / f"{howl_id}.json"
        if not howl_file.exists():
            return False
        
        try:
            data = json.loads(howl_file.read_text())
            data["heard"] = True
            howl_file.write_text(json.dumps(data, indent=2))
            return True
        except Exception:
            return False
    
    def count_unheard(self, wolf_id: str) -> int:
        """Count unheard howls for a wolf."""
        return len(self.listen(wolf_id, unheard_only=True))


# Convenience functions
_default_queue: Optional[MessageQueue] = None


def get_queue(territory: str = "./pack_messages") -> MessageQueue:
    """Get or create default message queue."""
    global _default_queue
    if _default_queue is None:
        _default_queue = MessageQueue(territory)
    return _default_queue


def howl(
    sender: str,
    recipient: str,
    content: str,
    urgency: HowlUrgency = HowlUrgency.NORMAL
) -> Howl:
    """🐺 Send a howl using the default queue."""
    return get_queue().send(sender, recipient, content, urgency)


def broadcast(
    sender: str,
    content: str,
    pack: List[str],
    urgency: HowlUrgency = HowlUrgency.NORMAL
) -> List[Howl]:
    """🐺 Howl to the entire pack."""
    queue = get_queue()
    howls = []
    for wolf in pack:
        msg = queue.send(
            sender=sender,
            recipient=wolf,
            content=content,
            urgency=urgency,
            howl_type=HowlType.PACK_HOWL
        )
        howls.append(msg)
    return howls
