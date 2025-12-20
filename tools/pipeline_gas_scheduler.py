#!/usr/bin/env python3
"""
Pipeline Gas Scheduler - Automated Gas Delivery System
======================================================

Automatically sends pipeline gas at 75%, 90%, and 100% completion.

Problem Solved: Agent-1 forgot to send gas, Agent-2 sent only at 100%
Solution: 3-send protocol automation (75% early, 90% safety, 100% final)

Author: Agent-1 - Integration & Core Systems Specialist
Date: 2025-10-15
License: MIT
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class PipelineGasScheduler:
    """Automatically sends pipeline gas at checkpoints."""
    
    # Pipeline sequence for 75-repo mission
    PIPELINE_SEQUENCE = {
        'Agent-1': 'Agent-2',
        'Agent-2': 'Agent-3',
        'Agent-3': 'Agent-5',
        'Agent-5': 'Agent-6',
        'Agent-6': 'Agent-7',
        'Agent-7': 'Agent-8',
        'Agent-8': 'Agent-4',
        'Agent-4': None  # Captain finishes
    }
    
    def __init__(
        self,
        agent_id: str,
        mission_name: str,
        total_items: int,
        send_message_func: Optional[Callable] = None
    ):
        """
        Initialize pipeline gas scheduler.
        
        Args:
            agent_id: Current agent ID
            mission_name: Mission name for context
            total_items: Total items in mission (for % calculation)
            send_message_func: Function to send messages (optional)
        """
        self.agent_id = agent_id
        self.mission_name = mission_name
        self.total_items = total_items
        self.send_message_func = send_message_func or self._default_send_message
        
        # Track gas delivery
        self.gas_checkpoints = {
            '75': {'sent': False, 'threshold': 0.75},
            '90': {'sent': False, 'threshold': 0.90},
            '100': {'sent': False, 'threshold': 1.00}
        }
        
        self.next_agent = self.PIPELINE_SEQUENCE.get(agent_id)
        if not self.next_agent:
            logger.info(f"ℹ️ {agent_id} is last in pipeline (no gas delivery needed)")
    
    def check_progress(self, current_item: int) -> dict[str, bool]:
        """
        Check progress and send gas if checkpoint reached.
        
        Args:
            current_item: Current item number (1-indexed)
            
        Returns:
            Dict of gas sent status
        """
        if not self.next_agent:
            return {}  # Last agent, no gas needed
        
        progress = current_item / self.total_items
        results = {}
        
        # Check each checkpoint
        for checkpoint, config in self.gas_checkpoints.items():
            if progress >= config['threshold'] and not config['sent']:
                success = self._send_gas_at_checkpoint(checkpoint, progress)
                config['sent'] = success
                results[checkpoint] = success
        
        return results
    
    def _send_gas_at_checkpoint(self, checkpoint: str, progress: float) -> bool:
        """Send gas at specific checkpoint."""
        if checkpoint == '75':
            return self._send_early_gas(progress)
        elif checkpoint == '90':
            return self._send_safety_gas(progress)
        elif checkpoint == '100':
            return self._send_final_gas(progress)
        return False
    
    def _send_early_gas(self, progress: float) -> bool:
        """Send 75% early gas (PIPELINE CRITICAL!)."""
        message = self._format_early_gas_message(progress)
        
        print(f"\n⛽ EARLY GAS (75%) → {self.next_agent}")
        print(f"PIPELINE CRITICAL: Sending gas BEFORE running out!")
        
        return self.send_message_func(self.next_agent, message, priority='HIGH')
    
    def _send_safety_gas(self, progress: float) -> bool:
        """Send 90% safety gas (backup)."""
        message = self._format_safety_gas_message(progress)
        
        print(f"\n⛽ SAFETY GAS (90%) → {self.next_agent}")
        print(f"BACKUP: Ensuring pipeline continuity!")
        
        return self.send_message_func(self.next_agent, message, priority='REGULAR')
    
    def _send_final_gas(self, progress: float) -> bool:
        """Send 100% final gas (completion handoff)."""
        message = self._format_final_gas_message()
        
        print(f"\n⛽ FINAL GAS (100%) → {self.next_agent}")
        print(f"HANDOFF COMPLETE: Pipeline passing!")
        
        return self.send_message_func(self.next_agent, message, priority='HIGH')
    
    def _format_early_gas_message(self, progress: float) -> str:
        """Format early gas message (75%)."""
        current = int(self.total_items * progress)
        remaining = self.total_items - current
        
        return f"""⛽ PIPELINE GAS: {self.next_agent}!

