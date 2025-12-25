"""
Swarm Messaging - Agent-to-agent communication system.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import deque


class MessagePriority(Enum):
    """Message priority levels."""
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class MessageType(Enum):
    """Types of messages in the swarm."""
    AGENT_TO_AGENT = "a2a"
    CAPTAIN_TO_AGENT = "c2a"
    AGENT_TO_CAPTAIN = "a2c"
    BROADCAST = "broadcast"
    SYSTEM = "system"


@dataclass
class Message:
    """A message in the swarm communication system."""
    id: str
    sender: str
    recipient: str
    content: str
    message_type: MessageType = MessageType.AGENT_TO_AGENT
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    delivered: bool = False
    read: bool = False


class MessageQueue:
    """
    File-based message queue for agent communication.
    
    Example:
        queue = MessageQueue(queue_dir="./message_queue")
        
        # Send a message
        queue.send("agent-1", "agent-2", "Please review PR #42")
        
        # Check inbox
        messages = queue.get_inbox("agent-2")
        
        # Mark as read
        queue.mark_read(messages[0].id)
    """
    
    def __init__(self, queue_dir: str = "./message_queue"):
        """
        Initialize message queue.
        
        Args:
            queue_dir: Directory to store messages
        """
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self._message_counter = 0
    
    def _generate_id(self) -> str:
        """Generate unique message ID."""
        self._message_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"msg_{timestamp}_{self._message_counter}"
    
    def send(
        self,
        sender: str,
        recipient: str,
        content: str,
        priority: MessagePriority = MessagePriority.NORMAL,
        message_type: MessageType = MessageType.AGENT_TO_AGENT,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Send a message from one agent to another.
        
        Args:
            sender: Sender agent ID
            recipient: Recipient agent ID
            content: Message content
            priority: Message priority
            message_type: Type of message
            metadata: Additional metadata
            
        Returns:
            The sent message
        """
        msg = Message(
            id=self._generate_id(),
            sender=sender,
            recipient=recipient,
            content=content,
            message_type=message_type,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Save to recipient's inbox
        inbox_dir = self.queue_dir / recipient / "inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        
        msg_file = inbox_dir / f"{msg.id}.json"
        msg_data = {
            "id": msg.id,
            "sender": msg.sender,
            "recipient": msg.recipient,
            "content": msg.content,
            "message_type": msg.message_type.value,
            "priority": msg.priority.value,
            "timestamp": msg.timestamp.isoformat(),
            "metadata": msg.metadata,
            "delivered": True,
            "read": False
        }
        msg_file.write_text(json.dumps(msg_data, indent=2))
        
        return msg
    
    def get_inbox(
        self,
        agent_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Message]:
        """
        Get messages from an agent's inbox.
        
        Args:
            agent_id: Agent to get inbox for
            unread_only: Only return unread messages
            limit: Maximum messages to return
            
        Returns:
            List of messages
        """
        inbox_dir = self.queue_dir / agent_id / "inbox"
        if not inbox_dir.exists():
            return []
        
        messages = []
        for msg_file in sorted(inbox_dir.glob("*.json"), reverse=True):
            if len(messages) >= limit:
                break
            
            try:
                data = json.loads(msg_file.read_text())
                if unread_only and data.get("read"):
                    continue
                
                msg = Message(
                    id=data["id"],
                    sender=data["sender"],
                    recipient=data["recipient"],
                    content=data["content"],
                    message_type=MessageType(data.get("message_type", "a2a")),
                    priority=MessagePriority(data.get("priority", 3)),
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    metadata=data.get("metadata", {}),
                    delivered=data.get("delivered", True),
                    read=data.get("read", False)
                )
                messages.append(msg)
            except Exception:
                pass
        
        return messages
    
    def mark_read(self, message_id: str, agent_id: str) -> bool:
        """Mark a message as read."""
        msg_file = self.queue_dir / agent_id / "inbox" / f"{message_id}.json"
        if not msg_file.exists():
            return False
        
        try:
            data = json.loads(msg_file.read_text())
            data["read"] = True
            msg_file.write_text(json.dumps(data, indent=2))
            return True
        except Exception:
            return False
    
    def get_unread_count(self, agent_id: str) -> int:
        """Get count of unread messages for an agent."""
        return len(self.get_inbox(agent_id, unread_only=True))


# Convenience functions
_default_queue: Optional[MessageQueue] = None


def get_queue(queue_dir: str = "./message_queue") -> MessageQueue:
    """Get or create default message queue."""
    global _default_queue
    if _default_queue is None:
        _default_queue = MessageQueue(queue_dir)
    return _default_queue


def send_message(
    sender: str,
    recipient: str,
    content: str,
    priority: MessagePriority = MessagePriority.NORMAL
) -> Message:
    """Send a message using the default queue."""
    return get_queue().send(sender, recipient, content, priority)


def broadcast(
    sender: str,
    content: str,
    recipients: List[str],
    priority: MessagePriority = MessagePriority.NORMAL
) -> List[Message]:
    """Broadcast a message to multiple agents."""
    queue = get_queue()
    messages = []
    for recipient in recipients:
        msg = queue.send(
            sender=sender,
            recipient=recipient,
            content=content,
            priority=priority,
            message_type=MessageType.BROADCAST
        )
        messages.append(msg)
    return messages
