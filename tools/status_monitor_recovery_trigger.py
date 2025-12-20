"""
Status Monitor Recovery Trigger - Standalone Recovery System
============================================================

Standalone tool to trigger recovery actions for stalled agents.
Works independently of orchestrator - can be run manually or scheduled.

V2 Compliance: ≤300 lines, single responsibility, comprehensive error handling.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
<!-- SSOT Domain: infrastructure -->
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrators.overnight.monitor import ProgressMonitor
from src.orchestrators.overnight.recovery import RecoverySystem
from src.orchestrators.overnight.enhanced_agent_activity_detector import EnhancedAgentActivityDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def trigger_recovery_for_stalled_agents() -> Dict[str, Any]:
    """
    Check for stalled agents and trigger recovery actions.
    
    Returns:
        Dict with recovery results
    """
    results = {
        "stalled_agents": [],
        "recovery_attempted": [],
        "recovery_succeeded": [],
        "recovery_failed": [],
        "errors": [],
    }
    
    try:
        # Initialize monitor and recovery system
        monitor = ProgressMonitor()
        recovery = RecoverySystem()
        
        # Initialize recovery system
        await recovery.initialize()
        
        # Get stalled agents using enhanced detector
        stalled_agents = await monitor.get_stalled_agents()
        
        if not stalled_agents:
            logger.info("✅ No stalled agents detected")
            return results
        
        logger.warning(f"🚨 Found {len(stalled_agents)} stalled agents: {stalled_agents}")
        results["stalled_agents"] = stalled_agents
        
        # Trigger recovery for each stalled agent
        for agent_id in stalled_agents:
            try:
                logger.info(f"🔄 Attempting recovery for {agent_id}")
                results["recovery_attempted"].append(agent_id)
                
                # Handle stalled agent via recovery system
                await recovery.handle_stalled_agents([agent_id])
                
                logger.info(f"✅ Recovery completed for {agent_id}")
                results["recovery_succeeded"].append(agent_id)
                
            except Exception as e:
                logger.error(f"❌ Recovery failed for {agent_id}: {e}")
                results["recovery_failed"].append(agent_id)
                results["errors"].append(f"{agent_id}: {str(e)}")
        
        # Summary
        logger.info(f"📊 Recovery Summary: {len(results['recovery_succeeded'])}/{len(results['recovery_attempted'])} succeeded")
        
    except Exception as e:
        logger.error(f"❌ Recovery trigger failed: {e}", exc_info=True)
        results["errors"].append(f"Recovery trigger: {str(e)}")
    
    return results


async def check_agent_status() -> Dict[str, Any]:
    """
    Check current agent status and activity.
    
    Returns:
        Dict with agent status information
    """
    status_info = {
        "agent_status": {},
        "stalled_agents": [],
        "active_agents": [],
        "idle_agents": [],
    }
    
    try:
        monitor = ProgressMonitor()
        detector = EnhancedAgentActivityDetector()
        
        # Get agent status from monitor
        agent_status = monitor.get_agent_status()
        status_info["agent_status"] = agent_status
        
        # Check for stalled agents
        stalled_agents = await monitor.get_stalled_agents()
        status_info["stalled_agents"] = stalled_agents
        
        # Categorize agents
        for agent_id, status_data in agent_status.items():
            status = status_data.get("status", "unknown")
            if status == "stalled":
                status_info["stalled_agents"].append(agent_id)
            elif status == "active" or status == "busy":
                status_info["active_agents"].append(agent_id)
            else:
                status_info["idle_agents"].append(agent_id)
        
        logger.info(f"📊 Status: {len(status_info['active_agents'])} active, "
                   f"{len(status_info['stalled_agents'])} stalled, "
                   f"{len(status_info['idle_agents'])} idle")
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}", exc_info=True)
        status_info["error"] = str(e)
    
    return status_info


async def main():
    """Main entry point for recovery trigger."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Status Monitor Recovery Trigger")
    parser.add_argument("--check-only", action="store_true", help="Only check status, don't trigger recovery")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🔍 Status Monitor Recovery Trigger")
    print("=" * 60)
    
    if args.check_only:
        print("📊 Checking agent status...")
        status = await check_agent_status()
        
        print(f"\n📊 Agent Status Summary:")
        print(f"  Active: {len(status['active_agents'])}")
        print(f"  Stalled: {len(status['stalled_agents'])}")
        print(f"  Idle: {len(status['idle_agents'])}")
        
        if status['stalled_agents']:
            print(f"\n🚨 Stalled Agents: {', '.join(status['stalled_agents'])}")
        else:
            print("\n✅ No stalled agents detected")
    else:
        print("🔄 Triggering recovery for stalled agents...")
        results = await trigger_recovery_for_stalled_agents()
        
        print(f"\n📊 Recovery Results:")
        print(f"  Stalled Agents: {len(results['stalled_agents'])}")
        print(f"  Recovery Attempted: {len(results['recovery_attempted'])}")
        print(f"  Recovery Succeeded: {len(results['recovery_succeeded'])}")
        print(f"  Recovery Failed: {len(results['recovery_failed'])}")
        
        if results['errors']:
            print(f"\n❌ Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"  - {error}")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    asyncio.run(main())