HANDOFF STATUS:
- My mission: {self.mission_name}
- My progress: {current}/{self.total_items} ({int(progress * 100)}%)
- Remaining: {remaining} items
- Your mission: Next in sequence

PIPELINE CRITICAL:
You're next! Start NOW to maintain flow!
I'm sending early so pipeline never breaks!

Expected completion: ~{remaining} items left for me
Your start: NOW (while I finish)

EXECUTE to keep swarm moving! 🚀
"""
    
    def _format_safety_gas_message(self, progress: float) -> str:
        """Format safety gas message (90%)."""
        return f"""⛽ PIPELINE SAFETY GAS: {self.next_agent}!

BACKUP HANDOFF:
- Mission: {self.mission_name}
- Progress: {int(progress * 100)}% (near finish)
- This is safety/backup gas
- Ensures pipeline continuity

If you haven't started yet: START NOW!
Pipeline depends on continuous flow!

🚀 Keep the swarm moving!
"""
    
    def _format_final_gas_message(self) -> str:
        """Format final gas message (100%)."""
        return f"""✅ MISSION COMPLETE + FINAL GAS: {self.next_agent}!

HANDOFF COMPLETE:
- Mission: {self.mission_name}
- Status: 100% DONE ✅
- Next mission: Your assignment awaits
- Methodology: Use deep analysis (proven effective!)

PIPELINE PASSING:
This is final handoff! Execute NOW!
My gas tank empty - you're fueled and ready!

Keep the swarm moving! 🐝🚀
"""
    
    def _default_send_message(
        self,
        recipient: str,
        message: str,
        priority: str = 'REGULAR'
    ) -> bool:
        """Default message sender (file-based)."""
        try:
            inbox_path = Path(f"agent_workspaces/{recipient}/inbox")
            inbox_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"PIPELINE_GAS_FROM_{self.agent_id}_{timestamp}.md"
            
            message_file = inbox_path / filename
            message_file.write_text(message)
            
            logger.info(f"✅ Pipeline gas sent to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send gas to {recipient}: {e}")
            return False
    
    def force_send_all_checkpoints(self) -> dict[str, bool]:
        """Force send all remaining checkpoints (emergency)."""
        results = {}
        
        for checkpoint in ['75', '90', '100']:
            if not self.gas_checkpoints[checkpoint]['sent']:
                success = self._send_gas_at_checkpoint(
                    checkpoint,
                    self.gas_checkpoints[checkpoint]['threshold']
                )
                self.gas_checkpoints[checkpoint]['sent'] = success
                results[checkpoint] = success
        
        return results


# CLI interface
def main():
    """CLI for testing pipeline gas scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test pipeline gas scheduler"
    )
    parser.add_argument('--agent', required=True, help='Agent ID')
    parser.add_argument('--mission', required=True, help='Mission name')
    parser.add_argument('--total', type=int, required=True,
                       help='Total items in mission')
    parser.add_argument('--simulate', action='store_true',
                       help='Simulate progress through mission')
    
    args = parser.parse_args()
    
    scheduler = PipelineGasScheduler(
        agent_id=args.agent,
        mission_name=args.mission,
        total_items=args.total
    )
    
    if args.simulate:
        print(f"\n🎯 SIMULATING: {args.mission}")
        print(f"Agent: {args.agent}, Total items: {args.total}")
        print(f"Next agent: {scheduler.next_agent}\n")
        
        # Simulate progress
        for i in range(1, args.total + 1):
            progress_pct = int((i / args.total) * 100)
            print(f"Item {i}/{args.total} ({progress_pct}%)")
            
            results = scheduler.check_progress(i)
            
            if results:
                print(f"  ⛽ Gas sent: {list(results.keys())}")
        
        print(f"\n✅ Simulation complete!")
        print(f"Gas checkpoints: {scheduler.gas_checkpoints}")
    
    return 0


if __name__ == '__main__':
    main()

