#!/usr/bin/env python3
"""
Twitch Bot Connection Diagnostics Tool

Phase 1: Connection Diagnostics
- Verify OAuth token validity
- Add detailed IRC protocol logging
- Test connection with enhanced diagnostics
- Capture connection handshake sequence
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.chat_presence.twitch_bridge import TwitchChatBridge

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('twitch_diagnostics.log')
    ]
)

logger = logging.getLogger(__name__)


class TwitchDiagnostics:
    """Enhanced diagnostics for Twitch bot connection."""
    
    def __init__(self, config_path: str = "config/chat_presence.json"):
        """Initialize diagnostics with config."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.bridge: Optional[TwitchChatBridge] = None
        
    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            logger.error(f"❌ Config file not found: {self.config_path}")
            return {}
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def verify_token_format(self) -> dict:
        """Verify OAuth token format."""
        logger.info("=" * 60)
        logger.info("🔐 TOKEN FORMAT VERIFICATION")
        logger.info("=" * 60)
        
        token = self.config.get('oauth_token', '')
        username = self.config.get('username', '')
        channel = self.config.get('channel', '')
        
        results = {
            'token_present': bool(token),
            'token_format_valid': False,
            'token_length': len(token) if token else 0,
            'username_present': bool(username),
            'channel_present': bool(channel),
            'issues': []
        }
        
        # Check token format
        if not token:
            results['issues'].append("❌ OAuth token is missing")
        elif not token.startswith('oauth:'):
            results['issues'].append(f"⚠️ Token doesn't start with 'oauth:' prefix")
            results['issues'].append(f"   Current format: {token[:20]}...")
        else:
            results['token_format_valid'] = True
            logger.info(f"✅ Token format valid: {token[:15]}...{token[-5:]}")
        
        # Check token length (typical Twitch tokens are ~30-40 chars after 'oauth:')
        if token and len(token) < 20:
            results['issues'].append(f"⚠️ Token seems too short ({len(token)} chars)")
        elif token and len(token) > 100:
            results['issues'].append(f"⚠️ Token seems too long ({len(token)} chars)")
        
        # Check username
        if not username:
            results['issues'].append("❌ Username is missing")
        else:
            logger.info(f"✅ Username: {username}")
        
        # Check channel
        if not channel:
            results['issues'].append("❌ Channel is missing")
        else:
            logger.info(f"✅ Channel: {channel}")
        
        logger.info("=" * 60)
        return results
    
    def print_token_verification_instructions(self):
        """Print instructions for manual token verification."""
        logger.info("=" * 60)
        logger.info("📋 MANUAL TOKEN VERIFICATION INSTRUCTIONS")
        logger.info("=" * 60)
        logger.info("")
        logger.info("1. Visit: https://twitchapps.com/tmi/")
        logger.info("2. Authorize the application")
        logger.info("3. Copy the generated OAuth token")
        logger.info("4. Verify token format: oauth:xxxxx")
        logger.info("5. Update config/chat_presence.json with new token")
        logger.info("")
        logger.info("=" * 60)
    
    async def test_connection_with_logging(self) -> dict:
        """Test connection with enhanced IRC protocol logging."""
        logger.info("=" * 60)
        logger.info("🔌 CONNECTION TEST WITH ENHANCED LOGGING")
        logger.info("=" * 60)
        
        username = self.config.get('username', '')
        oauth_token = self.config.get('oauth_token', '')
        channel = self.config.get('channel', '')
        
        if not all([username, oauth_token, channel]):
            logger.error("❌ Missing required config: username, oauth_token, or channel")
            return {'success': False, 'error': 'Missing config'}
        
        # Create bridge with message callback for diagnostics
        connection_events = []
        
        def on_message(msg: dict):
            """Capture all messages for diagnostics."""
            connection_events.append({
                'type': 'message',
                'data': msg,
                'timestamp': asyncio.get_event_loop().time()
            })
            logger.info(f"📨 Message received: {msg.get('text', '')[:50]}")
        
        self.bridge = TwitchChatBridge(
            username=username,
            oauth_token=oauth_token,
            channel=channel,
            on_message=on_message
        )
        
        logger.info(f"🔌 Attempting connection...")
        logger.info(f"   Username: {username}")
        logger.info(f"   Channel: {channel}")
        logger.info(f"   Token: {oauth_token[:15]}...{oauth_token[-5:]}")
        
        try:
            # Attempt connection
            result = await self.bridge.connect()
            
            if result:
                logger.info("✅ Connection attempt returned True")
            else:
                logger.warning("⚠️ Connection attempt returned False")
            
            # Wait a bit to see if connection stabilizes
            logger.info("⏳ Waiting 10 seconds to observe connection stability...")
            await asyncio.sleep(10)
            
            # Check connection status
            connected = self.bridge.connected
            running = self.bridge.running
            
            logger.info(f"📊 Connection Status:")
            logger.info(f"   connected: {connected}")
            logger.info(f"   running: {running}")
            logger.info(f"   events captured: {len(connection_events)}")
            
            return {
                'success': result,
                'connected': connected,
                'running': running,
                'events_captured': len(connection_events),
                'events': connection_events[:10]  # First 10 events
            }
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'connected': False,
                'running': False
            }
        finally:
            if self.bridge:
                logger.info("🛑 Stopping bridge...")
                self.bridge.stop()
    
    def generate_diagnostic_report(self, token_results: dict, connection_results: dict):
        """Generate comprehensive diagnostic report."""
        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 DIAGNOSTIC REPORT")
        logger.info("=" * 60)
        logger.info("")
        
        logger.info("🔐 TOKEN VERIFICATION:")
        logger.info(f"   Token Present: {token_results.get('token_present', False)}")
        logger.info(f"   Format Valid: {token_results.get('token_format_valid', False)}")
        logger.info(f"   Token Length: {token_results.get('token_length', 0)}")
        
        if token_results.get('issues'):
            logger.info("   Issues:")
            for issue in token_results['issues']:
                logger.info(f"     {issue}")
        
        logger.info("")
        logger.info("🔌 CONNECTION TEST:")
        logger.info(f"   Success: {connection_results.get('success', False)}")
        logger.info(f"   Connected: {connection_results.get('connected', False)}")
        logger.info(f"   Running: {connection_results.get('running', False)}")
        logger.info(f"   Events Captured: {connection_results.get('events_captured', 0)}")
        
        if connection_results.get('error'):
            logger.info(f"   Error: {connection_results['error']}")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("")
        
        # Recommendations
        logger.info("💡 RECOMMENDATIONS:")
        logger.info("")
        
        if not token_results.get('token_format_valid'):
            logger.info("   1. ⚠️ Verify OAuth token format (should start with 'oauth:')")
            logger.info("   2. Visit https://twitchapps.com/tmi/ to generate new token")
        
        if not connection_results.get('connected'):
            logger.info("   3. ⚠️ Connection failed - check IRC protocol logs")
            logger.info("   4. Review twitch_diagnostics.log for detailed IRC messages")
            logger.info("   5. Test token manually with IRC client (HexChat, mIRC)")
        
        if connection_results.get('connected') and not connection_results.get('running'):
            logger.info("   6. ⚠️ Connection established but bot not running")
            logger.info("   7. Check event loop and callback execution")
        
        logger.info("")
        logger.info("=" * 60)


async def main():
    """Run diagnostics."""
    logger.info("🚀 Starting Twitch Connection Diagnostics")
    logger.info("")
    
    diagnostics = TwitchDiagnostics()
    
    # Step 1: Verify token format
    token_results = diagnostics.verify_token_format()
    
    # Step 2: Print manual verification instructions
    diagnostics.print_token_verification_instructions()
    
    # Step 3: Test connection with enhanced logging
    connection_results = await diagnostics.test_connection_with_logging()
    
    # Step 4: Generate report
    diagnostics.generate_diagnostic_report(token_results, connection_results)
    
    logger.info("✅ Diagnostics complete")
    logger.info("📄 Full log saved to: twitch_diagnostics.log")


if __name__ == "__main__":
    asyncio.run(main())

